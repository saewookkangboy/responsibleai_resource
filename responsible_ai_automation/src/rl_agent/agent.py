"""
강화 학습 에이전트 모듈
"""

from typing import Dict, Any, Optional
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback

from .environment import RLIEnvironment
from .reward import RewardCalculator


class RLAIAgent:
    """Responsible AI 강화 학습 에이전트"""

    def __init__(
        self,
        env: RLIEnvironment,
        algorithm: str = "PPO",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            env: 강화 학습 환경
            algorithm: 사용할 알고리즘 (PPO, SAC, TD3 등)
            config: 에이전트 설정
        """
        self.env = env
        self.algorithm = algorithm
        self.config = config or {}

        # 알고리즘별 에이전트 초기화
        rl_config = self.config.get("reinforcement_learning", {})
        learning_rate = rl_config.get("learning_rate", 3e-4)

        if algorithm == "PPO":
            self.agent = PPO(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                verbose=1,
            )
        else:
            raise ValueError(f"지원하지 않는 알고리즘: {algorithm}")

    def train(self, total_timesteps: int = 100000, callback: Optional[BaseCallback] = None):
        """
        에이전트 학습

        Args:
            total_timesteps: 총 학습 스텝 수
            callback: 콜백 함수
        """
        self.agent.learn(
            total_timesteps=total_timesteps,
            callback=callback,
        )

    def predict(self, observation):
        """
        관찰에 대한 액션 예측

        Args:
            observation: 현재 관찰

        Returns:
            예측된 액션
        """
        return self.agent.predict(observation)

    def save(self, path: str):
        """
        에이전트 저장

        Args:
            path: 저장 경로
        """
        self.agent.save(path)

    def load(self, path: str):
        """
        에이전트 로드

        Args:
            path: 로드 경로
        """
        self.agent = PPO.load(path, env=self.env)

