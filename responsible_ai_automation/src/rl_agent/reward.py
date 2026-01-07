"""
보상 계산 모듈
"""

import numpy as np
from typing import Dict, Any


class RewardCalculator:
    """Responsible AI 지표를 기반으로 보상을 계산하는 클래스"""
    
    def __init__(self, weights: Dict[str, float] = None):
        """
        Args:
            weights: 각 지표의 가중치 딕셔너리
        """
        self.weights = weights or {
            "fairness": 0.25,
            "transparency": 0.20,
            "accountability": 0.15,
            "privacy": 0.20,
            "robustness": 0.20,
        }
    
    def calculate(
        self,
        current_metrics: Dict[str, Any],
        previous_metrics: Dict[str, Any] = None,
    ) -> float:
        """
        보상을 계산합니다.
        
        Args:
            current_metrics: 현재 평가 지표
            previous_metrics: 이전 평가 지표 (개선량 계산용)
        
        Returns:
            보상 값
        """
        # 기본 보상: 각 지표의 점수 가중 평균
        base_reward = 0.0
        
        for category, weight in self.weights.items():
            if category in current_metrics:
                score = current_metrics[category].get(
                    f"overall_{category}_score", 0.5
                )
                base_reward += score * weight
        
        # 개선 보상: 이전 대비 개선량
        improvement_reward = 0.0
        if previous_metrics is not None:
            for category in self.weights.keys():
                if category in current_metrics and category in previous_metrics:
                    current_score = current_metrics[category].get(
                        f"overall_{category}_score", 0.5
                    )
                    previous_score = previous_metrics[category].get(
                        f"overall_{category}_score", 0.5
                    )
                    improvement = current_score - previous_score
                    improvement_reward += improvement * self.weights[category] * 2  # 개선에 더 큰 가중치
        
        # 임계값 보너스: 각 지표가 임계값을 넘으면 보너스
        threshold_bonus = 0.0
        thresholds = {
            "fairness": 0.9,
            "transparency": 0.7,
            "accountability": 0.7,
            "privacy": 0.8,
            "robustness": 0.75,
        }
        
        for category, threshold in thresholds.items():
            if category in current_metrics:
                score = current_metrics[category].get(
                    f"overall_{category}_score", 0.5
                )
                if score >= threshold:
                    threshold_bonus += 0.1 * self.weights[category]
        
        # 전체 보상
        total_reward = base_reward + improvement_reward + threshold_bonus
        
        # 보상을 -1 ~ 1 범위로 정규화
        total_reward = np.clip(total_reward, -1.0, 1.0)
        
        return float(total_reward)
    
    def calculate_penalty(
        self,
        metrics: Dict[str, Any],
        violation_threshold: float = 0.5,
    ) -> float:
        """
        위반에 대한 페널티를 계산합니다.
        
        Args:
            metrics: 평가 지표
            violation_threshold: 위반 임계값
        
        Returns:
            페널티 값 (음수)
        """
        penalty = 0.0
        
        for category in self.weights.keys():
            if category in metrics:
                score = metrics[category].get(f"overall_{category}_score", 0.5)
                if score < violation_threshold:
                    # 임계값 미만이면 페널티
                    penalty -= (violation_threshold - score) * self.weights[category] * 2
        
        return float(penalty)

