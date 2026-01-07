"""
모델 업데이트 모듈
"""

import logging
from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

from .conditions import UpdateConditions
from ..evaluation.comprehensive import ComprehensiveEvaluator


class ModelUpdater:
    """모델 업데이트 클래스"""

    def __init__(self, config: Dict[str, Any], evaluator: ComprehensiveEvaluator):
        """
        Args:
            config: 업데이트 설정 딕셔너리
            evaluator: 종합 평가자
        """
        self.config = config.get("auto_update", {})
        self.evaluator = evaluator
        self.conditions = UpdateConditions(config)
        self.logger = logging.getLogger(__name__)

    def update(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
        previous_metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        모델 업데이트 수행

        Args:
            model: 현재 모델
            X: 입력 데이터
            y: 타겟 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터
            previous_metrics: 이전 평가 지표

        Returns:
            업데이트 결과 딕셔너리
        """
        self.logger.info("모델 업데이트 시작")

        # 현재 지표 평가
        current_metrics = self.evaluator.evaluate(
            model, X, y, y_pred, sensitive_features
        )

        # 업데이트 조건 확인
        conditions = self.conditions.check_all_conditions(
            current_metrics, previous_metrics
        )

        if not self.conditions.should_update(conditions):
            self.logger.info("업데이트 조건을 충족하지 않음")
            return {
                "updated": False,
                "reason": "업데이트 조건 미충족",
                "metrics": current_metrics,
            }

        # 실제 업데이트 로직 (여기서는 시뮬레이션)
        # 실제 구현에서는 모델 재학습 또는 파라미터 조정 수행
        self.logger.info("모델 업데이트 수행")

        # 업데이트 후 평가
        updated_metrics = self.evaluator.evaluate(
            model, X, y, y_pred, sensitive_features
        )

        return {
            "updated": True,
            "conditions": conditions,
            "previous_metrics": previous_metrics,
            "updated_metrics": updated_metrics,
            "improvement": updated_metrics.get("overall_responsible_ai_score", 0.0)
            - current_metrics.get("overall_responsible_ai_score", 0.0),
        }

