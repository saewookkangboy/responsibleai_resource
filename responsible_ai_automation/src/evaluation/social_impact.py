"""
사회적 영향 평가 모듈
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional


class SocialImpactEvaluator:
    """사회적 영향 평가 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 평가 설정 딕셔너리
        """
        self.config = config.get("social_impact", {})
        self.metrics = self.config.get("metrics", [
            "vulnerable_group_protection",
            "employment_impact",
            "digital_divide",
            "environmental_impact"
        ])

    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        사회적 영향 평가 수행

        Args:
            model: 학습된 모델
            X: 입력 데이터
            y: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임
            **kwargs: 추가 파라미터

        Returns:
            사회적 영향 평가 결과 딕셔너리
        """
        results = {}

        # 취약 계층 보호
        if "vulnerable_group_protection" in self.metrics:
            results["vulnerable_group_protection"] = self._evaluate_vulnerable_group_protection(
                y, y_pred, sensitive_features
            )

        # 고용 영향
        if "employment_impact" in self.metrics:
            results["employment_impact"] = self._evaluate_employment_impact(
                model, X, y_pred
            )

        # 디지털 격차
        if "digital_divide" in self.metrics:
            results["digital_divide"] = self._evaluate_digital_divide(
                X, y_pred, sensitive_features
            )

        # 환경 영향
        if "environmental_impact" in self.metrics:
            results["environmental_impact"] = self._evaluate_environmental_impact(
                model, X, kwargs.get("training_info", {})
            )

        # 종합 점수 계산
        overall_score = self._calculate_overall_score(results)
        results["overall_social_impact_score"] = overall_score

        return results

    def _evaluate_vulnerable_group_protection(
        self,
        y: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame]
    ) -> float:
        """
        취약 계층 보호 평가

        Args:
            y: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임

        Returns:
            취약 계층 보호 점수
        """
        if sensitive_features is None:
            return 0.5  # 기본값

        # 취약 계층 정의 (예: 소수 그룹, 저소득층 등)
        # 실제 구현에서는 더 정교한 로직 필요
        
        # 간단한 예제: 민감한 속성별 정확도 차이 계산
        accuracy_by_group = {}
        for col in sensitive_features.columns:
            unique_values = sensitive_features[col].unique()
            for value in unique_values:
                mask = sensitive_features[col] == value
                if mask.sum() > 0:
                    accuracy = np.mean(y[mask] == y_pred[mask])
                    accuracy_by_group[f"{col}_{value}"] = accuracy

        if not accuracy_by_group:
            return 0.5

        # 그룹 간 정확도 차이가 작을수록 높은 점수
        accuracies = list(accuracy_by_group.values())
        max_diff = max(accuracies) - min(accuracies)
        score = max(0.0, 1.0 - max_diff)

        return float(score)

    def _evaluate_employment_impact(
        self,
        model: Any,
        X: np.ndarray,
        y_pred: np.ndarray
    ) -> float:
        """
        고용 영향 평가

        Args:
            model: 학습된 모델
            X: 입력 데이터
            y_pred: 예측 레이블

        Returns:
            고용 영향 점수
        """
        # 자동화로 인한 고용 영향 평가
        # 실제 구현에서는 더 정교한 분석 필요
        
        # 간단한 예제: 모델의 자동화 정도 추정
        # (실제로는 도메인 전문가와 협의 필요)
        
        # 기본값: 중간 점수
        return 0.5

    def _evaluate_digital_divide(
        self,
        X: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame]
    ) -> float:
        """
        디지털 격차 평가

        Args:
            X: 입력 데이터
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임

        Returns:
            디지털 격차 점수
        """
        if sensitive_features is None:
            return 0.5

        # 접근성 평가: 다양한 그룹에 대한 모델 성능 차이
        # 성능 차이가 작을수록 높은 점수
        
        # 간단한 예제: 민감한 속성별 예측 분포 차이
        prediction_by_group = {}
        for col in sensitive_features.columns:
            unique_values = sensitive_features[col].unique()
            for value in unique_values:
                mask = sensitive_features[col] == value
                if mask.sum() > 0:
                    pred_rate = np.mean(y_pred[mask])
                    prediction_by_group[f"{col}_{value}"] = pred_rate

        if not prediction_by_group:
            return 0.5

        # 그룹 간 예측 비율 차이가 작을수록 높은 점수
        pred_rates = list(prediction_by_group.values())
        max_diff = max(pred_rates) - min(pred_rates)
        score = max(0.0, 1.0 - max_diff)

        return float(score)

    def _evaluate_environmental_impact(
        self,
        model: Any,
        X: np.ndarray,
        training_info: Dict[str, Any]
    ) -> float:
        """
        환경 영향 평가

        Args:
            model: 학습된 모델
            X: 입력 데이터
            training_info: 학습 정보

        Returns:
            환경 영향 점수
        """
        # 탄소 발자국 및 에너지 효율성 평가
        # 실제 구현에서는 실제 에너지 소비량 측정 필요
        
        # 간단한 예제: 모델 복잡도 기반 추정
        model_size = self._estimate_model_size(model)
        
        # 모델이 작을수록, 데이터가 적을수록 높은 점수
        size_score = max(0.0, 1.0 - (model_size / 1000000))  # 1MB 기준
        data_score = max(0.0, 1.0 - (len(X) / 1000000))  # 1M 샘플 기준
        
        score = (size_score + data_score) / 2.0
        
        return float(score)

    def _estimate_model_size(self, model: Any) -> int:
        """
        모델 크기 추정 (바이트)

        Args:
            model: 모델 객체

        Returns:
            추정 모델 크기
        """
        try:
            import pickle
            return len(pickle.dumps(model))
        except Exception:
            return 1000000  # 기본값

    def _calculate_overall_score(self, results: Dict[str, Any]) -> float:
        """
        종합 점수 계산

        Args:
            results: 개별 평가 결과

        Returns:
            종합 점수
        """
        if not results:
            return 0.0

        scores = []
        for key, value in results.items():
            if isinstance(value, (int, float)) and key != "overall_social_impact_score":
                scores.append(value)

        if not scores:
            return 0.0

        return float(np.mean(scores))

