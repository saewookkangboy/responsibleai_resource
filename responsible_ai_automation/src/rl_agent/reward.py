"""
보상 계산 모듈
"""

import numpy as np
from typing import Dict, Any, Optional


class RewardCalculator:
    """보상 계산 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 보상 설정 딕셔너리
        """
        self.config = config

    def calculate_reward(
        self, metrics: Dict[str, Any], previous_metrics: Optional[Dict[str, Any]] = None
    ) -> float:
        """
        보상 계산

        Args:
            metrics: 현재 Responsible AI 지표
            previous_metrics: 이전 Responsible AI 지표

        Returns:
            보상 값
        """
        # 전체 Responsible AI 점수 기반 보상
        overall_score = metrics.get("overall_responsible_ai_score", 0.0)

        # 기본 보상: 점수가 높을수록 높은 보상
        reward = overall_score

        # 개선 보상: 이전 대비 개선 시 추가 보상
        if previous_metrics is not None:
            previous_score = previous_metrics.get("overall_responsible_ai_score", 0.0)
            improvement = overall_score - previous_score
            reward += improvement * 2.0  # 개선에 대한 추가 보상

        # 각 카테고리별 임계값 충족 보상
        thresholds = {
            "fairness": 0.7,
            "transparency": 0.7,
            "accountability": 0.7,
            "privacy": 0.8,
            "robustness": 0.75,
        }

        for category, threshold in thresholds.items():
            if category in metrics:
                category_score = metrics[category].get(
                    f"overall_{category}_score", 0.0
                )
                if category_score >= threshold:
                    reward += 0.1  # 임계값 충족 시 추가 보상

        return float(reward)

