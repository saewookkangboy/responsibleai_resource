"""
Streamlit 기반 웹 대시보드 (확장 가능한 구현체)
"""

try:
    import streamlit as st
    import pandas as pd
    import plotly.graph_objects as go
    import plotly.express as px
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False

from typing import Dict, Any, Optional
import numpy as np
from .dashboard_base import DashboardBase


class StreamlitDashboard(DashboardBase):
    """Streamlit 기반 대시보드 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 대시보드 설정
        """
        if not STREAMLIT_AVAILABLE:
            raise ImportError(
                "Streamlit이 설치되지 않았습니다. "
                "pip install streamlit을 실행하세요."
            )
        super().__init__(config)
        self.port = self.config.get("port", 8501)

    def render(self, metrics: Optional[Dict[str, Any]] = None) -> None:
        """
        대시보드 렌더링

        Args:
            metrics: 현재 메트릭 (선택적)
        """
        if not self.enabled:
            return

        st.set_page_config(
            page_title="Responsible AI Dashboard",
            page_icon="🤖",
            layout="wide",
        )

        st.title("🤖 Responsible AI 모니터링 대시보드")

        if metrics:
            self.log_metrics(metrics)
            self._render_overview(metrics)
            self._render_category_metrics(metrics)
            self._render_trends()
        else:
            latest = self.get_latest_metrics()
            if latest:
                self._render_overview(latest)
                self._render_category_metrics(latest)
                self._render_trends()
            else:
                st.info("메트릭 데이터가 없습니다. 평가를 수행하면 대시보드가 업데이트됩니다.")

    def _render_overview(self, metrics: Dict[str, Any]):
        """개요 섹션 렌더링"""
        st.header("📊 개요")

        overall_score = metrics.get("overall_responsible_ai_score", 0.0)
        is_responsible = metrics.get("is_responsible", False)

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "종합 Responsible AI 점수",
                f"{overall_score:.3f}",
                delta="✅ 준수" if is_responsible else "⚠️ 미준수",
            )

        with col2:
            fairness_score = metrics.get("fairness", {}).get("overall_fairness_score", 0.0)
            st.metric("공정성 점수", f"{fairness_score:.3f}")

        with col3:
            transparency_score = metrics.get("transparency", {}).get("overall_transparency_score", 0.0)
            st.metric("투명성 점수", f"{transparency_score:.3f}")

        with col4:
            privacy_score = metrics.get("privacy", {}).get("overall_privacy_score", 0.0)
            st.metric("프라이버시 점수", f"{privacy_score:.3f}")

        # 종합 점수 게이지 차트
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=overall_score * 100,
                domain={"x": [0, 1], "y": [0, 1]},
                title={"text": "Responsible AI 점수"},
                gauge={
                    "axis": {"range": [None, 100]},
                    "bar": {"color": "darkblue"},
                    "steps": [
                        {"range": [0, 60], "color": "lightgray"},
                        {"range": [60, 80], "color": "gray"},
                    ],
                    "threshold": {
                        "line": {"color": "red", "width": 4},
                        "thickness": 0.75,
                        "value": 75,
                    },
                },
            )
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

    def _render_category_metrics(self, metrics: Dict[str, Any]):
        """카테고리별 메트릭 렌더링"""
        st.header("📈 카테고리별 메트릭")

        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
        category_scores = []

        for category in categories:
            if category in metrics:
                score = metrics[category].get(f"overall_{category}_score", 0.0)
                category_scores.append({"카테고리": category, "점수": score})

        if category_scores:
            df = pd.DataFrame(category_scores)

            fig = px.bar(
                df,
                x="카테고리",
                y="점수",
                color="점수",
                color_continuous_scale="RdYlGn",
                title="카테고리별 Responsible AI 점수",
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

            # 상세 메트릭 테이블
            st.subheader("상세 메트릭")
            detail_data = []
            for category in categories:
                if category in metrics:
                    category_metrics = metrics[category].get("metrics", {})
                    for metric_name, metric_value in category_metrics.items():
                        if isinstance(metric_value, (int, float)):
                            detail_data.append({
                                "카테고리": category,
                                "메트릭": metric_name,
                                "값": metric_value,
                            })

            if detail_data:
                detail_df = pd.DataFrame(detail_data)
                st.dataframe(detail_df, use_container_width=True)

    def _render_trends(self) -> None:
        """트렌드 차트 렌더링"""
        if len(self.metrics_history) < 2:
            return

        st.header("📉 트렌드 분석")

        # 시간별 종합 점수 추이
        overall_scores = [
            entry["metrics"].get("overall_responsible_ai_score", 0.0)
            for entry in self.metrics_history
        ]

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                y=overall_scores,
                mode="lines+markers",
                name="종합 점수",
                line=dict(color="blue", width=2),
            )
        )
        fig.add_hline(
            y=0.75,
            line_dash="dash",
            line_color="red",
            annotation_text="임계값 (0.75)",
        )
        fig.update_layout(
            title="Responsible AI 점수 추이",
            xaxis_title="평가 횟수",
            yaxis_title="점수",
            height=400,
        )
        st.plotly_chart(fig, use_container_width=True)

    def start(self) -> None:
        """대시보드 시작"""
        import subprocess
        import sys
        from pathlib import Path

        # Streamlit 앱 스크립트 경로
        app_script = Path(__file__).parent.parent.parent / "scripts" / "streamlit_app.py"
        
        # 앱 스크립트가 없으면 생성
        if not app_script.exists():
            self._create_streamlit_app_script(app_script)

        # Streamlit 앱 실행
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", str(app_script),
            "--server.port", str(self.port)
        ])

    def _create_streamlit_app_script(self, script_path: Path) -> None:
        """Streamlit 앱 스크립트 생성"""
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        script_content = '''"""
Streamlit 대시보드 앱
"""
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import yaml
from src.monitoring.dashboard_factory import DashboardFactory

# 설정 로드
config_path = project_root / "config.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

# 대시보드 생성 및 실행
dashboard = DashboardFactory.get_default(config)
if dashboard:
    dashboard.render()
'''
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(script_content)

