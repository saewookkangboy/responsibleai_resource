"""
견고성 평가 모듈 테스트
"""

import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.evaluation.robustness import RobustnessEvaluator


class TestRobustnessEvaluator:
    """견고성 평가 테스트 클래스"""

    def test_robustness_evaluation_basic(self):
        """기본 견고성 평가 테스트"""
        config = {
            "robustness": {
                "metrics": ["adversarial_robustness"],
                "threshold": 0.75,
            }
        }

        evaluator = RobustnessEvaluator(config)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.rand(50, 5)
        y = np.random.randint(0, 2, 50)
        model.fit(X, y)

        results = evaluator.evaluate(model, X, y)

        assert "overall_robustness_score" in results
        assert "metrics" in results
        assert "is_robust" in results
        assert isinstance(results["overall_robustness_score"], float)
        assert 0.0 <= results["overall_robustness_score"] <= 1.0

    def test_robustness_evaluation_with_ood_detection(self):
        """분포 외 데이터 감지를 포함한 견고성 평가 테스트"""
        config = {
            "robustness": {
                "metrics": ["adversarial_robustness", "out_of_distribution_detection"],
                "threshold": 0.75,
            }
        }

        evaluator = RobustnessEvaluator(config)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X_train = np.random.rand(50, 5)
        X_test = np.random.rand(30, 5) + 0.5  # 분포가 다른 테스트 데이터
        y = np.random.randint(0, 2, 50)
        model.fit(X_train, y)

        results = evaluator.evaluate(model, X_train, y, X_test=X_test)

        assert "adversarial_robustness" in results["metrics"]
        assert "out_of_distribution_detection" in results["metrics"]

    def test_robustness_evaluation_without_test_data(self):
        """테스트 데이터가 없는 경우 견고성 평가 테스트"""
        config = {
            "robustness": {
                "metrics": ["out_of_distribution_detection"],
                "threshold": 0.75,
            }
        }

        evaluator = RobustnessEvaluator(config)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.rand(50, 5)
        y = np.random.randint(0, 2, 50)
        model.fit(X, y)

        results = evaluator.evaluate(model, X, y, X_test=None)

        assert "out_of_distribution_detection" in results["metrics"]
        assert results["metrics"]["out_of_distribution_detection"] == 0.5  # 기본값

