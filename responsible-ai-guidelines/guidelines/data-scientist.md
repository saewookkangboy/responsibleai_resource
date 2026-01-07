# 데이터 사이언티스트를 위한 AI 윤리 및 Responsible AI 가이드라인

## 개요

이 가이드라인은 데이터 사이언티스트가 AI 모델 개발 과정에서 윤리적 원칙을 준수하도록 돕는 실무 지침을 제공합니다.

## 핵심 원칙

### 1. 데이터 수집 및 관리 (Data Collection & Management)

**실행 사항:**
- 데이터 출처의 합법성 및 윤리성 확인
- 데이터 수집 동의 및 개인정보 보호 고려
- 데이터 품질 및 편향 검증

**체크리스트:**
- [ ] 데이터 수집 목적 및 사용 범위 명확히 정의
- [ ] 데이터 출처의 신뢰성 및 합법성 확인
- [ ] 개인정보 보호법 준수 (GDPR, 개인정보보호법 등)
- [ ] 데이터 수집 시 사용자 동의 확인
- [ ] 데이터셋의 대표성 및 다양성 검증
- [ ] 데이터 품질 메트릭 정의 및 측정

### 2. 데이터 편향 검증 및 완화 (Bias Detection & Mitigation)

**실행 사항:**
- 데이터셋 내 편향 식별
- 다양한 그룹의 대표성 확인
- 편향 완화 기법 적용

**체크리스트:**
- [ ] 데이터셋의 인구통계학적 분포 분석
- [ ] 보호 특성(성별, 인종, 연령 등)별 데이터 분포 확인
- [ ] 과소/과대 표현된 그룹 식별
- [ ] 편향 완화 기법 적용 (재샘플링, 가중치 조정 등)
- [ ] 편향 검증 결과 문서화

### 3. 모델 선택 및 학습 (Model Selection & Training)

**실행 사항:**
- 공정성과 성능의 균형 고려
- 설명 가능한 모델 우선 고려
- 하이퍼파라미터 튜닝 시 공정성 메트릭 포함

**체크리스트:**
- [ ] 모델 선택 시 공정성과 성능 모두 고려
- [ ] 설명 가능한 모델(예: 선형 모델, 의사결정 트리) 우선 검토
- [ ] 교차 검증 시 그룹별 성능 측정
- [ ] 하이퍼파라미터 튜닝에 공정성 메트릭 포함
- [ ] 모델 학습 과정 및 결과 문서화

### 4. 모델 평가 및 검증 (Model Evaluation & Validation)

**실행 사항:**
- 다양한 메트릭으로 모델 평가
- 그룹별 성능 분석
- 엣지 케이스 및 예외 상황 테스트

**체크리스트:**
- [ ] 정확도 외에 공정성, 재현율, F1 스코어 등 다양한 메트릭 사용
- [ ] 보호 특성별 성능 분석
- [ ] 혼동 행렬(Confusion Matrix) 그룹별 분석
- [ ] ROC 곡선 및 PR 곡선 그룹별 비교
- [ ] 엣지 케이스 및 이상치에 대한 모델 동작 검증
- [ ] 모델 예측 신뢰도 분석

### 5. 모델 설명 가능성 (Model Explainability)

**실행 사항:**
- 모델 예측의 주요 요인 분석
- SHAP, LIME 등 설명 도구 활용
- 이해하기 쉬운 시각화 제공

**체크리스트:**
- [ ] 모델 예측에 영향을 미치는 주요 특성 식별
- [ ] SHAP 값 또는 LIME을 통한 예측 설명 생성
- [ ] 특성 중요도 시각화
- [ ] 예측 설명을 비기술자도 이해할 수 있도록 문서화
- [ ] 모델 설명 결과를 정기적으로 검토

### 6. 데이터 프라이버시 (Data Privacy)

**실행 사항:**
- 개인정보 식별 및 보호
- 데이터 익명화 및 마스킹
- 차등 프라이버시 기법 고려

**체크리스트:**
- [ ] 데이터셋 내 PII(개인식별정보) 식별
- [ ] 필요 시 데이터 익명화 또는 마스킹 적용
- [ ] 민감한 특성의 필요성 재검토
- [ ] 차등 프라이버시 기법 적용 검토
- [ ] 데이터 접근 권한 최소화
- [ ] 데이터 보관 기간 및 삭제 정책 준수

## 실험 단계별 체크리스트

### 탐색적 데이터 분석 (EDA)
- [ ] 데이터 출처 및 수집 방법 검토
- [ ] 데이터 품질 및 완전성 확인
- [ ] 인구통계학적 분포 분석
- [ ] 잠재적 편향 요소 식별
- [ ] 이상치 및 결측치 처리 계획 수립

### 특성 엔지니어링
- [ ] 특성 선택 시 공정성 고려
- [ ] 프록시 변수(proxy variable) 사용 지양
- [ ] 특성 인코딩 시 편향 도입 방지
- [ ] 특성 중요도 분석

### 모델 학습
- [ ] 학습/검증/테스트 세트 분할 시 그룹 균형 고려
- [ ] 공정성 메트릭을 포함한 평가 지표 정의
- [ ] 그룹별 성능 모니터링
- [ ] 하이퍼파라미터 튜닝 시 공정성 고려

### 모델 평가
- [ ] 다양한 평가 메트릭 사용
- [ ] 그룹별 성능 분석 및 비교
- [ ] 모델 설명 가능성 검증
- [ ] 엣지 케이스 테스트

### 모델 배포 준비
- [ ] 모델 성능 및 공정성 결과 문서화
- [ ] 모델 제한사항 및 가정 명시
- [ ] 모니터링 계획 수립
- [ ] 롤백 기준 정의

## 코드 예시

### 편향 검증 예시

```python
import pandas as pd
import numpy as np
from sklearn.metrics import accuracy_score, confusion_matrix

def analyze_dataset_bias(df, target_col, sensitive_col):
    """
    데이터셋 편향 분석
    """
    results = {}
    
    # 그룹별 분포 확인
    group_dist = df[sensitive_col].value_counts(normalize=True)
    print("그룹별 분포:")
    print(group_dist)
    
    # 그룹별 타겟 분포 확인
    for group in df[sensitive_col].unique():
        group_data = df[df[sensitive_col] == group]
        target_dist = group_data[target_col].value_counts(normalize=True)
        results[group] = {
            'size': len(group_data),
            'target_distribution': target_dist.to_dict()
        }
    
    return results

def evaluate_fairness_metrics(y_true, y_pred, sensitive_attr):
    """
    공정성 메트릭 평가
    """
    groups = np.unique(sensitive_attr)
    metrics = {}
    
    for group in groups:
        mask = sensitive_attr == group
        y_true_group = y_true[mask]
        y_pred_group = y_pred[mask]
        
        tn, fp, fn, tp = confusion_matrix(y_true_group, y_pred_group).ravel()
        
        metrics[group] = {
            'accuracy': accuracy_score(y_true_group, y_pred_group),
            'tpr': tp / (tp + fn) if (tp + fn) > 0 else 0,  # True Positive Rate
            'fpr': fp / (fp + tn) if (fp + tn) > 0 else 0,  # False Positive Rate
            'tnr': tn / (tn + fp) if (tn + fp) > 0 else 0,  # True Negative Rate
            'fnr': fn / (fn + tp) if (fn + tp) > 0 else 0   # False Negative Rate
        }
    
    # 그룹 간 차이 계산
    tprs = [m['tpr'] for m in metrics.values()]
    fprs = [m['fpr'] for m in metrics.values()]
    
    print(f"TPR 차이: {max(tprs) - min(tprs):.4f}")
    print(f"FPR 차이: {max(fprs) - min(fprs):.4f}")
    
    return metrics
```

### SHAP를 이용한 설명 가능성 예시

```python
import shap
import pandas as pd

def explain_model_predictions(model, X, sample_size=100):
    """
    SHAP를 이용한 모델 예측 설명
    """
    # 샘플링 (대용량 데이터의 경우)
    if len(X) > sample_size:
        X_sample = X.sample(n=sample_size, random_state=42)
    else:
        X_sample = X
    
    # SHAP explainer 생성
    explainer = shap.TreeExplainer(model)  # Tree 모델의 경우
    # explainer = shap.KernelExplainer(model.predict, X_sample)  # 일반 모델의 경우
    
    # SHAP 값 계산
    shap_values = explainer.shap_values(X_sample)
    
    # 요약 플롯
    shap.summary_plot(shap_values, X_sample)
    
    # 특성 중요도
    feature_importance = pd.DataFrame({
        'feature': X_sample.columns,
        'importance': np.abs(shap_values).mean(0)
    }).sort_values('importance', ascending=False)
    
    return shap_values, feature_importance
```

## 리소스 및 도구

- **편향 검증**: [Fairlearn](https://fairlearn.org/), [Aequitas](https://github.com/dssg/aequitas)
- **설명 가능성**: [SHAP](https://github.com/slundberg/shap), [LIME](https://github.com/marcotcr/lime)
- **프라이버시**: [TensorFlow Privacy](https://github.com/tensorflow/privacy), [PySyft](https://github.com/OpenMined/PySyft)
- **데이터 품질**: [Great Expectations](https://greatexpectations.io/)

## 연락처

AI 윤리 관련 문의사항이 있으시면 다음으로 연락하세요:
- AI 윤리 위원회: ethics@company.com
- 데이터 거버넌스 팀: data-governance@company.com

