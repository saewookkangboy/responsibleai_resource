"""
견고성(Robustness) 평가 모듈
"""

import numpy as np
from typing import Dict, Any, Optional


class RobustnessEvaluator:
    """견고성 평가 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 평가 설정 딕셔너리
        """
        self.config = config.get("robustness", {})
        self.metrics = self.config.get("metrics", ["adversarial_robustness", "out_of_distribution_detection"])
        self.threshold = self.config.get("threshold", 0.75)

    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        y: Optional[np.ndarray] = None,
        X_test: Optional[np.ndarray] = None,
    ) -> Dict[str, Any]:
        """
        견고성 평가 수행

        Args:
            model: 학습된 모델
            X: 훈련 데이터
            y: 타겟 레이블 (선택적)
            X_test: 테스트 데이터 (선택적)

        Returns:
            견고성 평가 결과 딕셔너리
        """
        results = {}

        # Adversarial Robustness
        if "adversarial_robustness" in self.metrics:
            try:
                # 간단한 노이즈 추가 테스트
                noise = np.random.normal(0, 0.01, X.shape)
                X_noisy = X + noise
                X_noisy = np.clip(X_noisy, 0, 1)  # 정규화된 데이터 가정

                if hasattr(model, "predict"):
                    pred_original = model.predict(X[:100])
                    pred_noisy = model.predict(X_noisy[:100])
                    accuracy_drop = 1.0 - np.mean(pred_original == pred_noisy)
                    robustness_score = max(0.0, 1.0 - accuracy_drop)
                else:
                    robustness_score = 0.5

                results["adversarial_robustness"] = float(robustness_score)
            except Exception:
                results["adversarial_robustness"] = 0.5

        # Out-of-Distribution Detection
        if "out_of_distribution_detection" in self.metrics:
            try:
                if X_test is not None:
                    # 간단한 분포 차이 계산
                    train_mean = np.mean(X, axis=0)
                    test_mean = np.mean(X_test, axis=0)
                    distribution_diff = np.mean(np.abs(train_mean - test_mean))
                    ood_score = max(0.0, 1.0 - distribution_diff)
                else:
                    ood_score = 0.5

                results["out_of_distribution_detection"] = float(ood_score)
            except Exception:
                results["out_of_distribution_detection"] = 0.5

        # 전체 견고성 점수 계산
        overall_score = float(np.mean(list(results.values()))) if results else 0.0
        is_robust = overall_score >= self.threshold

        return {
            "overall_robustness_score": overall_score,
            "metrics": results,
            "is_robust": is_robust,
            "threshold": self.threshold,
        }

