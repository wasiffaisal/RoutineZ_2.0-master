import React, { useState } from 'react';

/**
 * ModernButton Component
 * 
 * A collection of modern button styles following 2025 UI design trends.
 * Features various animations, morphism effects, and interactive states.
 * 
 * @param {Object} props - Component props
 * @param {ReactNode} props.children - Button content
 * @param {string} props.variant - Button style variant (default, primary, secondary, ghost, outline, link, gradient, morphism)
 * @param {string} props.size - Button size (sm, md, lg)
 * @param {string} props.className - Additional CSS classes
 * @param {boolean} props.isLoading - Loading state
 * @param {boolean} props.isDisabled - Disabled state
 * @param {string} props.animation - Animation type (none, pulse, float, shimmer, glow)
 * @param {Function} props.onClick - Click handler
 */
const ModernButton = ({
  children,
  variant = 'default',
  size = 'md',
  className = '',
  isLoading = false,
  isDisabled = false,
  animation = 'none',
  onClick,
  ...props
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  // Size classes
  const sizeClasses = {
    sm: 'h-8 px-3 text-xs rounded-lg',
    md: 'h-10 px-4 text-sm rounded-xl',
    lg: 'h-12 px-6 text-base rounded-2xl',
  };
  
  // Base button classes
  const baseClasses = `inline-flex items-center justify-center font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ${sizeClasses[size]}`;
  
  // Variant classes
  const variantClasses = {
    default: 'bg-primary text-primary-foreground hover:bg-primary/90 focus-visible:ring-primary',
    primary: 'bg-primary text-primary-foreground hover:bg-primary/90 focus-visible:ring-primary',
    secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/90 focus-visible:ring-secondary',
    ghost: 'hover:bg-accent hover:text-accent-foreground',
    outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
    link: 'text-primary underline-offset-4 hover:underline',
    gradient: 'bg-gradient-to-r from-ethereal-blue via-warm-yellow to-burnt-orange text-white',
    morphism: 'bg-background/80 backdrop-blur-md border border-background/20 shadow-lg hover:shadow-xl hover:bg-background/90',
  };
  
  // Animation classes
  const animationClasses = {
    none: '',
    pulse: 'animate-pulse',
    float: 'animate-float',
    shimmer: 'animate-shimmer overflow-hidden relative',
    glow: 'animate-glow',
  };
  
  // Special case for shimmer animation
  const shimmerOverlay = animation === 'shimmer' ? (
    <span className="absolute inset-0 -translate-x-full animate-shimmer bg-gradient-to-r from-transparent via-white/20 to-transparent" />
  ) : null;
  
  // Special case for glow animation
  const glowEffect = animation === 'glow' && isHovered ? (
    <span className="absolute inset-0 rounded-xl bg-gradient-to-r from-ethereal-blue via-warm-yellow to-burnt-orange opacity-30 blur-lg transition-opacity duration-500" />
  ) : null;
  
  // Loading spinner
  const loadingSpinner = isLoading ? (
    <svg className="mr-2 h-4 w-4 animate-spin" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
    </svg>
  ) : null;
  
  // Combine all classes
  const buttonClasses = `${baseClasses} ${variantClasses[variant]} ${animationClasses[animation]} ${className}`;
  
  return (
    <button
      className={buttonClasses}
      disabled={isDisabled || isLoading}
      onClick={onClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      {...props}
    >
      {glowEffect}
      {shimmerOverlay}
      <span className="relative flex items-center justify-center">
        {loadingSpinner}
        {children}
      </span>
    </button>
  );
};

export default ModernButton;