"""
병렬 평가 유틸리티 - 대규모 데이터 평가 최적화
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from .comprehensive import ComprehensiveEvaluator
from ..utils.batch_processor import BatchProcessor
import logging


class ParallelEvaluator:
    """병렬 평가 클래스"""

    def __init__(self, evaluator: ComprehensiveEvaluator, batch_size: int = 1000, max_workers: Optional[int] = None):
        """
        Args:
            evaluator: 종합 평가자
            batch_size: 배치 크기
            max_workers: 최대 워커 수
        """
        self.evaluator = evaluator
        self.batch_processor = BatchProcessor(batch_size=batch_size, max_workers=max_workers)
        self.logger = logging.getLogger(__name__)

    def evaluate_parallel(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        병렬 평가 수행

        Args:
            model: 학습된 모델
            X: 입력 데이터
            y: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임
            **kwargs: 추가 파라미터

        Returns:
            평가 결과 딕셔너리
        """
        # 대규모 데이터인 경우 배치 처리
        if len(X) > self.batch_processor.batch_size:
            self.logger.info(f"대규모 데이터 감지 ({len(X)} 샘플). 배치 처리 모드로 전환합니다.")

            # 데이터를 배치로 나누어 평가
            batch_results = []
            for i in range(0, len(X), self.batch_processor.batch_size):
                batch_end = min(i + self.batch_processor.batch_size, len(X))
                X_batch = X[i:batch_end]
                y_batch = y[i:batch_end]
                y_pred_batch = y_pred[i:batch_end]

                if sensitive_features is not None:
                    sensitive_batch = sensitive_features.iloc[i:batch_end]
                else:
                    sensitive_batch = None

                # 배치 평가
                batch_result = self.evaluator.evaluate(
                    model, X_batch, y_batch, y_pred_batch, sensitive_batch, **kwargs
                )
                batch_results.append(batch_result)

            # 결과 통합
            return self._aggregate_results(batch_results)
        else:
            # 소규모 데이터는 일반 평가
            return self.evaluator.evaluate(
                model, X, y, y_pred, sensitive_features, **kwargs
            )

    def _aggregate_results(self, batch_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        배치 결과 통합

        Args:
            batch_results: 배치별 평가 결과 리스트

        Returns:
            통합된 평가 결과
        """
        if not batch_results:
            return {}

        # 첫 번째 배치 결과를 기본으로 사용
        aggregated = batch_results[0].copy()

        # 카테고리별 점수 평균 계산
        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]

        for category in categories:
            if category in aggregated:
                scores = [
                    result[category].get(f"overall_{category}_score", 0.0)
                    for result in batch_results
                    if category in result
                ]
                if scores:
                    aggregated[category][f"overall_{category}_score"] = float(np.mean(scores))

        # 종합 점수 재계산
        overall_scores = [
            result.get("overall_responsible_ai_score", 0.0)
            for result in batch_results
        ]
        aggregated["overall_responsible_ai_score"] = float(np.mean(overall_scores))
        aggregated["is_responsible"] = aggregated["overall_responsible_ai_score"] >= 0.75

        # 배치 처리 정보 추가
        aggregated["batch_info"] = {
            "num_batches": len(batch_results),
            "batch_size": self.batch_processor.batch_size,
        }

        return aggregated

