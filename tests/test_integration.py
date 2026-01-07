"""
통합 테스트
"""

import pytest
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestIntegration:
    """통합 테스트 클래스"""

    def test_project_structure(self):
        """프로젝트 구조 확인"""
        assert (project_root / "responsible_ai_automation").exists()
        assert (project_root / "ai-platform-validator").exists()
        assert (project_root / "responsible-ai-guidelines").exists()
        assert (project_root / "responsible-ai-policy").exists()

    def test_responsible_ai_automation_imports(self):
        """Responsible AI Automation 모듈 import 테스트"""
        try:
            from main import ResponsibleAIAutomationSystem
            assert ResponsibleAIAutomationSystem is not None
        except ImportError:
            pytest.skip("Responsible AI Automation 모듈을 찾을 수 없습니다.")

    def test_ai_platform_validator_imports(self):
        """AI Platform Validator 모듈 import 테스트"""
        try:
            sys.path.insert(0, str(project_root / "ai-platform-validator"))
            from src.validator import AIPlatformValidator
            assert AIPlatformValidator is not None
        except ImportError:
            pytest.skip("AI Platform Validator 모듈을 찾을 수 없습니다.")

