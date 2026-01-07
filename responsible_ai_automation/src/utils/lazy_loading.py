"""
지연 로딩 유틸리티 - 빠른 초기화를 위한 모듈
"""

from typing import Any, Callable, Optional
import functools


class LazyLoader:
    """지연 로딩 클래스"""
    
    def __init__(self, loader_func: Callable, *args, **kwargs):
        """
        Args:
            loader_func: 로딩 함수
            *args: 로더 함수 인자
            **kwargs: 로더 함수 키워드 인자
        """
        self._loader_func = loader_func
        self._args = args
        self._kwargs = kwargs
        self._loaded_value: Optional[Any] = None
        self._is_loaded = False
    
    def __call__(self) -> Any:
        """값 로드"""
        if not self._is_loaded:
            self._loaded_value = self._loader_func(*self._args, **self._kwargs)
            self._is_loaded = True
        return self._loaded_value
    
    @property
    def value(self) -> Any:
        """값 속성"""
        return self.__call__()
    
    def reset(self):
        """로드된 값 초기화"""
        self._loaded_value = None
        self._is_loaded = False


def lazy_property(func: Callable) -> property:
    """
    지연 속성 데코레이터
    
    Args:
        func: 속성 함수
    
    Returns:
        property 객체
    """
    attr_name = f"_lazy_{func.__name__}"
    
    @property
    @functools.wraps(func)
    def wrapper(self):
        if not hasattr(self, attr_name):
            setattr(self, attr_name, func(self))
        return getattr(self, attr_name)
    
    return wrapper

