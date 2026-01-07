"""
알림 관리 모듈
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class AlertManager:
    """알림을 관리하는 클래스"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}
        self.alert_channels = self.config.get("monitoring", {}).get("alert_channels", ["console"])
        self.alert_history = []
    
    def check_and_alert(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        지표를 검사하고 필요한 경우 알림을 전송합니다.
        
        Args:
            metrics: 평가 지표
        
        Returns:
            전송된 알림 리스트
        """
        alerts = []
        
        # 1. 전체 점수 임계값 검사
        overall_score = metrics.get("overall_responsible_ai_score", 0.0)
        if overall_score < 0.7:
            alert = self._create_alert(
                "critical",
                "Overall Responsible AI Score Below Threshold",
                f"현재 점수: {overall_score:.3f} (임계값: 0.7)",
                metrics,
            )
            alerts.append(alert)
        
        # 2. 각 카테고리별 임계값 검사
        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
        thresholds = {
            "fairness": 0.9,
            "transparency": 0.7,
            "accountability": 0.7,
            "privacy": 0.8,
            "robustness": 0.75,
        }
        
        for category in categories:
            if category in metrics:
                category_score = metrics[category].get(
                    f"overall_{category}_score", 0.0
                )
                threshold = thresholds.get(category, 0.7)
                
                if category_score < threshold:
                    alert = self._create_alert(
                        "warning",
                        f"{category.capitalize()} Score Below Threshold",
                        f"{category} 점수: {category_score:.3f} (임계값: {threshold})",
                        metrics,
                    )
                    alerts.append(alert)
        
        # 알림 전송
        for alert in alerts:
            self._send_alert(alert)
            self.alert_history.append(alert)
        
        return alerts
    
    def _create_alert(
        self,
        level: str,
        title: str,
        message: str,
        metrics: Dict[str, Any],
    ) -> Dict[str, Any]:
        """알림을 생성합니다."""
        return {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "title": title,
            "message": message,
            "metrics": metrics,
        }
    
    def _send_alert(self, alert: Dict[str, Any]):
        """알림을 전송합니다."""
        for channel in self.alert_channels:
            if channel == "console":
                self._send_console_alert(alert)
            elif channel == "email":
                self._send_email_alert(alert)
            elif channel == "slack":
                self._send_slack_alert(alert)
    
    def _send_console_alert(self, alert: Dict[str, Any]):
        """콘솔에 알림을 출력합니다."""
        level_symbol = {
            "critical": "🔴",
            "warning": "⚠️",
            "info": "ℹ️",
        }.get(alert["level"], "ℹ️")
        
        print(f"\n{level_symbol} [{alert['level'].upper()}] {alert['title']}")
        print(f"   {alert['message']}")
        print(f"   시간: {alert['timestamp']}\n")
    
    def _send_email_alert(self, alert: Dict[str, Any]):
        """이메일로 알림을 전송합니다."""
        # 실제 구현 필요 (SMTP 등)
        pass
    
    def _send_slack_alert(self, alert: Dict[str, Any]):
        """Slack으로 알림을 전송합니다."""
        # 실제 구현 필요 (Slack API 등)
        pass
    
    def get_alert_history(self, days: int = 7) -> List[Dict[str, Any]]:
        """알림 이력을 반환합니다."""
        from datetime import timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_alerts = []
        for alert in self.alert_history:
            alert_time = datetime.fromisoformat(alert["timestamp"])
            if alert_time >= cutoff_date:
                filtered_alerts.append(alert)
        
        return filtered_alerts

