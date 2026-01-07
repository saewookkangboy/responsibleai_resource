"""
투명성 평가 모듈 테스트
"""

import pytest
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from src.evaluation.transparency import TransparencyEvaluator


class TestTransparencyEvaluator:
    """투명성 평가 테스트 클래스"""

    def test_transparency_evaluation_basic(self):
        """기본 투명성 평가 테스트"""
        config = {
            "transparency": {
                "metrics": ["explainability_score"],
                "threshold": 0.7,
            }
        }

        evaluator = TransparencyEvaluator(config)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.rand(50, 5)
        y = np.random.randint(0, 2, 50)
        model.fit(X, y)

        results = evaluator.evaluate(model, X, y)

        assert "overall_transparency_score" in results
        assert "metrics" in results
        assert "is_transparent" in results
        assert isinstance(results["overall_transparency_score"], float)
        assert 0.0 <= results["overall_transparency_score"] <= 1.0

    def test_transparency_evaluation_with_all_metrics(self):
        """모든 메트릭을 포함한 투명성 평가 테스트"""
        config = {
            "transparency": {
                "metrics": ["explainability_score", "model_complexity", "feature_importance"],
                "threshold": 0.7,
            }
        }

        evaluator = TransparencyEvaluator(config)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.rand(50, 5)
        y = np.random.randint(0, 2, 50)
        model.fit(X, y)

        results = evaluator.evaluate(model, X, y)

        assert "overall_transparency_score" in results
        assert "explainability_score" in results["metrics"]
        assert "model_complexity" in results["metrics"]
        assert "feature_importance" in results["metrics"]

    def test_calculate_complexity(self):
        """모델 복잡도 계산 테스트"""
        config = {"transparency": {"metrics": [], "threshold": 0.7}}
        evaluator = TransparencyEvaluator(config)

        # RandomForest 모델
        model = RandomForestClassifier(n_estimators=50, random_state=42)
        complexity = evaluator._calculate_complexity(model)
        assert 0.0 <= complexity <= 1.0

        # 다른 타입의 모델 (기본값 반환)
        class SimpleModel:
            pass

        simple_model = SimpleModel()
        complexity = evaluator._calculate_complexity(simple_model)
        assert complexity == 0.5

