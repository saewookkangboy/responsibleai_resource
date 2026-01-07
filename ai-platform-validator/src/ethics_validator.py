"""
AI 윤리 검증 모듈
"""
import re
from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class EthicsValidationResult:
    """AI 윤리 검증 결과"""
    status: str
    bias_score: float
    fairness_score: float
    transparency_score: float
    privacy_score: float
    issues: List[str]
    details: Dict[str, Any]


class EthicsValidator:
    """AI 윤리 검증 클래스"""

    # 편향성 관련 키워드
    BIAS_KEYWORDS = {
        "gender": ["남성", "여성", "male", "female", "man", "woman", "gender"],
        "race": ["인종", "race", "ethnicity", "흑인", "백인", "black", "white"],
        "age": ["나이", "age", "old", "young", "노인", "청년"],
        "religion": ["종교", "religion", "기독교", "불교", "islam"],
    }

    # 프라이버시 관련 패턴
    PRIVACY_PATTERNS = [
        r"\d{3}-\d{4}-\d{4}",  # 전화번호
        r"\d{6}-\d{7}",  # 주민등록번호
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # 카드번호
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # 이메일
    ]

    def validate(self, prompt: str, response: Optional[str] = None) -> EthicsValidationResult:
        """
        AI 윤리 검증 수행

        Args:
            prompt: 사용자 프롬프트
            response: AI 응답 (선택적)

        Returns:
            AI 윤리 검증 결과
        """
        text_to_check = response if response else prompt

        bias_score, bias_issues = self._check_bias(text_to_check)
        fairness_score, fairness_issues = self._check_fairness(text_to_check)
        transparency_score, transparency_issues = self._check_transparency(prompt, response)
        privacy_score, privacy_issues = self._check_privacy(text_to_check)

        all_issues = bias_issues + fairness_issues + transparency_issues + privacy_issues
        overall_score = (bias_score + fairness_score + transparency_score + privacy_score) / 4.0

        status = "pass" if overall_score >= 0.8 else ("warning" if overall_score >= 0.6 else "fail")

        return EthicsValidationResult(
            status=status,
            bias_score=bias_score,
            fairness_score=fairness_score,
            transparency_score=transparency_score,
            privacy_score=privacy_score,
            issues=all_issues,
            details={
                "bias_issues": bias_issues,
                "fairness_issues": fairness_issues,
                "transparency_issues": transparency_issues,
                "privacy_issues": privacy_issues,
            },
        )

    def _check_bias(self, text: str) -> tuple[float, List[str]]:
        """
        편향성 검사

        Args:
            text: 검사할 텍스트

        Returns:
            (편향성 점수, 발견된 이슈 리스트)
        """
        issues = []
        text_lower = text.lower()

        # 각 카테고리별 편향성 키워드 검사
        for category, keywords in self.BIAS_KEYWORDS.items():
            found_keywords = [kw for kw in keywords if kw.lower() in text_lower]
            if found_keywords:
                # 편향성 키워드가 발견되었지만, 이것만으로는 편향이라고 판단하기 어려움
                # 실제로는 더 정교한 분석 필요
                pass

        # 점수 계산: 편향성 키워드가 적을수록 높은 점수
        bias_count = sum(1 for keywords in self.BIAS_KEYWORDS.values() for kw in keywords if kw.lower() in text_lower)
        score = max(0.0, 1.0 - (bias_count * 0.1))

        return float(score), issues

    def _check_fairness(self, text: str) -> tuple[float, List[str]]:
        """
        공정성 검사

        Args:
            text: 검사할 텍스트

        Returns:
            (공정성 점수, 발견된 이슈 리스트)
        """
        issues = []
        text_lower = text.lower()

        # 차별적 표현 검사
        discriminatory_phrases = [
            "only for",
            "not for",
            "exclusively",
            "only",
            "제한",
            "제외",
        ]

        found_phrases = [phrase for phrase in discriminatory_phrases if phrase in text_lower]
        if found_phrases:
            issues.append(f"차별적 표현 발견: {', '.join(found_phrases)}")

        # 점수 계산
        score = max(0.0, 1.0 - (len(found_phrases) * 0.2))

        return float(score), issues

    def _check_transparency(self, prompt: str, response: Optional[str]) -> tuple[float, List[str]]:
        """
        투명성 검사

        Args:
            prompt: 사용자 프롬프트
            response: AI 응답

        Returns:
            (투명성 점수, 발견된 이슈 리스트)
        """
        issues = []

        # 프롬프트와 응답의 일관성 검사
        if response:
            # 응답이 프롬프트의 질문에 적절히 답변하는지 확인
            # 실제로는 더 정교한 분석 필요
            pass

        # 불확실성 표현 검사
        uncertainty_indicators = ["maybe", "perhaps", "might", "possibly", "아마도", "혹시"]
        if response:
            has_uncertainty = any(indicator in response.lower() for indicator in uncertainty_indicators)
            if has_uncertainty:
                # 불확실성을 표현하는 것은 투명성 측면에서 긍정적
                pass

        # 기본 점수
        score = 0.8

        return float(score), issues

    def _check_privacy(self, text: str) -> tuple[float, List[str]]:
        """
        프라이버시 검사

        Args:
            text: 검사할 텍스트

        Returns:
            (프라이버시 점수, 발견된 이슈 리스트)
        """
        issues = []

        # 개인정보 패턴 검사
        for pattern in self.PRIVACY_PATTERNS:
            matches = re.findall(pattern, text)
            if matches:
                issues.append(f"개인정보 패턴 발견: {pattern}")

        # 점수 계산: 개인정보 패턴이 발견되지 않으면 높은 점수
        score = max(0.0, 1.0 - (len(issues) * 0.3))

        return float(score), issues
