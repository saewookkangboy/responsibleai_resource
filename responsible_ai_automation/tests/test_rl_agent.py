"""
강화 학습 에이전트 테스트
"""

import pytest
import numpy as np
from src.rl_agent.environment import RLIEnvironment
from src.rl_agent.agent import RLAIAgent
from src.rl_agent.reward import RewardCalculator


class TestRLIEnvironment:
    """RL 환경 테스트 클래스"""

    def test_environment_reset(self):
        """환경 초기화 테스트"""
        config = {}
        env = RLIEnvironment(config)

        obs, info = env.reset()

        assert isinstance(obs, np.ndarray)
        assert obs.shape == (5,)
        assert "metrics" in info

    def test_environment_step(self):
        """환경 스텝 실행 테스트"""
        config = {}
        env = RLIEnvironment(config)

        obs, _ = env.reset()
        action = np.array([0.1, 0.1, 0.1, 0.1, 0.1])

        obs, reward, terminated, truncated, info = env.step(action)

        assert isinstance(obs, np.ndarray)
        assert isinstance(reward, float)
        assert isinstance(terminated, bool)
        assert isinstance(truncated, bool)
        assert "metrics" in info


class TestRLAIAgent:
    """RL 에이전트 테스트 클래스"""

    def test_agent_initialization_ppo(self):
        """PPO 에이전트 초기화 테스트"""
        config = {}
        env = RLIEnvironment(config)

        agent = RLAIAgent(env, algorithm="PPO", config=config)

        assert agent.algorithm == "PPO"
        assert agent.env == env

    def test_agent_recommend_algorithm(self):
        """알고리즘 추천 테스트"""
        # 연속 액션 공간
        algo = RLAIAgent.recommend_algorithm("stable", "continuous")
        assert algo == "SAC"

        algo = RLAIAgent.recommend_algorithm("fast", "continuous")
        assert algo == "TD3"

        # 이산 액션 공간
        algo = RLAIAgent.recommend_algorithm("stable", "discrete")
        assert algo == "PPO"


class TestRewardCalculator:
    """보상 계산 테스트 클래스"""

    def test_reward_calculation_basic(self):
        """기본 보상 계산 테스트"""
        config = {}
        calculator = RewardCalculator(config)

        metrics = {
            "overall_responsible_ai_score": 0.8,
            "fairness": {"overall_fairness_score": 0.75},
            "transparency": {"overall_transparency_score": 0.7},
        }

        reward = calculator.calculate_reward(metrics)

        assert isinstance(reward, float)
        assert reward > 0

    def test_reward_calculation_with_improvement(self):
        """개선이 있는 경우 보상 계산 테스트"""
        config = {}
        calculator = RewardCalculator(config)

        previous_metrics = {"overall_responsible_ai_score": 0.7}
        current_metrics = {"overall_responsible_ai_score": 0.8}

        reward = calculator.calculate_reward(current_metrics, previous_metrics)

        assert reward > 0.8  # 개선 보너스 포함

