"""
공정성 평가 모듈 테스트
"""

import pytest
import numpy as np
import pandas as pd
from src.evaluation.fairness import FairnessEvaluator


class TestFairnessEvaluator:
    """공정성 평가 테스트 클래스"""

    def test_fairness_evaluation_with_sensitive_features(self):
        """민감한 속성이 있는 경우 공정성 평가 테스트"""
        config = {
            "fairness": {
                "metrics": ["demographic_parity", "equalized_odds", "equal_opportunity"],
                "threshold": 0.1,
                "sensitive_attributes": ["gender", "race"],
            }
        }

        evaluator = FairnessEvaluator(config)

        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1, 0, 1, 0, 1, 0, 1])
        sensitive_features = pd.DataFrame({
            "gender": ["M", "F", "M", "F", "M", "F", "M", "F", "M", "F"],
            "race": ["A", "B", "A", "B", "A", "B", "A", "B", "A", "B"],
        })

        results = evaluator.evaluate(y_true, y_pred, sensitive_features)

        assert "overall_fairness_score" in results
        assert "metrics" in results
        assert "is_fair" in results
        assert isinstance(results["overall_fairness_score"], float)
        assert 0.0 <= results["overall_fairness_score"] <= 1.0

    def test_fairness_evaluation_without_sensitive_features(self):
        """민감한 속성이 없는 경우 공정성 평가 테스트"""
        config = {
            "fairness": {
                "metrics": ["demographic_parity"],
                "threshold": 0.1,
                "sensitive_attributes": ["gender"],
            }
        }

        evaluator = FairnessEvaluator(config)

        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])

        results = evaluator.evaluate(y_true, y_pred, None)

        assert results["overall_fairness_score"] == 0.0
        assert results["is_fair"] is False
        assert "message" in results

    def test_fairness_evaluation_with_missing_attribute(self):
        """설정된 민감한 속성이 데이터에 없는 경우 테스트"""
        config = {
            "fairness": {
                "metrics": ["demographic_parity"],
                "threshold": 0.1,
                "sensitive_attributes": ["gender", "age"],
            }
        }

        evaluator = FairnessEvaluator(config)

        y_true = np.array([0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1])
        sensitive_features = pd.DataFrame({"gender": ["M", "F", "M", "F"]})

        results = evaluator.evaluate(y_true, y_pred, sensitive_features)

        assert "overall_fairness_score" in results
        assert "gender" in results["metrics"]
        assert "age" not in results["metrics"]

    def test_calculate_overall_score(self):
        """전체 공정성 점수 계산 테스트"""
        config = {
            "fairness": {
                "metrics": ["demographic_parity"],
                "threshold": 0.1,
                "sensitive_attributes": ["gender"],
            }
        }

        evaluator = FairnessEvaluator(config)

        # 빈 결과 테스트
        score = evaluator._calculate_overall_score({})
        assert score == 0.0

        # 정상 결과 테스트
        results = {
            "gender": {
                "demographic_parity": 0.05,
                "equalized_odds": 0.03,
            }
        }
        score = evaluator._calculate_overall_score(results)
        assert 0.0 <= score <= 1.0

