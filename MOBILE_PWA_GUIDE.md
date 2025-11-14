# Mobile & PWA Features Guide

Complete guide to the mobile-first responsive design and Progressive Web App (PWA) features added to Email AI SaaS.

## 🎯 Overview

The application is now fully mobile-responsive with PWA support, providing a native app-like experience on mobile devices with offline capabilities.

## 📱 Mobile-First Design

### Touch-Friendly Interface

All interactive elements meet the minimum touch target size of **48x48px**:

- **Buttons**: Increased padding (py-3 px-6) with min-height: 48px
- **Inputs**: Larger tap targets with 16px font size (prevents iOS zoom)
- **Navigation items**: Touch-optimized spacing
- **Icons**: Appropriately sized for mobile tapping

### Responsive Breakpoints

- **Mobile**: < 768px (md breakpoint)
- **Tablet/Desktop**: ≥ 768px

### Mobile-Specific Features

1. **Bottom Navigation Bar**
   - Visible only on mobile devices
   - Fixed position with safe-area support
   - 4 primary actions: Home, Gmail, History, Settings

2. **Hamburger Menu & Drawer**
   - Slide-out sidebar drawer on mobile
   - Swipe from left edge to open
   - Tap outside to close
   - Auto-close on route change

3. **Mobile Header**
   - Fixed top header on mobile
   - App branding
   - Menu toggle button

4. **Responsive Padding**
   - Cards: p-4 on mobile, p-6 on desktop
   - Content: p-4 on mobile, p-8 on desktop
   - Bottom spacing for navigation: 80px on mobile

## 🚀 Progressive Web App (PWA)

### Installation

Users can install the app on their devices:

- **Android**: Chrome prompts "Add to Home Screen"
- **iOS**: Safari "Add to Home Screen"
- **Desktop**: Chrome/Edge install icon in address bar

### Manifest Configuration

Location: `/frontend/public/manifest.json`

Key features:
- App name and branding
- Icons (192x192, 512x512)
- Standalone display mode
- Portrait orientation
- Theme color (#0ea5e9)
- App shortcuts

### Service Worker

Location: `/frontend/public/service-worker.js`

**Caching Strategies:**

1. **Static Assets** (Cache-first with background update)
   - HTML, CSS, JavaScript
   - Images, icons
   - Offline page

2. **API Calls** (Network-first with cache fallback)
   - Summarization endpoints
   - Email integration APIs
   - User data

**Features:**
- Precaching on install
- Runtime caching
- Offline fallback
- Background sync (ready)
- Push notifications (framework ready)
- Update notifications

### Offline Support

When offline:
- Cached pages remain functional
- API calls use cached data
- Custom offline page shown
- Auto-reconnect detection

## 🎨 Mobile UI Components

### 1. MobileNav (Bottom Navigation)

Location: `/frontend/src/components/MobileNav.jsx`

```jsx
<MobileNav />
```

Features:
- 4 primary navigation items
- Active state highlighting
- Touch-optimized sizing
- Safe-area padding for notched devices

### 2. MobileHeader

Location: `/frontend/src/components/MobileHeader.jsx`

```jsx
<MobileHeader onMenuClick={handleMenuOpen} />
```

Features:
- Hamburger menu button
- App branding
- Fixed positioning
- Safe-area top padding

### 3. InstallPrompt

Location: `/frontend/src/components/InstallPrompt.jsx`

```jsx
<InstallPrompt />
```

Features:
- Detects `beforeinstallprompt` event
- Custom install UI
- Persistent state (localStorage)
- Auto-dismiss after install
- Polish language support

### 4. PullToRefresh

Location: `/frontend/src/components/PullToRefresh.jsx`

```jsx
<PullToRefresh onRefresh={async () => { /* refresh logic */ }}>
  {children}
</PullToRefresh>
```

Features:
- Native pull-to-refresh gesture
- Visual feedback
- Loading state
- Resistance curve
- Customizable threshold

### 5. Updated Sidebar (Drawer Mode)

Location: `/frontend/src/components/Sidebar.jsx`

```jsx
<Sidebar isOpen={drawerOpen} onClose={handleClose} />
```

Features:
- Desktop: Fixed sidebar
- Mobile: Slide-out drawer
- Overlay background
- Close on route change
- Escape key support

## 🎯 Touch Gestures

### Implemented Gestures

1. **Pull-to-Refresh**
   - Pull down from top to refresh content
   - Visual indicator shows progress
   - Works on email lists (Gmail, Outlook, IMAP)

2. **Swipe to Open Drawer**
   - Swipe from left edge to open menu
   - Framework ready in styles

3. **Tap Feedback**
   - Visual scale feedback on tap
   - Applied via `.tap-feedback` class
   - Only on touch devices

## ⚡ Performance Optimizations

### 1. Lazy Loading

All pages are lazy-loaded:

```jsx
const ManualInput = lazy(() => import('./pages/ManualInput'));
const Gmail = lazy(() => import('./pages/Gmail'));
// ... etc
```

Benefits:
- Smaller initial bundle
- Faster first load
- Code splitting per route

### 2. Service Worker Caching

- Static assets cached on install
- API responses cached for offline use
- Background updates for stale data

### 3. Viewport Height Fix

Handles mobile browser chrome:

```javascript
const vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty('--vh', `${vh}px`);
```

Use in CSS:
```css
height: calc(var(--vh, 1vh) * 100);
```

## 📋 Mobile-Specific Styles

### Custom CSS Classes

```css
/* Mobile sticky action buttons */
.mobile-sticky-action

/* Drawer overlay */
.drawer-overlay

/* Drawer slide animation */
.drawer
.drawer.open

/* Pull-to-refresh indicator */
.pull-to-refresh
.pull-to-refresh.visible

/* Touch feedback */
.tap-feedback

/* Mobile content wrapper */
.mobile-content-wrapper

/* Safe area support */
.safe-area-top
.safe-area-bottom
```

### iOS-Specific Fixes

```css
/* Prevent zoom on input focus */
input, textarea {
  font-size: 16px;
}

/* Remove iOS input styling */
-webkit-appearance: none;

/* Remove tap highlight */
-webkit-tap-highlight-color: transparent;

/* Prevent text size adjustment */
-webkit-text-size-adjust: 100%;

/* Prevent pull-to-refresh */
overscroll-behavior-y: contain;
```

## 🔧 Configuration

### Required Meta Tags

Already added to `index.html`:

```html
<!-- Viewport with safe-area -->
<meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover" />

<!-- PWA Manifest -->
<link rel="manifest" href="/manifest.json" />

<!-- Icons -->
<link rel="apple-touch-icon" href="/icon-192.png" />

<!-- Theme Color -->
<meta name="theme-color" content="#0ea5e9" />

<!-- Mobile Web App -->
<meta name="mobile-web-app-capable" content="yes" />
<meta name="apple-mobile-web-app-capable" content="yes" />
```

### Environment Variables

No additional variables needed. PWA works out of the box.

## 📱 Testing on Mobile

### Chrome DevTools

1. Open DevTools
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select mobile device
4. Test:
   - Responsive layout
   - Touch interactions
   - Bottom navigation
   - Drawer menu

### Lighthouse Audit

Run PWA audit:

```bash
npm run build
npx serve -s dist
```

Then in Chrome DevTools:
1. Go to Lighthouse tab
2. Select "Progressive Web App"
3. Run audit
4. Expected score: ≥ 95

### Real Device Testing

**Android:**
1. Deploy to HTTPS server
2. Open in Chrome
3. Tap "Add to Home Screen"
4. Test installed app

**iOS:**
1. Deploy to HTTPS server
2. Open in Safari
3. Tap Share → "Add to Home Screen"
4. Test installed app

## 🎨 Customization

### Change Theme Color

Update in:
- `/frontend/public/manifest.json` - `theme_color`
- `/frontend/index.html` - `<meta name="theme-color">`
- `/frontend/src/styles.css` - `.pwa-install-banner` border

### Custom Icons

Generate icons:
1. Open `/frontend/public/generate-icons.html` in browser
2. Right-click canvases and save as PNG
3. Save as `icon-192.png` and `icon-512.png`

Or use your own 192x192 and 512x512 PNG files.

### Install Prompt Text

Edit: `/frontend/src/components/InstallPrompt.jsx`

```jsx
<h3>Zainstaluj aplikację EmailAI</h3>
<p>Szybki dostęp, offline support, push notifications</p>
```

Change to your preferred language.

## 🐛 Common Issues

### Service Worker Not Updating

**Solution:**
```javascript
// In browser console
navigator.serviceWorker.getRegistrations().then(function(registrations) {
  for(let registration of registrations) {
    registration.unregister();
  }
});
```

Then reload.

### PWA Not Installing

**Check:**
1. HTTPS required (except localhost)
2. Valid manifest.json
3. Icons present (192x192, 512x512)
4. Service worker registered
5. No console errors

### Mobile Drawer Not Opening

**Check:**
1. `drawerOpen` state managed correctly
2. Overlay z-index (should be 40)
3. Drawer z-index (should be 50)
4. Transform transitions enabled

## 📚 Resources

- [PWA Checklist](https://web.dev/pwa-checklist/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://web.dev/add-manifest/)
- [Mobile Touch Best Practices](https://web.dev/mobile-touch/)
- [iOS Web Apps](https://developer.apple.com/design/human-interface-guidelines/ios/icons-and-images/launch-screen/)

## 🎉 Features Summary

✅ **Mobile-first responsive design**
✅ **Touch-friendly 48px+ tap targets**
✅ **Bottom navigation for mobile**
✅ **Slide-out drawer menu**
✅ **PWA installable on all platforms**
✅ **Service Worker with offline support**
✅ **Pull-to-refresh gestures**
✅ **Custom install prompts**
✅ **Lazy loading for performance**
✅ **Safe-area support for notched devices**
✅ **iOS-specific optimizations**
✅ **Lighthouse PWA score ready**

---

**The app is now ready for mobile deployment and PWA installation!**
