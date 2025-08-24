import React, { useEffect, useRef, useState } from 'react';

/**
 * Interactive3DArtwork Component
 * 
 * A modern 2025 UI component that displays artwork with 3D interactive effects.
 * The artwork responds to mouse movement and creates a parallax effect.
 * 
 * @param {Object} props - Component props
 * @param {string} props.imagePath - Path to the artwork image
 * @param {string} props.alt - Alt text for the image
 * @param {string} props.className - Additional CSS classes
 * @param {number} props.depth - Depth effect intensity (1-10)
 * @param {boolean} props.glowEffect - Whether to add a glow effect
 * @param {string} props.glowColor - Color of the glow effect
 */
const Interactive3DArtwork = ({
  imagePath,
  alt = 'Interactive Artwork',
  className = '',
  depth = 5,
  glowEffect = true,
  glowColor = 'rgba(33, 150, 243, 0.5)',
  ...props
}) => {
  const containerRef = useRef(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  
  // Normalize depth value
  const normalizedDepth = Math.min(Math.max(depth, 1), 10) / 10;
  
  // Handle mouse movement for 3D effect
  useEffect(() => {
    const handleMouseMove = (e) => {
      if (!containerRef.current || !isHovered) return;
      
      const container = containerRef.current;
      const rect = container.getBoundingClientRect();
      
      // Calculate mouse position relative to the center of the container
      const x = (e.clientX - rect.left - rect.width / 2) / (rect.width / 2);
      const y = (e.clientY - rect.top - rect.height / 2) / (rect.height / 2);
      
      setPosition({ x, y });
    };
    
    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [isHovered]);
  
  // Calculate transform values based on mouse position
  const transform = isHovered
    ? `perspective(1000px) rotateX(${position.y * -10 * normalizedDepth}deg) rotateY(${position.x * 10 * normalizedDepth}deg) scale3d(1.05, 1.05, 1.05)`
    : 'perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)';
  
  // Calculate shadow values based on mouse position
  const shadowX = position.x * 20 * normalizedDepth;
  const shadowY = position.y * 20 * normalizedDepth;
  const shadow = isHovered
    ? `${shadowX}px ${shadowY}px 25px rgba(0, 0, 0, 0.2)`
    : '0 10px 20px rgba(0, 0, 0, 0.15)';
  
  // Calculate glow effect
  const glow = isHovered && glowEffect
    ? `0 0 20px ${glowColor}, 0 0 30px ${glowColor}`
    : 'none';
  
  return (
    <div 
      ref={containerRef}
      className={`relative overflow-hidden rounded-xl ${className}`}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => {
        setIsHovered(false);
        setPosition({ x: 0, y: 0 });
      }}
      {...props}
    >
      <div
        className="transition-all duration-200 ease-out"
        style={{
          transform,
          boxShadow: shadow,
          filter: glow !== 'none' ? `drop-shadow(${glow})` : 'none',
        }}
      >
        <img 
          src={imagePath} 
          alt={alt}
          className="w-full h-full object-cover rounded-xl"
          style={{ transformStyle: 'preserve-3d' }}
        />
        
        {/* Reflection/highlight effect */}
        <div 
          className="absolute inset-0 bg-gradient-to-tr from-transparent via-white to-transparent opacity-0 transition-opacity duration-300 rounded-xl"
          style={{
            opacity: isHovered ? 0.1 : 0,
            transform: `translateX(${position.x * -30}px) translateY(${position.y * -30}px)`,
          }}
        />
      </div>
    </div>
  );
};

export default Interactive3DArtwork;