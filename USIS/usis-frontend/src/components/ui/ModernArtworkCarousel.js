import React, { useEffect, useState, useRef } from 'react';
import './ModernArtworkCarousel.css';

/**
 * ModernArtworkCarousel Component
 * 
 * A horizontal scrolling carousel that displays artwork with a modern 2025 design
 * featuring smooth left-to-right animations.
 */
const ModernArtworkCarousel = () => {
  const [isVisible, setIsVisible] = useState(false);
  const carouselRef = useRef(null);
  
  // Array of available artwork images from build/fanvue directory
  const artworkImages = [
    { name: 'Dark Sunflower', path: '/fanvue/Dark Sunflower.svg' },
    { name: 'Eleven St. Things', path: '/fanvue/Eleven St. Things.svg' },
    { name: 'Midnight Bloom', path: '/fanvue/Midnight Bloom.svg' },
    { name: 'RoutineZ Logo', path: '/fanvue/RoutineZ Logo.svg' },
    { name: 'Placeholder', path: '/fanvue/placeholder.svg' },
    // Fallback to SVG files in public/fanvue
  ];


  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          observer.unobserve(entry.target);
        }
      },
      { threshold: 0.1, rootMargin: '100px' }
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
      const scrollSpeed = 0.8; // pixels per frame - slower for better visibility
      
      const scroll = () => {
        if (!carousel) {
          cancelAnimationFrame(animationId);
          return;
        }
        
        scrollPos += scrollSpeed;
        carousel.scrollLeft = scrollPos;
        
        // Reset when we reach the end
        if (scrollPos >= scrollWidth - containerWidth) {
          // Smooth reset to beginning
          scrollPos = 0;
          carousel.scrollLeft = 0;
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
    <div className="modern-artwork-carousel" ref={carouselRef}>
      <div className="modern-artwork-track">
        {artworkImages.map((image, index) => (
          <div 
            key={index} 
            className="modern-artwork-item"
            style={{ animationDelay: `${index * 0.2}s` }}
          >
            <img 
              src={image.path} 
              alt={image.name} 
              className="modern-artwork-image"
              loading="lazy"
            />
            <div className="modern-artwork-overlay">
              <span className="modern-artwork-title">{image.name}</span>
            </div>
          </div>
        ))}
        
        {/* Clone the first few items to create seamless loop */}
        {artworkImages.slice(0, 4).map((image, index) => (
          <div 
            key={`clone-${index}`} 
            className="modern-artwork-item"
            style={{ animationDelay: `${(index + artworkImages.length) * 0.2}s` }}
          >
            <img 
              src={image.path} 
              alt={`${image.name} (clone)`} 
              className="modern-artwork-image"
              loading="lazy"
            />
            <div className="modern-artwork-overlay">
              <span className="modern-artwork-title">{image.name}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModernArtworkCarousel;