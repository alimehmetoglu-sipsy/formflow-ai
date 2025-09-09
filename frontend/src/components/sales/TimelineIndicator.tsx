/**
 * Timeline Indicator Component for FA-46
 * Visual representation of decision timeline and urgency
 */

import React from 'react';
import {
  Clock,
  Calendar,
  AlertTriangle,
  Zap,
  TrendingUp,
  CheckCircle
} from 'lucide-react';

interface TimelineIndicatorProps {
  timeline: string;
  urgency: 'urgent' | 'high' | 'medium' | 'low' | 'unknown';
  milestones?: Array<{
    date: string;
    event: string;
    completed?: boolean;
  }>;
}

const TimelineIndicator: React.FC<TimelineIndicatorProps> = ({
  timeline,
  urgency,
  milestones = []
}) => {
  const getUrgencyConfig = () => {
    switch (urgency) {
      case 'urgent':
        return {
          color: 'red',
          bgColor: 'bg-red-100',
          borderColor: 'border-red-500',
          textColor: 'text-red-700',
          icon: <AlertTriangle className="w-5 h-5" />,
          label: 'URGENT - Immediate Action Required',
          description: 'This lead requires immediate attention'
        };
      case 'high':
        return {
          color: 'amber',
          bgColor: 'bg-amber-100',
          borderColor: 'border-amber-500',
          textColor: 'text-amber-700',
          icon: <Zap className="w-5 h-5" />,
          label: 'HIGH PRIORITY - Act Within 48 Hours',
          description: 'Quick follow-up recommended'
        };
      case 'medium':
        return {
          color: 'blue',
          bgColor: 'bg-blue-100',
          borderColor: 'border-blue-500',
          textColor: 'text-blue-700',
          icon: <TrendingUp className="w-5 h-5" />,
          label: 'MEDIUM PRIORITY - This Week',
          description: 'Standard follow-up timeline'
        };
      case 'low':
        return {
          color: 'gray',
          bgColor: 'bg-gray-100',
          borderColor: 'border-gray-400',
          textColor: 'text-gray-700',
          icon: <Clock className="w-5 h-5" />,
          label: 'LOW PRIORITY - Nurture',
          description: 'Long-term nurturing required'
        };
      default:
        return {
          color: 'gray',
          bgColor: 'bg-gray-50',
          borderColor: 'border-gray-300',
          textColor: 'text-gray-600',
          icon: <Calendar className="w-5 h-5" />,
          label: 'TIMELINE UNKNOWN',
          description: 'No specific timeline provided'
        };
    }
  };

  const config = getUrgencyConfig();

  // Parse timeline to extract key dates
  const parseTimeline = (timelineStr: string) => {
    const lower = timelineStr.toLowerCase();
    
    if (lower.includes('immediate') || lower.includes('asap')) {
      return { period: 'Immediate', days: 0 };
    } else if (lower.includes('week')) {
      const match = lower.match(/(\d+)\s*week/);
      const weeks = match ? parseInt(match[1]) : 1;
      return { period: `${weeks} week${weeks > 1 ? 's' : ''}`, days: weeks * 7 };
    } else if (lower.includes('month')) {
      const match = lower.match(/(\d+)\s*month/);
      const months = match ? parseInt(match[1]) : 1;
      return { period: `${months} month${months > 1 ? 's' : ''}`, days: months * 30 };
    } else if (lower.includes('q1')) {
      return { period: 'Q1 2025', days: 90 };
    } else if (lower.includes('q2')) {
      return { period: 'Q2 2025', days: 180 };
    } else if (lower.includes('q3')) {
      return { period: 'Q3 2025', days: 270 };
    } else if (lower.includes('q4')) {
      return { period: 'Q4 2025', days: 365 };
    }
    
    return { period: timelineStr, days: null };
  };

  const timelineInfo = parseTimeline(timeline);

  return (
    <div className="timeline-indicator">
      {/* Urgency Alert */}
      <div className={`${config.bgColor} ${config.borderColor} border-l-4 rounded-lg p-4 mb-4`}>
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <span className={config.textColor}>{config.icon}</span>
            <div className="ml-3">
              <p className={`font-semibold ${config.textColor}`}>
                {config.label}
              </p>
              <p className="text-sm text-gray-600 mt-1">
                {config.description}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Timeline Details */}
      <div className="bg-white border rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="font-medium text-gray-900">Decision Timeline</h4>
          <span className="text-sm text-gray-500">
            {new Date().toLocaleDateString()}
          </span>
        </div>

        <div className="space-y-3">
          {/* Main Timeline */}
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
            <span className="text-sm text-gray-600">Expected Decision:</span>
            <span className="font-semibold text-gray-900">
              {timelineInfo.period}
            </span>
          </div>

          {/* Days Remaining */}
          {timelineInfo.days !== null && (
            <div className="flex items-center justify-between p-3 bg-gray-50 rounded">
              <span className="text-sm text-gray-600">Time Remaining:</span>
              <span className="font-semibold text-gray-900">
                {timelineInfo.days === 0 
                  ? 'Today' 
                  : `${timelineInfo.days} days`}
              </span>
            </div>
          )}

          {/* Visual Timeline */}
          {timelineInfo.days !== null && timelineInfo.days <= 90 && (
            <div className="mt-4">
              <div className="relative">
                <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full transition-all duration-500 ${
                      urgency === 'urgent' ? 'bg-red-500' :
                      urgency === 'high' ? 'bg-amber-500' :
                      urgency === 'medium' ? 'bg-blue-500' :
                      'bg-gray-400'
                    }`}
                    style={{ 
                      width: `${Math.max(10, Math.min(100, ((90 - timelineInfo.days) / 90) * 100))}%` 
                    }}
                  />
                </div>
                <div className="flex justify-between mt-2 text-xs text-gray-500">
                  <span>Today</span>
                  <span>{timelineInfo.period}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Milestones */}
        {milestones.length > 0 && (
          <div className="mt-4 pt-4 border-t">
            <h5 className="text-sm font-medium text-gray-700 mb-3">Key Milestones</h5>
            <div className="space-y-2">
              {milestones.map((milestone, index) => (
                <div key={index} className="flex items-center">
                  {milestone.completed ? (
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                  ) : (
                    <div className="w-4 h-4 border-2 border-gray-300 rounded-full mr-2" />
                  )}
                  <span className={`text-sm ${milestone.completed ? 'text-gray-500 line-through' : 'text-gray-700'}`}>
                    {milestone.event}
                  </span>
                  <span className="ml-auto text-xs text-gray-400">
                    {milestone.date}
                  </span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommended Actions Based on Timeline */}
        <div className="mt-4 p-3 bg-blue-50 rounded">
          <p className="text-sm text-blue-700">
            <strong>💡 Timeline Strategy:</strong>{' '}
            {urgency === 'urgent' 
              ? 'Schedule an immediate call or demo. Time is critical.'
              : urgency === 'high'
              ? 'Reach out within 24-48 hours while interest is high.'
              : urgency === 'medium'
              ? 'Plan a structured follow-up sequence over the next week.'
              : 'Add to nurture campaign and check in periodically.'}
          </p>
        </div>
      </div>
    </div>
  );
};

export default TimelineIndicator;