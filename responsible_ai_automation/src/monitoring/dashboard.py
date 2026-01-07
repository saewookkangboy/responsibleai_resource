"""
모니터링 대시보드
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns


class MonitoringDashboard:
    """Responsible AI 지표를 모니터링하는 대시보드"""
    
    def __init__(self, log_dir: str = "./monitoring_logs", config: Optional[Dict] = None):
        """
        Args:
            log_dir: 로그 저장 디렉토리
            config: 설정 딕셔너리
        """
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or {}
        self.metrics_history = []
    
    def log_metrics(self, metrics: Dict[str, Any], timestamp: Optional[datetime] = None):
        """지표를 로깅합니다."""
        if timestamp is None:
            timestamp = datetime.now()
        
        log_entry = {
            "timestamp": timestamp.isoformat(),
            "metrics": metrics,
        }
        
        self.metrics_history.append(log_entry)
        
        # 파일에 저장
        log_file = self.log_dir / f"metrics_{timestamp.strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
        
        # 오래된 로그 정리
        self._cleanup_old_logs()
    
    def get_metrics_history(
        self, days: int = 7
    ) -> List[Dict[str, Any]]:
        """지난 N일간의 지표 이력을 반환합니다."""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        filtered_history = []
        for entry in self.metrics_history:
            entry_time = datetime.fromisoformat(entry["timestamp"])
            if entry_time >= cutoff_date:
                filtered_history.append(entry)
        
        return filtered_history
    
    def generate_report(self, output_path: Optional[str] = None) -> Dict[str, Any]:
        """모니터링 리포트를 생성합니다."""
        history = self.get_metrics_history(days=30)
        
        if not history:
            return {"status": "no_data", "message": "데이터가 없습니다."}
        
        # 데이터프레임 생성
        df_data = []
        for entry in history:
            row = {"timestamp": entry["timestamp"]}
            metrics = entry["metrics"]
            
            # 전체 점수
            row["overall_score"] = metrics.get("overall_responsible_ai_score", 0.0)
            
            # 각 카테고리 점수
            for category in ["fairness", "transparency", "accountability", "privacy", "robustness"]:
                if category in metrics:
                    row[f"{category}_score"] = metrics[category].get(
                        f"overall_{category}_score", 0.0
                    )
                else:
                    row[f"{category}_score"] = 0.0
            
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        
        # 통계 계산
        report = {
            "period": {
                "start": df["timestamp"].min().isoformat(),
                "end": df["timestamp"].max().isoformat(),
                "days": (df["timestamp"].max() - df["timestamp"].min()).days,
            },
            "overall_statistics": {
                "mean": float(df["overall_score"].mean()),
                "std": float(df["overall_score"].std()),
                "min": float(df["overall_score"].min()),
                "max": float(df["overall_score"].max()),
                "current": float(df["overall_score"].iloc[-1]),
            },
            "category_statistics": {},
        }
        
        # 각 카테고리별 통계
        for category in ["fairness", "transparency", "accountability", "privacy", "robustness"]:
            col_name = f"{category}_score"
            if col_name in df.columns:
                report["category_statistics"][category] = {
                    "mean": float(df[col_name].mean()),
                    "std": float(df[col_name].std()),
                    "min": float(df[col_name].min()),
                    "max": float(df[col_name].max()),
                    "current": float(df[col_name].iloc[-1]),
                }
        
        # 리포트 저장
        if output_path:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, "w") as f:
                json.dump(report, f, indent=2)
        
        return report
    
    def plot_metrics_trend(
        self, output_path: Optional[str] = None, days: int = 7
    ):
        """지표 추이를 시각화합니다."""
        history = self.get_metrics_history(days=days)
        
        if not history:
            print("시각화할 데이터가 없습니다.")
            return
        
        # 데이터프레임 생성
        df_data = []
        for entry in history:
            row = {"timestamp": entry["timestamp"]}
            metrics = entry["metrics"]
            
            row["overall"] = metrics.get("overall_responsible_ai_score", 0.0)
            for category in ["fairness", "transparency", "accountability", "privacy", "robustness"]:
                if category in metrics:
                    row[category] = metrics[category].get(
                        f"overall_{category}_score", 0.0
                    )
                else:
                    row[category] = 0.0
            
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values("timestamp")
        
        # 플롯 생성
        fig, axes = plt.subplots(2, 1, figsize=(12, 10))
        
        # 전체 점수 추이
        axes[0].plot(df["timestamp"], df["overall"], label="Overall Score", linewidth=2)
        axes[0].axhline(y=0.75, color="r", linestyle="--", label="Target (0.75)")
        axes[0].set_title("Overall Responsible AI Score Trend", fontsize=14, fontweight="bold")
        axes[0].set_xlabel("Time")
        axes[0].set_ylabel("Score")
        axes[0].legend()
        axes[0].grid(True, alpha=0.3)
        
        # 카테고리별 점수 추이
        for category in ["fairness", "transparency", "accountability", "privacy", "robustness"]:
            if category in df.columns:
                axes[1].plot(df["timestamp"], df[category], label=category.capitalize(), alpha=0.7)
        
        axes[1].set_title("Category-wise Score Trends", fontsize=14, fontweight="bold")
        axes[1].set_xlabel("Time")
        axes[1].set_ylabel("Score")
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if output_path:
            plt.savefig(output_path, dpi=300, bbox_inches="tight")
            print(f"플롯이 저장되었습니다: {output_path}")
        else:
            plt.show()
        
        plt.close()
    
    def _cleanup_old_logs(self):
        """오래된 로그를 정리합니다."""
        retention_days = self.config.get("monitoring", {}).get("metrics_retention_days", 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        for log_file in self.log_dir.glob("metrics_*.jsonl"):
            try:
                file_date = datetime.strptime(
                    log_file.stem.replace("metrics_", ""), "%Y%m%d"
                )
                if file_date < cutoff_date:
                    log_file.unlink()
            except:
                pass

