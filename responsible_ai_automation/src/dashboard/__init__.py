"""
Responsible AI Dashboard 모듈

Microsoft Responsible AI Toolbox 스타일의 통합 대시보드를 제공합니다.

주요 컴포넌트:
- ResponsibleAIDashboard: 종합 분석 대시보드
- DashboardConfig: 대시보드 설정

Reference: https://github.com/microsoft/responsible-ai-toolbox
"""

from .rai_dashboard import (
    ResponsibleAIDashboard,
    DashboardConfig,
    create_rai_dashboard,
)

__all__ = [
    "ResponsibleAIDashboard",
    "DashboardConfig",
    "create_rai_dashboard",
]

