"""
모델 자동 업데이트 모듈
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
import json

from ..rl_agent.agent import RLAIAgent
from ..evaluation.comprehensive import ComprehensiveEvaluator


class ModelUpdater:
    """모델을 자동으로 업데이트하는 클래스"""
    
    def __init__(
        self,
        model_path: str,
        backup_path: str = "./model_backups",
        config: Optional[Dict] = None,
    ):
        """
        Args:
            model_path: 현재 모델 경로
            backup_path: 백업 저장 경로
            config: 설정 딕셔너리
        """
        self.model_path = Path(model_path)
        self.backup_path = Path(backup_path)
        self.backup_path.mkdir(parents=True, exist_ok=True)
        self.config = config or {}
        
        # 업데이트 이력
        self.update_history = []
        self.history_file = Path("./update_history.json")
        self._load_history()
    
    def update(
        self,
        agent: RLAIAgent,
        evaluator: ComprehensiveEvaluator,
        X: Any,
        y: Any,
        sensitive_features: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        모델을 업데이트합니다.
        
        Args:
            agent: 강화 학습 에이전트
            evaluator: 평가자
            X: 입력 데이터
            y: 실제 레이블
            sensitive_features: 민감한 속성 데이터
        
        Returns:
            업데이트 결과 딕셔너리
        """
        update_time = datetime.now()
        
        # 1. 현재 모델 백업
        backup_info = self._backup_current_model(update_time)
        
        # 2. 에이전트 추가 학습
        training_steps = self.config.get("reinforcement_learning", {}).get(
            "training_steps", 10000
        )
        agent.train(total_timesteps=training_steps)
        
        # 3. 업데이트된 모델 평가
        evaluation_results = self._evaluate_updated_model(
            agent, evaluator, X, y, sensitive_features
        )
        
        # 4. 모델 저장
        new_model_path = self._save_updated_model(agent, update_time)
        
        # 5. 업데이트 기록
        update_record = {
            "timestamp": update_time.isoformat(),
            "backup_path": str(backup_info["backup_path"]),
            "new_model_path": str(new_model_path),
            "evaluation_results": evaluation_results,
            "status": "success",
        }
        self.update_history.append(update_record)
        self._save_history()
        
        return {
            "status": "success",
            "update_time": update_time.isoformat(),
            "backup_path": str(backup_info["backup_path"]),
            "new_model_path": str(new_model_path),
            "evaluation_results": evaluation_results,
        }
    
    def _backup_current_model(self, update_time: datetime) -> Dict[str, Any]:
        """현재 모델을 백업합니다."""
        if not self.model_path.exists():
            return {"backup_path": None, "status": "no_model_to_backup"}
        
        # 백업 파일명 생성
        timestamp = update_time.strftime("%Y%m%d_%H%M%S")
        backup_filename = f"model_backup_{timestamp}"
        backup_file_path = self.backup_path / backup_filename
        
        # 모델 파일 복사
        if self.model_path.is_file():
            shutil.copy2(self.model_path, backup_file_path)
        elif self.model_path.is_dir():
            shutil.copytree(self.model_path, backup_file_path, dirs_exist_ok=True)
        
        return {
            "backup_path": backup_file_path,
            "status": "backed_up",
        }
    
    def _evaluate_updated_model(
        self,
        agent: RLAIAgent,
        evaluator: ComprehensiveEvaluator,
        X: Any,
        y: Any,
        sensitive_features: Optional[Any],
    ) -> Dict[str, Any]:
        """업데이트된 모델을 평가합니다."""
        # 에이전트 평가
        agent_eval_results = agent.evaluate(n_episodes=5)
        
        # Responsible AI 평가 (환경에서 수행)
        # 실제로는 환경의 모델을 평가해야 함
        # 여기서는 시뮬레이션
        metrics = {
            "agent_evaluation": agent_eval_results,
            "overall_responsible_ai_score": 0.75,  # 시뮬레이션 값
        }
        
        return metrics
    
    def _save_updated_model(self, agent: RLAIAgent, update_time: datetime) -> Path:
        """업데이트된 모델을 저장합니다."""
        timestamp = update_time.strftime("%Y%m%d_%H%M%S")
        model_filename = f"model_{timestamp}"
        model_file_path = self.model_path.parent / model_filename
        
        # 모델 저장
        agent.save(str(model_file_path))
        
        # 현재 모델 경로 업데이트 (심볼릭 링크 또는 복사)
        if self.model_path.exists():
            if self.model_path.is_file():
                self.model_path.unlink()
            elif self.model_path.is_dir():
                shutil.rmtree(self.model_path)
        
        # 새 모델을 현재 모델로 설정
        if model_file_path.is_file():
            shutil.copy2(model_file_path, self.model_path)
        elif model_file_path.is_dir():
            shutil.copytree(model_file_path, self.model_path, dirs_exist_ok=True)
        
        return model_file_path
    
    def _load_history(self):
        """업데이트 이력을 로드합니다."""
        if self.history_file.exists():
            try:
                with open(self.history_file, "r") as f:
                    data = json.load(f)
                    self.update_history = data.get("update_history", [])
            except:
                self.update_history = []
        else:
            self.update_history = []
    
    def _save_history(self):
        """업데이트 이력을 저장합니다."""
        data = {"update_history": self.update_history[-100:]}  # 최근 100개만 저장
        
        with open(self.history_file, "w") as f:
            json.dump(data, f, indent=2)
    
    def get_update_history(self) -> list:
        """업데이트 이력을 반환합니다."""
        return self.update_history.copy()

