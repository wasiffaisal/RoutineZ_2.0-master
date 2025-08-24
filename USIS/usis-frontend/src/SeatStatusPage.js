import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';
import { API_BASE } from './config';
import { formatTime12Hour } from './App';
import { Search, X, AlertCircle } from 'lucide-react';

// Modern UI Components
const Card = ({ children, className = '' }) => (
  <div className={`bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 ${className}`}>
    {children}
  </div>
);

const Badge = ({ children, variant = 'default', className = '' }) => {
  const variants = {
    default: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
    success: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
    warning: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
    danger: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    secondary: 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
  };
  
  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${variants[variant]} ${className}`}>
      {children}
    </span>
  );
};

const Skeleton = ({ className = '' }) => (
  <div className={`animate-pulse bg-gray-200 dark:bg-gray-700 rounded ${className}`} />
);

const SeatStatusPage = () => {
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState('');
  const [sections, setSections] = useState([]);
  const [loading, setLoading] = useState(false);
  const [lastUpdated, setLastUpdated] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [activeSuggestion, setActiveSuggestion] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  const abortControllerRef = useRef(null);
  const eventSourceRef = useRef(null);
  const searchRef = useRef(null);

  // Fetch all courses
  const fetchCourses = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE}/courses`);
      const coursesData = Array.isArray(response.data) ? response.data : (response.data.data || []);
      setCourses(coursesData.sort((a, b) => a.code.localeCompare(b.code)));
    } catch (error) {
      console.error('Failed to fetch courses:', error);
    }
  }, []);

  // Fetch sections for selected course - no caching
  const fetchSections = useCallback(async (courseCode, showLoading = true) => {
    if (!courseCode) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    abortControllerRef.current = new AbortController();

    try {
      if (showLoading) setLoading(true);
      
      const response = await axios.get(`${API_BASE}/course_details?course=${courseCode}`, {
        signal: abortControllerRef.current.signal,
        headers: {
          'Cache-Control': 'no-cache, no-store, must-revalidate',
          'Pragma': 'no-cache',
          'Expires': '0'
        }
      });
      
      const sectionsData = Array.isArray(response.data) ? response.data : (response.data.data || []);
      setSections(sectionsData.map(section => ({ ...section, courseCode })));
      setLastUpdated(new Date());
    } catch (error) {
      if (!axios.isCancel(error)) {
        console.error('Failed to fetch sections:', error);
        setSections([]);
      }
    } finally {
      if (showLoading) setLoading(false);
    }
  }, []);



  // Initial load
  useEffect(() => {
    fetchCourses();
  }, [fetchCourses]);

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
      if (selectedCourse) {
        fetchSections(selectedCourse, false);
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
  }, [selectedCourse, fetchSections]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  // Close suggestions when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchRef.current && !searchRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleCourseChange = (courseCode) => {
    setSelectedCourse(courseCode);
    setSearchTerm('');
    if (courseCode) {
      fetchSections(courseCode);
    } else {
      setSections([]);
    }
  };

  const handleCourseSelection = (course) => {
    setSelectedCourse(course.code);
    setSearchTerm(course.code);
    setShowSuggestions(false);
    fetchSections(course.code);
  };

  const getLabSchedulesArray = (labSchedules, section) => {
    if (Array.isArray(labSchedules)) return labSchedules;
    if (labSchedules && typeof labSchedules === 'object' && Array.isArray(labSchedules.classSchedules)) {
      return labSchedules.classSchedules.map(sched => ({
        ...sched,
        room: section?.labRoomName || sched.room || 'TBA',
      }));
    }
    return [];
  };

  const getSeatStatusBadge = (availableSeats, capacity) => {
    if (availableSeats === undefined) return <Badge variant="secondary">N/A</Badge>;
    
    const percentage = (availableSeats / capacity) * 100;
    
    if (availableSeats === 0) return <Badge variant="danger">Full</Badge>;
    if (percentage < 20) return <Badge variant="warning">Low</Badge>;
    return <Badge variant="success">Available</Badge>;
  };

  const filteredCourses = courses.filter(course => 
    course.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.title?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const hasAvailableSeats = sections.some(item => item.availableSeats > 0);

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-white to-slate-100 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-600 to-purple-600 bg-clip-text text-transparent mb-2">
            Seat Status
          </h1>
          <p className="text-slate-600 dark:text-slate-400">Live course availability and seat tracking</p>
          
          {/* Connection Status */}
          <div className="mt-4 flex justify-center">
            <div className={`inline-flex items-center px-4 py-2 rounded-full text-sm font-medium ${
              isConnected 
                ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' 
                : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
            }`}>
              <div className={`w-2 h-2 rounded-full mr-2 ${
                isConnected ? 'bg-green-500 animate-pulse' : 'bg-yellow-500'
              }`}></div>
              {isConnected ? '● Live Updates Connected' : '● Connecting to Live Updates...'}
            </div>
          </div>
        </div>

        {/* Controls */}
        <Card className="mb-6 p-6">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                Search Course
              </label>
              <div className="relative" ref={searchRef}>
                <input
                  type="text"
                  placeholder={selectedCourse ? selectedCourse : "Type to search courses..."}
                  value={searchTerm}
                  onChange={(e) => {
                    setSearchTerm(e.target.value);
                    setShowSuggestions(true);
                    setActiveSuggestion(0);
                  }}
                  onFocus={() => setShowSuggestions(true)}
                  onKeyDown={(e) => {
                    if (e.key === 'ArrowDown') {
                      e.preventDefault();
                      setActiveSuggestion(prev => 
                        prev < filteredCourses.length - 1 ? prev + 1 : prev
                      );
                    } else if (e.key === 'ArrowUp') {
                      e.preventDefault();
                      setActiveSuggestion(prev => prev > 0 ? prev - 1 : 0);
                    } else if (e.key === 'Enter') {
                      e.preventDefault();
                      if (filteredCourses[activeSuggestion]) {
                        handleCourseSelection(filteredCourses[activeSuggestion]);
                      }
                    } else if (e.key === 'Escape') {
                      setShowSuggestions(false);
                    }
                  }}
                  className="w-full px-4 py-3 border border-slate-300 dark:border-slate-600 rounded-lg bg-white dark:bg-slate-800 text-slate-900 dark:text-slate-100 focus:ring-2 focus:ring-indigo-500 focus:border-transparent placeholder-slate-400"
                />
                {showSuggestions && searchTerm && (
                   <div className="absolute z-10 w-full mt-1 bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-lg shadow-lg max-h-60 overflow-y-auto">
                     {filteredCourses.length > 0 ? (
                       filteredCourses.map((course, index) => (
                         <div
                           key={course.code}
                           className={`px-4 py-2 cursor-pointer hover:bg-slate-50 dark:hover:bg-slate-700 ${
                             index === activeSuggestion ? 'bg-slate-50 dark:bg-slate-700' : ''
                           }`}
                           onClick={() => handleCourseSelection(course)}
                           onMouseEnter={() => setActiveSuggestion(index)}
                         >
                           <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                             {course.code}
                           </div>
                           <div className="text-sm text-slate-600 dark:text-slate-400">
                             {course.title}
                           </div>
                         </div>
                       ))
                     ) : (
                       <div className="px-4 py-2 text-sm text-slate-500 dark:text-slate-400">
                         No courses found
                       </div>
                     )}
                   </div>
                 )}
              </div>
            </div>


          </div>

          <div className="flex items-center justify-between mt-4">
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => selectedCourse && fetchSections(selectedCourse, true)}
                  disabled={!selectedCourse || loading}
                  className="px-4 py-2 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-500 text-white rounded-lg transition-colors text-sm font-medium"
                >
                  Refresh
                </button>
              </div>

              {lastUpdated && (
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Last updated: {lastUpdated.toLocaleTimeString()}
                </div>
              )}
            </div>
        </Card>

        {/* Content */}
        {!selectedCourse ? (
          <div className="text-center py-12">
            <Search className="w-8 h-8 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-medium text-slate-700 dark:text-slate-300 mb-1">
              Search for Courses
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              Enter a course code to see seat availability
            </p>
          </div>
        ) : loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto mb-4"></div>
            <p className="text-slate-600 dark:text-slate-400">Loading sections...</p>
          </div>
        ) : sections.length === 0 ? (
          <div className="text-center py-12">
            <AlertCircle className="w-8 h-8 text-slate-400 mx-auto mb-3" />
            <h3 className="text-base font-medium text-slate-700 dark:text-slate-300 mb-1">
              No Sections Found
            </h3>
            <p className="text-sm text-slate-500 dark:text-slate-400">
              No sections available for {selectedCourse}
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {/* Summary Card */}
            {selectedCourse && sections.length > 0 && (
              <Card className="mb-8 border-slate-200 dark:border-slate-700">
                <div className="pt-6 px-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-2xl font-bold text-slate-900 dark:text-slate-100">
                        {selectedCourse}
                      </h3>
                      <p className="text-slate-600 dark:text-slate-400">
                        {sections.length} section{sections.length !== 1 ? 's' : ''} available
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-bold text-indigo-600 dark:text-indigo-400">
                        {sections.reduce((total, section) => total + (section.availableSeats || 0), 0)}
                      </div>
                      <div className="text-sm text-slate-600 dark:text-slate-400">Total Available Seats</div>
                    </div>
                  </div>
                </div>
              </Card>
            )}

            {/* Sections Table */}
            <div className="overflow-x-auto">
              <table className="w-full bg-white dark:bg-slate-800 rounded-lg shadow-lg">
                <thead className="bg-slate-50 dark:bg-slate-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Section
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Faculty
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Schedule
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Available Seats
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Midterm Exam
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-semibold text-slate-600 dark:text-slate-400 uppercase tracking-wider">
                      Final Exam
                    </th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
                  {sections
                    .slice()
                    .sort((a, b) => (a.sectionName || '').localeCompare(b.sectionName || ''))
                    .map((section) => (
                      <tr key={section.sectionId || `${section.courseCode}-${section.sectionName}`} className="hover:bg-slate-50 dark:hover:bg-slate-700/50 transition-colors">
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm font-semibold text-slate-900 dark:text-slate-100">
                            {section.sectionName}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-600 dark:text-slate-400">
                            {section.faculties || 'TBA'}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap">
                          <div className="text-sm text-slate-600 dark:text-slate-400">
                            {section.sectionSchedule?.classSchedules?.map((sched, index) => (
                              <div key={index}>
                                {`Class: ${sched.day} ${formatTime12Hour(sched.startTime)}-${formatTime12Hour(sched.endTime)}`}
                              </div>
                            ))}
                            {getLabSchedulesArray(section.labSchedules, section)?.map((sched, index) => (
                              <div key={`lab-${index}`}>
                                {`Lab: ${sched.day} ${formatTime12Hour(sched.startTime)}-${formatTime12Hour(sched.endTime)} ${sched.room ? `(${sched.room})` : ''}`}
                              </div>
                            ))}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <div className="text-sm font-bold text-slate-900 dark:text-slate-100">
                            {section.availableSeats || 0} / {section.capacity}
                          </div>
                          <div className="w-full bg-slate-200 dark:bg-slate-700 rounded-full h-2 mt-1">
                            <div 
                              className="h-2 rounded-full transition-all duration-300"
                              style={{
                                width: `${Math.min(((section.availableSeats || 0) / section.capacity) * 100, 100)}%`,
                                backgroundColor: section.availableSeats === 0 ? '#ef4444' : 
                                  (section.availableSeats || 0) < 5 ? '#f59e0b' : '#10b981'
                              }}
                            />
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <span className={`px-3 py-1 inline-flex text-xs leading-5 font-semibold rounded-full ${
                            section.availableSeats === 0 ? 'bg-rose-100 text-rose-800 dark:bg-rose-900/30 dark:text-rose-400' :
                            (section.availableSeats || 0) < 5 ? 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-400' :
                            'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/30 dark:text-emerald-400'
                          }`}>
                            {section.availableSeats === 0 ? 'Full' :
                             (section.availableSeats || 0) < 5 ? 'Low' : 'Available'}
                          </span>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <div className="text-sm text-slate-600 dark:text-slate-400">
                            {section.midExamDate ? (
                              <>
                                <div>{section.midExamDate}</div>
                                {section.formattedMidExamTime && (
                                  <div className="text-slate-500 text-xs">{section.formattedMidExamTime}</div>
                                )}
                              </>
                            ) : (
                              <span className="text-slate-400 text-xs italic">Not Scheduled</span>
                            )}
                          </div>
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-center">
                          <div className="text-sm text-slate-600 dark:text-slate-400">
                            {section.finalExamDate ? (
                              <>
                                <div>{section.finalExamDate}</div>
                                {section.formattedFinalExamTime && (
                                  <div className="text-slate-500 text-xs">{section.formattedFinalExamTime}</div>
                                )}
                              </>
                            ) : (
                              <span className="text-slate-400 text-xs italic">Not Scheduled</span>
                            )}
                          </div>
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default SeatStatusPage;