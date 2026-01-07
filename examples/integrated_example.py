"""
통합 예제: 4개 프로젝트를 함께 사용하는 완전한 end-to-end 예제
"""

import os
import sys
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

# 프로젝트 경로 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "responsible_ai_automation"))
sys.path.insert(0, str(project_root / "ai-platform-validator"))

try:
    from main import ResponsibleAIAutomationSystem
    from src.validator import AIPlatformValidator
except ImportError:
    print("⚠ 일부 모듈을 import할 수 없습니다. 경로를 확인하세요.")
    ResponsibleAIAutomationSystem = None
    AIPlatformValidator = None


def step1_check_guidelines():
    """1단계: Guidelines 체크리스트 확인"""
    print("\n" + "=" * 60)
    print("[1단계] Responsible AI Guidelines 체크리스트 확인")
    print("=" * 60)
    
    checklist_path = project_root / "responsible-ai-guidelines" / "checklists" / "pre-project.md"
    
    if checklist_path.exists():
        print(f"✓ 체크리스트 파일 확인: {checklist_path}")
        print("  → 프로젝트 시작 전 체크리스트를 검토하세요.")
    else:
        print(f"⚠ 체크리스트 파일을 찾을 수 없습니다: {checklist_path}")
    
    return True


def step2_apply_policy():
    """2단계: Policy 템플릿 적용"""
    print("\n" + "=" * 60)
    print("[2단계] Responsible AI Policy 템플릿 적용")
    print("=" * 60)
    
    policy_path = project_root / "responsible-ai-policy" / "policies" / "api-service-policy.md"
    
    if policy_path.exists():
        print(f"✓ 정책 템플릿 확인: {policy_path}")
        print("  → API 서비스 정책 템플릿을 참고하여 정책을 수립하세요.")
    else:
        print(f"⚠ 정책 템플릿 파일을 찾을 수 없습니다: {policy_path}")
    
    return True


def step3_validate_api():
    """3단계: AI Platform Validator로 API 검증"""
    print("\n" + "=" * 60)
    print("[3단계] AI Platform Validator로 API 검증")
    print("=" * 60)
    
    if AIPlatformValidator is None:
        print("⚠ AI Platform Validator를 사용할 수 없습니다.")
        return False
    
    try:
        validator = AIPlatformValidator()
        print("✓ AI Platform Validator 초기화 완료")
        
        # API 키 검증 (예제)
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            print("  → API 키가 설정되어 있습니다.")
            # 실제 검증 수행
            # validation_result = validator.validate(api_key)
        else:
            print("  ⚠ API 키가 설정되지 않았습니다. 환경 변수를 설정하세요.")
        
        return True
    except Exception as e:
        print(f"⚠ API 검증 중 오류 발생: {e}")
        return False


def step4_evaluate_with_automation():
    """4단계: Responsible AI Automation으로 평가"""
    print("\n" + "=" * 60)
    print("[4단계] Responsible AI Automation으로 평가")
    print("=" * 60)
    
    if ResponsibleAIAutomationSystem is None:
        print("⚠ Responsible AI Automation을 사용할 수 없습니다.")
        return False
    
    try:
        # 설정 파일 경로
        config_path = project_root / "responsible_ai_automation" / "config.yaml"
        
        if not config_path.exists():
            print(f"⚠ 설정 파일을 찾을 수 없습니다: {config_path}")
            return False
        
        # 시스템 초기화
        system = ResponsibleAIAutomationSystem(str(config_path))
        print("✓ Responsible AI Automation 시스템 초기화 완료")
        
        # 샘플 데이터 생성
        print("\n  → 샘플 데이터 생성 중...")
        X, y = make_classification(
            n_samples=1000,
            n_features=10,
            n_informative=5,
            n_redundant=2,
            n_classes=2,
            random_state=42
        )
        
        sensitive_features = pd.DataFrame({
            "gender": np.random.choice(["M", "F"], 1000),
            "race": np.random.choice(["A", "B", "C"], 1000),
        })
        
        # 데이터 분할
        X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = train_test_split(
            X, y, sensitive_features, test_size=0.2, random_state=42
        )
        
        # 모델 학습
        print("  → 모델 학습 중...")
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        # 모델 초기화
        print("  → 모델 초기화 중...")
        system.initialize_model(model, X_test, y_test, sensitive_test)
        
        # 평가 수행
        print("  → Responsible AI 평가 수행 중...")
        y_pred = model.predict(X_test)
        metrics = system.evaluate(X_test, y_test, y_pred, sensitive_test)
        
        # 결과 출력
        print("\n  📊 평가 결과:")
        print(f"    - 전체 Responsible AI 점수: {metrics.get('overall_responsible_ai_score', 0.0):.3f}")
        print(f"    - Responsible AI 기준 충족: {'✓' if metrics.get('is_responsible', False) else '✗'}")
        
        if "fairness" in metrics:
            print(f"    - 공정성 점수: {metrics['fairness'].get('overall_fairness_score', 0.0):.3f}")
        if "transparency" in metrics:
            print(f"    - 투명성 점수: {metrics['transparency'].get('overall_transparency_score', 0.0):.3f}")
        
        return True
        
    except Exception as e:
        print(f"⚠ 평가 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False


def step5_monitoring():
    """5단계: 지속적 모니터링"""
    print("\n" + "=" * 60)
    print("[5단계] 지속적 모니터링 설정")
    print("=" * 60)
    
    print("  → Responsible AI Automation 모니터링을 활성화하세요.")
    print("  → python main.py --config config.yaml --mode monitor")
    print("  → 대시보드: http://localhost:8080")
    
    return True


def main():
    """메인 함수: 전체 워크플로우 실행"""
    print("=" * 60)
    print("Responsible AI 통합 워크플로우 예제")
    print("=" * 60)
    
    steps = [
        ("Guidelines 체크리스트 확인", step1_check_guidelines),
        ("Policy 템플릿 적용", step2_apply_policy),
        ("API 검증", step3_validate_api),
        ("Responsible AI 평가", step4_evaluate_with_automation),
        ("모니터링 설정", step5_monitoring),
    ]
    
    results = {}
    
    for step_name, step_func in steps:
        try:
            result = step_func()
            results[step_name] = result
        except Exception as e:
            print(f"\n⚠ {step_name} 단계에서 오류 발생: {e}")
            results[step_name] = False
    
    # 최종 결과 출력
    print("\n" + "=" * 60)
    print("워크플로우 실행 결과")
    print("=" * 60)
    
    for step_name, result in results.items():
        status = "✓ 완료" if result else "✗ 실패"
        print(f"  {step_name}: {status}")
    
    success_count = sum(1 for r in results.values() if r)
    total_count = len(results)
    
    print(f"\n  총 {total_count}개 단계 중 {success_count}개 완료")
    
    if success_count == total_count:
        print("\n  🎉 모든 단계가 성공적으로 완료되었습니다!")
    else:
        print("\n  ⚠ 일부 단계에서 문제가 발생했습니다. 로그를 확인하세요.")


if __name__ == "__main__":
    main()

