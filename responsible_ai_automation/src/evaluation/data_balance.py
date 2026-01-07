"""
Data Balance 분석 모듈

Microsoft Responsible AI Toolbox의 Data Balance 기능을 참고하여 구현
- 데이터 불균형 분석
- 특성별 분포 시각화
- 레이블 분포 분석
- 민감한 속성별 데이터 균형 평가

Reference: https://github.com/microsoft/responsible-ai-toolbox
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from collections import Counter
import warnings


@dataclass
class FeatureBalance:
    """특성 균형 분석 결과"""
    feature_name: str
    feature_type: str  # categorical, numerical
    distribution: Dict[str, Any]
    imbalance_score: float  # 0 = 완벽한 균형, 1 = 극심한 불균형
    majority_class: Optional[str] = None
    minority_class: Optional[str] = None
    imbalance_ratio: float = 1.0
    recommendations: List[str] = field(default_factory=list)


@dataclass
class LabelBalance:
    """레이블 균형 분석 결과"""
    label_name: str
    class_distribution: Dict[Any, int]
    class_percentages: Dict[Any, float]
    imbalance_ratio: float
    is_balanced: bool
    majority_class: Any
    minority_class: Any
    recommendations: List[str]


@dataclass
class SensitiveAttributeBalance:
    """민감한 속성 균형 분석 결과"""
    attribute_name: str
    group_distribution: Dict[Any, int]
    positive_outcome_rates: Dict[Any, float]
    statistical_parity_difference: float
    disparate_impact_ratio: float
    is_fair: bool
    recommendations: List[str]


class DataBalanceAnalyzer:
    """
    Data Balance 분석 클래스
    
    데이터셋의 균형 상태를 종합적으로 분석하고
    불균형으로 인한 잠재적 편향을 식별합니다.
    
    주요 기능:
    - 특성별 분포 분석
    - 레이블 불균형 분석
    - 민감한 속성별 균형 분석
    - 교차 분석 (Intersectional Analysis)
    - 데이터 품질 평가
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        sensitive_features: Optional[List[str]] = None,
        label_column: Optional[str] = None,
        imbalance_threshold: float = 0.2,
    ):
        """
        Args:
            config: 설정 딕셔너리
            sensitive_features: 민감한 속성 목록
            label_column: 레이블 컬럼명
            imbalance_threshold: 불균형 임계값
        """
        self.config = config or {}
        self.sensitive_features = sensitive_features or []
        self.label_column = label_column
        self.imbalance_threshold = imbalance_threshold
        
        # 분석 결과
        self._feature_balances: List[FeatureBalance] = []
        self._label_balance: Optional[LabelBalance] = None
        self._sensitive_balances: List[SensitiveAttributeBalance] = []
        
    def analyze(
        self,
        data: pd.DataFrame,
        label_column: Optional[str] = None,
        sensitive_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        데이터 균형 종합 분석
        
        Args:
            data: 분석할 데이터프레임
            label_column: 레이블 컬럼명
            sensitive_features: 민감한 속성 목록
            categorical_features: 범주형 특성 목록
            
        Returns:
            분석 결과 딕셔너리
        """
        label_column = label_column or self.label_column
        sensitive_features = sensitive_features or self.sensitive_features
        
        # 범주형 특성 자동 감지
        if categorical_features is None:
            categorical_features = self._detect_categorical_features(data)
        
        results = {
            "dataset_info": self._get_dataset_info(data),
        }
        
        # 1. 특성별 균형 분석
        self._feature_balances = self._analyze_feature_balance(
            data, categorical_features
        )
        results["feature_balance"] = [
            self._feature_balance_to_dict(fb) for fb in self._feature_balances
        ]
        
        # 2. 레이블 균형 분석
        if label_column and label_column in data.columns:
            self._label_balance = self._analyze_label_balance(data, label_column)
            results["label_balance"] = self._label_balance_to_dict(self._label_balance)
        
        # 3. 민감한 속성 균형 분석
        if sensitive_features and label_column:
            self._sensitive_balances = self._analyze_sensitive_balance(
                data, sensitive_features, label_column
            )
            results["sensitive_attribute_balance"] = [
                self._sensitive_balance_to_dict(sb) for sb in self._sensitive_balances
            ]
        
        # 4. 교차 분석
        if len(sensitive_features) >= 2 and label_column:
            results["intersectional_analysis"] = self._intersectional_analysis(
                data, sensitive_features[:2], label_column
            )
        
        # 5. 데이터 품질 평가
        results["data_quality"] = self._assess_data_quality(data)
        
        # 6. 종합 요약
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _get_dataset_info(self, data: pd.DataFrame) -> Dict[str, Any]:
        """데이터셋 기본 정보"""
        return {
            "num_samples": len(data),
            "num_features": len(data.columns),
            "feature_names": list(data.columns),
            "memory_usage_mb": float(data.memory_usage(deep=True).sum() / 1024 / 1024),
            "missing_values": {
                col: int(data[col].isna().sum()) 
                for col in data.columns 
                if data[col].isna().sum() > 0
            },
        }
    
    def _detect_categorical_features(
        self, 
        data: pd.DataFrame, 
        unique_threshold: int = 10
    ) -> List[str]:
        """범주형 특성 자동 감지"""
        categorical = []
        for col in data.columns:
            if data[col].dtype == 'object' or data[col].dtype.name == 'category':
                categorical.append(col)
            elif data[col].nunique() <= unique_threshold:
                categorical.append(col)
        return categorical
    
    def _analyze_feature_balance(
        self,
        data: pd.DataFrame,
        categorical_features: List[str],
    ) -> List[FeatureBalance]:
        """특성별 균형 분석"""
        balances = []
        
        for col in data.columns:
            if col in categorical_features:
                balance = self._analyze_categorical_feature(data, col)
            else:
                balance = self._analyze_numerical_feature(data, col)
            balances.append(balance)
        
        # 불균형 점수 기준 정렬
        balances.sort(key=lambda x: x.imbalance_score, reverse=True)
        return balances
    
    def _analyze_categorical_feature(
        self, 
        data: pd.DataFrame, 
        col: str
    ) -> FeatureBalance:
        """범주형 특성 분석"""
        value_counts = data[col].value_counts()
        total = len(data)
        
        distribution = {
            str(k): {"count": int(v), "percentage": float(v / total * 100)}
            for k, v in value_counts.items()
        }
        
        # 불균형 점수 계산 (엔트로피 기반)
        probabilities = value_counts.values / total
        max_entropy = np.log(len(value_counts)) if len(value_counts) > 1 else 1
        actual_entropy = -np.sum(probabilities * np.log(probabilities + 1e-10))
        imbalance_score = 1 - (actual_entropy / max_entropy) if max_entropy > 0 else 0
        
        majority = str(value_counts.index[0])
        minority = str(value_counts.index[-1]) if len(value_counts) > 1 else majority
        imbalance_ratio = float(value_counts.iloc[0] / value_counts.iloc[-1]) if len(value_counts) > 1 else 1.0
        
        recommendations = []
        if imbalance_score > 0.5:
            recommendations.append(f"'{col}'의 불균형이 심각합니다. 오버샘플링 또는 언더샘플링을 고려하세요.")
        if imbalance_ratio > 10:
            recommendations.append(f"다수 클래스와 소수 클래스 비율이 {imbalance_ratio:.1f}:1 입니다.")
        
        return FeatureBalance(
            feature_name=col,
            feature_type="categorical",
            distribution=distribution,
            imbalance_score=float(imbalance_score),
            majority_class=majority,
            minority_class=minority,
            imbalance_ratio=imbalance_ratio,
            recommendations=recommendations,
        )
    
    def _analyze_numerical_feature(
        self, 
        data: pd.DataFrame, 
        col: str
    ) -> FeatureBalance:
        """수치형 특성 분석"""
        values = data[col].dropna()
        
        distribution = {
            "mean": float(values.mean()),
            "std": float(values.std()),
            "min": float(values.min()),
            "max": float(values.max()),
            "median": float(values.median()),
            "q1": float(values.quantile(0.25)),
            "q3": float(values.quantile(0.75)),
            "skewness": float(values.skew()) if len(values) > 2 else 0,
            "kurtosis": float(values.kurtosis()) if len(values) > 3 else 0,
        }
        
        # 불균형 점수 (왜도 기반)
        skewness = abs(distribution["skewness"])
        imbalance_score = min(1.0, skewness / 2)  # 왜도 2 이상이면 불균형
        
        recommendations = []
        if skewness > 1:
            recommendations.append(f"'{col}'의 분포가 치우쳐 있습니다 (왜도: {skewness:.2f}). 로그 변환을 고려하세요.")
        
        iqr = distribution["q3"] - distribution["q1"]
        outlier_low = distribution["q1"] - 1.5 * iqr
        outlier_high = distribution["q3"] + 1.5 * iqr
        outlier_count = int(((values < outlier_low) | (values > outlier_high)).sum())
        
        if outlier_count > len(values) * 0.05:
            recommendations.append(f"'{col}'에 이상치가 {outlier_count}개 ({outlier_count/len(values)*100:.1f}%) 있습니다.")
            distribution["outlier_count"] = outlier_count
        
        return FeatureBalance(
            feature_name=col,
            feature_type="numerical",
            distribution=distribution,
            imbalance_score=float(imbalance_score),
            recommendations=recommendations,
        )
    
    def _analyze_label_balance(
        self, 
        data: pd.DataFrame, 
        label_column: str
    ) -> LabelBalance:
        """레이블 균형 분석"""
        label_counts = data[label_column].value_counts()
        total = len(data)
        
        class_distribution = {k: int(v) for k, v in label_counts.items()}
        class_percentages = {k: float(v / total * 100) for k, v in label_counts.items()}
        
        majority_class = label_counts.index[0]
        minority_class = label_counts.index[-1]
        imbalance_ratio = float(label_counts.iloc[0] / label_counts.iloc[-1]) if len(label_counts) > 1 else 1.0
        
        # 균형 여부 판단 (비율이 3:1 이하면 균형)
        is_balanced = imbalance_ratio <= 3.0
        
        recommendations = []
        if not is_balanced:
            recommendations.append(f"레이블 불균형 비율: {imbalance_ratio:.1f}:1")
            if imbalance_ratio > 10:
                recommendations.append("SMOTE, ADASYN 등의 오버샘플링 기법을 고려하세요.")
            else:
                recommendations.append("클래스 가중치 조정 또는 층화 샘플링을 고려하세요.")
        
        return LabelBalance(
            label_name=label_column,
            class_distribution=class_distribution,
            class_percentages=class_percentages,
            imbalance_ratio=imbalance_ratio,
            is_balanced=is_balanced,
            majority_class=majority_class,
            minority_class=minority_class,
            recommendations=recommendations,
        )
    
    def _analyze_sensitive_balance(
        self,
        data: pd.DataFrame,
        sensitive_features: List[str],
        label_column: str,
    ) -> List[SensitiveAttributeBalance]:
        """민감한 속성별 균형 분석"""
        balances = []
        
        for attr in sensitive_features:
            if attr not in data.columns:
                continue
            
            # 그룹별 분포
            group_counts = data[attr].value_counts()
            group_distribution = {str(k): int(v) for k, v in group_counts.items()}
            
            # 그룹별 긍정 결과 비율
            positive_rates = {}
            positive_class = data[label_column].value_counts().index[0]  # 가장 빈번한 클래스를 긍정으로 가정
            
            for group in data[attr].unique():
                group_data = data[data[attr] == group]
                positive_rate = (group_data[label_column] == positive_class).mean()
                positive_rates[str(group)] = float(positive_rate)
            
            # Statistical Parity Difference
            rates = list(positive_rates.values())
            spd = max(rates) - min(rates) if rates else 0
            
            # Disparate Impact Ratio
            dir_ratio = min(rates) / max(rates) if max(rates) > 0 else 1.0
            
            # 공정성 판단 (80% 규칙)
            is_fair = dir_ratio >= 0.8
            
            recommendations = []
            if not is_fair:
                recommendations.append(f"'{attr}'에서 그룹 간 결과 차이가 발견되었습니다.")
                recommendations.append(f"Disparate Impact Ratio: {dir_ratio:.2f} (권장: >= 0.8)")
                recommendations.append("공정성 제약 조건을 적용하거나 데이터 리밸런싱을 고려하세요.")
            
            balances.append(SensitiveAttributeBalance(
                attribute_name=attr,
                group_distribution=group_distribution,
                positive_outcome_rates=positive_rates,
                statistical_parity_difference=float(spd),
                disparate_impact_ratio=float(dir_ratio),
                is_fair=is_fair,
                recommendations=recommendations,
            ))
        
        return balances
    
    def _intersectional_analysis(
        self,
        data: pd.DataFrame,
        sensitive_features: List[str],
        label_column: str,
    ) -> Dict[str, Any]:
        """교차 분석 (두 민감한 속성의 조합)"""
        if len(sensitive_features) < 2:
            return {"message": "교차 분석에는 2개 이상의 민감한 속성이 필요합니다."}
        
        attr1, attr2 = sensitive_features[0], sensitive_features[1]
        
        # 교차 그룹 생성
        data["_intersect"] = data[attr1].astype(str) + "_" + data[attr2].astype(str)
        
        # 교차 그룹별 분포 및 결과
        intersect_counts = data["_intersect"].value_counts()
        positive_class = data[label_column].value_counts().index[0]
        
        intersect_results = {}
        for group in data["_intersect"].unique():
            group_data = data[data["_intersect"] == group]
            intersect_results[group] = {
                "count": int(len(group_data)),
                "percentage": float(len(group_data) / len(data) * 100),
                "positive_rate": float((group_data[label_column] == positive_class).mean()),
            }
        
        # 교차 불균형 분석
        rates = [r["positive_rate"] for r in intersect_results.values()]
        max_disparity = max(rates) - min(rates) if rates else 0
        
        # 정리
        data.drop("_intersect", axis=1, inplace=True)
        
        return {
            "attributes": [attr1, attr2],
            "intersectional_groups": intersect_results,
            "max_disparity": float(max_disparity),
            "is_intersectionally_fair": max_disparity < 0.2,
            "recommendations": [
                f"교차 그룹 간 최대 차이: {max_disparity:.2%}"
            ] if max_disparity >= 0.2 else [],
        }
    
    def _assess_data_quality(self, data: pd.DataFrame) -> Dict[str, Any]:
        """데이터 품질 평가"""
        quality = {
            "completeness": {},
            "uniqueness": {},
            "consistency": {},
            "overall_score": 0.0,
        }
        
        scores = []
        
        # 완전성 (결측치 비율)
        for col in data.columns:
            missing_rate = data[col].isna().mean()
            quality["completeness"][col] = float(1 - missing_rate)
            scores.append(1 - missing_rate)
        
        # 고유성 (중복 행 비율)
        duplicate_rate = data.duplicated().mean()
        quality["uniqueness"]["duplicate_rate"] = float(duplicate_rate)
        quality["uniqueness"]["score"] = float(1 - duplicate_rate)
        scores.append(1 - duplicate_rate)
        
        # 일관성 (데이터 타입 일관성)
        type_consistency = 1.0
        for col in data.columns:
            try:
                # 수치형 컬럼에 문자열이 있는지 확인
                if data[col].dtype == 'object':
                    numeric_count = pd.to_numeric(data[col], errors='coerce').notna().sum()
                    if numeric_count > 0 and numeric_count < len(data[col]):
                        type_consistency -= 0.1
            except:
                pass
        quality["consistency"]["type_consistency"] = float(max(0, type_consistency))
        scores.append(type_consistency)
        
        quality["overall_score"] = float(np.mean(scores))
        
        return quality
    
    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """분석 요약 생성"""
        summary = {
            "total_features_analyzed": len(results.get("feature_balance", [])),
            "imbalanced_features": [],
            "label_status": "unknown",
            "fairness_status": "unknown",
            "data_quality_score": results.get("data_quality", {}).get("overall_score", 0),
            "key_findings": [],
            "priority_actions": [],
        }
        
        # 불균형 특성 식별
        for fb in results.get("feature_balance", []):
            if fb["imbalance_score"] > 0.5:
                summary["imbalanced_features"].append(fb["feature_name"])
        
        # 레이블 상태
        label_balance = results.get("label_balance")
        if label_balance:
            summary["label_status"] = "balanced" if label_balance["is_balanced"] else "imbalanced"
            if not label_balance["is_balanced"]:
                summary["key_findings"].append(
                    f"레이블 불균형 감지: {label_balance['imbalance_ratio']:.1f}:1 비율"
                )
                summary["priority_actions"].append("레이블 리밸런싱 필요")
        
        # 공정성 상태
        sensitive_balances = results.get("sensitive_attribute_balance", [])
        unfair_attrs = [sb["attribute_name"] for sb in sensitive_balances if not sb["is_fair"]]
        
        if sensitive_balances:
            if unfair_attrs:
                summary["fairness_status"] = "unfair"
                summary["key_findings"].append(
                    f"공정성 문제 감지: {', '.join(unfair_attrs)}"
                )
                summary["priority_actions"].append("공정성 개선 조치 필요")
            else:
                summary["fairness_status"] = "fair"
        
        # 데이터 품질 관련
        if summary["data_quality_score"] < 0.8:
            summary["key_findings"].append(
                f"데이터 품질 점수가 낮습니다: {summary['data_quality_score']:.2f}"
            )
            summary["priority_actions"].append("데이터 정제 및 전처리 필요")
        
        return summary
    
    def _feature_balance_to_dict(self, fb: FeatureBalance) -> Dict[str, Any]:
        """FeatureBalance를 딕셔너리로 변환"""
        return {
            "feature_name": fb.feature_name,
            "feature_type": fb.feature_type,
            "distribution": fb.distribution,
            "imbalance_score": fb.imbalance_score,
            "majority_class": fb.majority_class,
            "minority_class": fb.minority_class,
            "imbalance_ratio": fb.imbalance_ratio,
            "recommendations": fb.recommendations,
        }
    
    def _label_balance_to_dict(self, lb: LabelBalance) -> Dict[str, Any]:
        """LabelBalance를 딕셔너리로 변환"""
        return {
            "label_name": lb.label_name,
            "class_distribution": lb.class_distribution,
            "class_percentages": lb.class_percentages,
            "imbalance_ratio": lb.imbalance_ratio,
            "is_balanced": lb.is_balanced,
            "majority_class": lb.majority_class,
            "minority_class": lb.minority_class,
            "recommendations": lb.recommendations,
        }
    
    def _sensitive_balance_to_dict(self, sb: SensitiveAttributeBalance) -> Dict[str, Any]:
        """SensitiveAttributeBalance를 딕셔너리로 변환"""
        return {
            "attribute_name": sb.attribute_name,
            "group_distribution": sb.group_distribution,
            "positive_outcome_rates": sb.positive_outcome_rates,
            "statistical_parity_difference": sb.statistical_parity_difference,
            "disparate_impact_ratio": sb.disparate_impact_ratio,
            "is_fair": sb.is_fair,
            "recommendations": sb.recommendations,
        }
    
    def get_feature_balances(self) -> List[FeatureBalance]:
        """특성 균형 결과 반환"""
        return self._feature_balances
    
    def get_label_balance(self) -> Optional[LabelBalance]:
        """레이블 균형 결과 반환"""
        return self._label_balance
    
    def get_sensitive_balances(self) -> List[SensitiveAttributeBalance]:
        """민감한 속성 균형 결과 반환"""
        return self._sensitive_balances


def create_data_balance_analyzer(
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> DataBalanceAnalyzer:
    """DataBalanceAnalyzer 인스턴스 생성 헬퍼 함수"""
    return DataBalanceAnalyzer(config=config, **kwargs)

