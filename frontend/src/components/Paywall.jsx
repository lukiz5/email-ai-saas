import React from 'react';
import { Lock, Sparkles } from 'lucide-react';
import { redirectToCheckout } from '../lib/billing';
import { useState } from 'react';

const Paywall = ({ feature = 'this feature' }) => {
  const [loading, setLoading] = useState(false);

  const handleUpgrade = async () => {
    setLoading(true);
    try {
      await redirectToCheckout();
    } catch (error) {
      alert('Error redirecting to checkout. Please try again.');
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto mt-12">
      <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-2xl p-8 text-center border-2 border-primary-200">
        <div className="inline-flex items-center justify-center w-16 h-16 bg-white rounded-full mb-6 shadow-lg">
          <Lock className="text-primary-600" size={32} />
        </div>

        <h2 className="text-3xl font-bold text-gray-900 mb-4">
          Upgrade to PRO
        </h2>

        <p className="text-lg text-gray-700 mb-6">
          Unlock {feature} and all premium features
        </p>

        <div className="bg-white rounded-lg p-6 mb-6 text-left">
          <h3 className="font-semibold text-gray-900 mb-4 flex items-center">
            <Sparkles className="text-primary-600 mr-2" size={20} />
            PRO Features Include:
          </h3>
          <ul className="space-y-3">
            {[
              'Gmail integration',
              'Outlook integration',
              'IMAP support',
              'Smart AI replies',
              'Cloud history sync',
              'Priority scoring',
              'Unlimited summaries',
              'Priority support',
            ].map((feature, index) => (
              <li key={index} className="flex items-center text-gray-700">
                <svg
                  className="w-5 h-5 text-green-500 mr-3"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path
                    fillRule="evenodd"
                    d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z"
                    clipRule="evenodd"
                  />
                </svg>
                {feature}
              </li>
            ))}
          </ul>
        </div>

        <button
          onClick={handleUpgrade}
          disabled={loading}
          className="btn-primary text-lg px-8 py-4 w-full max-w-sm mx-auto disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? 'Redirecting...' : 'Upgrade Now - $9.99/month'}
        </button>

        <p className="text-sm text-gray-600 mt-4">
          Cancel anytime. No questions asked.
        </p>
      </div>
    </div>
  );
};

export default Paywall;
