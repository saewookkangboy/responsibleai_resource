"""
모니터링 대시보드 모듈 (하위 호환성을 위한 래퍼)
"""

import logging
from typing import Dict, Any, Optional
from .dashboard_factory import DashboardFactory


class MonitoringDashboard:
    """모니터링 대시보드 클래스 (하위 호환성 래퍼)"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 모니터링 설정 딕셔너리
        """
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # 팩토리를 통해 실제 대시보드 인스턴스 생성
        self._dashboard = DashboardFactory.get_default(config)
        if self._dashboard is None:
            # 기본값으로 콘솔 대시보드 사용
            self._dashboard = DashboardFactory.create("console", config)

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
        """
        메트릭 기록

        Args:
            metrics: 평가 지표 딕셔너리
        """
        if self._dashboard:
            self._dashboard.log_metrics(metrics)
            self.logger.info(f"메트릭 기록: {metrics.get('overall_responsible_ai_score', 0.0):.3f}")

    def get_latest_metrics(self) -> Optional[Dict[str, Any]]:
        """
        최신 메트릭 조회

        Returns:
            최신 평가 지표 또는 None
        """
        if self._dashboard:
            return self._dashboard.get_latest_metrics()
        return None

    def get_metrics_history(self, limit: Optional[int] = None):
        """
        메트릭 히스토리 조회

        Args:
            limit: 조회할 최대 개수

        Returns:
            메트릭 히스토리 리스트
        """
        if self._dashboard:
            return self._dashboard.get_metrics_history(limit)
        return []

    def start_dashboard(self) -> None:
        """대시보드 시작"""
        if self._dashboard:
            self._dashboard.start()
        else:
            self.logger.warning("대시보드를 시작할 수 없습니다.")

