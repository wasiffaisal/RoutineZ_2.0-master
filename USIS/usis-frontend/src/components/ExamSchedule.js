import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Select from 'react-select';
import { API_BASE } from '../config';

const ExamSchedule = ({ sections: routineSections }) => {
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [courses, setCourses] = useState([]);
  const [sections, setSections] = useState([]);
  const [isLoadingSections, setIsLoadingSections] = useState(false);

  // If routineSections is provided, use that instead of fetching
  const useRoutineSections = !!routineSections;

  // Fetch all courses on mount (only if not using routineSections)
  useEffect(() => {
    if (!useRoutineSections) {
      axios.get(`${API_BASE}/courses`).then(res => {
        // Check if res.data is an array or an object with a data property
        const coursesData = Array.isArray(res.data) ? res.data : (res.data.data || []);
        setCourses(coursesData);
      });
    }
  }, [useRoutineSections]);

  // Fetch course details when a course is selected (only if not using routineSections)
  useEffect(() => {
    if (!useRoutineSections && selectedCourse) {
      setIsLoadingSections(true);
      axios.get(`${API_BASE}/course_details?course=${selectedCourse.value}`)
        .then(res => {
          // Check if res.data is an array or an object with a data property
          const sectionsData = Array.isArray(res.data) ? res.data : (res.data.data || []);
          setSections(sectionsData);
        })
        .catch(error => {
          console.error("Error fetching sections:", error);
          setSections([]); // Clear sections on error
        })
        .finally(() => setIsLoadingSections(false));
    } else if (!useRoutineSections) {
      setSections([]);
      setIsLoadingSections(false);
    }
  }, [selectedCourse, useRoutineSections]);

  // Determine which sections to display
  const displaySections = useRoutineSections ? routineSections : sections;
  
  // Sort sections for display
  const sortedSections = (displaySections || []).slice().sort((a, b) => {
    const nameA = a.sectionName || '';
    const nameB = b.sectionName || '';
    return nameA.localeCompare(nameB, undefined, { numeric: true, sensitivity: 'base' });
  });

  return (
    <div className="seat-status-container">
      <h2 className="seat-status-heading">Exam Dates</h2>
      
      {/* Only show course selector if not using routineSections */}
      {!useRoutineSections && (
        <div style={{ marginBottom: '18px', maxWidth: 400, marginLeft: 'auto', marginRight: 'auto' }}>
          <Select
            options={courses.map(c => ({ value: c.code, label: c.code }))}
            value={selectedCourse}
            onChange={setSelectedCourse}
            placeholder="Search and select a course..."
            isClearable={true}
            isSearchable={true}
          />
        </div>
      )}
      
      {/* Loading and empty states for standalone mode */}
      {!useRoutineSections && isLoadingSections && (
        <div className="seat-status-message loading">Loading sections...</div>
      )}
      {!useRoutineSections && !selectedCourse && !isLoadingSections && (
        <div className="seat-status-message info">Please select a course to view exam dates.</div>
      )}
      {!useRoutineSections && selectedCourse && !isLoadingSections && sections.length === 0 && (
        <div className="seat-status-message warning">No exam dates available for this course.</div>
      )}
      
      {/* Empty state for routine mode */}
      {useRoutineSections && (!sortedSections || sortedSections.length === 0) && (
        <div className="seat-status-message info">No exam dates available for selected courses.</div>
      )}
      
      {/* Show table when we have sections to display */}
      {sortedSections && sortedSections.length > 0 && (
        <div className="seat-status-table-wrapper">
          <table className="seat-status-table">
            <thead>
              <tr>
                <th>Section</th>
                <th>Faculty</th>
                <th>Midterm Exam</th>
                <th>Final Exam</th>
              </tr>
            </thead>
            <tbody>
              {sortedSections.map(section => (
                <tr key={section.sectionId}>
                  <td>
                    <div style={{ fontWeight: '500' }}>{section.sectionName}</div>
                    <div style={{ fontSize: '0.9em', color: '#6c757d' }}>{section.courseCode}</div>
                  </td>
                  <td>{section.faculties || 'TBA'}</td>
                  <td>
                    {section.midExamDate ? (
                      <>
                        <div>{section.midExamDate}</div>
                        {section.formattedMidExamTime && <div style={{ color: '#666', fontSize: '0.97em' }}>{section.formattedMidExamTime}</div>}
                      </>
                    ) : (
                      <span style={{ color: '#aaa', fontStyle: 'italic' }}>Not Scheduled</span>
                    )}
                  </td>
                  <td>
                    {section.finalExamDate ? (
                      <>
                        <div>{section.finalExamDate}</div>
                        {section.formattedFinalExamTime && <div style={{ color: '#666', fontSize: '0.97em' }}>{section.formattedFinalExamTime}</div>}
                      </>
                    ) : (
                      <span style={{ color: '#aaa', fontStyle: 'italic' }}>Not Scheduled</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};

export default ExamSchedule;