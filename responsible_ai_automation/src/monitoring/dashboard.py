"""
모니터링 대시보드 모듈
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime


class MonitoringDashboard:
    """모니터링 대시보드 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 모니터링 설정 딕셔너리
        """
        self.config = config.get("monitoring", {})
        self.enabled = self.config.get("enabled", True)
        self.port = self.config.get("dashboard_port", 8080)
        self.metrics_history: List[Dict[str, Any]] = []
        self.retention_days = self.config.get("metrics_retention_days", 30)

        self.logger = logging.getLogger(__name__)

    def log_metrics(self, metrics: Dict[str, Any]):
        """
        메트릭 기록

        Args:
            metrics: 평가 지표 딕셔너리
        """
        if not self.enabled:
            return

        entry = {
            "timestamp": datetime.now().isoformat(),
            "metrics": metrics,
        }

        self.metrics_history.append(entry)

        # 오래된 메트릭 제거
        self._cleanup_old_metrics()

        self.logger.info(f"메트릭 기록: {metrics.get('overall_responsible_ai_score', 0.0):.3f}")

    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """
        최신 메트릭 조회

        Returns:
            최신 평가 지표 또는 None
        """
        if not self.metrics_history:
            return None

        return self.metrics_history[-1]["metrics"]

    def get_metrics_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        메트릭 히스토리 조회

        Args:
            limit: 조회할 최대 개수

        Returns:
            메트릭 히스토리 리스트
        """
        if limit is None:
            return self.metrics_history

        return self.metrics_history[-limit:]

    def _cleanup_old_metrics(self):
        """오래된 메트릭 정리"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        self.metrics_history = [
            entry
            for entry in self.metrics_history
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
        ]

    def start_dashboard(self):
        """대시보드 시작 (실제 구현에서는 웹 서버 시작)"""
        if not self.enabled:
            self.logger.info("모니터링이 비활성화되어 있습니다.")
            return

        self.logger.info(f"모니터링 대시보드 시작 (포트: {self.port})")
        # 실제 구현에서는 Flask/FastAPI 등을 사용하여 웹 대시보드 구현

