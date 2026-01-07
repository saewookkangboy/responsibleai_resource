"""
롤백 관리 모듈
"""

import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import json


class RollbackManager:
    """모델 롤백을 관리하는 클래스"""
    
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
        self.config = config or {}
        self.rollback_config = self.config.get("auto_update", {}).get("rollback", {})
        
        self.max_rollback_attempts = self.rollback_config.get("max_rollback_attempts", 3)
        self.performance_threshold = self.rollback_config.get("performance_threshold", 0.95)
        self.rollback_count = 0
    
    def should_rollback(
        self,
        current_performance: float,
        previous_performance: float,
    ) -> bool:
        """
        롤백이 필요한지 결정합니다.
        
        Args:
            current_performance: 현재 성능
            previous_performance: 이전 성능
        
        Returns:
            롤백 필요 여부
        """
        if previous_performance == 0:
            return False
        
        # 성능 저하가 임계값 이상이면 롤백
        performance_ratio = current_performance / previous_performance
        
        if performance_ratio < self.performance_threshold:
            if self.rollback_count < self.max_rollback_attempts:
                return True
        
        return False
    
    def rollback(self, backup_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        모델을 롤백합니다.
        
        Args:
            backup_path: 롤백할 백업 경로 (None이면 최신 백업 사용)
        
        Returns:
            롤백 결과 딕셔너리
        """
        if backup_path is None:
            backup_path = self._get_latest_backup()
        
        if backup_path is None or not backup_path.exists():
            return {
                "status": "failed",
                "message": "롤백할 백업을 찾을 수 없습니다.",
            }
        
        try:
            # 현재 모델 백업 (롤백 전 안전장치)
            current_backup = self.model_path.parent / f"pre_rollback_{self.rollback_count}"
            if self.model_path.exists():
                if self.model_path.is_file():
                    shutil.copy2(self.model_path, current_backup)
                elif self.model_path.is_dir():
                    shutil.copytree(self.model_path, current_backup, dirs_exist_ok=True)
            
            # 백업에서 복원
            if backup_path.is_file():
                shutil.copy2(backup_path, self.model_path)
            elif backup_path.is_dir():
                if self.model_path.exists():
                    if self.model_path.is_dir():
                        shutil.rmtree(self.model_path)
                    else:
                        self.model_path.unlink()
                shutil.copytree(backup_path, self.model_path, dirs_exist_ok=True)
            
            self.rollback_count += 1
            
            return {
                "status": "success",
                "backup_path": str(backup_path),
                "rollback_count": self.rollback_count,
            }
        except Exception as e:
            return {
                "status": "failed",
                "message": f"롤백 실패: {str(e)}",
            }
    
    def _get_latest_backup(self) -> Optional[Path]:
        """가장 최근 백업을 찾습니다."""
        if not self.backup_path.exists():
            return None
        
        # 백업 파일/디렉토리 찾기
        backups = []
        for item in self.backup_path.iterdir():
            if item.name.startswith("model_backup_"):
                backups.append((item.stat().st_mtime, item))
        
        if not backups:
            return None
        
        # 최신 백업 반환
        backups.sort(reverse=True)
        return backups[0][1]
    
    def reset_rollback_count(self):
        """롤백 카운트를 리셋합니다."""
        self.rollback_count = 0

