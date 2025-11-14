import React, { useState, useEffect } from 'react';
import { Download, X, Sparkles } from 'lucide-react';

const InstallPrompt = () => {
  const [deferredPrompt, setDeferredPrompt] = useState(null);
  const [showPrompt, setShowPrompt] = useState(false);

  useEffect(() => {
    // Check if already dismissed
    const dismissed = localStorage.getItem('pwa-install-dismissed');
    const installed = localStorage.getItem('pwa-installed');

    if (dismissed || installed) {
      return;
    }

    // Listen for beforeinstallprompt event
    const handleBeforeInstallPrompt = (e) => {
      // Prevent Chrome 67 and earlier from automatically showing the prompt
      e.preventDefault();

      // Stash the event so it can be triggered later
      setDeferredPrompt(e);

      // Show custom install prompt after a delay
      setTimeout(() => {
        setShowPrompt(true);
      }, 3000); // Show after 3 seconds
    };

    window.addEventListener('beforeinstallprompt', handleBeforeInstallPrompt);

    // Detect if app was successfully installed
    window.addEventListener('appinstalled', () => {
      console.log('PWA installed successfully');
      localStorage.setItem('pwa-installed', 'true');
      setShowPrompt(false);
      setDeferredPrompt(null);
    });

    return () => {
      window.removeEventListener('beforeinstallprompt', handleBeforeInstallPrompt);
    };
  }, []);

  const handleInstall = async () => {
    if (!deferredPrompt) {
      return;
    }

    // Show the install prompt
    deferredPrompt.prompt();

    // Wait for the user to respond to the prompt
    const { outcome } = await deferredPrompt.userChoice;

    console.log(`User response to install prompt: ${outcome}`);

    if (outcome === 'accepted') {
      console.log('User accepted the install prompt');
      localStorage.setItem('pwa-installed', 'true');
    } else {
      console.log('User dismissed the install prompt');
      localStorage.setItem('pwa-install-dismissed', 'true');
    }

    // Clear the deferredPrompt
    setDeferredPrompt(null);
    setShowPrompt(false);
  };

  const handleDismiss = () => {
    setShowPrompt(false);
    localStorage.setItem('pwa-install-dismissed', 'true');
  };

  if (!showPrompt) {
    return null;
  }

  return (
    <div className="pwa-install-banner">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3 flex-1">
          <div className="flex-shrink-0">
            <div className="w-12 h-12 bg-primary-100 rounded-xl flex items-center justify-center">
              <Sparkles className="text-primary-600" size={24} />
            </div>
          </div>

          <div className="flex-1 min-w-0">
            <h3 className="text-sm font-semibold text-gray-900">
              Zainstaluj aplikację EmailAI
            </h3>
            <p className="text-xs text-gray-600 mt-0.5">
              Szybki dostęp, offline support, push notifications
            </p>
          </div>
        </div>

        <div className="flex items-center space-x-2 ml-4">
          <button
            onClick={handleInstall}
            className="flex items-center space-x-1 bg-primary-600 text-white px-4 py-2 rounded-lg font-medium text-sm active:bg-primary-700 transition-colors tap-feedback"
          >
            <Download size={16} />
            <span className="hidden sm:inline">Instaluj</span>
          </button>

          <button
            onClick={handleDismiss}
            className="p-2 text-gray-500 active:bg-gray-100 rounded-lg transition-colors tap-feedback"
            aria-label="Dismiss"
          >
            <X size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default InstallPrompt;
