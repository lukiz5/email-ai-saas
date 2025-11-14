import React, { useState, useEffect } from 'react';
import { useIsPro } from '../lib/auth';
import Paywall from '../components/Paywall';
import Card from '../components/Card';
import Loader from '../components/Loader';
import { History as HistoryIcon, Trash2, Calendar } from 'lucide-react';
import { getSummaries, deleteSummary, getStats, clearHistory } from '../lib/api';

const History = () => {
  const isPro = useIsPro();
  const [loading, setLoading] = useState(true);
  const [summaries, setSummaries] = useState([]);
  const [stats, setStats] = useState(null);
  const [selectedSource, setSelectedSource] = useState('all');

  useEffect(() => {
    if (isPro) {
      loadData();
    }
  }, [isPro, selectedSource]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [summariesData, statsData] = await Promise.all([
        getSummaries(50, 0, selectedSource === 'all' ? null : selectedSource),
        getStats(),
      ]);

      setSummaries(summariesData.summaries || []);
      setStats(statsData);
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (summaryId) => {
    if (!confirm('Delete this summary?')) return;

    try {
      await deleteSummary(summaryId);
      setSummaries(summaries.filter((s) => s.id !== summaryId));
    } catch (error) {
      alert('Error deleting summary');
    }
  };

  const handleClearAll = async () => {
    if (!confirm('Delete ALL summaries? This cannot be undone.')) return;

    try {
      await clearHistory();
      setSummaries([]);
      loadData();
    } catch (error) {
      alert('Error clearing history');
    }
  };

  if (!isPro) {
    return (
      <div className="max-w-4xl mx-auto">
        <Paywall feature="history and cloud sync" />
      </div>
    );
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader size="lg" text="Loading history..." />
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">History</h1>
          <p className="text-gray-600 mt-2">
            Your email summary history (cloud synced)
          </p>
        </div>
        {summaries.length > 0 && (
          <button onClick={handleClearAll} className="btn-secondary text-red-600 hover:bg-red-50">
            Clear All
          </button>
        )}
      </div>

      {/* Stats */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">{stats.total_summaries}</p>
              <p className="text-sm text-gray-600 mt-1">Total Summaries</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">{stats.average_priority}</p>
              <p className="text-sm text-gray-600 mt-1">Avg Priority</p>
            </div>
          </Card>
          <Card>
            <div className="text-center">
              <p className="text-3xl font-bold text-primary-600">
                {Object.keys(stats.by_source || {}).length}
              </p>
              <p className="text-sm text-gray-600 mt-1">Sources Used</p>
            </div>
          </Card>
        </div>
      )}

      {/* Filter */}
      <div className="flex items-center space-x-2">
        <span className="text-sm text-gray-600">Filter:</span>
        <select
          value={selectedSource}
          onChange={(e) => setSelectedSource(e.target.value)}
          className="input-field w-48"
        >
          <option value="all">All Sources</option>
          <option value="gmail">Gmail</option>
          <option value="outlook">Outlook</option>
          <option value="imap">IMAP</option>
          <option value="manual">Manual</option>
        </select>
      </div>

      {/* Summaries List */}
      <Card>
        {summaries.length === 0 ? (
          <div className="text-center py-12 text-gray-500">
            <HistoryIcon size={48} className="mx-auto mb-4 opacity-50" />
            <p>No summaries found</p>
          </div>
        ) : (
          <div className="space-y-4">
            {summaries.map((summary) => (
              <div
                key={summary.id}
                className="border border-gray-200 rounded-lg p-4 hover:border-gray-300 transition-colors"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-2 mb-2">
                      <span className="text-xs font-medium text-primary-600 bg-primary-50 px-2 py-1 rounded">
                        {summary.source}
                      </span>
                      {summary.priority && (
                        <span className="text-xs font-medium text-gray-600 bg-gray-100 px-2 py-1 rounded">
                          Priority: {summary.priority}/5
                        </span>
                      )}
                    </div>

                    <h3 className="font-semibold text-gray-900 mb-1">
                      {summary.subject || 'No Subject'}
                    </h3>
                    <p className="text-sm text-gray-600 mb-2">{summary.from}</p>

                    <p className="text-gray-700 mb-3">{summary.summary}</p>

                    {summary.actions && (
                      <div className="text-sm">
                        <span className="font-medium text-gray-700">Actions:</span>
                        <span className="text-gray-600 ml-2">{summary.actions}</span>
                      </div>
                    )}

                    <div className="flex items-center text-xs text-gray-500 mt-3">
                      <Calendar size={12} className="mr-1" />
                      {new Date(summary.created_at).toLocaleString()}
                    </div>
                  </div>

                  <button
                    onClick={() => handleDelete(summary.id)}
                    className="ml-4 text-red-500 hover:text-red-700 p-2"
                  >
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default History;
