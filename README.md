# Running the Project with Docker

## Prerequisites

Before running the project, make sure the following software is installed:

- Docker
- Docker Compose

Verify the installation:

```bash
docker --version
docker compose version
```

---

## Clone the Repository

```bash
git clone https://github.com/sageethhimachala/train-seat-booking.git

cd train-seat-booking
```

---

## Start the Application

Build the Docker images (if necessary) and start all services:

```bash
docker compose \
  --env-file .env.docker \
  up -d --build
```

This command will:

- Build the backend image
- Build the frontend image
- Start PostgreSQL
- Run Alembic database migrations automatically
- Start the FastAPI backend
- Start the React frontend

---

## Verify Containers

```bash
docker compose \
  --env-file .env.docker \
  ps
```

Expected services:

- database
- backend
- frontend

All services should eventually report a healthy status.

---

## Open the Application

Frontend

```
http://localhost
```

Backend API

```
http://localhost:8000
```

Swagger UI

```
http://localhost:8000/docs
```

Health Check

```
http://localhost/health
```

---

## View Logs

All services

```bash
docker compose \
  --env-file .env.docker \
  logs -f
```

Backend only

```bash
docker compose \
  --env-file .env.docker \
  logs -f backend
```

Frontend only

```bash
docker compose \
  --env-file .env.docker \
  logs -f frontend
```

Database only

```bash
docker compose \
  --env-file .env.docker \
  logs -f database
```

Stop viewing logs with:

```
Ctrl + C
```

---

## Restart the Project

If the project has already been built previously:

```bash
docker compose \
  --env-file .env.docker \
  up -d
```

If Docker images need rebuilding after code changes:

```bash
docker compose \
  --env-file .env.docker \
  up -d --build
```

---

## Stop the Containers

```bash
docker compose \
  --env-file .env.docker \
  stop
```

---

## Stop and Remove Containers

```bash
docker compose \
  --env-file .env.docker \
  down
```

This removes the containers but keeps the PostgreSQL data volume.

---

## Remove Everything (Including Database Data)

```bash
docker compose \
  --env-file .env.docker \
  down -v
```

This command removes:

- Containers
- Network
- PostgreSQL data volume

Use it only if you want a completely fresh database.

---

## Rebuild Images

If Dockerfiles or dependencies have changed:

```bash
docker compose \
  --env-file .env.docker \
  build --no-cache

docker compose \
  --env-file .env.docker \
  up -d
```

---

## Docker Images

To list locally built images:

```bash
docker images
```

Project images:

```bash
docker images | grep train-seat-booking
```

## 🚀 Live Demo

The application is deployed on AWS using Docker, Amazon EC2, Amazon RDS, and an Application Load Balancer.

**Live Application:**

http://train-booking-alb-93566483.ap-southeast-2.elb.amazonaws.com/

## ERD

![Database](assets/train-seat-booking-erd.svg)

## 🧪 Running Tests

### Backend Tests

Make sure PostgreSQL is running:

```bash
sudo systemctl start postgresql
```

Create a separate test database if it does not already exist:

```sql
CREATE DATABASE train_booking_test;
```

Set the test database URL:

```bash
export TEST_DATABASE_URL="postgresql+psycopg2://postgres:YOUR_PASSWORD@localhost:5432/train_booking_test"
```

Navigate to the backend and activate the virtual environment:

```bash
cd backend
source venv/bin/activate
```

Run all backend tests:

```bash
pytest
```

---

### Frontend Tests

Navigate to the frontend:

```bash
cd frontend
```

Install dependencies if they have not already been installed:

```bash
npm install
```

Run all frontend tests:

```bash
npm test
```

Run tests in watch mode during development:

```bash
npm run test:watch
```
