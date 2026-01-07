"""
규제 준수 모듈
"""

from .eu_ai_act import EUAIActValidator, EUAIActComplianceResult
from .gdpr import GDPRCompliance

__all__ = [
    "EUAIActValidator",
    "EUAIActComplianceResult",
    "GDPRCompliance",
]
