"""
FastAPI 기반 대시보드 (선택적 구현체)
"""

try:
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    import uvicorn
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False

from typing import Dict, Any, Optional
from .dashboard_base import DashboardBase


class FastAPIDashboard(DashboardBase):
    """FastAPI 기반 대시보드 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 대시보드 설정
        """
        if not FASTAPI_AVAILABLE:
            raise ImportError(
                "FastAPI가 설치되지 않았습니다. "
                "pip install fastapi uvicorn을 실행하세요."
            )
        super().__init__(config)
        self.port = self.config.get("port", 8000)
        self.app = FastAPI(title="Responsible AI Dashboard")

        # 라우트 설정
        self._setup_routes()

    def _setup_routes(self) -> None:
        """FastAPI 라우트 설정"""
        @self.app.get("/", response_class=HTMLResponse)
        async def root():
            """대시보드 메인 페이지"""
            latest = self.get_latest_metrics()
            if not latest:
                return "<h1>메트릭 데이터가 없습니다.</h1>"

            overall_score = latest.get("overall_responsible_ai_score", 0.0)
            is_responsible = latest.get("is_responsible", False)

            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>Responsible AI Dashboard</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; }}
                    .score {{ font-size: 48px; font-weight: bold; }}
                    .status {{ font-size: 24px; }}
                </style>
            </head>
            <body>
                <h1>Responsible AI 모니터링 대시보드</h1>
                <div class="score">종합 점수: {overall_score:.3f}</div>
                <div class="status">상태: {'✅ 준수' if is_responsible else '⚠️ 미준수'}</div>
            </body>
            </html>
            """
            return html

        @self.app.get("/api/metrics")
        async def get_metrics():
            """메트릭 API"""
            return self.get_latest_metrics()

        @self.app.get("/api/history")
        async def get_history(limit: Optional[int] = None):
            """메트릭 히스토리 API"""
            return self.get_metrics_history(limit)

    def render(self, metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        대시보드 렌더링 (FastAPI는 start()에서 처리)

        Args:
            metrics: 현재 메트릭 (선택적)
        """
        if metrics:
            self.log_metrics(metrics)

    def start(self) -> None:
        """FastAPI 대시보드 시작"""
        uvicorn.run(self.app, host="0.0.0.0", port=self.port)

