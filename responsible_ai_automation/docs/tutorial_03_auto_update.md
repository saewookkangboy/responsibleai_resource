# 튜토리얼 3: 자동 업데이트 시스템 설정

이 튜토리얼에서는 자동 업데이트 시스템을 설정하고 사용하는 방법을 학습합니다.

## 목표

- 자동 업데이트 조건 설정
- 모델 업데이트 수행
- 롤백 메커니즘 이해

## 단계 1: 설정 파일 구성

`config.yaml`에 자동 업데이트 설정 추가:

```yaml
auto_update:
  enabled: true
  check_interval: 3600  # 1시간마다 확인
  conditions:
    performance_degradation:
      threshold: 0.05  # 5% 이상 성능 저하 시 업데이트
    ethics_threshold_breach:
      threshold: 0.1  # 윤리 지표가 10% 이상 낮을 때
    distribution_shift:
      threshold: 0.2  # 데이터 분포가 20% 이상 변화했을 때
  rollback:
    enabled: true
    performance_threshold: 0.95  # 이전 성능의 95% 미만이면 롤백
    max_rollback_attempts: 3
```

## 단계 2: 업데이트 조건 확인

```python
from main import ResponsibleAIAutomationSystem

system = ResponsibleAIAutomationSystem("config.yaml")

# 업데이트 조건 확인
should_update = system.check_update_conditions()

if should_update:
    print("업데이트가 필요합니다.")
else:
    print("업데이트가 필요하지 않습니다.")
```

## 단계 3: 수동 업데이트 수행

```python
# 모델 업데이트 수행
system.perform_update()

# 또는 새로운 데이터로 업데이트
new_X = np.random.rand(200, 10)
new_y = np.random.randint(0, 2, 200)
system.perform_update(new_X, new_y, sensitive_features)
```

## 단계 4: 자동 모니터링 및 업데이트

```python
# 지속적인 모니터링 시작 (자동 업데이트 포함)
system.run_continuous_monitoring(X, y, sensitive_features)
```

## 단계 5: 롤백 수행

롤백은 자동으로 수행되지만, 수동으로도 가능합니다:

```python
# 롤백 필요 여부 확인
current_metrics = system.evaluate(X, y, y_pred, sensitive_features)
previous_metrics = system.previous_metrics

if system.rollback_manager.should_rollback(current_metrics, previous_metrics):
    # 롤백 수행
    rollback_result = system.rollback_manager.rollback()
    if rollback_result:
        system.model = rollback_result["model"]
        print("롤백 완료")
```

## 다음 단계

- [튜토리얼 4: 모니터링 대시보드 사용](./tutorial_04_monitoring.md)
- [API 레퍼런스](./api_reference.md)

