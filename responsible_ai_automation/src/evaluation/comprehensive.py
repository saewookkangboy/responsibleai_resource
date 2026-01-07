"""
종합 평가 모듈
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional

from .fairness import FairnessEvaluator
from .transparency import TransparencyEvaluator
from .accountability import AccountabilityEvaluator
from .privacy import PrivacyEvaluator
from .robustness import RobustnessEvaluator
from .social_impact import SocialImpactEvaluator


class ComprehensiveEvaluator:
    """종합 Responsible AI 평가 클래스"""

    # 기본 가중치
    DEFAULT_WEIGHTS = {
        "fairness": 0.25,
        "transparency": 0.20,
        "accountability": 0.15,
        "privacy": 0.20,
        "robustness": 0.20,
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 평가 설정 딕셔너리
        """
        self.config = config
        self.fairness_evaluator = FairnessEvaluator(config)
        self.transparency_evaluator = TransparencyEvaluator(config)
        self.accountability_evaluator = AccountabilityEvaluator(config)
        self.privacy_evaluator = PrivacyEvaluator(config)
        self.robustness_evaluator = RobustnessEvaluator(config)
        self.social_impact_evaluator = SocialImpactEvaluator(config)

        # 가중치 설정
        self.weights = config.get("weights", self.DEFAULT_WEIGHTS)

    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        종합 Responsible AI 평가 수행

        Args:
            model: 학습된 모델
            X: 입력 데이터
            y: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임
            **kwargs: 추가 파라미터

        Returns:
            종합 평가 결과 딕셔너리
        """
        # 성능 최적화: 데이터 샘플링 (설정된 경우)
        try:
            from ..utils.optimization import optimize_data_for_evaluation
            X_opt, y_opt = optimize_data_for_evaluation(X, y, self.config)
            
            # 샘플링된 경우 y_pred도 조정
            if len(X_opt) < len(X):
                indices = np.random.choice(len(X), len(X_opt), replace=False)
                y_pred = y_pred[indices]
                if sensitive_features is not None:
                    sensitive_features = sensitive_features.iloc[indices].reset_index(drop=True)
                X, y = X_opt, y_opt
        except (ImportError, AttributeError):
            # optimization 모듈이 없는 경우 그대로 진행
            pass
        
        results = {}

        # 공정성 평가
        fairness_results = self.fairness_evaluator.evaluate(y, y_pred, sensitive_features)
        results["fairness"] = fairness_results

        # 투명성 평가
        transparency_results = self.transparency_evaluator.evaluate(model, X, y)
        results["transparency"] = transparency_results

        # 책임성 평가
        accountability_results = self.accountability_evaluator.evaluate()
        results["accountability"] = accountability_results

        # 프라이버시 평가
        privacy_results = self.privacy_evaluator.evaluate(
            X,
            data_anonymization_level=kwargs.get("data_anonymization_level"),
            access_control_enabled=kwargs.get("access_control_enabled", False),
        )
        results["privacy"] = privacy_results

        # 견고성 평가
        robustness_results = self.robustness_evaluator.evaluate(
            model, X, y, X_test=kwargs.get("X_test")
        )
        results["robustness"] = robustness_results

        # 사회적 영향 평가
        social_impact_results = self.social_impact_evaluator.evaluate(
            model, X, y, y_pred, sensitive_features, **kwargs
        )
        results["social_impact"] = social_impact_results

        # 종합 점수 계산
        overall_score = self._calculate_overall_score(results)
        is_responsible = overall_score >= 0.75

        results["overall_responsible_ai_score"] = overall_score
        results["is_responsible"] = is_responsible

        return results

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """
        종합 Responsible AI 점수 계산

        Args:
            results: 카테고리별 평가 결과

        Returns:
            종합 점수 (0.0 ~ 1.0)
        """
        score = 0.0

        # 공정성
        if "fairness" in results:
            fairness_score = results["fairness"].get("overall_fairness_score", 0.0)
            score += self.weights.get("fairness", 0.25) * fairness_score

        # 투명성
        if "transparency" in results:
            transparency_score = results["transparency"].get("overall_transparency_score", 0.0)
            score += self.weights.get("transparency", 0.20) * transparency_score

        # 책임성
        if "accountability" in results:
            accountability_score = results["accountability"].get("overall_accountability_score", 0.0)
            score += self.weights.get("accountability", 0.15) * accountability_score

        # 프라이버시
        if "privacy" in results:
            privacy_score = results["privacy"].get("overall_privacy_score", 0.0)
            score += self.weights.get("privacy", 0.20) * privacy_score

        # 견고성
        if "robustness" in results:
            robustness_score = results["robustness"].get("overall_robustness_score", 0.0)
            score += self.weights.get("robustness", 0.20) * robustness_score

        return float(score)

