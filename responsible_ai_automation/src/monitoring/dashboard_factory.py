"""
대시보드 팩토리 - 다양한 대시보드 구현체를 생성하고 관리
"""

from typing import Dict, Any, Optional, Type
from .dashboard_base import DashboardBase


class DashboardFactory:
    """대시보드 팩토리 클래스"""

    _registry: Dict[str, Type[DashboardBase]] = {}

    @classmethod
    def register(cls, name: str, dashboard_class: Type[DashboardBase]) -> None:
        """
        대시보드 구현체 등록

        Args:
            name: 대시보드 이름
            dashboard_class: 대시보드 클래스
        """
        cls._registry[name.lower()] = dashboard_class

    @classmethod
    def create(cls, name: str, config: Dict[str, Any]) -> Optional[DashboardBase]:
        """
        대시보드 인스턴스 생성

        Args:
            name: 대시보드 이름
            config: 설정 딕셔너리

        Returns:
            대시보드 인스턴스 또는 None
        """
        dashboard_class = cls._registry.get(name.lower())
        if dashboard_class is None:
            return None

        return dashboard_class(config)

    @classmethod
    def list_available(cls) -> List[str]:
        """
        사용 가능한 대시보드 목록 반환

        Returns:
            대시보드 이름 리스트
        """
        return list(cls._registry.keys())

    @classmethod
    def get_default(cls, config: Dict[str, Any]) -> Optional[DashboardBase]:
        """
        기본 대시보드 인스턴스 생성 (설정에서 지정된 대시보드)

        Args:
            config: 설정 딕셔너리

        Returns:
            대시보드 인스턴스 또는 None
        """
        dashboard_config = config.get("monitoring", {}).get("dashboard", {})
        dashboard_type = dashboard_config.get("type", "console")

        return cls.create(dashboard_type, config)


# 자동으로 사용 가능한 대시보드 등록
def _register_builtin_dashboards():
    """내장 대시보드 자동 등록"""
    # Console 대시보드 (항상 사용 가능)
    from .dashboard_console import ConsoleDashboard
    DashboardFactory.register("console", ConsoleDashboard)

    # Streamlit 대시보드 (선택적)
    try:
        from .dashboard_streamlit import StreamlitDashboard
        DashboardFactory.register("streamlit", StreamlitDashboard)
    except ImportError:
        pass

    # Gradio 대시보드 (선택적)
    try:
        from .dashboard_gradio import GradioDashboard
        DashboardFactory.register("gradio", GradioDashboard)
    except ImportError:
        pass

    # FastAPI 대시보드 (선택적)
    try:
        from .dashboard_fastapi import FastAPIDashboard
        DashboardFactory.register("fastapi", FastAPIDashboard)
    except ImportError:
        pass


# 모듈 로드 시 자동 등록
_register_builtin_dashboards()

