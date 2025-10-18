# Social Media App

A production-ready social media backend API built with FastAPI and PostgreSQL, featuring comprehensive monitoring and observability.

## ✨ Features

- 🔐 **JWT Authentication** - Secure user authentication and authorization
- 👤 **User Management** - Registration, profiles, and account management
- 📝 **Posts, Comments, Likes, and Follow System**
- 📊 **Monitoring** - Prometheus metrics and Grafana dashboards
- 🐳 **Docker Ready** - Complete containerized setup
- 🚀 **Production Ready** - Nginx reverse proxy, health checks, and auto-migrations

## 🛠️ Tech Stack

- **Backend**: FastAPI 0.118.3, Python 3.12
- **Database**: PostgreSQL 16+ with AsyncPG
- **ORM**: SQLAlchemy 2.0 (Async)
- **Migrations**: Alembic
- **Auth**: JWT Token
- **Monitoring**: Prometheus + Grafana
- **Proxy**: Nginx
- **Containerization**: Docker & Docker Compose

## 🚀 Quick Start (Docker - Recommended)

### 1. Clone and Setup

```bash
git clone https://github.com/AhmedNabil03/social-media-app.git
cd social-media-app

# Setup environment files
cd docker/env
cp .app.env.example .app.env
cp .postgres.env.example .postgres.env
cp .grafana.env.example .grafana.env
cp .postgres-exporter.env.example .postgres-exporter.env

# Edit .env files with your credentials
```

### 2. Start Services

```bash
cd docker
docker compose up -d --build
```

### 3. Access the Application

- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Nginx**: http://localhost
- **Grafana**: http://localhost:3000 (admin/admin)
- **Prometheus**: http://localhost:9090

## 📋 Manual Setup (Development)

### Prerequisites

- Python 3.12+
- PostgreSQL 16+
- pip or conda

### Installation

```bash
# Install system dependencies
sudo apt update
sudo apt install libpq-dev gcc python3-dev postgresql

# Create virtual environment
conda create -n social-media-app python=3.12
conda activate social-media-app

# Or use venv
python3.12 -m venv venv
source venv/bin/activate

# Install Python packages
cd src
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your database credentials

# Create database
sudo -u postgres psql -c "CREATE DATABASE socialmedia;"

cd models/db_schemas
cp alembic.ini.example alembic.ini
# Edit alembic.ini and update the sqlalchemy.url with your database URL
alembic upgrade head

# Start the server
cd ../..
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit http://localhost:8000/docs for interactive API documentation.

### Key Endpoints

| Category     | Method | Endpoint                                   | Description                      |
| ------------ | ------ | ------------------------------------------ | -------------------------------- |
| **Auth**     | POST   | `/api/v1/users/signup`                     | Register new user                |
|              | POST   | `/api/v1/users/login`                      | Login and get JWT token          |
|              | POST   | `/api/v1/users/logout`                     | Logout and invalidate token      |
| **Users**    | GET    | `/api/v1/users/profile`                    | Get current user profile         |
|              | PATCH  | `/api/v1/users/profile`                    | Update profile                   |
|              | PATCH  | `/api/v1/users/password`                   | Update password                  |
|              | GET    | `/api/v1/users/{username}`                 | Get public user profile          |
|              | DELETE | `/api/v1/users/`                           | Delete own account               |
| **Posts**    | POST   | `/api/v1/posts`                            | Create new post                  |
|              | GET    | `/api/v1/posts/`                           | Get own posts                    |
|              | GET    | `/api/v1/posts/{post_id}`                  | Get specific post                |
|              | GET    | `/api/v1/posts/user/{user_id}`             | Get user's posts                 |
|              | GET    | `/api/v1/posts/feed/all`                   | Get feed posts                   |
|              | PATCH  | `/api/v1/posts/{post_id}`                  | Update post                      |
|              | DELETE | `/api/v1/posts/{post_id}`                  | Delete post                      |
| **Comments** | POST   | `/api/v1/comments`                         | Create comment (or reply)        |
|              | GET    | `/api/v1/comments/post/{post_id}`          | Get post comments                |
|              | GET    | `/api/v1/comments/{comment_id}/replies`    | Get comment replies              |
|              | PATCH  | `/api/v1/comments/{comment_id}`            | Update comment                   |
|              | DELETE | `/api/v1/comments/{comment_id}`            | Delete comment                   |
| **Likes**    | POST   | `/api/v1/likes/{post_id}`                  | Like a post                      |
|              | DELETE | `/api/v1/likes/{post_id}`                  | Unlike a post                    |
|              | GET    | `/api/v1/likes/{post_id}/check`            | Check if user liked post         |
|              | GET    | `/api/v1/likes/{post_id}/count`            | Get post likes count             |
| **Follow**   | POST   | `/api/v1/follows/{following_id}`           | Follow user                      |
|              | DELETE | `/api/v1/follows/{following_id}`           | Unfollow user                    |
|              | GET    | `/api/v1/follows/{user_id}/check`          | Check if following user          |
|              | GET    | `/api/v1/follows/stats/{user_id}`          | Get followers & following counts |
|              | GET    | `/api/v1/follows/user/{user_id}/followers` | Get followers count              |
|              | GET    | `/api/v1/follows/user/{user_id}/following` | Get following count              |


## 📊 Monitoring & Metrics

The application includes comprehensive monitoring with Prometheus and Grafana.

### Available Metrics

- **HTTP Metrics**: Request rate, latency, error rate
- **System Metrics**: CPU, memory, disk, network
- **Database Metrics**: Connections, queries, performance

### Pre-configured Dashboards

- FastAPI Observability (request metrics, latency, errors)
- PostgreSQL Exporter (database performance)
- Node Exporter (system resources)

Access Grafana at http://localhost:3000 to view all metrics.

## 🐳 Docker Services

| Service           | Port | Description        |
| ----------------- | ---- | ------------------ |
| FastAPI           | 8000 | Main application   |
| Nginx             | 80   | Reverse proxy      |
| PostgreSQL        | 5432 | Database           |
| Prometheus        | 9090 | Metrics collection |
| Grafana           | 3000 | Dashboards         |
| Node Exporter     | 9100 | System metrics     |
| Postgres Exporter | 9187 | DB metrics         |

See [docker/README.md](docker/README.md) for detailed Docker setup and troubleshooting.

## 🔧 Development

### Project Structure

```
social-media-app/
├── docker/              # Docker configuration
│   ├── fastapi-app/    # FastAPI Dockerfile
│   ├── nginx/          # Nginx config
│   ├── prometheus/     # Prometheus config
│   ├── grafana/        # Grafana dashboards
│   └── env/            # Environment files
├── models/             # Database models
├── routes/             # API routes
├── helpers/            # Utility functions
├── utils/              # Metrics utilities
├── main.py             # Application entry
└── requirements.txt    # Python dependencies
```

### Database Migrations

```bash
# Create new migration
cd src/models/db_schemas
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1

# View history
alembic history
```

## 🔒 Security

- ✅ JWT token authentication
- ✅ Input validation with Pydantic
- ✅ SQL injection prevention (SQLAlchemy ORM)
- ✅ CORS configuration
- ✅ Environment-based secrets
- ⚠️ **Note**: Passwords should be hashed with bcrypt before production use.

## 🚀 Deployment

### Production Checklist

- [ ] Update all `.env` files with strong passwords
- [ ] Use secrets management (not `.env` files)
- [ ] Enable HTTPS with SSL certificates
- [ ] Set up database backups
- [ ] Monitor disk space for metrics and logs

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the Apache-2.0 License - see the LICENSE file for details.
