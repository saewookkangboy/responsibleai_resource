"""
빠른 시작 스크립트 - 최소 설정으로 즉시 사용 가능
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.datasets import make_classification
from pathlib import Path
import sys

# 프로젝트 경로 추가
sys.path.insert(0, str(Path(__file__).parent))

from main import ResponsibleAIAutomationSystem


def quick_start():
    """빠른 시작 예제"""
    print("=" * 60)
    print("Responsible AI Automation 빠른 시작")
    print("=" * 60)
    
    # 1. 시스템 초기화 (최소 설정)
    print("\n[1단계] 시스템 초기화...")
    config_path = Path(__file__).parent / "config.yaml"
    
    if not config_path.exists():
        print("⚠ 설정 파일이 없습니다. 기본 설정을 생성합니다...")
        create_default_config(config_path)
    
    system = ResponsibleAIAutomationSystem(str(config_path))
    print("✓ 시스템 초기화 완료")
    
    # 2. 샘플 데이터 생성
    print("\n[2단계] 샘플 데이터 생성...")
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
    
    X_train, X_test, y_train, y_test, sensitive_train, sensitive_test = train_test_split(
        X, y, sensitive_features, test_size=0.2, random_state=42
    )
    print(f"✓ 데이터 생성 완료 (훈련: {len(X_train)}, 테스트: {len(X_test)})")
    
    # 3. 모델 학습
    print("\n[3단계] 모델 학습...")
    model = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    model.fit(X_train, y_train)
    print("✓ 모델 학습 완료")
    
    # 4. 모델 초기화
    print("\n[4단계] Responsible AI 시스템에 모델 등록...")
    system.initialize_model(model, X_test, y_test, sensitive_test)
    print("✓ 모델 등록 완료")
    
    # 5. 평가 수행
    print("\n[5단계] Responsible AI 평가 수행...")
    y_pred = model.predict(X_test)
    metrics = system.evaluate(X_test, y_test, y_pred, sensitive_test)
    
    # 6. 결과 출력
    print("\n" + "=" * 60)
    print("평가 결과")
    print("=" * 60)
    
    overall_score = metrics.get("overall_responsible_ai_score", 0.0)
    is_responsible = metrics.get("is_responsible", False)
    
    print(f"\n📊 전체 Responsible AI 점수: {overall_score:.3f}")
    print(f"✅ Responsible AI 기준 충족: {'예' if is_responsible else '아니오'}")
    
    print("\n카테고리별 점수:")
    categories = {
        "fairness": "공정성",
        "transparency": "투명성",
        "accountability": "책임성",
        "privacy": "프라이버시",
        "robustness": "견고성"
    }
    
    for key, name in categories.items():
        if key in metrics:
            score_key = f"overall_{key}_score"
            score = metrics[key].get(score_key, 0.0)
            print(f"  - {name}: {score:.3f}")
    
    print("\n" + "=" * 60)
    print("빠른 시작 완료! 🎉")
    print("=" * 60)
    print("\n다음 단계:")
    print("1. config.yaml 파일을 수정하여 설정을 커스터마이징하세요")
    print("2. 실제 데이터로 모델을 평가하세요")
    print("3. 웹 대시보드 실행: streamlit run src/monitoring/dashboard_web.py")
    print("4. API 서버 실행: python -m src.api.server")


def create_default_config(config_path: Path):
    """기본 설정 파일 생성"""
    default_config = """# Responsible AI Automation 기본 설정

# 평가 설정
evaluation:
  fairness:
    metrics: ["demographic_parity", "equalized_odds"]
    threshold: 0.1
    sensitive_attributes: ["gender", "race"]
  
  transparency:
    metrics: ["explainability_score"]
    threshold: 0.7
  
  accountability:
    enabled: true
  
  privacy:
    metrics: ["data_anonymization", "access_control"]
    threshold: 0.8
  
  robustness:
    metrics: ["adversarial_robustness"]
    threshold: 0.75

# 강화 학습 설정 (빠른 시작을 위해 간소화)
reinforcement_learning:
  algorithm: "PPO"
  learning_rate: 3e-4
  batch_size: 64
  training_steps: 10000  # 빠른 시작을 위해 감소

# 자동 업데이트 설정
auto_update:
  enabled: false  # 빠른 시작을 위해 비활성화
  check_interval: 3600

# 모니터링 설정
monitoring:
  enabled: true
  dashboard_port: 8080
  log_level: "INFO"
  metrics_retention_days: 7  # 빠른 시작을 위해 감소
  alert_channels:
    - "console"

# 모델 설정
model:
  save_path: "./models"
  checkpoint_frequency: 1000
  max_checkpoints: 5  # 빠른 시작을 위해 감소
"""
    
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, "w", encoding="utf-8") as f:
        f.write(default_config)
    
    print(f"✓ 기본 설정 파일 생성: {config_path}")


if __name__ == "__main__":
    try:
        quick_start()
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        print("\n도움말:")
        print("1. requirements.txt의 패키지가 모두 설치되었는지 확인하세요")
        print("2. Python 버전이 3.8 이상인지 확인하세요")
        print("3. config.yaml 파일이 올바른지 확인하세요")

