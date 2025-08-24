import React from 'react';
import axios from 'axios';
import { API_BASE } from '../config';
import { renderRoutineGrid } from '../App';
import CampusDaysDisplay from './CampusDaysDisplay';
import ExamSchedule from './ExamSchedule';

export const GenerateButton = ({
  routineCourses,
  selectedSectionsByFaculty,
  routineDays,
  routineTimes,
  commutePreference,
  setIsLoading,
  setRoutineError,
  setRoutineResult,
  setAiFeedback,
  setToast,
  setErrorBanner,
  setUsedAI
}) => {
  const handleGenerateRoutine = async () => {
    if (!routineCourses.length) {
      setErrorBanner("Please select at least one course.");
      return;
    }

    if (!Object.keys(selectedSectionsByFaculty).length) {
      setErrorBanner("Please select sections for your courses.");
      return;
    }

    setIsLoading(true);
    setRoutineError("");
    setRoutineResult(null);
    setAiFeedback(null);

    try {
      // Validate commute preference
      if (!commutePreference) {
        setErrorBanner("Please select a commute preference (Live Far or Live Near).");
        setIsLoading(false);
        return;
      }

      // Ensure commute preference is properly formatted for the backend
      const formattedCommutePreference = commutePreference.toLowerCase();

      // Prepare sections data
      const selectedSections = [];
      Object.entries(selectedSectionsByFaculty).forEach(([courseCode, facultySelections]) => {
        Object.values(facultySelections).forEach(section => {
          if (section) selectedSections.push(section.section);
        });
      });

      // Call the API to generate routine
      const response = await axios.post(`${API_BASE}/routine`, {
        sections: selectedSections,
        days: routineDays.map(d => d.value),
        times: routineTimes.map(t => t.value),
        commutePreference: formattedCommutePreference,
        useAI: false
      });

      if (response.data.error) {
        // Check if the error is a structured error object
        if (typeof response.data.error === 'object' && response.data.error.error === true) {
          // Use setErrorBanner for structured error objects
          setErrorBanner(response.data.error.message || response.data.error.title);
          // Also set routineError to display the full error message in the UI
          setRoutineError(response.data.error);
        } else {
          // Remove any "Error generating routine:" prefix from the error message
          const errorMsg = response.data.error;
          const cleanedError = errorMsg.replace(/^Error generating routine:\s*/i, '');
          setRoutineError(cleanedError);
        }
      } else {
        setRoutineResult(response.data.routine);
        setToast("Routine generated successfully!");
      }
    } catch (error) {
      console.error("Error generating routine:", error);
      if (error.response && error.response.data) {
        if (error.response.data.error) {
          // Check if the error is a structured error object
          if (typeof error.response.data.error === 'object' && error.response.data.error.error === true) {
            // Use setErrorBanner for structured error objects
            setErrorBanner(error.response.data.error.message || error.response.data.error.title);
            // Also set routineError to display the full error message in the UI
            setRoutineError(error.response.data.error);
          } else {
            // Convert simple string errors to structured error objects
            setRoutineError({error: true, message: String(error.response.data.error), title: 'Error'});
          }
        } else if (error.response.data.message) {
          setErrorBanner(error.response.data.message);
          // Also set routineError for consistent UI display
          setRoutineError({error: true, message: error.response.data.message});
        } else {
          const errorMessage = "Failed to generate routine. Please try again.";
          setRoutineError({error: true, message: errorMessage});
          setErrorBanner(errorMessage);
        }
      } else {
        const errorMessage = "Failed to generate routine. Please try again.";
        setRoutineError({error: true, message: errorMessage});
        setErrorBanner(errorMessage);
      }
    } finally {
      setIsLoading(false);
      setUsedAI(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleGenerateRoutine}
      style={{
        backgroundColor: '#4CAF50',
        color: 'white',
        padding: '10px 20px',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '1em',
        fontWeight: '500'
      }}
    >
      Generate Routine
    </button>
  );
};



export const GenerateAIButton = ({
  routineCourses,
  routineDays,
  routineTimes,
  commutePreference,
  setIsLoading,
  setRoutineError,
  setRoutineResult,
  setAiFeedback,
  setToast,
  setErrorBanner,
  setSelectedSectionsByFaculty,
  setUsedAI
}) => {
  const handleGenerateAIRoutine = async () => {
    if (!routineCourses.length) {
      setErrorBanner("Please select at least one course.");
      return;
    }

    setIsLoading(true);
    setRoutineError("");
    setRoutineResult(null);
    setAiFeedback(null);

    try {
      // Validate commute preference
      if (!commutePreference) {
        setErrorBanner("Please select a commute preference (Live Far or Live Near).");
        setIsLoading(false);
        return;
      }

      // Ensure commute preference is properly formatted for the backend
      const formattedCommutePreference = commutePreference.toLowerCase();
      
      // Call the API to generate AI routine
      const response = await axios.post(`${API_BASE}/routine`, {
        courses: routineCourses.map(c => c.value),
        days: routineDays.map(d => d.value),
        times: routineTimes.map(t => t.value),
        commutePreference: formattedCommutePreference,
        useAI: true
      });

      if (response.data.error) {
        // Check if the error is a structured error object
        if (typeof response.data.error === 'object' && response.data.error.error === true) {
          // Use setErrorBanner for structured error objects
          setErrorBanner(response.data.error.message || response.data.error.title);
          // Also set routineError to display the full error message in the UI
          setRoutineError(response.data.error);
        } else {
          // Remove any "Error generating routine:" prefix from the error message
          const errorMsg = response.data.error;
          const cleanedError = errorMsg.replace(/^Error generating routine:\s*/i, '');
          setRoutineError(cleanedError);
        }
      } else {
        setRoutineResult(response.data.routine);
        setAiFeedback(response.data.feedback);
        setToast("AI Routine generated successfully!");
        
        // Update selected sections
        const newSelectedSectionsByFaculty = {};
        response.data.routine.forEach(section => {
          if (!newSelectedSectionsByFaculty[section.courseCode]) {
            newSelectedSectionsByFaculty[section.courseCode] = {};
          }
          newSelectedSectionsByFaculty[section.courseCode][section.faculties] = {
            value: section.sectionName,
            label: section.sectionName,
            section: section
          };
        });
        setSelectedSectionsByFaculty(newSelectedSectionsByFaculty);
      }
    } catch (error) {
      console.error("Error generating AI routine:", error);
      if (error.response && error.response.data) {
        if (error.response.data.error) {
          // Check if the error is a structured error object
          if (typeof error.response.data.error === 'object' && error.response.data.error.error === true) {
            // Use setErrorBanner for structured error objects
            setErrorBanner(error.response.data.error.message || error.response.data.error.title);
            // Also set routineError to display the full error message in the UI
            setRoutineError(error.response.data.error);
          } else {
            // Convert simple string errors to structured error objects
            setRoutineError({error: true, message: String(error.response.data.error), title: 'Error'});
          }
        } else if (error.response.data.message) {
          setErrorBanner(error.response.data.message);
          // Also set routineError for consistent UI display
          setRoutineError({error: true, message: error.response.data.message});
        } else {
          const errorMessage = "Failed to generate AI routine. Please try again.";
          setRoutineError({error: true, message: errorMessage});
          setErrorBanner(errorMessage);
        }
      } else {
        const errorMessage = "Failed to generate AI routine. Please try again.";
        setRoutineError({error: true, message: errorMessage});
        setErrorBanner(errorMessage);
      }
    } finally {
      setIsLoading(false);
      setUsedAI(true);
    }
  };

  return (
    <button
      type="button"
      onClick={handleGenerateAIRoutine}
      style={{
        backgroundColor: '#2196F3',
        color: 'white',
        padding: '10px 20px',
        border: 'none',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '1em',
        fontWeight: '500'
      }}
    >
      Generate with AI
    </button>
  );
};

export const RoutineResult = ({
  routineGridRef,
  routineResult,
  routineError,
  aiFeedback,
  routineDays
}) => {
  // Handle structured error objects
  const renderError = () => {
    let displayError = routineError;

    // If routineError is not an object or if it's an object but not a structured error,
    // try to convert it to a structured error for consistent handling.
    if (typeof displayError !== 'object' || displayError === null || displayError.error !== true) {
      // If it's a simple string, convert it to a structured error object
      if (typeof displayError === 'string') {
        displayError = { error: true, message: displayError, title: 'Error' };
      } else if (displayError === null || displayError === undefined) {
        displayError = { error: true, message: 'An unknown error occurred.', title: 'Error' };
      } else {
        // If it's an object but not a structured error, try to use its message or stringify it
        displayError = { error: true, message: displayError.message || String(displayError), title: 'Error' };
      }
    }

    // Now, displayError is guaranteed to be a structured error object with error: true
    const errorTitle = String(displayError.title || 'Error Detected');
    const errorMessage = String(displayError.message || 'An error occurred');
    const errorSuggestion = String(displayError.suggestion || ''); // Ensure suggestion is also a string

    // Special handling for time conflicts
    if (errorTitle.includes('Time Conflicts')) {
      return (
        <div style={{
          marginTop: '20px',
          textAlign: 'left',
          padding: '24px',
          backgroundColor: '#fff8f8',
          borderRadius: '8px',
          border: '1px solid #ffcdd2',
          boxShadow: '0 4px 12px rgba(255, 82, 82, 0.1)',
          maxWidth: '800px',
          margin: '20px auto',
          fontFamily: '"Inter", "Roboto", sans-serif',
          position: 'relative',
          overflow: 'hidden'
        }}>
          <div style={{
            position: 'absolute',
            top: 0,
            left: 0,
            width: '4px',
            height: '100%',
            background: 'linear-gradient(to bottom, #ff5252, #ff867f)'
          }}></div>
          <h3 style={{
            color: '#d32f2f',
            margin: '0 0 16px 0',
            fontSize: '18px',
            fontWeight: '600',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <span style={{ fontSize: '22px' }}>⚠️</span> {errorTitle}
          </h3>
          <div style={{
            color: '#555',
            fontSize: '15px',
            lineHeight: '1.5',
            marginBottom: '16px',
            padding: '12px 16px',
            backgroundColor: 'rgba(255, 82, 82, 0.05)',
            borderRadius: '6px',
            fontFamily: 'sans-serif',
            whiteSpace: 'pre-wrap',
            wordBreak: 'break-word'
          }}>
            {errorMessage}
          </div>
          {errorSuggestion && (
            <div style={{
              color: '#555',
              fontSize: '14px',
              lineHeight: '1.5',
              marginBottom: '16px',
              padding: '12px 16px',
              backgroundColor: 'rgba(255, 82, 82, 0.02)',
              borderRadius: '6px',
              borderLeft: '3px solid #ffcdd2',
            }}>
              <strong>Suggestion:</strong> {errorSuggestion}
            </div>
          )}
        </div>
      );
    }
    
    // Default structured error display
    return (
      <div style={{ 
        color: "#d32f2f", 
        marginBottom: "20px", 
        padding: "15px", 
        backgroundColor: "#fff8f8", 
        borderRadius: "8px",
        border: "1px solid #ffcdd2"
      }}>
        <h4 style={{ marginTop: 0, color: "#d32f2f" }}>{errorTitle}</h4>
        <p>{errorMessage}</p>
        {errorSuggestion && <p><strong>Suggestion:</strong> {errorSuggestion}</p>}
      </div>
    );
  };
  
  return (
    <div ref={routineGridRef} data-routine-grid>
      {routineResult && (
        <div style={{ marginTop: "20px" }}>
          {routineError ? renderError() : (
            <>
              {aiFeedback && (
                <div style={{ marginBottom: "20px", padding: "15px", backgroundColor: "#f8f9fa", borderRadius: "8px" }}>
                  <h4 style={{ marginTop: 0 }}>AI Feedback</h4>
                  <p style={{ whiteSpace: "pre-wrap" }}>{aiFeedback}</p>
                </div>
              )}
              <CampusDaysDisplay routine={routineResult} />
              <div style={{ overflowX: "auto" }}>
                {renderRoutineGrid(routineResult, routineDays.map(d => d.value))}
              </div>
              <ExamSchedule sections={routineResult} />
            </>
          )}
        </div>
      )}
    </div>
  );
};
