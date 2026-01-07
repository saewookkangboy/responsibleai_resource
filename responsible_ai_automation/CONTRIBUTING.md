# 기여 가이드라인

Responsible AI Automation 프로젝트에 기여해 주셔서 감사합니다! 이 문서는 프로젝트에 기여하는 방법을 안내합니다.

## 📋 목차

- [코드 of Conduct](#코드-of-conduct)
- [기여 방법](#기여-방법)
- [개발 환경 설정](#개발-환경-설정)
- [코딩 스타일](#코딩-스타일)
- [커밋 메시지](#커밋-메시지)
- [Pull Request 프로세스](#pull-request-프로세스)
- [이슈 리포트](#이슈-리포트)

## 코드 of Conduct

이 프로젝트는 [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md)를 따릅니다. 기여 시 이러한 가이드라인을 준수해 주세요.

## 기여 방법

기여는 다음과 같은 방법으로 할 수 있습니다:

1. **버그 리포트**: 버그를 발견하셨나요? [GitHub Issues](https://github.com/yourusername/responsible-ai-automation/issues)에 리포트해 주세요.
2. **기능 제안**: 새로운 기능 아이디어가 있으신가요? 이슈를 열어 논의해 보세요.
3. **코드 기여**: 버그 수정, 기능 추가, 문서 개선 등
4. **문서 개선**: 문서의 오타, 불명확한 부분 개선
5. **테스트 코드 작성**: 테스트 커버리지 향상

## 개발 환경 설정

### 1. 저장소 포크 및 클론

```bash
# GitHub에서 저장소 포크
# 그 다음 클론
git clone https://github.com/YOUR_USERNAME/responsible-ai-automation.git
cd responsible-ai-automation

# 원본 저장소를 upstream으로 추가
git remote add upstream https://github.com/original-owner/responsible-ai-automation.git
```

### 2. 가상 환경 설정

```bash
# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 개발 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt  # 개발 도구 포함
```

### 3. 개발 브랜치 생성

```bash
# 최신 코드 가져오기
git checkout main
git pull upstream main

# 새 브랜치 생성
git checkout -b feature/your-feature-name
# 또는
git checkout -b fix/your-bug-fix
```

## 코딩 스타일

### Python 코드 스타일

이 프로젝트는 다음 스타일 가이드를 따릅니다:

- **포매터**: [Black](https://github.com/psf/black)
- **린터**: [Flake8](https://flake8.pycqa.org/)
- **타입 힌트**: PEP 484 스타일 타입 힌트 사용 권장
- **문서 문자열**: Google 스타일 docstring

코드 제출 전에 다음을 실행하세요:

```bash
# Black으로 포매팅
black src/ tests/

# Flake8로 린팅
flake8 src/ tests/

# 타입 체크 (선택사항)
mypy src/
```

### 코드 예제

```python
def evaluate_model(
    model: Any,
    X: np.ndarray,
    y: np.ndarray,
    sensitive_features: Optional[pd.DataFrame] = None,
) -> Dict[str, Any]:
    """
    모델을 평가합니다.
    
    Args:
        model: 평가할 모델 객체
        X: 입력 데이터 배열
        y: 실제 레이블 배열
        sensitive_features: 민감한 속성 데이터프레임 (선택사항)
    
    Returns:
        평가 결과를 포함한 딕셔너리
    
    Raises:
        ValueError: 입력 데이터 형식이 올바르지 않은 경우
    """
    # 구현 내용
    pass
```

## 커밋 메시지

커밋 메시지는 명확하고 일관성 있게 작성해 주세요.

### 형식

```
<타입>: <간단한 설명>

<자세한 설명 (선택사항)>

<이슈 번호> (선택사항)
```

### 타입

- `feat`: 새로운 기능 추가
- `fix`: 버그 수정
- `docs`: 문서 수정
- `style`: 코드 포매팅, 세미콜론 누락 등
- `refactor`: 코드 리팩토링
- `test`: 테스트 코드 추가/수정
- `chore`: 빌드 업무 수정, 패키지 매니저 설정 등

### 예시

```
feat: fairness 평가에 demographic parity 메트릭 추가

- DemographicParityMetric 클래스 구현
- ComprehensiveEvaluator에 통합
- 테스트 코드 추가

#123
```

## Pull Request 프로세스

### 1. 브랜치 준비

```bash
# 최신 main 브랜치와 동기화
git fetch upstream
git rebase upstream/main

# 변경사항 푸시
git push origin your-branch-name
```

### 2. PR 제출

1. GitHub에서 Pull Request를 생성하세요
2. PR 제목은 커밋 메시지 형식을 따르세요
3. PR 설명에 다음을 포함하세요:
   - 변경사항 요약
   - 관련 이슈 번호
   - 테스트 방법
   - 스크린샷 (UI 변경이 있는 경우)

### 3. PR 체크리스트

제출하기 전에 확인하세요:

- [ ] 코드가 프로젝트 스타일 가이드를 따릅니다
- [ ] 모든 테스트가 통과합니다
- [ ] 새로운 기능에 대한 테스트를 추가했습니다
- [ ] 문서를 업데이트했습니다 (필요한 경우)
- [ ] CHANGELOG.md를 업데이트했습니다
- [ ] 이슈 번호를 연결했습니다

### 4. 리뷰 프로세스

- 리뷰어가 코드를 검토하고 피드백을 제공합니다
- 피드백을 반영하여 수정하고 다시 커밋하세요
- 리뷰어가 승인하면 메인테이너가 머지합니다

## 이슈 리포트

버그를 발견하셨거나 기능을 제안하고 싶으시다면 이슈를 열어 주세요.

### 버그 리포트

버그 리포트에는 다음 정보를 포함해 주세요:

1. **버그 설명**: 명확하고 간결한 설명
2. **재현 단계**: 버그를 재현하는 방법
3. **예상 동작**: 어떤 동작을 기대했는지
4. **실제 동작**: 실제로 어떤 일이 일어났는지
5. **스크린샷**: 가능한 경우 스크린샷 포함
6. **환경 정보**:
   - OS 버전
   - Python 버전
   - 프로젝트 버전
   - 관련 패키지 버전

### 기능 제안

기능 제안에는 다음 정보를 포함해 주세요:

1. **문제 설명**: 이 기능이 해결할 문제
2. **제안 솔루션**: 원하는 기능 설명
3. **대안**: 고려한 다른 해결 방법
4. **추가 컨텍스트**: 관련 스크린샷, 링크 등

## 질문하기

질문이 있으시면:

- [GitHub Discussions](https://github.com/yourusername/responsible-ai-automation/discussions)
- 이슈를 열어 질문을 올려주세요

---

다시 한 번 기여해 주셔서 감사합니다! 🎉

