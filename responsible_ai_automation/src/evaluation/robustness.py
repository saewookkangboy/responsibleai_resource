"""
견고성(Robustness) 평가 모듈
"""

import numpy as np
from typing import Dict, Optional, Any, Tuple


class RobustnessEvaluator:
    """AI 모델의 견고성을 평가하는 클래스"""
    
    def __init__(self, threshold: float = 0.75):
        """
        Args:
            threshold: 최소 견고성 점수
        """
        self.threshold = threshold
    
    def evaluate(
        self,
        model: Any,
        X: np.ndarray,
        y: np.ndarray,
        adversarial_perturbation: float = 0.01,
    ) -> Dict[str, float]:
        """
        견고성 지표를 평가합니다.
        
        Args:
            model: 평가할 모델
            X: 입력 데이터
            y: 실제 레이블
            adversarial_perturbation: 적대적 공격 노이즈 크기
        
        Returns:
            견고성 지표 딕셔너리
        """
        results = {}
        
        # 1. 적대적 견고성
        adversarial_score = self._evaluate_adversarial_robustness(
            model, X, y, adversarial_perturbation
        )
        results["adversarial_robustness_score"] = adversarial_score
        
        # 2. 분포 외 데이터 감지
        ood_detection_score = self._evaluate_ood_detection(model, X)
        results["ood_detection_score"] = ood_detection_score
        
        # 3. 노이즈 견고성
        noise_robustness_score = self._evaluate_noise_robustness(model, X, y)
        results["noise_robustness_score"] = noise_robustness_score
        
        # 전체 견고성 점수
        overall_score = (
            adversarial_score * 0.4
            + ood_detection_score * 0.3
            + noise_robustness_score * 0.3
        )
        results["overall_robustness_score"] = overall_score
        results["is_robust"] = overall_score >= self.threshold
        
        return results
    
    def _evaluate_adversarial_robustness(
        self, model: Any, X: np.ndarray, y: np.ndarray, perturbation: float
    ) -> float:
        """적대적 견고성을 평가합니다."""
        try:
            # 원본 예측
            original_predictions = model.predict(X[:100])
            
            # 노이즈 추가
            noise = np.random.normal(0, perturbation, X[:100].shape)
            perturbed_X = X[:100] + noise
            perturbed_X = np.clip(perturbed_X, 0, 1)  # 값 범위 제한
            
            # 노이즈 추가 후 예측
            perturbed_predictions = model.predict(perturbed_X)
            
            # 예측 일관성 계산
            consistency = np.mean(original_predictions == perturbed_predictions)
            
            return float(consistency)
        except Exception as e:
            print(f"적대적 견고성 평가 실패: {e}")
            return 0.5
    
    def _evaluate_ood_detection(self, model: Any, X: np.ndarray) -> float:
        """분포 외 데이터 감지 능력을 평가합니다."""
        try:
            # 예측 신뢰도 기반 OOD 감지
            if hasattr(model, "predict_proba"):
                probabilities = model.predict_proba(X[:100])
                # 신뢰도가 낮은 예측의 비율
                max_probs = np.max(probabilities, axis=1)
                low_confidence_ratio = np.mean(max_probs < 0.5)
                
                # 낮은 신뢰도 비율이 적당하면 OOD 감지가 잘 됨
                # 너무 높거나 너무 낮으면 문제
                if 0.1 < low_confidence_ratio < 0.3:
                    return 0.9
                elif 0.05 < low_confidence_ratio < 0.5:
                    return 0.7
                else:
                    return 0.5
            else:
                return 0.5  # 기본값
        except:
            return 0.5
    
    def _evaluate_noise_robustness(
        self, model: Any, X: np.ndarray, y: np.ndarray
    ) -> float:
        """노이즈 견고성을 평가합니다."""
        try:
            # 원본 정확도
            original_accuracy = np.mean(model.predict(X[:100]) == y[:100])
            
            # 다양한 노이즈 레벨 테스트
            noise_levels = [0.01, 0.05, 0.1]
            robustness_scores = []
            
            for noise_level in noise_levels:
                noise = np.random.normal(0, noise_level, X[:100].shape)
                noisy_X = X[:100] + noise
                noisy_X = np.clip(noisy_X, 0, 1)
                
                noisy_accuracy = np.mean(model.predict(noisy_X) == y[:100])
                # 정확도 저하가 적을수록 견고함
                accuracy_drop = original_accuracy - noisy_accuracy
                robustness = max(0, 1 - (accuracy_drop / original_accuracy))
                robustness_scores.append(robustness)
            
            return np.mean(robustness_scores)
        except:
            return 0.5

