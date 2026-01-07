"""
투명성(Transparency) 평가 모듈
"""

import numpy as np
from typing import Dict, Any, Optional
import shap
from sklearn.inspection import permutation_importance


class TransparencyEvaluator:
    """투명성 평가 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 평가 설정 딕셔너리
        """
        self.config = config.get("transparency", {})
        self.metrics = self.config.get("metrics", ["explainability_score"])
        self.threshold = self.config.get("threshold", 0.7)

    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        투명성 평가 수행

        Args:
            model: 학습된 모델
            X: 입력 데이터
            y: 타겟 레이블 (선택적)

        Returns:
            투명성 평가 결과 딕셔너리
        """
        results = {}

        # Explainability Score (SHAP 기반)
        if "explainability_score" in self.metrics:
            try:
                explainer = shap.TreeExplainer(model)
                shap_values = explainer.shap_values(X[:100])  # 샘플링하여 계산
                if isinstance(shap_values, list):
                    shap_values = shap_values[0]
                explainability = float(np.mean(np.abs(shap_values)))
                # 정규화 (0~1 범위)
                results["explainability_score"] = min(1.0, explainability / 10.0)
            except Exception:
                # SHAP이 지원되지 않는 모델의 경우 대체 방법 사용
                results["explainability_score"] = 0.5

        # Model Complexity
        if "model_complexity" in self.metrics:
            try:
                complexity = self._calculate_complexity(model)
                # 복잡도가 낮을수록 높은 점수
                results["model_complexity"] = max(0.0, 1.0 - complexity)
            except Exception:
                results["model_complexity"] = 0.5

        # Feature Importance
        if "feature_importance" in self.metrics and y is not None:
            try:
                perm_importance = permutation_importance(
                    model, X, y, n_repeats=10, random_state=42, n_jobs=-1
                )
                importance_score = float(
                    np.mean(perm_importance.importances_mean) / np.max(perm_importance.importances_mean)
                )
                results["feature_importance"] = min(1.0, importance_score)
            except Exception:
                results["feature_importance"] = 0.5

        # 전체 투명성 점수 계산
        overall_score = float(np.mean(list(results.values()))) if results else 0.0
        is_transparent = overall_score >= self.threshold

        return {
            "overall_transparency_score": overall_score,
            "metrics": results,
            "is_transparent": is_transparent,
            "threshold": self.threshold,
        }

    def _calculate_complexity(self, model: Any) -> float:
        """
        모델 복잡도 계산

        Args:
            model: 학습된 모델

        Returns:
            복잡도 점수 (0.0 ~ 1.0)
        """
        try:
            # 모델 타입에 따라 복잡도 계산
            if hasattr(model, "n_estimators"):
                # Random Forest, Gradient Boosting 등
                complexity = model.n_estimators * 0.01
            elif hasattr(model, "n_layers"):
                # Neural Network
                complexity = model.n_layers * 0.1
            elif hasattr(model, "n_support_"):
                # SVM
                complexity = len(model.n_support_) * 0.01
            else:
                complexity = 0.5

            return min(1.0, complexity)
        except Exception:
            return 0.5

