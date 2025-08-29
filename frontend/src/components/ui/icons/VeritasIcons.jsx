import React from 'react';

// Custom Veritas icon components optimized for the brand
export const VeritasLogo = ({ className = "w-8 h-8", color = "currentColor" }) => (
  <svg className={className} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
    <rect width="32" height="32" rx="8" fill="url(#gradient1)" />
    <path
      d="M8 12L16 20L24 12"
      stroke="white"
      strokeWidth="2.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M12 8L16 12L20 8"
      stroke="white"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <defs>
      <linearGradient id="gradient1" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#3B82F6" />
        <stop offset="100%" stopColor="#1E40AF" />
      </linearGradient>
    </defs>
  </svg>
);

export const HealthScoreIcon = ({ className = "w-6 h-6", score = 50 }) => {
  const getColor = (score) => {
    if (score >= 80) return "#059669"; // emerald-600
    if (score >= 60) return "#65a30d"; // lime-600
    if (score >= 40) return "#d97706"; // amber-600
    if (score >= 20) return "#ea580c"; // orange-600
    return "#dc2626"; // red-600
  };

  return (
    <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="10" stroke="#e5e7eb" strokeWidth="2" />
      <circle
        cx="12"
        cy="12"
        r="10"
        stroke={getColor(score)}
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray={`${score * 0.628} 62.8`}
        transform="rotate(-90 12 12)"
        fill="none"
      />
      <text
        x="12"
        y="16"
        textAnchor="middle"
        fontSize="8"
        fontWeight="bold"
        fill={getColor(score)}
      >
        {score}
      </text>
    </svg>
  );
};

export const NutritionIcon = ({ className = "w-6 h-6", type = "protein" }) => {
  const icons = {
    protein: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M12 2L13.5 8.5L20 7L14.5 13L21 14L12 22L3 14L9.5 13L4 7L10.5 8.5L12 2Z"
          fill="#10b981"
          stroke="#10b981"
          strokeWidth="1"
          strokeLinejoin="round"
        />
      </svg>
    ),
    carbs: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="4" y="4" width="16" height="16" rx="2" fill="#3b82f6" />
        <rect x="7" y="7" width="10" height="10" rx="1" fill="white" fillOpacity="0.3" />
      </svg>
    ),
    fat: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="12" cy="12" rx="8" ry="6" fill="#f59e0b" />
        <ellipse cx="12" cy="12" rx="5" ry="3" fill="white" fillOpacity="0.3" />
      </svg>
    ),
    fiber: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M3 12C3 12 5.5 6 12 6S21 12 21 12C21 12 18.5 18 12 18S3 12 3 12Z"
          fill="#84cc16"
          stroke="#84cc16"
          strokeWidth="1"
        />
        <circle cx="12" cy="12" r="3" fill="white" fillOpacity="0.4" />
      </svg>
    ),
    sodium: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M12 2L22 8V16L12 22L2 16V8L12 2Z"
          fill="#ef4444"
          stroke="#ef4444"
          strokeWidth="1"
          strokeLinejoin="round"
        />
        <path d="M12 6L18 9V15L12 18L6 15V9L12 6Z" fill="white" fillOpacity="0.3" />
      </svg>
    )
  };

  return icons[type] || icons.protein;
};

export const ProcessStepIcon = ({ className = "w-8 h-8", step = 1 }) => {
  const stepIcons = {
    1: (
      <svg className={className} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="14" fill="url(#stepGradient1)" />
        <path
          d="M12 16L16 20L20 12"
          stroke="white"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <defs>
          <linearGradient id="stepGradient1" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#3B82F6" />
            <stop offset="100%" stopColor="#1E40AF" />
          </linearGradient>
        </defs>
      </svg>
    ),
    2: (
      <svg className={className} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="14" fill="url(#stepGradient2)" />
        <rect x="11" y="11" width="10" height="10" rx="2" fill="white" />
        <rect x="13" y="13" width="6" height="6" rx="1" fill="url(#stepGradient2)" />
        <defs>
          <linearGradient id="stepGradient2" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#0891B2" />
            <stop offset="100%" stopColor="#0E7490" />
          </linearGradient>
        </defs>
      </svg>
    ),
    3: (
      <svg className={className} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="14" fill="url(#stepGradient3)" />
        <path
          d="M12 10H20M16 10V22M16 14L20 18M16 18L12 14"
          stroke="white"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <defs>
          <linearGradient id="stepGradient3" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#8B5CF6" />
            <stop offset="100%" stopColor="#7C3AED" />
          </linearGradient>
        </defs>
      </svg>
    ),
    4: (
      <svg className={className} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="16" cy="16" r="14" fill="url(#stepGradient4)" />
        <path
          d="M10 12L16 18L22 12"
          stroke="white"
          strokeWidth="2.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <circle cx="16" cy="22" r="1.5" fill="white" />
        <defs>
          <linearGradient id="stepGradient4" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="#10B981" />
            <stop offset="100%" stopColor="#059669" />
          </linearGradient>
        </defs>
      </svg>
    )
  };

  return stepIcons[step] || stepIcons[1];
};

export const HealthImpactIcon = ({ className = "w-6 h-6", system = "cardiovascular" }) => {
  const systemIcons = {
    cardiovascular: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M12 21.35L10.55 20.03C5.4 15.36 2 12.28 2 8.5C2 5.42 4.42 3 7.5 3C9.24 3 10.91 3.81 12 5.09C13.09 3.81 14.76 3 16.5 3C19.58 3 22 5.42 22 8.5C22 12.28 18.6 15.36 13.45 20.04L12 21.35Z"
          fill="#ef4444"
        />
      </svg>
    ),
    metabolic: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M13 2L3 14H12L11 22L21 10H12L13 2Z"
          fill="#f59e0b"
          stroke="#f59e0b"
          strokeWidth="1"
          strokeLinejoin="round"
        />
      </svg>
    ),
    digestive: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <ellipse cx="12" cy="12" rx="10" ry="8" fill="#10b981" />
        <ellipse cx="12" cy="12" rx="6" ry="4" fill="white" fillOpacity="0.3" />
        <circle cx="9" cy="10" r="1" fill="#065f46" />
        <circle cx="15" cy="10" r="1" fill="#065f46" />
        <path d="M9 14C9 14 10.5 16 12 16S15 14 15 14" stroke="#065f46" strokeWidth="1.5" strokeLinecap="round" />
      </svg>
    ),
    inflammatory: (
      <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path
          d="M12 2L15.5 8.5L22 9L17 14L18.5 21L12 17.5L5.5 21L7 14L2 9L8.5 8.5L12 2Z"
          fill="#dc2626"
          stroke="#dc2626"
          strokeWidth="0.5"
          strokeLinejoin="round"
        />
      </svg>
    )
  };

  return systemIcons[system] || systemIcons.cardiovascular;
};

export const TrendIcon = ({ className = "w-5 h-5", direction = "up", color = "#10b981" }) => (
  <svg className={className} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d={direction === "up" ? "M5 12L10 7L15 12" : direction === "down" ? "M5 8L10 13L15 8" : "M3 10L17 10"}
      stroke={color}
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    {direction === "up" && <path d="M12 7H15V10" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />}
    {direction === "down" && <path d="M12 13H15V10" stroke={color} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />}
  </svg>
);

export const SecurityBadge = ({ className = "w-6 h-6" }) => (
  <svg className={className} viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
    <path
      d="M12 2L3 7V11C3 16.55 6.84 21.74 12 23C17.16 21.74 21 16.55 21 11V7L12 2Z"
      fill="url(#securityGradient)"
      stroke="url(#securityGradient)"
      strokeWidth="1"
      strokeLinejoin="round"
    />
    <path
      d="M9 12L11 14L15 10"
      stroke="white"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <defs>
      <linearGradient id="securityGradient" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#10B981" />
        <stop offset="100%" stopColor="#059669" />
      </linearGradient>
    </defs>
  </svg>
);

export const ProcessingIcon = ({ className = "w-5 h-5", type = "ocr" }) => {
  const processingIcons = {
    ocr: (
      <svg className={className} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <rect x="2" y="2" width="16" height="16" rx="2" stroke="#6b7280" strokeWidth="1.5" fill="none" />
        <path d="M6 6H14M6 10H12M6 14H10" stroke="#6b7280" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="15" cy="5" r="2" fill="#3b82f6" />
      </svg>
    ),
    ai: (
      <svg className={className} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="10" cy="10" r="8" stroke="#8b5cf6" strokeWidth="1.5" fill="none" />
        <path d="M7 7L13 13M13 7L7 13" stroke="#8b5cf6" strokeWidth="1.5" strokeLinecap="round" />
        <circle cx="10" cy="10" r="2" fill="#8b5cf6" />
      </svg>
    ),
    analysis: (
      <svg className={className} viewBox="0 0 20 20" fill="none" xmlns="http://www.w3.org/2000/svg">
        <path d="M3 17L7 13L11 15L17 9" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
        <path d="M14 9H17V12" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    )
  };

  return processingIcons[type] || processingIcons.ocr;
};

export default {
  VeritasLogo,
  HealthScoreIcon,
  NutritionIcon,
  ProcessStepIcon,
  HealthImpactIcon,
  TrendIcon,
  SecurityBadge,
  ProcessingIcon
};
