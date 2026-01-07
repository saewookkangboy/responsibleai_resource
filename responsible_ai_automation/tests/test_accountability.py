"""
책임성 평가 모듈 테스트
"""

import pytest
from src.evaluation.accountability import AccountabilityEvaluator


class TestAccountabilityEvaluator:
    """책임성 평가 테스트 클래스"""

    def test_accountability_evaluation_basic(self):
        """기본 책임성 평가 테스트"""
        config = {
            "accountability": {
                "metrics": ["audit_trail", "decision_logging"],
                "enabled": True,
            }
        }

        evaluator = AccountabilityEvaluator(config)

        # 로그 기록
        for i in range(50):
            evaluator.log_audit_trail(f"action_{i}", {"detail": f"test_{i}"})
            evaluator.log_decision(f"decision_{i}", {"context": f"test_{i}"})

        results = evaluator.evaluate()

        assert "overall_accountability_score" in results
        assert "metrics" in results
        assert "is_accountable" in results
        assert "audit_trail_count" in results
        assert "decision_log_count" in results
        assert isinstance(results["overall_accountability_score"], float)
        assert 0.0 <= results["overall_accountability_score"] <= 1.0

    def test_accountability_evaluation_disabled(self):
        """책임성 평가가 비활성화된 경우 테스트"""
        config = {
            "accountability": {
                "metrics": ["audit_trail"],
                "enabled": False,
            }
        }

        evaluator = AccountabilityEvaluator(config)

        results = evaluator.evaluate()

        assert results["overall_accountability_score"] == 0.0
        assert results["is_accountable"] is False
        assert "message" in results

    def test_log_audit_trail(self):
        """감사 추적 로그 기록 테스트"""
        config = {"accountability": {"metrics": [], "enabled": True}}
        evaluator = AccountabilityEvaluator(config)

        evaluator.log_audit_trail("test_action", {"detail": "test"})

        assert len(evaluator.audit_trail) == 1
        assert evaluator.audit_trail[0]["action"] == "test_action"

    def test_log_decision(self):
        """의사결정 로그 기록 테스트"""
        config = {"accountability": {"metrics": [], "enabled": True}}
        evaluator = AccountabilityEvaluator(config)

        evaluator.log_decision("test_decision", {"context": "test"})

        assert len(evaluator.decision_logs) == 1
        assert evaluator.decision_logs[0]["decision"] == "test_decision"

    def test_log_error(self):
        """오류 로그 기록 테스트"""
        config = {"accountability": {"metrics": [], "enabled": True}}
        evaluator = AccountabilityEvaluator(config)

        error = ValueError("Test error")
        evaluator.log_error(error, {"context": "test"})

        assert len(evaluator.error_logs) == 1
        assert evaluator.error_logs[0]["error_type"] == "ValueError"

