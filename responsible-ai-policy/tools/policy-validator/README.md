# 정책 검증 도구

이 도구는 서비스가 Responsible AI 정책을 준수하는지 자동으로 검증합니다.

## 설치

```bash
pip install -r requirements.txt
```

## 사용 방법

### 1. 예제 설정 파일 생성

```bash
python validator.py --create-example
```

이 명령은 `policy-config.json` 예제 파일을 생성합니다.

### 2. 설정 파일 수정

생성된 `policy-config.json` 파일을 서비스에 맞게 수정하세요.

### 3. 정책 검증

```bash
python validator.py --config policy-config.json
```

### 4. 결과를 파일로 저장

```bash
python validator.py --config policy-config.json --output results.json
```

## 설정 파일 구조

설정 파일은 다음 섹션을 포함해야 합니다:

- `privacy`: 프라이버시 정책
- `security`: 보안 정책
- `bias_prevention`: 편향 방지 정책
- `transparency`: 투명성 정책
- `data`: 데이터 관리
- `consent`: 사용자 동의
- `monitoring`: 모니터링 시스템

자세한 구조는 예제 설정 파일을 참조하세요.

## 검증 항목

도구는 다음 항목을 검증합니다:

1. **프라이버시 정책**
   - 데이터 수집 정책
   - 데이터 저장 정책
   - 데이터 공유 정책
   - 사용자 권리

2. **보안 정책**
   - 암호화 설정
   - 인증 메커니즘
   - Rate limiting

3. **편향 방지 정책**
   - 편향 테스트
   - 편향 모니터링

4. **투명성 정책**
   - AI 사용 고지
   - 설명 가능성

5. **데이터 최소화**
   - 데이터 최소화 원칙
   - 목적 제한 원칙

6. **사용자 동의**
   - 명시적 동의
   - 동의 철회

7. **모니터링**
   - 성능 모니터링
   - 보안 모니터링

## CI/CD 통합

이 도구는 CI/CD 파이프라인에 통합할 수 있습니다:

```yaml
# GitHub Actions 예제
- name: Validate AI Policy
  run: |
    python tools/policy-validator/validator.py --config policy-config.json
```

## 출력 형식

검증 결과는 다음 형식으로 출력됩니다:

- ✅ 통과한 검사
- ❌ 실패한 검사
- ⚠️ 경고

실패한 검사가 있으면 종료 코드 1을 반환합니다.

## 참고 자료

- [정책 템플릿](../../policies/)
- [가이드라인](../../guidelines/)

