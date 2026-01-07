"""
모델 버전 관리 시스템
"""

import mlflow
import mlflow.sklearn
from typing import Dict, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class ModelRegistry:
    """모델 버전 관리 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        mlflow.set_tracking_uri(config.get("mlflow", {}).get("tracking_uri", "file:./mlruns"))
        self.experiment_name = config.get("mlflow", {}).get("experiment_name", "responsible_ai")
        mlflow.set_experiment(self.experiment_name)

    def register_model(
        self,
        model: Any,
        metrics: Dict[str, Any],
        model_name: str = "responsible_ai_model",
        tags: Optional[Dict[str, str]] = None
    ) -> str:
        """
        모델 등록

        Args:
            model: 학습된 모델
            metrics: Responsible AI 메트릭
            model_name: 모델 이름
            tags: 태그 딕셔너리

        Returns:
            모델 버전
        """
        with mlflow.start_run():
            # 메트릭 로깅
            mlflow.log_metric("overall_responsible_ai_score", metrics.get("overall_responsible_ai_score", 0.0))
            mlflow.log_metric("is_responsible", 1.0 if metrics.get("is_responsible", False) else 0.0)
            
            for category in ["fairness", "transparency", "accountability", "privacy", "robustness"]:
                if category in metrics:
                    score_key = f"overall_{category}_score"
                    score = metrics[category].get(score_key, 0.0)
                    mlflow.log_metric(f"{category}_score", score)

            # 태그 추가
            if tags:
                mlflow.set_tags(tags)
            
            # Responsible AI 점수 기반 자동 태깅
            overall_score = metrics.get("overall_responsible_ai_score", 0.0)
            if overall_score >= 0.9:
                mlflow.set_tag("quality", "excellent")
            elif overall_score >= 0.75:
                mlflow.set_tag("quality", "good")
            else:
                mlflow.set_tag("quality", "needs_improvement")

            # 모델 저장
            mlflow.sklearn.log_model(model, "model")
            
            # 모델 등록
            model_uri = f"runs:/{mlflow.active_run().info.run_id}/model"
            mv = mlflow.register_model(model_uri, model_name)
            
            return mv.version

    def get_model_version(self, model_name: str, version: Optional[int] = None) -> Any:
        """
        모델 버전 조회

        Args:
            model_name: 모델 이름
            version: 버전 번호 (None이면 최신 버전)

        Returns:
            모델 객체
        """
        if version is None:
            model_uri = f"models:/{model_name}/latest"
        else:
            model_uri = f"models:/{model_name}/{version}"
        
        return mlflow.sklearn.load_model(model_uri)

    def compare_versions(self, model_name: str, versions: list) -> Dict[str, Any]:
        """
        여러 버전 비교

        Args:
            model_name: 모델 이름
            versions: 비교할 버전 리스트

        Returns:
            비교 결과
        """
        comparison = {}
        
        for version in versions:
            model = self.get_model_version(model_name, version)
            # 메트릭 조회 (실제 구현에서는 MLflow에서 메트릭 조회)
            comparison[f"version_{version}"] = {
                "version": version,
                "metrics": {}  # 실제로는 MLflow에서 조회
            }
        
        return comparison

