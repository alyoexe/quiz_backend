# PostgreSQL Setup for Quiz Backend

## Installation Steps (Windows)

### 1. Download PostgreSQL
- Download from: https://www.postgresql.org/download/windows/
- Version: 12+ recommended
- Use default installer

### 2. Install PostgreSQL
- Run installer
- Password for `postgres` user: **remember this!**
- Port: 5432 (default)
- Locale: English (default)
- Complete the installation

### 3. Open PostgreSQL Command Prompt

Windows → Search "SQL Shell (psql)" → Open

Or use the terminal:
```bash
\# Navigate to PostgreSQL bin directory
cd "C:\Program Files\PostgreSQL\16\bin"

# Connect to PostgreSQL
psql -U postgres
```

### 4. Create Database and User

```sql
-- Create database
CREATE DATABASE quiz_backend;

-- Create user
CREATE USER quiz_user WITH PASSWORD 'your_secure_password';

-- Grant privileges
ALTER ROLE quiz_user SET client_encoding TO 'utf8';
ALTER ROLE quiz_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE quiz_user SET default_transaction_deferrable TO on;
GRANT ALL PRIVILEGES ON DATABASE quiz_backend TO quiz_user;

-- Exit
\q
```

### 5. Update Your .env File

```env
DB_ENGINE=django.db.backends.postgresql
DB_NAME=quiz_backend
DB_USER=quiz_user
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432
```

### 6. Run Django Migrations

```bash
cd C:\Users\lenovo\Desktop\quiz_backend

# Activate virtual environment
venv\Scripts\activate

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

**Output:**
```
Operations to perform:
  Apply all migrations: account, admin, auth, authtoken, contenttypes, core, sessions, sites, socialaccount
Running migrations:
  Applying... ✓
  Applying... ✓
```

### 7. Start Django Server

```bash
python manage.py runserver
```

Server should now connect to PostgreSQL! ✅

---

## Verify Connection

### Option A: Django Shell
```bash
python manage.py shell
>>> from django.db import connection
>>> connection.ensure_connection()
>>> print("Database connection successful!")
```

### Option B: Check Tables
```sql
psql -U quiz_user -d quiz_backend -h localhost

-- List tables
\dt

-- Exit
\q
```

### Option C: pgAdmin GUI
1. Download pgAdmin: https://www.pgadmin.org/download/
2. Open pgAdmin
3. Right-click "Servers" → Register → Server
4. Name: `LocalQuizDB`
5. Host: `localhost`
6. Username: `quiz_user`
7. Password: Your password
8. Save and connect

---

## Common Issues & Solutions

### "FATAL: role "postgres" does not exist"
**Solution:**
- Reinstall PostgreSQL
- Make sure to set password during installation

### "psycopg2.OperationalError: could not translate host name"
**Solution:**
- Check DB_HOST is correct (should be `localhost`)
- Verify PostgreSQL service is running:
  ```bash
  # Windows Services
  Services → PostgreSQL Server → Status should be "Running"
  
  # Or restart:
  net stop postgresql-x64-16
  net start postgresql-x64-16
  ```

### "permission denied for schema public"
**Solution:**
- Grant permissions properly (see step 4 above)
- Or:
  ```sql
  GRANT ALL ON SCHEMA public TO quiz_user;
  ```

### "Database quiz_backend does not exist"
**Solution:**
```sql
psql -U postgres

CREATE DATABASE quiz_backend;
GRANT ALL PRIVILEGES ON DATABASE quiz_backend TO quiz_user;
\q
```

---

## Backup & Restore

### Backup Database
```bash
pg_dump -U quiz_user -d quiz_backend -h localhost > backup.sql
```

### Restore Database
```bash
psql -U postgres < backup.sql
```

---

## Performance Optimization (Optional)

### postgresql.conf Settings
For development:
```
shared_buffers = 128MB
effective_cache_size = 1GB
maintenance_work_mem = 32MB
work_mem = 8MB
```

Location: `C:\Program Files\PostgreSQL\16\data\postgresql.conf`

After editing, restart PostgreSQL service.

---

## What Changed in Django

Before (SQLite):
```
DB_ENGINE=django.db.backends.sqlite3
DB_NAME=db.sqlite3
```

Now (PostgreSQL):
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=quiz_backend
DB_USER=quiz_user
DB_PASSWORD=password
DB_HOST=localhost
DB_PORT=5432
```

---

## Running Migrations

**First time setup:**
```bash
python manage.py migrate
```

**After new migrations:**
```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Next Steps

1. ✅ Install PostgreSQL
2. ✅ Create database and user
3. ✅ Update .env file
4. ✅ Run migrations
5. ✅ Start Django server
6. Test the API endpoints
7. Deploy to production!

---

**Your project is now using PostgreSQL!** 🎉

For production deployment, use a managed database service:
- AWS RDS PostgreSQL
- DigitalOcean Managed Database
- Azure Database for PostgreSQL
- Heroku PostgreSQL

These handle backups, scaling, and security for you.
