"""
알림 관리 모듈
"""

import logging
import os
from typing import Dict, Any, List, Optional
import json

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

try:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    SMTP_AVAILABLE = True
except ImportError:
    SMTP_AVAILABLE = False


class AlertManager:
    """알림 관리 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 모니터링 설정 딕셔너리
        """
        self.config = config.get("monitoring", {})
        alerts_config = self.config.get("alerts", {})
        self.enabled = alerts_config.get("enabled", True)
        self.channels = alerts_config.get("channels", [{"type": "console"}])
        self.thresholds = alerts_config.get("thresholds", {})
        self.logger = logging.getLogger(__name__)

    def send_alert(self, message: str, level: str = "INFO", details: Optional[Dict[str, Any]] = None):
        """
        알림 전송

        Args:
            message: 알림 메시지
            level: 알림 레벨 (INFO, WARNING, ERROR)
            details: 상세 정보
        """
        if not self.enabled:
            return

        for channel_config in self.channels:
            channel_type = channel_config.get("type", "console")
            settings = channel_config.get("settings", {})

            if channel_type == "console":
                self._send_console_alert(message, level, details)
            elif channel_type == "email":
                self._send_email_alert(message, level, details, settings)
            elif channel_type == "slack":
                self._send_slack_alert(message, level, details, settings)
            elif channel_type == "webhook":
                self._send_webhook_alert(message, level, details, settings)

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
        self, message: str, level: str, details: Optional[Dict[str, Any]], settings: Dict[str, Any]
    ):
        """이메일 알림 전송"""
        if not SMTP_AVAILABLE:
            self.logger.warning("SMTP 라이브러리가 없어 이메일 알림을 전송할 수 없습니다.")
            return

        try:
            smtp_server = settings.get("smtp_server", os.getenv("SMTP_SERVER", "smtp.gmail.com"))
            smtp_port = settings.get("smtp_port", int(os.getenv("SMTP_PORT", "587")))
            from_email = settings.get("from_email", os.getenv("FROM_EMAIL"))
            to_email = settings.get("to_email", os.getenv("TO_EMAIL"))
            password = settings.get("password", os.getenv("EMAIL_PASSWORD"))

            if not from_email or not to_email:
                self.logger.warning("이메일 설정이 완료되지 않았습니다.")
                return

            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = f"[Responsible AI] {level}: {message}"

            body = f"""
            Responsible AI 알림
            
            레벨: {level}
            메시지: {message}
            """
            if details:
                body += f"\n상세 정보:\n{json.dumps(details, indent=2, ensure_ascii=False)}"

            msg.attach(MIMEText(body, "plain", "utf-8"))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(from_email, password)
            server.send_message(msg)
            server.quit()

            self.logger.info(f"이메일 알림 전송 완료: {to_email}")
        except Exception as e:
            self.logger.error(f"이메일 알림 전송 실패: {e}")

    def _send_slack_alert(
        self, message: str, level: str, details: Optional[Dict[str, Any]], settings: Dict[str, Any]
    ):
        """Slack 알림 전송"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("requests 라이브러리가 없어 Slack 알림을 전송할 수 없습니다.")
            return

        try:
            webhook_url = settings.get("webhook_url", os.getenv("SLACK_WEBHOOK_URL"))

            if not webhook_url:
                self.logger.warning("Slack 웹훅 URL이 설정되지 않았습니다.")
                return

            # 색상 설정
            color_map = {
                "INFO": "#36a64f",  # 녹색
                "WARNING": "#ff9900",  # 주황색
                "ERROR": "#ff0000",  # 빨간색
            }
            color = color_map.get(level, "#808080")

            payload = {
                "text": f"Responsible AI 알림 - {level}",
                "attachments": [
                    {
                        "color": color,
                        "title": message,
                        "fields": [
                            {
                                "title": "레벨",
                                "value": level,
                                "short": True,
                            }
                        ],
                    }
                ],
            }

            if details:
                payload["attachments"][0]["fields"].append(
                    {
                        "title": "상세 정보",
                        "value": json.dumps(details, indent=2, ensure_ascii=False),
                        "short": False,
                    }
                )

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            self.logger.info("Slack 알림 전송 완료")
        except Exception as e:
            self.logger.error(f"Slack 알림 전송 실패: {e}")

    def _send_webhook_alert(
        self, message: str, level: str, details: Optional[Dict[str, Any]], settings: Dict[str, Any]
    ):
        """웹훅 알림 전송"""
        if not REQUESTS_AVAILABLE:
            self.logger.warning("requests 라이브러리가 없어 웹훅 알림을 전송할 수 없습니다.")
            return

        try:
            webhook_url = settings.get("url")
            custom_payload = settings.get("payload", {})

            if not webhook_url:
                self.logger.warning("웹훅 URL이 설정되지 않았습니다.")
                return

            # 기본 페이로드
            payload = {
                "message": message,
                "level": level,
                "details": details,
            }

            # 커스텀 페이로드 병합
            if custom_payload:
                payload.update(custom_payload)

            response = requests.post(webhook_url, json=payload, timeout=10)
            response.raise_for_status()

            self.logger.info("웹훅 알림 전송 완료")
        except Exception as e:
            self.logger.error(f"웹훅 알림 전송 실패: {e}")

    def check_thresholds(self, metrics: Dict[str, Any]) -> List[str]:
        """
        임계값 위반 확인

        Args:
            metrics: 평가 지표

        Returns:
            위반된 임계값 목록
        """
        violations = []

        # 설정된 임계값 사용, 없으면 기본값 사용
        overall_threshold = self.thresholds.get("overall_responsible_ai_score", 0.75)
        overall_score = metrics.get("overall_responsible_ai_score", 0.0)
        if overall_score < overall_threshold:
            violations.append("overall_responsible_ai_score")

        # 각 카테고리별 임계값 확인
        default_thresholds = {
            "fairness_score": 0.7,
            "transparency_score": 0.7,
            "accountability_score": 0.7,
            "privacy_score": 0.8,
            "robustness_score": 0.75,
        }

        for key, default_threshold in default_thresholds.items():
            threshold = self.thresholds.get(key, default_threshold)
            category = key.replace("_score", "")

            if category in metrics:
                category_score = metrics[category].get(
                    f"overall_{category}_score", 0.0
                )
                if category_score < threshold:
                    violations.append(key)

        return violations

