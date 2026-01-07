"""
알림 관리 모듈
"""

import logging
from typing import Dict, Any, List, Optional


class AlertManager:
    """알림 관리 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 모니터링 설정 딕셔너리
        """
        self.config = config.get("monitoring", {})
        self.alert_channels = self.config.get("alert_channels", ["console"])
        self.logger = logging.getLogger(__name__)

    def send_alert(self, message: str, level: str = "INFO", details: Optional[Dict[str, Any]] = None):
        """
        알림 전송

        Args:
            message: 알림 메시지
            level: 알림 레벨 (INFO, WARNING, ERROR)
            details: 상세 정보
        """
        for channel in self.alert_channels:
            if channel == "console":
                self._send_console_alert(message, level, details)
            elif channel == "email":
                self._send_email_alert(message, level, details)
            elif channel == "slack":
                self._send_slack_alert(message, level, details)

    def _send_console_alert(
        self, message: str, level: str, details: Optional[Dict[str, Any]]
    ):
        """콘솔 알림 전송"""
        log_message = f"[{level}] {message}"
        if details:
            log_message += f" - {details}"

        if level == "ERROR":
            self.logger.error(log_message)
        elif level == "WARNING":
            self.logger.warning(log_message)
        else:
            self.logger.info(log_message)

    def _send_email_alert(
        self, message: str, level: str, details: Optional[Dict[str, Any]]
    ):
        """이메일 알림 전송 (실제 구현 필요)"""
        self.logger.info(f"이메일 알림 전송: {message}")

    def _send_slack_alert(
        self, message: str, level: str, details: Optional[Dict[str, Any]]
    ):
        """Slack 알림 전송 (실제 구현 필요)"""
        self.logger.info(f"Slack 알림 전송: {message}")

    def check_thresholds(self, metrics: Dict[str, Any]) -> List[str]:
        """
        임계값 위반 확인

        Args:
            metrics: 평가 지표

        Returns:
            위반된 임계값 목록
        """
        violations = []

        overall_score = metrics.get("overall_responsible_ai_score", 0.0)
        if overall_score < 0.75:
            violations.append("overall_responsible_ai_score")

        # 각 카테고리별 임계값 확인
        thresholds = {
            "fairness": 0.7,
            "transparency": 0.7,
            "accountability": 0.7,
            "privacy": 0.8,
            "robustness": 0.75,
        }

        for category, threshold in thresholds.items():
            if category in metrics:
                category_score = metrics[category].get(
                    f"overall_{category}_score", 0.0
                )
                if category_score < threshold:
                    violations.append(f"{category}_score")

        return violations

