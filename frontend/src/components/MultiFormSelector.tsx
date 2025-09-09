/**
 * MultiFormSelector Component for FA-44 Epic
 * Allows users to select and configure multiple forms for aggregated dashboards
 */

import React, { useState, useEffect } from 'react';
import { 
  Search, 
  Plus, 
  Trash2, 
  Settings, 
  AlertCircle,
  ChevronDown,
  ChevronUp,
  Database,
  Link2,
  Weight
} from 'lucide-react';

interface FormSource {
  id: string;
  form_type: 'typeform' | 'google_forms' | 'custom';
  form_external_id: string;
  form_title: string;
  field_mappings: Record<string, string>;
  weight: number;
  priority: number;
  total_responses?: number;
  last_response_at?: string;
}

interface MultiFormSelectorProps {
  onFormsSelected: (forms: FormSource[]) => void;
  initialForms?: FormSource[];
  maxForms?: number;
  userPlan?: 'free' | 'pro' | 'business';
}

const MultiFormSelector: React.FC<MultiFormSelectorProps> = ({
  onFormsSelected,
  initialForms = [],
  maxForms = 10,
  userPlan = 'free'
}) => {
  const [selectedForms, setSelectedForms] = useState<FormSource[]>(initialForms);
  const [availableForms, setAvailableForms] = useState<FormSource[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [showFieldMapping, setShowFieldMapping] = useState<string | null>(null);
  const [aggregationMethod, setAggregationMethod] = useState<'union' | 'intersection' | 'weighted'>('union');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Determine max forms based on user plan
  const getMaxFormsAllowed = () => {
    switch (userPlan) {
      case 'free':
        return 3;
      case 'pro':
        return 5;
      case 'business':
        return maxForms;
      default:
        return 3;
    }
  };

  useEffect(() => {
    fetchAvailableForms();
  }, []);

  useEffect(() => {
    onFormsSelected(selectedForms);
  }, [selectedForms]);

  const fetchAvailableForms = async () => {
    setLoading(true);
    try {
      // Fetch user's available forms from API
      const response = await fetch('/api/v1/forms/available', {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      if (!response.ok) throw new Error('Failed to fetch forms');
      
      const data = await response.json();
      setAvailableForms(data.forms);
    } catch (err) {
      setError('Failed to load available forms');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const addForm = (form: FormSource) => {
    if (selectedForms.length >= getMaxFormsAllowed()) {
      setError(`You can only select up to ${getMaxFormsAllowed()} forms with your ${userPlan} plan`);
      return;
    }

    if (selectedForms.find(f => f.id === form.id)) {
      setError('This form is already selected');
      return;
    }

    setSelectedForms([...selectedForms, { ...form, weight: 1.0, priority: selectedForms.length }]);
    setError(null);
  };

  const removeForm = (formId: string) => {
    setSelectedForms(selectedForms.filter(f => f.id !== formId));
  };

  const updateFormWeight = (formId: string, weight: number) => {
    setSelectedForms(selectedForms.map(f => 
      f.id === formId ? { ...f, weight } : f
    ));
  };

  const updateFormPriority = (formId: string, priority: number) => {
    setSelectedForms(selectedForms.map(f => 
      f.id === formId ? { ...f, priority } : f
    ));
  };

  const updateFieldMapping = (formId: string, mappings: Record<string, string>) => {
    setSelectedForms(selectedForms.map(f => 
      f.id === formId ? { ...f, field_mappings: mappings } : f
    ));
  };

  const filteredForms = availableForms.filter(form =>
    form.form_title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="multi-form-selector">
      {/* Header */}
      <div className="mb-6">
        <h3 className="text-lg font-semibold mb-2">Select Forms to Aggregate</h3>
        <p className="text-sm text-gray-600">
          Combine data from multiple forms into a single dashboard. 
          {userPlan === 'free' && (
            <span className="text-amber-600 ml-1">
              (Free plan: up to 3 forms)
            </span>
          )}
        </p>
      </div>

      {/* Aggregation Method Selection */}
      <div className="mb-6 p-4 bg-gray-50 rounded-lg">
        <label className="block text-sm font-medium mb-2">Aggregation Method</label>
        <div className="grid grid-cols-3 gap-2">
          <button
            onClick={() => setAggregationMethod('union')}
            className={`p-2 rounded border ${
              aggregationMethod === 'union' 
                ? 'bg-blue-500 text-white border-blue-500' 
                : 'bg-white border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Database className="w-4 h-4 inline mr-1" />
            Union
          </button>
          <button
            onClick={() => setAggregationMethod('intersection')}
            className={`p-2 rounded border ${
              aggregationMethod === 'intersection' 
                ? 'bg-blue-500 text-white border-blue-500' 
                : 'bg-white border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Link2 className="w-4 h-4 inline mr-1" />
            Intersection
          </button>
          <button
            onClick={() => setAggregationMethod('weighted')}
            className={`p-2 rounded border ${
              aggregationMethod === 'weighted' 
                ? 'bg-blue-500 text-white border-blue-500' 
                : 'bg-white border-gray-300 hover:bg-gray-50'
            }`}
          >
            <Weight className="w-4 h-4 inline mr-1" />
            Weighted
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          {aggregationMethod === 'union' && 'Combine all records from all forms'}
          {aggregationMethod === 'intersection' && 'Only include common fields across forms'}
          {aggregationMethod === 'weighted' && 'Apply weights to numeric values from each form'}
        </p>
      </div>

      {/* Selected Forms */}
      <div className="mb-6">
        <h4 className="text-sm font-medium mb-3">
          Selected Forms ({selectedForms.length}/{getMaxFormsAllowed()})
        </h4>
        
        {selectedForms.length === 0 ? (
          <div className="p-4 border-2 border-dashed border-gray-300 rounded-lg text-center text-gray-500">
            No forms selected yet. Search and add forms below.
          </div>
        ) : (
          <div className="space-y-2">
            {selectedForms.map((form) => (
              <div key={form.id} className="border rounded-lg p-3 bg-white">
                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center">
                      <span className="font-medium">{form.form_title}</span>
                      <span className="ml-2 px-2 py-1 text-xs bg-gray-100 rounded">
                        {form.form_type}
                      </span>
                      {form.total_responses && (
                        <span className="ml-2 text-xs text-gray-500">
                          {form.total_responses} responses
                        </span>
                      )}
                    </div>
                    
                    {/* Weight and Priority Controls for Weighted Method */}
                    {aggregationMethod === 'weighted' && (
                      <div className="mt-2 flex items-center space-x-4">
                        <div className="flex items-center">
                          <label className="text-xs text-gray-600 mr-1">Weight:</label>
                          <input
                            type="number"
                            min="0"
                            max="10"
                            step="0.1"
                            value={form.weight}
                            onChange={(e) => updateFormWeight(form.id, parseFloat(e.target.value))}
                            className="w-16 px-2 py-1 text-xs border rounded"
                          />
                        </div>
                        <div className="flex items-center">
                          <label className="text-xs text-gray-600 mr-1">Priority:</label>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={form.priority}
                            onChange={(e) => updateFormPriority(form.id, parseInt(e.target.value))}
                            className="w-16 px-2 py-1 text-xs border rounded"
                          />
                        </div>
                      </div>
                    )}
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => setShowFieldMapping(
                        showFieldMapping === form.id ? null : form.id
                      )}
                      className="p-1 text-gray-500 hover:text-gray-700"
                      title="Configure field mappings"
                    >
                      <Settings className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => removeForm(form.id)}
                      className="p-1 text-red-500 hover:text-red-700"
                      title="Remove form"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
                
                {/* Field Mapping Panel */}
                {showFieldMapping === form.id && (
                  <div className="mt-3 p-3 bg-gray-50 rounded">
                    <FieldMappingPanel
                      form={form}
                      onUpdate={(mappings) => updateFieldMapping(form.id, mappings)}
                    />
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Available Forms Search */}
      <div className="mb-4">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <input
            type="text"
            placeholder="Search available forms..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:border-blue-500"
          />
        </div>
      </div>

      {/* Available Forms List */}
      {loading ? (
        <div className="text-center py-4">Loading available forms...</div>
      ) : error ? (
        <div className="p-4 bg-red-50 text-red-600 rounded-lg flex items-center">
          <AlertCircle className="w-4 h-4 mr-2" />
          {error}
        </div>
      ) : (
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {filteredForms.map((form) => (
            <div
              key={form.id}
              className="p-3 border rounded-lg hover:bg-gray-50 cursor-pointer flex items-center justify-between"
              onClick={() => addForm(form)}
            >
              <div>
                <span className="font-medium">{form.form_title}</span>
                <span className="ml-2 text-xs text-gray-500">
                  {form.form_type} • {form.total_responses || 0} responses
                </span>
              </div>
              <Plus className="w-4 h-4 text-gray-400" />
            </div>
          ))}
        </div>
      )}

      {/* Upgrade Prompt for Free Users */}
      {userPlan === 'free' && selectedForms.length >= 3 && (
        <div className="mt-4 p-4 bg-amber-50 border border-amber-200 rounded-lg">
          <p className="text-sm text-amber-800">
            <AlertCircle className="w-4 h-4 inline mr-1" />
            You've reached the limit for free accounts. 
            <a href="/pricing" className="ml-1 font-medium underline">
              Upgrade to Pro
            </a> to add more forms.
          </p>
        </div>
      )}
    </div>
  );
};

// Field Mapping Panel Component
const FieldMappingPanel: React.FC<{
  form: FormSource;
  onUpdate: (mappings: Record<string, string>) => void;
}> = ({ form, onUpdate }) => {
  const [mappings, setMappings] = useState<Record<string, string>>(
    form.field_mappings || {}
  );

  const commonFields = [
    'name', 'email', 'phone', 'company', 'score', 'rating', 
    'feedback', 'date', 'amount', 'category'
  ];

  const handleMappingChange = (targetField: string, sourceField: string) => {
    const newMappings = { ...mappings, [targetField]: sourceField };
    setMappings(newMappings);
    onUpdate(newMappings);
  };

  return (
    <div>
      <p className="text-xs text-gray-600 mb-2">
        Map form fields to common fields for better aggregation
      </p>
      <div className="space-y-2">
        {commonFields.map((field) => (
          <div key={field} className="flex items-center">
            <label className="text-xs w-24">{field}:</label>
            <input
              type="text"
              placeholder={`Source field name`}
              value={mappings[field] || ''}
              onChange={(e) => handleMappingChange(field, e.target.value)}
              className="flex-1 px-2 py-1 text-xs border rounded"
            />
          </div>
        ))}
      </div>
    </div>
  );
};

export default MultiFormSelector;