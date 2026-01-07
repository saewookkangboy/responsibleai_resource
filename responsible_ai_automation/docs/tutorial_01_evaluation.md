# 튜토리얼 1: Responsible AI 평가 시작하기

이 튜토리얼에서는 Responsible AI 평가를 수행하는 방법을 단계별로 학습합니다.

## 목표

- Responsible AI 평가 시스템 초기화
- 다양한 평가 메트릭 이해
- 평가 결과 해석

## 단계 1: 시스템 초기화

```python
from main import ResponsibleAIAutomationSystem
import yaml

# 설정 파일 로드
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

# 시스템 초기화
system = ResponsibleAIAutomationSystem("config.yaml")
```

## 단계 2: 데이터 및 모델 준비

```python
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 데이터 생성 (실제로는 실제 데이터 사용)
X = np.random.rand(1000, 20)
y = np.random.randint(0, 2, 1000)
sensitive_features = pd.DataFrame({
    "gender": np.random.choice(["M", "F"], 1000),
    "race": np.random.choice(["A", "B", "C"], 1000),
})

# 데이터 분할
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# 모델 학습
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)
```

## 단계 3: 모델 초기화

```python
# 시스템에 모델 등록
system.initialize_model(model, X_train, y_train, sensitive_features.iloc[:len(X_train)])
```

## 단계 4: 평가 수행

```python
# 예측 수행
y_pred = model.predict(X_test)

# 평가 수행
metrics = system.evaluate(
    X_test,
    y_test,
    y_pred,
    sensitive_features.iloc[len(X_train):]
)
```

## 단계 5: 결과 해석

```python
# 종합 점수
print(f"종합 Responsible AI 점수: {metrics['overall_responsible_ai_score']:.3f}")
print(f"Responsible AI 준수 여부: {metrics['is_responsible']}")

# 카테고리별 점수
print("\n=== 카테고리별 점수 ===")
print(f"공정성: {metrics['fairness']['overall_fairness_score']:.3f}")
print(f"투명성: {metrics['transparency']['overall_transparency_score']:.3f}")
print(f"책임성: {metrics['accountability']['overall_accountability_score']:.3f}")
print(f"프라이버시: {metrics['privacy']['overall_privacy_score']:.3f}")
print(f"견고성: {metrics['robustness']['overall_robustness_score']:.3f}")

# 세부 메트릭
print("\n=== 공정성 세부 메트릭 ===")
for attr, attr_metrics in metrics['fairness']['metrics'].items():
    print(f"\n{attr}:")
    for metric_name, metric_value in attr_metrics.items():
        if metric_value is not None:
            print(f"  {metric_name}: {metric_value:.3f}")
```

## 다음 단계

- [튜토리얼 2: 강화 학습 기반 최적화](./tutorial_02_rl_optimization.md)
- [API 레퍼런스](./api_reference.md)

