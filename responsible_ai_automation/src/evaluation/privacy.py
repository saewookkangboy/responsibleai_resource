"""
프라이버시(Privacy) 평가 모듈
"""

import numpy as np
from typing import Dict, Optional, Any


class PrivacyEvaluator:
    """AI 모델의 프라이버시를 평가하는 클래스"""
    
    def __init__(self, threshold: float = 0.8):
        """
        Args:
            threshold: 최소 프라이버시 점수
        """
        self.threshold = threshold
    
    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        differential_privacy_epsilon: Optional[float] = None,
        data_anonymization_level: Optional[float] = None,
        access_control_enabled: bool = True,
    ) -> Dict[str, float]:
        """
        프라이버시 지표를 평가합니다.
        
        Args:
            model: 평가할 모델
            X: 입력 데이터
            differential_privacy_epsilon: 차등 프라이버시 엡실론 값
            data_anonymization_level: 데이터 익명화 수준 (0-1)
            access_control_enabled: 접근 제어 활성화 여부
        
        Returns:
            프라이버시 지표 딕셔너리
        """
        results = {}
        
        # 1. 차등 프라이버시
        if differential_privacy_epsilon is not None:
            # 엡실론이 낮을수록 프라이버시 보호가 강함
            dp_score = max(0, 1 - (differential_privacy_epsilon / 10))
        else:
            dp_score = 0.5  # 기본값
        results["differential_privacy_score"] = dp_score
        
        # 2. 데이터 익명화
        if data_anonymization_level is not None:
            anonymization_score = data_anonymization_level
        else:
            anonymization_score = self._estimate_anonymization_level(X)
        results["data_anonymization_score"] = anonymization_score
        
        # 3. 접근 제어
        access_control_score = 1.0 if access_control_enabled else 0.0
        results["access_control_score"] = access_control_score
        
        # 4. 모델 메모리 누출 검사
        memory_leak_score = self._check_memory_leakage(model, X)
        results["memory_leakage_score"] = memory_leak_score
        
        # 전체 프라이버시 점수
        overall_score = (
            dp_score * 0.3
            + anonymization_score * 0.3
            + access_control_score * 0.2
            + memory_leak_score * 0.2
        )
        results["overall_privacy_score"] = overall_score
        results["is_private"] = overall_score >= self.threshold
        
        return results
    
    def _estimate_anonymization_level(self, X: np.ndarray) -> float:
        """데이터 익명화 수준을 추정합니다."""
        # 데이터의 고유값 비율을 기반으로 추정
        # 고유값이 많을수록 익명화가 잘 되어 있음
        unique_ratio = np.unique(X.flatten()).size / X.size
        return min(1.0, unique_ratio * 2)  # 정규화
    
    def _check_memory_leakage(self, model: Any, X: np.ndarray) -> float:
        """모델이 학습 데이터를 기억하는지 검사합니다."""
        # 간단한 멤버십 추론 공격 시뮬레이션
        # 실제로는 더 정교한 방법이 필요함
        try:
            # 모델의 예측 일관성 확인
            predictions_1 = model.predict(X[:10])
            predictions_2 = model.predict(X[:10])
            
            # 예측이 완전히 일치하면 메모리 누출 가능성
            consistency = np.mean(predictions_1 == predictions_2)
            
            # 일관성이 너무 높으면 (1.0) 메모리 누출 가능성
            # 일관성이 적당하면 (0.7-0.9) 정상
            if consistency > 0.99:
                return 0.5  # 의심스러움
            elif consistency > 0.7:
                return 0.9  # 정상
            else:
                return 0.7  # 낮은 일관성
        except:
            return 0.5  # 기본값

