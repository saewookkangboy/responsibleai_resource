"""
Responsible AI Dashboard 통합 모듈

Microsoft Responsible AI Toolbox의 ResponsibleAIDashboard를 참고하여 구현
- 통합된 모델 분석 대시보드
- Error Analysis, Counterfactual, Causal Analysis, Data Balance 통합
- 인터랙티브 시각화 및 분석

Reference: https://github.com/microsoft/responsible-ai-toolbox
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, field
import json
import warnings


@dataclass
class DashboardConfig:
    """대시보드 설정"""
    title: str = "Responsible AI Dashboard"
    components: List[str] = field(default_factory=lambda: [
        "model_overview",
        "error_analysis",
        "data_explorer",
        "fairness_assessment",
        "counterfactual_analysis",
        "causal_analysis",
    ])
    theme: str = "light"
    locale: str = "ko"
    port: int = 8050


class ResponsibleAIDashboard:
    """
    Responsible AI Dashboard 클래스
    
    Microsoft Responsible AI Toolbox의 ResponsibleAIDashboard를 참고하여
    모델 분석을 위한 통합 대시보드를 제공합니다.
    
    주요 기능:
    - Model Overview: 모델 성능 및 메트릭 개요
    - Error Analysis: 오류 분석 및 코호트 식별
    - Data Explorer: 데이터 탐색 및 시각화
    - Fairness Assessment: 공정성 평가
    - Counterfactual Analysis: 반사실적 분석
    - Causal Analysis: 인과 분석
    - Feature Importance: 특성 중요도 분석
    """
    
    def __init__(
        self,
        model: Any,
        X_train: pd.DataFrame,
        y_train: np.ndarray,
        X_test: pd.DataFrame,
        y_test: np.ndarray,
        task_type: str = "classification",  # classification, regression
        sensitive_features: Optional[List[str]] = None,
        categorical_features: Optional[List[str]] = None,
        treatment_features: Optional[List[str]] = None,
        config: Optional[DashboardConfig] = None,
    ):
        """
        Args:
            model: 학습된 모델 (predict, predict_proba 메서드 필요)
            X_train: 학습 데이터
            y_train: 학습 레이블
            X_test: 테스트 데이터
            y_test: 테스트 레이블
            task_type: 태스크 유형
            sensitive_features: 민감한 속성 목록
            categorical_features: 범주형 특성 목록
            treatment_features: 처치 변수 목록 (인과 분석용)
            config: 대시보드 설정
        """
        self.model = model
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        self.task_type = task_type
        self.sensitive_features = sensitive_features or []
        self.categorical_features = categorical_features or []
        self.treatment_features = treatment_features or []
        self.config = config or DashboardConfig()
        
        # 분석기 인스턴스
        self._error_analyzer = None
        self._counterfactual_analyzer = None
        self._causal_analyzer = None
        self._data_balance_analyzer = None
        
        # 분석 결과 캐시
        self._analysis_cache: Dict[str, Any] = {}
        
        # 예측 결과
        self._y_pred_train = None
        self._y_pred_test = None
        
    def _get_predictions(self):
        """예측 결과 계산"""
        if self._y_pred_train is None:
            self._y_pred_train = self.model.predict(self.X_train)
        if self._y_pred_test is None:
            self._y_pred_test = self.model.predict(self.X_test)
        return self._y_pred_train, self._y_pred_test
    
    def compute_model_overview(self) -> Dict[str, Any]:
        """모델 개요 계산"""
        y_pred_train, y_pred_test = self._get_predictions()
        
        overview = {
            "task_type": self.task_type,
            "train_samples": len(self.X_train),
            "test_samples": len(self.X_test),
            "num_features": len(self.X_train.columns),
            "feature_names": list(self.X_train.columns),
        }
        
        if self.task_type == "classification":
            overview["metrics"] = self._compute_classification_metrics(
                self.y_test, y_pred_test
            )
            overview["train_metrics"] = self._compute_classification_metrics(
                self.y_train, y_pred_train
            )
        else:
            overview["metrics"] = self._compute_regression_metrics(
                self.y_test, y_pred_test
            )
            overview["train_metrics"] = self._compute_regression_metrics(
                self.y_train, y_pred_train
            )
        
        # 과적합 여부 확인
        train_score = overview["train_metrics"].get("accuracy", overview["train_metrics"].get("r2", 0))
        test_score = overview["metrics"].get("accuracy", overview["metrics"].get("r2", 0))
        overview["overfitting_risk"] = "high" if train_score - test_score > 0.1 else "low"
        
        self._analysis_cache["model_overview"] = overview
        return overview
    
    def _compute_classification_metrics(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """분류 메트릭 계산"""
        try:
            from sklearn.metrics import (
                accuracy_score, precision_score, recall_score, f1_score,
                confusion_matrix
            )
            
            metrics = {
                "accuracy": float(accuracy_score(y_true, y_pred)),
            }
            
            # 이진 분류인 경우
            if len(np.unique(y_true)) == 2:
                metrics["precision"] = float(precision_score(y_true, y_pred, zero_division=0))
                metrics["recall"] = float(recall_score(y_true, y_pred, zero_division=0))
                metrics["f1"] = float(f1_score(y_true, y_pred, zero_division=0))
            else:
                metrics["precision_macro"] = float(precision_score(y_true, y_pred, average='macro', zero_division=0))
                metrics["recall_macro"] = float(recall_score(y_true, y_pred, average='macro', zero_division=0))
                metrics["f1_macro"] = float(f1_score(y_true, y_pred, average='macro', zero_division=0))
            
            # 혼동 행렬
            cm = confusion_matrix(y_true, y_pred)
            metrics["confusion_matrix"] = cm.tolist()
            
            return metrics
            
        except ImportError:
            return {"accuracy": float(np.mean(y_true == y_pred))}
    
    def _compute_regression_metrics(
        self, 
        y_true: np.ndarray, 
        y_pred: np.ndarray
    ) -> Dict[str, float]:
        """회귀 메트릭 계산"""
        try:
            from sklearn.metrics import (
                mean_squared_error, mean_absolute_error, r2_score
            )
            
            return {
                "mse": float(mean_squared_error(y_true, y_pred)),
                "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
                "mae": float(mean_absolute_error(y_true, y_pred)),
                "r2": float(r2_score(y_true, y_pred)),
            }
            
        except ImportError:
            mse = float(np.mean((y_true - y_pred) ** 2))
            return {"mse": mse, "rmse": float(np.sqrt(mse))}
    
    def compute_error_analysis(self) -> Dict[str, Any]:
        """오류 분석 수행"""
        from ..evaluation.error_analysis import ErrorAnalyzer
        
        y_pred_train, y_pred_test = self._get_predictions()
        
        self._error_analyzer = ErrorAnalyzer()
        results = self._error_analyzer.analyze(
            X=self.X_test,
            y_true=self.y_test,
            y_pred=y_pred_test,
            feature_names=list(self.X_test.columns),
            categorical_features=self.categorical_features,
        )
        
        self._analysis_cache["error_analysis"] = results
        return results
    
    def compute_fairness_assessment(self) -> Dict[str, Any]:
        """공정성 평가 수행"""
        if not self.sensitive_features:
            return {"message": "민감한 속성이 지정되지 않았습니다."}
        
        from ..evaluation.fairness import FairnessEvaluator
        
        y_pred_train, y_pred_test = self._get_predictions()
        
        config = {
            "fairness": {
                "metrics": ["demographic_parity", "equalized_odds", "equal_opportunity"],
                "sensitive_attributes": self.sensitive_features,
                "threshold": 0.1,
            }
        }
        
        evaluator = FairnessEvaluator(config)
        
        # 민감한 속성 데이터프레임 생성
        sensitive_df = self.X_test[self.sensitive_features].copy()
        
        results = evaluator.evaluate(
            y_true=self.y_test,
            y_pred=y_pred_test,
            sensitive_features=sensitive_df,
        )
        
        self._analysis_cache["fairness_assessment"] = results
        return results
    
    def compute_counterfactual_analysis(
        self,
        instance_indices: Optional[List[int]] = None,
        desired_outcome: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """반사실적 분석 수행"""
        from ..evaluation.counterfactual import CounterfactualAnalyzer
        
        self._counterfactual_analyzer = CounterfactualAnalyzer(
            num_counterfactuals=5,
            features_to_vary=[c for c in self.X_test.columns if c not in self.sensitive_features],
        )
        self._counterfactual_analyzer.fit(
            self.X_train, 
            categorical_features=self.categorical_features
        )
        
        # 분석할 인스턴스 선택
        if instance_indices is None:
            # 기본적으로 잘못 예측된 샘플 중 5개 선택
            y_pred = self._get_predictions()[1]
            wrong_indices = np.where(self.y_test != y_pred)[0]
            instance_indices = wrong_indices[:5].tolist() if len(wrong_indices) > 0 else [0]
        
        # 원하는 결과 결정
        if desired_outcome is None:
            # 현재 예측과 다른 결과
            y_pred = self._get_predictions()[1]
            unique_classes = np.unique(self.y_test)
            desired_outcome = [c for c in unique_classes if c != y_pred[instance_indices[0]]]
        
        # 예측 함수
        def predict_fn(X):
            return self.model.predict(X)
        
        results = {
            "explanations": [],
            "summary": {},
        }
        
        for idx in instance_indices:
            instance = self.X_test.iloc[idx]
            explanation = self._counterfactual_analyzer.generate_counterfactuals(
                instance=instance,
                predict_fn=predict_fn,
                desired_outcome=desired_outcome,
                instance_id=idx,
            )
            results["explanations"].append({
                "instance_id": explanation.instance_id,
                "original_prediction": explanation.original_prediction,
                "desired_outcome": explanation.desired_outcome,
                "num_counterfactuals": len(explanation.counterfactuals),
                "summary": explanation.summary,
            })
        
        self._analysis_cache["counterfactual_analysis"] = results
        return results
    
    def compute_causal_analysis(
        self,
        treatment: Optional[str] = None,
        outcome: Optional[str] = None,
    ) -> Dict[str, Any]:
        """인과 분석 수행"""
        if not self.treatment_features and treatment is None:
            return {"message": "처치 변수가 지정되지 않았습니다."}
        
        from ..evaluation.causal_analysis import CausalAnalyzer
        
        treatment = treatment or self.treatment_features[0]
        
        # 결과 변수 (레이블 사용)
        train_data = self.X_train.copy()
        train_data["_outcome"] = self.y_train
        
        self._causal_analyzer = CausalAnalyzer(
            treatment_features=[treatment],
            outcome_feature="_outcome",
            method="linear",
        )
        
        self._causal_analyzer.fit(
            X=train_data,
            treatment=treatment,
            outcome="_outcome",
        )
        
        # ATE 추정
        ate_result = self._causal_analyzer.estimate_ate(
            treatment=treatment,
            outcome="_outcome",
        )
        
        # What-If 시나리오
        scenarios = [
            {"name": f"{treatment} 10% 증가", "changes": {treatment: self.X_train[treatment].mean() * 1.1}},
            {"name": f"{treatment} 10% 감소", "changes": {treatment: self.X_train[treatment].mean() * 0.9}},
        ]
        what_if_results = self._causal_analyzer.what_if_analysis(self.X_test, scenarios)
        
        results = {
            "treatment_effect": {
                "treatment": ate_result.treatment,
                "outcome": ate_result.outcome,
                "ate": ate_result.ate,
                "ate_std": ate_result.ate_std,
                "confidence_interval": ate_result.confidence_interval,
                "is_significant": ate_result.is_significant,
            },
            "what_if_scenarios": [
                {
                    "scenario_name": wir.scenario_name,
                    "predicted_outcome_change": wir.predicted_outcome_change,
                    "confidence_interval": wir.confidence_interval,
                    "recommendations": wir.recommendations,
                }
                for wir in what_if_results
            ],
            "summary": self._causal_analyzer.get_causal_summary(),
        }
        
        self._analysis_cache["causal_analysis"] = results
        return results
    
    def compute_data_balance(self) -> Dict[str, Any]:
        """데이터 균형 분석 수행"""
        from ..evaluation.data_balance import DataBalanceAnalyzer
        
        # 학습 데이터에 레이블 추가
        train_data = self.X_train.copy()
        train_data["_label"] = self.y_train
        
        self._data_balance_analyzer = DataBalanceAnalyzer(
            sensitive_features=self.sensitive_features,
            label_column="_label",
        )
        
        results = self._data_balance_analyzer.analyze(
            data=train_data,
            label_column="_label",
            sensitive_features=self.sensitive_features,
            categorical_features=self.categorical_features,
        )
        
        self._analysis_cache["data_balance"] = results
        return results
    
    def compute_all(self) -> Dict[str, Any]:
        """모든 분석 수행"""
        results = {}
        
        # 1. 모델 개요
        results["model_overview"] = self.compute_model_overview()
        
        # 2. 오류 분석
        try:
            results["error_analysis"] = self.compute_error_analysis()
        except Exception as e:
            results["error_analysis"] = {"error": str(e)}
        
        # 3. 공정성 평가
        try:
            results["fairness_assessment"] = self.compute_fairness_assessment()
        except Exception as e:
            results["fairness_assessment"] = {"error": str(e)}
        
        # 4. 데이터 균형
        try:
            results["data_balance"] = self.compute_data_balance()
        except Exception as e:
            results["data_balance"] = {"error": str(e)}
        
        # 5. 반사실적 분석 (선택적)
        try:
            results["counterfactual_analysis"] = self.compute_counterfactual_analysis()
        except Exception as e:
            results["counterfactual_analysis"] = {"error": str(e)}
        
        # 6. 인과 분석 (처치 변수가 있는 경우)
        if self.treatment_features:
            try:
                results["causal_analysis"] = self.compute_causal_analysis()
            except Exception as e:
                results["causal_analysis"] = {"error": str(e)}
        
        return results
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """대시보드용 데이터 반환"""
        if not self._analysis_cache:
            self.compute_all()
        
        return {
            "config": {
                "title": self.config.title,
                "components": self.config.components,
                "theme": self.config.theme,
                "locale": self.config.locale,
            },
            "analysis_results": self._analysis_cache,
            "metadata": {
                "task_type": self.task_type,
                "num_features": len(self.X_train.columns),
                "train_samples": len(self.X_train),
                "test_samples": len(self.X_test),
                "sensitive_features": self.sensitive_features,
                "categorical_features": self.categorical_features,
            },
        }
    
    def export_to_json(self, filepath: str):
        """분석 결과를 JSON으로 내보내기"""
        data = self.get_dashboard_data()
        
        # numpy 타입 변환
        def convert_numpy(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.int64, np.int32)):
                return int(obj)
            elif isinstance(obj, (np.float64, np.float32)):
                return float(obj)
            elif isinstance(obj, dict):
                return {k: convert_numpy(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(v) for v in obj]
            return obj
        
        data = convert_numpy(data)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def generate_report(self) -> str:
        """분석 리포트 생성"""
        if not self._analysis_cache:
            self.compute_all()
        
        report = []
        report.append(f"# {self.config.title}")
        report.append("")
        
        # 모델 개요
        if "model_overview" in self._analysis_cache:
            overview = self._analysis_cache["model_overview"]
            report.append("## 1. 모델 개요")
            report.append(f"- 태스크 유형: {overview['task_type']}")
            report.append(f"- 학습 샘플: {overview['train_samples']:,}")
            report.append(f"- 테스트 샘플: {overview['test_samples']:,}")
            report.append(f"- 특성 수: {overview['num_features']}")
            
            metrics = overview.get("metrics", {})
            report.append("\n### 테스트 성능")
            for metric, value in metrics.items():
                if metric != "confusion_matrix":
                    report.append(f"- {metric}: {value:.4f}")
            report.append("")
        
        # 오류 분석
        if "error_analysis" in self._analysis_cache:
            ea = self._analysis_cache["error_analysis"]
            if "error" not in ea:
                report.append("## 2. 오류 분석")
                report.append(f"- 전체 오류율: {ea.get('overall_error_rate', 0):.2%}")
                report.append(f"- 식별된 코호트 수: {len(ea.get('cohorts', []))}")
                
                if ea.get("summary", {}).get("recommendations"):
                    report.append("\n### 권장 사항")
                    for rec in ea["summary"]["recommendations"]:
                        report.append(f"- {rec}")
                report.append("")
        
        # 공정성 평가
        if "fairness_assessment" in self._analysis_cache:
            fa = self._analysis_cache["fairness_assessment"]
            if "error" not in fa and "message" not in fa:
                report.append("## 3. 공정성 평가")
                report.append(f"- 전체 공정성 점수: {fa.get('overall_fairness_score', 0):.2f}")
                report.append(f"- 공정성 충족 여부: {'✓' if fa.get('is_fair') else '✗'}")
                report.append("")
        
        # 데이터 균형
        if "data_balance" in self._analysis_cache:
            db = self._analysis_cache["data_balance"]
            if "error" not in db:
                report.append("## 4. 데이터 균형 분석")
                summary = db.get("summary", {})
                report.append(f"- 데이터 품질 점수: {summary.get('data_quality_score', 0):.2f}")
                report.append(f"- 레이블 상태: {summary.get('label_status', 'unknown')}")
                report.append(f"- 공정성 상태: {summary.get('fairness_status', 'unknown')}")
                
                if summary.get("priority_actions"):
                    report.append("\n### 우선 조치 사항")
                    for action in summary["priority_actions"]:
                        report.append(f"- {action}")
                report.append("")
        
        return "\n".join(report)


def create_rai_dashboard(
    model: Any,
    X_train: pd.DataFrame,
    y_train: np.ndarray,
    X_test: pd.DataFrame,
    y_test: np.ndarray,
    **kwargs
) -> ResponsibleAIDashboard:
    """ResponsibleAIDashboard 인스턴스 생성 헬퍼 함수"""
    return ResponsibleAIDashboard(
        model=model,
        X_train=X_train,
        y_train=y_train,
        X_test=X_test,
        y_test=y_test,
        **kwargs
    )

