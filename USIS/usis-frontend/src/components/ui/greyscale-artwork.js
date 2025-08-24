import React, { useEffect, useState, useRef } from 'react';
import './greyscale-artwork.css';

/**
 * GreyscaleArtwork Component
 * 
 * This component integrates greyscale artwork as background elements in the UI.
 * It accepts an image path and positioning parameters to create visually appealing
 * background elements that enhance the user experience without distracting from content.
 */
const GreyscaleArtwork = ({
  imagePath,
  position = 'bottom-right', // Changed default to bottom positioning
  opacity = 0.15,
  size = 'medium',
  zIndex = -1,
  className = '',
  index = 0, // For staggered animations
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [isLoaded, setIsLoaded] = useState(false);
  const [imageError, setImageError] = useState(false);
  const artworkRef = useRef(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.1, rootMargin: '150px' } // Increased margin for earlier detection
    );

    const currentRef = artworkRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, []);

  const handleImageLoad = () => {
    console.log(`Image loaded: ${imagePath}`);
    setIsLoaded(true);
  };
  
  const handleImageError = () => {
    console.error(`Failed to load image: ${imagePath}`);
    setImageError(true);
  };
  // Map size string to actual dimensions (reduced sizes for more subtle appearance)
  const sizeMap = {
    small: { width: '120px', height: 'auto' },
    medium: { width: '180px', height: 'auto' },
    large: { width: '250px', height: 'auto' },
    full: { width: '100%', height: 'auto' },
    tiny: { width: '80px', height: 'auto' },
  };

  // Map position string to CSS position values
  const positionMap = {
    'top-left': { top: '0', left: '0' },
    'top-right': { top: '0', right: '0' },
    'bottom-left': { bottom: '0', left: '0' },
    'bottom-right': { bottom: '0', right: '0' },
    'center': { bottom: '25%', left: '50%', transform: 'translateX(-50%)' }, // Changed to bottom alignment
    'center-top': { top: '0', left: '50%', transform: 'translateX(-50%)' },
    'center-bottom': { bottom: '0', left: '50%', transform: 'translateX(-50%)' },
    'center-left': { bottom: '25%', left: '0' }, // Changed to bottom alignment
    'center-right': { bottom: '25%', right: '0' }, // Changed to bottom alignment
  };

  // Get position and size styles
  const positionStyle = positionMap[position] || positionMap['bottom-right'];
  const sizeStyle = sizeMap[size] || sizeMap['medium'];

  // If image failed to load, don't render anything
  if (imageError) {
    return null;
  }
  
  // Determine initial transform based on position for horizontal transitions
  const getInitialTransform = () => {
    if (position.includes('right')) {
      return 'translateX(60px)';
    } else if (position.includes('left')) {
      return 'translateX(-60px)';
    } else {
      return 'translateY(40px)';
    }
  };
  
  return (
    <div
      ref={artworkRef}
      className={`greyscale-artwork visible ${className}`}
      style={{
        position: 'absolute',
        ...positionStyle,
        opacity: opacity, // Always use the provided opacity
        zIndex,
        overflow: 'hidden',
        pointerEvents: 'none',
        '--artwork-index': index,
        transform: 'none', // Always use normal transform
        transition: 'opacity 0.8s ease, transform 0.8s ease', // Increased transition time
      }}
    >
      <img
        src={imagePath}
        alt=""
        onLoad={handleImageLoad}
        onError={handleImageError}
        style={{
          ...sizeStyle,
          filter: 'grayscale(100%) contrast(0.9)', // Simple greyscale effect without brightness enhancement
          mixBlendMode: 'overlay', // Blend with background
          borderRadius: '6px', // Smaller rounded corners
          transition: 'all 0.5s cubic-bezier(0.4, 0.0, 0.2, 1)', // Smooth transitions
          opacity: 1, // Always visible
        }}
      />
    </div>
  );
};

export default GreyscaleArtwork;