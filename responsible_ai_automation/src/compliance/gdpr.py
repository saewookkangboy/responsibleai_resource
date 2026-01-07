"""
GDPR 준수 기능 모듈
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
import json
from pathlib import Path


class GDPRCompliance:
    """GDPR 준수 클래스"""

    def __init__(self, config: Dict[str, Any]):
        """
        Args:
            config: GDPR 설정
        """
        self.config = config.get("compliance", {}).get("gdpr", {})
        self.enabled = self.config.get("enabled", True)
        self.data_retention_days = self.config.get("data_retention_days", 365)
        self.audit_log_path = Path(self.config.get("audit_log_path", "./logs/gdpr_audit.log"))
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger = logging.getLogger(__name__)

        # 개인정보 처리 기록
        self.processing_records: List[Dict[str, Any]] = []

    def log_data_processing(
        self,
        user_id: str,
        data_type: str,
        purpose: str,
        legal_basis: str
    ) -> bool:
        """
        데이터 처리 기록

        Args:
            user_id: 사용자 ID
            data_type: 데이터 유형
            purpose: 처리 목적
            legal_basis: 법적 근거

        Returns:
            기록 성공 여부
        """
        if not self.enabled:
            return False

        record = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "data_type": data_type,
            "purpose": purpose,
            "legal_basis": legal_basis,
        }

        self.processing_records.append(record)
        self._save_audit_log(record)

        self.logger.info(f"데이터 처리 기록: {user_id} - {data_type}")
        return True

    def handle_right_to_be_forgotten(self, user_id: str) -> bool:
        """
        삭제 요청 처리 (Right to be Forgotten)

        Args:
            user_id: 사용자 ID

        Returns:
            처리 성공 여부
        """
        if not self.enabled:
            return False

        try:
            # 사용자 데이터 삭제
            deleted_count = self._delete_user_data(user_id)

            # 삭제 기록
            deletion_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "data_deletion",
                "user_id": user_id,
                "deleted_records": deleted_count,
            }
            self._save_audit_log(deletion_record)

            self.logger.info(f"데이터 삭제 완료: {user_id} ({deleted_count}개 레코드)")
            return True
        except Exception as e:
            self.logger.error(f"데이터 삭제 실패: {e}")
            return False

    def handle_data_portability_request(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        데이터 이식성 요청 처리

        Args:
            user_id: 사용자 ID

        Returns:
            사용자 데이터 또는 None
        """
        if not self.enabled:
            return None

        try:
            user_data = self._export_user_data(user_id)

            # 내보내기 기록
            export_record = {
                "timestamp": datetime.now().isoformat(),
                "action": "data_export",
                "user_id": user_id,
            }
            self._save_audit_log(export_record)

            self.logger.info(f"데이터 내보내기 완료: {user_id}")
            return user_data
        except Exception as e:
            self.logger.error(f"데이터 내보내기 실패: {e}")
            return None

    def cleanup_old_data(self) -> int:
        """
        오래된 데이터 정리

        Returns:
            삭제된 레코드 수
        """
        if not self.enabled:
            return 0

        cutoff_date = datetime.now() - timedelta(days=self.data_retention_days)
        deleted_count = 0

        # 오래된 처리 기록 제거
        self.processing_records = [
            record
            for record in self.processing_records
            if datetime.fromisoformat(record["timestamp"]) >= cutoff_date
        ]

        # 실제 데이터 삭제는 구현체에서 수행
        # 여기서는 기록만 정리

        self.logger.info(f"오래된 데이터 정리 완료: {deleted_count}개 레코드")
        return deleted_count

    def _delete_user_data(self, user_id: str) -> int:
        """
        사용자 데이터 삭제 (구현체에서 구현 필요)

        Args:
            user_id: 사용자 ID

        Returns:
            삭제된 레코드 수
        """
        # 실제 구현에서는 데이터베이스나 저장소에서 데이터 삭제
        deleted_count = sum(
            1 for record in self.processing_records
            if record.get("user_id") == user_id
        )

        self.processing_records = [
            record for record in self.processing_records
            if record.get("user_id") != user_id
        ]

        return deleted_count

    def _export_user_data(self, user_id: str) -> Dict[str, Any]:
        """
        사용자 데이터 내보내기 (구현체에서 구현 필요)

        Args:
            user_id: 사용자 ID

        Returns:
            사용자 데이터 딕셔너리
        """
        user_records = [
            record for record in self.processing_records
            if record.get("user_id") == user_id
        ]

        return {
            "user_id": user_id,
            "records": user_records,
            "export_date": datetime.now().isoformat(),
        }

    def _save_audit_log(self, record: Dict[str, Any]) -> None:
        """
        감사 로그 저장

        Args:
            record: 기록할 레코드
        """
        try:
            with open(self.audit_log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except Exception as e:
            self.logger.error(f"감사 로그 저장 실패: {e}")

    def get_processing_history(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        처리 이력 조회

        Args:
            user_id: 사용자 ID (None이면 전체)

        Returns:
            처리 이력 리스트
        """
        if user_id is None:
            return self.processing_records

        return [
            record for record in self.processing_records
            if record.get("user_id") == user_id
        ]
