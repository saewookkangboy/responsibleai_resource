# 튜토리얼 2: 강화 학습 기반 최적화

이 튜토리얼에서는 강화 학습을 사용하여 Responsible AI 지표를 자동으로 최적화하는 방법을 학습합니다.

## 목표

- 강화 학습 환경 설정
- RL 에이전트 학습
- 최적화 결과 확인

## 단계 1: 환경 및 에이전트 초기화

```python
from src.rl_agent.environment import RLIEnvironment
from src.rl_agent.agent import RLAIAgent

# 환경 초기화
config = {}
env = RLIEnvironment(config)

# 에이전트 초기화 (PPO 알고리즘 사용)
agent = RLAIAgent(env, algorithm="PPO", config=config)
```

## 단계 2: 에이전트 학습

```python
# 에이전트 학습 (100,000 스텝)
agent.train(total_timesteps=100000)

# 학습된 에이전트 저장
agent.save("models/rl_agent_ppo")
```

## 단계 3: 최적화된 정책 사용

```python
# 환경 초기화
obs, info = env.reset()

# 최적화된 액션 예측
action, _ = agent.predict(obs)

# 환경에 액션 적용
obs, reward, terminated, truncated, info = env.step(action)

print(f"보상: {reward}")
print(f"메트릭: {info['metrics']}")
```

## 단계 4: 알고리즘 선택 가이드

```python
# 문제 유형에 따른 알고리즘 추천
algorithm = RLAIAgent.recommend_algorithm("stable", "continuous")
print(f"추천 알고리즘: {algorithm}")  # "SAC"

algorithm = RLAIAgent.recommend_algorithm("fast", "continuous")
print(f"추천 알고리즘: {algorithm}")  # "TD3"
```

## 다음 단계

- [튜토리얼 3: 자동 업데이트 시스템 설정](./tutorial_03_auto_update.md)
- [API 레퍼런스](./api_reference.md)

