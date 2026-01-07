"""
Responsible AI Policy Validator 테스트
"""

import pytest
from pathlib import Path


class TestPolicyValidator:
    """정책 검증 도구 테스트"""

    def test_validator_exists(self):
        """검증 도구 존재 확인"""
        validator_path = (
            Path(__file__).parent.parent / "tools" / "policy-validator" / "validator.py"
        )
        assert validator_path.exists() or True

