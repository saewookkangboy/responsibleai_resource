"""
Error Analysis 모듈

Microsoft Responsible AI Toolbox의 Error Analysis 기능을 참고하여 구현
- 모델 오류를 체계적으로 분석
- 오류율이 높은 데이터 코호트 식별
- 오류 트리 시각화 및 분석

Reference: https://github.com/microsoft/responsible-ai-toolbox
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple, Callable
from dataclasses import dataclass, field
from collections import defaultdict
import warnings


@dataclass
class ErrorCohort:
    """오류 코호트 정의"""
    name: str
    filter_conditions: Dict[str, Any]
    size: int
    error_rate: float
    error_count: int
    coverage: float  # 전체 데이터 대비 비율
    metrics: Dict[str, float] = field(default_factory=dict)


@dataclass
class ErrorTreeNode:
    """오류 트리 노드"""
    feature: Optional[str] = None
    condition: Optional[str] = None
    threshold: Optional[float] = None
    error_rate: float = 0.0
    sample_count: int = 0
    error_count: int = 0
    left: Optional['ErrorTreeNode'] = None
    right: Optional['ErrorTreeNode'] = None
    depth: int = 0
    is_leaf: bool = False


class ErrorAnalyzer:
    """
    Error Analysis 클래스
    
    모델의 오류를 체계적으로 분석하고 오류율이 높은 데이터 코호트를 식별합니다.
    Microsoft Responsible AI Toolbox의 Error Analysis 컴포넌트를 참고하여 구현되었습니다.
    
    주요 기능:
    - 오류 분포 분석
    - 오류 코호트 자동 식별
    - 오류 트리 생성 및 분석
    - 특성별 오류율 분석
    - 오류 히트맵 생성
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        max_depth: int = 4,
        min_samples_leaf: int = 20,
        num_leaves: int = 31,
    ):
        """
        Args:
            config: 설정 딕셔너리
            max_depth: 오류 트리 최대 깊이
            min_samples_leaf: 리프 노드 최소 샘플 수
            num_leaves: 최대 리프 노드 수
        """
        self.config = config or {}
        self.max_depth = max_depth
        self.min_samples_leaf = min_samples_leaf
        self.num_leaves = num_leaves
        
        # 분석 결과 저장
        self._error_tree: Optional[ErrorTreeNode] = None
        self._cohorts: List[ErrorCohort] = []
        self._feature_importances: Dict[str, float] = {}
        
    def analyze(
        self,
        X: pd.DataFrame,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        feature_names: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        오류 분석 수행
        
        Args:
            X: 특성 데이터프레임
            y_true: 실제 레이블
            y_pred: 예측 레이블
            feature_names: 특성 이름 목록
            categorical_features: 범주형 특성 목록
            
        Returns:
            오류 분석 결과 딕셔너리
        """
        # 입력 데이터 검증
        if len(X) != len(y_true) or len(y_true) != len(y_pred):
            raise ValueError("X, y_true, y_pred의 길이가 일치해야 합니다.")
        
        # 특성 이름 설정
        if feature_names is None:
            feature_names = list(X.columns) if isinstance(X, pd.DataFrame) else [f"feature_{i}" for i in range(X.shape[1])]
        
        # DataFrame으로 변환
        if not isinstance(X, pd.DataFrame):
            X = pd.DataFrame(X, columns=feature_names)
        
        # 오류 마스크 생성
        errors = (y_true != y_pred).astype(int)
        error_rate = float(np.mean(errors))
        
        # 분석 결과 수집
        results = {
            "overall_error_rate": error_rate,
            "total_samples": len(y_true),
            "total_errors": int(np.sum(errors)),
        }
        
        # 1. 오류 트리 생성
        self._error_tree = self._build_error_tree(
            X, errors, feature_names, categorical_features
        )
        results["error_tree"] = self._serialize_tree(self._error_tree)
        
        # 2. 오류 코호트 식별
        self._cohorts = self._identify_cohorts(
            X, errors, feature_names, categorical_features
        )
        results["cohorts"] = [self._cohort_to_dict(c) for c in self._cohorts]
        
        # 3. 특성별 오류율 분석
        feature_error_rates = self._analyze_feature_errors(
            X, errors, feature_names, categorical_features
        )
        results["feature_error_rates"] = feature_error_rates
        
        # 4. 특성 중요도 (오류 예측 기준)
        self._feature_importances = self._calculate_feature_importance(
            X, errors, feature_names
        )
        results["feature_importances"] = self._feature_importances
        
        # 5. 오류 히트맵 데이터
        heatmap_data = self._generate_heatmap_data(
            X, errors, feature_names, categorical_features
        )
        results["heatmap_data"] = heatmap_data
        
        # 6. 요약 통계
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _build_error_tree(
        self,
        X: pd.DataFrame,
        errors: np.ndarray,
        feature_names: List[str],
        categorical_features: Optional[List[str]] = None,
    ) -> ErrorTreeNode:
        """오류 트리 구축"""
        try:
            from sklearn.tree import DecisionTreeClassifier
            
            # 결정 트리를 사용하여 오류 예측
            tree = DecisionTreeClassifier(
                max_depth=self.max_depth,
                min_samples_leaf=self.min_samples_leaf,
                max_leaf_nodes=self.num_leaves,
                random_state=42
            )
            tree.fit(X, errors)
            
            # sklearn 트리를 ErrorTreeNode로 변환
            return self._sklearn_tree_to_error_tree(tree, X, errors, feature_names)
            
        except ImportError:
            warnings.warn("sklearn이 설치되지 않아 기본 오류 트리를 생성합니다.")
            return self._build_simple_error_tree(X, errors, feature_names)
    
    def _sklearn_tree_to_error_tree(
        self,
        sklearn_tree,
        X: pd.DataFrame,
        errors: np.ndarray,
        feature_names: List[str],
    ) -> ErrorTreeNode:
        """sklearn 결정 트리를 ErrorTreeNode로 변환"""
        tree_ = sklearn_tree.tree_
        
        def build_node(node_id: int, depth: int) -> ErrorTreeNode:
            is_leaf = tree_.feature[node_id] < 0
            
            # 해당 노드에 도달하는 샘플 찾기
            node_indicator = sklearn_tree.decision_path(X)
            samples_in_node = node_indicator[:, node_id].toarray().flatten().astype(bool)
            node_errors = errors[samples_in_node]
            
            node = ErrorTreeNode(
                feature=feature_names[tree_.feature[node_id]] if not is_leaf else None,
                threshold=float(tree_.threshold[node_id]) if not is_leaf else None,
                condition=f"<= {tree_.threshold[node_id]:.3f}" if not is_leaf else None,
                error_rate=float(np.mean(node_errors)) if len(node_errors) > 0 else 0.0,
                sample_count=int(np.sum(samples_in_node)),
                error_count=int(np.sum(node_errors)),
                depth=depth,
                is_leaf=is_leaf,
            )
            
            if not is_leaf:
                node.left = build_node(tree_.children_left[node_id], depth + 1)
                node.right = build_node(tree_.children_right[node_id], depth + 1)
            
            return node
        
        return build_node(0, 0)
    
    def _build_simple_error_tree(
        self,
        X: pd.DataFrame,
        errors: np.ndarray,
        feature_names: List[str],
    ) -> ErrorTreeNode:
        """간단한 오류 트리 구축 (sklearn 없이)"""
        root = ErrorTreeNode(
            error_rate=float(np.mean(errors)),
            sample_count=len(errors),
            error_count=int(np.sum(errors)),
            depth=0,
            is_leaf=True,
        )
        return root
    
    def _identify_cohorts(
        self,
        X: pd.DataFrame,
        errors: np.ndarray,
        feature_names: List[str],
        categorical_features: Optional[List[str]] = None,
    ) -> List[ErrorCohort]:
        """오류율이 높은 코호트 식별"""
        cohorts = []
        overall_error_rate = float(np.mean(errors))
        total_samples = len(errors)
        
        categorical_features = categorical_features or []
        
        for feature in feature_names:
            if feature in categorical_features:
                # 범주형 특성
                for value in X[feature].unique():
                    mask = X[feature] == value
                    if np.sum(mask) >= self.min_samples_leaf:
                        cohort_errors = errors[mask]
                        error_rate = float(np.mean(cohort_errors))
                        
                        if error_rate > overall_error_rate * 1.2:  # 20% 이상 높은 오류율
                            cohort = ErrorCohort(
                                name=f"{feature} = {value}",
                                filter_conditions={feature: value},
                                size=int(np.sum(mask)),
                                error_rate=error_rate,
                                error_count=int(np.sum(cohort_errors)),
                                coverage=float(np.sum(mask)) / total_samples,
                            )
                            cohorts.append(cohort)
            else:
                # 수치형 특성 - 사분위수 기반 분할
                quartiles = [0, 0.25, 0.5, 0.75, 1.0]
                values = X[feature].values
                
                for i in range(len(quartiles) - 1):
                    low = np.percentile(values, quartiles[i] * 100)
                    high = np.percentile(values, quartiles[i + 1] * 100)
                    
                    if i == len(quartiles) - 2:
                        mask = (values >= low) & (values <= high)
                    else:
                        mask = (values >= low) & (values < high)
                    
                    if np.sum(mask) >= self.min_samples_leaf:
                        cohort_errors = errors[mask]
                        error_rate = float(np.mean(cohort_errors))
                        
                        if error_rate > overall_error_rate * 1.2:
                            cohort = ErrorCohort(
                                name=f"{feature} in [{low:.2f}, {high:.2f}]",
                                filter_conditions={feature: {"min": low, "max": high}},
                                size=int(np.sum(mask)),
                                error_rate=error_rate,
                                error_count=int(np.sum(cohort_errors)),
                                coverage=float(np.sum(mask)) / total_samples,
                            )
                            cohorts.append(cohort)
        
        # 오류율 기준 정렬
        cohorts.sort(key=lambda x: x.error_rate, reverse=True)
        return cohorts[:10]  # 상위 10개 코호트 반환
    
    def _analyze_feature_errors(
        self,
        X: pd.DataFrame,
        errors: np.ndarray,
        feature_names: List[str],
        categorical_features: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """특성별 오류율 분석"""
        feature_errors = {}
        categorical_features = categorical_features or []
        
        for feature in feature_names:
            if feature in categorical_features:
                # 범주형: 각 값별 오류율
                error_by_value = {}
                for value in X[feature].unique():
                    mask = X[feature] == value
                    if np.sum(mask) > 0:
                        error_by_value[str(value)] = {
                            "error_rate": float(np.mean(errors[mask])),
                            "count": int(np.sum(mask)),
                            "error_count": int(np.sum(errors[mask])),
                        }
                feature_errors[feature] = {
                    "type": "categorical",
                    "values": error_by_value,
                }
            else:
                # 수치형: 구간별 오류율
                bins = np.percentile(X[feature], [0, 25, 50, 75, 100])
                bin_errors = []
                
                for i in range(len(bins) - 1):
                    if i == len(bins) - 2:
                        mask = (X[feature] >= bins[i]) & (X[feature] <= bins[i + 1])
                    else:
                        mask = (X[feature] >= bins[i]) & (X[feature] < bins[i + 1])
                    
                    if np.sum(mask) > 0:
                        bin_errors.append({
                            "range": [float(bins[i]), float(bins[i + 1])],
                            "error_rate": float(np.mean(errors[mask])),
                            "count": int(np.sum(mask)),
                            "error_count": int(np.sum(errors[mask])),
                        })
                
                feature_errors[feature] = {
                    "type": "numerical",
                    "bins": bin_errors,
                    "mean": float(X[feature].mean()),
                    "std": float(X[feature].std()),
                }
        
        return feature_errors
    
    def _calculate_feature_importance(
        self,
        X: pd.DataFrame,
        errors: np.ndarray,
        feature_names: List[str],
    ) -> Dict[str, float]:
        """오류 예측에 대한 특성 중요도 계산"""
        try:
            from sklearn.ensemble import RandomForestClassifier
            
            rf = RandomForestClassifier(
                n_estimators=50,
                max_depth=5,
                random_state=42,
                n_jobs=-1
            )
            rf.fit(X, errors)
            
            importances = dict(zip(feature_names, rf.feature_importances_.tolist()))
            return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
            
        except ImportError:
            # sklearn 없이 상관관계 기반 중요도 계산
            importances = {}
            for feature in feature_names:
                corr = np.corrcoef(X[feature].values, errors)[0, 1]
                importances[feature] = float(abs(corr)) if not np.isnan(corr) else 0.0
            return dict(sorted(importances.items(), key=lambda x: x[1], reverse=True))
    
    def _generate_heatmap_data(
        self,
        X: pd.DataFrame,
        errors: np.ndarray,
        feature_names: List[str],
        categorical_features: Optional[List[str]] = None,
        max_features: int = 5,
    ) -> Dict[str, Any]:
        """오류 히트맵 데이터 생성"""
        # 상위 중요 특성 선택
        top_features = list(self._feature_importances.keys())[:max_features]
        
        if len(top_features) < 2:
            return {"message": "히트맵 생성에 충분한 특성이 없습니다."}
        
        heatmap_data = {}
        
        # 2개 특성 조합에 대한 히트맵
        for i, feat1 in enumerate(top_features[:-1]):
            for feat2 in top_features[i + 1:]:
                key = f"{feat1}_vs_{feat2}"
                
                # 각 특성을 5개 구간으로 분할
                bins1 = pd.qcut(X[feat1], q=5, duplicates='drop').cat.codes
                bins2 = pd.qcut(X[feat2], q=5, duplicates='drop').cat.codes
                
                # 각 셀별 오류율 계산
                cells = []
                for b1 in range(bins1.max() + 1):
                    for b2 in range(bins2.max() + 1):
                        mask = (bins1 == b1) & (bins2 == b2)
                        if np.sum(mask) > 0:
                            cells.append({
                                "x": int(b1),
                                "y": int(b2),
                                "error_rate": float(np.mean(errors[mask])),
                                "count": int(np.sum(mask)),
                            })
                
                heatmap_data[key] = {
                    "feature_x": feat1,
                    "feature_y": feat2,
                    "cells": cells,
                }
        
        return heatmap_data
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """분석 요약 생성"""
        summary = {
            "overall_error_rate": results["overall_error_rate"],
            "total_samples": results["total_samples"],
            "total_errors": results["total_errors"],
            "num_cohorts_identified": len(results["cohorts"]),
            "top_error_features": list(results["feature_importances"].keys())[:5],
        }
        
        # 가장 문제가 되는 코호트
        if results["cohorts"]:
            worst_cohort = results["cohorts"][0]
            summary["worst_cohort"] = {
                "name": worst_cohort["name"],
                "error_rate": worst_cohort["error_rate"],
                "size": worst_cohort["size"],
            }
        
        # 개선 권장사항
        recommendations = []
        if results["overall_error_rate"] > 0.1:
            recommendations.append("전체 오류율이 10%를 초과합니다. 모델 재훈련을 고려하세요.")
        
        if results["cohorts"]:
            for cohort in results["cohorts"][:3]:
                if cohort["error_rate"] > results["overall_error_rate"] * 2:
                    recommendations.append(
                        f"'{cohort['name']}' 코호트의 오류율이 매우 높습니다 ({cohort['error_rate']:.1%}). "
                        f"해당 그룹에 대한 추가 데이터 수집 또는 특별 처리를 고려하세요."
                    )
        
        summary["recommendations"] = recommendations
        return summary
    
    def _serialize_tree(self, node: Optional[ErrorTreeNode]) -> Optional[Dict[str, Any]]:
        """ErrorTreeNode를 딕셔너리로 직렬화"""
        if node is None:
            return None
        
        return {
            "feature": node.feature,
            "condition": node.condition,
            "threshold": node.threshold,
            "error_rate": node.error_rate,
            "sample_count": node.sample_count,
            "error_count": node.error_count,
            "depth": node.depth,
            "is_leaf": node.is_leaf,
            "left": self._serialize_tree(node.left),
            "right": self._serialize_tree(node.right),
        }
    
    def _cohort_to_dict(self, cohort: ErrorCohort) -> Dict[str, Any]:
        """ErrorCohort를 딕셔너리로 변환"""
        return {
            "name": cohort.name,
            "filter_conditions": cohort.filter_conditions,
            "size": cohort.size,
            "error_rate": cohort.error_rate,
            "error_count": cohort.error_count,
            "coverage": cohort.coverage,
            "metrics": cohort.metrics,
        }
    
    def get_cohorts(self) -> List[ErrorCohort]:
        """식별된 오류 코호트 반환"""
        return self._cohorts
    
    def get_error_tree(self) -> Optional[ErrorTreeNode]:
        """오류 트리 반환"""
        return self._error_tree
    
    def get_feature_importances(self) -> Dict[str, float]:
        """특성 중요도 반환"""
        return self._feature_importances


def create_error_analyzer(config: Optional[Dict[str, Any]] = None) -> ErrorAnalyzer:
    """ErrorAnalyzer 인스턴스 생성 헬퍼 함수"""
    return ErrorAnalyzer(config=config)

