import React, { useState, useEffect } from 'react';
import { useUser } from '@clerk/clerk-react';
import { useIsPro } from '../lib/auth';
import Card from '../components/Card';
import { Sparkles, CreditCard, User, Shield } from 'lucide-react';
import { redirectToCheckout, redirectToPortal } from '../lib/billing';
import { getSubscription, getPricing } from '../lib/api';

const Settings = () => {
  const { user } = useUser();
  const isPro = useIsPro();
  const [subscription, setSubscription] = useState(null);
  const [pricing, setPricing] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [isPro]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [pricingData, subData] = await Promise.all([
        getPricing(),
        isPro ? getSubscription().catch(() => null) : Promise.resolve(null),
      ]);

      setPricing(pricingData);
      setSubscription(subData);
    } catch (error) {
      console.error('Error loading settings data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpgrade = async () => {
    try {
      await redirectToCheckout();
    } catch (error) {
      alert('Error redirecting to checkout');
    }
  };

  const handleManageSubscription = async () => {
    try {
      await redirectToPortal();
    } catch (error) {
      alert('Error opening customer portal');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <p className="text-gray-600 mt-2">
          Manage your account and subscription
        </p>
      </div>

      {/* Account Info */}
      <Card title="Account Information">
        <div className="space-y-4">
          <div className="flex items-center space-x-4">
            <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
              <User className="text-primary-600" size={32} />
            </div>
            <div>
              <p className="font-medium text-gray-900">{user?.fullName || user?.emailAddresses[0]?.emailAddress}</p>
              <p className="text-sm text-gray-600">{user?.emailAddresses[0]?.emailAddress}</p>
            </div>
          </div>

          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="font-medium text-gray-900">Current Plan</p>
                <p className="text-sm text-gray-600">
                  {isPro ? 'PRO - Premium features enabled' : 'FREE - Limited features'}
                </p>
              </div>
              <div className={`px-4 py-2 rounded-full ${isPro ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-700'}`}>
                {isPro ? (
                  <div className="flex items-center space-x-2">
                    <Sparkles size={16} />
                    <span className="font-semibold">PRO</span>
                  </div>
                ) : (
                  <span className="font-semibold">FREE</span>
                )}
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Subscription */}
      {isPro && subscription ? (
        <Card title="Subscription">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Status</p>
                <p className="font-medium text-gray-900 capitalize">{subscription.status}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Plan</p>
                <p className="font-medium text-gray-900">$9.99/month</p>
              </div>
            </div>

            {subscription.current_period_end && (
              <div>
                <p className="text-sm text-gray-600">Next billing date</p>
                <p className="font-medium text-gray-900">
                  {new Date(subscription.current_period_end * 1000).toLocaleDateString()}
                </p>
              </div>
            )}

            <button onClick={handleManageSubscription} className="btn-primary w-full">
              <CreditCard size={16} className="mr-2 inline" />
              Manage Subscription
            </button>

            <p className="text-xs text-gray-500 text-center">
              Update payment method, cancel subscription, view invoices
            </p>
          </div>
        </Card>
      ) : !isPro && pricing ? (
        <Card title="Upgrade to PRO">
          <div className="space-y-6">
            <div className="bg-gradient-to-br from-primary-50 to-primary-100 rounded-lg p-6">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">PRO Plan</h3>
                  <p className="text-gray-600 mt-1">Unlock all premium features</p>
                </div>
                <div className="text-right">
                  <p className="text-3xl font-bold text-primary-600">$9.99</p>
                  <p className="text-sm text-gray-600">/month</p>
                </div>
              </div>

              <ul className="space-y-3">
                {pricing.plans[1]?.features.map((feature, index) => (
                  <li key={index} className="flex items-center text-gray-700">
                    <svg
                      className="w-5 h-5 text-green-500 mr-3 flex-shrink-0"
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

            <button onClick={handleUpgrade} className="btn-primary w-full text-lg py-4">
              <Sparkles size={20} className="mr-2 inline" />
              Upgrade to PRO
            </button>

            <p className="text-xs text-gray-500 text-center">
              Cancel anytime. No questions asked.
            </p>
          </div>
        </Card>
      ) : null}

      {/* Security */}
      <Card title="Security & Privacy">
        <div className="space-y-4">
          <div className="flex items-start space-x-3">
            <Shield className="text-green-500 mt-1" size={20} />
            <div>
              <p className="font-medium text-gray-900">Data Encryption</p>
              <p className="text-sm text-gray-600">
                All your email credentials are encrypted at rest using industry-standard encryption
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Shield className="text-green-500 mt-1" size={20} />
            <div>
              <p className="font-medium text-gray-900">Secure Authentication</p>
              <p className="text-sm text-gray-600">
                Authentication powered by Clerk with JWT tokens
              </p>
            </div>
          </div>

          <div className="flex items-start space-x-3">
            <Shield className="text-green-500 mt-1" size={20} />
            <div>
              <p className="font-medium text-gray-900">No Email Storage</p>
              <p className="text-sm text-gray-600">
                We only store summaries, not your original emails
              </p>
            </div>
          </div>
        </div>
      </Card>
    </div>
  );
};

export default Settings;
