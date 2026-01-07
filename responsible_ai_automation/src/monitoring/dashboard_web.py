"""
웹 기반 모니터링 대시보드
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

from .dashboard import MonitoringDashboard


class WebDashboard:
    """웹 기반 모니터링 대시보드"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 모니터링 설정
        """
        self.config = config
        self.dashboard = MonitoringDashboard(config)
        self.metrics_history: List[Dict[str, Any]] = []
        self.load_metrics_history()

    def load_metrics_history(self):
        """저장된 메트릭 히스토리 로드"""
        metrics_file = Path(self.config.get("model", {}).get("save_path", "./models")) / "metrics_history.json"
        if metrics_file.exists():
            try:
                with open(metrics_file, "r") as f:
                    self.metrics_history = json.load(f)
            except Exception:
                self.metrics_history = []

    def save_metrics(self, metrics: Dict[str, Any]):
        """메트릭 저장"""
        metrics_with_timestamp = {
            "timestamp": datetime.now().isoformat(),
            **metrics
        }
        self.metrics_history.append(metrics_with_timestamp)
        
        # 최근 1000개만 유지
        if len(self.metrics_history) > 1000:
            self.metrics_history = self.metrics_history[-1000:]
        
        # 파일에 저장
        metrics_file = Path(self.config.get("model", {}).get("save_path", "./models")) / "metrics_history.json"
        metrics_file.parent.mkdir(parents=True, exist_ok=True)
        with open(metrics_file, "w") as f:
            json.dump(self.metrics_history, f, indent=2)

    def render_overview(self):
        """전체 개요 대시보드"""
        st.title("Responsible AI 모니터링 대시보드")
        
        if not self.metrics_history:
            st.warning("아직 평가된 메트릭이 없습니다.")
            return
        
        latest_metrics = self.metrics_history[-1]
        
        # 전체 점수 표시
        col1, col2, col3, col4 = st.columns(4)
        
        overall_score = latest_metrics.get("overall_responsible_ai_score", 0.0)
        with col1:
            st.metric(
                "전체 Responsible AI 점수",
                f"{overall_score:.3f}",
                delta=f"{overall_score - 0.75:.3f}" if overall_score >= 0.75 else None
            )
        
        is_responsible = latest_metrics.get("is_responsible", False)
        with col2:
            status = "✓ 기준 충족" if is_responsible else "✗ 기준 미달"
            st.metric("Responsible AI 상태", status)
        
        with col3:
            st.metric("총 평가 횟수", len(self.metrics_history))
        
        with col4:
            if len(self.metrics_history) > 1:
                prev_score = self.metrics_history[-2].get("overall_responsible_ai_score", 0.0)
                change = overall_score - prev_score
                st.metric("변화량", f"{change:+.3f}")

    def render_category_metrics(self):
        """카테고리별 메트릭"""
        st.header("카테고리별 평가 점수")
        
        if not self.metrics_history:
            return
        
        latest_metrics = self.metrics_history[-1]
        
        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
        category_names = {
            "fairness": "공정성",
            "transparency": "투명성",
            "accountability": "책임성",
            "privacy": "프라이버시",
            "robustness": "견고성"
        }
        
        scores = []
        labels = []
        
        for category in categories:
            if category in latest_metrics:
                score_key = f"overall_{category}_score"
                score = latest_metrics[category].get(score_key, 0.0)
                scores.append(score)
                labels.append(category_names[category])
        
        if scores:
            fig = go.Figure(data=go.Bar(
                x=labels,
                y=scores,
                marker=dict(
                    color=scores,
                    colorscale='RdYlGn',
                    cmin=0,
                    cmax=1
                )
            ))
            fig.update_layout(
                title="카테고리별 Responsible AI 점수",
                yaxis=dict(range=[0, 1]),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_trend_chart(self):
        """트렌드 차트"""
        st.header("메트릭 트렌드")
        
        if len(self.metrics_history) < 2:
            st.info("트렌드를 표시하려면 최소 2개의 평가 결과가 필요합니다.")
            return
        
        df = pd.DataFrame(self.metrics_history)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        # 전체 점수 트렌드
        fig = px.line(
            df,
            x='timestamp',
            y='overall_responsible_ai_score',
            title='전체 Responsible AI 점수 트렌드',
            labels={'overall_responsible_ai_score': '점수', 'timestamp': '시간'}
        )
        fig.add_hline(y=0.75, line_dash="dash", line_color="red", annotation_text="기준선 (0.75)")
        st.plotly_chart(fig, use_container_width=True)
        
        # 카테고리별 트렌드
        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
        category_names = {
            "fairness": "공정성",
            "transparency": "투명성",
            "accountability": "책임성",
            "privacy": "프라이버시",
            "robustness": "견고성"
        }
        
        category_scores = {}
        for category in categories:
            scores = []
            for metrics in self.metrics_history:
                if category in metrics:
                    score_key = f"overall_{category}_score"
                    score = metrics[category].get(score_key, 0.0)
                    scores.append(score)
                else:
                    scores.append(0.0)
            category_scores[category_names[category]] = scores
        
        if category_scores:
            df_categories = pd.DataFrame(category_scores)
            df_categories['timestamp'] = df['timestamp']
            
            fig = px.line(
                df_categories,
                x='timestamp',
                y=list(category_names.values()),
                title='카테고리별 점수 트렌드',
                labels={'value': '점수', 'timestamp': '시간', 'variable': '카테고리'}
            )
            st.plotly_chart(fig, use_container_width=True)

    def render_detailed_metrics(self):
        """상세 메트릭"""
        st.header("상세 메트릭")
        
        if not self.metrics_history:
            return
        
        latest_metrics = self.metrics_history[-1]
        
        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
        category_names = {
            "fairness": "공정성",
            "transparency": "투명성",
            "accountability": "책임성",
            "privacy": "프라이버시",
            "robustness": "견고성"
        }
        
        for category in categories:
            if category in latest_metrics:
                with st.expander(category_names[category]):
                    category_data = latest_metrics[category]
                    st.json(category_data)

    def run(self):
        """대시보드 실행"""
        st.set_page_config(
            page_title="Responsible AI Dashboard",
            page_icon="🤖",
            layout="wide"
        )
        
        # 사이드바
        with st.sidebar:
            st.header("설정")
            auto_refresh = st.checkbox("자동 새로고침", value=False)
            refresh_interval = st.slider("새로고침 간격 (초)", 5, 60, 10)
            
            if st.button("메트릭 새로고침"):
                self.load_metrics_history()
                st.rerun()
        
        # 메인 대시보드
        self.render_overview()
        st.divider()
        
        col1, col2 = st.columns(2)
        
        with col1:
            self.render_category_metrics()
        
        with col2:
            self.render_trend_chart()
        
        st.divider()
        self.render_detailed_metrics()
        
        if auto_refresh:
            import time
            time.sleep(refresh_interval)
            st.rerun()


def main():
    """대시보드 실행 함수"""
    import yaml
    from pathlib import Path
    
    config_path = Path(__file__).parent.parent.parent / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    
    dashboard = WebDashboard(config)
    dashboard.run()


if __name__ == "__main__":
    main()

