"""
공정성(Fairness) 평가 모듈
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from fairlearn.metrics import (
    demographic_parity_difference,
    equalized_odds_difference,
    equal_opportunity_difference,
)


class FairnessEvaluator:
    """공정성 평가 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 평가 설정 딕셔너리
        """
        self.config = config.get("fairness", {})
        self.metrics = self.config.get("metrics", ["demographic_parity"])
        self.threshold = self.config.get("threshold", 0.1)
        self.sensitive_attributes = self.config.get("sensitive_attributes", [])

    def evaluate(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """
        공정성 평가 수행

        Args:
            y_true: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임

        Returns:
            공정성 평가 결과 딕셔너리
        """
        results = {}

        if sensitive_features is None or len(sensitive_features) == 0:
            return {
                "overall_fairness_score": 0.0,
                "metrics": {},
                "is_fair": False,
                "message": "민감한 속성 데이터가 제공되지 않았습니다.",
            }

        # 각 민감한 속성별로 평가
        for attr in self.sensitive_attributes:
            if attr not in sensitive_features.columns:
                continue

            attr_values = sensitive_features[attr]
            attr_results = {}

            # Demographic Parity
            if "demographic_parity" in self.metrics:
                try:
                    dp_diff = demographic_parity_difference(
                        y_true, y_pred, sensitive_features=attr_values
                    )
                    attr_results["demographic_parity"] = float(abs(dp_diff))
                except Exception as e:
                    attr_results["demographic_parity"] = None

            # Equalized Odds
            if "equalized_odds" in self.metrics:
                try:
                    eo_diff = equalized_odds_difference(
                        y_true, y_pred, sensitive_features=attr_values
                    )
                    attr_results["equalized_odds"] = float(abs(eo_diff))
                except Exception as e:
                    attr_results["equalized_odds"] = None

            # Equal Opportunity
            if "equal_opportunity" in self.metrics:
                try:
                    eopp_diff = equal_opportunity_difference(
                        y_true, y_pred, sensitive_features=attr_values
                    )
                    attr_results["equal_opportunity"] = float(abs(eopp_diff))
                except Exception as e:
                    attr_results["equal_opportunity"] = None

            results[attr] = attr_results

        # 전체 공정성 점수 계산 (임계값 기준)
        overall_score = self._calculate_overall_score(results)
        is_fair = overall_score >= (1.0 - self.threshold)

        return {
            "overall_fairness_score": overall_score,
            "metrics": results,
            "is_fair": is_fair,
            "threshold": self.threshold,
        }

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """
        전체 공정성 점수 계산

        Args:
            results: 속성별 평가 결과

        Returns:
            전체 공정성 점수 (0.0 ~ 1.0)
        """
        if not results:
            return 0.0

        scores = []
        for attr_results in results.values():
            for metric_name, metric_value in attr_results.items():
                if metric_value is not None:
                    # 차이가 작을수록 높은 점수 (1.0 - normalized_diff)
                    normalized_score = max(0.0, 1.0 - metric_value / self.threshold)
                    scores.append(min(1.0, normalized_score))

        return float(np.mean(scores)) if scores else 0.0

