"""
강화 학습 에이전트
"""

import numpy as np
from typing import Dict, Any, Optional
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.monitor import Monitor
import os

from .environment import ResponsibleAIEnv


class TrainingCallback(BaseCallback):
    """학습 진행 상황을 추적하는 콜백"""
    
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_rewards = []
        self.episode_lengths = []
    
    def _on_step(self) -> bool:
        return True
    
    def _on_rollout_end(self) -> None:
        if len(self.episode_rewards) > 0:
            mean_reward = np.mean(self.episode_rewards[-100:])
            if self.verbose > 0:
                print(f"Mean reward: {mean_reward:.3f}")


class RLAIAgent:
    """Responsible AI 최적화를 위한 강화 학습 에이전트"""
    
    def __init__(
        self,
        env: ResponsibleAIEnv,
        algorithm: str = "PPO",
        config: Optional[Dict] = None,
        model_path: Optional[str] = None,
    ):
        """
        Args:
            env: 강화 학습 환경
            algorithm: 사용할 알고리즘 (PPO, SAC, TD3 등)
            config: 설정 딕셔너리
            model_path: 저장된 모델 경로 (로드용)
        """
        self.env = env
        self.algorithm = algorithm
        self.config = config or {}
        self.model_path = model_path
        
        # 환경을 Monitor로 래핑 (통계 수집용)
        log_dir = self.config.get("log_dir", "./logs")
        os.makedirs(log_dir, exist_ok=True)
        self.env = Monitor(self.env, log_dir)
        
        # 모델 초기화 또는 로드
        if model_path and os.path.exists(model_path):
            self.model = self._load_model(model_path)
        else:
            self.model = self._create_model()
    
    def _create_model(self):
        """새 모델을 생성합니다."""
        rl_config = self.config.get("reinforcement_learning", {})
        
        if self.algorithm == "PPO":
            return PPO(
                "MlpPolicy",
                self.env,
                learning_rate=rl_config.get("learning_rate", 3e-4),
                n_steps=rl_config.get("n_steps", 2048),
                batch_size=rl_config.get("batch_size", 64),
                gamma=rl_config.get("gamma", 0.99),
                verbose=1,
                tensorboard_log=self.config.get("tensorboard_log", "./tensorboard_logs"),
            )
        else:
            raise ValueError(f"지원하지 않는 알고리즘: {self.algorithm}")
    
    def _load_model(self, model_path: str):
        """저장된 모델을 로드합니다."""
        if self.algorithm == "PPO":
            return PPO.load(model_path, env=self.env)
        else:
            raise ValueError(f"지원하지 않는 알고리즘: {self.algorithm}")
    
    def train(self, total_timesteps: int = 100000, callback: Optional[BaseCallback] = None):
        """에이전트를 학습시킵니다."""
        if callback is None:
            callback = TrainingCallback(verbose=1)
        
        self.model.learn(
            total_timesteps=total_timesteps,
            callback=callback,
            progress_bar=True,
        )
    
    def predict(self, observation: np.ndarray, deterministic: bool = True) -> np.ndarray:
        """주어진 관측에 대한 행동을 예측합니다."""
        action, _ = self.model.predict(observation, deterministic=deterministic)
        return action
    
    def save(self, path: str):
        """모델을 저장합니다."""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        self.model.save(path)
        print(f"모델이 저장되었습니다: {path}")
    
    def evaluate(self, n_episodes: int = 10) -> Dict[str, float]:
        """에이전트를 평가합니다."""
        episode_rewards = []
        episode_lengths = []
        
        for _ in range(n_episodes):
            obs, _ = self.env.reset()
            done = False
            episode_reward = 0.0
            episode_length = 0
            
            while not done:
                action, _ = self.model.predict(obs, deterministic=True)
                obs, reward, terminated, truncated, info = self.env.step(action)
                done = terminated or truncated
                episode_reward += reward
                episode_length += 1
            
            episode_rewards.append(episode_reward)
            episode_lengths.append(episode_length)
        
        return {
            "mean_reward": np.mean(episode_rewards),
            "std_reward": np.std(episode_rewards),
            "mean_length": np.mean(episode_lengths),
            "std_length": np.std(episode_lengths),
        }

