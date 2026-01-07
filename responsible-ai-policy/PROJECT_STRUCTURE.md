# 프로젝트 구조

이 문서는 Responsible AI Policy Framework 프로젝트의 구조를 설명합니다.

## 디렉토리 구조

```
responsible-ai-policy/
├── README.md                 # 프로젝트 소개
├── LICENSE                   # MIT 라이선스
├── CONTRIBUTING.md          # 기여 가이드
├── PROJECT_STRUCTURE.md     # 이 문서
├── .gitignore               # Git 무시 파일
│
├── docs/                    # 문서
│   ├── platforms/          # 플랫폼별 AI 정책
│   │   ├── google-ai-principles.md
│   │   ├── openai-policies.md
│   │   ├── claude-guidelines.md
│   │   ├── anthropic-safety.md
│   │   ├── perplexity-policies.md
│   │   ├── naver-ai-policies.md
│   │   └── kakao-ai-policies.md
│   └── regulations/        # 규제 및 법률
│       ├── eu-ai-act.md
│       └── eu-ai-ethics-guidelines.md
│
├── guidelines/              # 가이드라인
│   ├── responsible-ai-principles.md
│   ├── implementation-guidelines.md
│   └── checklist.md
│
├── policies/                # 정책 템플릿
│   ├── web-service-policy.md
│   ├── mobile-app-policy.md
│   └── api-service-policy.md
│
├── examples/                # 예제 코드
│   ├── web/                 # 웹 서비스 예제
│   │   ├── index.html
│   │   ├── styles.css
│   │   └── app.js
│   ├── mobile/              # 모바일 앱 예제
│   │   ├── README.md
│   │   └── react-native/
│   │       └── AIService.js
│   └── api/                 # API 서비스 예제
│       ├── server.js
│       ├── package.json
│       └── README.md
│
└── tools/                   # 검증 도구
    ├── policy-validator/    # 정책 검증 도구 (Python)
    │   ├── validator.py
    │   ├── requirements.txt
    │   └── README.md
    └── checklist-tool/      # 체크리스트 도구 (Node.js)
        ├── index.js
        ├── package.json
        └── README.md
```

## 주요 컴포넌트

### 1. 문서 (docs/)

#### 1.1 플랫폼별 AI 정책 (docs/platforms/)

각 주요 AI 플랫폼의 정책과 가이드라인을 문서화합니다:

- **Google AI Principles**: Google의 AI 원칙 및 정책
- **OpenAI Policies**: OpenAI 사용 정책 및 보안 가이드라인
- **Claude Guidelines**: Anthropic의 Claude AI 가이드라인
- **Anthropic Safety**: Anthropic의 AI 안전 연구 및 정책
- **Perplexity Policies**: Perplexity AI의 정책 및 가이드라인
- **Naver AI Policies**: 네이버의 AI 정책 및 주권 AI 전략
- **Kakao AI Policies**: 카카오의 AI 윤리 가이드라인

#### 1.2 규제 및 법률 (docs/regulations/)

AI 관련 규제 및 법률을 문서화합니다:

- **EU AI Act**: 유럽연합 인공지능법 (위험 기반 규제)
- **EU AI Ethics Guidelines**: EU 신뢰할 수 있는 AI를 위한 윤리 가이드라인

### 2. 가이드라인 (guidelines/)

Responsible AI 구현을 위한 가이드라인:

- **responsible-ai-principles.md**: 7대 핵심 원칙
- **implementation-guidelines.md**: 개발 단계별 구현 가이드
- **checklist.md**: 체크리스트 항목

### 3. 정책 템플릿 (policies/)

서비스 유형별 보안 정책 템플릿:

- **web-service-policy.md**: 웹 서비스용 정책 템플릿
- **mobile-app-policy.md**: 모바일 앱용 정책 템플릿
- **api-service-policy.md**: API 서비스용 정책 템플릿

### 4. 예제 (examples/)

실제 구현 예제 코드:

- **web/**: HTML/CSS/JavaScript 웹 애플리케이션 예제
- **mobile/**: React Native 모바일 앱 예제
- **api/**: Node.js/Express API 서비스 예제

### 5. 도구 (tools/)

정책 준수 검증 도구:

- **policy-validator/**: Python 기반 정책 검증 도구
- **checklist-tool/**: Node.js 기반 체크리스트 도구

## 파일 설명

### README.md
프로젝트 소개, 빠른 시작 가이드, 사용 방법

### LICENSE
MIT 라이선스

### CONTRIBUTING.md
기여 가이드 및 개발 환경 설정

### .gitignore
Git에서 무시할 파일 목록

## 사용 흐름

1. **정책 학습**: `docs/` 및 `guidelines/` 문서 읽기
2. **정책 수립**: `policies/` 템플릿 사용
3. **구현**: `examples/` 예제 참고
4. **검증**: `tools/` 도구 사용

## 확장 계획

향후 추가될 수 있는 내용:

- 더 많은 플랫폼 정책 (Microsoft, Meta 등)
- 추가 예제 (Python, Java 등)
- 자동화된 테스트 도구
- CI/CD 통합 예제
- 다국어 지원

## 참고

프로젝트 구조는 필요에 따라 변경될 수 있습니다. 주요 변경 사항은 CHANGELOG에 기록됩니다.

