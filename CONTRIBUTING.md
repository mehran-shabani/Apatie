# Contributing to Apatye Backend

Thank you for your interest in contributing to Apatye! This document provides guidelines and instructions for contributing.

## 🚀 Getting Started

1. Fork the repository
2. Clone your fork: `git clone <your-fork-url>`
3. Create a feature branch: `git checkout -b feature/your-feature-name`
4. Make your changes
5. Test your changes
6. Commit with clear messages
7. Push to your fork
8. Create a Pull Request

## 📋 Development Setup

Follow the [README.md](README.md) for initial setup instructions.

## 🎯 Code Style

### Python

We follow PEP 8 with some modifications:
- Line length: 100 characters
- Use Black for formatting
- Use isort for import sorting

```bash
# Format your code before committing
make fmt
```

### Django Best Practices

- Use class-based views where appropriate
- Keep views thin, models fat
- Use Django's built-in features
- Follow Django naming conventions
- Write descriptive docstrings

## 🧪 Testing

All new features and bug fixes must include tests:

```bash
# Run tests
make test

# Run tests with coverage
make test-cov
```

### Test Guidelines

- Aim for ≥ 80% coverage on critical paths
- Use pytest fixtures
- Test edge cases
- Use factory_boy for test data
- Mock external services

Example test structure:
```python
# apps/users/tests/test_models.py
import pytest
from apps.users.models import User

@pytest.mark.django_db
class TestUserModel:
    def test_create_user(self):
        user = User.objects.create_user(
            mobile='09123456789',
            password='test123'
        )
        assert user.mobile == '09123456789'
        assert user.is_active is True
```

## 📝 Commit Messages

Use conventional commit format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(appointments): add appointment cancellation endpoint

- Add cancel_appointment view
- Add cancellation reason field
- Update serializers and tests

Closes #123
```

## 🔍 Pull Request Process

1. **Update Documentation**: Update README.md if needed
2. **Add Tests**: Ensure tests pass and coverage is adequate
3. **Format Code**: Run `make fmt` and `make lint`
4. **Describe Changes**: Write clear PR description
5. **Link Issues**: Reference related issues
6. **Request Review**: Tag appropriate reviewers

### PR Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added
- [ ] Coverage maintained/improved

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-reviewed code
- [ ] Commented complex code
- [ ] Updated documentation
- [ ] No new warnings
```

## 🏗️ Architecture Guidelines

### Modular Monolith

- Keep apps loosely coupled
- Use events for cross-app communication
- Shared utilities in `apps.common`
- Each app should be potentially extractable

### Adding New Apps

1. Create app: `python manage.py startapp app_name apps/app_name`
2. Add to `INSTALLED_APPS` in `config/settings/base.py`
3. Create URL patterns and include in `config/urls.py`
4. Add models, views, serializers
5. Write tests
6. Update documentation

### API Design

- RESTful principles
- Consistent response format
- Proper HTTP status codes
- Pagination for lists
- Filtering and ordering
- OpenAPI documentation

Example response format:
```json
{
  "success": true,
  "data": { ... },
  "message": "Optional success message"
}
```

Error format:
```json
{
  "success": false,
  "error": {
    "message": "Error description",
    "status_code": 400,
    "details": { ... }
  }
}
```

## 🔐 Security

- Never commit secrets
- Use environment variables
- Validate all inputs
- Sanitize user data
- Use Django's security features
- Keep dependencies updated

## 🌍 Localization

- All user-facing strings must be translatable
- Use Django's translation utilities
- Support Persian (fa-IR) locale
- Handle RTL layouts
- Use Jalali dates where appropriate

Example:
```python
from django.utils.translation import gettext_lazy as _

class MyModel(models.Model):
    name = models.CharField(_('Name'), max_length=100)
```

## 📚 Documentation

- Docstrings for all public functions/classes
- Comments for complex logic
- Update API documentation
- Keep README.md current
- Add examples for new features

## 🐛 Bug Reports

Use GitHub Issues with:
- Clear title
- Steps to reproduce
- Expected behavior
- Actual behavior
- Environment details
- Screenshots if applicable

## 💡 Feature Requests

- Describe the problem
- Propose solution
- Consider alternatives
- Additional context

## 🤝 Code of Conduct

- Be respectful
- Be collaborative
- Be constructive
- Be professional

## 📞 Questions?

If you have questions, please:
1. Check existing documentation
2. Search existing issues
3. Ask in discussions
4. Contact maintainers

Thank you for contributing! 🎉
