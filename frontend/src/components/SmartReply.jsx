import React, { useState } from 'react';
import { Sparkles, Copy, Check } from 'lucide-react';

const SmartReply = ({ emailText, onGenerate }) => {
  const [tone, setTone] = useState('professional');
  const [reply, setReply] = useState('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  const tones = [
    { value: 'professional', label: 'Professional' },
    { value: 'friendly', label: 'Friendly' },
    { value: 'brief', label: 'Brief' },
  ];

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const generatedReply = await onGenerate(emailText, tone);
      setReply(generatedReply);
    } catch (error) {
      alert('Error generating reply');
    } finally {
      setLoading(false);
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(reply);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-gray-900 flex items-center">
          <Sparkles className="text-primary-600 mr-2" size={20} />
          Smart Reply
        </h3>
        <select
          value={tone}
          onChange={(e) => setTone(e.target.value)}
          className="input-field w-40"
        >
          {tones.map((t) => (
            <option key={t.value} value={t.value}>
              {t.label}
            </option>
          ))}
        </select>
      </div>

      {!reply && (
        <button
          onClick={handleGenerate}
          disabled={loading}
          className="btn-primary w-full disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Reply'}
        </button>
      )}

      {reply && (
        <div className="space-y-3">
          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <p className="text-gray-800 whitespace-pre-wrap">{reply}</p>
          </div>

          <div className="flex space-x-2">
            <button onClick={handleCopy} className="btn-secondary flex items-center">
              {copied ? <Check size={16} className="mr-2" /> : <Copy size={16} className="mr-2" />}
              {copied ? 'Copied!' : 'Copy'}
            </button>
            <button onClick={handleGenerate} className="btn-secondary" disabled={loading}>
              Regenerate
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default SmartReply;
