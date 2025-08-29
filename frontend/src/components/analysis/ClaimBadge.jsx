import React from 'react';
import { CheckCircle, AlertTriangle, XCircle, Info } from 'lucide-react';

const ClaimBadge = ({ level, size = 'md', className = '' }) => {
  const configs = {
    excellent: {
      bg: 'bg-emerald-100',
      text: 'text-emerald-800',
      border: 'border-emerald-200',
      icon: CheckCircle,
      label: 'Excellent',
      description: 'Highly nutritious choice'
    },
    good: {
      bg: 'bg-lime-100',
      text: 'text-lime-800',
      border: 'border-lime-200',
      icon: CheckCircle,
      label: 'Good',
      description: 'Generally healthy option'
    },
    moderate: {
      bg: 'bg-amber-100',
      text: 'text-amber-800',
      border: 'border-amber-200',
      icon: Info,
      label: 'Moderate',
      description: 'Consume in moderation'
    },
    poor: {
      bg: 'bg-orange-100',
      text: 'text-orange-800',
      border: 'border-orange-200',
      icon: AlertTriangle,
      label: 'Poor',
      description: 'Consider alternatives'
    },
    critical: {
      bg: 'bg-red-100',
      text: 'text-red-800',
      border: 'border-red-200',
      icon: XCircle,
      label: 'Critical',
      description: 'Avoid regular consumption'
    }
  };

  const sizes = {
    sm: {
      container: 'px-2 py-1 text-xs',
      icon: 'w-3 h-3',
      text: 'text-xs'
    },
    md: {
      container: 'px-3 py-1.5 text-sm',
      icon: 'w-4 h-4',
      text: 'text-sm'
    },
    lg: {
      container: 'px-4 py-2 text-base',
      icon: 'w-5 h-5',
      text: 'text-base'
    }
  };

  const config = configs[level] || configs.moderate;
  const sizeConfig = sizes[size];
  const Icon = config.icon;

  return (
    <div className={`
      inline-flex items-center space-x-2 rounded-full font-semibold border
      ${config.bg} ${config.text} ${config.border} ${sizeConfig.container} ${className}
    `}>
      <Icon className={sizeConfig.icon} />
      <span className={sizeConfig.text}>{config.label}</span>
    </div>
  );
};

// Extended version with description
export const ClaimBadgeExtended = ({ level, showDescription = true, className = '' }) => {
  const configs = {
    excellent: {
      bg: 'bg-emerald-50',
      text: 'text-emerald-900',
      border: 'border-emerald-200',
      accent: 'bg-emerald-500',
      icon: CheckCircle,
      label: 'Excellent Choice',
      description: 'This product is highly nutritious with beneficial ingredients and minimal processing.',
      score: '80-100'
    },
    good: {
      bg: 'bg-lime-50',
      text: 'text-lime-900',
      border: 'border-lime-200',
      accent: 'bg-lime-500',
      icon: CheckCircle,
      label: 'Good Choice',
      description: 'A generally healthy option with good nutritional value and quality ingredients.',
      score: '60-79'
    },
    moderate: {
      bg: 'bg-amber-50',
      text: 'text-amber-900',
      border: 'border-amber-200',
      accent: 'bg-amber-500',
      icon: Info,
      label: 'Moderate Choice',
      description: 'Acceptable for occasional consumption, but consider healthier alternatives.',
      score: '40-59'
    },
    poor: {
      bg: 'bg-orange-50',
      text: 'text-orange-900',
      border: 'border-orange-200',
      accent: 'bg-orange-500',
      icon: AlertTriangle,
      label: 'Poor Choice',
      description: 'Limited nutritional value with concerning ingredients. Consume sparingly.',
      score: '20-39'
    },
    critical: {
      bg: 'bg-red-50',
      text: 'text-red-900',
      border: 'border-red-200',
      accent: 'bg-red-500',
      icon: XCircle,
      label: 'Avoid',
      description: 'High risk ingredients and poor nutritional profile. Avoid regular consumption.',
      score: '0-19'
    }
  };

  const config = configs[level] || configs.moderate;
  const Icon = config.icon;

  return (
    <div className={`${config.bg} ${config.border} border rounded-2xl p-4 ${className}`}>
      <div className="flex items-start space-x-3">
        <div className={`${config.accent} rounded-full p-2 flex-shrink-0`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center space-x-2 mb-1">
            <h3 className={`font-bold ${config.text}`}>{config.label}</h3>
            <span className={`text-xs font-semibold px-2 py-1 rounded-full ${config.bg} ${config.text} border ${config.border}`}>
              {config.score}
            </span>
          </div>
          {showDescription && (
            <p className={`text-sm ${config.text} opacity-80 leading-relaxed`}>
              {config.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
};

// Compact version for lists
export const ClaimBadgeCompact = ({ level, className = '' }) => {
  const configs = {
    excellent: { color: 'bg-emerald-500', label: 'EXC' },
    good: { color: 'bg-lime-500', label: 'GOOD' },
    moderate: { color: 'bg-amber-500', label: 'MOD' },
    poor: { color: 'bg-orange-500', label: 'POOR' },
    critical: { color: 'bg-red-500', label: 'CRIT' }
  };

  const config = configs[level] || configs.moderate;

  return (
    <div className={`
      inline-flex items-center justify-center w-12 h-6 rounded-full text-white text-xs font-bold
      ${config.color} ${className}
    `}>
      {config.label}
    </div>
  );
};

export default ClaimBadge;
