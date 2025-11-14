import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Mail, Inbox, History, Settings } from 'lucide-react';

const MobileNav = () => {
  const location = useLocation();

  const navItems = [
    { name: 'Home', path: '/', icon: Mail },
    { name: 'Gmail', path: '/gmail', icon: Inbox },
    { name: 'History', path: '/history', icon: History },
    { name: 'Settings', path: '/settings', icon: Settings },
  ];

  return (
    <nav className="md:hidden fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 z-50 safe-area-bottom">
      <div className="flex items-center justify-around h-16">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = location.pathname === item.path;

          return (
            <Link
              key={item.path}
              to={item.path}
              className={`
                flex flex-col items-center justify-center flex-1 h-full
                transition-colors duration-150 tap-feedback
                ${isActive ? 'text-primary-600' : 'text-gray-600'}
              `}
              style={{ minHeight: '48px' }}
            >
              <Icon size={24} />
              <span className="text-xs mt-1 font-medium">{item.name}</span>
            </Link>
          );
        })}
      </div>
    </nav>
  );
};

export default MobileNav;
