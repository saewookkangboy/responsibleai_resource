"""
책임성(Accountability) 평가 모듈
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path


class AccountabilityEvaluator:
    """AI 모델의 책임성을 평가하는 클래스"""
    
    def __init__(self, audit_trail_path: str = "./audit_trails"):
        """
        Args:
            audit_trail_path: 감사 추적 로그 저장 경로
        """
        self.audit_trail_path = Path(audit_trail_path)
        self.audit_trail_path.mkdir(parents=True, exist_ok=True)
        self.decision_logs = []
        self.error_logs = []
    
    def log_decision(
        self,
        decision_id: str,
        model_version: str,
        input_data: dict,
        prediction: any,
        confidence: float,
        metadata: Optional[dict] = None,
    ):
        """의사결정을 로깅합니다."""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "decision_id": decision_id,
            "model_version": model_version,
            "input_data": input_data,
            "prediction": str(prediction),
            "confidence": confidence,
            "metadata": metadata or {},
        }
        self.decision_logs.append(log_entry)
        
        # 파일에 저장
        log_file = self.audit_trail_path / f"decisions_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(log_entry) + "\n")
    
    def log_error(
        self,
        error_type: str,
        error_message: str,
        model_version: str,
        context: Optional[dict] = None,
    ):
        """에러를 로깅합니다."""
        error_entry = {
            "timestamp": datetime.now().isoformat(),
            "error_type": error_type,
            "error_message": error_message,
            "model_version": model_version,
            "context": context or {},
        }
        self.error_logs.append(error_entry)
        
        # 파일에 저장
        log_file = self.audit_trail_path / f"errors_{datetime.now().strftime('%Y%m%d')}.jsonl"
        with open(log_file, "a") as f:
            f.write(json.dumps(error_entry) + "\n")
    
    def evaluate(self) -> Dict[str, float]:
        """
        책임성 지표를 평가합니다.
        
        Returns:
            책임성 지표 딕셔너리
        """
        results = {}
        
        # 1. 감사 추적 완전성
        audit_trail_score = self._evaluate_audit_trail()
        results["audit_trail_score"] = audit_trail_score
        
        # 2. 의사결정 로깅 완전성
        decision_logging_score = self._evaluate_decision_logging()
        results["decision_logging_score"] = decision_logging_score
        
        # 3. 에러 추적 완전성
        error_tracking_score = self._evaluate_error_tracking()
        results["error_tracking_score"] = error_tracking_score
        
        # 전체 책임성 점수
        overall_score = (
            audit_trail_score * 0.4
            + decision_logging_score * 0.4
            + error_tracking_score * 0.2
        )
        results["overall_accountability_score"] = overall_score
        results["is_accountable"] = overall_score >= 0.7
        
        return results
    
    def _evaluate_audit_trail(self) -> float:
        """감사 추적 완전성을 평가합니다."""
        # 감사 추적 파일이 존재하고 최근에 업데이트되었는지 확인
        if not self.audit_trail_path.exists():
            return 0.0
        
        # 최근 7일간의 로그 파일 확인
        recent_files = list(self.audit_trail_path.glob("decisions_*.jsonl"))
        if not recent_files:
            return 0.0
        
        # 최근 파일의 최신성 확인
        latest_file = max(recent_files, key=lambda p: p.stat().st_mtime)
        days_since_update = (datetime.now().timestamp() - latest_file.stat().st_mtime) / 86400
        
        if days_since_update > 7:
            return 0.5
        elif days_since_update > 1:
            return 0.8
        else:
            return 1.0
    
    def _evaluate_decision_logging(self) -> float:
        """의사결정 로깅 완전성을 평가합니다."""
        if not self.decision_logs:
            return 0.0
        
        # 최근 로그의 완전성 확인
        recent_logs = self.decision_logs[-100:]  # 최근 100개
        complete_logs = sum(
            1
            for log in recent_logs
            if all(
                key in log
                for key in ["timestamp", "decision_id", "model_version", "prediction"]
            )
        )
        
        return complete_logs / len(recent_logs) if recent_logs else 0.0
    
    def _evaluate_error_tracking(self) -> float:
        """에러 추적 완전성을 평가합니다."""
        if not self.error_logs:
            return 0.5  # 에러가 없으면 중간 점수
        
        # 최근 에러 로그의 완전성 확인
        recent_errors = self.error_logs[-50:]  # 최근 50개
        complete_errors = sum(
            1
            for error in recent_errors
            if all(
                key in error
                for key in ["timestamp", "error_type", "error_message", "model_version"]
            )
        )
        
        return complete_errors / len(recent_errors) if recent_errors else 0.0

