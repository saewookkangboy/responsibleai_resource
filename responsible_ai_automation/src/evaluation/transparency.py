"""
투명성(Transparency) 평가 모듈
"""

import numpy as np
from typing import Dict, Optional, Any
import shap


class TransparencyEvaluator:
    """AI 모델의 투명성을 평가하는 클래스"""
    
    def __init__(self, threshold: float = 0.7):
        """
        Args:
            threshold: 최소 투명성 점수
        """
        self.threshold = threshold
    
    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        feature_names: Optional[list] = None,
        model_complexity: Optional[float] = None,
    ) -> Dict[str, float]:
        """
        투명성 지표를 평가합니다.
        
        Args:
            model: 평가할 모델
            X: 입력 데이터
            feature_names: 특성 이름 리스트
            model_complexity: 모델 복잡도 (None이면 자동 계산)
        
        Returns:
            투명성 지표 딕셔너리
        """
        results = {}
        
        # 1. 설명 가능성 점수 (SHAP 값 사용)
        explainability_score = self._calculate_explainability(model, X, feature_names)
        results["explainability_score"] = explainability_score
        
        # 2. 모델 복잡도
        if model_complexity is None:
            model_complexity = self._estimate_model_complexity(model)
        results["model_complexity"] = model_complexity
        # 복잡도가 낮을수록 투명함 (정규화)
        complexity_score = max(0, 1 - min(1, model_complexity / 100))
        results["complexity_score"] = complexity_score
        
        # 3. 특성 중요도 일관성
        feature_importance_score = self._calculate_feature_importance_consistency(
            model, X, feature_names
        )
        results["feature_importance_score"] = feature_importance_score
        
        # 전체 투명성 점수
        overall_score = (
            explainability_score * 0.4
            + complexity_score * 0.3
            + feature_importance_score * 0.3
        )
        results["overall_transparency_score"] = overall_score
        results["is_transparent"] = overall_score >= self.threshold
        
        return results
    
    def _calculate_explainability(
        self, model: Any, X: np.ndarray, feature_names: Optional[list]
    ) -> float:
        """설명 가능성 점수를 계산합니다."""
        try:
            # SHAP explainer 생성
            if hasattr(model, "predict_proba"):
                explainer = shap.TreeExplainer(model) if hasattr(model, "tree_") else shap.KernelExplainer(model.predict_proba, X[:100])
            else:
                explainer = shap.TreeExplainer(model) if hasattr(model, "tree_") else shap.KernelExplainer(model.predict, X[:100])
            
            # 샘플 데이터에 대한 SHAP 값 계산
            shap_values = explainer.shap_values(X[:100])
            
            # SHAP 값의 일관성과 크기를 기반으로 점수 계산
            if isinstance(shap_values, list):
                shap_values = shap_values[0]  # 다중 클래스의 경우 첫 번째 클래스 사용
            
            # 특성별 중요도의 일관성 측정
            feature_importance = np.abs(shap_values).mean(axis=0)
            consistency = 1 - (feature_importance.std() / (feature_importance.mean() + 1e-10))
            
            return min(1.0, max(0.0, consistency))
        except Exception as e:
            # SHAP 계산 실패 시 기본값 반환
            print(f"SHAP 계산 실패: {e}")
            return 0.5
    
    def _estimate_model_complexity(self, model: Any) -> float:
        """모델 복잡도를 추정합니다."""
        try:
            # 파라미터 수 기반 복잡도 추정
            if hasattr(model, "n_estimators"):
                return model.n_estimators * 10
            elif hasattr(model, "n_layers"):
                return model.n_layers * 50
            elif hasattr(model, "coef_"):
                return np.abs(model.coef_).sum()
            else:
                return 50.0  # 기본값
        except:
            return 50.0
    
    def _calculate_feature_importance_consistency(
        self, model: Any, X: np.ndarray, feature_names: Optional[list]
    ) -> float:
        """특성 중요도 일관성을 계산합니다."""
        try:
            if hasattr(model, "feature_importances_"):
                importances = model.feature_importances_
                # 중요도가 고르게 분포되어 있으면 일관성이 낮음
                # 일부 특성에 집중되어 있으면 일관성이 높음
                entropy = -np.sum(importances * np.log(importances + 1e-10))
                max_entropy = np.log(len(importances))
                consistency = 1 - (entropy / max_entropy)
                return max(0.0, min(1.0, consistency))
            else:
                return 0.5  # 기본값
        except:
            return 0.5

