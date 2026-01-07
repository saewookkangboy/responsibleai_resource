"""
종합 평가 모듈
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .fairness import FairnessEvaluator
from .transparency import TransparencyEvaluator
from .accountability import AccountabilityEvaluator
from .privacy import PrivacyEvaluator
from .robustness import RobustnessEvaluator


class ComprehensiveEvaluator:
    """모든 Responsible AI 지표를 종합적으로 평가하는 클래스"""
    
    def __init__(self, config: dict):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        
        # 각 평가자 초기화
        eval_config = config.get("evaluation", {})
        
        self.fairness_evaluator = FairnessEvaluator(
            sensitive_attributes=eval_config.get("fairness", {}).get("sensitive_attributes", []),
            threshold=eval_config.get("fairness", {}).get("threshold", 0.1),
        )
        
        self.transparency_evaluator = TransparencyEvaluator(
            threshold=eval_config.get("transparency", {}).get("threshold", 0.7),
        )
        
        self.accountability_evaluator = AccountabilityEvaluator()
        
        self.privacy_evaluator = PrivacyEvaluator(
            threshold=eval_config.get("privacy", {}).get("threshold", 0.8),
        )
        
        self.robustness_evaluator = RobustnessEvaluator(
            threshold=eval_config.get("robustness", {}).get("threshold", 0.75),
        )
    
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
        모든 Responsible AI 지표를 종합적으로 평가합니다.
        
        Args:
            model: 평가할 모델
            X: 입력 데이터
            y: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임
            **kwargs: 추가 평가 파라미터
        
        Returns:
            종합 평가 결과 딕셔너리
        """
        results = {}
        
        # 1. 공정성 평가
        if sensitive_features is not None:
            fairness_results = self.fairness_evaluator.evaluate(
                y, y_pred, sensitive_features
            )
            results["fairness"] = fairness_results
        else:
            results["fairness"] = {"overall_fairness_score": 0.5, "is_fair": False}
        
        # 2. 투명성 평가
        transparency_results = self.transparency_evaluator.evaluate(
            model, X, feature_names=kwargs.get("feature_names")
        )
        results["transparency"] = transparency_results
        
        # 3. 책임성 평가
        accountability_results = self.accountability_evaluator.evaluate()
        results["accountability"] = accountability_results
        
        # 4. 프라이버시 평가
        privacy_results = self.privacy_evaluator.evaluate(
            model,
            X,
            differential_privacy_epsilon=kwargs.get("differential_privacy_epsilon"),
            data_anonymization_level=kwargs.get("data_anonymization_level"),
            access_control_enabled=kwargs.get("access_control_enabled", True),
        )
        results["privacy"] = privacy_results
        
        # 5. 견고성 평가
        robustness_results = self.robustness_evaluator.evaluate(
            model, X, y, adversarial_perturbation=kwargs.get("adversarial_perturbation", 0.01)
        )
        results["robustness"] = robustness_results
        
        # 종합 점수 계산
        overall_score = self._calculate_overall_score(results)
        results["overall_responsible_ai_score"] = overall_score
        results["is_responsible"] = overall_score >= 0.75
        
        return results
    
    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """종합 Responsible AI 점수를 계산합니다."""
        weights = {
            "fairness": 0.25,
            "transparency": 0.20,
            "accountability": 0.15,
            "privacy": 0.20,
            "robustness": 0.20,
        }
        
        score = 0.0
        for category, weight in weights.items():
            if category in results:
                category_score = results[category].get(
                    f"overall_{category}_score", 0.5
                )
                score += category_score * weight
        
        return score

