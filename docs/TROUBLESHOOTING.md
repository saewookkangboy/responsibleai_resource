# 트러블슈팅 가이드

Responsible AI Resource Collection 사용 중 발생할 수 있는 일반적인 문제와 해결 방법을 제공합니다.

## 📋 목차

1. [설치 문제](#설치-문제)
2. [실행 오류](#실행-오류)
3. [성능 문제](#성능-문제)
4. [보안 문제](#보안-문제)
5. [통합 문제](#통합-문제)

## 설치 문제

### 문제 1: 의존성 설치 실패

**증상**:
```
ERROR: Could not find a version that satisfies the requirement torch>=2.0.0
```

**해결 방법**:
```bash
# Python 버전 확인 (3.8 이상 필요)
python --version

# pip 업그레이드
pip install --upgrade pip

# 개별 패키지 설치
pip install torch==2.0.0
pip install stable-baselines3==2.0.0
```

### 문제 2: SHAP 설치 오류

**증상**:
```
ERROR: Failed building wheel for shap
```

**해결 방법**:
```bash
# 시스템 의존성 설치 (Ubuntu/Debian)
sudo apt-get install build-essential

# 또는 conda 사용
conda install -c conda-forge shap
```

### 문제 3: Fairlearn 설치 문제

**증상**:
```
ERROR: No matching distribution found for fairlearn
```

**해결 방법**:
```bash
# 최신 버전 확인
pip install --upgrade fairlearn

# 또는 특정 버전 설치
pip install fairlearn==0.9.0
```

## 실행 오류

### 문제 1: 설정 파일을 찾을 수 없음

**증상**:
```
FileNotFoundError: config.yaml not found
```

**해결 방법**:
```bash
# 설정 파일 경로 확인
ls -la responsible_ai_automation/config.yaml

# 절대 경로 사용
python main.py --config /absolute/path/to/config.yaml

# 또는 현재 디렉토리에서 실행
cd responsible_ai_automation
python main.py --config config.yaml
```

### 문제 2: 모델 초기화 오류

**증상**:
```
AttributeError: 'RandomForestClassifier' object has no attribute 'predict_proba'
```

**해결 방법**:
```python
# 모델이 predict_proba를 지원하는지 확인
if hasattr(model, 'predict_proba'):
    probabilities = model.predict_proba(X)
else:
    predictions = model.predict(X)
```

### 문제 3: 메모리 부족 오류

**증상**:
```
MemoryError: Unable to allocate array
```

**해결 방법**:
```python
# 데이터 샘플링
sample_size = min(10000, len(X))
indices = np.random.choice(len(X), sample_size, replace=False)
X_sample = X[indices]
y_sample = y[indices]

# 또는 청크 단위 처리
chunk_size = 1000
for i in range(0, len(X), chunk_size):
    chunk = X[i:i+chunk_size]
    # 처리
```

## 성능 문제

### 문제 1: 평가 시간이 너무 오래 걸림

**증상**:
- 대용량 데이터셋에서 평가가 매우 느림

**해결 방법**:
```python
# 샘플링 사용
from src.evaluation.comprehensive import ComprehensiveEvaluator

# SHAP 계산 시 샘플링
explainer = shap.TreeExplainer(model)
shap_values = explainer.shap_values(X[:100])  # 처음 100개만 사용

# 병렬 처리
from multiprocessing import Pool

def evaluate_chunk(chunk):
    return evaluator.evaluate(model, chunk[0], chunk[1], ...)

with Pool(processes=4) as pool:
    results = pool.map(evaluate_chunk, data_chunks)
```

### 문제 2: 강화 학습이 수렴하지 않음

**증상**:
- 학습이 오래 걸리고 성능이 개선되지 않음

**해결 방법**:
```yaml
# config.yaml 수정
reinforcement_learning:
  learning_rate: 1e-4  # 더 낮은 학습률
  batch_size: 128     # 더 큰 배치 크기
  training_steps: 200000  # 더 많은 스텝
```

### 문제 3: 대시보드가 느림

**증상**:
- 모니터링 대시보드가 느리게 로드됨

**해결 방법**:
```python
# 메트릭 보관 기간 단축
monitoring:
  metrics_retention_days: 7  # 30일에서 7일로 단축

# 샘플링된 메트릭만 저장
dashboard.log_metrics(metrics, sample_rate=0.1)  # 10%만 저장
```

## 보안 문제

### 문제 1: API 키 노출

**증상**:
- API 키가 코드나 로그에 노출됨

**해결 방법**:
```python
# 환경 변수 사용
import os
api_key = os.getenv("OPENAI_API_KEY")

# .env 파일 사용 (python-dotenv)
from dotenv import load_dotenv
load_dotenv()

# 암호화된 키 저장
from cryptography.fernet import Fernet
key = Fernet.generate_key()
cipher = Fernet(key)
encrypted_key = cipher.encrypt(api_key.encode())
```

### 문제 2: 민감한 데이터 로깅

**증상**:
- 로그에 민감한 정보가 기록됨

**해결 방법**:
```python
# 민감한 정보 마스킹
def mask_sensitive_data(data):
    if 'api_key' in data:
        data['api_key'] = '***'
    if 'password' in data:
        data['password'] = '***'
    return data

logger.info(f"Data: {mask_sensitive_data(data)}")
```

## 통합 문제

### 문제 1: 프로젝트 간 import 오류

**증상**:
```
ModuleNotFoundError: No module named 'src.validator'
```

**해결 방법**:
```python
# 프로젝트 경로 추가
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "ai-platform-validator"))
sys.path.insert(0, str(project_root / "responsible_ai_automation"))
```

### 문제 2: 설정 파일 형식 불일치

**증상**:
- 프로젝트 간 설정 파일 형식이 다름

**해결 방법**:
```python
# 설정 파일 변환 유틸리티 사용
from src.utils.config_converter import convert_config

converted_config = convert_config(
    source_config="ai-platform-validator/config.yaml",
    target_format="responsible_ai_automation"
)
```

## 일반적인 디버깅 팁

### 1. 로그 레벨 조정

```python
# DEBUG 레벨로 상세 로그 확인
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. 단계별 실행

```python
# 각 단계를 개별적으로 실행하여 문제 지점 파악
system = ResponsibleAIAutomationSystem("config.yaml")
# 1단계: 초기화 확인
print("Initialization: OK")

# 2단계: 모델 로드 확인
system.initialize_model(model, X, y)
print("Model initialization: OK")

# 3단계: 평가 확인
metrics = system.evaluate(X, y, y_pred)
print("Evaluation: OK")
```

### 3. 예외 처리 강화

```python
try:
    result = system.evaluate(X, y, y_pred)
except Exception as e:
    import traceback
    traceback.print_exc()
    logger.error(f"Evaluation failed: {e}")
    raise
```

## 추가 도움말

- [GitHub Issues](https://github.com/yourusername/responsibleai_resource/issues)
- [API 레퍼런스](responsible_ai_automation/docs/api_reference.md)
- [통합 가이드](docs/INTEGRATION_GUIDE.md)

---

**Last Updated**: 2026-01-07

