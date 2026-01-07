"""
EU AI Act 준수 검증 모듈
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class EUAIActComplianceResult:
    """EU AI Act 준수 검증 결과"""
    status: str
    risk_level: str
    compliance_score: float
    requirements_met: List[str]
    requirements_failed: List[str]
    details: Dict[str, Any]


class EUAIActValidator:
    """EU AI Act 준수 검증 클래스"""

    RISK_LEVELS = {
        "minimal": "최소 위험",
        "limited": "제한적 위험",
        "high": "높은 위험",
        "unacceptable": "허용 불가 위험"
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: EU AI Act 설정
        """
        self.config = config.get("compliance", {}).get("eu_ai_act", {})
        self.enabled = self.config.get("enabled", True)
        self.logger = logging.getLogger(__name__)

    def validate(
        self,
        model_info: Dict[str, Any],
        use_case: str,
        metrics: Optional[Dict[str, Any]] = None
    ) -> EUAIActComplianceResult:
        """
        EU AI Act 준수 검증 수행

        Args:
            model_info: 모델 정보
            use_case: 사용 사례
            metrics: Responsible AI 평가 메트릭

        Returns:
            EU AI Act 준수 검증 결과
        """
        if not self.enabled:
            return EUAIActComplianceResult(
                status="skipped",
                risk_level="unknown",
                compliance_score=0.0,
                requirements_met=[],
                requirements_failed=[],
                details={"message": "EU AI Act 검증이 비활성화되어 있습니다."}
            )

        # 위험 수준 결정
        risk_level = self._determine_risk_level(use_case, model_info)

        # 요구사항 검증
        requirements_met, requirements_failed = self._check_requirements(
            risk_level, model_info, metrics
        )

        # 준수 점수 계산
        total_requirements = len(requirements_met) + len(requirements_failed)
        compliance_score = len(requirements_met) / total_requirements if total_requirements > 0 else 0.0

        # 상태 결정
        if compliance_score >= 0.9:
            status = "compliant"
        elif compliance_score >= 0.7:
            status = "mostly_compliant"
        else:
            status = "non_compliant"

        return EUAIActComplianceResult(
            status=status,
            risk_level=risk_level,
            compliance_score=compliance_score,
            requirements_met=requirements_met,
            requirements_failed=requirements_failed,
            details={
                "risk_level_description": self.RISK_LEVELS.get(risk_level, "알 수 없음"),
                "validation_date": datetime.now().isoformat(),
            }
        )

    def _determine_risk_level(self, use_case: str, model_info: Dict[str, Any]) -> str:
        """
        위험 수준 결정

        Args:
            use_case: 사용 사례
            model_info: 모델 정보

        Returns:
            위험 수준
        """
        # 사용 사례 기반 위험 수준 매핑
        high_risk_cases = [
            "credit_scoring",
            "recruitment",
            "criminal_justice",
            "biometric_identification",
        ]

        limited_risk_cases = [
            "recommendation",
            "content_moderation",
            "chatbot",
        ]

        if use_case in high_risk_cases:
            return "high"
        elif use_case in limited_risk_cases:
            return "limited"
        else:
            return "minimal"

    def _check_requirements(
        self,
        risk_level: str,
        model_info: Dict[str, Any],
        metrics: Optional[Dict[str, Any]]
    ) -> tuple[List[str], List[str]]:
        """
        요구사항 검증

        Args:
            risk_level: 위험 수준
            model_info: 모델 정보
            metrics: Responsible AI 평가 메트릭

        Returns:
            (충족된 요구사항, 미충족 요구사항)
        """
        requirements_met = []
        requirements_failed = []

        # 공통 요구사항
        if model_info.get("transparency", False):
            requirements_met.append("투명성")
        else:
            requirements_failed.append("투명성")

        if model_info.get("human_oversight", False):
            requirements_met.append("인간 감독")
        else:
            requirements_failed.append("인간 감독")

        # 높은 위험 수준 요구사항
        if risk_level == "high":
            if metrics and metrics.get("overall_responsible_ai_score", 0.0) >= 0.8:
                requirements_met.append("높은 Responsible AI 점수")
            else:
                requirements_failed.append("높은 Responsible AI 점수")

            if model_info.get("risk_management", False):
                requirements_met.append("위험 관리 시스템")
            else:
                requirements_failed.append("위험 관리 시스템")

            if model_info.get("data_governance", False):
                requirements_met.append("데이터 거버넌스")
            else:
                requirements_failed.append("데이터 거버넌스")

        return requirements_met, requirements_failed

    def generate_compliance_report(self, result: EUAIActComplianceResult) -> str:
        """
        준수 리포트 생성

        Args:
            result: 검증 결과

        Returns:
            리포트 문자열
        """
        report = f"""
EU AI Act 준수 검증 리포트
==========================

검증 일시: {result.details.get('validation_date', 'N/A')}
위험 수준: {result.risk_level} ({result.details.get('risk_level_description', 'N/A')})
준수 점수: {result.compliance_score:.2%}
상태: {result.status}

충족된 요구사항:
{chr(10).join(f'  ✓ {req}' for req in result.requirements_met)}

미충족 요구사항:
{chr(10).join(f'  ✗ {req}' for req in result.requirements_failed)}
"""
        return report
