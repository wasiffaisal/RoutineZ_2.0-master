import React from 'react';

/**
 * MorphismCard Component
 * 
 * A modern UI component that implements the 2025 morphism design trend.
 * Creates a card with subtle blur effects, shadows, and depth for a modern look.
 * 
 * @param {Object} props - Component props
 * @param {React.ReactNode} props.children - Content to display inside the card
 * @param {string} props.className - Additional CSS classes
 * @param {string} props.variant - Card variant (default, glow, subtle)
 * @param {string} props.size - Card size (sm, md, lg)
 * @param {boolean} props.interactive - Whether the card has hover effects
 */
const MorphismCard = ({
  children,
  className = '',
  variant = 'default',
  size = 'md',
  interactive = false,
  ...props
}) => {
  // Define base styles
  const baseStyles = 'relative bg-white/80 dark:bg-slate-900/80 backdrop-blur-md rounded-morph transition-all duration-300';
  
  // Size variants
  const sizeStyles = {
    sm: 'p-3',
    md: 'p-5',
    lg: 'p-7',
  };
  
  // Visual variants
  const variantStyles = {
    default: 'shadow-morph-md border border-white/20 dark:border-slate-700/30',
    glow: 'shadow-morph-md shadow-morph-glow border border-white/30 dark:border-slate-700/40',
    subtle: 'shadow-morph-sm border border-white/10 dark:border-slate-800/20',
  };
  
  // Interactive hover effects
  const interactiveStyles = interactive 
    ? 'hover:shadow-morph-lg hover:scale-[1.02] cursor-pointer' 
    : '';
  
  // Combine all styles
  const cardStyles = `${baseStyles} ${sizeStyles[size]} ${variantStyles[variant]} ${interactiveStyles} ${className}`;
  
  return (
    <div className={cardStyles} {...props}>
      <div className="relative z-10">{children}</div>
      {variant === 'glow' && (
        <div className="absolute inset-0 bg-gradient-to-br from-primary/10 to-secondary/10 rounded-morph -z-10 animate-pulse opacity-70"></div>
      )}
    </div>
  );
};

export default MorphismCard;