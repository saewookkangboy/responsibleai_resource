"""
Responsible AI 자동화 시스템 메인 실행 스크립트
"""

import argparse
import yaml
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Optional, Dict, Any
import schedule
import time
from datetime import datetime

from src.evaluation.comprehensive import ComprehensiveEvaluator
from src.rl_agent.environment import ResponsibleAIEnv
from src.rl_agent.agent import RLAIAgent
from src.auto_update.conditions import UpdateConditionChecker
from src.auto_update.updater import ModelUpdater
from src.auto_update.rollback import RollbackManager
from src.monitoring.dashboard import MonitoringDashboard
from src.monitoring.alerts import AlertManager


class ResponsibleAIAutomationSystem:
    """Responsible AI 자동화 시스템 메인 클래스"""
    
    def __init__(self, config_path: str):
        """
        Args:
            config_path: 설정 파일 경로
        """
        # 설정 로드
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        
        # 컴포넌트 초기화
        self.evaluator = ComprehensiveEvaluator(self.config)
        self.condition_checker = UpdateConditionChecker(self.config)
        self.dashboard = MonitoringDashboard(
            log_dir="./monitoring_logs", config=self.config
        )
        self.alert_manager = AlertManager(self.config)
        
        # 모델 및 에이전트 (실제 사용 시 초기화 필요)
        self.model = None
        self.agent = None
        self.env = None
        self.updater = None
        self.rollback_manager = None
        
        # 상태
        self.current_metrics = None
        self.previous_metrics = None
    
    def initialize_model(self, model: Any, X: np.ndarray, y: np.ndarray, sensitive_features: Optional[pd.DataFrame] = None):
        """모델을 초기화합니다."""
        self.model = model
        
        # 환경 생성
        self.env = ResponsibleAIEnv(
            model=model,
            X=X,
            y=y,
            sensitive_features=sensitive_features,
            evaluator=self.evaluator,
            config=self.config,
        )
        
        # 에이전트 생성
        model_path = self.config.get("model", {}).get("save_path", "./models")
        self.agent = RLAIAgent(
            env=self.env,
            algorithm=self.config.get("reinforcement_learning", {}).get("algorithm", "PPO"),
            config=self.config,
        )
        
        # 업데이터 및 롤백 매니저
        self.updater = ModelUpdater(
            model_path=f"{model_path}/current_model",
            backup_path=f"{model_path}/backups",
            config=self.config,
        )
        
        self.rollback_manager = RollbackManager(
            model_path=f"{model_path}/current_model",
            backup_path=f"{model_path}/backups",
            config=self.config,
        )
    
    def evaluate(self, X: np.ndarray, y: np.ndarray, y_pred: np.ndarray, sensitive_features: Optional[pd.DataFrame] = None) -> Dict[str, Any]:
        """모델을 평가합니다."""
        metrics = self.evaluator.evaluate(
            self.model,
            X,
            y,
            y_pred,
            sensitive_features=sensitive_features,
        )
        
        # 이전 지표 저장
        self.previous_metrics = self.current_metrics
        self.current_metrics = metrics
        
        # 모니터링 대시보드에 로깅
        self.dashboard.log_metrics(metrics)
        
        # 알림 검사
        self.alert_manager.check_and_alert(metrics)
        
        return metrics
    
    def check_update_conditions(self) -> bool:
        """업데이트 조건을 검사합니다."""
        if self.current_metrics is None:
            return False
        
        conditions = self.condition_checker.check_all_conditions(
            self.current_metrics,
            self.previous_metrics,
        )
        
        return self.condition_checker.should_update(conditions)
    
    def perform_update(self, X: np.ndarray, y: np.ndarray, sensitive_features: Optional[pd.DataFrame] = None):
        """모델을 업데이트합니다."""
        if self.agent is None or self.updater is None:
            print("모델이 초기화되지 않았습니다.")
            return None
        
        print("모델 업데이트를 시작합니다...")
        
        # 업데이트 수행
        update_result = self.updater.update(
            self.agent,
            self.evaluator,
            X,
            y,
            sensitive_features,
        )
        
        # 업데이트 기록
        self.condition_checker.record_update()
        
        # 업데이트 후 평가
        if self.model is not None:
            y_pred = self.model.predict(X)
            new_metrics = self.evaluate(X, y, y_pred, sensitive_features)
            
            # 롤백 필요 여부 확인
            if self.previous_metrics is not None:
                current_score = new_metrics.get("overall_responsible_ai_score", 0.0)
                previous_score = self.previous_metrics.get("overall_responsible_ai_score", 0.0)
                
                if self.rollback_manager.should_rollback(current_score, previous_score):
                    print("성능 저하 감지. 롤백을 수행합니다...")
                    rollback_result = self.rollback_manager.rollback()
                    print(f"롤백 결과: {rollback_result}")
        
        print("모델 업데이트가 완료되었습니다.")
        return update_result
    
    def run_continuous_monitoring(self, X: np.ndarray, y: np.ndarray, sensitive_features: Optional[pd.DataFrame] = None):
        """지속적인 모니터링을 실행합니다."""
        auto_update_config = self.config.get("auto_update", {})
        check_interval = auto_update_config.get("check_interval", 3600)
        
        def monitoring_task():
            print(f"\n[{datetime.now()}] 모니터링 작업 실행...")
            
            # 평가 수행
            if self.model is not None:
                y_pred = self.model.predict(X)
                metrics = self.evaluate(X, y, y_pred, sensitive_features)
                
                # 업데이트 조건 검사
                if self.check_update_conditions():
                    print("업데이트 조건이 충족되었습니다. 업데이트를 수행합니다...")
                    self.perform_update(X, y, sensitive_features)
                else:
                    print("업데이트 조건이 충족되지 않았습니다.")
        
        # 스케줄 설정
        schedule.every(check_interval).seconds.do(monitoring_task)
        
        print(f"지속적인 모니터링을 시작합니다. (체크 간격: {check_interval}초)")
        print("종료하려면 Ctrl+C를 누르세요.")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n모니터링을 종료합니다.")


def main():
    """메인 함수"""
    parser = argparse.ArgumentParser(description="Responsible AI 자동화 시스템")
    parser.add_argument(
        "--config",
        type=str,
        default="config.yaml",
        help="설정 파일 경로",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["train", "evaluate", "monitor", "update"],
        default="monitor",
        help="실행 모드",
    )
    
    args = parser.parse_args()
    
    # 시스템 초기화
    system = ResponsibleAIAutomationSystem(args.config)
    
    # 예시 데이터 (실제 사용 시 교체 필요)
    # 여기서는 시뮬레이션 데이터 사용
    X = np.random.rand(100, 10)
    y = np.random.randint(0, 2, 100)
    sensitive_features = pd.DataFrame({
        "gender": np.random.choice(["M", "F"], 100),
        "race": np.random.choice(["A", "B", "C"], 100),
    })
    
    # 간단한 모델 (실제 사용 시 교체 필요)
    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=10, random_state=42)
    model.fit(X, y)
    
    # 모델 초기화
    system.initialize_model(model, X, y, sensitive_features)
    
    # 모드에 따라 실행
    if args.mode == "train":
        print("강화 학습을 시작합니다...")
        training_steps = system.config.get("reinforcement_learning", {}).get("training_steps", 100000)
        system.agent.train(total_timesteps=training_steps)
        system.agent.save(f"./models/rl_agent_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
    
    elif args.mode == "evaluate":
        print("모델을 평가합니다...")
        y_pred = model.predict(X)
        metrics = system.evaluate(X, y, y_pred, sensitive_features)
        print(f"\n평가 결과:")
        print(f"  전체 Responsible AI 점수: {metrics.get('overall_responsible_ai_score', 0.0):.3f}")
    
    elif args.mode == "monitor":
        print("지속적인 모니터링을 시작합니다...")
        system.run_continuous_monitoring(X, y, sensitive_features)
    
    elif args.mode == "update":
        print("수동 업데이트를 수행합니다...")
        system.perform_update(X, y, sensitive_features)


if __name__ == "__main__":
    main()

