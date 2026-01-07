# 튜토리얼 4: 모니터링 대시보드 사용

이 튜토리얼에서는 모니터링 대시보드를 사용하여 Responsible AI 지표를 추적하는 방법을 학습합니다.

## 목표

- 모니터링 대시보드 시작
- 실시간 메트릭 추적
- 알림 설정

## 단계 1: 대시보드 시작

```python
from main import ResponsibleAIAutomationSystem

system = ResponsibleAIAutomationSystem("config.yaml")

# 대시보드 시작
system.dashboard.start_dashboard()
```

또는 명령줄에서:

```bash
python main.py --config config.yaml --mode monitor
```

## 단계 2: 메트릭 로깅

```python
# 평가 수행 시 자동으로 메트릭이 로깅됩니다
metrics = system.evaluate(X, y, y_pred, sensitive_features)

# 또는 수동으로 로깅
system.dashboard.log_metrics(metrics)
```

## 단계 3: 알림 설정

`config.yaml`에 알림 설정 추가:

```yaml
monitoring:
  alerts:
    enabled: true
    channels:
      - type: "console"
      - type: "email"
        settings:
          smtp_server: "smtp.gmail.com"
          smtp_port: 587
          from_email: "your-email@gmail.com"
          to_email: "recipient@gmail.com"
      - type: "slack"
        settings:
          webhook_url: "https://hooks.slack.com/services/YOUR/WEBHOOK/URL"
    thresholds:
      overall_responsible_ai_score: 0.75
      fairness_score: 0.7
      transparency_score: 0.7
```

## 단계 4: 알림 확인

```python
# 임계값 위반 확인
violations = system.alert_manager.check_thresholds(metrics)

if violations:
    print(f"임계값 위반: {violations}")
    # 알림이 자동으로 전송됩니다
```

## 다음 단계

- [튜토리얼 5: 프로덕션 배포](./tutorial_05_deployment.md)
- [API 레퍼런스](./api_reference.md)

