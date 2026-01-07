# 빠른 시작 가이드 (Quick Start Guide)

5분 안에 Responsible AI Automation을 시작하세요!

## 🚀 1단계: 설치 (1분)

```bash
# 저장소 클론
git clone https://github.com/saewookkangboy/responsible-ai-resource.git
cd responsible-ai-resource/responsible_ai_automation

# 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

## ⚡ 2단계: 빠른 시작 스크립트 실행 (2분)

```bash
python quick_start.py
```

이 스크립트는:
- ✅ 자동으로 기본 설정 파일 생성
- ✅ 샘플 데이터 생성 및 모델 학습
- ✅ Responsible AI 평가 수행
- ✅ 결과 출력

## 📊 3단계: 결과 확인

스크립트 실행 후 다음과 같은 결과를 확인할 수 있습니다:

```
📊 전체 Responsible AI 점수: 0.750
✅ Responsible AI 기준 충족: 예

카테고리별 점수:
  - 공정성: 0.750
  - 투명성: 0.700
  - 책임성: 0.650
  - 프라이버시: 0.800
  - 견고성: 0.750
```

## 🎯 4단계: 실제 데이터로 평가 (2분)

```python
from main import ResponsibleAIAutomationSystem
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 시스템 초기화
system = ResponsibleAIAutomationSystem("config.yaml")

# 모델 및 데이터 준비
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 모델 등록
system.initialize_model(model, X_test, y_test, sensitive_features)

# 평가 수행
y_pred = model.predict(X_test)
metrics = system.evaluate(X_test, y_test, y_pred, sensitive_features)

print(f"Responsible AI 점수: {metrics['overall_responsible_ai_score']:.3f}")
```

## 🌐 5단계: 웹 대시보드 실행 (선택사항)

```bash
streamlit run src/monitoring/dashboard_web.py
```

브라우저에서 `http://localhost:8501` 접속

## 🔧 최적화 팁

### 빠른 평가를 위한 설정

`config.yaml`에서 다음 설정을 조정하세요:

```yaml
evaluation:
  transparency:
    # SHAP 계산 샘플 수 감소
    sample_size: 100  # 기본값: 1000
```

### 대용량 데이터 처리

```python
from src.utils.performance import PerformanceOptimizer

# 데이터 샘플링
X_sample = PerformanceOptimizer.sample_data(X, sample_size=10000)
```

### 병렬 처리 활성화

```python
# config.yaml
evaluation:
  use_parallel: true
  n_jobs: -1  # 모든 CPU 코어 사용
```

## ❓ 문제 해결

### 설치 오류

```bash
# Python 버전 확인 (3.8 이상 필요)
python --version

# pip 업그레이드
pip install --upgrade pip

# 개별 패키지 설치
pip install numpy pandas scikit-learn
```

### 메모리 부족

```python
# 데이터 샘플링 사용
from src.utils.performance import PerformanceOptimizer
X_sample = PerformanceOptimizer.sample_data(X, sample_size=5000)
```

### 평가 시간이 너무 오래 걸림

```yaml
# config.yaml - 평가 메트릭 간소화
evaluation:
  transparency:
    metrics: ["explainability_score"]  # SHAP만 사용
  robustness:
    metrics: ["adversarial_robustness"]  # 적대적 공격만
```

## 📚 다음 단계

- [통합 사용 가이드](../docs/INTEGRATION_GUIDE.md) - 4개 프로젝트 통합
- [API 레퍼런스](docs/api_reference.md) - 상세 API 문서
- [설정 가이드](docs/configuration.md) - 고급 설정
- [예제 코드](examples/) - 다양한 사용 예제

## 💡 빠른 참조

```python
# 최소 코드로 평가
from main import ResponsibleAIAutomationSystem

system = ResponsibleAIAutomationSystem("config.yaml")
system.initialize_model(model, X, y, sensitive_features)
metrics = system.evaluate(X, y, y_pred, sensitive_features)
```

---

**문제가 있나요?** [FAQ](../docs/FAQ.md) 또는 [트러블슈팅 가이드](../docs/TROUBLESHOOTING.md)를 확인하세요.

