import React, { useState, useEffect } from 'react';
import { ChevronRight, BookOpen, Calendar, Users, Zap, ArrowRight } from 'lucide-react';
import ModernArtworkGrid from './ui/ModernArtworkGrid';
import './HomePage.css';

const HomePage = ({ onNavigate }) => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
  }, []);

  const features = [
    {
      icon: <Calendar className="w-6 h-6" />,
      title: "Smart Routine Generation",
      description: "Generate optimized class schedules with AI-powered conflict detection and seat availability checking.",
      color: "hsl(var(--primary))"
    },
    {
      icon: <BookOpen className="w-6 h-6" />,
      title: "Course Management",
      description: "Browse and select from comprehensive course catalogs with detailed information and prerequisites.",
      color: "hsl(var(--primary))"
    },
    {
      icon: <Users className="w-6 h-6" />,
      title: "Faculty Insights",
      description: "Get detailed faculty information, teaching schedules, and course assignments for better planning.",
      color: "hsl(var(--primary))"
    },
    {
      icon: <Zap className="w-6 h-6" />,
      title: "Real-time Updates",
      description: "Stay updated with real-time seat availability, exam schedules, and course changes.",
      color: "hsl(var(--primary))"
    }
  ];

  const quickActions = [
    {
      title: "Generate Routine",
      description: "Create your perfect schedule",
      action: "routine",
      gradient: "linear-gradient(135deg, hsl(var(--primary)), hsl(var(--primary) / 0.8))"
    },
    {
      title: "Check Seat Status",
      description: "View available seats",
      action: "seats",
      gradient: "linear-gradient(135deg, hsl(var(--primary) / 0.9), hsl(var(--primary) / 0.7))"
    },
    {
      title: "View Courses",
      description: "Explore course catalog",
      action: "courses",
      gradient: "linear-gradient(135deg, hsl(var(--primary) / 0.8), hsl(var(--primary) / 0.6))"
    }
  ];

  return (
    <div className="homepage-container">


      <div className="hero-section">
        <div className="hero-content">
          <h1 className={`hero-title ${isVisible ? 'animate' : ''}`}>USIS Routine Generator</h1>
          <p className={`hero-subtitle ${isVisible ? 'animate' : ''}`}>
            Create your perfect class schedule with AI-powered optimization, 
            real-time seat availability, and comprehensive course management.
          </p>
          <div className={`cta-buttons ${isVisible ? 'animate' : ''}`}>
            <button 
              className="cta-button cta-primary"
              onClick={() => onNavigate('routine')}
            >
              Get Started
              <ArrowRight className="w-5 h-5" />
            </button>
            <button 
              className="cta-button cta-secondary"
              onClick={() => onNavigate('seats')}
            >
              Check Seats
            </button>
          </div>
        </div>
      </div>

      <div className="features-section">
        <h2 className="section-title">Why Choose Our Platform?</h2>
        <p className="section-subtitle">
          Experience the most advanced course scheduling solution designed specifically for students
        </p>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div 
              key={index} 
              className="feature-card"
              style={{
                opacity: isVisible ? 1 : 0,
                transform: `translateY(${isVisible ? 0 : 30}px)`,
                transition: `all 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) ${0.1 * (index + 1)}s`
              }}
            >
              <div className="feature-icon" style={{ background: feature.color }}>
                {feature.icon}
              </div>
              <h3 className="feature-title">{feature.title}</h3>
              <p className="feature-description">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      <div className="quick-actions-section">
        <h2 className="section-title">Quick Actions</h2>
        <div className="quick-actions-grid">
          {quickActions.map((action, index) => (
            <div 
              key={index}
              className="quick-action-card"
              onClick={() => onNavigate(action.action)}
              style={{
                opacity: isVisible ? 1 : 0,
                transform: `translateY(${isVisible ? 0 : 30}px)`,
                transition: `all 0.6s cubic-bezier(0.2, 0.8, 0.2, 1) ${0.1 * (index + 1)}s`
              }}
            >
              <h3 className="quick-action-title">{action.title}</h3>
              <p className="quick-action-description">{action.description}</p>
              <button className="quick-action-button">
                Learn More
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      </div>

      <div className="artwork-section">
        <div className="artwork-header">
          <h2 className="artwork-title">Featured Artwork</h2>
          <p className="artwork-subtitle">
            Discover stunning digital art created by talented student artists
          </p>
        </div>
        <ModernArtworkGrid />
      </div>

      <footer className="professional-footer">
        <div className="footer-content">
          <div className="footer-sections">
            <div className="footer-section">
              <h4>USIS Routine Generator</h4>
              <p>Empowering students with intelligent scheduling solutions since 2024.</p>
            </div>
            <div className="footer-section">
              <h4>Features</h4>
              <ul>
                <li>Smart Routine Generation</li>
                <li>Real-time Seat Monitoring</li>
                <li>Course Management</li>
                <li>Faculty Insights</li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Technology</h4>
              <ul>
                <li>React & Modern Web Stack</li>
                <li>AI-Powered Optimization</li>
                <li>Real-time Data Sync</li>
                <li>Responsive Design</li>
              </ul>
            </div>
            <div className="footer-section">
              <h4>Connect</h4>
              <p>Built with ❤️ for the student community</p>
              <div className="footer-links">
                <a href="#" className="footer-link">Support</a>
                <a href="#" className="footer-link">Feedback</a>
                <a href="#" className="footer-link">About</a>
              </div>
            </div>
          </div>
          <div className="footer-bottom">
            <p>&copy; 2025 RoutineZ. Built for BRAC University students.</p>
            <p>Designed for BRACU students • Built with modern web technologies • Always improving</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default HomePage;