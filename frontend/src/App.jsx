import React, { Suspense, lazy, useState } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut, SignIn, SignUp, RedirectToSignIn } from '@clerk/clerk-react';
import Sidebar from './components/Sidebar';
import MobileNav from './components/MobileNav';
import MobileHeader from './components/MobileHeader';
import InstallPrompt from './components/InstallPrompt';
import Loader from './components/Loader';
import { useAuthSync } from './lib/auth';

// Lazy load pages for better performance
const ManualInput = lazy(() => import('./pages/ManualInput'));
const Gmail = lazy(() => import('./pages/Gmail'));
const Outlook = lazy(() => import('./pages/Outlook'));
const IMAP = lazy(() => import('./pages/IMAP'));
const History = lazy(() => import('./pages/History'));
const Settings = lazy(() => import('./pages/Settings'));

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || 'pk_test_XXXXXX';

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-screen">
    <Loader size="lg" text="Loading..." />
  </div>
);

// Protected route wrapper
const ProtectedRoute = ({ children }) => {
  return (
    <>
      <SignedIn>{children}</SignedIn>
      <SignedOut>
        <RedirectToSignIn />
      </SignedOut>
    </>
  );
};

// Public route (allows both signed in and signed out)
const PublicRoute = ({ children }) => {
  return children;
};

// Main app content with layout
const AppContent = () => {
  useAuthSync(); // Sync auth token

  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden">
      {/* Desktop sidebar / Mobile drawer */}
      <Sidebar isOpen={drawerOpen} onClose={() => setDrawerOpen(false)} />

      {/* Mobile header */}
      <MobileHeader onMenuClick={() => setDrawerOpen(true)} />

      {/* Main content */}
      <main className="flex-1 overflow-y-auto md:overflow-auto">
        <div className="p-4 md:p-8 pt-16 md:pt-8 mobile-content-wrapper">
          <Suspense fallback={<PageLoader />}>
            <Routes>
              {/* Public route - FREE tier */}
              <Route path="/" element={<PublicRoute><ManualInput /></PublicRoute>} />

              {/* Protected routes - require login */}
              <Route
                path="/gmail"
                element={
                  <ProtectedRoute>
                    <Gmail />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/outlook"
                element={
                  <ProtectedRoute>
                    <Outlook />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/imap"
                element={
                  <ProtectedRoute>
                    <IMAP />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/history"
                element={
                  <ProtectedRoute>
                    <History />
                  </ProtectedRoute>
                }
              />
              <Route
                path="/settings"
                element={
                  <ProtectedRoute>
                    <Settings />
                  </ProtectedRoute>
                }
              />

              {/* Catch all */}
              <Route path="*" element={<ManualInput />} />
            </Routes>
          </Suspense>
        </div>
      </main>

      {/* Mobile bottom navigation */}
      <MobileNav />

      {/* PWA Install prompt */}
      <InstallPrompt />
    </div>
  );
};

// Sign in page
const SignInPage = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <SignIn routing="path" path="/sign-in" signUpUrl="/sign-up" />
  </div>
);

// Sign up page
const SignUpPage = () => (
  <div className="min-h-screen flex items-center justify-center bg-gray-50">
    <SignUp routing="path" path="/sign-up" signInUrl="/sign-in" />
  </div>
);

function App() {
  return (
    <ClerkProvider publishableKey={CLERK_PUBLISHABLE_KEY}>
      <Router>
        <Routes>
          <Route path="/sign-in/*" element={<SignInPage />} />
          <Route path="/sign-up/*" element={<SignUpPage />} />
          <Route path="/*" element={<AppContent />} />
        </Routes>
      </Router>
    </ClerkProvider>
  );
}

export default App;
