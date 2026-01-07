"""
대시보드 베이스 클래스 - 확장 가능한 대시보드 인터페이스
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import datetime


class DashboardBase(ABC):
    """대시보드 베이스 클래스 - 모든 대시보드 구현체가 상속해야 함"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 대시보드 설정
        """
        self.config = config.get("monitoring", {}).get("dashboard", {})
        self.enabled = self.config.get("enabled", True)
        self.port = self.config.get("port", 8080)
        self.metrics_history: List[Dict[str, Any]] = []
        self.retention_days = self.config.get("retention_days", 30)

    @abstractmethod
    def render(self, metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        대시보드 렌더링 (구현체에서 구현 필요)

        Args:
            metrics: 현재 메트릭 (선택적)
        """
        pass

    @abstractmethod
    def start(self) -> None:
        """대시보드 시작 (구현체에서 구현 필요)"""
        pass

    def log_metrics(self, metrics: Dict[str, Any]) -> None:
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
        self._cleanup_old_metrics()

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

    def _cleanup_old_metrics(self) -> None:
        """오래된 메트릭 정리"""
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=self.retention_days)

        self.metrics_history = [
            entry
            for entry in self.metrics_history
            if datetime.fromisoformat(entry["timestamp"]) >= cutoff_date
        ]

    def get_metrics_summary(self) -> Dict[str, Any]:
        """
        메트릭 요약 정보 반환

        Returns:
            메트릭 요약 딕셔너리
        """
        if not self.metrics_history:
            return {
                "total_evaluations": 0,
                "latest_score": None,
                "average_score": None,
            }

        scores = [
            entry["metrics"].get("overall_responsible_ai_score", 0.0)
            for entry in self.metrics_history
        ]

        return {
            "total_evaluations": len(self.metrics_history),
            "latest_score": scores[-1] if scores else None,
            "average_score": sum(scores) / len(scores) if scores else None,
            "min_score": min(scores) if scores else None,
            "max_score": max(scores) if scores else None,
        }

