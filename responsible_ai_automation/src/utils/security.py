"""
보안 유틸리티 - API 키 관리, Rate Limiting 등
"""

import os
import hashlib
import secrets
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from collections import defaultdict
import logging

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    import base64
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False


class APIKeyManager:
    """API 키 관리 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 보안 설정
        """
        self.config = config.get("security", {})
        self.key_storage_path = self.config.get("key_storage_path", "./.keys")
        self.logger = logging.getLogger(__name__)

        # 키 저장소 디렉토리 생성
        os.makedirs(self.key_storage_path, exist_ok=True)

    def get_api_key(self, key_name: str, from_env: bool = True) -> Optional[str]:
        """
        API 키 조회

        Args:
            key_name: 키 이름
            from_env: 환경 변수에서 먼저 조회할지 여부

        Returns:
            API 키 또는 None
        """
        if from_env:
            env_key = os.getenv(key_name)
            if env_key:
                return env_key

        # 파일에서 조회 (암호화된 경우)
        key_file = os.path.join(self.key_storage_path, f"{key_name}.key")
        if os.path.exists(key_file):
            try:
                with open(key_file, "r") as f:
                    encrypted_key = f.read().strip()
                return self._decrypt_key(encrypted_key)
            except Exception as e:
                self.logger.error(f"키 파일 읽기 실패: {e}")
                return None

        return None

    def store_api_key(self, key_name: str, key_value: str, encrypt: bool = True) -> bool:
        """
        API 키 저장

        Args:
            key_name: 키 이름
            key_value: 키 값
            encrypt: 암호화 여부

        Returns:
            저장 성공 여부
        """
        try:
            if encrypt and CRYPTOGRAPHY_AVAILABLE:
                encrypted_key = self._encrypt_key(key_value)
            else:
                encrypted_key = key_value

            key_file = os.path.join(self.key_storage_path, f"{key_name}.key")
            with open(key_file, "w") as f:
                f.write(encrypted_key)

            # 파일 권한 설정 (소유자만 읽기/쓰기)
            os.chmod(key_file, 0o600)

            self.logger.info(f"API 키 저장 완료: {key_name}")
            return True
        except Exception as e:
            self.logger.error(f"API 키 저장 실패: {e}")
            return False

    def rotate_api_key(self, key_name: str) -> Optional[str]:
        """
        API 키 로테이션

        Args:
            key_name: 키 이름

        Returns:
            새 API 키 또는 None
        """
        # 새 키 생성
        new_key = secrets.token_urlsafe(32)

        if self.store_api_key(key_name, new_key):
            self.logger.info(f"API 키 로테이션 완료: {key_name}")
            return new_key

        return None

    def _encrypt_key(self, key: str) -> str:
        """키 암호화"""
        if not CRYPTOGRAPHY_AVAILABLE:
            return key

        # 마스터 키 생성 (실제로는 안전한 곳에 저장해야 함)
        master_key = os.getenv("MASTER_ENCRYPTION_KEY", Fernet.generate_key().decode())
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"responsible_ai_salt",
            iterations=100000,
            backend=default_backend()
        )
        key_bytes = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
        fernet = Fernet(key_bytes)

        return fernet.encrypt(key.encode()).decode()

    def _decrypt_key(self, encrypted_key: str) -> str:
        """키 복호화"""
        if not CRYPTOGRAPHY_AVAILABLE:
            return encrypted_key

        try:
            master_key = os.getenv("MASTER_ENCRYPTION_KEY", Fernet.generate_key().decode())
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b"responsible_ai_salt",
                iterations=100000,
                backend=default_backend()
            )
            key_bytes = base64.urlsafe_b64encode(kdf.derive(master_key.encode()))
            fernet = Fernet(key_bytes)

            return fernet.decrypt(encrypted_key.encode()).decode()
        except Exception as e:
            self.logger.error(f"키 복호화 실패: {e}")
            return encrypted_key


class RateLimiter:
    """Rate Limiting 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: Rate Limiting 설정
        """
        self.config = config.get("security", {}).get("rate_limiting", {})
        self.enabled = self.config.get("enabled", True)
        self.default_limit = self.config.get("limit", 100)  # 기본: 시간당 100회
        self.window_seconds = self.config.get("window_seconds", 3600)  # 기본: 1시간

        # IP/사용자별 요청 기록
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
        self.logger = logging.getLogger(__name__)

    def is_allowed(self, identifier: str, limit: Optional[int] = None) -> bool:
        """
        요청 허용 여부 확인

        Args:
            identifier: 요청자 식별자 (IP 주소, 사용자 ID 등)
            limit: 제한 횟수 (None이면 기본값 사용)

        Returns:
            허용 여부
        """
        if not self.enabled:
            return True

        if limit is None:
            limit = self.default_limit

        now = datetime.now()
        cutoff_time = now - timedelta(seconds=self.window_seconds)

        # 오래된 요청 기록 제거
        self.requests[identifier] = [
            req_time
            for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]

        # 제한 확인
        if len(self.requests[identifier]) >= limit:
            self.logger.warning(f"Rate limit 초과: {identifier} ({len(self.requests[identifier])}/{limit})")
            return False

        # 요청 기록 추가
        self.requests[identifier].append(now)
        return True

    def get_remaining(self, identifier: str, limit: Optional[int] = None) -> int:
        """
        남은 요청 횟수 조회

        Args:
            identifier: 요청자 식별자
            limit: 제한 횟수

        Returns:
            남은 요청 횟수
        """
        if limit is None:
            limit = self.default_limit

        now = datetime.now()
        cutoff_time = now - timedelta(seconds=self.window_seconds)

        self.requests[identifier] = [
            req_time
            for req_time in self.requests[identifier]
            if req_time > cutoff_time
        ]

        return max(0, limit - len(self.requests[identifier]))

    def reset(self, identifier: Optional[str] = None) -> None:
        """
        요청 기록 초기화

        Args:
            identifier: 요청자 식별자 (None이면 전체 초기화)
        """
        if identifier is None:
            self.requests.clear()
        else:
            self.requests.pop(identifier, None)


class SecurityManager:
    """통합 보안 관리 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: 보안 설정
        """
        self.config = config
        self.api_key_manager = APIKeyManager(config)
        self.rate_limiter = RateLimiter(config)
        self.logger = logging.getLogger(__name__)

    def validate_request(
        self,
        identifier: str,
        api_key: Optional[str] = None,
        required_key: Optional[str] = None
    ) -> tuple[bool, str]:
        """
        요청 검증

        Args:
            identifier: 요청자 식별자
            api_key: 제공된 API 키
            required_key: 필요한 API 키 이름

        Returns:
            (검증 성공 여부, 오류 메시지)
        """
        # Rate Limiting 확인
        if not self.rate_limiter.is_allowed(identifier):
            return False, "Rate limit exceeded"

        # API 키 검증
        if required_key:
            stored_key = self.api_key_manager.get_api_key(required_key)
            if not stored_key:
                return False, f"API key not found: {required_key}"

            if api_key != stored_key:
                return False, "Invalid API key"

        return True, ""
