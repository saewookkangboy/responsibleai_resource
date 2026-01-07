"""
자동 업데이트 조건 검사 모듈
"""

import numpy as np
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from pathlib import Path
import json


class UpdateConditionChecker:
    """자동 업데이트 조건을 검사하는 클래스"""
    
    def __init__(self, config: Dict):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config
        self.auto_update_config = config.get("auto_update", {})
        self.conditions_config = self.auto_update_config.get("conditions", {})
        
        # 이전 성능 기록
        self.performance_history = []
        self.last_update_time = None
        self.history_file = Path("./update_history.json")
        self._load_history()
    
    def check_all_conditions(
        self,
        current_metrics: Dict[str, Any],
        previous_metrics: Optional[Dict[str, Any]] = None,
        data_distribution: Optional[Dict[str, float]] = None,
    ) -> Dict[str, bool]:
        """
        모든 업데이트 조건을 검사합니다.
        
        Args:
            current_metrics: 현재 평가 지표
            previous_metrics: 이전 평가 지표
            data_distribution: 현재 데이터 분포
        
        Returns:
            각 조건별 업데이트 필요 여부 딕셔너리
        """
        results = {}
        
        # 1. 성능 저하 검사
        results["performance_degradation"] = self._check_performance_degradation(
            current_metrics, previous_metrics
        )
        
        # 2. 윤리 지표 임계값 위반 검사
        results["ethics_threshold_breach"] = self._check_ethics_threshold_breach(
            current_metrics
        )
        
        # 3. 데이터 분포 변화 검사
        results["distribution_shift"] = self._check_distribution_shift(data_distribution)
        
        # 4. 정기 업데이트 검사
        results["scheduled"] = self._check_scheduled_update()
        
        return results
    
    def should_update(self, conditions: Dict[str, bool]) -> bool:
        """업데이트가 필요한지 결정합니다."""
        # 하나라도 True이면 업데이트 필요
        return any(conditions.values())
    
    def _check_performance_degradation(
        self,
        current_metrics: Dict[str, Any],
        previous_metrics: Optional[Dict[str, Any]],
    ) -> bool:
        """성능 저하를 검사합니다."""
        if previous_metrics is None:
            return False
        
        condition_config = self.conditions_config.get("performance_degradation", {})
        if not condition_config:
            return False
        
        threshold = condition_config.get("threshold", 0.05)
        
        # 전체 Responsible AI 점수 비교
        current_score = current_metrics.get("overall_responsible_ai_score", 0.0)
        previous_score = previous_metrics.get("overall_responsible_ai_score", 0.0)
        
        if previous_score == 0:
            return False
        
        degradation = (previous_score - current_score) / previous_score
        
        return degradation >= threshold
    
    def _check_ethics_threshold_breach(self, current_metrics: Dict[str, Any]) -> bool:
        """윤리 지표 임계값 위반을 검사합니다."""
        condition_config = self.conditions_config.get("ethics_threshold_breach", {})
        if not condition_config:
            return False
        
        threshold_breach = condition_config.get("threshold", 0.1)
        
        # 각 윤리 지표의 임계값 확인
        eval_config = self.config.get("evaluation", {})
        
        categories = ["fairness", "transparency", "accountability", "privacy", "robustness"]
        for category in categories:
            category_config = eval_config.get(category, {})
            category_threshold = category_config.get("threshold", 0.7)
            
            if category in current_metrics:
                category_score = current_metrics[category].get(
                    f"overall_{category}_score", 0.0
                )
                
                # 임계값보다 낮은 정도가 threshold_breach 이상이면 위반
                if category_score < category_threshold * (1 - threshold_breach):
                    return True
        
        return False
    
    def _check_distribution_shift(
        self, current_distribution: Optional[Dict[str, float]]
    ) -> bool:
        """데이터 분포 변화를 검사합니다."""
        condition_config = self.conditions_config.get("distribution_shift", {})
        if not condition_config or current_distribution is None:
            return False
        
        threshold = condition_config.get("threshold", 0.2)
        
        # 이전 분포와 비교 (간단한 예시)
        # 실제로는 더 정교한 분포 비교 방법이 필요함
        if not hasattr(self, "previous_distribution") or self.previous_distribution is None:
            self.previous_distribution = current_distribution
            return False
        
        # 분포 차이 계산
        shift = self._calculate_distribution_shift(
            self.previous_distribution, current_distribution
        )
        
        self.previous_distribution = current_distribution
        
        return shift >= threshold
    
    def _calculate_distribution_shift(
        self, dist1: Dict[str, float], dist2: Dict[str, float]
    ) -> float:
        """두 분포 간의 차이를 계산합니다."""
        # 공통 키에 대해 차이 계산
        common_keys = set(dist1.keys()) & set(dist2.keys())
        if not common_keys:
            return 1.0  # 완전히 다른 분포
        
        total_diff = 0.0
        for key in common_keys:
            diff = abs(dist1[key] - dist2[key])
            total_diff += diff
        
        return total_diff / len(common_keys) if common_keys else 1.0
    
    def _check_scheduled_update(self) -> bool:
        """정기 업데이트 시간인지 검사합니다."""
        condition_config = self.conditions_config.get("scheduled", {})
        if not condition_config:
            return False
        
        frequency = condition_config.get("frequency", "weekly")
        
        if self.last_update_time is None:
            return True  # 첫 업데이트
        
        now = datetime.now()
        time_since_update = now - self.last_update_time
        
        if frequency == "weekly":
            return time_since_update >= timedelta(weeks=1)
        elif frequency == "monthly":
            return time_since_update >= timedelta(days=30)
        elif frequency == "daily":
            return time_since_update >= timedelta(days=1)
        else:
            return False
    
    def record_update(self, update_time: Optional[datetime] = None):
        """업데이트를 기록합니다."""
        if update_time is None:
            update_time = datetime.now()
        
        self.last_update_time = update_time
        self._save_history()
    
    def _load_history(self):
        """업데이트 이력을 로드합니다."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    history = json.load(f)
                    if "last_update_time" in history:
                        self.last_update_time = datetime.fromisoformat(
                            history["last_update_time"]
                        )
            except:
                self.last_update_time = None
        else:
            self.last_update_time = None
    
    def _save_history(self):
        """업데이트 이력을 저장합니다."""
        history = {
            "last_update_time": (
                self.last_update_time.isoformat() if self.last_update_time else None
            ),
        }
        
        with open(self.history_file, "w") as f:
            json.dump(history, f)

