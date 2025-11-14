import React, { useState, useEffect } from 'react';
import { useIsPro } from '../lib/auth';
import Paywall from '../components/Paywall';
import Card from '../components/Card';
import EmailList from '../components/EmailList';
import Loader from '../components/Loader';
import { Inbox, RefreshCw } from 'lucide-react';
import { getIMAPStatus, connectIMAP, listIMAPMessages, disconnectIMAP, summarizeEmails } from '../lib/api';

const IMAP = () => {
  const isPro = useIsPro();
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const [connecting, setConnecting] = useState(false);
  const [messages, setMessages] = useState([]);
  const [selectedEmails, setSelectedEmails] = useState([]);
  const [summarizing, setSummarizing] = useState(false);
  const [summaries, setSummaries] = useState(null);
  const [connectedEmail, setConnectedEmail] = useState(null);

  // Connection form
  const [formData, setFormData] = useState({
    host: '',
    email: '',
    password: '',
    port: 993,
  });

  useEffect(() => {
    if (isPro) {
      checkConnection();
    }
  }, [isPro]);

  const checkConnection = async () => {
    setLoading(true);
    try {
      const status = await getIMAPStatus();
      setConnected(status.connected);
      setConnectedEmail(status.email);

      if (status.connected) {
        await loadMessages();
      }
    } catch (error) {
      console.error('Error checking IMAP status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (e) => {
    e.preventDefault();

    if (!formData.host || !formData.email || !formData.password) {
      alert('Please fill in all fields');
      return;
    }

    setConnecting(true);
    try {
      await connectIMAP(
        formData.host,
        formData.email,
        formData.password,
        formData.port
      );

      setConnected(true);
      await loadMessages();

      // Clear password
      setFormData({ ...formData, password: '' });
    } catch (error) {
      alert('Error connecting to IMAP server. Please check your credentials.');
    } finally {
      setConnecting(false);
    }
  };

  const handleDisconnect = async () => {
    try {
      await disconnectIMAP();
      setConnected(false);
      setMessages([]);
      setSelectedEmails([]);
      setSummaries(null);
      setConnectedEmail(null);
    } catch (error) {
      alert('Error disconnecting');
    }
  };

  const loadMessages = async () => {
    setLoading(true);
    try {
      const data = await listIMAPMessages(20, 'INBOX', false);
      setMessages(data.messages || []);
    } catch (error) {
      alert('Error loading messages');
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

      const result = await summarizeEmails(emailsToSummarize, 'imap');
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
        <Paywall feature="IMAP integration" />
      </div>
    );
  }

  if (loading && !connected) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader size="lg" text="Loading IMAP..." />
      </div>
    );
  }

  if (!connected) {
    return (
      <div className="max-w-2xl mx-auto mt-12">
        <Card title="Connect IMAP Email" subtitle="Connect any email provider using IMAP">
          <form onSubmit={handleConnect} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                IMAP Host
              </label>
              <input
                type="text"
                value={formData.host}
                onChange={(e) => setFormData({ ...formData, host: e.target.value })}
                placeholder="imap.gmail.com"
                className="input-field"
              />
              <p className="text-xs text-gray-500 mt-1">
                Common: imap.gmail.com, imap.mail.yahoo.com, outlook.office365.com
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Email Address
              </label>
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="your@email.com"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Password
              </label>
              <input
                type="password"
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="App password (recommended)"
                className="input-field"
              />
              <p className="text-xs text-gray-500 mt-1">
                For Gmail/Yahoo, use an app-specific password
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Port
              </label>
              <input
                type="number"
                value={formData.port}
                onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
                className="input-field"
              />
              <p className="text-xs text-gray-500 mt-1">
                Default: 993 (SSL/TLS)
              </p>
            </div>

            <button
              type="submit"
              disabled={connecting}
              className="btn-primary w-full disabled:opacity-50"
            >
              {connecting ? 'Connecting...' : 'Connect IMAP'}
            </button>
          </form>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">IMAP Email</h1>
          <p className="text-gray-600 mt-2">
            Connected: {connectedEmail}
          </p>
        </div>
        <div className="flex space-x-2">
          <button
            onClick={loadMessages}
            className="btn-secondary flex items-center"
            disabled={loading}
          >
            <RefreshCw size={16} className="mr-2" />
            Refresh
          </button>
          <button onClick={handleDisconnect} className="btn-secondary">
            Disconnect
          </button>
        </div>
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
        {loading ? (
          <div className="py-12">
            <Loader size="lg" text="Loading messages..." />
          </div>
        ) : (
          <EmailList
            emails={messages}
            selectedEmails={selectedEmails}
            onSelectEmail={setSelectedEmails}
          />
        )}
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

export default IMAP;
