"""
책임성(Accountability) 평가 모듈
"""

from typing import Dict, Any, List, Optional
import logging
from datetime import datetime


class AccountabilityEvaluator:
    """책임성 평가 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 평가 설정 딕셔너리
        """
        self.config = config.get("accountability", {})
        self.metrics = self.config.get("metrics", ["audit_trail", "decision_logging"])
        self.enabled = self.config.get("enabled", True)
        self.audit_trail: List[Dict[str, Any]] = []
        self.decision_logs: List[Dict[str, Any]] = []
        self.error_logs: List[Dict[str, Any]] = []

        # 로깅 설정
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def evaluate(self) -> Dict[str, Any]:
        """
        책임성 평가 수행

        Returns:
            책임성 평가 결과 딕셔너리
        """
        if not self.enabled:
            return {
                "overall_accountability_score": 0.0,
                "metrics": {},
                "is_accountable": False,
                "message": "책임성 평가가 비활성화되어 있습니다.",
            }

        results = {}

        # Audit Trail
        if "audit_trail" in self.metrics:
            audit_score = min(1.0, len(self.audit_trail) / 100.0)  # 최소 100개 기록 기준
            results["audit_trail"] = audit_score

        # Decision Logging
        if "decision_logging" in self.metrics:
            decision_score = min(1.0, len(self.decision_logs) / 100.0)
            results["decision_logging"] = decision_score

        # Error Tracking
        if "error_tracking" in self.metrics:
            error_score = 1.0 if len(self.error_logs) == 0 else max(0.0, 1.0 - len(self.error_logs) / 10.0)
            results["error_tracking"] = error_score

        # 전체 책임성 점수 계산
        overall_score = float(sum(results.values()) / len(results)) if results else 0.0
        is_accountable = overall_score >= 0.7

        return {
            "overall_accountability_score": overall_score,
            "metrics": results,
            "is_accountable": is_accountable,
            "audit_trail_count": len(self.audit_trail),
            "decision_log_count": len(self.decision_logs),
            "error_log_count": len(self.error_logs),
        }

    def log_audit_trail(self, action: str, details: Dict[str, Any]):
        """
        감사 추적 로그 기록

        Args:
            action: 수행된 액션
            details: 상세 정보
        """
        audit_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "details": details,
        }
        self.audit_trail.append(audit_entry)
        self.logger.info(f"Audit Trail: {action} - {details}")

    def log_decision(self, decision: str, context: Dict[str, Any]):
        """
        의사결정 로그 기록

        Args:
            decision: 의사결정 내용
            context: 컨텍스트 정보
        """
        decision_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision": decision,
            "context": context,
        }
        self.decision_logs.append(decision_entry)
        self.logger.info(f"Decision Log: {decision} - {context}")

    def log_error(self, error: Exception, context: Dict[str, Any]):
        """
        오류 로그 기록

        Args:
            error: 발생한 오류
            context: 컨텍스트 정보
        """
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": type(error).__name__,
            "error_message": str(error),
            "context": context,
        }
        self.error_logs.append(error_entry)
        self.logger.error(f"Error Log: {error} - {context}")

