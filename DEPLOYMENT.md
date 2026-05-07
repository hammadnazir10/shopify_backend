# Docker Deployment Guide for EC2

## Overview
This guide walks through deploying the FastAPI app to EC2 using Docker and Docker Hub.

## Prerequisites
- Docker installed locally
- Docker Hub account
- AWS EC2 instance running (Ubuntu or Amazon Linux)
- SSH access to EC2 instance

---

## Step 1: Build Docker Image Locally

```bash
cd d:\shopify
docker build -t <your-dockerhub-username>/shopify-backend:latest .
```

Replace `<your-dockerhub-username>` with your Docker Hub username.

---

## Step 2: Test Locally (Optional)

```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY="your-key-here" \
  <your-dockerhub-username>/shopify-backend:latest
```

Visit `http://localhost:8000/docs` to test the API.

---

## Step 3: Push to Docker Hub

Login to Docker Hub:
```bash
docker login
```

Push the image:
```bash
docker push <your-dockerhub-username>/shopify-backend:latest
```

---

## Step 4: EC2 Setup

### 4a. Connect to EC2 and Install Docker

SSH into your EC2 instance:
```bash
ssh -i <your-key.pem> ec2-user@<your-ec2-ip>
# or for Ubuntu
ssh -i <your-key.pem> ubuntu@<your-ec2-ip>
```

Install Docker:
```bash
# For Amazon Linux / Red Hat
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ec2-user

# For Ubuntu
sudo apt-get update -y
sudo apt-get install docker.io -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu
```

Re-login or run:
```bash
newgrp docker
```

### 4b. Pull and Run the Container

```bash
docker pull <your-dockerhub-username>/shopify-backend:latest

docker run -d \
  --name shopify-api \
  -p 8000:8000 \
  -e OPENAI_API_KEY="your-production-key" \
  -e MODEL_NAME="gpt-4o" \
  <your-dockerhub-username>/shopify-backend:latest
```

**Flags:**
- `-d`: Run in detached mode (background)
- `--name shopify-api`: Container name for easy reference
- `-p 8000:8000`: Map port 8000 from container to host
- `-e KEY=VALUE`: Set environment variables

### 4c. Verify it's Running

```bash
# Check container status
docker ps

# View logs
docker logs shopify-api

# Test the API (from EC2)
curl http://localhost:8000/

# Test from your machine
curl http://<your-ec2-ip>:8000/
```

---

## Step 5: Production Setup (Recommended)

### Using Docker Compose

Create `docker-compose.yml` on your EC2 instance:

```yaml
version: '3.8'

services:
  shopify-api:
    image: <your-dockerhub-username>/shopify-backend:latest
    container_name: shopify-api
    ports:
      - "8000:8000"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - MODEL_NAME=gpt-4o
    restart: always
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 5s
```

Run with:
```bash
docker-compose up -d
```

### Using Nginx Reverse Proxy (Recommended for Production)

```nginx
upstream shopify_api {
    server localhost:8000;
}

server {
    listen 80;
    server_name <your-domain.com>;

    location / {
        proxy_pass http://shopify_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Step 6: AWS Security Group Configuration

Make sure your EC2 security group allows:
- **Inbound Rule**: HTTP/HTTPS on port 80/443 (or 8000 if testing)
- **Source**: `0.0.0.0/0` (or restrict to your IP)

---

## Useful Docker Commands

```bash
# View running containers
docker ps

# View all containers
docker ps -a

# View logs
docker logs shopify-api

# Stop container
docker stop shopify-api

# Start container
docker start shopify-api

# Remove container
docker rm shopify-api

# Update image
docker pull <your-dockerhub-username>/shopify-backend:latest
docker stop shopify-api
docker rm shopify-api
docker run -d --name shopify-api -p 8000:8000 <your-dockerhub-username>/shopify-backend:latest
```

---

## Troubleshooting

### Container won't start
```bash
docker logs shopify-api
```

### Port already in use
```bash
docker run -p 8001:8000 ...  # Map to different port
```

### Cannot pull from Docker Hub
```bash
docker login  # Re-authenticate
```

### Need to access logs in real-time
```bash
docker logs -f shopify-api
```

---

## Next Steps

1. Set up CI/CD pipeline (GitHub Actions, GitLab CI) to auto-build and push to Docker Hub
2. Use AWS CloudWatch for monitoring
3. Set up SSL/TLS certificate with Let's Encrypt
4. Consider AWS ECS for production-grade orchestration
