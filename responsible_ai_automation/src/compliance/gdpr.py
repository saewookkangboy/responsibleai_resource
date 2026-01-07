"""
GDPR 규정 준수 검증 모듈
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class GDPRCompliance:
    """GDPR 규정 준수 검증 클래스"""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}

    def check_requirements(self, metrics: Dict[str, Any], data_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GDPR 요구사항 확인

        Args:
            metrics: Responsible AI 메트릭
            data_info: 데이터 정보 (선택적)

        Returns:
            요구사항 준수 결과
        """
        results = {
            "requirements": {},
            "compliant": True,
            "timestamp": datetime.now().isoformat()
        }

        # 요구사항 1: 데이터 보호
        privacy_score = metrics.get("privacy", {}).get("overall_privacy_score", 0.0)
        results["requirements"]["data_protection"] = {
            "required": True,
            "score": privacy_score,
            "compliant": privacy_score >= 0.8,
            "description": "개인 데이터 보호 및 프라이버시"
        }

        # 요구사항 2: 데이터 익명화
        anonymization_score = metrics.get("privacy", {}).get("data_anonymization_score", 0.0)
        results["requirements"]["anonymization"] = {
            "required": True,
            "score": anonymization_score,
            "compliant": anonymization_score >= 0.8,
            "description": "개인 식별 정보 익명화"
        }

        # 요구사항 3: 접근 제어
        access_control_score = metrics.get("privacy", {}).get("access_control_score", 0.0)
        results["requirements"]["access_control"] = {
            "required": True,
            "score": access_control_score,
            "compliant": access_control_score >= 0.8,
            "description": "데이터 접근 제어 및 권한 관리"
        }

        # 요구사항 4: 투명성 (사용자에게 정보 제공)
        transparency_score = metrics.get("transparency", {}).get("overall_transparency_score", 0.0)
        results["requirements"]["transparency"] = {
            "required": True,
            "score": transparency_score,
            "compliant": transparency_score >= 0.7,
            "description": "데이터 처리에 대한 투명성"
        }

        # 요구사항 5: 책임성
        accountability_score = metrics.get("accountability", {}).get("overall_accountability_score", 0.0)
        results["requirements"]["accountability"] = {
            "required": True,
            "score": accountability_score,
            "compliant": accountability_score >= 0.7,
            "description": "데이터 처리 책임성"
        }

        # 전체 준수 여부
        results["compliant"] = all(
            req["compliant"] for req in results["requirements"].values()
        )

        return results

    def generate_compliance_report(self, metrics: Dict[str, Any], data_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        GDPR 규정 준수 리포트 생성

        Args:
            metrics: Responsible AI 메트릭
            data_info: 데이터 정보 (선택적)

        Returns:
            규정 준수 리포트
        """
        compliance_check = self.check_requirements(metrics, data_info)
        
        report = {
            "regulation": "GDPR",
            "assessment_date": datetime.now().isoformat(),
            "overall_compliant": compliance_check["compliant"],
            "requirements": compliance_check["requirements"],
            "recommendations": self._generate_recommendations(compliance_check)
        }

        return report

    def _generate_recommendations(self, compliance_check: Dict[str, Any]) -> List[str]:
        """
        개선 권장사항 생성

        Args:
            compliance_check: 준수 확인 결과

        Returns:
            권장사항 리스트
        """
        recommendations = []

        for req_name, req_data in compliance_check["requirements"].items():
            if not req_data["compliant"]:
                recommendations.append(
                    f"{req_name} 점수를 {req_data['score']:.2f}에서 요구 수준 이상으로 개선해야 합니다."
                )

        if not recommendations:
            recommendations.append("모든 GDPR 요구사항을 충족하고 있습니다.")

        return recommendations

