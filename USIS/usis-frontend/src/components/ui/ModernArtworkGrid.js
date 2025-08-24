import React from 'react';
import './ModernArtworkGrid.css';

/**
 * ModernArtworkGrid Component
 * 
 * A contemporary UI component that displays artwork in a responsive grid layout
 * with a sophisticated design arranged in two rows. Features subtle animations,
 * hover effects, and a refined aesthetic that aligns with modern design principles.
 * Title: Art by Wasif
 */
const ModernArtworkGrid = () => {
  // Array of available artwork images from public/fanvue directory
  const artworkImages = [
    { name: 'Dark Sunflower', path: '/fanvue/Dark Sunflower.jpg' },
    { name: 'Eleven St. Things', path: '/fanvue/Eleven St. Things.jpg' },
    { name: 'Naorose Raya', path: '/fanvue/Naorose Raya.jpg' },
    { name: 'Reputation Artwork', path: '/fanvue/Reputation Artwork.png' },
    { name: 'Selena Gomez', path: '/fanvue/Selena Gomez.jpg' },
    { name: 'Sophia Lillis', path: '/fanvue/Sophia Lillis.jpg' },
    { name: 'The August', path: '/fanvue/The August.jpg' },
    { name: 'The Sunflower', path: '/fanvue/The Sunflower.jpg' },
  ];

  // All images will be the same size for a consistent, elegant look
  const getSpanClass = () => {
    // All items are the same size for a uniform contemporary look
    return 'grid-col-span-1 grid-row-span-1';
  };
  
  // Random subtle animation delay for a more organic feel
  const getRandomDelay = () => {
    return (Math.random() * 0.3).toFixed(2);
  };

  return (
    <div className="modern-artwork-grid-container">
      <h2 className="artwork-gallery-title">Art by Wasif</h2>
      <div className="modern-artwork-grid">
        {artworkImages.map((image, index) => {
          const spanClass = getSpanClass();
          const randomDelay = getRandomDelay();
          
          return (
            <div 
              key={index} 
              className={`modern-artwork-grid-item ${spanClass}`}
              style={{ 
                animationDelay: `${index * 0.1 + parseFloat(randomDelay)}s`,
                animationDuration: `${0.5 + parseFloat(randomDelay) * 0.5}s`
              }}
            >
              <div className="modern-artwork-card">
                <img 
                  src={image.path} 
                  alt={image.name} 
                  className="modern-artwork-image"
                  loading="lazy"
                  style={{ 
                    transitionDelay: `${parseFloat(randomDelay) * 0.2}s` 
                  }}
                />
                <div className="modern-artwork-overlay">
                  <span className="modern-artwork-title">{image.name}</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ModernArtworkGrid;