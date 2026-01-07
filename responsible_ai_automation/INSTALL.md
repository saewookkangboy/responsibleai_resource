# 설치 가이드 (Installation Guide)

## 최소 요구사항

- Python 3.8 이상
- 4GB 이상 RAM (대용량 데이터의 경우 8GB 이상 권장)
- 2GB 이상 디스크 공간

## 빠른 설치 (권장)

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/responsibleai_resource.git
cd responsibleai_resource/responsible_ai_automation

# 2. 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 의존성 설치
pip install -r requirements.txt

# 4. 빠른 시작
python quick_start.py
```

## 단계별 설치

### 1. Python 환경 확인

```bash
python --version  # Python 3.8 이상 필요
pip --version
```

### 2. 가상 환경 생성 (권장)

```bash
# 가상 환경 생성
python -m venv venv

# 활성화
# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### 3. 의존성 설치

#### 기본 설치

```bash
pip install -r requirements.txt
```

#### 개발 환경 설치

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

#### 최소 설치 (빠른 시작용)

```bash
pip install numpy pandas scikit-learn pyyaml
```

### 4. 설치 확인

```bash
python -c "from main import ResponsibleAIAutomationSystem; print('설치 성공!')"
```

## 문제 해결

### 문제 1: pip 설치 오류

```bash
# pip 업그레이드
pip install --upgrade pip setuptools wheel

# 개별 패키지 설치
pip install numpy
pip install pandas
pip install scikit-learn
```

### 문제 2: Python 버전 오류

```bash
# Python 3.8 이상 필요
python --version

# Python 3.8 이상 설치 필요
# https://www.python.org/downloads/
```

### 문제 3: 메모리 부족

```bash
# 가상 환경에서만 필수 패키지 설치
pip install --no-cache-dir -r requirements.txt
```

### 문제 4: 권한 오류

```bash
# 사용자 디렉토리에 설치
pip install --user -r requirements.txt
```

## 선택적 의존성

### GPU 지원 (PyTorch)

```bash
# CUDA 지원 PyTorch 설치
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
```

### 웹 대시보드

```bash
pip install streamlit plotly
```

### API 서버

```bash
pip install fastapi uvicorn
```

### 모델 버전 관리

```bash
pip install mlflow
```

## Docker 설치 (선택사항)

```bash
# Docker 이미지 빌드
docker build -t responsible-ai-automation .

# Docker 컨테이너 실행
docker run -p 8080:8080 responsible-ai-automation
```

## 클라우드 설치

### Google Colab

```python
!pip install numpy pandas scikit-learn pyyaml
!git clone https://github.com/yourusername/responsibleai_resource.git
```

### AWS SageMaker

```bash
# SageMaker 노트북 인스턴스에서
pip install -r requirements.txt
```

## 설치 후 확인

```bash
# 빠른 시작 스크립트 실행
python quick_start.py

# 또는 Python에서 확인
python
>>> from main import ResponsibleAIAutomationSystem
>>> system = ResponsibleAIAutomationSystem("config.yaml")
>>> print("설치 성공!")
```

## 다음 단계

- [빠른 시작 가이드](QUICK_START.md)
- [사용 예제](examples/)
- [API 레퍼런스](docs/api_reference.md)

