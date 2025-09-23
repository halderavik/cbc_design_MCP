# CBC Design Generator MCP Server - Deployment Guide

This guide provides comprehensive instructions for deploying the CBC Design Generator MCP Server in various environments, from local development to production cloud deployments.

## Table of Contents

1. [Overview](#overview)
2. [Local Deployment](#local-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Production Considerations](#production-considerations)
6. [Monitoring and Maintenance](#monitoring-and-maintenance)
7. [Security](#security)
8. [Troubleshooting](#troubleshooting)

## Overview

The CBC Design Generator MCP Server can be deployed in various environments:

- **Local Development**: For development and testing
- **Docker Containers**: For consistent deployment across environments
- **Cloud Platforms**: For scalable production deployment
- **On-Premises**: For enterprise environments

## Local Deployment

### Prerequisites
- Python 3.11 or higher
- pip package manager
- Git (for version control)

### Installation Steps

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd CBC_design_MCP
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -e .
   ```

4. **Verify Installation**
   ```bash
   python -m conjoint_mcp.server
   ```

### Configuration

1. **Environment Variables**
   ```bash
   export APP_VERSION=0.1.0
   export LOG_LEVEL=INFO
   export MAX_RESPONSE_TIME=30
   export MAX_MEMORY_USAGE=500MB
   ```

2. **Configuration File**
   Create `.env` file:
   ```env
   APP_VERSION=0.1.0
   LOG_LEVEL=INFO
   MAX_RESPONSE_TIME=30
   MAX_MEMORY_USAGE=500MB
   DEBUG=false
   ```

### Running the Server

1. **Basic Startup**
   ```bash
   python -m conjoint_mcp.server
   ```

2. **With Logging**
   ```bash
   python -m conjoint_mcp.server > server.log 2>&1
   ```

3. **Background Process**
   ```bash
   nohup python -m conjoint_mcp.server > server.log 2>&1 &
   ```

## Docker Deployment

### Prerequisites
- Docker Engine 20.10 or higher
- Docker Compose 2.0 or higher

### Dockerfile

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY pyproject.toml ./
COPY setup.cfg ./

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy application code
COPY src/ ./src/
COPY scripts/ ./scripts/
COPY docs/ ./docs/

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port (if HTTP mode is implemented)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Start the server
CMD ["python", "-m", "conjoint_mcp.server"]
```

### Docker Compose

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  conjoint-mcp:
    build: .
    ports:
      - "8080:8080"
    environment:
      - APP_VERSION=0.1.0
      - LOG_LEVEL=INFO
      - MAX_RESPONSE_TIME=30
      - MAX_MEMORY_USAGE=500MB
    volumes:
      - ./logs:/app/logs
      - ./exports:/app/exports
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "python", "-c", "import requests; requests.get('http://localhost:8080/health')"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  # Optional: Add monitoring
  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    volumes:
      - grafana-storage:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  grafana-storage:
```

### Building and Running

1. **Build the Image**
   ```bash
   docker build -t conjoint-mcp:latest .
   ```

2. **Run with Docker Compose**
   ```bash
   docker-compose up -d
   ```

3. **Check Status**
   ```bash
   docker-compose ps
   docker-compose logs -f conjoint-mcp
   ```

4. **Stop Services**
   ```bash
   docker-compose down
   ```

## Cloud Deployment

### Heroku Deployment

1. **Prerequisites**
   - Heroku CLI installed
   - Git repository
   - Heroku account

2. **Create Heroku App**
   ```bash
   heroku create your-app-name
   ```

3. **Configure Environment Variables**
   ```bash
   heroku config:set APP_VERSION=0.1.0
   heroku config:set LOG_LEVEL=INFO
   heroku config:set MAX_RESPONSE_TIME=30
   ```

4. **Deploy**
   ```bash
   git push heroku main
   ```

5. **Check Status**
   ```bash
   heroku ps
   heroku logs --tail
   ```

### AWS Deployment

1. **EC2 Instance**
   ```bash
   # Launch EC2 instance
   aws ec2 run-instances \
     --image-id ami-0c02fb55956c7d316 \
     --instance-type t3.medium \
     --key-name your-key-pair \
     --security-group-ids sg-12345678 \
     --subnet-id subnet-12345678
   ```

2. **Install Dependencies**
   ```bash
   sudo yum update -y
   sudo yum install -y python3 python3-pip git
   ```

3. **Deploy Application**
   ```bash
   git clone <repository-url>
   cd CBC_design_MCP
   python3 -m venv venv
   source venv/bin/activate
   pip install -e .
   ```

4. **Configure Systemd Service**
   Create `/etc/systemd/system/conjoint-mcp.service`:
   ```ini
   [Unit]
   Description=CBC Design Generator MCP Server
   After=network.target

   [Service]
   Type=simple
   User=ec2-user
   WorkingDirectory=/home/ec2-user/CBC_design_MCP
   Environment=PATH=/home/ec2-user/CBC_design_MCP/venv/bin
   ExecStart=/home/ec2-user/CBC_design_MCP/venv/bin/python -m conjoint_mcp.server
   Restart=always
   RestartSec=10

   [Install]
   WantedBy=multi-user.target
   ```

5. **Start Service**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable conjoint-mcp
   sudo systemctl start conjoint-mcp
   sudo systemctl status conjoint-mcp
   ```

### Google Cloud Platform

1. **Create VM Instance**
   ```bash
   gcloud compute instances create conjoint-mcp \
     --zone=us-central1-a \
     --machine-type=e2-medium \
     --image-family=ubuntu-2004-lts \
     --image-project=ubuntu-os-cloud \
     --boot-disk-size=20GB
   ```

2. **Deploy Application**
   ```bash
   gcloud compute ssh conjoint-mcp --zone=us-central1-a
   # Follow EC2 deployment steps
   ```

### Azure Deployment

1. **Create VM**
   ```bash
   az vm create \
     --resource-group myResourceGroup \
     --name conjoint-mcp \
     --image UbuntuLTS \
     --size Standard_B2s \
     --admin-username azureuser \
     --generate-ssh-keys
   ```

2. **Deploy Application**
   ```bash
   az vm run-command invoke \
     --resource-group myResourceGroup \
     --name conjoint-mcp \
     --command-id RunShellScript \
     --scripts "git clone <repository-url> && cd CBC_design_MCP && python3 -m venv venv && source venv/bin/activate && pip install -e ."
   ```

## Production Considerations

### Performance Optimization

1. **Resource Allocation**
   ```yaml
   # Docker Compose with resource limits
   services:
     conjoint-mcp:
       deploy:
         resources:
           limits:
             cpus: '2.0'
             memory: 1G
           reservations:
             cpus: '1.0'
             memory: 512M
   ```

2. **Scaling**
   ```bash
   # Horizontal scaling with Docker Compose
   docker-compose up --scale conjoint-mcp=3
   ```

3. **Load Balancing**
   ```nginx
   # Nginx configuration
   upstream conjoint_mcp {
       server localhost:8080;
       server localhost:8081;
       server localhost:8082;
   }

   server {
       listen 80;
       location / {
           proxy_pass http://conjoint_mcp;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

### High Availability

1. **Health Checks**
   ```bash
   # Health check script
   #!/bin/bash
   response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
   if [ $response != "200" ]; then
       echo "Health check failed"
       exit 1
   fi
   ```

2. **Auto-restart**
   ```bash
   # Systemd service with auto-restart
   [Service]
   Restart=always
   RestartSec=10
   ```

3. **Backup Strategy**
   ```bash
   # Backup script
   #!/bin/bash
   tar -czf backup-$(date +%Y%m%d).tar.gz \
     /app/exports \
     /app/logs \
     /app/config
   ```

### Security

1. **Firewall Configuration**
   ```bash
   # UFW firewall rules
   sudo ufw allow 22/tcp
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw enable
   ```

2. **SSL/TLS Configuration**
   ```nginx
   # Nginx SSL configuration
   server {
       listen 443 ssl;
       ssl_certificate /path/to/certificate.crt;
       ssl_certificate_key /path/to/private.key;
       
       location / {
           proxy_pass http://conjoint_mcp;
       }
   }
   ```

3. **Access Control**
   ```bash
   # IP whitelist
   iptables -A INPUT -p tcp --dport 8080 -s 192.168.1.0/24 -j ACCEPT
   iptables -A INPUT -p tcp --dport 8080 -j DROP
   ```

## Monitoring and Maintenance

### Logging

1. **Log Configuration**
   ```python
   # Logging configuration
   import logging
   from logging.handlers import RotatingFileHandler

   # Create rotating file handler
   handler = RotatingFileHandler(
       'app.log', maxBytes=10000000, backupCount=5
   )
   handler.setLevel(logging.INFO)
   
   # Create formatter
   formatter = logging.Formatter(
       '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
   )
   handler.setFormatter(formatter)
   
   # Add handler to logger
   logger = logging.getLogger('conjoint_mcp')
   logger.addHandler(handler)
   ```

2. **Log Rotation**
   ```bash
   # Logrotate configuration
   /app/logs/*.log {
       daily
       missingok
       rotate 30
       compress
       delaycompress
       notifempty
       create 644 app app
   }
   ```

### Monitoring

1. **Prometheus Metrics**
   ```python
   # Prometheus metrics
   from prometheus_client import Counter, Histogram, Gauge

   request_count = Counter('requests_total', 'Total requests', ['method', 'status'])
   request_duration = Histogram('request_duration_seconds', 'Request duration')
   active_connections = Gauge('active_connections', 'Active connections')
   ```

2. **Health Monitoring**
   ```bash
   # Health check endpoint
   curl -f http://localhost:8080/health || exit 1
   ```

3. **Performance Monitoring**
   ```bash
   # Performance monitoring script
   #!/bin/bash
   while true; do
       response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:8080/health)
       echo "$(date): Response time: ${response_time}s"
       sleep 60
   done
   ```

### Maintenance

1. **Regular Updates**
   ```bash
   # Update dependencies
   pip install --upgrade -e .
   
   # Update system packages
   sudo apt update && sudo apt upgrade -y
   ```

2. **Database Maintenance** (if applicable)
   ```bash
   # Database backup
   pg_dump -h localhost -U user -d database > backup.sql
   
   # Database optimization
   psql -h localhost -U user -d database -c "VACUUM ANALYZE;"
   ```

3. **Log Cleanup**
   ```bash
   # Clean old logs
   find /app/logs -name "*.log" -mtime +30 -delete
   ```

## Security

### Authentication and Authorization

1. **API Key Authentication**
   ```python
   # API key middleware
   def authenticate_request(request):
       api_key = request.headers.get('X-API-Key')
       if not api_key or not validate_api_key(api_key):
           raise UnauthorizedError("Invalid API key")
   ```

2. **Rate Limiting**
   ```python
   # Rate limiting
   from flask_limiter import Limiter
   
   limiter = Limiter(
       app,
       key_func=lambda: request.remote_addr,
       default_limits=["1000 per hour"]
   )
   ```

### Data Protection

1. **Input Validation**
   ```python
   # Input validation
   from pydantic import BaseModel, validator
   
   class DesignRequest(BaseModel):
       method: str
       grid: dict
       
       @validator('method')
       def validate_method(cls, v):
           if v not in ['random', 'balanced', 'orthogonal', 'doptimal']:
               raise ValueError('Invalid method')
           return v
   ```

2. **Output Sanitization**
   ```python
   # Output sanitization
   def sanitize_response(response):
       # Remove sensitive information
       if 'error' in response:
           response['error'] = sanitize_error(response['error'])
       return response
   ```

### Network Security

1. **HTTPS Configuration**
   ```nginx
   # Nginx HTTPS configuration
   server {
       listen 443 ssl http2;
       ssl_certificate /path/to/certificate.crt;
       ssl_certificate_key /path/to/private.key;
       ssl_protocols TLSv1.2 TLSv1.3;
       ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
       ssl_prefer_server_ciphers off;
   }
   ```

2. **Security Headers**
   ```nginx
   # Security headers
   add_header X-Frame-Options DENY;
   add_header X-Content-Type-Options nosniff;
   add_header X-XSS-Protection "1; mode=block";
   add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
   ```

## Troubleshooting

### Common Issues

1. **Server Won't Start**
   ```bash
   # Check logs
   journalctl -u conjoint-mcp -f
   
   # Check port availability
   netstat -tlnp | grep :8080
   ```

2. **High Memory Usage**
   ```bash
   # Monitor memory usage
   ps aux | grep conjoint_mcp
   free -h
   
   # Check for memory leaks
   valgrind --tool=memcheck python -m conjoint_mcp.server
   ```

3. **Slow Performance**
   ```bash
   # Profile performance
   python -m cProfile -o profile.stats -m conjoint_mcp.server
   
   # Analyze profile
   python -c "import pstats; pstats.Stats('profile.stats').sort_stats('cumulative').print_stats(10)"
   ```

### Recovery Procedures

1. **Service Recovery**
   ```bash
   # Restart service
   sudo systemctl restart conjoint-mcp
   
   # Check status
   sudo systemctl status conjoint-mcp
   ```

2. **Data Recovery**
   ```bash
   # Restore from backup
   tar -xzf backup-20240101.tar.gz -C /
   
   # Verify data integrity
   python -c "import json; json.load(open('exports/design.json'))"
   ```

3. **Configuration Recovery**
   ```bash
   # Restore configuration
   cp config.backup .env
   
   # Validate configuration
   python -c "from conjoint_mcp.config.settings import get_settings; print(get_settings())"
   ```

## Best Practices

### Deployment

1. **Use Infrastructure as Code**
   - Terraform for cloud resources
   - Ansible for configuration management
   - Docker for containerization

2. **Implement CI/CD**
   - Automated testing
   - Automated deployment
   - Rollback procedures

3. **Monitor Everything**
   - Application metrics
   - Infrastructure metrics
   - Business metrics

### Security

1. **Principle of Least Privilege**
   - Minimal permissions
   - Regular access reviews
   - Secure defaults

2. **Defense in Depth**
   - Multiple security layers
   - Network segmentation
   - Regular security audits

3. **Incident Response**
   - Response procedures
   - Communication plans
   - Recovery procedures

### Operations

1. **Automation**
   - Automated deployments
   - Automated monitoring
   - Automated recovery

2. **Documentation**
   - Deployment procedures
   - Troubleshooting guides
   - Runbooks

3. **Training**
   - Team training
   - Documentation
   - Knowledge sharing
