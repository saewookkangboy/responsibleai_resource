"""
업데이트 조건 모듈
"""

import numpy as np
from typing import Dict, Any, Optional


class UpdateConditions:
    """업데이트 조건 확인 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 업데이트 설정 딕셔너리
        """
        self.config = config.get("auto_update", {})
        self.conditions_config = self.config.get("conditions", {})

    def check_all_conditions(
        self,
        current_metrics: Dict[str, Any],
        previous_metrics: Optional[Dict[str, Any]] = None,
        data_distribution_shift: Optional[float] = None,
    ) -> Dict[str, bool]:
        """
        모든 업데이트 조건 확인

        Args:
            current_metrics: 현재 Responsible AI 지표
            previous_metrics: 이전 Responsible AI 지표
            data_distribution_shift: 데이터 분포 변화 정도

        Returns:
            조건별 확인 결과 딕셔너리
        """
        results = {}

        # 성능 저하 감지
        if "performance_degradation" in self.conditions_config:
            results["performance_degradation"] = self._check_performance_degradation(
                current_metrics, previous_metrics
            )

        # 윤리 지표 임계값 위반
        if "ethics_threshold_breach" in self.conditions_config:
            results["ethics_threshold_breach"] = self._check_ethics_threshold_breach(
                current_metrics
            )

        # 데이터 분포 변화
        if "distribution_shift" in self.conditions_config:
            results["distribution_shift"] = self._check_distribution_shift(
                data_distribution_shift
            )

        return results

    def should_update(self, conditions: Dict[str, bool]) -> bool:
        """
        업데이트 필요 여부 확인

        Args:
            conditions: 조건별 확인 결과

        Returns:
            업데이트 필요 여부
        """
        return any(conditions.values())

    def _check_performance_degradation(
        self,
        current_metrics: Dict[str, Any],
        previous_metrics: Optional[Dict[str, Any]],
    ) -> bool:
        """성능 저하 감지"""
        if previous_metrics is None:
            return False

        config = self.conditions_config.get("performance_degradation", {})
        threshold = config.get("threshold", 0.05)

        current_score = current_metrics.get("overall_responsible_ai_score", 0.0)
        previous_score = previous_metrics.get("overall_responsible_ai_score", 0.0)

        degradation = previous_score - current_score
        return degradation >= threshold

    def _check_ethics_threshold_breach(self, current_metrics: Dict[str, Any]) -> bool:
        """윤리 지표 임계값 위반 확인"""
        config = self.conditions_config.get("ethics_threshold_breach", {})
        threshold = config.get("threshold", 0.1)

        overall_score = current_metrics.get("overall_responsible_ai_score", 0.0)
        return overall_score < (0.75 - threshold)  # 기준점 0.75에서 threshold만큼 낮으면 위반

    def _check_distribution_shift(self, distribution_shift: Optional[float]) -> bool:
        """데이터 분포 변화 확인"""
        if distribution_shift is None:
            return False

        config = self.conditions_config.get("distribution_shift", {})
        threshold = config.get("threshold", 0.2)

        return distribution_shift >= threshold

