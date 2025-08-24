import React, { useState, useEffect } from 'react';
import TextTransition from './text-transition';
import './text-transition.css';

const TextTransitionShowcase = () => {
  const [activeIndex, setActiveIndex] = useState(0);
  const [activeType, setActiveType] = useState('fade');
  
  const textExamples = [
    'Modern UI Design 2025',
    'Ethereal Blues & Warm Yellows',
    'Interactive Experiences',
    'Morphism Effects ✨',
    'Dynamic Typography 🚀'
  ];

  const transitionTypes = [
    'fade',
    'slide',
    'typewriter',
    'wave',
    'blur',
    'scale'
  ];

  useEffect(() => {
    const textInterval = setInterval(() => {
      setActiveIndex((prev) => (prev + 1) % textExamples.length);
    }, 3000);

    const typeInterval = setInterval(() => {
      setActiveType((prev) => {
        const currentIndex = transitionTypes.indexOf(prev);
        return transitionTypes[(currentIndex + 1) % transitionTypes.length];
      });
    }, 9000);

    return () => {
      clearInterval(textInterval);
      clearInterval(typeInterval);
    };
  }, []);

  return (
    <div className="text-transition-showcase">
      <h2 className="showcase-title">Text Transition Effects</h2>
      
      <div className="showcase-container">
        <div className="showcase-main">
          <div className="transition-type-label">
            Animation Type: <span className="transition-type-value">{activeType}</span>
          </div>
          
          <div className="showcase-text-container">
            <TextTransition 
              text={textExamples[activeIndex]}
              type={activeType}
              duration={0.75}
              spring={activeType !== 'typewriter' && activeType !== 'wave'}
              className="showcase-text"
            />
          </div>
        </div>

        <div className="showcase-examples">
          <h3>Transition Types</h3>
          <div className="transition-types-grid">
            {transitionTypes.map((type) => (
              <div 
                key={type}
                className={`transition-type-card ${type === activeType ? 'active' : ''}`}
                onClick={() => setActiveType(type)}
              >
                <span className="transition-name">{type}</span>
                <div className="transition-preview">
                  <TextTransition 
                    text="Preview"
                    type={type}
                    duration={0.5}
                    spring={type !== 'typewriter' && type !== 'wave'}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="showcase-examples">
          <h3>Special Effects</h3>
          <div className="special-effects-grid">
            <div className="effect-card">
              <span className="effect-name">Gradient Text</span>
              <div className="effect-preview">
                <TextTransition 
                  text="Colorful Gradient"
                  type="fade"
                  duration={0.5}
                  className="gradient-text"
                />
              </div>
            </div>
            <div className="effect-card">
              <span className="effect-name">3D Text</span>
              <div className="effect-preview">
                <TextTransition 
                  text="Depth Effect"
                  type="scale"
                  duration={0.5}
                  className="text-3d"
                />
              </div>
            </div>
            <div className="effect-card">
              <span className="effect-name">Glow Text</span>
              <div className="effect-preview">
                <TextTransition 
                  text="Ethereal Glow"
                  type="blur"
                  duration={0.5}
                  className="text-glow"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TextTransitionShowcase;