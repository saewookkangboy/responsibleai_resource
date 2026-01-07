"""
보안 유틸리티 모듈
"""

import os
import logging
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import base64

logger = logging.getLogger(__name__)


class SecurityManager:
    """보안 관리 클래스"""

    def __init__(self, encryption_key: Optional[str] = None):
        """
        Args:
            encryption_key: 암호화 키 (None이면 환경 변수에서 로드)
        """
        self.encryption_key = encryption_key or os.getenv("ENCRYPTION_KEY")
        if not self.encryption_key:
            logger.warning("암호화 키가 설정되지 않았습니다. 보안 기능이 제한됩니다.")
            self.cipher = None
        else:
            self.cipher = self._create_cipher(self.encryption_key)

    def _create_cipher(self, key: str) -> Fernet:
        """
        Fernet 암호화 객체 생성

        Args:
            key: 암호화 키

        Returns:
            Fernet 암호화 객체
        """
        # 키를 32바이트로 변환
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'responsible_ai_salt',
            iterations=100000,
            backend=default_backend()
        )
        key_bytes = kdf.derive(key.encode())
        return Fernet(base64.urlsafe_b64encode(key_bytes))

    def encrypt(self, data: str) -> Optional[str]:
        """
        데이터 암호화

        Args:
            data: 암호화할 데이터

        Returns:
            암호화된 데이터 또는 None
        """
        if not self.cipher:
            logger.error("암호화 키가 설정되지 않아 암호화할 수 없습니다.")
            return None

        try:
            encrypted = self.cipher.encrypt(data.encode())
            return encrypted.decode()
        except Exception as e:
            logger.error(f"암호화 중 오류 발생: {e}")
            return None

    def decrypt(self, encrypted_data: str) -> Optional[str]:
        """
        데이터 복호화

        Args:
            encrypted_data: 암호화된 데이터

        Returns:
            복호화된 데이터 또는 None
        """
        if not self.cipher:
            logger.error("암호화 키가 설정되지 않아 복호화할 수 없습니다.")
            return None

        try:
            decrypted = self.cipher.decrypt(encrypted_data.encode())
            return decrypted.decode()
        except Exception as e:
            logger.error(f"복호화 중 오류 발생: {e}")
            return None

    @staticmethod
    def mask_sensitive_data(data: dict) -> dict:
        """
        민감한 데이터 마스킹

        Args:
            data: 마스킹할 데이터 딕셔너리

        Returns:
            마스킹된 데이터 딕셔너리
        """
        sensitive_keys = ['api_key', 'password', 'secret', 'token', 'credential']
        masked_data = data.copy()

        for key in masked_data:
            if any(sensitive in key.lower() for sensitive in sensitive_keys):
                if isinstance(masked_data[key], str) and len(masked_data[key]) > 4:
                    masked_data[key] = masked_data[key][:2] + '***' + masked_data[key][-2:]
                else:
                    masked_data[key] = '***'

        return masked_data

    @staticmethod
    def generate_encryption_key() -> str:
        """
        새로운 암호화 키 생성

        Returns:
            생성된 암호화 키
        """
        return Fernet.generate_key().decode()

