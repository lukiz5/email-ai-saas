import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ClerkProvider, SignedIn, SignedOut, SignIn, SignUp, RedirectToSignIn } from '@clerk/clerk-react';
import Sidebar from './components/Sidebar';
import ManualInput from './pages/ManualInput';
import Gmail from './pages/Gmail';
import Outlook from './pages/Outlook';
import IMAP from './pages/IMAP';
import History from './pages/History';
import Settings from './pages/Settings';
import { useAuthSync } from './lib/auth';

const CLERK_PUBLISHABLE_KEY = import.meta.env.VITE_CLERK_PUBLISHABLE_KEY || 'pk_test_XXXXXX';

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

  return (
    <div className="flex h-screen bg-gray-50">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="p-8">
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
        </div>
      </main>
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
