import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Mail, Inbox, MessageSquare, History, Settings, Sparkles } from 'lucide-react';
import { useIsPro } from '../lib/auth';

const Sidebar = () => {
  const location = useLocation();
  const isPro = useIsPro();

  const menuItems = [
    { name: 'Manual Input', path: '/', icon: Mail, free: true },
    { name: 'Gmail', path: '/gmail', icon: Inbox, free: false },
    { name: 'Outlook', path: '/outlook', icon: MessageSquare, free: false },
    { name: 'IMAP', path: '/imap', icon: Inbox, free: false },
    { name: 'History', path: '/history', icon: History, free: false },
    { name: 'Settings', path: '/settings', icon: Settings, free: true },
  ];

  return (
    <div className="w-64 bg-white border-r border-gray-200 h-screen flex flex-col">
      {/* Logo */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Sparkles className="text-primary-600" size={32} />
          <div>
            <h1 className="text-xl font-bold text-gray-900">Email AI</h1>
            <p className="text-xs text-gray-500">Smart Summaries</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;
          const isLocked = !item.free && !isPro;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex items-center space-x-3 px-4 py-3 rounded-lg transition-colors duration-150
                ${isActive
                  ? 'bg-primary-50 text-primary-700 font-medium'
                  : 'text-gray-700 hover:bg-gray-50'
                }
                ${isLocked ? 'opacity-50 cursor-not-allowed' : ''}
              `}
              onClick={(e) => {
                if (isLocked) {
                  e.preventDefault();
                  alert('PRO feature - Please upgrade to access');
                }
              }}
            >
              <Icon size={20} />
              <span>{item.name}</span>
              {isLocked && (
                <span className="ml-auto">
                  <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                    <path
                      fillRule="evenodd"
                      d="M5 9V7a5 5 0 0110 0v2a2 2 0 012 2v5a2 2 0 01-2 2H5a2 2 0 01-2-2v-5a2 2 0 012-2zm8-2v2H7V7a3 3 0 016 0z"
                      clipRule="evenodd"
                    />
                  </svg>
                </span>
              )}
            </Link>
          );
        })}
      </nav>

      {/* PRO Badge / Upgrade Button */}
      <div className="p-4 border-t border-gray-200">
        {isPro ? (
          <div className="bg-gradient-to-r from-primary-500 to-primary-600 text-white px-4 py-3 rounded-lg text-center">
            <div className="flex items-center justify-center space-x-2">
              <Sparkles size={16} />
              <span className="font-semibold">PRO Member</span>
            </div>
          </div>
        ) : (
          <Link
            to="/settings"
            className="block w-full bg-gradient-to-r from-primary-500 to-primary-600 text-white px-4 py-3 rounded-lg text-center font-semibold hover:from-primary-600 hover:to-primary-700 transition-all duration-200"
          >
            Upgrade to PRO
          </Link>
        )}
      </div>
    </div>
  );
};

export default Sidebar;
