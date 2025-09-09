/**
 * Contact Card Component for FA-46
 * Displays lead contact and company information
 */

import React from 'react';
import {
  Phone,
  Mail,
  Building,
  Globe,
  Linkedin,
  User,
  Users,
  DollarSign,
  MapPin,
  Copy,
  ExternalLink
} from 'lucide-react';

interface ContactCardProps {
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
    location?: string;
  };
}

const ContactCard: React.FC<ContactCardProps> = ({ contact, company }) => {
  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // You could add a toast notification here
  };

  const openLink = (url: string) => {
    if (!url.startsWith('http')) {
      url = `https://${url}`;
    }
    window.open(url, '_blank');
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Contact Information */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <User className="w-5 h-5 mr-2" />
            Contact Information
          </h3>
          
          <div className="space-y-3">
            {/* Name */}
            <div className="flex items-center justify-between">
              <div className="flex items-center">
                <span className="text-2xl font-bold text-gray-900">
                  {contact.name}
                </span>
              </div>
            </div>

            {/* Role */}
            {contact.role && (
              <div className="flex items-center text-gray-600">
                <User className="w-4 h-4 mr-2 text-gray-400" />
                <span>{contact.role}</span>
              </div>
            )}

            {/* Email */}
            <div className="flex items-center justify-between group">
              <div className="flex items-center text-gray-600">
                <Mail className="w-4 h-4 mr-2 text-gray-400" />
                <a
                  href={`mailto:${contact.email}`}
                  className="hover:text-blue-600 transition-colors"
                >
                  {contact.email}
                </a>
              </div>
              <button
                onClick={() => copyToClipboard(contact.email)}
                className="opacity-0 group-hover:opacity-100 transition-opacity"
                title="Copy email"
              >
                <Copy className="w-4 h-4 text-gray-400 hover:text-gray-600" />
              </button>
            </div>

            {/* Phone */}
            {contact.phone && (
              <div className="flex items-center justify-between group">
                <div className="flex items-center text-gray-600">
                  <Phone className="w-4 h-4 mr-2 text-gray-400" />
                  <a
                    href={`tel:${contact.phone}`}
                    className="hover:text-blue-600 transition-colors"
                  >
                    {contact.phone}
                  </a>
                </div>
                <button
                  onClick={() => copyToClipboard(contact.phone)}
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                  title="Copy phone"
                >
                  <Copy className="w-4 h-4 text-gray-400 hover:text-gray-600" />
                </button>
              </div>
            )}

            {/* LinkedIn */}
            {contact.linkedin && (
              <div className="flex items-center text-gray-600">
                <Linkedin className="w-4 h-4 mr-2 text-gray-400" />
                <button
                  onClick={() => openLink(contact.linkedin)}
                  className="hover:text-blue-600 transition-colors flex items-center"
                >
                  View Profile
                  <ExternalLink className="w-3 h-3 ml-1" />
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Company Information */}
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
            <Building className="w-5 h-5 mr-2" />
            Company Details
          </h3>
          
          <div className="space-y-3">
            {/* Company Name */}
            <div className="flex items-center">
              <span className="text-xl font-bold text-gray-900">
                {company.name}
              </span>
            </div>

            {/* Industry */}
            {company.industry && (
              <div className="flex items-center text-gray-600">
                <Building className="w-4 h-4 mr-2 text-gray-400" />
                <span>{company.industry}</span>
              </div>
            )}

            {/* Company Size */}
            {company.size && (
              <div className="flex items-center text-gray-600">
                <Users className="w-4 h-4 mr-2 text-gray-400" />
                <span>{company.size} employees</span>
              </div>
            )}

            {/* Revenue */}
            {company.revenue && (
              <div className="flex items-center text-gray-600">
                <DollarSign className="w-4 h-4 mr-2 text-gray-400" />
                <span>{company.revenue} annual revenue</span>
              </div>
            )}

            {/* Website */}
            {company.website && (
              <div className="flex items-center text-gray-600">
                <Globe className="w-4 h-4 mr-2 text-gray-400" />
                <button
                  onClick={() => openLink(company.website)}
                  className="hover:text-blue-600 transition-colors flex items-center"
                >
                  {company.website}
                  <ExternalLink className="w-3 h-3 ml-1" />
                </button>
              </div>
            )}

            {/* Location */}
            {company.location && (
              <div className="flex items-center text-gray-600">
                <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                <span>{company.location}</span>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-6 border-t flex flex-wrap gap-3">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 flex items-center">
          <Phone className="w-4 h-4 mr-2" />
          Call Now
        </button>
        <button className="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 flex items-center">
          <Mail className="w-4 h-4 mr-2" />
          Send Email
        </button>
        {contact.linkedin && (
          <button
            onClick={() => openLink(contact.linkedin!)}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg text-sm font-medium hover:bg-blue-600 flex items-center"
          >
            <Linkedin className="w-4 h-4 mr-2" />
            Connect
          </button>
        )}
        <button className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-300 flex items-center">
          <User className="w-4 h-4 mr-2" />
          Add to CRM
        </button>
      </div>
    </div>
  );
};

export default ContactCard;