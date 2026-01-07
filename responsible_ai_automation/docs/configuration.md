# 설정 가이드

`config.yaml` 파일을 통한 시스템 설정 방법을 설명합니다.

## 설정 파일 구조

```yaml
# 평가 설정
evaluation:
  fairness:
    metrics: ["demographic_parity", "equalized_odds", "equal_opportunity"]
    threshold: 0.1
    sensitive_attributes: ["gender", "race", "age"]
  
  transparency:
    metrics: ["explainability_score", "model_complexity", "feature_importance"]
    threshold: 0.7
  
  accountability:
    metrics: ["audit_trail", "decision_logging", "error_tracking"]
    enabled: true
  
  privacy:
    metrics: ["differential_privacy", "data_anonymization", "access_control"]
    threshold: 0.8
  
  robustness:
    metrics: ["adversarial_robustness", "out_of_distribution_detection"]
    threshold: 0.75

# 강화 학습 설정
reinforcement_learning:
  algorithm: "PPO"  # PPO, SAC, TD3 등
  learning_rate: 3e-4
  batch_size: 64
  buffer_size: 100000
  gamma: 0.99
  tau: 0.005
  training_steps: 100000
  evaluation_frequency: 1000
  save_frequency: 5000

# 자동 업데이트 설정
auto_update:
  enabled: true
  check_interval: 3600  # 초 단위
  
  conditions:
    performance_degradation:
      threshold: 0.05
      action: "update"
    
    ethics_threshold_breach:
      threshold: 0.1
      action: "update"
    
    distribution_shift:
      threshold: 0.2
      action: "update"
    
    scheduled:
      frequency: "weekly"
      action: "update"
  
  rollback:
    enabled: true
    max_rollback_attempts: 3
    performance_threshold: 0.95

# 모니터링 설정
monitoring:
  enabled: true
  dashboard_port: 8080
  log_level: "INFO"
  metrics_retention_days: 30
  alert_channels:
    - "console"

# 모델 설정
model:
  save_path: "./models"
  checkpoint_frequency: 1000
  max_checkpoints: 10
```

## 주요 설정 설명

### evaluation

Responsible AI 평가 지표 설정입니다.

- **fairness**: 공정성 평가 설정
  - `threshold`: 허용 가능한 차이 임계값
  - `sensitive_attributes`: 민감한 속성 목록

- **transparency**: 투명성 평가 설정
  - `threshold`: 최소 투명성 점수

- **privacy**: 프라이버시 평가 설정
  - `threshold`: 최소 프라이버시 점수

- **robustness**: 견고성 평가 설정
  - `threshold`: 최소 견고성 점수

### reinforcement_learning

강화 학습 알고리즘 설정입니다.

- `algorithm`: 사용할 알고리즘 (PPO, SAC, TD3 등)
- `learning_rate`: 학습률
- `training_steps`: 전체 학습 스텝 수

### auto_update

자동 업데이트 설정입니다.

- `enabled`: 자동 업데이트 활성화 여부
- `check_interval`: 업데이트 조건 체크 간격 (초)
- `conditions`: 업데이트 조건들
- `rollback`: 롤백 설정

### monitoring

모니터링 설정입니다.

- `dashboard_port`: 대시보드 포트 번호
- `log_level`: 로그 레벨 (DEBUG, INFO, WARNING, ERROR)
- `alert_channels`: 알림 채널 목록

---

설정 파일을 수정한 후에는 시스템을 재시작해야 변경사항이 적용됩니다.

