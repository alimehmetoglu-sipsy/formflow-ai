/**
 * Sales Lead Dashboard Template for FA-46
 * Optimized dashboard layout for sales teams with lead insights
 */

import React, { useState, useEffect } from 'react';
import {
  Phone,
  Mail,
  Building,
  Calendar,
  DollarSign,
  User,
  AlertCircle,
  Download,
  Share2,
  ChevronRight,
  Target,
  TrendingUp,
  Clock,
  Zap
} from 'lucide-react';
import LeadScoreWidget from '../components/LeadScoreWidget';
import ContactCard from '../components/sales/ContactCard';
import NextActionsWidget from '../components/sales/NextActionsWidget';
import CompetitorInsights from '../components/sales/CompetitorInsights';
import TimelineIndicator from '../components/sales/TimelineIndicator';

interface SalesLeadTemplateProps {
  dashboardData: {
    leadScore: {
      score: number;
      category: 'hot' | 'warm' | 'cold';
      factors: any;
      aiAdjustment: number;
      buyingSignals: string[];
    };
    contact: {
      name: string;
      email: string;
      phone?: string;
      role?: string;
      linkedin?: string;
    };
    company: {
      name: string;
      size?: string;
      industry?: string;
      website?: string;
      revenue?: string;
    };
    insights: {
      budget?: string;
      timeline?: string;
      painPoints?: string[];
      currentSolution?: string;
      decisionProcess?: string;
    };
    nextActions: Array<{
      action: string;
      priority: 'high' | 'medium' | 'low';
      timing: string;
      template?: string;
    }>;
    competitors?: Array<{
      name: string;
      mentioned: boolean;
      advantages: string[];
    }>;
  };
  onExport?: (format: 'csv' | 'pdf') => void;
  onShare?: () => void;
}

const SalesLeadTemplate: React.FC<SalesLeadTemplateProps> = ({
  dashboardData,
  onExport,
  onShare
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'insights' | 'actions'>('overview');
  const [showShareModal, setShowShareModal] = useState(false);

  // Determine urgency level
  const getUrgencyLevel = () => {
    const { timeline } = dashboardData.insights;
    if (!timeline) return 'unknown';
    
    const lowerTimeline = timeline.toLowerCase();
    if (lowerTimeline.includes('immediate') || lowerTimeline.includes('asap')) {
      return 'urgent';
    } else if (lowerTimeline.includes('month') || lowerTimeline.includes('q1')) {
      return 'high';
    } else if (lowerTimeline.includes('quarter') || lowerTimeline.includes('q2')) {
      return 'medium';
    }
    return 'low';
  };

  const urgencyLevel = getUrgencyLevel();

  return (
    <div className="sales-lead-template min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Lead Intelligence Dashboard
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Generated {new Date().toLocaleDateString()}
              </p>
            </div>
            
            {/* Action Buttons */}
            <div className="flex space-x-3">
              <button
                onClick={() => onExport?.('csv')}
                className="px-4 py-2 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center"
              >
                <Download className="w-4 h-4 mr-2" />
                Export to CRM
              </button>
              <button
                onClick={() => setShowShareModal(true)}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Top Section - Score and Contact */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
          {/* Lead Score */}
          <div className="lg:col-span-1">
            <LeadScoreWidget
              score={dashboardData.leadScore.score}
              category={dashboardData.leadScore.category}
              scoreFactors={dashboardData.leadScore.factors}
              aiAdjustment={dashboardData.leadScore.aiAdjustment}
              buyingSignals={dashboardData.leadScore.buyingSignals}
              showDetails={true}
            />
          </div>

          {/* Contact Information */}
          <div className="lg:col-span-2">
            <ContactCard
              contact={dashboardData.contact}
              company={dashboardData.company}
            />
          </div>
        </div>

        {/* Timeline and Budget Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Timeline */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <Clock className="w-5 h-5 mr-2" />
              Decision Timeline
            </h3>
            <TimelineIndicator
              timeline={dashboardData.insights.timeline || 'Not specified'}
              urgency={urgencyLevel}
            />
          </div>

          {/* Budget */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
              <DollarSign className="w-5 h-5 mr-2" />
              Budget Information
            </h3>
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Budget Range:</span>
                <span className="font-semibold text-gray-900">
                  {dashboardData.insights.budget || 'Not disclosed'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600">Approval Status:</span>
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                  dashboardData.insights.budget?.includes('approved') 
                    ? 'bg-green-100 text-green-700'
                    : 'bg-gray-100 text-gray-700'
                }`}>
                  {dashboardData.insights.budget?.includes('approved') ? 'Approved' : 'Pending'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Tabbed Content */}
        <div className="bg-white rounded-lg shadow">
          {/* Tab Navigation */}
          <div className="border-b">
            <div className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('overview')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'overview'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Overview
              </button>
              <button
                onClick={() => setActiveTab('insights')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'insights'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Key Insights
              </button>
              <button
                onClick={() => setActiveTab('actions')}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === 'actions'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                Next Actions
              </button>
            </div>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'overview' && (
              <div className="space-y-6">
                {/* Pain Points */}
                {dashboardData.insights.painPoints && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                      <Target className="w-4 h-4 mr-2" />
                      Identified Pain Points
                    </h4>
                    <ul className="space-y-2">
                      {dashboardData.insights.painPoints.map((pain, index) => (
                        <li key={index} className="flex items-start">
                          <span className="text-red-500 mr-2">•</span>
                          <span className="text-gray-700">{pain}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Current Solution */}
                {dashboardData.insights.currentSolution && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">
                      Current Solution
                    </h4>
                    <p className="text-gray-600 bg-gray-50 p-3 rounded">
                      {dashboardData.insights.currentSolution}
                    </p>
                  </div>
                )}

                {/* Decision Process */}
                {dashboardData.insights.decisionProcess && (
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-3">
                      Decision Process
                    </h4>
                    <p className="text-gray-600">
                      {dashboardData.insights.decisionProcess}
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'insights' && (
              <div className="space-y-6">
                {/* Competitor Analysis */}
                {dashboardData.competitors && dashboardData.competitors.length > 0 && (
                  <CompetitorInsights competitors={dashboardData.competitors} />
                )}

                {/* Buying Signals */}
                <div>
                  <h4 className="text-sm font-semibold text-gray-700 mb-3 flex items-center">
                    <Zap className="w-4 h-4 mr-2" />
                    Buying Signals Detected
                  </h4>
                  <div className="grid grid-cols-2 gap-4">
                    {dashboardData.leadScore.buyingSignals.map((signal, index) => (
                      <div key={index} className="flex items-center space-x-2">
                        <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                        <span className="text-gray-700 capitalize">
                          {signal.replace(/_/g, ' ')}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'actions' && (
              <NextActionsWidget actions={dashboardData.nextActions} />
            )}
          </div>
        </div>

        {/* Quick Stats Bar */}
        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {dashboardData.leadScore.score}
            </div>
            <div className="text-sm text-gray-500">Lead Score</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {urgencyLevel === 'urgent' ? '🔥' : urgencyLevel === 'high' ? '⚡' : '📅'}
            </div>
            <div className="text-sm text-gray-500">Urgency</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {dashboardData.nextActions.filter(a => a.priority === 'high').length}
            </div>
            <div className="text-sm text-gray-500">Priority Actions</div>
          </div>
          <div className="bg-white rounded-lg shadow p-4 text-center">
            <div className="text-2xl font-bold text-gray-900">
              {dashboardData.competitors?.length || 0}
            </div>
            <div className="text-sm text-gray-500">Competitors</div>
          </div>
        </div>
      </div>

      {/* Share Modal */}
      {showShareModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-lg font-semibold mb-4">Share Dashboard</h3>
            <p className="text-gray-600 mb-4">
              Share this dashboard with your team members
            </p>
            <input
              type="text"
              value={`${window.location.origin}/dashboard/${Math.random().toString(36).substr(2, 9)}`}
              readOnly
              className="w-full p-2 border rounded mb-4"
            />
            <div className="flex justify-end space-x-3">
              <button
                onClick={() => setShowShareModal(false)}
                className="px-4 py-2 text-gray-600 hover:text-gray-800"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  navigator.clipboard.writeText(window.location.href);
                  setShowShareModal(false);
                }}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Copy Link
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default SalesLeadTemplate;