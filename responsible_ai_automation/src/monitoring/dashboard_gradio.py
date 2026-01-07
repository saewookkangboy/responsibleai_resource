"""
Gradio 기반 대시보드 (선택적 구현체)
"""

try:
    import gradio as gr
    GRADIO_AVAILABLE = True
except ImportError:
    GRADIO_AVAILABLE = False

from typing import Dict, Any, Optional
from .dashboard_base import DashboardBase


class GradioDashboard(DashboardBase):
    """Gradio 기반 대시보드 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 대시보드 설정
        """
        if not GRADIO_AVAILABLE:
            raise ImportError(
                "Gradio가 설치되지 않았습니다. "
                "pip install gradio를 실행하세요."
            )
        super().__init__(config)
        self.port = self.config.get("port", 7860)

    def render(self, metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        대시보드 렌더링

        Args:
            metrics: 현재 메트릭 (선택적)
        """
        if not self.enabled:
            return

        if metrics:
            self.log_metrics(metrics)

        # Gradio 인터페이스는 start()에서 생성

    def start(self) -> None:
        """Gradio 대시보드 시작"""
        def get_metrics_display():
            """메트릭 표시 함수"""
            latest = self.get_latest_metrics()
            if not latest:
                return "메트릭 데이터가 없습니다."

            overall_score = latest.get("overall_responsible_ai_score", 0.0)
            is_responsible = latest.get("is_responsible", False)

            display = f"""
            # Responsible AI 평가 결과
            
            ## 종합 점수: {overall_score:.3f} {'✅' if is_responsible else '⚠️'}
            
            ### 카테고리별 점수:
            """
            categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
            for category in categories:
                if category in latest:
                    score = latest[category].get(f"overall_{category}_score", 0.0)
                    display += f"\n- {category}: {score:.3f}"

            return display

        iface = gr.Interface(
            fn=get_metrics_display,
            inputs=None,
            outputs="markdown",
            title="Responsible AI 모니터링 대시보드",
            description="Responsible AI 평가 메트릭을 확인하세요.",
        )

        iface.launch(server_port=self.port, share=False)

