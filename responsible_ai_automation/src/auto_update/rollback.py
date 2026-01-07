"""
롤백 관리 모듈
"""

import logging
import pickle
from pathlib import Path
from typing import Dict, Any, Optional


class RollbackManager:
    """롤백 관리 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 롤백 설정 딕셔너리
        """
        self.config = config.get("auto_update", {}).get("rollback", {})
        self.enabled = self.config.get("enabled", True)
        self.max_attempts = self.config.get("max_rollback_attempts", 3)
        self.performance_threshold = self.config.get("performance_threshold", 0.95)

        self.model_save_path = Path(config.get("model", {}).get("save_path", "./models"))
        self.model_save_path.mkdir(parents=True, exist_ok=True)

        self.checkpoint_history: list = []
        self.logger = logging.getLogger(__name__)

    def save_checkpoint(
        self, model: Any, metrics: Dict[str, Any], checkpoint_id: Optional[str] = None
    ):
        """
        체크포인트 저장

        Args:
            model: 저장할 모델
            metrics: 현재 평가 지표
            checkpoint_id: 체크포인트 ID (None이면 자동 생성)
        """
        if not self.enabled:
            return

        import datetime

        if checkpoint_id is None:
            checkpoint_id = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

        checkpoint_path = self.model_save_path / f"checkpoint_{checkpoint_id}.pkl"
        metrics_path = self.model_save_path / f"metrics_{checkpoint_id}.pkl"

        # 모델 저장
        with open(checkpoint_path, "wb") as f:
            pickle.dump(model, f)

        # 메트릭 저장
        with open(metrics_path, "wb") as f:
            pickle.dump(metrics, f)

        # 히스토리에 추가
        self.checkpoint_history.append(
            {
                "checkpoint_id": checkpoint_id,
                "checkpoint_path": str(checkpoint_path),
                "metrics_path": str(metrics_path),
                "metrics": metrics,
            }
        )

        self.logger.info(f"체크포인트 저장: {checkpoint_id}")

    def should_rollback(
        self, current_metrics: Dict[str, Any], previous_metrics: Dict[str, Any]
    ) -> bool:
        """
        롤백 필요 여부 확인

        Args:
            current_metrics: 현재 평가 지표
            previous_metrics: 이전 평가 지표

        Returns:
            롤백 필요 여부
        """
        if not self.enabled:
            return False

        current_score = current_metrics.get("overall_responsible_ai_score", 0.0)
        previous_score = previous_metrics.get("overall_responsible_ai_score", 0.0)

        # 성능이 이전의 performance_threshold 미만으로 떨어지면 롤백
        return current_score < (previous_score * self.performance_threshold)

    def rollback(self) -> Optional[Dict[str, Any]]:
        """
        이전 체크포인트로 롤백

        Returns:
            롤백된 체크포인트 정보 또는 None
        """
        if not self.enabled or len(self.checkpoint_history) < 2:
            return None

        # 가장 최근 체크포인트 제거
        self.checkpoint_history.pop()

        # 이전 체크포인트 로드
        previous_checkpoint = self.checkpoint_history[-1]

        checkpoint_path = Path(previous_checkpoint["checkpoint_path"])

        if not checkpoint_path.exists():
            self.logger.error(f"체크포인트 파일을 찾을 수 없음: {checkpoint_path}")
            return None

        import pickle

        with open(checkpoint_path, "rb") as f:
            model = pickle.load(f)

        self.logger.info(f"롤백 완료: {previous_checkpoint['checkpoint_id']}")

        return {
            "model": model,
            "checkpoint_info": previous_checkpoint,
        }

