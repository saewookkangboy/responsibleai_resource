# 빠른 시작 가이드

이 가이드에서는 Responsible AI Automation 시스템을 빠르게 시작하는 방법을 안내합니다.

## 📋 사전 요구사항

- Python 3.8 이상
- pip 패키지 관리자

## 🚀 설치

### 1. 저장소 클론

```bash
git clone https://github.com/yourusername/responsibleai_resource.git
cd responsibleai_resource/responsible_ai_automation
```

### 2. 가상 환경 생성 (권장)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

## 📝 기본 사용법

### 1. 설정 파일 준비

`config.yaml` 파일을 생성하고 다음 내용을 추가합니다:

```yaml
fairness:
  metrics: ["demographic_parity", "equalized_odds"]
  threshold: 0.1
  sensitive_attributes: ["gender", "race"]

transparency:
  metrics: ["explainability_score", "feature_importance"]
  threshold: 0.7

accountability:
  metrics: ["audit_trail", "decision_logging"]
  enabled: true

privacy:
  metrics: ["differential_privacy", "data_anonymization"]
  threshold: 0.8

robustness:
  metrics: ["adversarial_robustness"]
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
```

### 2. 기본 평가 수행

```python
from main import ResponsibleAIAutomationSystem
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# 시스템 초기화
system = ResponsibleAIAutomationSystem("config.yaml")

# 데이터 준비
X = np.random.rand(100, 10)
y = np.random.randint(0, 2, 100)
sensitive_features = pd.DataFrame({
    "gender": np.random.choice(["M", "F"], 100),
    "race": np.random.choice(["A", "B", "C"], 100),
})

# 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# 모델 초기화
system.initialize_model(model, X, y, sensitive_features)

# 평가 수행
y_pred = model.predict(X)
metrics = system.evaluate(X, y, y_pred, sensitive_features)

print(f"Responsible AI 점수: {metrics['overall_responsible_ai_score']:.3f}")
print(f"공정성 점수: {metrics['fairness']['overall_fairness_score']:.3f}")
print(f"투명성 점수: {metrics['transparency']['overall_transparency_score']:.3f}")
```

### 3. 자동 모니터링 시작

```python
# 지속적인 모니터링 시작
system.run_continuous_monitoring(X, y, sensitive_features)
```

또는 명령줄에서:

```bash
python main.py --config config.yaml --mode monitor
```

## 📊 다음 단계

- [튜토리얼 1: Responsible AI 평가 시작하기](./tutorial_01_evaluation.md)
- [튜토리얼 2: 강화 학습 기반 최적화](./tutorial_02_rl_optimization.md)
- [튜토리얼 3: 자동 업데이트 시스템 설정](./tutorial_03_auto_update.md)
- [API 레퍼런스](./api_reference.md)

## ❓ 문제 해결

문제가 발생하면 [FAQ](../docs/FAQ.md) 또는 [트러블슈팅 가이드](../docs/TROUBLESHOOTING.md)를 참조하세요.

