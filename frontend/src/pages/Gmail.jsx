import React, { useState, useEffect } from 'react';
import { useIsPro } from '../lib/auth';
import Paywall from '../components/Paywall';
import Card from '../components/Card';
import EmailList from '../components/EmailList';
import Loader from '../components/Loader';
import { Mail, RefreshCw } from 'lucide-react';
import { getGmailStatus, getGmailAuthUrl, listGmailMessages, summarizeEmails } from '../lib/api';

const Gmail = () => {
  const isPro = useIsPro();
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState([]);
  const [selectedEmails, setSelectedEmails] = useState([]);
  const [summarizing, setSummarizing] = useState(false);
  const [summaries, setSummaries] = useState(null);

  useEffect(() => {
    if (isPro) {
      checkConnection();
    }
  }, [isPro]);

  const checkConnection = async () => {
    setLoading(true);
    try {
      const status = await getGmailStatus();
      setConnected(status.connected);

      if (status.connected) {
        await loadMessages();
      }
    } catch (error) {
      console.error('Error checking Gmail status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async () => {
    try {
      const { auth_url } = await getGmailAuthUrl();
      window.location.href = auth_url;
    } catch (error) {
      alert('Error connecting to Gmail. Please try again.');
    }
  };

  const loadMessages = async () => {
    setLoading(true);
    try {
      const data = await listGmailMessages(20, '');
      setMessages(data.messages || []);
    } catch (error) {
      alert('Error loading Gmail messages');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (selectedEmails.length === 0) {
      alert('Please select at least one email');
      return;
    }

    setSummarizing(true);
    try {
      const emailsToSummarize = messages
        .filter((msg) => selectedEmails.includes(msg.id))
        .map((msg) => ({
          id: msg.id,
          subject: msg.subject,
          from: msg.from,
          body: msg.body,
          date: msg.date,
        }));

      const result = await summarizeEmails(emailsToSummarize, 'gmail');
      setSummaries(result.summaries);
    } catch (error) {
      alert('Error generating summaries');
    } finally {
      setSummarizing(false);
    }
  };

  if (!isPro) {
    return (
      <div className="max-w-4xl mx-auto">
        <Paywall feature="Gmail integration" />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader size="lg" text="Loading Gmail..." />
      </div>
    );
  }

  if (!connected) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <Card title="Connect Gmail" subtitle="Authorize access to your Gmail account">
          <div className="text-center py-8">
            <Mail size={64} className="mx-auto mb-6 text-gray-400" />
            <p className="text-gray-600 mb-6">
              Connect your Gmail account to automatically fetch and summarize your emails
            </p>
            <button onClick={handleConnect} className="btn-primary">
              Connect Gmail Account
            </button>
          </div>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gmail</h1>
          <p className="text-gray-600 mt-2">
            Select emails to summarize with AI
          </p>
        </div>
        <button
          onClick={loadMessages}
          className="btn-secondary flex items-center"
          disabled={loading}
        >
          <RefreshCw size={16} className="mr-2" />
          Refresh
        </button>
      </div>

      {messages.length > 0 && (
        <div className="bg-white rounded-lg p-4 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <span className="text-sm text-gray-600">
              {selectedEmails.length} of {messages.length} selected
            </span>
            <button
              onClick={handleSummarize}
              disabled={selectedEmails.length === 0 || summarizing}
              className="btn-primary disabled:opacity-50"
            >
              {summarizing ? 'Summarizing...' : 'Summarize Selected'}
            </button>
          </div>
        </div>
      )}

      <Card>
        <EmailList
          emails={messages}
          selectedEmails={selectedEmails}
          onSelectEmail={setSelectedEmails}
        />
      </Card>

      {summaries && summaries.length > 0 && (
        <Card title="Summaries">
          <div className="space-y-4">
            {summaries.map((summary) => (
              <div key={summary.id} className="border-b border-gray-200 pb-4 last:border-0">
                <h3 className="font-semibold text-gray-900">{summary.subject}</h3>
                <p className="text-sm text-gray-600 mt-1">{summary.from}</p>
                <p className="text-gray-700 mt-3">{summary.summary}</p>
                {summary.actions && summary.actions.length > 0 && (
                  <div className="mt-3">
                    <span className="text-sm font-medium text-gray-700">Actions:</span>
                    <ul className="list-disc list-inside text-sm text-gray-600 mt-1">
                      {summary.actions.map((action, idx) => (
                        <li key={idx}>{action}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default Gmail;
