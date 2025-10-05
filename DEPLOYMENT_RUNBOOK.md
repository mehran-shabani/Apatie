# Apatye Backend - Deployment Runbook

## 🚀 Quick Start Guide

This runbook provides step-by-step instructions to deploy and verify the Apatye backend.

## Prerequisites

- Docker Engine 20.10+
- Docker Compose 2.0+ (or `docker compose` plugin)
- Git
- 4GB RAM minimum
- 10GB disk space

## Step 1: Clone Repository

```bash
git clone <repository-url>
cd apatye_backend
```

## Step 2: Environment Configuration

```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
nano .env  # or vim, code, etc.
```

Required variables:
- `SECRET_KEY`: Generate a secure random key
- `DATABASE_URL`: Default is fine for development
- `REDIS_URL`: Default is fine for development
- `KAVENEGAR_API_KEY`: Add your SMS provider API key
- `CITY_NAME`: Default is "Abadeh"

## Step 3: Build Docker Images

```bash
make build
```

This will:
- Pull base images (Python 3.11, PostgreSQL 16, Redis 7)
- Install all dependencies
- Build the application image

Expected time: 2-5 minutes (depending on internet speed)

## Step 4: Start Services

```bash
make up
```

This starts 5 services:
1. **db** (PostgreSQL) - Port 5432
2. **redis** (Redis) - Port 6379
3. **web** (Django) - Port 8000
4. **celery** (Celery Worker)
5. **celery_beat** (Celery Scheduler)

Wait for health checks to pass (10-30 seconds).

## Step 5: Run Database Migrations

```bash
make migrate
```

This will:
- Create database tables
- Set up initial schema
- Apply all migrations

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions, users, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

## Step 6: Create Superuser (Optional but Recommended)

```bash
make createsuperuser
```

You'll be prompted for:
- Mobile number (e.g., 09123456789)
- Password
- Password confirmation

## Step 7: Verify Deployment

### 7.1 Check Service Status

```bash
docker compose ps
```

All services should show "Up" status.

### 7.2 Test Health Check Endpoint

```bash
curl http://localhost:8000/health/
```

Expected response (HTTP 200):
```json
{
  "status": "healthy",
  "city": "Abadeh",
  "timezone": "Asia/Tehran",
  "language": "fa-ir",
  "database": "connected",
  "redis": "connected"
}
```

### 7.3 Access Swagger Documentation

Open browser: http://localhost:8000/api/docs/

You should see:
- Interactive API documentation
- "Apatye API - آپاتیه" title
- List of available endpoints
- Try-it-out functionality

### 7.4 Access ReDoc Documentation

Open browser: http://localhost:8000/api/redoc/

### 7.5 Access Admin Panel

Open browser: http://localhost:8000/admin/

Login with superuser credentials created in Step 6.

## Step 8: View Logs (If Issues)

```bash
# All services
make logs

# Specific service
docker compose logs web
docker compose logs db
docker compose logs celery
```

## Common Issues & Solutions

### Issue 1: Port Already in Use

**Symptoms**: Error about port 8000, 5432, or 6379 already in use

**Solution**:
```bash
# Find process using port
lsof -i :8000  # or :5432, :6379

# Kill process or change port in docker-compose.yml
```

### Issue 2: Database Connection Error

**Symptoms**: "could not connect to server"

**Solution**:
```bash
# Ensure database is healthy
docker compose ps db

# Check database logs
docker compose logs db

# Restart services
make restart
```

### Issue 3: Permission Denied

**Symptoms**: Permission errors when running commands

**Solution**:
```bash
# Fix permissions
chmod +x manage.py
sudo chown -R $USER:$USER .
```

### Issue 4: Redis Connection Error

**Symptoms**: Health check shows Redis error

**Solution**:
```bash
# Check Redis status
docker compose logs redis

# Test Redis connection
docker compose exec redis redis-cli ping
# Should return: PONG
```

## Verification Checklist

- [ ] All 5 services running (`docker compose ps`)
- [ ] Health check returns 200 (`curl http://localhost:8000/health/`)
- [ ] Swagger docs accessible (http://localhost:8000/api/docs/)
- [ ] Admin panel accessible (http://localhost:8000/admin/)
- [ ] Database migrations applied (`make migrate`)
- [ ] Superuser created (optional)
- [ ] No errors in logs (`make logs`)

## Stopping Services

```bash
# Stop services (preserves data)
make down

# Stop and remove volumes (deletes data)
make clean
```

## Production Deployment Notes

For production deployment:

1. **Change settings module**:
   ```env
   DJANGO_SETTINGS_MODULE=config.settings.prod
   ```

2. **Set secure SECRET_KEY**:
   ```bash
   python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
   ```

3. **Configure proper database**:
   ```env
   DATABASE_URL=postgres://user:pass@host:5432/dbname
   ```

4. **Set ALLOWED_HOSTS**:
   ```env
   ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
   ```

5. **Enable SMS**:
   ```env
   SMS_ENABLED=True
   KAVENEGAR_API_KEY=your-real-api-key
   ```

6. **Configure CORS**:
   ```env
   CORS_ALLOWED_ORIGINS=https://yourdomain.com
   ```

7. **Use proper web server**:
   - Replace `runserver` with `gunicorn` in docker-compose.yml
   - Add nginx reverse proxy

8. **Enable HTTPS**:
   - Configure SSL certificates
   - Set `SECURE_SSL_REDIRECT=True`

9. **Configure monitoring**:
   - Set SENTRY_DSN for error tracking
   - Enable Flower for Celery monitoring

10. **Backup strategy**:
    - Regular PostgreSQL backups
    - Volume backups
    - Configuration backups

## Support

If you encounter issues:

1. Check logs: `make logs`
2. Review documentation: README.md
3. Check SETUP_VERIFICATION.md
4. Review CONTRIBUTING.md
5. Create issue with logs and error details

## Success!

If all verification steps pass, congratulations! 🎉

Your Apatye backend is now running and ready for development.

Next steps:
- Explore API documentation
- Review code structure
- Start implementing business logic
- Write tests
- Deploy to production

---

**Last Updated**: 2025-10-05
**Version**: 1.0.0
