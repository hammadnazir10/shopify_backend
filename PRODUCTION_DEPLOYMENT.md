# EC2 Production Deployment with Docker Compose & Nginx

## Step 1: Prepare EC2 Instance

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@<your-ec2-ip>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose
sudo apt install docker.io docker-compose-v2 -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -a -G docker ubuntu

# Logout and login again
exit
ssh -i your-key.pem ubuntu@<your-ec2-ip>
```

## Step 2: Clone or Copy Your Project

```bash
# Option A: Clone from GitHub
git clone https://github.com/your-username/shopify.git
cd shopify

# Option B: SCP files from local machine
# scp -i your-key.pem -r /path/to/shopify/* ubuntu@<your-ec2-ip>:~/shopify/
```

## Step 3: Create `.env` File on EC2

```bash
cat > .env << 'EOF'
EOF
```

⚠️ **Security Best Practice:** Use AWS Secrets Manager instead:
```bash
aws secretsmanager create-secret --name shopify-api-env --secret-string file://.env
```

## Step 4: Create SSL Directory (for future HTTPS)

```bash
mkdir -p ssl
# Later: Add your SSL certificates here
# cp /path/to/cert.pem ssl/
# cp /path/to/key.pem ssl/
```

## Step 5: Start Docker Compose

```bash
# Pull latest image
docker-compose pull

# Start services (logs will show real-time)
docker-compose up -d

# View logs
docker-compose logs -f

# Check services running
docker-compose ps
```

## Step 6: Verify Everything is Running

```bash
# Check containers
docker ps

# Test locally
curl http://localhost/

# Test from your machine
curl http://<your-ec2-ip>/

# View API docs
# Open browser: http://<your-ec2-ip>/docs
```

## Step 7: AWS Security Group Configuration

In AWS Console:
1. EC2 → Security Groups
2. Find your security group
3. Add **Inbound Rules**:
   - HTTP: Port 80, Source: 0.0.0.0/0
   - HTTPS: Port 443, Source: 0.0.0.0/0
   - SSH: Port 22, Source: Your IP (recommended)

## Step 8: Set Up SSL/TLS with Let's Encrypt (Recommended)

### Option A: Use Certbot on EC2 (before Docker)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot certonly --standalone -d your-domain.com -d www.your-domain.com
sudo ls /etc/letsencrypt/live/your-domain.com/
```

Copy certs to project:
```bash
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem ssl/cert.pem
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem ssl/key.pem
sudo chown ubuntu:ubuntu ssl/*
```

### Option B: Use Certbot with Docker

```bash
docker run --rm \
  -v $(pwd)/ssl:/etc/letsencrypt \
  certbot/certbot certonly \
  --standalone \
  -d your-domain.com \
  -d www.your-domain.com \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email
```

Then uncomment the HTTPS section in `nginx.conf` and restart:
```bash
docker-compose restart nginx
```

## Step 9: Monitor & Manage

```bash
# View real-time logs
docker-compose logs -f shopify-api
docker-compose logs -f nginx

# Stop all services
docker-compose down

# Restart services
docker-compose restart

# Update to latest image
docker-compose pull
docker-compose up -d

# View resource usage
docker stats

# Check nginx config for errors
docker exec shopify-nginx nginx -t
```

## Step 10: Auto-Renewal for SSL Certificates

Create a cron job:
```bash
sudo crontab -e
```

Add:
```
# Renew SSL certificate every month
0 2 1 * * /usr/bin/certbot renew --quiet && cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /home/ubuntu/shopify/ssl/cert.pem && cp /etc/letsencrypt/live/your-domain.com/privkey.pem /home/ubuntu/shopify/ssl/key.pem && docker exec shopify-nginx nginx -s reload
```

---

## Useful Docker Compose Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# Restart specific service
docker-compose restart shopify-api
docker-compose restart nginx

# View logs
docker-compose logs -f

# Execute command in container
docker-compose exec shopify-api bash
docker-compose exec nginx sh

# Rebuild images
docker-compose build --no-cache

# Update and restart
docker-compose pull && docker-compose up -d
```

---

## Troubleshooting

### Services won't start
```bash
docker-compose logs
docker-compose down
docker-compose up -d
```

### Nginx returns 502 Bad Gateway
```bash
# Check if FastAPI container is running
docker-compose ps

# Check FastAPI logs
docker-compose logs shopify-api

# Verify nginx config
docker exec shopify-nginx nginx -t
```

### Port 80 already in use
```bash
sudo lsof -i :80
sudo kill -9 <PID>
# Or change nginx port in docker-compose.yml
```

### SSL certificate issues
```bash
docker exec shopify-nginx nginx -t  # Test config
docker-compose logs nginx           # View logs
docker-compose restart nginx        # Restart nginx
```

---

## Architecture

```
User Request
    ↓
Security Group (Port 80/443)
    ↓
Docker Network (shopify-network)
    ↓
Nginx Container (Port 80/443)
    ↓
Rate Limiting & Proxy
    ↓
FastAPI Container (Port 8000)
    ↓
Application Logic
```

---

## Next Steps

1. ✅ Set up domain name & DNS pointing to EC2
2. ✅ Configure SSL certificate
3. ✅ Enable firewall rules
4. ✅ Set up CloudWatch monitoring
5. ✅ Create automated backups
6. ✅ Set up log aggregation
