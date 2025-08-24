import React from 'react';
import './modern-typography.css';

/**
 * TypographyShowcase Component
 * 
 * A showcase of all modern typography styles for the 2025 UI design.
 * Demonstrates big typography, gradients, emoticons, and various text styles.
 */
const TypographyShowcase = () => {
  return (
    <div className="p-6 space-y-12 max-w-4xl mx-auto">
      <div>
        <h2 className="h2 mb-6">2025 Typography Showcase</h2>
        
        <div className="space-y-8">
          {/* Big Typography Section */}
          <section>
            <h3 className="h3 mb-4">Big Typography</h3>
            <div className="space-y-6">
              <div>
                <p className="text-mega">MEGA TEXT</p>
                <p className="text-mega-outline">OUTLINE</p>
              </div>
            </div>
          </section>
          
          {/* Headings Section */}
          <section>
            <h3 className="h3 mb-4">Headings</h3>
            <div className="space-y-4">
              <h1 className="h1">Heading 1</h1>
              <h2 className="h2">Heading 2</h2>
              <h3 className="h3">Heading 3</h3>
              <h4 className="h4">Heading 4</h4>
              <h5 className="h5">Heading 5</h5>
              <h6 className="h6">Heading 6</h6>
            </div>
          </section>
          
          {/* Body Text Section */}
          <section>
            <h3 className="h3 mb-4">Body Text</h3>
            <div className="space-y-4">
              <p className="text-lead">This is lead text, slightly larger than normal body text. It's often used for introductory paragraphs or to emphasize important information.</p>
              <p className="text-body">This is regular body text. It's used for the main content of your website or application. The font size, line height, and spacing are optimized for readability.</p>
              <p className="text-small">This is small text, used for less important information or when space is limited.</p>
              <p className="text-xs">This is extra small text, typically used for captions, footnotes, or legal text.</p>
              <p className="text-mono">This is monospace text, often used for code snippets or technical information.</p>
            </div>
          </section>
          
          {/* Text Effects Section */}
          <section>
            <h3 className="h3 mb-4">Text Effects</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="h4 mb-2">Gradient Text</h4>
                <p className="text-gradient text-2xl font-bold">Ethereal Blue to Yellow</p>
                <p className="text-gradient-reverse text-2xl font-bold mt-2">Yellow to Burnt Orange</p>
              </div>
              <div>
                <h4 className="h4 mb-2">Outline & Glow</h4>
                <p className="text-outline text-2xl font-bold">Outline Text</p>
                <p className="text-glow text-2xl font-bold mt-2 text-ethereal-blue">Glowing Text</p>
              </div>
              <div>
                <h4 className="h4 mb-2">Letter Spacing</h4>
                <p className="text-uppercase text-xl font-bold">Uppercase Wide</p>
                <p className="text-spaced text-xl font-bold mt-2">Extra Wide Spacing</p>
                <p className="text-tight text-xl font-bold mt-2">Tight Spacing</p>
              </div>
              <div>
                <h4 className="h4 mb-2">Emoticons</h4>
                <p className="text-xl">
                  Regular text with <span className="text-emoticon">✨</span> emoticon
                </p>
                <p className="text-xl mt-2">
                  Text with <span className="text-emoticon emoticon-large">🚀</span> large emoticon
                </p>
                <p className="text-xl mt-2">
                  <span className="text-emoticon">🌈</span> <span className="text-gradient font-bold">Gradient</span> <span className="text-emoticon">✨</span>
                </p>
              </div>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
};

export default TypographyShowcase;