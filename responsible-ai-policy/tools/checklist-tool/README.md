# 체크리스트 도구

Responsible AI 체크리스트를 대화형으로 실행하고 결과를 저장하는 도구입니다.

## 설치

```bash
npm install
```

## 사용 방법

### 대화형 모드

```bash
npm start
# 또는
node index.js --interactive
```

대화형 모드에서는 다음을 선택할 수 있습니다:

1. **개발 단계별 체크리스트**: 기획, 설계, 개발, 테스트, 배포, 운영 단계별 체크리스트
2. **원칙별 체크리스트**: 공정성, 투명성, 프라이버시 등 원칙별 체크리스트
3. **전체 체크리스트**: 모든 체크리스트 항목

### 결과 확인

```bash
npm run check
# 또는
node index.js --check checklist-results.json
```

## 출력 형식

체크리스트 결과는 JSON 파일로 저장됩니다:

```json
{
  "timestamp": "2024-01-01T00:00:00.000Z",
  "results": {
    "planning": {
      "p1": true,
      "p2": false,
      ...
    }
  },
  "summary": {
    "total": 50,
    "passed": 45,
    "failed": 5,
    "percentage": 90
  }
}
```

## 체크리스트 항목

도구는 다음 체크리스트를 포함합니다:

### 개발 단계별
- 기획 단계 (8개 항목)
- 설계 단계 (8개 항목)
- 개발 단계 (6개 항목)
- 테스트 단계 (5개 항목)
- 배포 단계 (4개 항목)
- 운영 단계 (4개 항목)

### 원칙별
- 공정성 (3개 항목)
- 투명성 (3개 항목)
- 프라이버시 (3개 항목)

## CI/CD 통합

이 도구는 CI/CD 파이프라인에 통합할 수 있습니다:

```yaml
# GitHub Actions 예제
- name: Run AI Checklist
  run: |
    npm install
    echo 'n' | npm start  # 비대화형 모드 (향후 구현)
```

## 참고 자료

- [체크리스트 가이드라인](../../guidelines/checklist.md)
- [정책 템플릿](../../policies/)

