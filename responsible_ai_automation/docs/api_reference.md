# API 레퍼런스

Responsible AI Automation 시스템의 주요 API 문서입니다.

## ResponsibleAIAutomationSystem

메인 시스템 클래스로, Responsible AI 평가, 자동 업데이트, 모니터링 기능을 제공합니다.

### 초기화

```python
system = ResponsibleAIAutomationSystem(config_path: str)
```

**파라미터:**
- `config_path` (str): 설정 파일 경로 (YAML 형식)

**예제:**
```python
system = ResponsibleAIAutomationSystem("config.yaml")
```

### 메서드

#### `initialize_model(model, X, y, sensitive_features=None)`

모델을 시스템에 등록하고 초기화합니다.

**파라미터:**
- `model`: 학습된 머신러닝 모델
- `X` (np.ndarray): 입력 데이터
- `y` (np.ndarray): 타겟 레이블
- `sensitive_features` (pd.DataFrame, optional): 민감한 속성 데이터

**예제:**
```python
system.initialize_model(model, X, y, sensitive_features)
```

#### `evaluate(X, y, y_pred, sensitive_features=None) -> Dict[str, Any]`

모델을 Responsible AI 지표로 평가합니다.

**파라미터:**
- `X` (np.ndarray): 입력 데이터
- `y` (np.ndarray): 실제 레이블
- `y_pred` (np.ndarray): 예측 레이블
- `sensitive_features` (pd.DataFrame, optional): 민감한 속성 데이터

**반환값:**
평가 결과 딕셔너리

**예제:**
```python
metrics = system.evaluate(X, y, y_pred, sensitive_features)
print(metrics['overall_responsible_ai_score'])
```

#### `check_update_conditions() -> bool`

업데이트 조건을 확인합니다.

**반환값:**
업데이트 필요 여부 (bool)

#### `perform_update(X, y, sensitive_features=None)`

모델을 업데이트합니다.

**파라미터:**
- `X` (np.ndarray): 입력 데이터
- `y` (np.ndarray): 타겟 레이블
- `sensitive_features` (pd.DataFrame, optional): 민감한 속성 데이터

#### `run_continuous_monitoring(X, y, sensitive_features=None)`

지속적인 모니터링을 시작합니다.

**파라미터:**
- `X` (np.ndarray): 입력 데이터
- `y` (np.ndarray): 타겟 레이블
- `sensitive_features` (pd.DataFrame, optional): 민감한 속성 데이터

## ComprehensiveEvaluator

종합 평가자를 제공하는 클래스입니다.

### 사용법

```python
from src.evaluation.comprehensive import ComprehensiveEvaluator

evaluator = ComprehensiveEvaluator(config)
metrics = evaluator.evaluate(model, X, y, y_pred, sensitive_features)
```

## RLAIAgent

강화 학습 에이전트 클래스입니다.

### 사용법

```python
from src.rl_agent.agent import RLAIAgent

agent = RLAIAgent(env, algorithm="PPO", config=config)
agent.train(total_timesteps=100000)
```

---

더 자세한 API 문서는 코드의 docstring을 참조하세요.

