"""
Responsible AI Automation 기본 사용 예제

이 예제는 Responsible AI Automation 시스템을 사용하여
모델을 평가하고 모니터링하는 기본적인 방법을 보여줍니다.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

# 시스템 import
import sys
from pathlib import Path

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import ResponsibleAIAutomationSystem


def main():
    """기본 사용 예제"""
    
    print("=" * 60)
    print("Responsible AI Automation 기본 사용 예제")
    print("=" * 60)
    
    # 1. 시스템 초기화
    print("\n[1단계] 시스템 초기화")
    system = ResponsibleAIAutomationSystem("config.yaml")
    print("✓ 시스템이 초기화되었습니다.")
    
    # 2. 샘플 데이터 생성
    print("\n[2단계] 샘플 데이터 생성")
    X, y = make_classification(
        n_samples=1000,
        n_features=10,
        n_informative=5,
        n_redundant=2,
        n_classes=2,
        random_state=42
    )
    
    # 민감한 속성 생성 (시뮬레이션)
    sensitive_features = pd.DataFrame({
        "gender": np.random.choice(["M", "F"], 1000),
        "race": np.random.choice(["A", "B", "C"], 1000),
        "age": np.random.randint(18, 80, 1000),
    })
    
    # 데이터 분할
    X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = train_test_split(
        X, y, sensitive_features, test_size=0.2, random_state=42
    )
    
    print(f"✓ 훈련 데이터: {X_train.shape[0]}개 샘플")
    print(f"✓ 테스트 데이터: {X_test.shape[0]}개 샘플")
    
    # 3. 모델 학습
    print("\n[3단계] 모델 학습")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    print("✓ 모델 학습이 완료되었습니다.")
    
    # 4. 시스템에 모델 등록
    print("\n[4단계] 시스템에 모델 등록")
    system.initialize_model(
        model=model,
        X=X_test,
        y=y_test,
        sensitive_features=sensitive_test,
    )
    print("✓ 모델이 시스템에 등록되었습니다.")
    
    # 5. 모델 평가
    print("\n[5단계] Responsible AI 평가 수행")
    y_pred = model.predict(X_test)
    metrics = system.evaluate(
        X=X_test,
        y=y_test,
        y_pred=y_pred,
        sensitive_features=sensitive_test,
    )
    
    # 6. 평가 결과 출력
    print("\n" + "=" * 60)
    print("평가 결과")
    print("=" * 60)
    
    overall_score = metrics.get("overall_responsible_ai_score", 0.0)
    print(f"\n전체 Responsible AI 점수: {overall_score:.3f}")
    print(f"Responsible AI 기준 충족: {'✓' if metrics.get('is_responsible', False) else '✗'}")
    
    # 각 카테고리별 점수
    print("\n카테고리별 점수:")
    print(f"  - 공정성 (Fairness): {metrics.get('fairness', {}).get('overall_fairness_score', 0.0):.3f}")
    print(f"  - 투명성 (Transparency): {metrics.get('transparency', {}).get('explainability_score', 0.0):.3f}")
    print(f"  - 책임성 (Accountability): {metrics.get('accountability', {}).get('overall_accountability_score', 0.0):.3f}")
    print(f"  - 프라이버시 (Privacy): {metrics.get('privacy', {}).get('overall_privacy_score', 0.0):.3f}")
    print(f"  - 견고성 (Robustness): {metrics.get('robustness', {}).get('overall_robustness_score', 0.0):.3f}")
    
    # 7. 업데이트 조건 확인
    print("\n[6단계] 업데이트 조건 확인")
    should_update = system.check_update_conditions()
    print(f"업데이트 필요 여부: {'✓ 예' if should_update else '✗ 아니오'}")
    
    print("\n" + "=" * 60)
    print("예제 실행 완료!")
    print("=" * 60)


if __name__ == "__main__":
    main()

