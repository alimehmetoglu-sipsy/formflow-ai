/**
 * Next Actions Widget Component for FA-46
 * Displays recommended follow-up actions for sales team
 */

import React, { useState } from 'react';
import {
  Phone,
  Mail,
  Calendar,
  FileText,
  MessageSquare,
  Clock,
  ChevronRight,
  CheckCircle,
  Copy,
  AlertCircle,
  Zap,
  Send
} from 'lucide-react';

interface Action {
  action: string;
  priority: 'high' | 'medium' | 'low';
  timing: string;
  method?: 'call' | 'email' | 'meeting' | 'linkedin' | 'demo';
  template?: string;
  reason?: string;
}

interface NextActionsWidgetProps {
  actions: Action[];
  onActionComplete?: (index: number) => void;
  onCopyTemplate?: (template: string) => void;
}

const NextActionsWidget: React.FC<NextActionsWidgetProps> = ({
  actions,
  onActionComplete,
  onCopyTemplate
}) => {
  const [completedActions, setCompletedActions] = useState<number[]>([]);
  const [expandedAction, setExpandedAction] = useState<number | null>(null);

  const handleActionComplete = (index: number) => {
    setCompletedActions([...completedActions, index]);
    onActionComplete?.(index);
  };

  const copyTemplate = (template: string) => {
    navigator.clipboard.writeText(template);
    onCopyTemplate?.(template);
  };

  const getMethodIcon = (method?: string) => {
    switch (method) {
      case 'call':
        return <Phone className="w-4 h-4" />;
      case 'email':
        return <Mail className="w-4 h-4" />;
      case 'meeting':
        return <Calendar className="w-4 h-4" />;
      case 'linkedin':
        return <MessageSquare className="w-4 h-4" />;
      case 'demo':
        return <FileText className="w-4 h-4" />;
      default:
        return <ChevronRight className="w-4 h-4" />;
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'bg-red-100 text-red-700 border-red-200';
      case 'medium':
        return 'bg-amber-100 text-amber-700 border-amber-200';
      case 'low':
        return 'bg-blue-100 text-blue-700 border-blue-200';
      default:
        return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  const getTimingIcon = (timing: string) => {
    const lowerTiming = timing.toLowerCase();
    if (lowerTiming.includes('24') || lowerTiming.includes('today')) {
      return <Zap className="w-4 h-4 text-red-500" />;
    } else if (lowerTiming.includes('week')) {
      return <Clock className="w-4 h-4 text-amber-500" />;
    }
    return <Clock className="w-4 h-4 text-gray-400" />;
  };

  // Sort actions by priority
  const sortedActions = [...actions].sort((a, b) => {
    const priorityOrder = { high: 0, medium: 1, low: 2 };
    return priorityOrder[a.priority] - priorityOrder[b.priority];
  });

  return (
    <div className="next-actions-widget">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 flex items-center">
          <AlertCircle className="w-5 h-5 mr-2 text-blue-500" />
          Recommended Next Actions
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          AI-powered recommendations based on lead analysis
        </p>
      </div>

      <div className="space-y-3">
        {sortedActions.map((action, index) => {
          const isCompleted = completedActions.includes(index);
          const isExpanded = expandedAction === index;

          return (
            <div
              key={index}
              className={`border rounded-lg transition-all ${
                isCompleted ? 'opacity-50 bg-gray-50' : 'bg-white hover:shadow-md'
              }`}
            >
              <div className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    {/* Action Header */}
                    <div className="flex items-center space-x-3 mb-2">
                      <span className={`px-2 py-1 rounded-full text-xs font-medium border ${
                        getPriorityColor(action.priority)
                      }`}>
                        {action.priority.toUpperCase()}
                      </span>
                      <div className="flex items-center text-gray-500 text-sm">
                        {getTimingIcon(action.timing)}
                        <span className="ml-1">{action.timing}</span>
                      </div>
                    </div>

                    {/* Action Description */}
                    <div className="flex items-start">
                      <div className="mr-3 mt-1">
                        {getMethodIcon(action.method)}
                      </div>
                      <div className="flex-1">
                        <p className={`text-gray-900 font-medium ${
                          isCompleted ? 'line-through' : ''
                        }`}>
                          {action.action}
                        </p>
                        
                        {action.reason && (
                          <p className="text-sm text-gray-500 mt-1">
                            {action.reason}
                          </p>
                        )}

                        {/* Template Section */}
                        {action.template && !isCompleted && (
                          <div className="mt-3">
                            <button
                              onClick={() => setExpandedAction(isExpanded ? null : index)}
                              className="text-sm text-blue-600 hover:text-blue-800 font-medium flex items-center"
                            >
                              {isExpanded ? 'Hide' : 'Show'} Template
                              <ChevronRight className={`w-4 h-4 ml-1 transition-transform ${
                                isExpanded ? 'rotate-90' : ''
                              }`} />
                            </button>
                            
                            {isExpanded && (
                              <div className="mt-3 p-3 bg-gray-50 rounded-lg">
                                <div className="flex justify-between items-start mb-2">
                                  <span className="text-xs font-semibold text-gray-600">
                                    SUGGESTED TEMPLATE
                                  </span>
                                  <button
                                    onClick={() => copyTemplate(action.template!)}
                                    className="text-xs text-blue-600 hover:text-blue-800 flex items-center"
                                  >
                                    <Copy className="w-3 h-3 mr-1" />
                                    Copy
                                  </button>
                                </div>
                                <p className="text-sm text-gray-700 whitespace-pre-wrap">
                                  {action.template}
                                </p>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="ml-4 flex items-center space-x-2">
                    {!isCompleted ? (
                      <>
                        <button
                          onClick={() => handleActionComplete(index)}
                          className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                          title="Mark as complete"
                        >
                          <CheckCircle className="w-5 h-5" />
                        </button>
                        {action.method === 'email' && (
                          <button
                            className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                            title="Send email"
                          >
                            <Send className="w-5 h-5" />
                          </button>
                        )}
                        {action.method === 'call' && (
                          <button
                            className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                            title="Call now"
                          >
                            <Phone className="w-5 h-5" />
                          </button>
                        )}
                      </>
                    ) : (
                      <div className="text-green-600">
                        <CheckCircle className="w-5 h-5 fill-current" />
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Summary Stats */}
      <div className="mt-6 p-4 bg-gray-50 rounded-lg">
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {actions.filter(a => a.priority === 'high').length}
            </div>
            <div className="text-xs text-gray-500">High Priority</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {completedActions.length}
            </div>
            <div className="text-xs text-gray-500">Completed</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-gray-900">
              {actions.length - completedActions.length}
            </div>
            <div className="text-xs text-gray-500">Remaining</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default NextActionsWidget;