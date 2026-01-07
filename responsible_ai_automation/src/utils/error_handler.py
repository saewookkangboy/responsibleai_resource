"""
에러 핸들링 유틸리티 모듈
"""

import logging
import traceback
from typing import Optional, Callable, Any
from functools import wraps

logger = logging.getLogger(__name__)


class ErrorHandler:
    """에러 핸들링 클래스"""

    @staticmethod
    def handle_exception(
        func: Callable,
        default_return: Any = None,
        log_error: bool = True,
        reraise: bool = False
    ) -> Callable:
        """
        예외 처리 데코레이터

        Args:
            func: 처리할 함수
            default_return: 예외 발생 시 반환할 기본값
            log_error: 오류 로깅 여부
            reraise: 예외 재발생 여부

        Returns:
            예외 처리된 함수
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if log_error:
                    logger.error(
                        f"함수 {func.__name__} 실행 중 오류 발생: {e}\n"
                        f"인자: args={args}, kwargs={kwargs}\n"
                        f"트레이스백:\n{traceback.format_exc()}"
                    )

                if reraise:
                    raise

                return default_return

        return wrapper

    @staticmethod
    def validate_input(
        value: Any,
        expected_type: type,
        name: str = "value",
        allow_none: bool = False
    ) -> Any:
        """
        입력 값 검증

        Args:
            value: 검증할 값
            expected_type: 예상 타입
            name: 값의 이름 (오류 메시지용)
            allow_none: None 허용 여부

        Returns:
            검증된 값

        Raises:
            TypeError: 타입이 일치하지 않을 때
            ValueError: 값이 None이고 allow_none이 False일 때
        """
        if value is None:
            if allow_none:
                return None
            raise ValueError(f"{name}은(는) None일 수 없습니다.")

        if not isinstance(value, expected_type):
            raise TypeError(
                f"{name}은(는) {expected_type.__name__} 타입이어야 합니다. "
                f"현재 타입: {type(value).__name__}"
            )

        return value

    @staticmethod
    def safe_execute(
        func: Callable,
        *args,
        default_return: Any = None,
        **kwargs
    ) -> Any:
        """
        안전한 함수 실행

        Args:
            func: 실행할 함수
            *args: 함수 인자
            default_return: 예외 발생 시 반환할 기본값
            **kwargs: 함수 키워드 인자

        Returns:
            함수 실행 결과 또는 기본값
        """
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"함수 실행 중 오류 발생: {e}")
            return default_return

