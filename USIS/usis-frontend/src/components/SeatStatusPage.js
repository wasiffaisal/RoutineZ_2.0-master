// SeatStatusPage.js - Component for displaying seat status information with SSE
import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import Select from "react-select";
import '../App.css';
import { formatTime12Hour, getLabSchedulesArray } from '../App';
import { API_BASE } from '../config';

const SeatStatusPage = ({ courses }) => {
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [sections, setSections] = useState([]);
  const [isLoadingSections, setIsLoadingSections] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef(null);

  // Fetch course details when a course is selected
  useEffect(() => {
    if (selectedCourse) {
      setIsLoadingSections(true);
      axios.get(`${API_BASE}/course_details?course=${selectedCourse.value}`)
        .then(res => setSections(res.data))
        .catch(error => {
          console.error("Error fetching sections:", error);
          setSections([]); // Clear sections on error
        })
        .finally(() => setIsLoadingSections(false));
    } else {
      setSections([]);
      setIsLoadingSections(false);
    }
  }, [selectedCourse]);

  // SSE connection for real-time updates
  useEffect(() => {
    // Always establish SSE connection when component is active
    const eventSource = new EventSource(`${API_BASE}/courses/sse`);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      setIsConnected(true);
      console.log('SSE connection established');
    };

    eventSource.addEventListener('connected', (event) => {
      setIsConnected(true);
    });

    eventSource.addEventListener('update', (event) => {
      // Refresh current course data when SSE sends update
      if (selectedCourse && selectedCourse.value) {
        axios.get(`${API_BASE}/course_details?course=${selectedCourse.value}`)
          .then(res => setSections(res.data))
          .catch(error => {
            console.error("Error fetching sections from SSE:", error);
          });
      }
    });

    eventSource.addEventListener('error', (event) => {
      console.error('SSE error:', event);
      setIsConnected(false);
    });

    eventSource.onerror = (error) => {
      console.error('SSE connection error:', error);
      setIsConnected(false);
    };

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
        setIsConnected(false);
      }
    };
  }, [selectedCourse]);

  const sortedSections = sections.slice().sort((a, b) => {
    const nameA = a.sectionName || '';
    const nameB = b.sectionName || '';
    return nameA.localeCompare(nameB, undefined, { numeric: true, sensitivity: 'base' });
  });

  return (
    <div className="seat-status-container">
      <h2 className="seat-status-heading">
        Seat Status
        {isConnected && (
          <span style={{ 
            fontSize: '0.7em', 
            color: '#28a745', 
            marginLeft: '10px',
            fontWeight: 'normal'
          }}>
            ● Live Updates
          </span>
        )}
      </h2>
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
      {isLoadingSections && (
        <div className="seat-status-message loading">Loading sections...</div>
      )}
      {!selectedCourse && !isLoadingSections && (
        <div className="seat-status-message info">Please select a course to view seat status.</div>
      )}
      {selectedCourse && !isLoadingSections && sections.length === 0 && (
        <div className="seat-status-message warning">No seat available for this course.</div>
      )}
      {selectedCourse && sections.length > 0 && (
        <div className="seat-status-table-wrapper">
          <table className="seat-status-table">
            <thead>
              <tr>
                <th>Section</th>
                <th>Faculty</th>
                <th>Seats</th>
                <th>Schedule</th>
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
                    <div className={
                      section.availableSeats > 10 ? 'seat-badge seat-available' :
                      section.availableSeats > 0 ? 'seat-badge seat-few' : 'seat-badge seat-full'
                    }>
                      Seat Cap.: {section.capacity} / Booked: {section.capacity - section.availableSeats}
                    </div>
                  </td>
                  <td>
                    {/* Class Schedule */}
                    {(section.sectionSchedule?.classSchedules || []).map((schedule, index) => (
                      <div key={index} className="class-schedule">
                        <span className="schedule-day">{schedule.day}</span>{' '}
                        <span>{formatTime12Hour(schedule.startTime)} - {formatTime12Hour(schedule.endTime)}</span>
                        {schedule.room && (
                          <span className="schedule-room"> ({schedule.room})</span>
                        )}
                      </div>
                    ))}
                    {/* Lab Schedule */}
                    {getLabSchedulesArray(section).map((schedule, index) => (
                      <div key={index} className="lab-schedule">
                        <span className="schedule-day">Lab: {schedule.day}</span>{' '}
                        <span>{formatTime12Hour(schedule.startTime)} - {formatTime12Hour(schedule.endTime)}</span>
                        {schedule.room && (
                          <span className="schedule-room"> ({schedule.room})</span>
                        )}
                      </div>
                    ))}
                  </td>
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

export default SeatStatusPage;