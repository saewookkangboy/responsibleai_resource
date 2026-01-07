"""
EU AI Act 규정 준수 검증 모듈
"""

from typing import Dict, Any, List, Optional
from datetime import datetime


class EUAIActCompliance:
    """EU AI Act 규정 준수 검증 클래스"""

    RISK_LEVELS = {
        "unacceptable": "허용 불가",
        "high": "고위험",
        "limited": "제한적 위험",
        "minimal": "최소 위험"
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Args:
            config: 설정 딕셔너리
        """
        self.config = config or {}

    def assess_risk_level(self, metrics: Dict[str, Any]) -> str:
        """
        위험 수준 평가

        Args:
            metrics: Responsible AI 메트릭

        Returns:
            위험 수준
        """
        overall_score = metrics.get("overall_responsible_ai_score", 0.0)
        
        if overall_score < 0.5:
            return "unacceptable"
        elif overall_score < 0.65:
            return "high"
        elif overall_score < 0.8:
            return "limited"
        else:
            return "minimal"

    def check_requirements(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        EU AI Act 요구사항 확인

        Args:
            metrics: Responsible AI 메트릭

        Returns:
            요구사항 준수 결과
        """
        results = {
            "risk_level": self.assess_risk_level(metrics),
            "requirements": {},
            "compliant": True,
            "timestamp": datetime.now().isoformat()
        }

        # 요구사항 1: 투명성
        transparency_score = metrics.get("transparency", {}).get("overall_transparency_score", 0.0)
        results["requirements"]["transparency"] = {
            "required": True,
            "score": transparency_score,
            "compliant": transparency_score >= 0.7,
            "description": "AI 시스템의 투명성 및 설명 가능성"
        }

        # 요구사항 2: 공정성
        fairness_score = metrics.get("fairness", {}).get("overall_fairness_score", 0.0)
        results["requirements"]["fairness"] = {
            "required": True,
            "score": fairness_score,
            "compliant": fairness_score >= 0.7,
            "description": "편향 없는 공정한 AI 시스템"
        }

        # 요구사항 3: 프라이버시
        privacy_score = metrics.get("privacy", {}).get("overall_privacy_score", 0.0)
        results["requirements"]["privacy"] = {
            "required": True,
            "score": privacy_score,
            "compliant": privacy_score >= 0.8,
            "description": "개인정보 보호 및 데이터 프라이버시"
        }

        # 요구사항 4: 견고성
        robustness_score = metrics.get("robustness", {}).get("overall_robustness_score", 0.0)
        results["requirements"]["robustness"] = {
            "required": True,
            "score": robustness_score,
            "compliant": robustness_score >= 0.75,
            "description": "안전하고 신뢰할 수 있는 AI 시스템"
        }

        # 요구사항 5: 책임성
        accountability_score = metrics.get("accountability", {}).get("overall_accountability_score", 0.0)
        results["requirements"]["accountability"] = {
            "required": True,
            "score": accountability_score,
            "compliant": accountability_score >= 0.7,
            "description": "명확한 책임 소재 및 감사 추적"
        }

        # 전체 준수 여부
        results["compliant"] = all(
            req["compliant"] for req in results["requirements"].values()
        )

        return results

    def generate_compliance_report(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        규정 준수 리포트 생성

        Args:
            metrics: Responsible AI 메트릭

        Returns:
            규정 준수 리포트
        """
        compliance_check = self.check_requirements(metrics)
        
        report = {
            "regulation": "EU AI Act",
            "assessment_date": datetime.now().isoformat(),
            "risk_level": compliance_check["risk_level"],
            "risk_level_description": self.RISK_LEVELS.get(compliance_check["risk_level"], "알 수 없음"),
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
                    f"{req_name} 점수를 {req_data['score']:.2f}에서 0.7 이상으로 개선해야 합니다."
                )

        if not recommendations:
            recommendations.append("모든 EU AI Act 요구사항을 충족하고 있습니다.")

        return recommendations

