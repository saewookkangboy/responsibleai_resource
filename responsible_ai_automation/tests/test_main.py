"""
메인 모듈 테스트
"""

import pytest
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from pathlib import Path
import yaml

from main import ResponsibleAIAutomationSystem


class TestResponsibleAIAutomationSystem:
    """Responsible AI Automation 시스템 테스트"""

    @pytest.fixture
    def config_file(self, tmp_path):
        """임시 설정 파일 생성"""
        config = {
            "evaluation": {
                "fairness": {
                    "metrics": ["demographic_parity"],
                    "threshold": 0.1,
                    "sensitive_attributes": ["gender"],
                },
                "transparency": {
                    "metrics": ["explainability_score"],
                    "threshold": 0.7,
                },
                "accountability": {
                    "metrics": ["audit_trail"],
                    "enabled": True,
                },
                "privacy": {
                    "metrics": ["differential_privacy"],
                    "threshold": 0.8,
                },
                "robustness": {
                    "metrics": ["adversarial_robustness"],
                    "threshold": 0.75,
                },
            },
            "auto_update": {
                "enabled": True,
                "check_interval": 3600,
                "conditions": {
                    "performance_degradation": {
                        "threshold": 0.05,
                        "action": "update",
                    },
                },
                "rollback": {
                    "enabled": True,
                    "max_rollback_attempts": 3,
                    "performance_threshold": 0.95,
                },
            },
            "monitoring": {
                "enabled": True,
                "dashboard_port": 8080,
                "log_level": "INFO",
                "metrics_retention_days": 30,
                "alert_channels": ["console"],
            },
            "model": {
                "save_path": str(tmp_path / "models"),
                "checkpoint_frequency": 1000,
                "max_checkpoints": 10,
            },
        }

        config_path = tmp_path / "config.yaml"
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f)

        return str(config_path)

    @pytest.fixture
    def sample_data(self):
        """샘플 데이터 생성"""
        X = np.random.rand(100, 10)
        y = np.random.randint(0, 2, 100)
        sensitive_features = pd.DataFrame({"gender": np.random.choice(["M", "F"], 100)})
        return X, y, sensitive_features

    def test_system_initialization(self, config_file):
        """시스템 초기화 테스트"""
        system = ResponsibleAIAutomationSystem(config_file)
        assert system is not None
        assert system.evaluator is not None
        assert system.updater is not None

    def test_model_initialization(self, config_file, sample_data):
        """모델 초기화 테스트"""
        system = ResponsibleAIAutomationSystem(config_file)
        X, y, sensitive_features = sample_data

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        system.initialize_model(model, X, y, sensitive_features)

        assert system.model is not None
        assert system.X is not None
        assert system.y is not None

    def test_evaluation(self, config_file, sample_data):
        """평가 테스트"""
        system = ResponsibleAIAutomationSystem(config_file)
        X, y, sensitive_features = sample_data

        model = RandomForestClassifier(n_estimators=10, random_state=42)
        model.fit(X, y)

        system.initialize_model(model, X, y, sensitive_features)

        y_pred = model.predict(X)
        metrics = system.evaluate(X, y, y_pred, sensitive_features)

        assert "overall_responsible_ai_score" in metrics
        assert isinstance(metrics["overall_responsible_ai_score"], float)

