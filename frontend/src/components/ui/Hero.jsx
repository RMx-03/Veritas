import React from 'react';
import { ArrowRight, Sparkles, Shield, Zap } from 'lucide-react';

const Hero = ({ onGetStarted }) => {
  return (
    <section className="relative min-h-screen lg:min-h-[90vh] bg-gradient-to-br from-brand-blue-50 via-white to-brand-teal-50 flex items-center overflow-hidden">
        {/* Background image with blur, gradient wash and noise overlay */}
        <div className="absolute inset-0 z-0" aria-hidden="true">
          <div className="absolute inset-0 bg-[url('/HeroSection.png')] bg-cover bg-center blur-xl scale-105"></div>
          <div className="absolute inset-0 bg-gradient-to-b from-white/80 via-white/60 to-white/80"></div>
          <div className="absolute inset-0 noise-overlay"></div>
        </div>

        {/* Decorative blobs (kept subtle and below content) */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-brand-blue-100 rounded-full blur-3xl opacity-30 z-0"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-brand-teal-100 rounded-full blur-3xl opacity-30 z-0"></div>
      
      <div className="container-wide relative z-10 px-4 sm:px-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 sm:gap-12 lg:gap-20 items-center">
          {/* Left Column - Content */}
          <div className="animate-fade-in">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-brand-blue-100 text-brand-blue-700 px-4 py-2 rounded-full text-sm font-semibold mb-8">
              <Sparkles className="w-4 h-4" />
              <span>MVP - Early Version</span>
            </div>
            
            {/* Veritas Brand */}
            <div className="flex items-center space-x-4 mb-6">
              <img 
                src="/VeritasLogo.png" 
                alt="Veritas Logo" 
                className="h-10 w-auto"
              />
              <h2 className="text-3xl sm:text-4xl font-black text-neutral-900 tracking-tight">
                Veritas
              </h2>
            </div>
            
            {/* Main Headline */}
            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-black text-neutral-900 leading-none mb-4 sm:mb-6 tracking-tight">
              Your Pocket
              <span className="text-gradient-brand block">
                Nutrition Scientist
              </span>
            </h1>
            
            {/* Subheadline */}
            <p className="text-base sm:text-lg md:text-xl lg:text-2xl text-neutral-600 mb-6 sm:mb-8 leading-relaxed max-w-xl sm:max-w-2xl mx-auto lg:mx-0">
              Upload a food label photo and get AI-powered nutrition analysis. 
              This is an early version for testing purposes.
            </p>
            
            
            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-3 sm:gap-4 items-center justify-center lg:justify-start mb-8 sm:mb-12">
              <button 
                onClick={onGetStarted}
                className="btn-primary btn-lg w-full sm:w-auto min-w-[200px] group"
                aria-label="Start analyzing your first nutrition label"
              >
                <span>Analyze Your First Label</span>
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </button>
              <button 
                onClick={() => {
                  const howItWorksSection = document.getElementById('how-it-works-section');
                  howItWorksSection?.scrollIntoView({ behavior: 'smooth' });
                }}
                className="btn-secondary btn-lg w-full sm:w-auto min-w-[180px] group"
                aria-label="Learn how Veritas works"
              >
                <span>See How It Works</span>
              </button>
            </div>
            
            {/* Trust Indicators */}
            <div className="flex items-center space-x-6 mt-12 pt-8 border-t border-neutral-200">
              <div className="flex items-center space-x-2 text-neutral-600">
                <Shield className="w-5 h-5 text-brand-teal-500" />
                <span className="text-sm">GDPR Compliant</span>
              </div>
              <div className="flex items-center space-x-2 text-neutral-600">
                <Zap className="w-5 h-5 text-brand-blue-500" />
                <span className="text-sm">Instant Results</span>
              </div>
              <div className="flex items-center space-x-2 text-neutral-600">
                <Sparkles className="w-5 h-5 text-brand-purple-500" />
                <span className="text-sm">AI-Powered</span>
              </div>
            </div>
          </div>
          
          {/* Right Column - Visual */}
          <div className="relative hidden sm:block mt-8 lg:mt-0 animate-slide-up animation-delay-200">
            {/* Phone Mockup Container */}
            <div className="relative z-10 bg-white rounded-3xl shadow-2xl p-4 sm:p-6 lg:p-8 max-w-sm sm:max-w-md mx-auto">
              
              {/* Main Phone Interface */}
              <div className="bg-neutral-900 rounded-[3rem] p-2 shadow-2xl">
                <div className="bg-white rounded-[2.5rem] overflow-hidden h-[600px] relative">
                  {/* Phone Screen Content */}
                  <div className="p-6 h-full flex flex-col">
                    {/* Header */}
                    <div className="flex items-center justify-between mb-6">
                      <img 
                        src="/VeritasLogo.png" 
                        alt="Veritas Logo" 
                        className="h-6 w-auto"
                      />
                      <div className="text-sm font-medium text-neutral-700">Nutrition Analysis</div>
                      <div className="w-8 h-8"></div>
                    </div>
                    
                    {/* Sample Analysis Card */}
                    <div className="bg-neutral-50 rounded-2xl p-4 mb-4">
                      <div className="h-32 bg-neutral-200 rounded-xl mb-3 flex items-center justify-center">
                        <span className="text-neutral-500 text-xs">Food Label</span>
                      </div>
                      <div className="text-sm font-semibold text-neutral-900 mb-1">Organic Granola Bar</div>
                      <div className="text-xs text-neutral-600">Analyzing ingredients...</div>
                    </div>
                    
                    {/* Progress Indicator */}
                    <div className="mb-4">
                      <div className="flex justify-between text-xs text-neutral-600 mb-2">
                        <span>Analysis Progress</span>
                        <span>87%</span>
                      </div>
                      <div className="h-2 bg-neutral-200 rounded-full overflow-hidden">
                        <div className="h-full bg-brand-blue-600 rounded-full animate-pulse" style={{width: '87%'}}></div>
                      </div>
                    </div>
                    
                    {/* Sample Results */}
                    <div className="space-y-3 flex-1">
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-xl">
                        <span className="text-sm text-neutral-700">Protein Content</span>
                        <span className="nutrition-excellent">Excellent</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-amber-50 rounded-xl">
                        <span className="text-sm text-neutral-700">Sugar Level</span>
                        <span className="nutrition-moderate">Moderate</span>
                      </div>
                      <div className="flex items-center justify-between p-3 bg-green-50 rounded-xl">
                        <span className="text-sm text-neutral-700">Fiber Content</span>
                        <span className="nutrition-good">Good</span>
                      </div>
                    </div>
                    
                    {/* Bottom Action */}
                    <div className="mt-auto">
                      <div className="w-full bg-brand-blue-500 text-white py-3 rounded-xl text-center text-sm font-semibold">
                        View Detailed Report
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;
