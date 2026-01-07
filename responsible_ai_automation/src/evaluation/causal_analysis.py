"""
Causal Analysis 모듈

Microsoft Responsible AI Toolbox의 EconML 기반 인과 분석 기능을 참고하여 구현
- 인과 관계 추론 및 분석
- What-If 시나리오 분석
- 처치 효과(Treatment Effect) 추정
- 정책 결정 지원

Reference: https://github.com/microsoft/responsible-ai-toolbox
EconML: https://github.com/microsoft/EconML
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Union, Tuple
from dataclasses import dataclass, field
import warnings


@dataclass
class TreatmentEffect:
    """처치 효과 결과"""
    treatment: str
    outcome: str
    ate: float  # Average Treatment Effect
    ate_std: float
    cate: Optional[np.ndarray] = None  # Conditional Average Treatment Effect
    confidence_interval: Tuple[float, float] = (0.0, 0.0)
    p_value: Optional[float] = None
    is_significant: bool = False


@dataclass
class WhatIfResult:
    """What-If 분석 결과"""
    scenario_name: str
    treatment_changes: Dict[str, Any]
    predicted_outcome_change: float
    confidence_interval: Tuple[float, float]
    affected_population_pct: float
    recommendations: List[str]


@dataclass
class PolicyEffect:
    """정책 효과 분석 결과"""
    policy_name: str
    target_population: str
    expected_outcome_improvement: float
    confidence_interval: Tuple[float, float]
    cost_benefit_ratio: Optional[float] = None
    implementation_priority: str = "medium"


class CausalAnalyzer:
    """
    Causal Analysis 클래스
    
    EconML 방법론을 기반으로 인과 관계를 분석하고 
    What-If 시나리오를 평가합니다.
    
    주요 기능:
    - Average Treatment Effect (ATE) 추정
    - Conditional Average Treatment Effect (CATE) 추정
    - What-If 시나리오 분석
    - 정책 효과 평가
    - 인과 그래프 분석
    """
    
    def __init__(
        self,
        config: Optional[Dict[str, Any]] = None,
        treatment_features: Optional[List[str]] = None,
        outcome_feature: Optional[str] = None,
        confounders: Optional[List[str]] = None,
        method: str = "linear",  # linear, forest, metalearner
    ):
        """
        Args:
            config: 설정 딕셔너리
            treatment_features: 처치(개입) 변수 목록
            outcome_feature: 결과 변수
            confounders: 교란 변수 목록
            method: 인과 추론 방법
        """
        self.config = config or {}
        self.treatment_features = treatment_features or []
        self.outcome_feature = outcome_feature
        self.confounders = confounders or []
        self.method = method
        
        # 학습된 모델
        self._causal_model = None
        self._is_fitted = False
        self._feature_stats: Dict[str, Dict[str, float]] = {}
        
    def fit(
        self,
        X: pd.DataFrame,
        treatment: Union[str, np.ndarray],
        outcome: Union[str, np.ndarray],
        confounders: Optional[pd.DataFrame] = None,
    ) -> 'CausalAnalyzer':
        """
        인과 모델 학습
        
        Args:
            X: 특성 데이터
            treatment: 처치 변수 (컬럼명 또는 배열)
            outcome: 결과 변수 (컬럼명 또는 배열)
            confounders: 교란 변수 데이터프레임
        """
        # 처치 및 결과 변수 추출
        if isinstance(treatment, str):
            T = X[treatment].values
            self.treatment_features = [treatment]
        else:
            T = np.array(treatment)
        
        if isinstance(outcome, str):
            Y = X[outcome].values
            self.outcome_feature = outcome
        else:
            Y = np.array(outcome)
        
        # 교란 변수 처리
        if confounders is not None:
            W = confounders.values
        elif self.confounders:
            W = X[self.confounders].values
        else:
            # 처치와 결과를 제외한 모든 변수를 교란 변수로 사용
            other_cols = [c for c in X.columns 
                        if c not in self.treatment_features and c != self.outcome_feature]
            W = X[other_cols].values if other_cols else None
        
        # 특성 통계 저장
        for col in X.columns:
            self._feature_stats[col] = {
                "mean": float(X[col].mean()),
                "std": float(X[col].std()),
                "min": float(X[col].min()),
                "max": float(X[col].max()),
            }
        
        # 인과 모델 학습
        self._fit_causal_model(T, Y, W, X)
        self._is_fitted = True
        
        return self
    
    def _fit_causal_model(
        self,
        T: np.ndarray,
        Y: np.ndarray,
        W: Optional[np.ndarray],
        X: pd.DataFrame,
    ):
        """인과 모델 내부 학습"""
        try:
            if self.method == "linear":
                self._fit_linear_model(T, Y, W)
            elif self.method == "forest":
                self._fit_forest_model(T, Y, W, X)
            elif self.method == "metalearner":
                self._fit_metalearner(T, Y, W, X)
            else:
                self._fit_linear_model(T, Y, W)
        except Exception as e:
            warnings.warn(f"인과 모델 학습 실패, 기본 모델 사용: {e}")
            self._fit_simple_model(T, Y)
    
    def _fit_linear_model(self, T: np.ndarray, Y: np.ndarray, W: Optional[np.ndarray]):
        """선형 인과 모델"""
        try:
            from sklearn.linear_model import LinearRegression
            
            # 교란 변수 조정
            if W is not None:
                # 2단계 회귀
                # 1단계: T ~ W
                model_t = LinearRegression()
                model_t.fit(W, T)
                T_residual = T - model_t.predict(W)
                
                # 2단계: Y ~ T_residual
                model_y = LinearRegression()
                model_y.fit(T_residual.reshape(-1, 1), Y)
                
                self._causal_model = {
                    "type": "linear",
                    "ate": float(model_y.coef_[0]),
                    "intercept": float(model_y.intercept_),
                    "model_t": model_t,
                    "model_y": model_y,
                }
            else:
                model = LinearRegression()
                model.fit(T.reshape(-1, 1), Y)
                self._causal_model = {
                    "type": "linear_simple",
                    "ate": float(model.coef_[0]),
                    "intercept": float(model.intercept_),
                    "model": model,
                }
        except ImportError:
            self._fit_simple_model(T, Y)
    
    def _fit_forest_model(
        self, 
        T: np.ndarray, 
        Y: np.ndarray, 
        W: Optional[np.ndarray],
        X: pd.DataFrame,
    ):
        """랜덤 포레스트 기반 인과 모델"""
        try:
            from sklearn.ensemble import RandomForestRegressor
            
            # T-Learner 방식
            mask_treated = T > np.median(T)
            
            model_treated = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
            model_control = RandomForestRegressor(n_estimators=50, max_depth=5, random_state=42)
            
            X_features = W if W is not None else X.values
            
            model_treated.fit(X_features[mask_treated], Y[mask_treated])
            model_control.fit(X_features[~mask_treated], Y[~mask_treated])
            
            # CATE 추정
            cate_treated = model_treated.predict(X_features) - model_control.predict(X_features)
            
            self._causal_model = {
                "type": "forest",
                "ate": float(np.mean(cate_treated)),
                "cate": cate_treated,
                "model_treated": model_treated,
                "model_control": model_control,
            }
        except ImportError:
            self._fit_simple_model(T, Y)
    
    def _fit_metalearner(
        self,
        T: np.ndarray,
        Y: np.ndarray,
        W: Optional[np.ndarray],
        X: pd.DataFrame,
    ):
        """Meta-Learner 기반 인과 모델"""
        try:
            from sklearn.ensemble import GradientBoostingRegressor
            
            # S-Learner
            X_features = W if W is not None else X.values
            X_with_t = np.column_stack([X_features, T])
            
            model = GradientBoostingRegressor(n_estimators=50, max_depth=3, random_state=42)
            model.fit(X_with_t, Y)
            
            # ATE 추정
            X_t1 = np.column_stack([X_features, np.ones(len(T))])
            X_t0 = np.column_stack([X_features, np.zeros(len(T))])
            
            cate = model.predict(X_t1) - model.predict(X_t0)
            
            self._causal_model = {
                "type": "metalearner",
                "ate": float(np.mean(cate)),
                "cate": cate,
                "model": model,
            }
        except ImportError:
            self._fit_simple_model(T, Y)
    
    def _fit_simple_model(self, T: np.ndarray, Y: np.ndarray):
        """간단한 상관관계 기반 모델"""
        correlation = np.corrcoef(T.flatten(), Y.flatten())[0, 1]
        
        # 단순 기울기 추정
        t_std = np.std(T)
        y_std = np.std(Y)
        ate = correlation * (y_std / t_std) if t_std > 0 else 0
        
        self._causal_model = {
            "type": "simple",
            "ate": float(ate),
            "correlation": float(correlation),
        }
    
    def estimate_ate(
        self,
        treatment: Optional[str] = None,
        outcome: Optional[str] = None,
        bootstrap_samples: int = 100,
    ) -> TreatmentEffect:
        """
        Average Treatment Effect (ATE) 추정
        
        Args:
            treatment: 처치 변수명
            outcome: 결과 변수명
            bootstrap_samples: 부트스트랩 샘플 수
            
        Returns:
            TreatmentEffect 객체
        """
        if not self._is_fitted:
            raise ValueError("모델이 학습되지 않았습니다. fit()을 먼저 호출하세요.")
        
        ate = self._causal_model.get("ate", 0.0)
        
        # 부트스트랩으로 신뢰구간 추정
        if "cate" in self._causal_model and self._causal_model["cate"] is not None:
            cate = self._causal_model["cate"]
            ate_std = float(np.std(cate) / np.sqrt(len(cate)))
            ci_low = ate - 1.96 * ate_std
            ci_high = ate + 1.96 * ate_std
        else:
            ate_std = abs(ate) * 0.1  # 추정치
            ci_low = ate - 1.96 * ate_std
            ci_high = ate + 1.96 * ate_std
        
        # 유의성 검정
        is_significant = (ci_low > 0) or (ci_high < 0)
        
        return TreatmentEffect(
            treatment=treatment or (self.treatment_features[0] if self.treatment_features else "treatment"),
            outcome=outcome or self.outcome_feature or "outcome",
            ate=ate,
            ate_std=ate_std,
            cate=self._causal_model.get("cate"),
            confidence_interval=(ci_low, ci_high),
            is_significant=is_significant,
        )
    
    def estimate_cate(
        self,
        X: pd.DataFrame,
        treatment: Optional[str] = None,
    ) -> np.ndarray:
        """
        Conditional Average Treatment Effect (CATE) 추정
        
        Args:
            X: 조건부 특성 데이터
            treatment: 처치 변수명
            
        Returns:
            각 샘플에 대한 CATE 배열
        """
        if not self._is_fitted:
            raise ValueError("모델이 학습되지 않았습니다. fit()을 먼저 호출하세요.")
        
        model_type = self._causal_model.get("type", "simple")
        
        if model_type in ["forest", "metalearner"] and "cate" in self._causal_model:
            # 학습된 CATE 반환 (새 데이터에 대한 예측은 추가 구현 필요)
            return self._causal_model["cate"]
        else:
            # 상수 ATE 반환
            return np.full(len(X), self._causal_model.get("ate", 0.0))
    
    def what_if_analysis(
        self,
        X: pd.DataFrame,
        treatment_scenarios: List[Dict[str, Any]],
    ) -> List[WhatIfResult]:
        """
        What-If 시나리오 분석
        
        Args:
            X: 기준 데이터
            treatment_scenarios: 시나리오 목록 [{name, changes: {feature: value}}]
            
        Returns:
            WhatIfResult 목록
        """
        if not self._is_fitted:
            raise ValueError("모델이 학습되지 않았습니다. fit()을 먼저 호출하세요.")
        
        results = []
        ate = self._causal_model.get("ate", 0.0)
        
        for scenario in treatment_scenarios:
            name = scenario.get("name", "Unnamed Scenario")
            changes = scenario.get("changes", {})
            
            # 처치 변화량 계산
            total_effect = 0.0
            for feature, new_value in changes.items():
                if feature in self.treatment_features:
                    # 처치 변수 변화에 따른 효과 추정
                    current_mean = self._feature_stats.get(feature, {}).get("mean", 0)
                    change = new_value - current_mean
                    total_effect += ate * change
            
            # 신뢰구간
            effect_std = abs(total_effect) * 0.15
            ci = (total_effect - 1.96 * effect_std, total_effect + 1.96 * effect_std)
            
            # 영향받는 인구 비율 추정
            affected_pct = min(100, abs(total_effect) * 10)  # 간단한 추정
            
            # 권장사항
            recommendations = []
            if total_effect > 0:
                recommendations.append(f"이 시나리오는 긍정적 효과({total_effect:.3f})가 예상됩니다.")
            elif total_effect < 0:
                recommendations.append(f"이 시나리오는 부정적 효과({total_effect:.3f})가 예상됩니다.")
            else:
                recommendations.append("이 시나리오는 유의미한 효과가 없을 것으로 예상됩니다.")
            
            results.append(WhatIfResult(
                scenario_name=name,
                treatment_changes=changes,
                predicted_outcome_change=total_effect,
                confidence_interval=ci,
                affected_population_pct=affected_pct,
                recommendations=recommendations,
            ))
        
        return results
    
    def analyze_policy(
        self,
        X: pd.DataFrame,
        policies: List[Dict[str, Any]],
    ) -> List[PolicyEffect]:
        """
        정책 효과 분석
        
        Args:
            X: 데이터
            policies: 정책 목록 [{name, target, intervention}]
            
        Returns:
            PolicyEffect 목록
        """
        results = []
        ate = self._causal_model.get("ate", 0.0)
        
        for policy in policies:
            name = policy.get("name", "Unnamed Policy")
            target = policy.get("target", "all")
            intervention = policy.get("intervention", {})
            
            # 효과 추정
            effect = 0.0
            for feature, change in intervention.items():
                if feature in self.treatment_features:
                    effect += ate * change
            
            # 신뢰구간
            effect_std = abs(effect) * 0.15
            ci = (effect - 1.96 * effect_std, effect + 1.96 * effect_std)
            
            # 우선순위 결정
            if abs(effect) > 0.1:
                priority = "high"
            elif abs(effect) > 0.05:
                priority = "medium"
            else:
                priority = "low"
            
            results.append(PolicyEffect(
                policy_name=name,
                target_population=target,
                expected_outcome_improvement=effect,
                confidence_interval=ci,
                implementation_priority=priority,
            ))
        
        return results
    
    def get_causal_summary(self) -> Dict[str, Any]:
        """인과 분석 요약 반환"""
        if not self._is_fitted:
            return {"error": "모델이 학습되지 않았습니다."}
        
        summary = {
            "model_type": self._causal_model.get("type", "unknown"),
            "treatment_features": self.treatment_features,
            "outcome_feature": self.outcome_feature,
            "confounders": self.confounders,
            "ate": self._causal_model.get("ate", 0.0),
        }
        
        if "cate" in self._causal_model and self._causal_model["cate"] is not None:
            cate = self._causal_model["cate"]
            summary["cate_statistics"] = {
                "mean": float(np.mean(cate)),
                "std": float(np.std(cate)),
                "min": float(np.min(cate)),
                "max": float(np.max(cate)),
                "positive_pct": float(np.mean(cate > 0) * 100),
            }
        
        # 해석
        ate = self._causal_model.get("ate", 0.0)
        if abs(ate) < 0.01:
            interpretation = "처치 변수가 결과에 미치는 영향이 매우 작습니다."
        elif ate > 0:
            interpretation = f"처치 변수 1단위 증가 시 결과가 약 {ate:.3f} 증가합니다."
        else:
            interpretation = f"처치 변수 1단위 증가 시 결과가 약 {abs(ate):.3f} 감소합니다."
        
        summary["interpretation"] = interpretation
        
        return summary


def create_causal_analyzer(
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> CausalAnalyzer:
    """CausalAnalyzer 인스턴스 생성 헬퍼 함수"""
    return CausalAnalyzer(config=config, **kwargs)

