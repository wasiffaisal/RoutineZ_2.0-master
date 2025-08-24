import React from 'react';
import MorphismCard from './morphism-card';

/**
 * BentoGrid Component
 * 
 * A modern 2025 UI component that implements the Bento Grid layout trend.
 * Creates a responsive grid with different sized cards in a visually appealing arrangement.
 * 
 * @param {Object} props - Component props
 * @param {Array} props.items - Array of items to display in the grid
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.gap - Gap between grid items (sm, md, lg)
 */
const BentoGrid = ({
  items = [],
  className = '',
  gap = 'md',
  ...props
}) => {
  // Define gap styles
  const gapStyles = {
    sm: 'gap-3',
    md: 'gap-4',
    lg: 'gap-6',
  };
  
  // Base grid styles
  const gridStyles = `grid grid-cols-1 md:grid-cols-3 ${gapStyles[gap]} ${className}`;
  
  // Default span configurations for different positions
  const getSpanClass = (index) => {
    // Create visually interesting layout patterns based on index
    const patterns = [
      'md:col-span-2 md:row-span-2', // Featured (large)
      'md:col-span-1 md:row-span-1', // Standard
      'md:col-span-1 md:row-span-1', // Standard
      'md:col-span-1 md:row-span-2', // Tall
      'md:col-span-2 md:row-span-1', // Wide
      'md:col-span-1 md:row-span-1', // Standard
      'md:col-span-1 md:row-span-1', // Standard
      'md:col-span-2 md:row-span-1', // Wide
      'md:col-span-1 md:row-span-1', // Standard
    ];
    
    return patterns[index % patterns.length];
  };

  return (
    <div className={gridStyles} {...props}>
      {items.map((item, index) => {
        const spanClass = item.span || getSpanClass(index);
        const isFeature = spanClass.includes('col-span-2') && spanClass.includes('row-span-2');
        
        return (
          <div key={index} className={`${spanClass} min-h-[200px]`}>
            <MorphismCard 
              variant={item.variant || (isFeature ? 'glow' : 'default')}
              className="h-full w-full overflow-hidden"
              interactive={item.interactive !== undefined ? item.interactive : true}
            >
              {item.content}
            </MorphismCard>
          </div>
        );
      })}
    </div>
  );
};

export default BentoGrid;