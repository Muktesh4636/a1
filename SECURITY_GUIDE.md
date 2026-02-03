# 🔒 Security Hardening Guide

This document outlines all security measures implemented to protect your dice game platform from attacks.

## ✅ Security Features Implemented

### 1. **Production Settings**
- ✅ `DEBUG = False` by default (prevents exposing sensitive information)
- ✅ Restricted `ALLOWED_HOSTS` to specific domains only
- ✅ Strong password validation (minimum 8 characters, complexity checks)
- ✅ Secure session and CSRF cookie settings

### 2. **HTTPS/SSL Security**
- ✅ HSTS (HTTP Strict Transport Security) enabled
- ✅ Secure cookie flags (HttpOnly, Secure, SameSite)
- ✅ SSL redirect configuration ready
- ✅ Security headers configured

### 3. **Authentication & Authorization**
- ✅ JWT tokens with shorter lifetimes (1 hour access tokens)
- ✅ Token rotation and blacklisting enabled
- ✅ Strong password validators
- ✅ Admin permission system with granular controls

### 4. **API Security**
- ✅ Rate limiting (100/hour for anonymous, 1000/hour for authenticated)
- ✅ CSRF protection enabled
- ✅ CORS restricted to specific origins only
- ✅ API endpoints require authentication

### 5. **Database Security**
- ✅ PostgreSQL with connection pooling
- ✅ Database credentials via environment variables
- ✅ Connection timeouts configured

### 6. **Redis Security**
- ✅ Password authentication support
- ✅ Connection pooling with limits

## 🚨 Critical Security Checklist

### Before Going Live:

1. **Set Strong Secret Key**
   ```bash
   # Generate a secure secret key
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Add to `.env`:
   ```
   SECRET_KEY=your-generated-secret-key-here
   ```

2. **Enable HTTPS/SSL**
   - Install SSL certificate (Let's Encrypt recommended)
   - Set `SECURE_SSL_REDIRECT=True` in environment
   - Update `CSRF_TRUSTED_ORIGINS` to use `https://` only

3. **Set Strong Database Password**
   ```env
   DB_PASSWORD=your-strong-random-password-here
   ```

4. **Set Redis Password**
   ```env
   REDIS_PASSWORD=your-strong-redis-password-here
   ```

5. **Restrict ALLOWED_HOSTS**
   ```env
   ALLOWED_HOSTS=gunduata.online,www.gunduata.online
   ```

6. **Change Default Admin Password**
   - Use the admin management panel to change default passwords
   - Ensure all admin accounts use strong passwords

7. **Enable Firewall Rules**
   ```bash
   # Only allow necessary ports
   ufw allow 22/tcp    # SSH
   ufw allow 80/tcp    # HTTP
   ufw allow 443/tcp   # HTTPS
   ufw enable
   ```

8. **Regular Security Updates**
   ```bash
   # Update system packages regularly
   apt update && apt upgrade -y
   ```

## 🔐 Environment Variables Required

Create a `.env` file in your `backend/` directory with:

```env
# Django Settings
DEBUG=False
SECRET_KEY=your-very-long-random-secret-key-here
ALLOWED_HOSTS=gunduata.online,www.gunduata.online,72.61.254.71

# Database
USE_SQLITE=False
DB_NAME=dice_game
DB_USER=postgres
DB_PASSWORD=your-strong-database-password
DB_HOST=db
DB_PORT=5432

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=your-strong-redis-password

# SSL/HTTPS (when enabled)
SECURE_SSL_REDIRECT=True

# CORS
CORS_ALLOWED_ORIGINS=https://gunduata.online,https://www.gunduata.online
```

## 🛡️ Additional Security Recommendations

### Server-Level Security

1. **Fail2Ban** - Install to prevent brute force attacks
   ```bash
   apt install fail2ban
   ```

2. **Regular Backups** - Set up automated database backups
   ```bash
   # Add to crontab
   0 2 * * * docker compose exec -T db pg_dump -U postgres dice_game > /backups/db_$(date +\%Y\%m\%d).sql
   ```

3. **Monitor Logs** - Set up log monitoring for suspicious activity
   ```bash
   docker compose logs -f web | grep -i "error\|unauthorized\|failed"
   ```

4. **Keep Dependencies Updated**
   ```bash
   pip list --outdated
   pip install --upgrade package-name
   ```

### Application-Level Security

1. **Input Validation** - All user inputs are validated
2. **SQL Injection Protection** - Django ORM prevents SQL injection
3. **XSS Protection** - Django templates auto-escape content
4. **CSRF Protection** - Enabled for all forms
5. **Session Security** - Secure, HttpOnly cookies

## 🚫 Security Best Practices

### DO:
- ✅ Use strong, unique passwords for all accounts
- ✅ Enable HTTPS before going live
- ✅ Keep all software updated
- ✅ Monitor logs regularly
- ✅ Use environment variables for secrets
- ✅ Restrict database access to application only
- ✅ Use rate limiting on APIs
- ✅ Implement proper error handling (don't expose stack traces)

### DON'T:
- ❌ Commit `.env` files to git
- ❌ Use default passwords
- ❌ Run with DEBUG=True in production
- ❌ Expose database ports publicly
- ❌ Use weak secret keys
- ❌ Allow CORS from all origins
- ❌ Store passwords in plain text
- ❌ Share admin credentials

## 📊 Security Monitoring

### Check Security Status:
```bash
# Check if DEBUG is disabled
docker compose exec web python manage.py shell -c "from django.conf import settings; print('DEBUG:', settings.DEBUG)"

# Check allowed hosts
docker compose exec web python manage.py shell -c "from django.conf import settings; print('ALLOWED_HOSTS:', settings.ALLOWED_HOSTS)"

# Check security headers
curl -I https://gunduata.online | grep -i "strict-transport\|x-frame\|x-content-type"
```

## 🔄 Regular Security Maintenance

1. **Weekly**: Review access logs for suspicious activity
2. **Monthly**: Update dependencies and system packages
3. **Quarterly**: Review and rotate secrets/keys
4. **Annually**: Security audit and penetration testing

## 📞 Security Incident Response

If you suspect a security breach:

1. **Immediately**: Change all admin passwords
2. **Rotate**: All secret keys and tokens
3. **Review**: Access logs for unauthorized access
4. **Update**: All dependencies to latest secure versions
5. **Notify**: Users if data may have been compromised

---

**Last Updated**: February 2026
**Security Level**: Production-Ready ✅
