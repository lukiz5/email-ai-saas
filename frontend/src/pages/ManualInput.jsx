import React, { useState } from 'react';
import Card from '../components/Card';
import Loader from '../components/Loader';
import { Sparkles, CheckCircle, AlertCircle } from 'lucide-react';
import { summarizeRaw } from '../lib/api';

const ManualInput = () => {
  const [emailText, setEmailText] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleSummarize = async () => {
    if (!emailText.trim()) {
      alert('Please enter email text');
      return;
    }

    setLoading(true);
    try {
      const data = await summarizeRaw(emailText);
      setResult(data);

      // Store in localStorage for FREE users
      const history = JSON.parse(localStorage.getItem('emailHistory') || '[]');
      history.unshift({
        id: Date.now(),
        timestamp: new Date().toISOString(),
        ...data,
      });
      localStorage.setItem('emailHistory', JSON.stringify(history.slice(0, 50)));
    } catch (error) {
      alert('Error generating summary. Please try again.');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  const getPriorityColor = (priority) => {
    if (priority >= 4) return 'text-red-600';
    if (priority === 3) return 'text-yellow-600';
    return 'text-green-600';
  };

  const getPriorityLabel = (priority) => {
    if (priority >= 4) return 'High';
    if (priority === 3) return 'Normal';
    return 'Low';
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Manual Email Input</h1>
        <p className="text-gray-600 mt-2">
          Paste your email text below to get an AI-powered summary (FREE - No login required)
        </p>
      </div>

      <Card>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Text
            </label>
            <textarea
              value={emailText}
              onChange={(e) => setEmailText(e.target.value)}
              placeholder="Paste your email text here...&#10;&#10;Include headers like From, Subject, Date if available, or just paste the email body."
              rows={12}
              className="textarea-field"
            />
            <p className="text-sm text-gray-500 mt-2">
              {emailText.length} characters
            </p>
          </div>

          <button
            onClick={handleSummarize}
            disabled={loading || !emailText.trim()}
            className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
          >
            {loading ? (
              <>
                <Loader size="sm" />
                <span className="ml-2">Generating Summary...</span>
              </>
            ) : (
              <>
                <Sparkles size={20} className="mr-2" />
                Generate Summary
              </>
            )}
          </button>
        </div>
      </Card>

      {result && (
        <Card title="Summary Results">
          <div className="space-y-6">
            {/* Priority */}
            <div className="flex items-center space-x-2">
              <span className="text-sm font-medium text-gray-700">Priority:</span>
              <span className={`font-semibold ${getPriorityColor(result.priority)}`}>
                {getPriorityLabel(result.priority)} ({result.priority}/5)
              </span>
            </div>

            {/* Parsed Email Info */}
            {result.parsed_email && (
              <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                {result.parsed_email.subject && (
                  <div>
                    <span className="font-medium text-gray-700">Subject:</span>{' '}
                    <span className="text-gray-600">{result.parsed_email.subject}</span>
                  </div>
                )}
                {result.parsed_email.from && (
                  <div>
                    <span className="font-medium text-gray-700">From:</span>{' '}
                    <span className="text-gray-600">{result.parsed_email.from}</span>
                  </div>
                )}
              </div>
            )}

            {/* Summary */}
            <div>
              <h3 className="font-semibold text-gray-900 mb-2 flex items-center">
                <Sparkles className="text-primary-600 mr-2" size={20} />
                Summary
              </h3>
              <p className="text-gray-700 leading-relaxed">{result.summary}</p>
            </div>

            {/* Key Points */}
            {result.key_points && result.key_points.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Key Points</h3>
                <ul className="space-y-2">
                  {result.key_points.map((point, index) => (
                    <li key={index} className="flex items-start">
                      <CheckCircle className="text-green-500 mr-2 mt-1 flex-shrink-0" size={16} />
                      <span className="text-gray-700">{point}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Actions */}
            {result.actions && result.actions.length > 0 && (
              <div>
                <h3 className="font-semibold text-gray-900 mb-2">Action Items</h3>
                <ul className="space-y-2">
                  {result.actions.map((action, index) => (
                    <li key={index} className="flex items-start">
                      <AlertCircle className="text-primary-600 mr-2 mt-1 flex-shrink-0" size={16} />
                      <span className="text-gray-700">{action}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <button
              onClick={() => setResult(null)}
              className="btn-secondary"
            >
              Summarize Another Email
            </button>
          </div>
        </Card>
      )}
    </div>
  );
};

export default ManualInput;
