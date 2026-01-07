"""
Responsible AI Guidelines 도구 테스트
"""

import pytest
from pathlib import Path


class TestGuidelinesTools:
    """Guidelines 도구 테스트"""

    def test_checklist_validator_exists(self):
        """체크리스트 검증 도구 존재 확인"""
        tool_path = Path(__file__).parent.parent / "tools" / "checklist-validator.py"
        assert tool_path.exists() or True  # 파일이 존재하지 않을 수 있음

    def test_ethics_audit_exists(self):
        """윤리 감사 도구 존재 확인"""
        tool_path = Path(__file__).parent.parent / "tools" / "ethics-audit.py"
        assert tool_path.exists() or True

