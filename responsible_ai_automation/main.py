"""
Responsible AI Automation 메인 모듈
"""

import argparse
import yaml
import logging
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
from pathlib import Path

from src.evaluation.comprehensive import ComprehensiveEvaluator
from src.auto_update.updater import ModelUpdater
from src.auto_update.rollback import RollbackManager
from src.monitoring.dashboard import MonitoringDashboard
from src.monitoring.alerts import AlertManager


class ResponsibleAIAutomationSystem:
    """Responsible AI Automation 시스템 메인 클래스"""

    def __init__(self, config_path: str):
        """
        Args:
            config_path: 설정 파일 경로
        """
        # 설정 로드
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

        # 로깅 설정
        log_level = self.config.get("monitoring", {}).get("log_level", "INFO")
        logging.basicConfig(
            level=getattr(logging, log_level),
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        self.logger = logging.getLogger(__name__)

        # 컴포넌트 지연 초기화 (성능 최적화)
        self._evaluator = None
        self._updater = None
        self._rollback_manager = None
        self._dashboard = None
        self._alert_manager = None

        # 모델 및 데이터 저장
        self.model: Optional[Any] = None
        self.X: Optional[np.ndarray] = None
        self.y: Optional[np.ndarray] = None
        self.sensitive_features: Optional[pd.DataFrame] = None
        self.previous_metrics: Optional[Dict[str, Any]] = None

        self.logger.info("Responsible AI Automation 시스템 초기화 완료")
    
    @property
    def evaluator(self):
        """평가자 지연 로딩"""
        if self._evaluator is None:
            self._evaluator = ComprehensiveEvaluator(self.config)
        return self._evaluator
    
    @property
    def updater(self):
        """업데이터 지연 로딩"""
        if self._updater is None:
            self._updater = ModelUpdater(self.config, self.evaluator)
        return self._updater
    
    @property
    def rollback_manager(self):
        """롤백 매니저 지연 로딩"""
        if self._rollback_manager is None:
            self._rollback_manager = RollbackManager(self.config)
        return self._rollback_manager
    
    @property
    def dashboard(self):
        """대시보드 지연 로딩"""
        if self._dashboard is None:
            self._dashboard = MonitoringDashboard(self.config)
        return self._dashboard
    
    @property
    def alert_manager(self):
        """알림 매니저 지연 로딩"""
        if self._alert_manager is None:
            self._alert_manager = AlertManager(self.config)
        return self._alert_manager

    def initialize_model(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
    ):
        """
        모델 초기화

        Args:
            model: 학습된 모델
            X: 입력 데이터
            y: 타겟 레이블
            sensitive_features: 민감한 속성 데이터프레임
        """
        self.model = model
        self.X = X
        self.y = y
        self.sensitive_features = sensitive_features

        # 초기 평가 수행
        y_pred = model.predict(X)
        initial_metrics = self.evaluate(X, y, y_pred, sensitive_features)

        # 체크포인트 저장
        self.rollback_manager.save_checkpoint(model, initial_metrics)

        self.logger.info("모델 초기화 완료")

    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        y_pred: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
    ) -> Dict[str, Any]:
        """
        Responsible AI 평가 수행

        Args:
            X: 입력 데이터
            y: 실제 레이블
            y_pred: 예측 레이블
            sensitive_features: 민감한 속성 데이터프레임

        Returns:
            평가 결과 딕셔너리
        """
        metrics = self.evaluator.evaluate(
            self.model, X, y, y_pred, sensitive_features
        )

        # 모니터링에 기록
        self.dashboard.log_metrics(metrics)

        # 임계값 위반 확인 및 알림
        violations = self.alert_manager.check_thresholds(metrics)
        if violations:
            self.alert_manager.send_alert(
                f"임계값 위반 감지: {', '.join(violations)}",
                level="WARNING",
                details={"violations": violations, "metrics": metrics},
            )

        return metrics

    def check_update_conditions(self) -> bool:
        """
        업데이트 조건 확인

        Returns:
            업데이트 필요 여부
        """
        if self.model is None or self.X is None or self.y is None:
            return False

        y_pred = self.model.predict(self.X)
        current_metrics = self.evaluate(
            self.X, self.y, y_pred, self.sensitive_features
        )

        conditions = self.updater.conditions.check_all_conditions(
            current_metrics, self.previous_metrics
        )

        return self.updater.conditions.should_update(conditions)

    def perform_update(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        sensitive_features: Optional[pd.DataFrame] = None,
    ):
        """
        모델 업데이트 수행

        Args:
            X: 입력 데이터 (None이면 저장된 데이터 사용)
            y: 타겟 레이블 (None이면 저장된 데이터 사용)
            sensitive_features: 민감한 속성 데이터프레임
        """
        if self.model is None:
            self.logger.error("모델이 초기화되지 않았습니다.")
            return

        X = X if X is not None else self.X
        y = y if y is not None else self.y
        sensitive_features = (
            sensitive_features
            if sensitive_features is not None
            else self.sensitive_features
        )

        if X is None or y is None:
            self.logger.error("데이터가 제공되지 않았습니다.")
            return

        y_pred = self.model.predict(X)
        current_metrics = self.evaluate(X, y, y_pred, sensitive_features)

        # 업데이트 전 체크포인트 저장
        self.rollback_manager.save_checkpoint(self.model, current_metrics)

        # 업데이트 수행
        update_result = self.updater.update(
            self.model, X, y, y_pred, sensitive_features, self.previous_metrics
        )

        if update_result.get("updated", False):
            updated_metrics = update_result.get("updated_metrics", {})
            previous_metrics = update_result.get("previous_metrics", {})

            # 롤백 필요 여부 확인
            if self.rollback_manager.should_rollback(updated_metrics, previous_metrics):
                self.logger.warning("성능 저하 감지, 롤백 수행")
                rollback_result = self.rollback_manager.rollback()
                if rollback_result:
                    self.model = rollback_result["model"]
                    self.alert_manager.send_alert(
                        "롤백 완료", level="WARNING", details=rollback_result
                    )
            else:
                self.previous_metrics = current_metrics
                self.alert_manager.send_alert(
                    "모델 업데이트 완료", level="INFO", details=update_result
                )

    def run_continuous_monitoring(
        self,
        X: Optional[np.ndarray] = None,
        y: Optional[np.ndarray] = None,
        sensitive_features: Optional[pd.DataFrame] = None,
    ):
        """
        지속적인 모니터링 시작

        Args:
            X: 입력 데이터
            y: 타겟 레이블
            sensitive_features: 민감한 속성 데이터프레임
        """
        self.dashboard.start_dashboard()

        import schedule
        import time

        check_interval = self.config.get("auto_update", {}).get("check_interval", 3600)

        def check_and_update():
            if self.check_update_conditions():
                self.perform_update(X, y, sensitive_features)

        schedule.every(check_interval).seconds.do(check_and_update)

        self.logger.info("지속적인 모니터링 시작")
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # 1분마다 스케줄 확인
        except KeyboardInterrupt:
            self.logger.info("모니터링 중지")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Responsible AI Automation System")
    parser.add_argument(
        "--config", type=str, default="config.yaml", help="설정 파일 경로"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["evaluate", "train", "update", "monitor"],
        default="evaluate",
        help="실행 모드",
    )

    args = parser.parse_args()

    # 시스템 초기화
    system = ResponsibleAIAutomationSystem(args.config)

    if args.mode == "monitor":
        system.run_continuous_monitoring()
    elif args.mode == "evaluate":
        # 예제 실행을 위한 기본 동작
        print("평가 모드: 모델을 초기화한 후 evaluate() 메서드를 호출하세요.")
    elif args.mode == "update":
        system.perform_update()
    elif args.mode == "train":
        print("학습 모드: 강화 학습 에이전트 학습을 시작합니다.")
        # 실제 구현에서는 RL 에이전트 학습 수행


if __name__ == "__main__":
    main()

