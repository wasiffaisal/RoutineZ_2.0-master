import React, { useState, useEffect, useRef } from 'react';
import './text-transition.css';

/**
 * TextTransition Component
 * 
 * A modern 2025 UI component that creates smooth transitions between text content.
 * Supports various animation types and customization options.
 * 
 * @param {Object} props - Component props
 * @param {string|Array} props.text - Text content or array of texts to cycle through
 * @param {string} props.animation - Animation type (fade, slide, typewriter, wave, blur, scale)
 * @param {number} props.duration - Animation duration in milliseconds
 * @param {number} props.delay - Delay between text changes in milliseconds (when text is an array)
 * @param {string} props.className - Additional CSS classes
 * @param {boolean} props.springEffect - Whether to use spring physics for animations
 */
const TextTransition = ({
  text,
  animation = 'fade',
  duration = 800,
  delay = 3000,
  className = '',
  springEffect = false,
  ...props
}) => {
  // Handle both single text and array of texts
  const textArray = Array.isArray(text) ? text : [text];
  const [currentIndex, setCurrentIndex] = useState(0);
  const [displayText, setDisplayText] = useState(textArray[0]);
  const [isAnimating, setIsAnimating] = useState(false);
  const containerRef = useRef(null);
  
  // Animation class mapping
  const animationClasses = {
    fade: 'text-transition-fade',
    slide: 'text-transition-slide',
    typewriter: 'text-transition-typewriter',
    wave: 'text-transition-wave',
    blur: 'text-transition-blur',
    scale: 'text-transition-scale',
  };
  
  // Spring effect class
  const springClass = springEffect ? 'text-transition-spring' : '';
  
  // Set animation duration as CSS variable
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.style.setProperty('--transition-duration', `${duration}ms`);
    }
  }, [duration]);
  
  // Handle text cycling for arrays
  useEffect(() => {
    if (textArray.length <= 1) return;
    
    const intervalId = setInterval(() => {
      setIsAnimating(true);
      
      // After animation out completes, change the text
      setTimeout(() => {
        setCurrentIndex((prevIndex) => (prevIndex + 1) % textArray.length);
        setDisplayText(textArray[(currentIndex + 1) % textArray.length]);
        setIsAnimating(false);
      }, duration / 2);
      
    }, delay);
    
    return () => clearInterval(intervalId);
  }, [textArray, delay, duration, currentIndex]);
  
  // Special case for typewriter animation
  if (animation === 'typewriter') {
    return (
      <div 
        ref={containerRef}
        className={`text-transition-container ${className}`}
        style={{ '--transition-duration': `${duration}ms` }}
        {...props}
      >
        <TypewriterText text={displayText} speed={duration / displayText.length} />
      </div>
    );
  }
  
  // Special case for wave animation
  if (animation === 'wave') {
    return (
      <div 
        ref={containerRef}
        className={`text-transition-container ${className}`}
        style={{ '--transition-duration': `${duration}ms` }}
        {...props}
      >
        <WaveText text={displayText} />
      </div>
    );
  }
  
  // Default animations
  return (
    <div 
      ref={containerRef}
      className={`text-transition-container ${className}`}
      {...props}
    >
      <span 
        className={`text-transition ${animationClasses[animation]} ${springClass} ${isAnimating ? 'animating' : ''}`}
      >
        {displayText}
      </span>
    </div>
  );
};

/**
 * TypewriterText Component
 * 
 * A helper component that creates a typewriter effect for text.
 */
const TypewriterText = ({ text, speed = 50 }) => {
  const [displayText, setDisplayText] = useState('');
  const [currentIndex, setCurrentIndex] = useState(0);
  
  useEffect(() => {
    // Reset when text changes
    setDisplayText('');
    setCurrentIndex(0);
  }, [text]);
  
  useEffect(() => {
    if (currentIndex >= text.length) return;
    
    const timeoutId = setTimeout(() => {
      setDisplayText(prev => prev + text[currentIndex]);
      setCurrentIndex(prev => prev + 1);
    }, speed);
    
    return () => clearTimeout(timeoutId);
  }, [currentIndex, text, speed]);
  
  return (
    <span className="text-transition-typewriter-text">
      {displayText}
      <span className="text-transition-cursor">|</span>
    </span>
  );
};

/**
 * WaveText Component
 * 
 * A helper component that creates a wave animation for text characters.
 */
const WaveText = ({ text }) => {
  return (
    <span className="text-transition-wave-container">
      {text.split('').map((char, index) => (
        <span 
          key={index} 
          className="text-transition-wave-char"
          style={{ '--char-index': index }}
        >
          {char === ' ' ? '\u00A0' : char}
        </span>
      ))}
    </span>
  );
};

export default TextTransition;