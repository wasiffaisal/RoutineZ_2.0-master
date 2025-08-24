import React, { useState, useEffect } from 'react';
import { ArrowRight, Calendar, Zap, Users, Clock, Shield, Star, Download, Sparkles, Target, CheckCircle, BarChart3, BookOpen, Brain, Award, Heart } from 'lucide-react';
import './LandingPage.css';

const LandingPage = ({ onNavigate }) => {
  const [isVisible, setIsVisible] = useState(false);
  const [activeFeature, setActiveFeature] = useState(0);

  const heroFeatures = [
    "Real-time BracU Connect Data",
    "AI-Powered Optimization", 
    "Instant Conflict Detection",
    "Commute-Optimized Schedules",
    "Faculty & Section Selection",
    "Lab Schedule Integration"
  ];

  useEffect(() => {
    setIsVisible(true);
    
    // Animation for text items appearing one at a time in the same position
    const interval = setInterval(() => {
      // Fade out current feature
      setActiveFeature(prev => {
        // Calculate next feature index
        const nextIndex = (prev + 1) % heroFeatures.length;
        return nextIndex;
      });
    }, 3000); // Change text every 3 seconds
    
    return () => clearInterval(interval);
  }, [heroFeatures.length]);

  const features = [
    {
      icon: <Zap className="w-8 h-8" />,
      title: "Live Data Integration",
      description: "Connects directly to BracU Connect for real-time course availability, seat counts, and schedule updates.",
      color: "from-blue-500 to-cyan-500",
      stats: "100% Live"
    },
    {
      icon: <Brain className="w-8 h-8" />,
      title: "AI Smart Scheduling",
      description: "Advanced AI algorithms create optimal schedules based on your preferences, commute, and course requirements.",
      color: "from-purple-500 to-pink-500",
      stats: "Powered by Gemini"
    },
    {
      icon: <Shield className="w-8 h-8" />,
      title: "Conflict Prevention",
      description: "Automatically detects and prevents class, lab, and exam conflicts before they happen.",
      color: "from-green-500 to-emerald-500",
      stats: "Zero Conflicts"
    },
    {
      icon: <Clock className="w-8 h-8" />,
      title: "Commute Optimization",
      description: "Choose between 'Live Far' (more classes/day) or 'Live Near' (spread out) preferences.",
      color: "from-orange-500 to-red-500",
      stats: "Smart Gaps"
    },
    {
      icon: <Users className="w-8 h-8" />,
      title: "Faculty Selection",
      description: "Pick your preferred faculty members and specific sections with detailed teaching schedules.",
      color: "from-indigo-500 to-purple-500",
      stats: "All Faculty"
    },
    {
      icon: <BookOpen className="w-8 h-8" />,
      title: "Lab Integration",
      description: "Never miss lab timings - automatically includes lab schedules in your routine planning.",
      color: "from-teal-500 to-blue-500",
      stats: "Full Coverage"
    }
  ];

  const benefits = [
    {
      icon: <Star className="w-6 h-6" />,
      title: "Save Hours",
      description: "Generate perfect routines in seconds, not hours of manual planning"
    },
    {
      icon: <CheckCircle className="w-6 h-6" />,
      title: "Avoid Mistakes",
      description: "Eliminate human error in schedule creation with intelligent validation"
    },
    {
      icon: <BarChart3 className="w-6 h-6" />,
      title: "Better Planning",
      description: "Get a clear visual preview of your entire semester before registration"
    },
    {
      icon: <Download className="w-6 h-6" />,
      title: "Easy Export",
      description: "Download and compare multiple schedule drafts before finalizing"
    }
  ];

  const testimonials = [
    {
      quote: "RoutineZ saved me 3+ hours during advising week! The AI suggestions were spot-on and helped me create the perfect schedule without any conflicts.",
      name: "Anonymous Student"
    },
    {
      quote: "Finally, no more Excel sheets and manual checking. This is exactly what BracU needed! I was able to balance my work and study commitments perfectly.",
      name: "Anonymous Student"
    },
    {
      quote: "The commute optimization feature is genius. My daily travel time reduced by 40%. Now I can focus more on studying instead of being stuck in traffic.",
      name: "Anonymous Student"
    },
    {
      quote: "Before RoutineZ, I always ended up with awkward gaps between classes. Now my schedule is optimized with just the right breaks for lunch and study time.",
      name: "Anonymous Student"
    },
    {
      quote: "Registration used to be so stressful! With RoutineZ, I was able to plan multiple schedule options and choose the best one for my lifestyle.",
      name: "Anonymous Student"
    }
  ];

  return (
    <div className="landing-container">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-background">
          <div className="hero-grid"></div>
          <div className="hero-gradient"></div>
        </div>
        
        <div className="hero-content">
          <h1 className={`hero-title ${isVisible ? 'animate' : ''}`}>
            <span className="gradient-text">RoutineZ</span>
            <br />
            <span className="hero-subtitle-text">Smart Course Scheduling</span>
          </h1>
          
          <p className={`hero-description ${isVisible ? 'animate' : ''}`}>
            Say goodbye to registration chaos! RoutineZ uses live BracU Connect data 
            to generate conflict-free, AI-optimized schedules in seconds. Perfect for 
            BRAC University students.
          </p>
          
          <div className={`hero-features ${isVisible ? 'animate' : ''}`}>
            <div className="feature-carousel">
              {heroFeatures.map((feature, index) => (
                <span 
                  key={index}
                  className={`feature-item ${activeFeature === index ? 'active' : ''}`}
                >
                  {feature}
                </span>
              ))}
            </div>
          </div>
          
          <div className={`hero-cta ${isVisible ? 'animate' : ''}`}>
            <button 
              className="cta-primary"
              onClick={() => onNavigate('routine')}
            >
              <Sparkles className="w-5 h-5" />
              Generate Your Routine
              <ArrowRight className="w-5 h-5" />
            </button>
            
            <button 
              className="cta-secondary"
              onClick={() => onNavigate('seats')}
            >
              Check Live Seats
            </button>
          </div>
          
          <div className="hero-stats">
            <div className="stat">
              <div className="stat-number">5,000+</div>
              <div className="stat-label">Students Helped</div>
            </div>
            <div className="stat">
              <div className="stat-number">15,000+</div>
              <div className="stat-label">Routines Generated</div>
            </div>
            <div className="stat">
              <div className="stat-number">99.9%</div>
              <div className="stat-label">Conflict-Free</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">
              Why <span className="gradient-text">RoutineZ</span> is a Game-Changer
            </h2>
            <p className="section-subtitle">
              Built specifically for BRAC University students with features that actually matter
            </p>
          </div>
          
          <div className="features-grid">
            {features.map((feature, index) => (
              <div 
                key={index} 
                className={`feature-card ${isVisible ? 'animate' : ''}`}
                style={{ transitionDelay: `${index * 0.1}s` }}
              >
                <div className={`feature-icon ${feature.color}`}>
                  {feature.icon}
                </div>
                <div className="feature-content">
                  <h3 className="feature-title">{feature.title}</h3>
                  <p className="feature-description">{feature.description}</p>
                  <div className="feature-stats">{feature.stats}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <div className="container">
          <div className="benefits-content">
            <div className="benefits-text">
              <h2 className="section-title">
                Transform Your Registration Experience
              </h2>
              <p className="section-subtitle">
                From hours of frustration to seconds of perfection
              </p>
              
              <div className="benefits-list">
                {benefits.map((benefit, index) => (
                  <div 
                    key={index}
                    className={`benefit-item ${isVisible ? 'animate' : ''}`}
                    style={{ transitionDelay: `${index * 0.1}s` }}
                  >
                    <div className="benefit-icon">
                      {benefit.icon}
                    </div>
                    <div>
                      <h4 className="benefit-title">{benefit.title}</h4>
                      <p className="benefit-description">{benefit.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
            
            <div className="benefits-visual">
              <div className="visual-card">
                <div className="visual-header">
                  <div className="visual-dots">
                    <div></div>
                    <div></div>
                    <div></div>
                  </div>
                </div>
                <div className="visual-content">
                  <div className="visual-schedule">
                    <div className="schedule-item">
                      <span>CSE101 - A</span>
                      <span className="time">9:30 AM</span>
                    </div>
                    <div className="schedule-item">
                      <span>MAT201 - B</span>
                      <span className="time">11:00 AM</span>
                    </div>
                    <div className="schedule-item">
                      <span>PHY101 - L1</span>
                      <span className="time">2:00 PM</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Creator Message Section */}
      <section className="creator-message-section">
        <div className="container">
          <div className="creator-card">
            <div className="creator-visual">
              <div className="creator-photo">
                <div className="photo-placeholder">
                  <img 
                    src={process.env.PUBLIC_URL + '/images/developer.jpg'} 
                    alt="Developer" 
                    style={{
                      width: '100%',
                      height: '100%',
                      objectFit: 'cover',
                      borderRadius: '50%',
                      /* Enhanced hardware acceleration */
                      transform: 'translateZ(0)',
                      willChange: 'transform',
                      /* Remove filters completely for better performance */
                      backfaceVisibility: 'hidden'
                    }}
                    loading="eager"
                    decoding="async"
                    onError={(e) => {
                      console.log('Image failed to load:', e.target.src);
                      // Fallback to a simple div with initials
                      e.target.style.display = 'none';
                      const placeholder = e.target.parentNode;
                      const fallback = document.createElement('div');
                      fallback.style.cssText = 'display: flex; align-items: center; justify-content: center; color: white; font-size: 48px; font-weight: bold; background: linear-gradient(135deg, #3b82f6, #8b5cf6); width: 100%; height: 100%; border-radius: 50%;';
                      fallback.textContent = 'A';
                      placeholder.appendChild(fallback);
                    }}
                  />
                </div>
                <div className="photo-glow"></div>
              </div>
              <div className="creator-details">
                <h3 className="creator-name">Wasif Faisal</h3>
                <p className="creator-title">Creator & Developer</p>
                <div className="creator-badges">
                  <span className="badge">BRACU CS</span>
                  <span className="badge">Full Stack Dev</span>
                </div>
              </div>
            </div>
            <div className="creator-message">
              <h4 className="message-title">A Personal Note to Every BRACU Student</h4>
              <div className="message-content">
                <p>
                  &ldquo;I built RoutineZ because I experienced firsthand the frustration of manual schedule planning during my time at BRACU. 
                  Those late nights comparing sections, calculating time slots, and still ending up with conflicts - I knew there had to be a better way.
                </p>
                <p>
                  This platform isn&apos;t just about automation; it&apos;s about giving you back your time and peace of mind. 
                  Every feature was designed with real student needs in mind, tested by hundreds of your peers, and refined based on actual feedback.
                </p>
                <p>
                  My hope is that RoutineZ becomes your trusted companion throughout your BRACU journey, 
                  helping you focus on what truly matters - your learning, growth, and making the most of your university experience.&rdquo;
                </p>
              </div>
              <div className="message-footer">
                <span className="signature">- Wasif</span>
                <div className="social-links">
                  <a href="https://github.com/cswasif" target="_blank" rel="noopener noreferrer" className="social-link">
                    <svg viewBox="0 0 24 24" className="social-icon">
                      <path d="M12 0C5.374 0 0 5.373 0 12 0 17.302 3.438 21.8 8.207 23.387c.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.300 24 12c0-6.627-5.373-12-12-12z"/>
                    </svg>
                  </a>
                  <a href="https://linkedin.com/in/cswasif" target="_blank" rel="noopener noreferrer" className="social-link">
                    <svg viewBox="0 0 24 24" className="social-icon">
                      <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                    </svg>
                  </a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="testimonials-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">
              Loved by <span className="gradient-text">BRACU Students</span>
            </h2>
            <p className="section-subtitle">
              Real stories from anonymous students who transformed their registration experience
            </p>
          </div>
          
          <div className="testimonials-grid">
            {testimonials.map((testimonial, index) => (
              <div 
                key={index}
                className={`testimonial-card ${isVisible ? 'animate' : ''}`}
                style={{ transitionDelay: `${index * 0.15}s` }}
              >
                <div className="testimonial-quote">
                  &ldquo;{testimonial.quote}&rdquo;
                </div>
                <div className="testimonial-author">
                  <div className="author-avatar">
                    {testimonial.name.charAt(0)}
                  </div>
                  <div>
                    <div className="author-name">{testimonial.name}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta-section">
        <div className="container">
          <div className="cta-content">
            <div className="cta-text">
              <h2 className="cta-title">
                Ready to Create Your Perfect Schedule?
              </h2>
              <p className="cta-subtitle">
                Join thousands of BRACU students who&apos;ve already revolutionized their registration process
              </p>
            </div>
            
            <div className="cta-actions">
              <button 
                className="cta-primary large"
                onClick={() => onNavigate('routine')}
              >
                <Target className="w-5 h-5" />
                Start Building Your Routine
                <ArrowRight className="w-5 h-5" />
              </button>
              
              <div className="cta-features">
                <span className="feature-tag">
                  <CheckCircle className="w-4 h-4" />
                  100% Free
                </span>
                <span className="feature-tag">
                  <CheckCircle className="w-4 h-4" />
                  No Login Required
                </span>
                <span className="feature-tag">
                  <CheckCircle className="w-4 h-4" />
                  Mobile Friendly
                </span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-brand-section">
              <h3 className="footer-brand">RoutineZ</h3>
              <p className="footer-description">Simplifying course registration for BRACU students with AI-powered scheduling and conflict detection.</p>
              <div className="footer-social">
                <a href="#" onClick={() => window.open('https://github.com/cswasif/routinez', '_blank')} aria-label="GitHub">
                  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 19c-5 1.5-5-2.5-7-3m14 6v-3.87a3.37 3.37 0 0 0-.94-2.61c3.14-.35 6.44-1.54 6.44-7A5.44 5.44 0 0 0 20 4.77 5.07 5.07 0 0 0 19.91 1S18.73.65 16 2.48a13.38 13.38 0 0 0-7 0C6.27.65 5.09 1 5.09 1A5.07 5.07 0 0 0 5 4.77a5.44 5.44 0 0 0-1.5 3.78c0 5.42 3.3 6.61 6.44 7A3.37 3.37 0 0 0 9 18.13V22"></path></svg>
                </a>
              </div>
            </div>
            
            <div className="footer-column">
              <h4>Quick Links</h4>
              <ul>
                <li><a href="#">Home</a></li>
                <li><a href="#features">Features</a></li>
                <li><a href="#testimonials">Testimonials</a></li>
                <li><a href="/app">App Dashboard</a></li>
              </ul>
            </div>
              
            <div className="footer-column">
              <h4>Support</h4>
              <ul>
                <li><a href="#" onClick={() => window.open('https://github.com/cswasif/routinez', '_blank')}>GitHub</a></li>
                <li><a href="#">Feedback</a></li>
                <li><a href="#">Report Bug</a></li>
                <li><a href="#">Contact Us</a></li>
              </ul>
            </div>
          </div>
          
          <hr className="footer-divider" />
          
          <div className="footer-bottom">
            <p>&copy; {new Date().getFullYear()} RoutineZ. Built for BRAC University students.</p>
            <p>Made with <span className="footer-heart">❤</span> by Wasif Faisal</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;