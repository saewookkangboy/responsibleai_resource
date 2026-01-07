"""
전역 최적화 설정 및 유틸리티
"""

import os
from typing import Dict, Any, Optional
import numpy as np


class OptimizationConfig:
    """최적화 설정 클래스"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 설정 딕셔너리
        """
        perf_config = config.get("performance", {})
        
        self.use_parallel = perf_config.get("use_parallel", True)
        self.n_jobs = perf_config.get("n_jobs", -1)
        self.cache_enabled = perf_config.get("cache_enabled", True)
        self.cache_size = perf_config.get("cache_size", 100)
        self.sample_size = perf_config.get("sample_size")
        self.streaming = perf_config.get("streaming", False)
        
        # 환경 변수에서 오버라이드
        if os.getenv("RAI_USE_PARALLEL"):
            self.use_parallel = os.getenv("RAI_USE_PARALLEL").lower() == "true"
        if os.getenv("RAI_N_JOBS"):
            self.n_jobs = int(os.getenv("RAI_N_JOBS"))
    
    def get_sample_size(self, data_size: int) -> int:
        """
        샘플 크기 결정
        
        Args:
            data_size: 전체 데이터 크기
        
        Returns:
            샘플 크기
        """
        if self.sample_size is None:
            return data_size
        
        if isinstance(self.sample_size, float) and 0 < self.sample_size < 1:
            # 비율로 지정된 경우
            return int(data_size * self.sample_size)
        
        # 절대값으로 지정된 경우
        return min(self.sample_size, data_size)
    
    def should_use_parallel(self, data_size: int) -> bool:
        """
        병렬 처리 사용 여부 결정
        
        Args:
            data_size: 데이터 크기
        
        Returns:
            병렬 처리 사용 여부
        """
        if not self.use_parallel:
            return False
        
        # 작은 데이터는 병렬 처리 오버헤드가 더 큼
        return data_size > 1000


# 전역 최적화 설정 인스턴스
_global_optimization_config: Optional[OptimizationConfig] = None


def get_optimization_config(config: Dict[str, Any]) -> OptimizationConfig:
    """
    전역 최적화 설정 가져오기
    
    Args:
        config: 설정 딕셔너리
    
    Returns:
        최적화 설정 객체
    """
    global _global_optimization_config
    
    if _global_optimization_config is None:
        _global_optimization_config = OptimizationConfig(config)
    
    return _global_optimization_config


def optimize_data_for_evaluation(
    X: np.ndarray,
    y: np.ndarray,
    config: Dict[str, Any]
) -> tuple[np.ndarray, np.ndarray]:
    """
    평가를 위한 데이터 최적화
    
    Args:
        X: 입력 데이터
        y: 타겟 레이블
        config: 설정 딕셔너리
    
    Returns:
        최적화된 데이터 (X, y)
    """
    opt_config = get_optimization_config(config)
    
    # 샘플링
    sample_size = opt_config.get_sample_size(len(X))
    if sample_size < len(X):
        indices = np.random.choice(len(X), sample_size, replace=False)
        X = X[indices]
        y = y[indices]
    
    # 메모리 최적화
    from .performance import PerformanceOptimizer
    X = PerformanceOptimizer.optimize_memory_usage(X)
    
    return X, y

