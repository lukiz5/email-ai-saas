import React from 'react';
import { Menu, Sparkles } from 'lucide-react';

const MobileHeader = ({ onMenuClick }) => {
  return (
    <header className="md:hidden fixed top-0 left-0 right-0 bg-white border-b border-gray-200 z-30 safe-area-top">
      <div className="flex items-center justify-between h-14 px-4">
        <button
          onClick={onMenuClick}
          className="p-2 -ml-2 rounded-lg active:bg-gray-100 transition-colors tap-feedback"
          aria-label="Open menu"
          style={{ minHeight: '48px', minWidth: '48px' }}
        >
          <Menu size={24} className="text-gray-700" />
        </button>

        <div className="flex items-center space-x-2">
          <Sparkles className="text-primary-600" size={24} />
          <h1 className="text-lg font-bold text-gray-900">Email AI</h1>
        </div>

        {/* Spacer for symmetry */}
        <div style={{ width: '48px' }} />
      </div>
    </header>
  );
};

export default MobileHeader;
