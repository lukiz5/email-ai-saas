import React from 'react';
import { Mail, Clock } from 'lucide-react';

const EmailList = ({ emails, onSelectEmail, selectedEmails = [] }) => {
  const isSelected = (emailId) => selectedEmails.includes(emailId);

  const toggleSelect = (emailId) => {
    if (isSelected(emailId)) {
      onSelectEmail(selectedEmails.filter((id) => id !== emailId));
    } else {
      onSelectEmail([...selectedEmails, emailId]);
    }
  };

  if (!emails || emails.length === 0) {
    return (
      <div className="text-center py-12 text-gray-500">
        <Mail size={48} className="mx-auto mb-4 opacity-50" />
        <p>No emails found</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      {emails.map((email) => (
        <div
          key={email.id}
          onClick={() => toggleSelect(email.id)}
          className={`
            p-4 border rounded-lg cursor-pointer transition-all duration-150
            ${
              isSelected(email.id)
                ? 'border-primary-500 bg-primary-50'
                : 'border-gray-200 hover:border-gray-300 bg-white'
            }
          `}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={isSelected(email.id)}
                  onChange={() => {}}
                  className="rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                />
                <h3 className="font-medium text-gray-900 truncate">{email.subject || 'No Subject'}</h3>
              </div>
              <p className="text-sm text-gray-600 mt-1">{email.from || 'Unknown sender'}</p>
              {email.preview && (
                <p className="text-sm text-gray-500 mt-2 line-clamp-2">{email.preview}</p>
              )}
            </div>
            <div className="ml-4 flex items-center space-x-2 text-sm text-gray-500">
              <Clock size={14} />
              <span>{formatDate(email.date)}</span>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};

const formatDate = (dateString) => {
  if (!dateString) return '';

  try {
    const date = new Date(dateString);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;

    return date.toLocaleDateString();
  } catch {
    return dateString;
  }
};

export default EmailList;
