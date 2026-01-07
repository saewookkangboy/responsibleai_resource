"""
평가 모듈 테스트
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from src.evaluation.fairness import FairnessEvaluator
from src.evaluation.transparency import TransparencyEvaluator
from src.evaluation.accountability import AccountabilityEvaluator
from src.evaluation.privacy import PrivacyEvaluator
from src.evaluation.robustness import RobustnessEvaluator
from src.evaluation.comprehensive import ComprehensiveEvaluator


class TestFairnessEvaluator:
    """공정성 평가 테스트"""

    def test_fairness_evaluation(self):
        """공정성 평가 기본 테스트"""
        config = {
            "fairness": {
                "metrics": ["demographic_parity"],
                "threshold": 0.1,
                "sensitive_attributes": ["gender"],
            }
        }

        evaluator = FairnessEvaluator(config)

        y_true = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        y_pred = np.array([0, 1, 0, 1, 0, 1, 0, 1])
        sensitive_features = pd.DataFrame({"gender": ["M", "F", "M", "F", "M", "F", "M", "F"]})

        results = evaluator.evaluate(y_true, y_pred, sensitive_features)

        assert "overall_fairness_score" in results
        assert isinstance(results["overall_fairness_score"], float)
        assert 0.0 <= results["overall_fairness_score"] <= 1.0


class TestTransparencyEvaluator:
    """투명성 평가 테스트"""

    def test_transparency_evaluation(self):
        """투명성 평가 기본 테스트"""
        config = {
            "transparency": {
                "metrics": ["explainability_score"],
                "threshold": 0.7,
            }
        }

        evaluator = TransparencyEvaluator(config)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.rand(100, 10)
        y = np.random.randint(0, 2, 100)
        model.fit(X, y)

        results = evaluator.evaluate(model, X, y)

        assert "overall_transparency_score" in results
        assert isinstance(results["overall_transparency_score"], float)
        assert 0.0 <= results["overall_transparency_score"] <= 1.0


class TestAccountabilityEvaluator:
    """책임성 평가 테스트"""

    def test_accountability_evaluation(self):
        """책임성 평가 기본 테스트"""
        config = {
            "accountability": {
                "metrics": ["audit_trail", "decision_logging"],
                "enabled": True,
            }
        }

        evaluator = AccountabilityEvaluator(config)

        # 로그 기록
        evaluator.log_audit_trail("test_action", {"detail": "test"})
        evaluator.log_decision("test_decision", {"context": "test"})

        results = evaluator.evaluate()

        assert "overall_accountability_score" in results
        assert isinstance(results["overall_accountability_score"], float)


class TestComprehensiveEvaluator:
    """종합 평가 테스트"""

    def test_comprehensive_evaluation(self):
        """종합 평가 기본 테스트"""
        config = {
            "fairness": {
                "metrics": ["demographic_parity"],
                "threshold": 0.1,
                "sensitive_attributes": ["gender"],
            },
            "transparency": {
                "metrics": ["explainability_score"],
                "threshold": 0.7,
            },
            "accountability": {
                "metrics": ["audit_trail"],
                "enabled": True,
            },
            "privacy": {
                "metrics": ["differential_privacy"],
                "threshold": 0.8,
            },
            "robustness": {
                "metrics": ["adversarial_robustness"],
                "threshold": 0.75,
            },
        }

        evaluator = ComprehensiveEvaluator(config)

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        X = np.random.rand(100, 10)
        y = np.random.randint(0, 2, 100)
        model.fit(X, y)

        y_pred = model.predict(X)
        sensitive_features = pd.DataFrame({"gender": np.random.choice(["M", "F"], 100)})

        results = evaluator.evaluate(model, X, y, y_pred, sensitive_features)

        assert "overall_responsible_ai_score" in results
        assert "is_responsible" in results
        assert isinstance(results["overall_responsible_ai_score"], float)
        assert 0.0 <= results["overall_responsible_ai_score"] <= 1.0

