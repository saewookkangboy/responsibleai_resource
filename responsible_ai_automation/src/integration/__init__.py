"""
ML 프레임워크 통합 모듈
"""

from typing import Optional

# TensorFlow 통합
try:
    from .tensorflow import TensorFlowIntegration
    __all__ = ["TensorFlowIntegration"]
except ImportError:
    TensorFlowIntegration = None

# PyTorch 통합
try:
    from .pytorch import PyTorchIntegration
    if TensorFlowIntegration:
        __all__ = ["TensorFlowIntegration", "PyTorchIntegration"]
    else:
        __all__ = ["PyTorchIntegration"]
except ImportError:
    PyTorchIntegration = None
    if not TensorFlowIntegration:
        __all__ = []


def get_integration(model: Any) -> Optional[Any]:
    """
    모델 타입에 맞는 통합 클래스 반환

    Args:
        model: 확인할 모델

    Returns:
        통합 클래스 인스턴스 또는 None
    """
    if TensorFlowIntegration and TensorFlowIntegration.is_tensorflow_model(model):
        return TensorFlowIntegration()
    
    if PyTorchIntegration and PyTorchIntegration.is_pytorch_model(model):
        return PyTorchIntegration()
    
    return None

