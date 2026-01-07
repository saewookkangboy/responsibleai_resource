"""
콘솔 기반 대시보드 (기본 구현체)
"""

import logging
from typing import Dict, Any, Optional
from .dashboard_base import DashboardBase


class ConsoleDashboard(DashboardBase):
    """콘솔 기반 대시보드 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 대시보드 설정
        """
        super().__init__(config)
        self.logger = logging.getLogger(__name__)

    def render(self, metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        콘솔에 메트릭 출력

        Args:
            metrics: 현재 메트릭 (선택적)
        """
        if metrics:
            self.log_metrics(metrics)
            self._print_metrics(metrics)
        else:
            latest = self.get_latest_metrics()
            if latest:
                self._print_metrics(latest)
            else:
                self.logger.info("표시할 메트릭이 없습니다.")

    def _print_metrics(self, metrics: Dict[str, Any]) -> None:
        """메트릭을 콘솔에 출력"""
        overall_score = metrics.get("overall_responsible_ai_score", 0.0)
        is_responsible = metrics.get("is_responsible", False)

        self.logger.info("=" * 60)
        self.logger.info("Responsible AI 평가 결과")
        self.logger.info("=" * 60)
        self.logger.info(f"종합 점수: {overall_score:.3f} {'✅' if is_responsible else '⚠️'}")

        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
        category_names = {
            "fairness": "공정성",
            "transparency": "투명성",
            "accountability": "책임성",
            "privacy": "프라이버시",
            "robustness": "견고성",
        }

        for category in categories:
            if category in metrics:
                score = metrics[category].get(f"overall_{category}_score", 0.0)
                self.logger.info(f"  {category_names[category]}: {score:.3f}")

        self.logger.info("=" * 60)

    def start(self) -> None:
        """콘솔 대시보드는 별도 시작 과정이 필요 없음"""
        self.logger.info("콘솔 대시보드 활성화됨")

