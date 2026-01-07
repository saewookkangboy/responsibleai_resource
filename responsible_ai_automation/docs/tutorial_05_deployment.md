# 튜토리얼 5: 프로덕션 배포

이 튜토리얼에서는 Responsible AI Automation 시스템을 프로덕션 환경에 배포하는 방법을 학습합니다.

## 목표

- 프로덕션 설정 구성
- Docker 컨테이너화
- 모니터링 및 로깅 설정

## 단계 1: 프로덕션 설정 파일

`config.production.yaml` 생성:

```yaml
fairness:
  metrics: ["demographic_parity", "equalized_odds", "equal_opportunity"]
  threshold: 0.1
  sensitive_attributes: ["gender", "race", "age"]

transparency:
  metrics: ["explainability_score", "feature_importance"]
  threshold: 0.7

accountability:
  metrics: ["audit_trail", "decision_logging", "error_tracking"]
  enabled: true

privacy:
  metrics: ["differential_privacy", "data_anonymization", "access_control"]
  threshold: 0.8

robustness:
  metrics: ["adversarial_robustness", "out_of_distribution_detection"]
  threshold: 0.75

auto_update:
  enabled: true
  check_interval: 3600
  conditions:
    performance_degradation:
      threshold: 0.05
    ethics_threshold_breach:
      threshold: 0.1
  rollback:
    enabled: true
    performance_threshold: 0.95

monitoring:
  log_level: "INFO"
  dashboard:
    enabled: true
    port: 8080
  alerts:
    enabled: true
    channels:
      - type: "slack"
        settings:
          webhook_url: "${SLACK_WEBHOOK_URL}"

model:
  save_path: "/app/models"
```

## 단계 2: Docker 컨테이너화

`Dockerfile` 생성:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 환경 변수 설정
ENV PYTHONUNBUFFERED=1

# 포트 노출
EXPOSE 8080

# 실행 명령
CMD ["python", "main.py", "--config", "config.production.yaml", "--mode", "monitor"]
```

## 단계 3: Docker Compose 설정

`docker-compose.yml` 생성:

```yaml
version: '3.8'

services:
  responsible-ai:
    build: .
    ports:
      - "8080:8080"
    environment:
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - ./models:/app/models
      - ./logs:/app/logs
    restart: unless-stopped
```

## 단계 4: 배포

```bash
# Docker 이미지 빌드
docker-compose build

# 컨테이너 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f
```

## 단계 5: 모니터링

- 대시보드: http://localhost:8080
- 로그: `docker-compose logs -f responsible-ai`

## 다음 단계

- [배포 가이드](../../docs/DEPLOYMENT_GUIDE.md)
- [트러블슈팅 가이드](../../docs/TROUBLESHOOTING.md)

