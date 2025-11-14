# Email AI SaaS - Frontend

React + Vite frontend for the Email AI SaaS platform.

## Features

- Modern React with Vite for fast development
- Tailwind CSS for styling
- Clerk for authentication
- Responsive design
- Route protection for PRO features
- Real-time API integration

## Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Environment Variables

Create `.env` file:

```env
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_your_key
```

### 3. Run Development Server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

### 4. Build for Production

```bash
npm run build
```

Build output will be in `dist/` directory.

## Project Structure

```
frontend/
├── src/
│   ├── components/       # Reusable UI components
│   │   ├── Sidebar.jsx   # Navigation sidebar
│   │   ├── Card.jsx      # Card wrapper
│   │   ├── EmailList.jsx # Email list display
│   │   ├── Loader.jsx    # Loading spinner
│   │   ├── Paywall.jsx   # PRO upgrade component
│   │   ├── Tabs.jsx      # Tab navigation
│   │   └── SmartReply.jsx # Smart reply generator
│   │
│   ├── pages/            # Page components
│   │   ├── ManualInput.jsx  # FREE - Manual email input
│   │   ├── Gmail.jsx        # PRO - Gmail integration
│   │   ├── Outlook.jsx      # PRO - Outlook integration
│   │   ├── IMAP.jsx         # PRO - IMAP integration
│   │   ├── History.jsx      # PRO - Summary history
│   │   └── Settings.jsx     # Settings & billing
│   │
│   ├── lib/              # Utilities & API
│   │   ├── api.js        # API client functions
│   │   ├── auth.js       # Auth utilities
│   │   └── billing.js    # Billing utilities
│   │
│   ├── App.jsx           # Main app component
│   ├── main.jsx          # App entry point
│   └── styles.css        # Global styles
│
├── package.json
├── vite.config.js
├── tailwind.config.js
└── postcss.config.js
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## Component Library

### Sidebar
Navigation sidebar with menu items and PRO upgrade button.

### Card
Reusable card wrapper with optional title and subtitle.

### EmailList
Display list of emails with checkbox selection.

### Loader
Loading spinner component with configurable size.

### Paywall
PRO upgrade prompt for locked features.

### Tabs
Tab navigation component.

### SmartReply
AI-powered reply generation component.

## Pages

### ManualInput (FREE)
- Paste email text
- Get AI summary
- View actions and priority
- No login required

### Gmail (PRO)
- OAuth connection
- List messages
- Select and summarize
- Cloud sync

### Outlook (PRO)
- Microsoft 365 OAuth
- List messages
- Select and summarize
- Cloud sync

### IMAP (PRO)
- Connect with credentials
- Universal email support
- List messages
- Select and summarize

### History (PRO)
- View past summaries
- Filter by source
- Statistics dashboard
- Delete summaries

### Settings
- Account information
- Subscription management
- Upgrade to PRO
- Security info

## API Integration

All API calls are handled through `lib/api.js`:

```javascript
import { summarizeRaw, getGmailStatus } from './lib/api';

// Summarize raw email text (FREE)
const result = await summarizeRaw(emailText);

// Check Gmail connection status (PRO)
const status = await getGmailStatus();
```

## Authentication

Uses Clerk for authentication:

```javascript
import { useUser, useAuth } from '@clerk/clerk-react';

// Get current user
const { user } = useUser();

// Get auth token
const { getToken } = useAuth();
const token = await getToken();
```

## Routing

Routes are protected based on authentication:

- `/` - Public (FREE)
- `/gmail` - Protected (PRO)
- `/outlook` - Protected (PRO)
- `/imap` - Protected (PRO)
- `/history` - Protected (PRO)
- `/settings` - Protected

## Styling

Uses Tailwind CSS with custom configuration:

```javascript
// Custom classes in styles.css
.btn-primary
.btn-secondary
.btn-outline
.card
.input-field
.textarea-field
```

## Deployment

### Vercel

```bash
npm run build
vercel --prod
```

### Netlify

```bash
npm run build
netlify deploy --prod --dir=dist
```

### Docker

```bash
docker build -t email-ai-frontend .
docker run -p 80:80 email-ai-frontend
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| VITE_API_URL | Backend API URL | Yes |
| VITE_CLERK_PUBLISHABLE_KEY | Clerk public key | Yes |

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## License

MIT
