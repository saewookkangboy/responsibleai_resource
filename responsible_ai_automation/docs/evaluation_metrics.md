# 평가 메트릭 설명

Responsible AI Automation 시스템에서 사용하는 평가 메트릭에 대한 설명입니다.

## 공정성 (Fairness) 메트릭

### Demographic Parity
인구 통계학적 패리티를 측정합니다. 민감한 속성 그룹 간의 긍정 예측 비율이 얼마나 유사한지를 평가합니다.

### Equalized Odds
민감한 속성 그룹 간의 True Positive Rate와 False Positive Rate의 차이를 측정합니다.

### Equal Opportunity
민감한 속성 그룹 간의 True Positive Rate의 평등을 측정합니다.

## 투명성 (Transparency) 메트릭

### Explainability Score
모델의 설명 가능성을 측정합니다. SHAP 값과 feature importance를 기반으로 계산됩니다.

### Model Complexity
모델의 복잡도를 측정합니다. 더 단순한 모델일수록 높은 점수를 받습니다.

### Feature Importance
특성 중요도 분석을 통해 모델의 의사결정 과정을 이해할 수 있는 정도를 측정합니다.

## 책임성 (Accountability) 메트릭

### Audit Trail
모델의 의사결정과 변경 이력이 기록되는 정도를 측정합니다.

### Decision Logging
의사결정이 로깅되는 정도를 측정합니다.

### Error Tracking
오류 추적 시스템의 존재와 활용도를 측정합니다.

## 프라이버시 (Privacy) 메트릭

### Differential Privacy
차등 프라이버시 메커니즘의 적용 정도를 측정합니다. Epsilon 값으로 측정됩니다.

### Data Anonymization
데이터 익명화 레벨을 측정합니다.

### Access Control
접근 제어 메커니즘이 적절히 구현되어 있는지 측정합니다.

## 견고성 (Robustness) 메트릭

### Adversarial Robustness
적대적 공격에 대한 저항성을 측정합니다. 적대적 예제에 대한 모델의 성능 저하 정도를 평가합니다.

### Out-of-Distribution Detection
분포 외 데이터를 감지하는 능력을 측정합니다.

## 종합 점수

모든 카테고리별 점수를 가중 평균하여 종합 Responsible AI 점수를 계산합니다.

기본 가중치:
- 공정성: 25%
- 투명성: 20%
- 책임성: 15%
- 프라이버시: 20%
- 견고성: 20%

점수가 0.75 이상이면 "Responsible AI 기준 충족"으로 판단됩니다.

---

각 메트릭에 대한 자세한 계산 방법은 소스 코드의 docstring을 참조하세요.

