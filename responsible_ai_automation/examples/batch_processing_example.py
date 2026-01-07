"""
배치 처리 및 병렬 처리 예제
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from main import ResponsibleAIAutomationSystem
from src.evaluation.parallel_evaluator import ParallelEvaluator
from src.evaluation.comprehensive import ComprehensiveEvaluator
from src.utils.batch_processor import BatchProcessor
import yaml


def batch_processing_example():
    """배치 처리 예제"""
    print("=== 배치 처리 예제 ===")

    # 대규모 데이터 생성
    X = np.random.rand(10000, 20)
    y = np.random.randint(0, 2, 10000)
    sensitive_features = pd.DataFrame({
        "gender": np.random.choice(["M", "F"], 10000),
        "race": np.random.choice(["A", "B", "C"], 10000),
    })

    # 모델 학습
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    # 시스템 초기화
    with open("config.yaml", "r") as f:
        config = yaml.safe_load(f)

    evaluator = ComprehensiveEvaluator(config)
    parallel_evaluator = ParallelEvaluator(evaluator, batch_size=1000)

    # 병렬 평가 수행
    y_pred = model.predict(X)
    metrics = parallel_evaluator.evaluate_parallel(
        model, X, y, y_pred, sensitive_features
    )

    print(f"종합 점수: {metrics['overall_responsible_ai_score']:.3f}")
    print(f"배치 정보: {metrics.get('batch_info', {})}")


def batch_processor_example():
    """배치 프로세서 직접 사용 예제"""
    print("\n=== 배치 프로세서 예제 ===")

    # 대규모 데이터
    data = np.random.rand(5000, 10)

    # 처리 함수 정의
    def process_batch(batch):
        return np.mean(batch, axis=0)

    # 배치 프로세서 생성
    processor = BatchProcessor(batch_size=1000)

    # 배치 처리
    results = processor.process_in_batches(data, process_batch)

    print(f"원본 데이터 크기: {data.shape}")
    print(f"배치 수: {len(results)}")
    print(f"각 배치 결과 크기: {[r.shape for r in results]}")


if __name__ == "__main__":
    batch_processing_example()
    batch_processor_example()

