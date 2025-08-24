import React from 'react';
import ModernButton from './modern-button';
import { RainbowButton } from './rainbow-button';
import './modern-button.css';

/**
 * ButtonShowcase Component
 * 
 * A showcase of all modern button styles and variants for the 2025 UI design.
 */
const ButtonShowcase = () => {
  return (
    <div className="p-6 space-y-8">
      <div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">Modern Button Variants</h2>
        <div className="flex flex-wrap gap-4">
          <ModernButton variant="default">Default</ModernButton>
          <ModernButton variant="primary">Primary</ModernButton>
          <ModernButton variant="secondary">Secondary</ModernButton>
          <ModernButton variant="ghost">Ghost</ModernButton>
          <ModernButton variant="outline">Outline</ModernButton>
          <ModernButton variant="link">Link</ModernButton>
          <ModernButton variant="gradient">Gradient</ModernButton>
          <ModernButton variant="morphism">Morphism</ModernButton>
          <RainbowButton>Rainbow</RainbowButton>
        </div>
      </div>
      
      <div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">Button Sizes</h2>
        <div className="flex flex-wrap items-center gap-4">
          <ModernButton size="sm" variant="primary">Small</ModernButton>
          <ModernButton size="md" variant="primary">Medium</ModernButton>
          <ModernButton size="lg" variant="primary">Large</ModernButton>
        </div>
      </div>
      
      <div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">Button Animations</h2>
        <div className="flex flex-wrap gap-4">
          <ModernButton variant="primary" animation="pulse">Pulse</ModernButton>
          <ModernButton variant="primary" animation="float">Float</ModernButton>
          <ModernButton variant="primary" animation="shimmer">Shimmer</ModernButton>
          <ModernButton variant="primary" animation="glow">Glow</ModernButton>
        </div>
      </div>
      
      <div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">Button States</h2>
        <div className="flex flex-wrap gap-4">
          <ModernButton variant="primary">Normal</ModernButton>
          <ModernButton variant="primary" isLoading>Loading</ModernButton>
          <ModernButton variant="primary" isDisabled>Disabled</ModernButton>
        </div>
      </div>
      
      <div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">Gradient Buttons</h2>
        <div className="flex flex-wrap gap-4">
          <ModernButton variant="gradient">Gradient</ModernButton>
          <ModernButton variant="gradient" animation="shimmer">Gradient + Shimmer</ModernButton>
          <ModernButton variant="gradient" animation="glow">Gradient + Glow</ModernButton>
        </div>
      </div>
      
      <div>
        <h2 className="text-2xl font-bold mb-4 text-foreground">Morphism Buttons</h2>
        <div className="flex flex-wrap gap-4 p-6 bg-gradient-to-r from-ethereal-blue/20 to-burnt-orange/20 rounded-xl">
          <ModernButton variant="morphism">Morphism</ModernButton>
          <ModernButton variant="morphism" animation="float">Morphism + Float</ModernButton>
          <ModernButton variant="morphism" animation="glow">Morphism + Glow</ModernButton>
        </div>
      </div>
    </div>
  );
};

export default ButtonShowcase;