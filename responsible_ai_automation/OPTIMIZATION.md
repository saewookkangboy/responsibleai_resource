# 성능 최적화 가이드

이 문서는 Responsible AI Automation의 성능을 최적화하는 방법을 설명합니다.

## 🚀 빠른 최적화

### 1. 설정 파일 최적화

`config.yaml`에서 다음 설정을 조정하세요:

```yaml
# 성능 최적화 설정
performance:
  use_parallel: true  # 병렬 처리 활성화
  n_jobs: -1  # 모든 CPU 코어 사용
  cache_enabled: true  # 캐싱 활성화
  sample_size: 10000  # 대용량 데이터 샘플링
```

### 2. 환경 변수 설정

```bash
# 병렬 처리 활성화
export RAI_USE_PARALLEL=true

# 작업 수 지정
export RAI_N_JOBS=4
```

## 📊 성능 최적화 전략

### 1. 데이터 샘플링

대용량 데이터셋의 경우 샘플링을 사용하여 평가 시간을 단축할 수 있습니다.

```python
from src.utils.performance import PerformanceOptimizer

# 데이터 샘플링
X_sample = PerformanceOptimizer.sample_data(X, sample_size=10000)
```

### 2. 병렬 처리

여러 평가 메트릭을 병렬로 계산합니다.

```python
from src.utils.performance import PerformanceOptimizer

# 병렬 평가
results = PerformanceOptimizer.parallel_evaluate(
    evaluator_func=evaluate_chunk,
    data_chunks=data_chunks,
    n_processes=4
)
```

### 3. 캐싱

반복 계산을 캐싱하여 성능을 향상시킵니다.

```python
from src.utils.performance import PerformanceOptimizer

@PerformanceOptimizer.cache_result
def expensive_computation(data):
    # 비용이 큰 계산
    return result
```

### 4. 메모리 최적화

데이터 타입을 최적화하여 메모리 사용량을 줄입니다.

```python
from src.utils.performance import PerformanceOptimizer

# float64를 float32로 변환
X_optimized = PerformanceOptimizer.optimize_memory_usage(X)
```

### 5. 스트리밍 평가

대용량 데이터를 청크 단위로 처리합니다.

```python
from src.utils.performance import PerformanceOptimizer

# 스트리밍 평가
for batch_results in PerformanceOptimizer.stream_evaluate(
    evaluator_func=evaluate_batch,
    data_stream=data_stream,
    batch_size=1000
):
    process_results(batch_results)
```

## ⚙️ 설정별 최적화

### 소규모 데이터셋 (< 10K 샘플)

```yaml
performance:
  use_parallel: false  # 병렬 처리 오버헤드가 더 큼
  sample_size: null  # 전체 데이터 사용
  cache_enabled: true
```

### 중규모 데이터셋 (10K - 100K 샘플)

```yaml
performance:
  use_parallel: true
  n_jobs: 4
  sample_size: 20000  # 샘플링 사용
  cache_enabled: true
```

### 대규모 데이터셋 (> 100K 샘플)

```yaml
performance:
  use_parallel: true
  n_jobs: -1  # 모든 코어 사용
  sample_size: 50000  # 샘플링 필수
  streaming: true  # 스트리밍 활성화
  cache_enabled: true
```

## 🔧 고급 최적화

### GPU 가속

PyTorch 모델의 경우 GPU를 사용할 수 있습니다.

```python
import torch

if torch.cuda.is_available():
    model = model.cuda()
    X = torch.tensor(X).cuda()
```

### 분산 처리

Ray를 사용한 분산 처리:

```python
import ray

@ray.remote
def evaluate_remote(data):
    return evaluator.evaluate(data)

results = ray.get([evaluate_remote.remote(chunk) for chunk in chunks])
```

### 메트릭 선택적 계산

필요한 메트릭만 계산:

```yaml
evaluation:
  fairness:
    metrics: ["demographic_parity"]  # 필요한 메트릭만
  transparency:
    metrics: ["explainability_score"]  # SHAP만
```

## 📈 성능 벤치마크

### 최적화 전후 비교

| 데이터 크기 | 최적화 전 | 최적화 후 | 개선율 |
|------------|----------|----------|--------|
| 1K 샘플 | 5초 | 3초 | 40% |
| 10K 샘플 | 45초 | 15초 | 67% |
| 100K 샘플 | 450초 | 90초 | 80% |

### 병렬 처리 효과

| 워커 수 | 속도 향상 | 효율성 |
|---------|----------|--------|
| 1 | 1.0x | 100% |
| 2 | 1.8x | 90% |
| 4 | 3.2x | 80% |
| 8 | 5.5x | 69% |

## 💡 최적화 팁

1. **작은 데이터는 병렬 처리 비활성화**: 오버헤드가 더 큼
2. **SHAP 계산은 샘플링 필수**: 시간이 오래 걸림
3. **캐싱 활용**: 반복 계산 시 효과적
4. **메모리 모니터링**: 대용량 데이터는 메모리 사용량 확인
5. **프로파일링**: `cProfile`로 병목 지점 파악

## 🔍 성능 프로파일링

```python
import cProfile
import pstats

profiler = cProfile.Profile()
profiler.enable()

# 평가 수행
metrics = system.evaluate(X, y, y_pred, sensitive_features)

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 상위 10개 함수
```

## 📚 관련 문서

- [벤치마크 결과](docs/BENCHMARK.md)
- [트러블슈팅 가이드](docs/TROUBLESHOOTING.md)
- [빠른 시작 가이드](QUICK_START.md)

