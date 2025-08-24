import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import LandingPage from './LandingPage';
import App from '../App'; // Import the existing App component

const HomePageWrapper = () => {
  const navigate = useNavigate();
  const location = useLocation();

  const handleNavigation = (target) => {
    if (target === 'app' || target === 'routine' || target === 'courses') {
      navigate('/app');
    } else if (target === 'seats') {
      navigate('/seats');
    }
  };

  const handleBackToHome = () => {
    navigate('/');
  };

  if (location.pathname === '/') {
    return <LandingPage onNavigate={handleNavigation} />;
  }

  return <App />;
};

export default HomePageWrapper;