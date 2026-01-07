"""
성능 최적화 유틸리티 모듈
"""

import numpy as np
from typing import List, Callable, Any, Optional
from functools import lru_cache
from multiprocessing import Pool, cpu_count
import hashlib
import pickle


class PerformanceOptimizer:
    """성능 최적화 클래스"""

    @staticmethod
    def parallel_evaluate(
        evaluator_func: Callable,
        data_chunks: List[Any],
        n_processes: Optional[int] = None
    ) -> List[Any]:
        """
        병렬 평가 수행

        Args:
            evaluator_func: 평가 함수
            data_chunks: 데이터 청크 리스트
            n_processes: 프로세스 수 (None이면 CPU 코어 수)

        Returns:
            평가 결과 리스트
        """
        if n_processes is None:
            n_processes = min(cpu_count(), len(data_chunks))

        if n_processes <= 1:
            return [evaluator_func(chunk) for chunk in data_chunks]

        with Pool(processes=n_processes) as pool:
            results = pool.map(evaluator_func, data_chunks)

        return results

    @staticmethod
    def cache_result(func: Callable) -> Callable:
        """
        함수 결과 캐싱 데코레이터

        Args:
            func: 캐싱할 함수

        Returns:
            캐싱된 함수
        """
        cache_dict = {}

        def cached_func(*args, **kwargs):
            # 인자 기반 캐시 키 생성
            cache_key = PerformanceOptimizer._generate_cache_key(args, kwargs)

            if cache_key in cache_dict:
                return cache_dict[cache_key]

            result = func(*args, **kwargs)
            cache_dict[cache_key] = result
            return result

        return cached_func

    @staticmethod
    def _generate_cache_key(args: tuple, kwargs: dict) -> str:
        """
        캐시 키 생성

        Args:
            args: 함수 인자
            kwargs: 함수 키워드 인자

        Returns:
            캐시 키 문자열
        """
        # 인자를 해시 가능한 형태로 변환
        key_data = {
            'args': PerformanceOptimizer._hash_array(args),
            'kwargs': {k: PerformanceOptimizer._hash_array(v) if isinstance(v, np.ndarray) else v
                      for k, v in kwargs.items()}
        }

        key_str = str(key_data)
        return hashlib.md5(key_str.encode()).hexdigest()

    @staticmethod
    def _hash_array(arr: Any) -> str:
        """
        배열 해시 생성

        Args:
            arr: 배열 또는 스칼라

        Returns:
            해시 문자열
        """
        if isinstance(arr, np.ndarray):
            # 배열의 해시 생성 (크기와 데이터 기반)
            return hashlib.md5(
                str(arr.shape).encode() + arr.tobytes()
            ).hexdigest()
        elif isinstance(arr, (list, tuple)):
            return str([PerformanceOptimizer._hash_array(item) for item in arr])
        else:
            return str(arr)

    @staticmethod
    def optimize_memory_usage(data: np.ndarray, target_dtype: Optional[type] = None) -> np.ndarray:
        """
        메모리 사용량 최적화

        Args:
            data: 최적화할 데이터 배열
            target_dtype: 목표 데이터 타입 (None이면 자동 선택)

        Returns:
            최적화된 데이터 배열
        """
        if target_dtype is None:
            # float64를 float32로 변환 (메모리 절약)
            if data.dtype == np.float64:
                target_dtype = np.float32
            elif data.dtype == np.int64:
                target_dtype = np.int32
            else:
                return data

        if data.dtype != target_dtype:
            return data.astype(target_dtype)

        return data

    @staticmethod
    def sample_data(
        data: np.ndarray,
        sample_size: int,
        random_state: Optional[int] = None
    ) -> np.ndarray:
        """
        데이터 샘플링

        Args:
            data: 샘플링할 데이터
            sample_size: 샘플 크기
            random_state: 랜덤 시드

        Returns:
            샘플링된 데이터
        """
        if len(data) <= sample_size:
            return data

        rng = np.random.RandomState(random_state)
        indices = rng.choice(len(data), sample_size, replace=False)
        return data[indices]

