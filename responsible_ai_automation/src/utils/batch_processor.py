"""
배치 처리 유틸리티 - 대규모 데이터 처리 최적화
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Iterator
from functools import wraps
import time
import logging


class BatchProcessor:
    """배치 처리 클래스"""

    def __init__(self, batch_size: int = 1000, max_workers: Optional[int] = None):
        """
        Args:
            batch_size: 배치 크기
            max_workers: 최대 워커 수 (None이면 CPU 코어 수)
        """
        self.batch_size = batch_size
        self.max_workers = max_workers
        self.logger = logging.getLogger(__name__)

    def process_in_batches(
        self,
        data: np.ndarray,
        process_func: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """
        데이터를 배치로 나누어 처리

        Args:
            data: 처리할 데이터
            process_func: 처리 함수
            *args: 함수에 전달할 위치 인자
            **kwargs: 함수에 전달할 키워드 인자

        Returns:
            처리 결과 리스트
        """
        results = []
        total_batches = (len(data) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(data), self.batch_size):
            batch = data[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1

            self.logger.debug(f"배치 {batch_num}/{total_batches} 처리 중...")

            try:
                result = process_func(batch, *args, **kwargs)
                results.append(result)
            except Exception as e:
                self.logger.error(f"배치 {batch_num} 처리 중 오류 발생: {e}")
                raise

        return results

    def process_parallel(
        self,
        data: np.ndarray,
        process_func: Callable,
        *args,
        **kwargs
    ) -> List[Any]:
        """
        데이터를 병렬로 처리

        Args:
            data: 처리할 데이터
            process_func: 처리 함수
            *args: 함수에 전달할 위치 인자
            **kwargs: 함수에 전달할 키워드 인자

        Returns:
            처리 결과 리스트
        """
        try:
            from concurrent.futures import ProcessPoolExecutor, as_completed
            import multiprocessing

            if self.max_workers is None:
                max_workers = multiprocessing.cpu_count()
            else:
                max_workers = self.max_workers

            # 데이터를 배치로 나누기
            batches = [
                data[i:i + self.batch_size]
                for i in range(0, len(data), self.batch_size)
            ]

            results = []
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                futures = {
                    executor.submit(process_func, batch, *args, **kwargs): i
                    for i, batch in enumerate(batches)
                }

                for future in as_completed(futures):
                    batch_idx = futures[future]
                    try:
                        result = future.result()
                        results.append((batch_idx, result))
                    except Exception as e:
                        self.logger.error(f"배치 {batch_idx} 처리 중 오류 발생: {e}")
                        raise

            # 결과를 원래 순서로 정렬
            results.sort(key=lambda x: x[0])
            return [result for _, result in results]

        except ImportError:
            self.logger.warning("병렬 처리를 사용할 수 없습니다. 순차 처리로 전환합니다.")
            return self.process_in_batches(data, process_func, *args, **kwargs)

    def chunk_dataframe(
        self,
        df: pd.DataFrame,
        chunk_size: Optional[int] = None
    ) -> Iterator[pd.DataFrame]:
        """
        데이터프레임을 청크로 나누기

        Args:
            df: 데이터프레임
            chunk_size: 청크 크기 (None이면 batch_size 사용)

        Yields:
            데이터프레임 청크
        """
        if chunk_size is None:
            chunk_size = self.batch_size

        for i in range(0, len(df), chunk_size):
            yield df.iloc[i:i + chunk_size]


def batch_process_decorator(batch_size: int = 1000):
    """
    배치 처리 데코레이터

    Args:
        batch_size: 배치 크기

    Returns:
        데코레이터 함수
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(data: np.ndarray, *args, **kwargs):
            processor = BatchProcessor(batch_size=batch_size)
            return processor.process_in_batches(data, func, *args, **kwargs)
        return wrapper
    return decorator


def parallel_process_decorator(batch_size: int = 1000, max_workers: Optional[int] = None):
    """
    병렬 처리 데코레이터

    Args:
        batch_size: 배치 크기
        max_workers: 최대 워커 수

    Returns:
        데코레이터 함수
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(data: np.ndarray, *args, **kwargs):
            processor = BatchProcessor(batch_size=batch_size, max_workers=max_workers)
            return processor.process_parallel(data, func, *args, **kwargs)
        return wrapper
    return decorator

