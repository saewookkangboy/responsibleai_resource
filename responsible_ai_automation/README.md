# Responsible AI 자동화 시스템

AI 윤리와 Responsible AI 원칙을 자동으로 학습, 최적화, 적용하는 강화 학습 기반 시스템입니다.

> **🆕 v0.2.0 업데이트**: [Microsoft Responsible AI Toolbox](https://github.com/microsoft/responsible-ai-toolbox) 스타일의 새로운 분석 컴포넌트가 추가되었습니다!

## 🌟 주요 기능

### 1. 종합적인 Responsible AI 평가 프레임워크

- **공정성(Fairness)** 평가
  - Demographic Parity, Equalized Odds, Equal Opportunity 등
  - 민감한 속성별 편향 분석
- **투명성(Transparency)** 평가
  - 모델 설명 가능성 점수
  - Feature Importance 분석
  - SHAP 기반 해석
- **책임성(Accountability)** 평가
  - 감사 추적(Audit Trail)
  - 의사결정 로깅
  - 오류 추적
- **프라이버시(Privacy)** 평가
  - Differential Privacy 측정
  - 데이터 익명화 레벨 검증
  - 접근 제어 검사
- **견고성(Robustness)** 평가
  - 적대적 공격 저항성
  - 분포 외 데이터 감지

### 🆕 2. Microsoft RAI Toolbox 스타일 컴포넌트

[Microsoft Responsible AI Toolbox](https://github.com/microsoft/responsible-ai-toolbox)를 참고하여 구현된 고급 분석 기능:

- **Error Analysis** - 모델 오류 분석 및 코호트 식별
  - 오류 트리 시각화
  - 오류율이 높은 데이터 코호트 자동 식별
  - 특성별 오류율 분석
  
- **Counterfactual Analysis** - 반사실적 설명 (DiCE 기반)
  - "무엇이 달랐다면 결과가 바뀌었을까?" 질문에 답변
  - 최소 변경 시나리오 제시
  - 실행 가능한 권장 사항 제공
  
- **Causal Analysis** - 인과 관계 분석 (EconML 기반)
  - Average Treatment Effect (ATE) 추정
  - What-If 시나리오 분석
  - 정책 효과 평가
  
- **Data Balance** - 데이터 균형 분석
  - 특성별 분포 분석
  - 레이블 불균형 감지
  - 민감한 속성별 공정성 평가
  
- **Responsible AI Dashboard** - 통합 분석 대시보드
  - 모든 분석 컴포넌트 통합
  - 종합 리포트 생성
  - JSON 내보내기 지원

### 3. 강화 학습 기반 자동 최적화

- RL Agent가 AI 모델의 윤리적 성능을 자동으로 최적화
- 다양한 윤리 지표 간 균형 자동 조정
- 지속적인 학습 및 개선을 통한 성능 향상
- PPO 알고리즘 기반 최적화

### 4. 지능형 자동 업데이트 시스템

- 조건 기반 자동 업데이트
  - 성능 저하 감지 시 자동 개선
  - 윤리 지표 임계값 위반 시 최적화
  - 데이터 분포 변화 감지 및 대응
- 성능 임계값 모니터링
- 자동 롤백 메커니즘
- 안전한 업데이트 보장

### 5. 실시간 모니터링 및 알림

- 대시보드를 통한 실시간 평가 지표 추적
- 경고 및 알림 시스템
- TensorBoard 통합
- 커스터마이징 가능한 알림 채널 (Console, Email, Slack 등)

## 📋 요구사항

- Python 3.8 이상
- NumPy, Pandas, Scikit-learn
- PyTorch 2.0 이상
- Stable-Baselines3
- Fairlearn, AIF360
- SHAP

전체 요구사항은 [requirements.txt](requirements.txt)를 참조하세요.

## 🚀 빠른 시작

### 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/responsible-ai-automation.git
cd responsible-ai-automation

# 가상 환경 생성 (권장)
python -m venv venv
source venv/bin/activate  # Windows의 경우: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 기본 사용법

```bash
# 설정 파일 사용하여 실행
python main.py --config config.yaml --mode monitor

# 평가만 수행
python main.py --config config.yaml --mode evaluate

# 강화 학습 수행
python main.py --config config.yaml --mode train

# 수동 업데이트
python main.py --config config.yaml --mode update
```

### 간단한 예제

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
model = RandomForestClassifier(n_estimators=100)
model.fit(X, y)

# 시스템에 모델 등록
system.initialize_model(model, X, y, sensitive_features)

# 평가 수행
y_pred = model.predict(X)
metrics = system.evaluate(X, y, y_pred, sensitive_features)

print(f"Responsible AI 점수: {metrics['overall_responsible_ai_score']:.3f}")
print(f"공정성 점수: {metrics['fairness']['overall_fairness_score']:.3f}")
print(f"투명성 점수: {metrics['transparency']['overall_transparency_score']:.3f}")
```

더 자세한 예제는 `example_usage.py` 파일을 참조하세요.

### 🆕 Microsoft RAI Toolbox 스타일 사용법

```python
from src.dashboard import ResponsibleAIDashboard, DashboardConfig
from src.evaluation import (
    ErrorAnalyzer, 
    CounterfactualAnalyzer, 
    CausalAnalyzer, 
    DataBalanceAnalyzer
)

# Responsible AI Dashboard 생성
dashboard = ResponsibleAIDashboard(
    model=model,
    X_train=X_train,
    y_train=y_train,
    X_test=X_test,
    y_test=y_test,
    task_type="classification",
    sensitive_features=["gender", "race"],
    categorical_features=["gender", "race", "occupation"],
)

# 모든 분석 수행
results = dashboard.compute_all()

# 종합 리포트 생성
report = dashboard.generate_report()
print(report)

# JSON으로 내보내기
dashboard.export_to_json("rai_analysis_results.json")
```

#### Error Analysis 직접 사용

```python
from src.evaluation import ErrorAnalyzer

analyzer = ErrorAnalyzer(max_depth=4, min_samples_leaf=20)
results = analyzer.analyze(
    X=X_test,
    y_true=y_test,
    y_pred=model.predict(X_test),
    feature_names=list(X_test.columns),
)

# 오류 코호트 확인
for cohort in results['cohorts'][:5]:
    print(f"코호트: {cohort['name']}, 오류율: {cohort['error_rate']:.2%}")
```

#### Counterfactual Analysis 직접 사용

```python
from src.evaluation import CounterfactualAnalyzer

cf_analyzer = CounterfactualAnalyzer(num_counterfactuals=5)
cf_analyzer.fit(X_train, categorical_features=['gender', 'race'])

explanation = cf_analyzer.generate_counterfactuals(
    instance=X_test.iloc[0],
    predict_fn=model.predict,
    desired_outcome=[1],
)

print(f"반사실적 예시 수: {len(explanation.counterfactuals)}")
```

## ⚡ 빠른 시작

5분 안에 시작하려면:

```bash
python quick_start.py
```

**자세한 내용**: [빠른 시작 가이드](QUICK_START.md) | [설치 가이드](INSTALL.md) | [성능 최적화](OPTIMIZATION.md)

## 📁 프로젝트 구조

```
responsible_ai_automation/
├── main.py                    # 메인 실행 스크립트
├── quick_start.py             # 빠른 시작 스크립트
├── config.yaml                # 설정 파일
├── requirements.txt           # Python 의존성
├── README.md                  # 프로젝트 문서
└── src/
    ├── __init__.py
    ├── evaluation/           # 평가 프레임워크
    │   ├── __init__.py
    │   ├── fairness.py
    │   ├── transparency.py
    │   ├── accountability.py
    │   ├── privacy.py
    │   ├── robustness.py
    │   ├── comprehensive.py
    │   ├── error_analysis.py      # 🆕 Error Analysis (MS RAI Toolbox)
    │   ├── counterfactual.py      # 🆕 Counterfactual Analysis (DiCE)
    │   ├── causal_analysis.py     # 🆕 Causal Analysis (EconML)
    │   └── data_balance.py        # 🆕 Data Balance Analysis
    ├── dashboard/            # 🆕 RAI Dashboard
    │   ├── __init__.py
    │   └── rai_dashboard.py       # Responsible AI Dashboard
    ├── rl_agent/             # 강화 학습 에이전트
    │   ├── __init__.py
    │   ├── environment.py
    │   ├── agent.py
    │   └── reward.py
    ├── auto_update/          # 자동 업데이트 시스템
    │   ├── __init__.py
    │   ├── conditions.py
    │   ├── updater.py
    │   └── rollback.py
    ├── monitoring/           # 모니터링 시스템
    │   ├── __init__.py
    │   ├── dashboard.py
    │   └── alerts.py
    └── utils/                # 유틸리티
        ├── security.py
        ├── performance.py
        └── ...
```

## ⚙️ 설정

설정 파일(`config.yaml`)을 통해 시스템을 커스터마이징할 수 있습니다.

주요 설정 항목:

- **평가 설정**: 각 Responsible AI 지표의 임계값 및 측정 방법
- **강화 학습 설정**: 알고리즘, 학습률, 배치 크기 등
- **자동 업데이트 설정**: 업데이트 조건 및 롤백 정책
- **모니터링 설정**: 대시보드 포트, 로그 레벨, 알림 채널 등

자세한 설정 옵션은 [docs/configuration.md](docs/configuration.md)를 참조하세요.

## 🔄 자동 업데이트 조건

시스템은 다음 조건에서 자동으로 업데이트를 수행합니다:

1. **성능 저하 감지**: 이전 대비 5% 이상 성능 저하 시
2. **윤리 지표 임계값 위반**: 각 윤리 지표가 설정된 임계값보다 10% 낮을 때
3. **데이터 분포 변화**: 데이터 분포가 20% 이상 변화했을 때
4. **정기 업데이트**: 주간/월간 정기 업데이트

자동 롤백도 지원하여 성능이 이전 버전의 95% 미만으로 떨어지면 자동으로 이전 버전으로 복원합니다.

## 📊 모니터링

시스템은 실시간으로 Responsible AI 지표를 모니터링하고 다음을 제공합니다:

- 실시간 대시보드
- 지표 추이 시각화
- 자동 알림 (콘솔, 이메일, Slack 등)
- 평가 리포트 생성

## 📓 Jupyter Notebook 예제

프로젝트 루트의 `notebooks/` 디렉토리에서 튜토리얼 노트북을 확인하세요:

- **01_responsible_ai_dashboard_tutorial.ipynb** - Responsible AI Dashboard 종합 튜토리얼

## 🙏 감사의 말

이 프로젝트는 다음 오픈 소스 프로젝트들에 기반하고 있습니다:

- [Microsoft Responsible AI Toolbox](https://github.com/microsoft/responsible-ai-toolbox) - Error Analysis, Counterfactual, Causal Analysis 참고
- [Stable-Baselines3](https://github.com/DLR-RM/stable-baselines3)
- [Fairlearn](https://github.com/fairlearn/fairlearn)
- [AIF360](https://github.com/Trusted-AI/AIF360)
- [SHAP](https://github.com/slundberg/shap)
- [DiCE](https://github.com/interpretml/DiCE) - Counterfactual Explanations
- [EconML](https://github.com/microsoft/EconML) - Causal Inference

---

**면책 조항**: 이 도구는 Responsible AI 원칙을 자동으로 평가하고 최적화하는 데 도움을 주지만, 최종적인 AI 시스템의 윤리적 검증은 전문가의 판단이 필요합니다.
