# Responsible AI Automation Dockerfile
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

# 모델 디렉토리 생성
RUN mkdir -p /app/models

# 포트 노출
EXPOSE 8080

# 실행 명령
CMD ["python", "main.py", "--config", "config.yaml", "--mode", "monitor"]

