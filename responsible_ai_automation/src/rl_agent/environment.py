"""
강화 학습 환경 모듈
"""

import numpy as np
import gymnasium as gym
from gymnasium import spaces
from typing import Dict, Any, Optional, Tuple


class RLIEnvironment(gym.Env):
    """Responsible AI 강화 학습 환경"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 환경 설정 딕셔너리
        """
        super().__init__()

        self.config = config
        # 액션 공간: 각 Responsible AI 지표에 대한 조정 값
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(5,), dtype=np.float32
        )  # fairness, transparency, accountability, privacy, robustness

        # 관찰 공간: 현재 Responsible AI 지표 값들
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(5,), dtype=np.float32
        )

        self.current_metrics = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        self.target_metrics = np.array([0.8, 0.8, 0.8, 0.8, 0.8])

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict]:
        """
        환경 초기화

        Args:
            seed: 랜덤 시드
            options: 추가 옵션

        Returns:
            초기 관찰과 정보 딕셔너리
        """
        super().reset(seed=seed)

        self.current_metrics = np.array([0.5, 0.5, 0.5, 0.5, 0.5])
        info = {"metrics": self.current_metrics.copy()}

        return self.current_metrics.astype(np.float32), info

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, bool, Dict]:
        """
        환경 스텝 실행

        Args:
            action: 에이전트 액션

        Returns:
            관찰, 보상, 종료 여부, 잘림 여부, 정보 딕셔너리
        """
        # 액션을 메트릭 조정에 적용
        self.current_metrics = np.clip(
            self.current_metrics + action * 0.1, 0.0, 1.0
        )

        # 보상 계산 (타겟과의 거리 기반)
        reward = -np.mean(np.abs(self.current_metrics - self.target_metrics))

        # 종료 조건: 모든 메트릭이 타겟에 도달
        terminated = np.all(self.current_metrics >= self.target_metrics * 0.95)
        truncated = False

        info = {
            "metrics": self.current_metrics.copy(),
            "reward": float(reward),
        }

        return (
            self.current_metrics.astype(np.float32),
            float(reward),
            terminated,
            truncated,
            info,
        )

