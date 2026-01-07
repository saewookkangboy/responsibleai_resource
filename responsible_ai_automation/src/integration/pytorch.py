"""
PyTorch 통합 모듈
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False


class PyTorchIntegration:
    """PyTorch 모델 통합 클래스"""

    def __init__(self, device: Optional[str] = None):
        """
        PyTorch 통합 초기화

        Args:
            device: 사용할 디바이스 ("cpu", "cuda", None=자동)
        """
        if not PYTORCH_AVAILABLE:
            raise ImportError(
                "PyTorch가 설치되지 않았습니다. "
                "pip install torch를 실행하세요."
            )

        if device is None:
            self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        else:
            self.device = torch.device(device)

    def evaluate_model(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        PyTorch 모델 평가

        Args:
            model: PyTorch 모델
            X: 입력 데이터
            y: 타겟 레이블
            sensitive_features: 민감한 속성 데이터
            config: 평가 설정

        Returns:
            평가 결과 딕셔너리
        """
        if not isinstance(model, nn.Module):
            raise ValueError("PyTorch 모델이 아닙니다.")

        model.eval()
        X_tensor = torch.FloatTensor(X).to(self.device)

        with torch.no_grad():
            outputs = model(X_tensor)
            
            # 이진 분류인 경우
            if outputs.shape[1] == 1:
                y_pred = (outputs > 0.5).cpu().numpy().flatten()
            else:
                y_pred = torch.argmax(outputs, dim=1).cpu().numpy()

        return {
            "model_type": "pytorch",
            "y_pred": y_pred,
            "device": str(self.device),
            "model_summary": self._get_model_summary(model),
        }

    def _get_model_summary(self, model: Any) -> Dict[str, Any]:
        """
        모델 요약 정보 추출

        Args:
            model: PyTorch 모델

        Returns:
            모델 요약 딕셔너리
        """
        total_params = sum(p.numel() for p in model.parameters())
        trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)

        return {
            "total_params": total_params,
            "trainable_params": trainable_params,
            "num_layers": len(list(model.modules())),
        }

    @staticmethod
    def is_pytorch_model(model: Any) -> bool:
        """
        모델이 PyTorch 모델인지 확인

        Args:
            model: 확인할 모델

        Returns:
            PyTorch 모델 여부
        """
        if not PYTORCH_AVAILABLE:
            return False
        return isinstance(model, nn.Module)

