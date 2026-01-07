"""
강화 학습 에이전트 모듈
"""

from typing import Dict, Any, Optional
from stable_baselines3 import PPO, SAC, TD3, A2C
from stable_baselines3.common.callbacks import BaseCallback

from .environment import RLIEnvironment
from .reward import RewardCalculator


class RLAIAgent:
    """Responsible AI 강화 학습 에이전트"""

    SUPPORTED_ALGORITHMS = ["PPO", "SAC", "TD3", "A2C"]

    def __init__(
        self,
        env: RLIEnvironment,
        algorithm: str = "PPO",
        config: Optional[Dict[str, Any]] = None,
    ):
        """
        Args:
            env: 강화 학습 환경
            algorithm: 사용할 알고리즘 (PPO, SAC, TD3, A2C)
            config: 에이전트 설정
        """
        self.env = env
        self.algorithm = algorithm.upper()
        self.config = config or {}

        if self.algorithm not in self.SUPPORTED_ALGORITHMS:
            raise ValueError(
                f"지원하지 않는 알고리즘: {algorithm}. "
                f"지원 알고리즘: {', '.join(self.SUPPORTED_ALGORITHMS)}"
            )

        # 알고리즘별 에이전트 초기화
        rl_config = self.config.get("reinforcement_learning", {})
        learning_rate = rl_config.get("learning_rate", 3e-4)
        batch_size = rl_config.get("batch_size", 64)
        buffer_size = rl_config.get("buffer_size", 100000)
        gamma = rl_config.get("gamma", 0.99)
        tau = rl_config.get("tau", 0.005)

        if self.algorithm == "PPO":
            self.agent = PPO(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                batch_size=batch_size,
                verbose=1,
            )
        elif self.algorithm == "SAC":
            self.agent = SAC(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                buffer_size=buffer_size,
                gamma=gamma,
                tau=tau,
                verbose=1,
            )
        elif self.algorithm == "TD3":
            self.agent = TD3(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                buffer_size=buffer_size,
                gamma=gamma,
                tau=tau,
                verbose=1,
            )
        elif self.algorithm == "A2C":
            self.agent = A2C(
                "MlpPolicy",
                env,
                learning_rate=learning_rate,
                gamma=gamma,
                verbose=1,
            )

    @classmethod
    def recommend_algorithm(
        cls, problem_type: str, action_space_type: str = "continuous"
    ) -> str:
        """
        문제 유형에 따라 최적 알고리즘 추천

        Args:
            problem_type: 문제 유형 ("stable", "fast", "sample_efficient")
            action_space_type: 액션 공간 타입 ("continuous", "discrete")

        Returns:
            추천 알고리즘
        """
        if action_space_type == "continuous":
            if problem_type == "stable":
                return "SAC"
            elif problem_type == "fast":
                return "TD3"
            else:
                return "PPO"
        else:
            return "PPO" if problem_type == "stable" else "A2C"

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
        if self.algorithm == "PPO":
            self.agent = PPO.load(path, env=self.env)
        elif self.algorithm == "SAC":
            self.agent = SAC.load(path, env=self.env)
        elif self.algorithm == "TD3":
            self.agent = TD3.load(path, env=self.env)
        elif self.algorithm == "A2C":
            self.agent = A2C.load(path, env=self.env)

