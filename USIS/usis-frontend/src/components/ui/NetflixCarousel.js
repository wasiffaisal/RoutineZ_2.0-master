import React, { useEffect, useState, useRef } from 'react';
import './NetflixCarousel.css';

/**
 * NetflixCarousel Component
 * 
 * A horizontal scrolling carousel that displays artwork in a Netflix-style presentation
 * with smooth animations from left to right.
 */
const NetflixCarousel = () => {
  const [isVisible, setIsVisible] = useState(false);
  const carouselRef = useRef(null);
  
  // Array of available artwork images
  const artworkImages = [
    { name: 'Dark Sunflower', path: '/fanvue/Dark Sunflower.svg' },
    { name: 'Eleven St. Things', path: '/fanvue/Eleven St. Things.svg' },
    { name: 'Midnight Bloom', path: '/fanvue/Midnight Bloom.svg' },
    { name: 'RoutineZ Logo', path: '/fanvue/RoutineZ Logo.svg' },
    { name: 'Placeholder', path: '/fanvue/placeholder.svg' },
    // Using SVG files from public/fanvue
  ];


  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.1, rootMargin: '150px' }
    );

    const currentRef = carouselRef.current;
    if (currentRef) {
      observer.observe(currentRef);
    }

    return () => {
      if (currentRef) {
        observer.unobserve(currentRef);
      }
    };
  }, []);
  
  // Start animation when component becomes visible
  useEffect(() => {
    if (isVisible && carouselRef.current) {
      startAnimation();
    }
  }, [isVisible]);

  const startAnimation = () => {
    const carousel = carouselRef.current;
    if (!carousel) return;
    
    const scrollWidth = carousel.scrollWidth;
    const containerWidth = carousel.clientWidth;
    
    // Only start auto-scroll if we have enough items to scroll
    if (scrollWidth > containerWidth) {
      // Set initial position
      carousel.scrollLeft = 0;
      
      // Animation variables
      let scrollPos = 0;
      let animationId = null;
      const scrollSpeed = 0.7; // pixels per frame - slightly faster
      
      const scroll = () => {
        if (!carousel) {
          cancelAnimationFrame(animationId);
          return;
        }
        
        scrollPos += scrollSpeed;
        carousel.scrollLeft = scrollPos;
        
        // Reset when we reach the end (with a buffer for the cloned items)
        if (scrollPos >= scrollWidth - containerWidth - 50) {
          // Smooth reset to beginning
          scrollPos = 0;
          
          // Use smooth scrolling for reset
          carousel.style.scrollBehavior = 'smooth';
          carousel.scrollLeft = 0;
          
          // Reset scroll behavior after transition
          setTimeout(() => {
            if (carousel) {
              carousel.style.scrollBehavior = 'auto';
            }
          }, 300);
        }
        
        animationId = requestAnimationFrame(scroll);
      };
      
      // Start the animation
      animationId = requestAnimationFrame(scroll);
      
      // Clean up animation on component unmount
      return () => {
        if (animationId) {
          cancelAnimationFrame(animationId);
        }
      };
    }
  };

  return (
    <div className="netflix-carousel-container" ref={carouselRef}>
      <div className="netflix-carousel-track">
        {artworkImages.map((image, index) => (
          <div key={index} className="netflix-carousel-item">
            <img 
              src={image.path} 
              alt={image.name} 
              className="netflix-carousel-image"
              loading="lazy"
            />
            <div className="netflix-carousel-overlay">
              <span>{image.name}</span>
            </div>
          </div>
        ))}
        
        {/* Clone the first few items to create seamless loop */}
        {artworkImages.slice(0, 3).map((image, index) => (
          <div key={`clone-${index}`} className="netflix-carousel-item">
            <img 
              src={image.path} 
              alt={`${image.name} (clone)`} 
              className="netflix-carousel-image"
              loading="lazy"
            />
            <div className="netflix-carousel-overlay">
              <span>{image.name}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NetflixCarousel;