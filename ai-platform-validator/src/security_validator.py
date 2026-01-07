"""
보안 검증 모듈
"""
import re
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class SecurityValidationResult:
    """보안 검증 결과"""
    status: str
    api_key_security_score: float
    data_encryption_score: float
    access_control_score: float
    rate_limiting_score: float
    issues: List[str]
    details: Dict[str, Any]


class SecurityValidator:
    """보안 검증 클래스"""

    def validate(
        self,
        api_key: Optional[str] = None,
        prompt: Optional[str] = None,
        response: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> SecurityValidationResult:
        """
        보안 검증 수행

        Args:
            api_key: API 키 (선택적, 실제로는 검증하지 않음)
            prompt: 사용자 프롬프트
            response: AI 응답
            config: 설정 정보

        Returns:
            보안 검증 결과
        """
        api_key_score, api_key_issues = self._check_api_key_security(api_key)
        encryption_score, encryption_issues = self._check_data_encryption(config)
        access_control_score, access_control_issues = self._check_access_control(config)
        rate_limiting_score, rate_limiting_issues = self._check_rate_limiting(config)

        all_issues = api_key_issues + encryption_issues + access_control_issues + rate_limiting_issues
        overall_score = (api_key_score + encryption_score + access_control_score + rate_limiting_score) / 4.0

        status = "pass" if overall_score >= 0.8 else ("warning" if overall_score >= 0.6 else "fail")

        return SecurityValidationResult(
            status=status,
            api_key_security_score=api_key_score,
            data_encryption_score=encryption_score,
            access_control_score=access_control_score,
            rate_limiting_score=rate_limiting_score,
            issues=all_issues,
            details={
                "api_key_issues": api_key_issues,
                "encryption_issues": encryption_issues,
                "access_control_issues": access_control_issues,
                "rate_limiting_issues": rate_limiting_issues,
            },
        )

    def _check_api_key_security(self, api_key: Optional[str]) -> tuple[float, List[str]]:
        """
        API 키 보안 검사

        Args:
            api_key: API 키 (실제로는 검증하지 않음)

        Returns:
            (API 키 보안 점수, 발견된 이슈 리스트)
        """
        issues = []

        # API 키가 환경 변수에 저장되어 있는지 확인
        if api_key:
            # API 키가 코드에 하드코딩되어 있으면 경고
            issues.append("API 키가 코드에 직접 포함되어 있을 수 있습니다. 환경 변수 사용을 권장합니다.")

        # 환경 변수에서 API 키 확인
        env_vars = ["OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GOOGLE_API_KEY", "AZURE_OPENAI_API_KEY"]
        has_env_key = any(os.getenv(var) for var in env_vars)

        if not has_env_key:
            issues.append("환경 변수에 API 키가 설정되어 있지 않습니다.")

        # 점수 계산
        score = 0.9 if has_env_key and not api_key else 0.7

        return float(score), issues

    def _check_data_encryption(self, config: Optional[Dict[str, Any]]) -> tuple[float, List[str]]:
        """
        데이터 암호화 검사

        Args:
            config: 설정 정보

        Returns:
            (데이터 암호화 점수, 발견된 이슈 리스트)
        """
        issues = []

        if config:
            encryption_enabled = config.get("encryption", {}).get("enabled", False)
            if not encryption_enabled:
                issues.append("데이터 암호화가 활성화되어 있지 않습니다.")
        else:
            issues.append("암호화 설정 정보가 없습니다.")

        # 점수 계산
        score = 0.8 if not issues else 0.6

        return float(score), issues

    def _check_access_control(self, config: Optional[Dict[str, Any]]) -> tuple[float, List[str]]:
        """
        접근 제어 검사

        Args:
            config: 설정 정보

        Returns:
            (접근 제어 점수, 발견된 이슈 리스트)
        """
        issues = []

        if config:
            access_control_enabled = config.get("access_control", {}).get("enabled", False)
            if not access_control_enabled:
                issues.append("접근 제어가 활성화되어 있지 않습니다.")

            # 인증 방식 확인
            auth_method = config.get("access_control", {}).get("auth_method", None)
            if not auth_method:
                issues.append("인증 방식이 설정되어 있지 않습니다.")
        else:
            issues.append("접근 제어 설정 정보가 없습니다.")

        # 점수 계산
        score = 0.85 if not issues else 0.6

        return float(score), issues

    def _check_rate_limiting(self, config: Optional[Dict[str, Any]]) -> tuple[float, List[str]]:
        """
        Rate Limiting 검사

        Args:
            config: 설정 정보

        Returns:
            (Rate Limiting 점수, 발견된 이슈 리스트)
        """
        issues = []

        if config:
            rate_limiting_enabled = config.get("rate_limiting", {}).get("enabled", False)
            if not rate_limiting_enabled:
                issues.append("Rate Limiting이 활성화되어 있지 않습니다.")

            # Rate limit 값 확인
            rate_limit = config.get("rate_limiting", {}).get("limit", None)
            if rate_limit is None:
                issues.append("Rate limit 값이 설정되어 있지 않습니다.")
        else:
            issues.append("Rate Limiting 설정 정보가 없습니다.")

        # 점수 계산
        score = 0.8 if not issues else 0.6

        return float(score), issues
