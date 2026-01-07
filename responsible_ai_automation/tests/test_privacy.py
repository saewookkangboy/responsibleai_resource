"""
프라이버시 평가 모듈 테스트
"""

import pytest
import numpy as np
from src.evaluation.privacy import PrivacyEvaluator


class TestPrivacyEvaluator:
    """프라이버시 평가 테스트 클래스"""

    def test_privacy_evaluation_basic(self):
        """기본 프라이버시 평가 테스트"""
        config = {
            "privacy": {
                "metrics": ["differential_privacy", "data_anonymization"],
                "threshold": 0.8,
            }
        }

        evaluator = PrivacyEvaluator(config)

        results = evaluator.evaluate(
            data_anonymization_level=0.9,
            access_control_enabled=True
        )

        assert "overall_privacy_score" in results
        assert "metrics" in results
        assert "is_private" in results
        assert isinstance(results["overall_privacy_score"], float)
        assert 0.0 <= results["overall_privacy_score"] <= 1.0

    def test_privacy_evaluation_with_access_control(self):
        """접근 제어가 활성화된 경우 프라이버시 평가 테스트"""
        config = {
            "privacy": {
                "metrics": ["differential_privacy", "data_anonymization", "access_control"],
                "threshold": 0.8,
            }
        }

        evaluator = PrivacyEvaluator(config)

        results = evaluator.evaluate(
            access_control_enabled=True,
            data_anonymization_level=0.8
        )

        assert "access_control" in results["metrics"]
        assert results["metrics"]["access_control"] == 1.0

    def test_privacy_evaluation_without_anonymization(self):
        """익명화 레벨이 제공되지 않은 경우 테스트"""
        config = {
            "privacy": {
                "metrics": ["data_anonymization"],
                "threshold": 0.8,
            }
        }

        evaluator = PrivacyEvaluator(config)

        results = evaluator.evaluate()

        assert "data_anonymization" in results["metrics"]
        assert results["metrics"]["data_anonymization"] == 0.5  # 기본값

