# Security Policy

## Reporting Security Issues

If you discover a security vulnerability, please email the maintainers directly instead of opening a public issue.

## Security Measures

### 1. Environment Variables
- **Database Credentials**: Moved to environment variables (`.env` file)
  - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`
  - Never commit real passwords to git
  - Use strong passwords in production

### 2. Secret Management
- `SECRET_KEY`: Must be changed in production
- `KAVENEGAR_API_KEY`: Keep secure, never commit
- `SENTRY_DSN`: Optional, for production monitoring

### 3. Dependency Security

Current status and planned updates:

| Package | Current | Latest Stable | Security Status | Action |
|---------|---------|---------------|-----------------|--------|
| Django | 5.0.10 | 5.1.x | Monitor | Update after testing |
| djangorestframework | 3.15.2 | 3.15.2 | OK | ✅ |
| requests | 2.32.3 | 2.32.3 | OK | ✅ |
| celery | 5.4.0 | 5.5.x | Monitor | Update after testing |

**Action Items:**
- [ ] Test Django 5.1.x compatibility
- [ ] Test Celery 5.5.x compatibility
- [ ] Run full test suite before major version updates

### 4. Docker Security
- Use official base images (Python 3.11, PostgreSQL 16, Redis 7)
- Health checks configured for all services
- Non-root user in production containers (TODO)

### 5. Production Security Checklist

Before deploying to production:

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `POSTGRES_PASSWORD` to a strong password
- [ ] Set `DEBUG=False` in production
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Enable `SECURE_SSL_REDIRECT=True`
- [ ] Configure CORS with specific origins
- [ ] Enable Sentry monitoring (optional)
- [ ] Review and enable rate limiting on sensitive endpoints
- [ ] Run security audit: `pip install safety && safety check`

### 6. Rate Limiting

Rate limiting is configured but needs to be applied to sensitive endpoints:

**TODO:** Add `@ratelimit` decorator to:
- OTP generation endpoints
- Login endpoints
- Password reset endpoints
- Payment initiation endpoints

Example:
```python
from django_ratelimit.decorators import ratelimit

@ratelimit(key='ip', rate='5/h', method='POST')
def send_otp(request):
    # OTP logic here
    pass
```

### 7. Monitoring

- Sentry SDK installed for production error tracking
- Conditional initialization (only when `SENTRY_DSN` is set)
- Celery integration included

## Security Best Practices

1. **Never commit secrets**: Use `.env` files and `.gitignore`
2. **Use HTTPS in production**: All production traffic should be encrypted
3. **Keep dependencies updated**: Regularly check for security updates
4. **Validate all inputs**: Use Django's built-in validation and DRF serializers
5. **Use parameterized queries**: Django ORM does this by default
6. **Enable CSRF protection**: Enabled by default in Django
7. **Secure cookies**: Configured in production settings
8. **Regular backups**: Implement automated database backups

## GitGuardian Integration

GitGuardian is integrated to scan for hardcoded secrets. If it flags false positives:

1. Review the flagged secret
2. If it's a dev/test password, it's acceptable but should use environment variables
3. For production secrets, rotate immediately and use proper secret management

## Dependency Scanning

Run security scans regularly:

```bash
# Install safety
pip install safety

# Check for known vulnerabilities
safety check -r requirements/base.txt
safety check -r requirements/prod.txt

# Update pip-audit (alternative)
pip install pip-audit
pip-audit
```

## Last Security Review

**Date**: 2025-10-05  
**Reviewer**: Cursor Agent  
**Status**: ✅ Basic security measures implemented

---

**Note**: This is a living document. Update it as security measures evolve.
