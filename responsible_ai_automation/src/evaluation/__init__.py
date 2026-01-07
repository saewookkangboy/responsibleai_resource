"""
Responsible AI 평가 모듈

Microsoft Responsible AI Toolbox 스타일의 종합적인 AI 평가 기능을 제공합니다.

주요 컴포넌트:
- Error Analysis: 모델 오류 분석 및 코호트 식별
- Counterfactual Analysis: 반사실적 설명 생성 (DiCE 기반)
- Causal Analysis: 인과 관계 분석 (EconML 기반)
- Data Balance: 데이터 균형 및 공정성 분석
- Fairness: 공정성 메트릭 평가
- Transparency: 모델 해석 가능성 평가
- Robustness: 모델 견고성 평가

Reference: https://github.com/microsoft/responsible-ai-toolbox
"""

from .comprehensive import ComprehensiveEvaluator
from .fairness import FairnessEvaluator
from .transparency import TransparencyEvaluator
from .accountability import AccountabilityEvaluator
from .privacy import PrivacyEvaluator
from .robustness import RobustnessEvaluator
from .social_impact import SocialImpactEvaluator

# Microsoft RAI Toolbox 스타일 컴포넌트
from .error_analysis import ErrorAnalyzer, create_error_analyzer
from .counterfactual import CounterfactualAnalyzer, create_counterfactual_analyzer
from .causal_analysis import CausalAnalyzer, create_causal_analyzer
from .data_balance import DataBalanceAnalyzer, create_data_balance_analyzer

__all__ = [
    # 기존 평가자
    "ComprehensiveEvaluator",
    "FairnessEvaluator",
    "TransparencyEvaluator",
    "AccountabilityEvaluator",
    "PrivacyEvaluator",
    "RobustnessEvaluator",
    "SocialImpactEvaluator",
    # Microsoft RAI Toolbox 스타일 컴포넌트
    "ErrorAnalyzer",
    "create_error_analyzer",
    "CounterfactualAnalyzer",
    "create_counterfactual_analyzer",
    "CausalAnalyzer",
    "create_causal_analyzer",
    "DataBalanceAnalyzer",
    "create_data_balance_analyzer",
]

