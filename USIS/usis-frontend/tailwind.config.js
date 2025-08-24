/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Rainbow colors
        "color-1": "hsl(var(--color-1))",
        "color-2": "hsl(var(--color-2))",
        "color-3": "hsl(var(--color-3))",
        "color-4": "hsl(var(--color-4))",
        "color-5": "hsl(var(--color-5))",
        
        // 2025 Modern UI Colors
        "background": "hsl(var(--background))",
        "foreground": "hsl(var(--foreground))",
        "primary": "hsl(var(--primary))",
        "primary-foreground": "hsl(var(--primary-foreground))",
        "secondary": "hsl(var(--secondary))",
        "secondary-foreground": "hsl(var(--secondary-foreground))",
        "accent": "hsl(var(--accent))",
        "accent-foreground": "hsl(var(--accent-foreground))",
        "muted": "hsl(var(--muted))",
        "muted-foreground": "hsl(var(--muted-foreground))",
        "card": "hsl(var(--card))",
        "card-foreground": "hsl(var(--card-foreground))",
        "border": "hsl(var(--border))",
        "input": "hsl(var(--input))",
        "ring": "hsl(var(--ring))",
        "rich-red": "hsl(var(--rich-red))",
        "rich-red-light": "hsl(var(--rich-red-light))",
        "burnt-orange": "hsl(var(--burnt-orange))",
        "burnt-orange-light": "hsl(var(--burnt-orange-light))",
      },
      animation: {
        rainbow: "rainbow var(--speed, 2s) infinite linear",
        pulse: "pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite",
        float: "float 6s ease-in-out infinite",
        shimmer: "shimmer 2s linear infinite",
        morphTransition: "morphTransition 0.5s ease-out",
      },
      keyframes: {
        rainbow: {
          "0%": { "background-position": "0%" },
          "100%": { "background-position": "200%" },
        },
        pulse: {
          '0%, 100%': { opacity: 1 },
          '50%': { opacity: 0.5 },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
        morphTransition: {
          '0%': { filter: 'blur(8px)', opacity: 0.7 },
          '100%': { filter: 'blur(0)', opacity: 1 },
        },
      },
      boxShadow: {
        'morph-sm': '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06), inset 0 0 0 1px rgba(255, 255, 255, 0.1)',
        'morph-md': '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05), inset 0 0 0 1px rgba(255, 255, 255, 0.1)',
        'morph-lg': '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04), inset 0 0 0 1px rgba(255, 255, 255, 0.1)',
        'morph-glow': '0 0 15px 2px rgba(var(--card-glow), 0.3)',
        'morph-inner': 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.06)',
      },
      backdropFilter: {
        'morph': 'blur(8px) saturate(180%)',
      },
      borderRadius: {
        'morph': '1.5rem',
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
    require('@tailwindcss/forms'),
  ],
};