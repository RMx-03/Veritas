import React from 'react';
import { Upload, Scan, BarChart, CheckCircle } from 'lucide-react';

const HowItWorks = () => {
  const steps = [
    {
      icon: Upload,
      title: "Upload Your Label",
      description: "Take a photo or upload an image of a food product label for testing.",
      details: ["JPG, PNG supported", "Standard file sizes", "Basic upload functionality"]
    },
    {
      icon: Scan,
      title: "AI Analysis",
      description: "AI technology extracts nutrition facts and ingredients from your uploaded image.",
      details: ["Experimental accuracy", "Basic nutrition categories", "English text only"]
    },
    {
      icon: BarChart,
      title: "Get Insights",
      description: "Get basic nutrition information and simple analysis from the uploaded label.",
      details: ["Basic health info", "Simple ingredient list", "General suggestions"]
    },
    {
      icon: CheckCircle,
      title: "Make Better Choices",
      description: "Review the basic analysis results to learn about the food product.",
      details: ["Experimental results", "General information", "For testing purposes"]
    }
  ];

  return (
    <section className="py-12 sm:py-16 lg:py-20 bg-white">
      <div className="container-wide px-4 sm:px-6">
        {/* Section Header */}
        <div className="text-center mb-20">
          <h2 className="text-display text-5xl lg:text-6xl text-neutral-900 mb-6 text-balance">
            How Veritas 
            <span className="text-gradient-brand block">Works</span>
          </h2>
          <p className="text-base sm:text-lg lg:text-xl text-neutral-600 max-w-2xl sm:max-w-3xl mx-auto text-balance">
            Upload a photo and get basic AI analysis. This is an early prototype for 
            testing and feedback.
          </p>
        </div>

        {/* Steps Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 sm:gap-8">
          {steps.map((step, index) => {
            const Icon = step.icon;
            return (
              <div 
                key={index} 
                className="relative group animate-fade-in"
                style={{ animationDelay: `${index * 100}ms` }}
              >
                {/* Connection Line (hidden on mobile) */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-full w-6 h-0.5 bg-gradient-to-r from-brand-blue-300 to-brand-teal-300 z-10"></div>
                )}
                
                {/* Step Card */}
                <div className="card-hover bg-white relative z-20">
                  {/* Step Number */}
                  <div className="bg-white p-6 sm:p-8 rounded-3xl shadow-soft border border-neutral-100 text-center group hover:shadow-medium transition-all duration-300">
                    {index + 1}
                  </div>
                  
                  {/* Icon */}
                  <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-4 sm:mb-6 bg-gradient-to-br from-brand-blue-500 to-brand-blue-600 rounded-2xl flex items-center justify-center group-hover:scale-110 transition-transform duration-300">
                    <Icon className="w-8 h-8 text-brand-blue-600" />
                  </div>
                  
                  {/* Content */}
                  <h2 className="text-2xl sm:text-3xl lg:text-4xl font-bold text-neutral-900 mb-4 sm:mb-6">{step.title}</h2>
                  <p className="text-sm sm:text-base text-neutral-600 mb-4 sm:mb-6 leading-relaxed">{step.description}</p>
                  
                  {/* Details List */}
                  <ul className="space-y-2">
                    {step.details.map((detail, detailIndex) => (
                      <li key={detailIndex} className="flex items-center space-x-2 text-sm text-neutral-500">
                        <div className="w-1.5 h-1.5 bg-brand-teal-400 rounded-full"></div>
                        <span>{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            );
          })}
        </div>

      </div>
    </section>
  );
};

export default HowItWorks;
