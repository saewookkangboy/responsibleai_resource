# 사용 사례 (Use Cases)

이 문서는 Responsible AI Resource를 다양한 도메인에서 사용하는 실제 사례를 제공합니다.

## 📊 1. 금융 서비스

### 시나리오
은행에서 대출 승인 모델의 공정성을 평가하고 개선합니다.

### 구현
```python
from main import ResponsibleAIAutomationSystem
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier

# 시스템 초기화
system = ResponsibleAIAutomationSystem("config.yaml")

# 대출 데이터 로드
loan_data = pd.read_csv("loan_data.csv")
X = loan_data.drop(["loan_approved"], axis=1)
y = loan_data["loan_approved"]
sensitive_features = loan_data[["gender", "race", "age"]]

# 모델 학습
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# Responsible AI 평가
system.initialize_model(model, X.values, y.values, sensitive_features)
y_pred = model.predict(X.values)
metrics = system.evaluate(X.values, y.values, y_pred, sensitive_features)

# 결과 확인
print(f"공정성 점수: {metrics['fairness']['overall_fairness_score']:.3f}")
```

### 주요 고려사항
- 민감한 속성(성별, 인종, 나이)별 공정성 평가
- 규제 준수 (EU AI Act, GDPR)
- 투명성 및 설명 가능성

---

## 🏥 2. 헬스케어

### 시나리오
의료 진단 모델의 편향성을 감지하고 환자 프라이버시를 보호합니다.

### 구현
```python
# 의료 데이터 평가
medical_data = pd.read_csv("medical_data.csv")
X = medical_data.drop(["diagnosis"], axis=1)
y = medical_data["diagnosis"]
sensitive_features = medical_data[["age", "gender", "socioeconomic_status"]]

# 프라이버시 강화 설정
config = {
    "privacy": {
        "metrics": ["differential_privacy", "data_anonymization"],
        "threshold": 0.9,  # 높은 프라이버시 요구사항
    }
}

system = ResponsibleAIAutomationSystem("config.yaml")
# ... 평가 수행
```

### 주요 고려사항
- 높은 프라이버시 요구사항
- HIPAA 준수
- 환자 데이터 보호

---

## 🎓 3. 교육

### 시나리오
입학 심사 모델의 공정성을 평가하고 개선합니다.

### 구현
```python
# 입학 데이터 평가
admission_data = pd.read_csv("admission_data.csv")
X = admission_data.drop(["admitted"], axis=1)
y = admission_data["admitted"]
sensitive_features = admission_data[["gender", "ethnicity", "socioeconomic_background"]]

# 사회적 영향 평가 포함
metrics = system.evaluate(
    X.values, y.values, y_pred, sensitive_features,
    include_social_impact=True
)
```

### 주요 고려사항
- 교육 기회의 공정성
- 사회적 영향 평가
- 투명성 및 설명 가능성

---

## 💼 4. 채용

### 시나리오
채용 지원자 선별 모델의 편향성을 감지하고 완화합니다.

### 구현
```python
# 채용 데이터 평가
hiring_data = pd.read_csv("hiring_data.csv")
X = hiring_data.drop(["hired"], axis=1)
y = hiring_data["hired"]
sensitive_features = hiring_data[["gender", "age", "ethnicity"]]

# 공정성 메트릭 강화
config = {
    "fairness": {
        "metrics": [
            "demographic_parity",
            "equalized_odds",
            "equal_opportunity"
        ],
        "threshold": 0.05,  # 엄격한 공정성 기준
    }
}
```

### 주요 고려사항
- 차별 금지 법률 준수
- 다양한 배경의 지원자 공정한 평가
- 설명 가능한 의사결정

---

## 🎯 5. 추천 시스템

### 시나리오
콘텐츠 추천 모델의 공정성과 투명성을 평가합니다.

### 구현
```python
# 추천 시스템 평가
recommendation_data = pd.read_csv("recommendation_data.csv")
X = recommendation_data.drop(["clicked"], axis=1)
y = recommendation_data["clicked"]
sensitive_features = recommendation_data[["user_demographics"]]

# 투명성 평가 강화
config = {
    "transparency": {
        "metrics": ["explainability_score", "feature_importance"],
        "threshold": 0.8,
    }
}
```

### 주요 고려사항
- 사용자 프라이버시
- 필터 버블 방지
- 추천 이유 설명 가능성

---

## 📈 벤치마크 결과

### Adult 데이터셋

| 메트릭 | 값 |
|--------|-----|
| 공정성 점수 | 0.85 |
| 투명성 점수 | 0.78 |
| 종합 점수 | 0.82 |

### COMPAS 데이터셋

| 메트릭 | 값 |
|--------|-----|
| 공정성 점수 | 0.88 |
| 투명성 점수 | 0.75 |
| 종합 점수 | 0.81 |

---

## 🔗 관련 자료

- [튜토리얼 1: Responsible AI 평가 시작하기](../responsible_ai_automation/docs/tutorial_01_evaluation.md)
- [통합 사용 가이드](INTEGRATION_GUIDE.md)
- [API 레퍼런스](../responsible_ai_automation/docs/api_reference.md)

---

**Last Updated**: 2026-01-07

