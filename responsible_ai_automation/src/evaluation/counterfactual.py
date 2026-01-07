"""
Counterfactual Analysis 모듈

Microsoft Responsible AI Toolbox의 DiCE(Diverse Counterfactual Explanations) 기능을 참고하여 구현
- 개별 예측에 대한 반사실적 설명 생성
- "무엇이 달랐다면 결과가 바뀌었을까?" 질문에 답변
- 최소 변경으로 다른 예측 결과를 얻을 수 있는 시나리오 제시

Reference: https://github.com/microsoft/responsible-ai-toolbox
DiCE Paper: https://arxiv.org/abs/1905.07697
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
import warnings


@dataclass
class Counterfactual:
    """반사실적 예시 데이터 클래스"""
    original: Dict[str, Any]
    counterfactual: Dict[str, Any]
    original_prediction: Any
    counterfactual_prediction: Any
    changes: Dict[str, Tuple[Any, Any]]  # feature: (original, new)
    distance: float  # 원본과의 거리
    validity: bool  # 유효한 반사실적 예시인지
    sparsity: int  # 변경된 특성 수


@dataclass
class CounterfactualExplanation:
    """반사실적 설명 결과"""
    instance_id: int
    original_instance: Dict[str, Any]
    original_prediction: Any
    desired_outcome: Any
    counterfactuals: List[Counterfactual]
    summary: Dict[str, Any]


class CounterfactualAnalyzer:
    """
    Counterfactual Analysis 클래스
    
    DiCE(Diverse Counterfactual Explanations) 방법론을 기반으로
    개별 예측에 대한 반사실적 설명을 생성합니다.
    
    주요 기능:
    - 다양한 반사실적 예시 생성
    - 최소 변경 반사실적 찾기
    - 실행 가능한 권장 사항 제공
    - 특성 중요도 분석
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        num_counterfactuals: int = 5,
        diversity_weight: float = 0.5,
        proximity_weight: float = 0.5,
        features_to_vary: Optional[List[str]] = None,
        permitted_range: Optional[Dict[str, Tuple[float, float]]] = None,
    ):
        """
        Args:
            config: 설정 딕셔너리
            num_counterfactuals: 생성할 반사실적 예시 수
            diversity_weight: 다양성 가중치
            proximity_weight: 근접성 가중치
            features_to_vary: 변경 가능한 특성 목록
            permitted_range: 특성별 허용 범위
        """
        self.config = config or {}
        self.num_counterfactuals = num_counterfactuals
        self.diversity_weight = diversity_weight
        self.proximity_weight = proximity_weight
        self.features_to_vary = features_to_vary
        self.permitted_range = permitted_range or {}
        
        # 데이터 통계
        self._feature_stats: Dict[str, Dict[str, float]] = {}
        self._categorical_features: List[str] = []
        self._continuous_features: List[str] = []
        
    def fit(
        self,
        X: pd.DataFrame,
        categorical_features: Optional[List[str]] = None,
    ) -> 'CounterfactualAnalyzer':
        """
        데이터 통계 학습
        
        Args:
            X: 학습 데이터
            categorical_features: 범주형 특성 목록
        """
        self._categorical_features = categorical_features or []
        self._continuous_features = [
            col for col in X.columns if col not in self._categorical_features
        ]
        
        # 특성별 통계 계산
        for col in X.columns:
            if col in self._categorical_features:
                self._feature_stats[col] = {
                    "type": "categorical",
                    "values": X[col].unique().tolist(),
                    "mode": X[col].mode().iloc[0] if len(X[col].mode()) > 0 else None,
                }
            else:
                self._feature_stats[col] = {
                    "type": "continuous",
                    "mean": float(X[col].mean()),
                    "std": float(X[col].std()),
                    "min": float(X[col].min()),
                    "max": float(X[col].max()),
                    "median": float(X[col].median()),
                }
        
        return self
    
    def generate_counterfactuals(
        self,
        instance: Union[pd.Series, Dict[str, Any]],
        predict_fn: Callable,
        desired_outcome: Any,
        instance_id: int = 0,
    ) -> CounterfactualExplanation:
        """
        반사실적 예시 생성
        
        Args:
            instance: 설명할 인스턴스
            predict_fn: 예측 함수 (입력: DataFrame, 출력: 예측값 배열)
            desired_outcome: 원하는 결과
            instance_id: 인스턴스 ID
            
        Returns:
            CounterfactualExplanation 객체
        """
        # 인스턴스를 딕셔너리로 변환
        if isinstance(instance, pd.Series):
            original_dict = instance.to_dict()
        else:
            original_dict = dict(instance)
        
        # 원본 예측
        original_df = pd.DataFrame([original_dict])
        original_pred = predict_fn(original_df)[0]
        
        # 변경 가능한 특성 결정
        features_to_vary = self.features_to_vary or list(original_dict.keys())
        
        # 반사실적 예시 생성
        counterfactuals = []
        
        # 방법 1: 그리디 탐색
        greedy_cfs = self._greedy_search(
            original_dict, predict_fn, desired_outcome, features_to_vary
        )
        counterfactuals.extend(greedy_cfs)
        
        # 방법 2: 랜덤 탐색
        random_cfs = self._random_search(
            original_dict, predict_fn, desired_outcome, features_to_vary
        )
        counterfactuals.extend(random_cfs)
        
        # 방법 3: 유전 알고리즘 기반 탐색
        genetic_cfs = self._genetic_search(
            original_dict, predict_fn, desired_outcome, features_to_vary
        )
        counterfactuals.extend(genetic_cfs)
        
        # 중복 제거 및 다양성 기준 선택
        counterfactuals = self._select_diverse_counterfactuals(
            counterfactuals, original_dict
        )
        
        # 요약 생성
        summary = self._generate_summary(
            original_dict, original_pred, desired_outcome, counterfactuals
        )
        
        return CounterfactualExplanation(
            instance_id=instance_id,
            original_instance=original_dict,
            original_prediction=original_pred,
            desired_outcome=desired_outcome,
            counterfactuals=counterfactuals,
            summary=summary,
        )
    
    def _greedy_search(
        self,
        original: Dict[str, Any],
        predict_fn: Callable,
        desired_outcome: Any,
        features_to_vary: List[str],
    ) -> List[Counterfactual]:
        """그리디 탐색으로 반사실적 예시 찾기"""
        counterfactuals = []
        
        # 각 특성을 개별적으로 변경해보기
        for feature in features_to_vary:
            if feature not in self._feature_stats:
                continue
            
            stats = self._feature_stats[feature]
            candidates = self._generate_feature_candidates(feature, stats, original[feature])
            
            for new_value in candidates:
                cf_dict = original.copy()
                cf_dict[feature] = new_value
                
                cf_df = pd.DataFrame([cf_dict])
                cf_pred = predict_fn(cf_df)[0]
                
                if self._is_desired_outcome(cf_pred, desired_outcome):
                    cf = self._create_counterfactual(
                        original, cf_dict, 
                        predict_fn(pd.DataFrame([original]))[0], 
                        cf_pred
                    )
                    counterfactuals.append(cf)
        
        return counterfactuals
    
    def _random_search(
        self,
        original: Dict[str, Any],
        predict_fn: Callable,
        desired_outcome: Any,
        features_to_vary: List[str],
        num_samples: int = 100,
    ) -> List[Counterfactual]:
        """랜덤 탐색으로 반사실적 예시 찾기"""
        counterfactuals = []
        original_pred = predict_fn(pd.DataFrame([original]))[0]
        
        for _ in range(num_samples):
            cf_dict = original.copy()
            
            # 랜덤하게 1-3개 특성 변경
            num_changes = np.random.randint(1, min(4, len(features_to_vary) + 1))
            features_to_change = np.random.choice(
                features_to_vary, size=num_changes, replace=False
            )
            
            for feature in features_to_change:
                if feature not in self._feature_stats:
                    continue
                    
                stats = self._feature_stats[feature]
                cf_dict[feature] = self._sample_feature_value(feature, stats)
            
            cf_df = pd.DataFrame([cf_dict])
            cf_pred = predict_fn(cf_df)[0]
            
            if self._is_desired_outcome(cf_pred, desired_outcome):
                cf = self._create_counterfactual(original, cf_dict, original_pred, cf_pred)
                counterfactuals.append(cf)
        
        return counterfactuals
    
    def _genetic_search(
        self,
        original: Dict[str, Any],
        predict_fn: Callable,
        desired_outcome: Any,
        features_to_vary: List[str],
        population_size: int = 50,
        generations: int = 20,
    ) -> List[Counterfactual]:
        """유전 알고리즘 기반 탐색"""
        counterfactuals = []
        original_pred = predict_fn(pd.DataFrame([original]))[0]
        
        # 초기 인구 생성
        population = []
        for _ in range(population_size):
            individual = original.copy()
            num_changes = np.random.randint(1, min(4, len(features_to_vary) + 1))
            features_to_change = np.random.choice(
                features_to_vary, size=num_changes, replace=False
            )
            
            for feature in features_to_change:
                if feature in self._feature_stats:
                    individual[feature] = self._sample_feature_value(
                        feature, self._feature_stats[feature]
                    )
            population.append(individual)
        
        # 세대 진화
        for _ in range(generations):
            # 적합도 평가
            fitness_scores = []
            for individual in population:
                cf_df = pd.DataFrame([individual])
                cf_pred = predict_fn(cf_df)[0]
                
                # 적합도: 원하는 결과 달성 + 근접성
                validity = 1.0 if self._is_desired_outcome(cf_pred, desired_outcome) else 0.0
                distance = self._calculate_distance(original, individual)
                fitness = validity * 0.7 + (1 - min(distance, 1)) * 0.3
                fitness_scores.append(fitness)
                
                # 유효한 반사실적 저장
                if validity == 1.0:
                    cf = self._create_counterfactual(original, individual, original_pred, cf_pred)
                    counterfactuals.append(cf)
            
            # 선택 및 교차
            if len(population) > 2:
                sorted_indices = np.argsort(fitness_scores)[::-1]
                elite = [population[i] for i in sorted_indices[:population_size // 4]]
                
                new_population = elite.copy()
                while len(new_population) < population_size:
                    parent1, parent2 = np.random.choice(len(elite), 2, replace=False)
                    child = self._crossover(elite[parent1], elite[parent2], features_to_vary)
                    child = self._mutate(child, features_to_vary, mutation_rate=0.1)
                    new_population.append(child)
                
                population = new_population
        
        return counterfactuals
    
    def _generate_feature_candidates(
        self,
        feature: str,
        stats: Dict[str, Any],
        current_value: Any,
    ) -> List[Any]:
        """특성에 대한 후보 값 생성"""
        candidates = []
        
        if stats["type"] == "categorical":
            candidates = [v for v in stats["values"] if v != current_value]
        else:
            # 연속형: 다양한 값 생성
            min_val = self.permitted_range.get(feature, (stats["min"], stats["max"]))[0]
            max_val = self.permitted_range.get(feature, (stats["min"], stats["max"]))[1]
            
            # 분위수 기반 값
            candidates.extend([
                stats["mean"],
                stats["median"],
                stats["mean"] + stats["std"],
                stats["mean"] - stats["std"],
            ])
            
            # 구간 값
            for p in [0.1, 0.25, 0.5, 0.75, 0.9]:
                val = min_val + (max_val - min_val) * p
                candidates.append(val)
            
            # 현재 값 기준 변화
            if isinstance(current_value, (int, float)):
                candidates.extend([
                    current_value * 1.1,
                    current_value * 0.9,
                    current_value + stats["std"],
                    current_value - stats["std"],
                ])
            
            # 범위 내로 제한
            candidates = [max(min_val, min(max_val, c)) for c in candidates]
            candidates = list(set(candidates))  # 중복 제거
        
        return candidates
    
    def _sample_feature_value(self, feature: str, stats: Dict[str, Any]) -> Any:
        """특성 값 샘플링"""
        if stats["type"] == "categorical":
            return np.random.choice(stats["values"])
        else:
            min_val = self.permitted_range.get(feature, (stats["min"], stats["max"]))[0]
            max_val = self.permitted_range.get(feature, (stats["min"], stats["max"]))[1]
            
            # 정규 분포에서 샘플링
            value = np.random.normal(stats["mean"], stats["std"])
            return max(min_val, min(max_val, value))
    
    def _is_desired_outcome(self, prediction: Any, desired_outcome: Any) -> bool:
        """예측이 원하는 결과인지 확인"""
        if isinstance(desired_outcome, (list, tuple)):
            return prediction in desired_outcome
        return prediction == desired_outcome
    
    def _create_counterfactual(
        self,
        original: Dict[str, Any],
        counterfactual: Dict[str, Any],
        original_pred: Any,
        cf_pred: Any,
    ) -> Counterfactual:
        """Counterfactual 객체 생성"""
        changes = {}
        for key in original:
            if original[key] != counterfactual[key]:
                changes[key] = (original[key], counterfactual[key])
        
        distance = self._calculate_distance(original, counterfactual)
        
        return Counterfactual(
            original=original,
            counterfactual=counterfactual,
            original_prediction=original_pred,
            counterfactual_prediction=cf_pred,
            changes=changes,
            distance=distance,
            validity=True,
            sparsity=len(changes),
        )
    
    def _calculate_distance(
        self,
        original: Dict[str, Any],
        counterfactual: Dict[str, Any],
    ) -> float:
        """원본과 반사실적 예시 간의 거리 계산"""
        total_distance = 0.0
        num_features = 0
        
        for feature in original:
            if feature not in counterfactual:
                continue
            
            orig_val = original[feature]
            cf_val = counterfactual[feature]
            
            if feature in self._categorical_features:
                # 범주형: 다르면 1, 같으면 0
                total_distance += 0 if orig_val == cf_val else 1
            else:
                # 연속형: 정규화된 거리
                stats = self._feature_stats.get(feature, {})
                std = stats.get("std", 1.0)
                if std > 0:
                    total_distance += abs(float(orig_val) - float(cf_val)) / std
            
            num_features += 1
        
        return total_distance / num_features if num_features > 0 else 0.0
    
    def _crossover(
        self,
        parent1: Dict[str, Any],
        parent2: Dict[str, Any],
        features: List[str],
    ) -> Dict[str, Any]:
        """두 부모로부터 자식 생성"""
        child = parent1.copy()
        for feature in features:
            if np.random.random() < 0.5:
                child[feature] = parent2[feature]
        return child
    
    def _mutate(
        self,
        individual: Dict[str, Any],
        features: List[str],
        mutation_rate: float = 0.1,
    ) -> Dict[str, Any]:
        """개체 변이"""
        mutated = individual.copy()
        for feature in features:
            if np.random.random() < mutation_rate and feature in self._feature_stats:
                mutated[feature] = self._sample_feature_value(
                    feature, self._feature_stats[feature]
                )
        return mutated
    
    def _select_diverse_counterfactuals(
        self,
        counterfactuals: List[Counterfactual],
        original: Dict[str, Any],
    ) -> List[Counterfactual]:
        """다양한 반사실적 예시 선택"""
        if len(counterfactuals) <= self.num_counterfactuals:
            return sorted(counterfactuals, key=lambda x: x.distance)
        
        # 거리 기준 정렬
        sorted_cfs = sorted(counterfactuals, key=lambda x: x.distance)
        
        selected = [sorted_cfs[0]]  # 가장 가까운 것 선택
        
        # 다양성을 고려하여 추가 선택
        for cf in sorted_cfs[1:]:
            if len(selected) >= self.num_counterfactuals:
                break
            
            # 이미 선택된 것들과의 다양성 확인
            is_diverse = True
            for selected_cf in selected:
                # 변경된 특성이 너무 비슷하면 제외
                common_changes = set(cf.changes.keys()) & set(selected_cf.changes.keys())
                if len(common_changes) == len(cf.changes) == len(selected_cf.changes):
                    is_diverse = False
                    break
            
            if is_diverse:
                selected.append(cf)
        
        return selected
    
    def _generate_summary(
        self,
        original: Dict[str, Any],
        original_pred: Any,
        desired_outcome: Any,
        counterfactuals: List[Counterfactual],
    ) -> Dict[str, Any]:
        """반사실적 분석 요약 생성"""
        summary = {
            "num_counterfactuals_found": len(counterfactuals),
            "original_prediction": original_pred,
            "desired_outcome": desired_outcome,
        }
        
        if not counterfactuals:
            summary["message"] = "원하는 결과를 달성하는 반사실적 예시를 찾지 못했습니다."
            return summary
        
        # 가장 적은 변경이 필요한 반사실적
        min_changes_cf = min(counterfactuals, key=lambda x: x.sparsity)
        summary["minimum_changes_required"] = min_changes_cf.sparsity
        summary["easiest_change"] = {
            "changes": min_changes_cf.changes,
            "distance": min_changes_cf.distance,
        }
        
        # 자주 변경되는 특성
        feature_change_counts = {}
        for cf in counterfactuals:
            for feature in cf.changes:
                feature_change_counts[feature] = feature_change_counts.get(feature, 0) + 1
        
        summary["most_important_features"] = sorted(
            feature_change_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        
        # 실행 가능한 권장 사항
        recommendations = []
        for feature, count in summary["most_important_features"]:
            change_values = [cf.changes[feature][1] for cf in counterfactuals if feature in cf.changes]
            if change_values:
                if feature in self._categorical_features:
                    most_common = max(set(change_values), key=change_values.count)
                    recommendations.append(
                        f"'{feature}'를 '{most_common}'(으)로 변경하면 결과가 달라질 수 있습니다."
                    )
                else:
                    avg_change = np.mean([float(v) for v in change_values])
                    orig_val = original.get(feature, 0)
                    direction = "증가" if avg_change > float(orig_val) else "감소"
                    recommendations.append(
                        f"'{feature}'를 {direction}시키면 결과가 달라질 수 있습니다. "
                        f"(현재: {orig_val:.2f} → 권장: {avg_change:.2f})"
                    )
        
        summary["recommendations"] = recommendations
        
        return summary
    
    def explain_batch(
        self,
        instances: pd.DataFrame,
        predict_fn: Callable,
        desired_outcome: Any,
    ) -> List[CounterfactualExplanation]:
        """여러 인스턴스에 대한 반사실적 설명 생성"""
        explanations = []
        for idx, row in instances.iterrows():
            explanation = self.generate_counterfactuals(
                instance=row,
                predict_fn=predict_fn,
                desired_outcome=desired_outcome,
                instance_id=idx,
            )
            explanations.append(explanation)
        return explanations


def create_counterfactual_analyzer(
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> CounterfactualAnalyzer:
    """CounterfactualAnalyzer 인스턴스 생성 헬퍼 함수"""
    return CounterfactualAnalyzer(config=config, **kwargs)

