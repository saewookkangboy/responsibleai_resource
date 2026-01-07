# 통합 사용 가이드

4개의 Responsible AI 프로젝트를 함께 사용하는 워크플로우와 연동 예제를 제공합니다.

## 📋 목차

1. [개요](#개요)
2. [통합 워크플로우](#통합-워크플로우)
3. [프로젝트 간 연동 예제](#프로젝트-간-연동-예제)
4. [실전 시나리오](#실전-시나리오)

## 개요

Responsible AI Resource Collection은 4개의 독립적인 프로젝트로 구성되어 있으며, 함께 사용하면 더욱 강력한 Responsible AI 구현이 가능합니다:

1. **Responsible AI Guidelines** - 프로젝트 시작 전 가이드라인 및 체크리스트
2. **Responsible AI Policy** - 정책 수립 및 템플릿 적용
3. **AI Platform Validator** - API 검증 및 보안 확인
4. **Responsible AI Automation** - 자동 평가 및 최적화

## 통합 워크플로우

### 단계별 워크플로우

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 프로젝트 시작 전                                          │
│    → Responsible AI Guidelines 체크리스트 확인              │
│    → Responsible AI Policy 템플릿 검토                      │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 2. 개발 단계                                                  │
│    → 역할별 가이드라인 준수                                  │
│    → AI Platform Validator로 API 검증                       │
│    → Responsible AI Automation으로 지속적 평가              │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 3. 배포 전                                                    │
│    → Responsible AI Guidelines 배포 전 체크리스트           │
│    → AI Platform Validator 최종 검증                        │
│    → Responsible AI Automation 종합 평가                     │
└─────────────────────────────────────────────────────────────┘
                        ↓
┌─────────────────────────────────────────────────────────────┐
│ 4. 배포 후                                                    │
│    → Responsible AI Automation 모니터링                     │
│    → Responsible AI Guidelines 배포 후 체크리스트           │
│    → 지속적 개선                                             │
└─────────────────────────────────────────────────────────────┘
```

## 프로젝트 간 연동 예제

### 예제 1: 전체 워크플로우 통합

```python
"""
4개 프로젝트를 통합하여 사용하는 예제
"""

import os
import sys
from pathlib import Path

# 프로젝트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "responsible_ai_automation"))
sys.path.insert(0, str(project_root / "ai-platform-validator"))

from main import ResponsibleAIAutomationSystem
from src.validator import AIPlatformValidator
import yaml


def integrated_workflow():
    """통합 워크플로우 실행"""
    
    print("=" * 60)
    print("Responsible AI 통합 워크플로우")
    print("=" * 60)
    
    # 1. Guidelines 체크리스트 확인 (수동)
    print("\n[1단계] Guidelines 체크리스트 확인")
    print("→ responsible-ai-guidelines/checklists/pre-project.md 확인")
    print("✓ 체크리스트 확인 완료")
    
    # 2. Policy 템플릿 적용 (수동)
    print("\n[2단계] Policy 템플릿 적용")
    print("→ responsible-ai-policy/policies/ 참고")
    print("✓ 정책 템플릿 적용 완료")
    
    # 3. AI Platform Validator로 API 검증
    print("\n[3단계] AI Platform Validator로 API 검증")
    validator = AIPlatformValidator()
    
    # OpenAI API 검증 예제
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        validation_result = validator.validate_openai_api(api_key)
        print(f"✓ API 검증 완료: {validation_result}")
    else:
        print("⚠ API 키가 설정되지 않았습니다.")
    
    # 4. Responsible AI Automation으로 평가
    print("\n[4단계] Responsible AI Automation으로 평가")
    system = ResponsibleAIAutomationSystem("responsible_ai_automation/config.yaml")
    
    # 모델 초기화 및 평가 (예제)
    # system.initialize_model(model, X, y, sensitive_features)
    # metrics = system.evaluate(X, y, y_pred, sensitive_features)
    
    print("✓ Responsible AI 평가 완료")
    
    # 5. 모니터링 시작
    print("\n[5단계] 지속적 모니터링")
    print("→ Responsible AI Automation 모니터링 활성화")
    # system.run_continuous_monitoring()
    
    print("\n" + "=" * 60)
    print("통합 워크플로우 완료!")
    print("=" * 60)


if __name__ == "__main__":
    integrated_workflow()
```

### 예제 2: Guidelines와 Automation 연동

```python
"""
Guidelines 체크리스트를 자동으로 검증하는 예제
"""

import json
from pathlib import Path
from responsible_ai_automation.main import ResponsibleAIAutomationSystem


def validate_guidelines_checklist():
    """Guidelines 체크리스트 자동 검증"""
    
    checklist_path = Path("responsible-ai-guidelines/checklists/pre-project.md")
    
    # 체크리스트 항목 읽기
    with open(checklist_path, "r", encoding="utf-8") as f:
        checklist_content = f.read()
    
    # 체크리스트 항목 추출 (간단한 예제)
    checklist_items = []
    for line in checklist_content.split("\n"):
        if line.strip().startswith("- [ ]") or line.strip().startswith("- [x]"):
            checklist_items.append(line.strip())
    
    # Responsible AI Automation으로 검증
    system = ResponsibleAIAutomationSystem("responsible_ai_automation/config.yaml")
    
    # 체크리스트 항목을 Responsible AI 평가에 반영
    validation_results = {}
    for item in checklist_items:
        # 실제 구현에서는 체크리스트 항목을 Responsible AI 지표로 매핑
        validation_results[item] = "checked"
    
    return validation_results
```

### 예제 3: Policy와 Validator 연동

```python
"""
Policy를 기반으로 Validator 설정을 자동으로 구성하는 예제
"""

import yaml
from pathlib import Path
from ai_platform_validator.src.validator import AIPlatformValidator


def apply_policy_to_validator(policy_name: str):
    """Policy를 Validator 설정에 적용"""
    
    # Policy 파일 읽기
    policy_path = Path(f"responsible-ai-policy/policies/{policy_name}.md")
    
    # Policy 내용 파싱 (간단한 예제)
    with open(policy_path, "r", encoding="utf-8") as f:
        policy_content = f.read()
    
    # Validator 설정 생성
    validator_config = {
        "security": {
            "api_key_encryption": True,
            "access_control": True,
        },
        "ethics": {
            "bias_detection": True,
            "fairness_check": True,
        },
    }
    
    # Validator 초기화
    validator = AIPlatformValidator()
    validator.configure(validator_config)
    
    return validator
```

## 실전 시나리오

### 시나리오 1: 새로운 AI 서비스 개발

1. **프로젝트 시작**
   ```bash
   # Guidelines 체크리스트 확인
   cat responsible-ai-guidelines/checklists/pre-project.md
   
   # Policy 템플릿 선택
   cat responsible-ai-policy/policies/api-service-policy.md
   ```

2. **개발 중**
   ```python
   # AI Platform Validator로 API 검증
   from ai_platform_validator.src.validator import AIPlatformValidator
   validator = AIPlatformValidator()
   validator.validate_api_endpoint("https://api.example.com")
   
   # Responsible AI Automation으로 모델 평가
   from responsible_ai_automation.main import ResponsibleAIAutomationSystem
   system = ResponsibleAIAutomationSystem("config.yaml")
   metrics = system.evaluate(X, y, y_pred, sensitive_features)
   ```

3. **배포 전**
   ```bash
   # 배포 전 체크리스트 확인
   cat responsible-ai-guidelines/checklists/pre-deployment.md
   
   # 최종 검증
   python -m ai_platform_validator.src.validator --full-check
   ```

4. **배포 후**
   ```python
   # 지속적 모니터링
   system.run_continuous_monitoring()
   ```

### 시나리오 2: 기존 시스템에 Responsible AI 적용

1. **현재 상태 평가**
   ```python
   # Responsible AI Automation으로 현재 모델 평가
   system = ResponsibleAIAutomationSystem("config.yaml")
   current_metrics = system.evaluate(X, y, y_pred, sensitive_features)
   
   # 개선 영역 식별
   improvement_areas = identify_improvement_areas(current_metrics)
   ```

2. **Guidelines 기반 개선**
   ```bash
   # 역할별 가이드라인 확인
   cat responsible-ai-guidelines/guidelines/developer.md
   ```

3. **Policy 적용**
   ```bash
   # 적절한 정책 템플릿 선택 및 적용
   cat responsible-ai-policy/policies/web-service-policy.md
   ```

4. **검증 및 모니터링**
   ```python
   # AI Platform Validator로 검증
   validator.validate_all()
   
   # Responsible AI Automation으로 모니터링
   system.run_continuous_monitoring()
   ```

## 추가 리소스

- [Responsible AI Guidelines 사용 가이드](responsible-ai-guidelines/USAGE.md)
- [Responsible AI Policy 프로젝트 구조](responsible-ai-policy/PROJECT_STRUCTURE.md)
- [AI Platform Validator 아키텍처](ai-platform-validator/architecture.md)
- [Responsible AI Automation API 레퍼런스](responsible_ai_automation/docs/api_reference.md)

---

**Last Updated**: 2026-01-07

