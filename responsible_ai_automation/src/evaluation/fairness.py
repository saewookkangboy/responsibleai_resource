"""
공정성(Fairness) 평가 모듈
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.metrics import confusion_matrix
from fairlearn.metrics import (
    demographic_parity_difference,
    equalized_odds_difference,
    equal_opportunity_difference,
)


class FairnessEvaluator:
    """AI 모델의 공정성을 평가하는 클래스"""
    
    def __init__(self, sensitive_attributes: List[str], threshold: float = 0.1):
        """
        Args:
            sensitive_attributes: 민감한 속성 리스트 (예: ['gender', 'race'])
            threshold: 허용 가능한 차이 임계값
        """
        self.sensitive_attributes = sensitive_attributes
        self.threshold = threshold
    
    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: pd.DataFrame,
    ) -> Dict[str, float]:
        """
        공정성 지표를 평가합니다.
        
        Args:
            y_true: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임
        
        Returns:
            공정성 지표 딕셔너리
        """
        results = {}
        
        for attr in self.sensitive_attributes:
            if attr not in sensitive_features.columns:
                continue
            
            # Demographic Parity (인구 통계적 평등)
            dp_diff = demographic_parity_difference(
                y_true, y_pred, sensitive_features=sensitive_features[attr]
            )
            results[f"{attr}_demographic_parity"] = abs(dp_diff)
            
            # Equalized Odds (균등화된 확률)
            eo_diff = equalized_odds_difference(
                y_true, y_pred, sensitive_features=sensitive_features[attr]
            )
            results[f"{attr}_equalized_odds"] = abs(eo_diff)
            
            # Equal Opportunity (균등 기회)
            eopp_diff = equal_opportunity_difference(
                y_true, y_pred, sensitive_features=sensitive_features[attr]
            )
            results[f"{attr}_equal_opportunity"] = abs(eopp_diff)
        
        # 전체 공정성 점수 계산 (임계값 기준)
        overall_score = self._calculate_overall_score(results)
        results["overall_fairness_score"] = overall_score
        results["is_fair"] = overall_score >= (1.0 - self.threshold)
        
        return results
    
    def _calculate_overall_score(self, metrics: Dict[str, float]) -> float:
        """전체 공정성 점수를 계산합니다."""
        if not metrics:
            return 0.0
        
        # 각 지표를 0-1 범위로 정규화 (임계값 기준)
        normalized_scores = []
        for key, value in metrics.items():
            if key == "overall_fairness_score" or key == "is_fair":
                continue
            # 값이 낮을수록 공정함 (0에 가까울수록 좋음)
            normalized = max(0, 1 - (value / self.threshold))
            normalized_scores.append(normalized)
        
        return np.mean(normalized_scores) if normalized_scores else 0.0

