"""
MLflow 통합 모듈 - 모델 버전 관리
"""

from typing import Dict, Any, Optional
import logging

try:
    import mlflow
    import mlflow.sklearn
    import mlflow.pytorch
    import mlflow.tensorflow
    MLFLOW_AVAILABLE = True
except ImportError:
    MLFLOW_AVAILABLE = False


class MLflowIntegration:
    """MLflow 통합 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: MLflow 설정
        """
        self.config = config.get("model_versioning", {}).get("mlflow", {})
        self.enabled = self.config.get("enabled", False)
        self.tracking_uri = self.config.get("tracking_uri", "./mlruns")
        self.experiment_name = self.config.get("experiment_name", "responsible_ai")
        self.logger = logging.getLogger(__name__)

        if self.enabled and MLFLOW_AVAILABLE:
            mlflow.set_tracking_uri(self.tracking_uri)
            mlflow.set_experiment(self.experiment_name)

    def log_model(
        self,
        model: Any,
        model_name: str,
        metrics: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        tags: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        모델 로깅

        Args:
            model: 학습된 모델
            model_name: 모델 이름
            metrics: 평가 메트릭
            params: 하이퍼파라미터
            tags: 태그

        Returns:
            실행 ID 또는 None
        """
        if not self.enabled or not MLFLOW_AVAILABLE:
            return None

        try:
            with mlflow.start_run():
                # 메트릭 로깅
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(key, value)

                # 파라미터 로깅
                if params:
                    for key, value in params.items():
                        mlflow.log_param(key, value)

                # 태그 로깅
                if tags:
                    mlflow.set_tags(tags)

                # 모델 로깅
                if hasattr(model, "predict"):  # Scikit-learn 스타일
                    mlflow.sklearn.log_model(model, "model")
                elif hasattr(model, "forward"):  # PyTorch 스타일
                    mlflow.pytorch.log_model(model, "model")
                else:
                    mlflow.sklearn.log_model(model, "model")

                run_id = mlflow.active_run().info.run_id
                self.logger.info(f"모델 로깅 완료: {model_name} (run_id: {run_id})")
                return run_id

        except Exception as e:
            self.logger.error(f"모델 로깅 실패: {e}")
            return None

    def load_model(self, run_id: str, model_path: str = "model") -> Optional[Any]:
        """
        모델 로드

        Args:
            run_id: 실행 ID
            model_path: 모델 경로

        Returns:
            로드된 모델 또는 None
        """
        if not self.enabled or not MLFLOW_AVAILABLE:
            return None

        try:
            model = mlflow.sklearn.load_model(f"runs:/{run_id}/{model_path}")
            self.logger.info(f"모델 로드 완료: {run_id}")
            return model
        except Exception as e:
            self.logger.error(f"모델 로드 실패: {e}")
            return None

    def search_runs(
        self,
        filter_string: Optional[str] = None,
        max_results: int = 10
    ) -> list:
        """
        실행 검색

        Args:
            filter_string: 필터 문자열
            max_results: 최대 결과 수

        Returns:
            실행 리스트
        """
        if not self.enabled or not MLFLOW_AVAILABLE:
            return []

        try:
            experiment = mlflow.get_experiment_by_name(self.experiment_name)
            if experiment is None:
                return []

            runs = mlflow.search_runs(
                experiment_ids=[experiment.experiment_id],
                filter_string=filter_string,
                max_results=max_results
            )
            return runs.to_dict("records")
        except Exception as e:
            self.logger.error(f"실행 검색 실패: {e}")
            return []

