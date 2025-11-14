# Email AI SaaS - Backend API

FastAPI backend for AI-powered email summarization SaaS platform.

## Features

- **AI Summarization**: Claude Sonnet 4.5 for email summaries, actions, and priority
- **Email Integrations**: Gmail, Outlook, IMAP support
- **Authentication**: Clerk JWT verification
- **Billing**: Stripe subscriptions (FREE/PRO plans)
- **Database**: PostgreSQL with SQLAlchemy ORM

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/email_ai_saas

# Anthropic AI
ANTHROPIC_API_KEY=your_anthropic_api_key

# Clerk Authentication
CLERK_PEM_PUBLIC_KEY=your_clerk_public_key

# Stripe Billing
STRIPE_SECRET_KEY=your_stripe_secret_key
STRIPE_PRICE_ID_PRO=price_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_SUCCESS_URL=http://localhost:5173/success
STRIPE_CANCEL_URL=http://localhost:5173/pricing
STRIPE_RETURN_URL=http://localhost:5173/settings

# Google OAuth (Gmail)
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/gmail/callback

# Microsoft OAuth (Outlook)
MICROSOFT_CLIENT_ID=your_microsoft_client_id
MICROSOFT_CLIENT_SECRET=your_microsoft_client_secret
MICROSOFT_TENANT_ID=common
MICROSOFT_REDIRECT_URI=http://localhost:8000/api/outlook/callback

# Security
ENCRYPTION_KEY=your_32_byte_encryption_key

# Frontend
FRONTEND_URL=http://localhost:5173
```

### 3. Initialize Database

```bash
python -c "from app.db.session import init_db; init_db()"
```

### 4. Run Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

API will be available at `http://localhost:8000`

Interactive docs at `http://localhost:8000/docs`

## API Endpoints

### Public Endpoints (No Auth Required)

- `POST /api/summarize/raw` - Summarize raw email text (FREE)
- `GET /api/billing/pricing` - Get pricing information

### Authenticated Endpoints

- `GET /api/auth/me` - Get current user
- `GET /api/auth/verify` - Verify JWT token

### PRO Endpoints (Require PRO Plan)

**Gmail**
- `GET /api/gmail/auth` - Get OAuth URL
- `POST /api/gmail/callback` - Handle OAuth callback
- `POST /api/gmail/list` - List Gmail messages
- `GET /api/gmail/message/{id}` - Get single message
- `GET /api/gmail/status` - Check connection status
- `DELETE /api/gmail/disconnect` - Disconnect Gmail

**Outlook**
- `GET /api/outlook/auth` - Get OAuth URL
- `POST /api/outlook/callback` - Handle OAuth callback
- `POST /api/outlook/list` - List Outlook messages
- `GET /api/outlook/message/{id}` - Get single message
- `GET /api/outlook/status` - Check connection status
- `DELETE /api/outlook/disconnect` - Disconnect Outlook

**IMAP**
- `POST /api/imap/connect` - Connect IMAP account
- `POST /api/imap/list` - List IMAP messages
- `GET /api/imap/folders` - Get folder list
- `GET /api/imap/status` - Check connection status
- `DELETE /api/imap/disconnect` - Disconnect IMAP

**History**
- `GET /api/history/summaries` - Get summary history
- `GET /api/history/summary/{id}` - Get single summary
- `DELETE /api/history/summary/{id}` - Delete summary
- `GET /api/history/stats` - Get statistics
- `DELETE /api/history/clear` - Clear all history

**Billing**
- `POST /api/billing/create-checkout-session` - Create Stripe checkout
- `POST /api/billing/portal` - Get customer portal URL
- `GET /api/billing/subscription` - Get subscription details
- `POST /api/billing/cancel` - Cancel subscription
- `POST /api/billing/webhook` - Stripe webhook handler

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI app entry point
│   ├── api/                 # API route handlers
│   │   ├── auth.py          # Authentication & authorization
│   │   ├── summarize.py     # Email summarization
│   │   ├── gmail.py         # Gmail integration
│   │   ├── outlook.py       # Outlook integration
│   │   ├── imap.py          # IMAP integration
│   │   ├── billing.py       # Stripe billing
│   │   └── history.py       # Summary history
│   ├── services/            # Business logic
│   │   ├── ai.py            # AI/Claude integration
│   │   ├── parser.py        # Email parsing engine
│   │   ├── gmail_service.py # Gmail API service
│   │   ├── outlook_service.py # Outlook API service
│   │   ├── imap_service.py  # IMAP service
│   │   └── billing_service.py # Stripe service
│   ├── db/                  # Database
│   │   ├── models.py        # SQLAlchemy models
│   │   └── session.py       # Database session
│   └── utils/               # Utilities
│       ├── email_cleaner.py # Email text cleaning
│       ├── html_to_text.py  # HTML conversion
│       └── validators.py    # Input validation
└── requirements.txt
```

## Deployment

### Render

Use `render.yaml` in infrastructure directory.

### Docker

```bash
docker build -t email-ai-backend .
docker run -p 8000:8000 --env-file .env email-ai-backend
```

## Security

- JWT validation via Clerk
- Encrypted credential storage
- SQL injection protection (SQLAlchemy)
- CORS configuration
- Input sanitization
- Stripe webhook signature verification

## License

MIT
