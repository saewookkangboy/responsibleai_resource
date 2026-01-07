"""
자동 업데이트 시스템 테스트
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from src.auto_update.conditions import UpdateConditions
from src.auto_update.updater import ModelUpdater
from src.auto_update.rollback import RollbackManager
from src.evaluation.comprehensive import ComprehensiveEvaluator


class TestUpdateConditions:
    """업데이트 조건 테스트 클래스"""

    def test_check_performance_degradation(self):
        """성능 저하 감지 테스트"""
        config = {
            "auto_update": {
                "conditions": {
                    "performance_degradation": {"threshold": 0.05}
                }
            }
        }

        conditions = UpdateConditions(config)

        current_metrics = {"overall_responsible_ai_score": 0.7}
        previous_metrics = {"overall_responsible_ai_score": 0.8}

        result = conditions._check_performance_degradation(current_metrics, previous_metrics)

        assert result is True

    def test_check_ethics_threshold_breach(self):
        """윤리 지표 임계값 위반 확인 테스트"""
        config = {
            "auto_update": {
                "conditions": {
                    "ethics_threshold_breach": {"threshold": 0.1}
                }
            }
        }

        conditions = UpdateConditions(config)

        current_metrics = {"overall_responsible_ai_score": 0.6}  # 0.75 - 0.1 = 0.65 미만

        result = conditions._check_ethics_threshold_breach(current_metrics)

        assert result is True

    def test_should_update(self):
        """업데이트 필요 여부 확인 테스트"""
        config = {"auto_update": {"conditions": {}}}
        conditions = UpdateConditions(config)

        # 업데이트 필요
        update_conditions = {"performance_degradation": True}
        assert conditions.should_update(update_conditions) is True

        # 업데이트 불필요
        no_update_conditions = {"performance_degradation": False}
        assert conditions.should_update(no_update_conditions) is False


class TestRollbackManager:
    """롤백 관리 테스트 클래스"""

    def test_should_rollback(self):
        """롤백 필요 여부 확인 테스트"""
        config = {
            "auto_update": {
                "rollback": {
                    "enabled": True,
                    "performance_threshold": 0.95
                }
            },
            "model": {"save_path": "./test_models"}
        }

        manager = RollbackManager(config)

        current_metrics = {"overall_responsible_ai_score": 0.7}
        previous_metrics = {"overall_responsible_ai_score": 0.8}

        # 0.7 < 0.8 * 0.95 = 0.76 이므로 롤백 필요
        result = manager.should_rollback(current_metrics, previous_metrics)

        assert result is True

    def test_rollback_disabled(self):
        """롤백이 비활성화된 경우 테스트"""
        config = {
            "auto_update": {
                "rollback": {
                    "enabled": False
                }
            },
            "model": {"save_path": "./test_models"}
        }

        manager = RollbackManager(config)

        current_metrics = {"overall_responsible_ai_score": 0.5}
        previous_metrics = {"overall_responsible_ai_score": 0.8}

        result = manager.should_rollback(current_metrics, previous_metrics)

        assert result is False

