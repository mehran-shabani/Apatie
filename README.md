# Apatye Backend (آپاتیه) - City of Abadeh

Backend API for Apatye platform - A modular monolith built with Django 5, DRF, PostgreSQL, Redis, and Celery.

## 🏗️ Architecture

- **Framework**: Django 5 + Django REST Framework
- **Database**: PostgreSQL 16
- **Cache/Message Broker**: Redis 7
- **Task Queue**: Celery + Celery Beat
- **Containerization**: Docker + Docker Compose
- **API Documentation**: OpenAPI 3 (drf-spectacular)

## 📦 MVP Modules

1. **Doctor Appointments** (`apps.appointments`) - Appointment scheduling system
2. **Motorcycle Delivery** (`apps.delivery`) - Delivery service management

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Make (optional, but recommended)

### Setup & Run

1. **Clone the repository**
```bash
git clone <repository-url>
cd apatye_backend
```

2. **Create environment file**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Build and start services**
```bash
make build
make up
```

4. **Run migrations**
```bash
make migrate
```

5. **Create superuser**
```bash
make createsuperuser
```

6. **Access the application**
- API: http://localhost:8000/
- Health Check: http://localhost:8000/health/
- API Documentation (Swagger): http://localhost:8000/api/docs/
- API Documentation (ReDoc): http://localhost:8000/api/redoc/
- Admin Panel: http://localhost:8000/admin/

## 🔧 Environment Variables

Key environment variables (see `.env.example` for full list):

```env
DJANGO_SETTINGS_MODULE=config.settings.dev
SECRET_KEY=your-secret-key
DATABASE_URL=postgres://apatye:apatye@db:5432/apatye
REDIS_URL=redis://redis:6379/0
CITY_NAME=Abadeh
KAVENEGAR_API_KEY=your-kavenegar-api-key
SMS_ENABLED=False
```

## 📖 Makefile Commands

```bash
make help              # Show all available commands
make up                # Start all services
make down              # Stop all services
make restart           # Restart all services
make logs              # Show logs
make migrate           # Run migrations
make makemigrations    # Create new migrations
make shell             # Open Django shell
make test              # Run tests
make test-cov          # Run tests with coverage
make lint              # Run linting
make fmt               # Format code
make clean             # Clean up containers and volumes
```

## 🏗️ Project Structure

```
apatye_backend/
├── apps/                       # Django applications
│   ├── common/                # Shared utilities and base classes
│   ├── users/                 # User management & authentication
│   ├── vendors/               # Service providers
│   ├── services/              # Available services
│   ├── appointments/          # Doctor appointment scheduling
│   ├── delivery/              # Motorcycle delivery service
│   ├── notifications/         # SMS & push notifications
│   └── billing/               # Business plan boost subscriptions
├── config/                    # Django configuration
│   ├── settings/             # Settings (base, dev, prod)
│   ├── urls.py               # URL configuration
│   ├── wsgi.py               # WSGI application
│   ├── asgi.py               # ASGI application
│   └── celery.py             # Celery configuration
├── requirements/              # Python dependencies
│   ├── base.txt              # Base requirements
│   ├── dev.txt               # Development requirements
│   └── prod.txt              # Production requirements
├── docker-compose.yml         # Docker Compose configuration
├── Dockerfile                 # Docker image definition
├── Makefile                   # Development commands
├── manage.py                  # Django management script
├── .env.example              # Example environment variables
└── README.md                  # This file
```

## 🌍 Localization

- **Language**: Persian (fa-IR)
- **Timezone**: Asia/Tehran
- **City**: Abadeh

## 🔐 Authentication

Mobile-based authentication using OTP (One-Time Password):
- SMS integration with Kavenegar
- Development mode: OTP codes logged to console
- Production mode: OTP codes sent via SMS

## 🧪 Testing

Run tests with pytest:

```bash
# Run all tests
make test

# Run tests with coverage
make test-cov
```

Target: ≥ 80% coverage on critical paths

## 📝 API Documentation

Interactive API documentation is available at:
- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **OpenAPI Schema**: http://localhost:8000/api/schema/

## 💰 Business Model

- **Revenue Model**: Business Plan Boost subscriptions only
- **No transaction commissions**

## 🛠️ Development

### Code Quality

```bash
# Format code
make fmt

# Run linters
make lint
```

### Database

```bash
# Create migrations
make makemigrations

# Apply migrations
make migrate

# Open database shell
make dbshell
```

### Celery

```bash
# Check Celery status
make celery-status

# Start Flower (Celery monitoring)
make flower
```

## 📚 Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution guidelines.

## 🔒 Security

- HTTPS enforced in production
- CORS configured for specific origins
- Rate limiting enabled
- Secure cookie settings in production

## 📄 License

[Your License Here]

## 📧 Contact

[Your Contact Information]
