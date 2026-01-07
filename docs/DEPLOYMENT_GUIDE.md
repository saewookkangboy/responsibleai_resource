# 배포 가이드

Responsible AI Resource Collection을 프로덕션 환경에 배포하는 방법을 안내합니다.

## 📋 목차

1. [개요](#개요)
2. [Docker 컨테이너화](#docker-컨테이너화)
3. [클라우드 배포](#클라우드-배포)
4. [프로덕션 환경 설정](#프로덕션-환경-설정)
5. [모니터링 및 로깅](#모니터링-및-로깅)

## 개요

이 가이드는 Responsible AI Resource Collection의 각 프로젝트를 프로덕션 환경에 배포하는 방법을 제공합니다.

### 배포 옵션

1. **Docker 컨테이너**: 가장 간단한 배포 방법
2. **클라우드 플랫폼**: AWS, GCP, Azure 등
3. **온프레미스**: 자체 서버 환경

## Docker 컨테이너화

### Responsible AI Automation Dockerfile

```dockerfile
# responsible_ai_automation/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# 시스템 의존성 설치
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# 포트 노출
EXPOSE 8080

# 실행 명령
CMD ["python", "main.py", "--config", "config.yaml", "--mode", "monitor"]
```

### Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  responsible-ai-automation:
    build:
      context: ./responsible_ai_automation
      dockerfile: Dockerfile
    ports:
      - "8080:8080"
    environment:
      - LOG_LEVEL=INFO
      - DASHBOARD_PORT=8080
    volumes:
      - ./responsible_ai_automation/models:/app/models
      - ./responsible_ai_automation/config.yaml:/app/config.yaml
    restart: unless-stopped

  ai-platform-validator:
    build:
      context: ./ai-platform-validator
      dockerfile: Dockerfile
    ports:
      - "8081:8081"
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped
```

### Docker 빌드 및 실행

```bash
# Responsible AI Automation 빌드
cd responsible_ai_automation
docker build -t responsible-ai-automation:latest .

# 실행
docker run -d \
  -p 8080:8080 \
  -v $(pwd)/models:/app/models \
  -v $(pwd)/config.yaml:/app/config.yaml \
  responsible-ai-automation:latest

# Docker Compose 사용
docker-compose up -d
```

## 클라우드 배포

### AWS 배포

#### 1. ECS (Elastic Container Service)

```bash
# ECR에 이미지 푸시
aws ecr create-repository --repository-name responsible-ai-automation
docker tag responsible-ai-automation:latest \
  <account-id>.dkr.ecr.<region>.amazonaws.com/responsible-ai-automation:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/responsible-ai-automation:latest

# ECS 태스크 정의 생성
aws ecs register-task-definition --cli-input-json file://task-definition.json
```

#### 2. Lambda 함수 (서버리스)

```python
# lambda_handler.py
import json
from main import ResponsibleAIAutomationSystem

def lambda_handler(event, context):
    system = ResponsibleAIAutomationSystem("config.yaml")
    
    # 이벤트 처리
    result = system.evaluate(...)
    
    return {
        'statusCode': 200,
        'body': json.dumps(result)
    }
```

### Google Cloud Platform 배포

#### Cloud Run

```bash
# 이미지 빌드 및 푸시
gcloud builds submit --tag gcr.io/<project-id>/responsible-ai-automation

# Cloud Run에 배포
gcloud run deploy responsible-ai-automation \
  --image gcr.io/<project-id>/responsible-ai-automation \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Azure 배포

#### Container Instances

```bash
# Azure Container Registry에 푸시
az acr build --registry <registry-name> \
  --image responsible-ai-automation:latest \
  ./responsible_ai_automation

# Container Instance 생성
az container create \
  --resource-group <resource-group> \
  --name responsible-ai-automation \
  --image <registry-name>.azurecr.io/responsible-ai-automation:latest \
  --cpu 2 \
  --memory 4
```

## 프로덕션 환경 설정

### 환경 변수 설정

```bash
# .env 파일
LOG_LEVEL=INFO
DASHBOARD_PORT=8080
MODEL_SAVE_PATH=/app/models
API_KEY_ENCRYPTION=true
DATABASE_URL=postgresql://user:password@localhost/dbname
REDIS_URL=redis://localhost:6379
```

### 설정 파일 최적화

```yaml
# config.production.yaml
evaluation:
  fairness:
    threshold: 0.1
  transparency:
    threshold: 0.7

monitoring:
  enabled: true
  dashboard_port: 8080
  log_level: INFO
  metrics_retention_days: 90  # 프로덕션에서는 더 긴 보관 기간

auto_update:
  enabled: true
  check_interval: 3600
  rollback:
    enabled: true
    performance_threshold: 0.95
```

### 보안 설정

```python
# 보안 설정 예제
import os
from cryptography.fernet import Fernet

# API 키 암호화
def encrypt_api_key(api_key: str) -> str:
    key = os.getenv("ENCRYPTION_KEY")
    f = Fernet(key)
    return f.encrypt(api_key.encode()).decode()

# 환경 변수에서 암호화된 키 로드
encrypted_key = os.getenv("ENCRYPTED_API_KEY")
api_key = decrypt_api_key(encrypted_key)
```

## 모니터링 및 로깅

### 로깅 설정

```python
# logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging(log_level=logging.INFO):
    logger = logging.getLogger()
    logger.setLevel(log_level)
    
    # 파일 핸들러
    file_handler = RotatingFileHandler(
        'logs/responsible_ai.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter('%(levelname)s - %(message)s')
    )
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
```

### 모니터링 대시보드

```python
# 대시보드 접근
# http://localhost:8080

# 메트릭 수집
from src.monitoring.dashboard import MonitoringDashboard

dashboard = MonitoringDashboard(config)
dashboard.log_metrics(metrics)
```

### 알림 설정

```python
# Slack 알림 설정
alert_channels:
  - "slack"
  
slack_webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
```

## 배포 체크리스트

### 배포 전 확인사항

- [ ] 모든 테스트 통과
- [ ] 환경 변수 설정 완료
- [ ] 보안 설정 확인
- [ ] 로깅 설정 확인
- [ ] 모니터링 대시보드 접근 가능
- [ ] 백업 전략 수립
- [ ] 롤백 계획 수립

### 배포 후 확인사항

- [ ] 서비스 정상 동작 확인
- [ ] 로그 정상 기록 확인
- [ ] 모니터링 메트릭 수집 확인
- [ ] 알림 시스템 동작 확인
- [ ] 성능 지표 확인

## 트러블슈팅

### 일반적인 문제

1. **포트 충돌**
   ```bash
   # 포트 사용 확인
   lsof -i :8080
   
   # 다른 포트 사용
   export DASHBOARD_PORT=8081
   ```

2. **메모리 부족**
   ```bash
   # Docker 메모리 제한 증가
   docker run -m 4g responsible-ai-automation
   ```

3. **의존성 오류**
   ```bash
   # 의존성 재설치
   pip install --upgrade -r requirements.txt
   ```

## 추가 리소스

- [Docker 공식 문서](https://docs.docker.com/)
- [AWS ECS 가이드](https://docs.aws.amazon.com/ecs/)
- [Google Cloud Run 가이드](https://cloud.google.com/run/docs)
- [Azure Container Instances 가이드](https://docs.microsoft.com/azure/container-instances/)

---

**Last Updated**: 2026-01-07

