# Kiosk Backend Server

A FastAPI-based backend server for kiosk management with MySQL database integration.

## 🚀 Features

- RESTful API endpoints for kiosk management
- MySQL database integration
- Docker containerization
- Authentication and authorization
- API documentation with Swagger UI
- Environment-based configuration
- Request validation and error handling

## 📋 Prerequisites

- Docker and Docker Compose
- Python 3.9+
- MySQL 8.0+

## 🛠️ Tech Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **MySQL**: Relational database
- **SQLAlchemy**: SQL toolkit and ORM
- **Pydantic**: Data validation using Python type annotations
- **uvicorn**: ASGI server implementation

## 🗂️ Project Structure

```
kiosk-backend/
├── src/              # Source code directory
│   ├── models/       # Database models
├── server.py         # Main FastAPI application server
├── urls.py           # Route definitions and endpoints
├── sonar-properties.py   # Sonar configuration
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
# Server Settings
DATABASEE_URL = <>

# graylogs
GRAYLOG_HOST = 192.168.1.211
GRAYLOG_PORT = 12201
APP_NAME = vending-machine
ENVIRONMENT = Development
```

## 🐳 Docker Setup

### Docker Compose Configuration

```yaml
version: "3.8"

services:
  api:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db
    volumes:
      - .:/app
    networks:
      - kiosk-network

  db:
    image: mysql:8.0
    ports:
      - "3306:3306"
    env_file:
      - .env
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - kiosk-network

volumes:
  mysql_data:

networks:
  kiosk-network:
    driver: bridge
```

### Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

## 🚀 Getting Started

1. **Clone the repository**

   ```bash
   git clone https://github.com/your-username/kiosk-backend.git
   cd kiosk-backend
   ```

2. **Set up environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`
API documentation at `http://localhost:8000/docs`

## 📦 Dependencies

Main dependencies (see requirements.txt for complete list):

```
fastapi==0.68.1
uvicorn==0.15.0
sqlalchemy==1.4.23
pymysql==1.0.2
pydantic==1.8.2
```

## 🔒 Security

- JWT-based authentication
- Password hashing using bcrypt
- CORS middleware
- Rate limiting
- Input validation

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 👥 Authors

- Prabhaakar Sundararaj - Initial work

## 🙏 Acknowledgments

- FastAPI documentation
- SQLAlchemy documentation
- Docker documentation
