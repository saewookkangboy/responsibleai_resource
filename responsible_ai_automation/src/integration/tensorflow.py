"""
TensorFlow/Keras 통합 모듈
"""

from typing import Dict, Any, Optional
import numpy as np
import pandas as pd

try:
    import tensorflow as tf
    from tensorflow import keras
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False


class TensorFlowIntegration:
    """TensorFlow/Keras 모델 통합 클래스"""

    def __init__(self):
        """TensorFlow 통합 초기화"""
        if not TENSORFLOW_AVAILABLE:
            raise ImportError(
                "TensorFlow가 설치되지 않았습니다. "
                "pip install tensorflow를 실행하세요."
            )

    def evaluate_model(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        sensitive_features: Optional[pd.DataFrame] = None,
        config: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        TensorFlow/Keras 모델 평가

        Args:
            model: TensorFlow/Keras 모델
            X: 입력 데이터
            y: 타겟 레이블
            sensitive_features: 민감한 속성 데이터
            config: 평가 설정

        Returns:
            평가 결과 딕셔너리
        """
        if not isinstance(model, (tf.keras.Model, keras.Model)):
            raise ValueError("TensorFlow/Keras 모델이 아닙니다.")

        # 예측 수행
        y_pred = model.predict(X, verbose=0)
        
        # 이진 분류인 경우 임계값 적용
        if y_pred.ndim > 1 and y_pred.shape[1] == 1:
            y_pred = (y_pred > 0.5).astype(int).flatten()
        elif y_pred.ndim > 1 and y_pred.shape[1] > 1:
            y_pred = np.argmax(y_pred, axis=1)
        else:
            y_pred = (y_pred > 0.5).astype(int)

        return {
            "model_type": "tensorflow",
            "y_pred": y_pred,
            "model_summary": self._get_model_summary(model),
        }

    def _get_model_summary(self, model: Any) -> Dict[str, Any]:
        """
        모델 요약 정보 추출

        Args:
            model: TensorFlow/Keras 모델

        Returns:
            모델 요약 딕셔너리
        """
        return {
            "num_layers": len(model.layers),
            "total_params": model.count_params(),
            "trainable_params": sum(
                tf.keras.backend.count_params(w) for w in model.trainable_weights
            ),
        }

    @staticmethod
    def is_tensorflow_model(model: Any) -> bool:
        """
        모델이 TensorFlow/Keras 모델인지 확인

        Args:
            model: 확인할 모델

        Returns:
            TensorFlow/Keras 모델 여부
        """
        if not TENSORFLOW_AVAILABLE:
            return False
        return isinstance(model, (tf.keras.Model, keras.Model))

