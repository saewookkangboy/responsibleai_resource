"""
Responsible AI 자동화 시스템 사용 예제
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification

from main import ResponsibleAIAutomationSystem


def main():
    """사용 예제"""
    
    # 1. 데이터 생성 (실제 사용 시 실제 데이터로 교체)
    print("데이터 생성 중...")
    X, y = make_classification(
        n_samples=1000,
        n_features=20,
        n_informative=10,
        n_redundant=10,
        n_classes=2,
        random_state=42,
    )
    
    # 민감한 속성 시뮬레이션
    sensitive_features = pd.DataFrame({
        "gender": np.random.choice(["M", "F"], len(X)),
        "race": np.random.choice(["A", "B", "C"], len(X)),
        "age": np.random.choice(["18-30", "31-50", "51+"], len(X)),
    })
    
    # 학습/테스트 분할
    X_train, X_test, y_train, y_test, sens_train, sens_test = train_test_split(
        X, y, sensitive_features, test_size=0.2, random_state=42
    )
    
    # 2. 모델 학습
    print("모델 학습 중...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    
    # 3. 시스템 초기화
    print("Responsible AI 자동화 시스템 초기화 중...")
    system = ResponsibleAIAutomationSystem("config.yaml")
    system.initialize_model(model, X_test, y_test, sens_test)
    
    # 4. 초기 평가
    print("\n=== 초기 평가 ===")
    y_pred = model.predict(X_test)
    initial_metrics = system.evaluate(X_test, y_test, y_pred, sens_test)
    
    print(f"전체 Responsible AI 점수: {initial_metrics.get('overall_responsible_ai_score', 0.0):.3f}")
    print(f"  - 공정성: {initial_metrics.get('fairness', {}).get('overall_fairness_score', 0.0):.3f}")
    print(f"  - 투명성: {initial_metrics.get('transparency', {}).get('overall_transparency_score', 0.0):.3f}")
    print(f"  - 책임성: {initial_metrics.get('accountability', {}).get('overall_accountability_score', 0.0):.3f}")
    print(f"  - 프라이버시: {initial_metrics.get('privacy', {}).get('overall_privacy_score', 0.0):.3f}")
    print(f"  - 견고성: {initial_metrics.get('robustness', {}).get('overall_robustness_score', 0.0):.3f}")
    
    # 5. 강화 학습 (선택사항)
    print("\n=== 강화 학습 시작 ===")
    print("강화 학습을 통해 Responsible AI 지표를 최적화합니다...")
    system.agent.train(total_timesteps=10000)  # 실제 사용 시 더 많은 스텝 권장
    
    # 6. 학습 후 평가
    print("\n=== 학습 후 평가 ===")
    y_pred_after = model.predict(X_test)
    after_metrics = system.evaluate(X_test, y_test, y_pred_after, sens_test)
    
    print(f"전체 Responsible AI 점수: {after_metrics.get('overall_responsible_ai_score', 0.0):.3f}")
    print(f"  - 공정성: {after_metrics.get('fairness', {}).get('overall_fairness_score', 0.0):.3f}")
    print(f"  - 투명성: {after_metrics.get('transparency', {}).get('overall_transparency_score', 0.0):.3f}")
    print(f"  - 책임성: {after_metrics.get('accountability', {}).get('overall_accountability_score', 0.0):.3f}")
    print(f"  - 프라이버시: {after_metrics.get('privacy', {}).get('overall_privacy_score', 0.0):.3f}")
    print(f"  - 견고성: {after_metrics.get('robustness', {}).get('overall_robustness_score', 0.0):.3f}")
    
    # 7. 업데이트 조건 검사
    print("\n=== 업데이트 조건 검사 ===")
    should_update = system.check_update_conditions()
    print(f"업데이트 필요: {should_update}")
    
    if should_update:
        print("자동 업데이트를 수행합니다...")
        update_result = system.perform_update(X_test, y_test, sens_test)
        print(f"업데이트 결과: {update_result.get('status', 'unknown')}")
    
    # 8. 모니터링 리포트 생성
    print("\n=== 모니터링 리포트 생성 ===")
    report = system.dashboard.generate_report(output_path="./monitoring_report.json")
    print(f"리포트 생성 완료: ./monitoring_report.json")
    
    # 9. 지표 추이 시각화
    print("\n=== 지표 추이 시각화 ===")
    system.dashboard.plot_metrics_trend(output_path="./metrics_trend.png")
    print("시각화 완료: ./metrics_trend.png")
    
    print("\n=== 완료 ===")
    print("Responsible AI 자동화 시스템 사용 예제가 완료되었습니다.")


if __name__ == "__main__":
    main()

