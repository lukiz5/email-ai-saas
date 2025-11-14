# Email AI SaaS

A full-stack SaaS platform for AI-powered email summarization with smart integrations and billing.

Built with **Claude Sonnet 4.5** for intelligent email analysis, summaries, and insights.

## Features

### FREE Plan
- ✅ Manual email input (paste text)
- ✅ AI-powered summaries
- ✅ Action item extraction
- ✅ Priority scoring (1-5 scale)
- ✅ Browser-only storage
- ✅ No login required

### PRO Plan ($9.99/month)
- 🚀 Everything in FREE
- 🚀 Gmail integration (OAuth)
- 🚀 Outlook/Microsoft 365 integration
- 🚀 IMAP support (any email provider)
- 🚀 Smart AI reply generation
- 🚀 Cloud history sync
- 🚀 Unlimited usage
- 🚀 Priority support

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Claude Sonnet 4.5** - AI summarization engine
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM
- **Clerk** - Authentication
- **Stripe** - Billing & subscriptions

### Frontend
- **React** - UI library
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **React Router** - Navigation
- **Axios** - API client

### Integrations
- **Gmail API** - Gmail integration
- **Microsoft Graph** - Outlook integration
- **IMAP** - Universal email access
- **Stripe** - Payment processing

## Project Structure

```
email-ai-saas/
├── backend/               # FastAPI backend
│   ├── app/
│   │   ├── api/          # API endpoints
│   │   ├── services/     # Business logic
│   │   ├── db/           # Database models
│   │   └── utils/        # Utilities
│   └── requirements.txt
│
├── frontend/             # React frontend
│   ├── src/
│   │   ├── components/   # Reusable components
│   │   ├── pages/        # Page components
│   │   └── lib/          # API & utilities
│   └── package.json
│
├── infrastructure/       # Deployment configs
│   ├── docker-compose.yml
│   ├── render.yaml
│   └── vercel.json
│
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL
- Anthropic API key
- Clerk account
- Stripe account

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/email-ai-saas.git
cd email-ai-saas
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Initialize database
python -c "from app.db.session import init_db; init_db()"

# Run server
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env
# Edit .env with your credentials

# Run development server
npm run dev
```

Frontend will be available at `http://localhost:5173`

## Environment Variables

### Backend (.env)

```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/email_ai_saas

# AI
ANTHROPIC_API_KEY=your_anthropic_key

# Auth
CLERK_PEM_PUBLIC_KEY=your_clerk_public_key

# Stripe
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PRICE_ID_PRO=price_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OAuth (Gmail)
GOOGLE_CLIENT_ID=your_client_id
GOOGLE_CLIENT_SECRET=your_client_secret

# OAuth (Outlook)
MICROSOFT_CLIENT_ID=your_client_id
MICROSOFT_CLIENT_SECRET=your_client_secret

# Security
ENCRYPTION_KEY=your_32_byte_key
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=pk_test_...
```

## Docker Deployment

```bash
# Build and run with Docker Compose
cd infrastructure
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Production Deployment

### Backend (Render)

1. Push code to GitHub
2. Connect repository to Render
3. Use `infrastructure/render.yaml` for configuration
4. Set environment variables in Render dashboard
5. Deploy

### Frontend (Vercel)

1. Push code to GitHub
2. Import project to Vercel
3. Set build settings:
   - Framework: Vite
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `dist`
4. Set environment variables
5. Deploy

## API Documentation

Once the backend is running, visit:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Features in Detail

### Email Parsing Engine
Advanced email parser that:
- Detects email boundaries
- Extracts headers (From, Subject, Date)
- Cleans HTML content
- Removes signatures
- Handles forwarded messages
- Supports email threads

### AI Capabilities (Claude Sonnet 4.5)
- **Summarization**: Concise 2-3 sentence summaries
- **Action Extraction**: Identifies tasks and to-dos
- **Priority Scoring**: 1-5 urgency scale
- **Key Points**: Bullet-point highlights
- **Smart Replies**: Context-aware response generation

### Security
- 🔒 JWT authentication via Clerk
- 🔒 Encrypted credential storage
- 🔒 SQL injection protection
- 🔒 CORS configuration
- 🔒 Input sanitization
- 🔒 Stripe webhook signature verification

## Development

### Backend Tests
```bash
cd backend
pytest
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Code Quality
```bash
# Backend
black app/
flake8 app/

# Frontend
npm run lint
```

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Email scheduling
- [ ] Custom AI prompts
- [ ] Team collaboration
- [ ] Advanced analytics
- [ ] Multi-language support
- [ ] Slack integration
- [ ] API access for developers

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

- 📧 Email: support@email-ai-saas.com
- 💬 Discord: [Join our community](https://discord.gg/email-ai-saas)
- 📝 Documentation: [docs.email-ai-saas.com](https://docs.email-ai-saas.com)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/email-ai-saas/issues)

## Acknowledgments

- [Anthropic](https://www.anthropic.com/) - Claude AI
- [Clerk](https://clerk.com/) - Authentication
- [Stripe](https://stripe.com/) - Payment processing
- [FastAPI](https://fastapi.tiangolo.com/) - Backend framework
- [React](https://react.dev/) - Frontend library

---

**Built with ❤️ using Claude Sonnet 4.5**

*Transform your inbox with AI-powered intelligence*