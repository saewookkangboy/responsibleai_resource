// Responsible AI API 서비스 예제 (Node.js/Express)

const express = require('express');
const rateLimit = require('express-rate-limit');
const helmet = require('helmet');
const cors = require('cors');
const crypto = require('crypto');

const app = express();
const PORT = process.env.PORT || 3000;

// 미들웨어
app.use(helmet()); // 보안 헤더
app.use(cors({
    origin: process.env.ALLOWED_ORIGINS?.split(',') || ['http://localhost:3000'],
    credentials: true
}));
app.use(express.json({ limit: '10mb' })); // 요청 크기 제한

// Rate Limiting
const limiter = rateLimit({
    windowMs: 15 * 60 * 1000, // 15분
    max: 100, // 최대 100 요청
    message: '너무 많은 요청이 발생했습니다. 잠시 후 다시 시도해주세요.',
    standardHeaders: true,
    legacyHeaders: false,
});

app.use('/api/', limiter);

// API 키 검증 미들웨어
function authenticateAPIKey(req, res, next) {
    const apiKey = req.headers['x-api-key'] || req.query.api_key;
    
    if (!apiKey) {
        return res.status(401).json({
            error: 'API 키가 필요합니다.',
            code: 'MISSING_API_KEY'
        });
    }

    // 실제로는 데이터베이스에서 API 키 검증
    // 예제에서는 환경 변수와 비교
    if (apiKey !== process.env.API_KEY) {
        return res.status(401).json({
            error: '유효하지 않은 API 키입니다.',
            code: 'INVALID_API_KEY'
        });
    }

    req.apiKey = apiKey;
    next();
}

// 입력 검증 미들웨어
function validateInput(req, res, next) {
    const { input } = req.body;

    if (!input || typeof input !== 'string') {
        return res.status(400).json({
            error: '입력이 필요합니다.',
            code: 'INVALID_INPUT'
        });
    }

    // 크기 제한
    if (input.length > 10000) {
        return res.status(400).json({
            error: '입력이 너무 깁니다. (최대 10,000자)',
            code: 'INPUT_TOO_LARGE'
        });
    }

    // 유해 콘텐츠 검사
    if (containsHarmfulContent(input)) {
        logSecurityEvent(req, 'harmful_content_detected', { inputLength: input.length });
        return res.status(400).json({
            error: '입력이 정책에 위배됩니다.',
            code: 'HARMFUL_CONTENT'
        });
    }

    next();
}

// 유해 콘텐츠 검사
function containsHarmfulContent(text) {
    const harmfulPatterns = [
        /violence/i,
        /hate/i,
        /illegal/i,
    ];

    return harmfulPatterns.some(pattern => pattern.test(text));
}

// 응답 필터링
function filterResponse(response) {
    // 유해 콘텐츠 제거
    if (response.output) {
        response.output = filterHarmfulContent(response.output);
    }

    // 개인정보 제거
    if (response.metadata) {
        delete response.metadata.userId;
        delete response.metadata.ipAddress;
    }

    return response;
}

function filterHarmfulContent(content) {
    // 실제 필터링 로직 구현
    return content;
}

// 보안 이벤트 로깅
function logSecurityEvent(req, eventType, data = {}) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        event: eventType,
        ip: req.ip,
        userAgent: req.get('user-agent'),
        data: data
    };

    // 실제로는 로그 시스템에 저장
    console.log('[SECURITY]', JSON.stringify(logEntry));
}

// 요청 로깅 미들웨어
function logRequest(req, res, next) {
    const logEntry = {
        timestamp: new Date().toISOString(),
        method: req.method,
        path: req.path,
        ip: req.ip,
        userAgent: req.get('user-agent'),
    };

    console.log('[REQUEST]', JSON.stringify(logEntry));
    next();
}

app.use(logRequest);

// AI 처리 엔드포인트
app.post('/api/ai/process', authenticateAPIKey, validateInput, async (req, res) => {
    try {
        const { input, options = {} } = req.body;

        // AI 처리 시뮬레이션 (실제로는 AI 모델 호출)
        const result = await simulateAIProcessing(input, options);

        // 응답 필터링
        const filteredResult = filterResponse(result);

        // 성공 로깅
        logSecurityEvent(req, 'ai_processing_completed', {
            inputLength: input.length,
            processingTime: result.processingTime
        });

        res.json({
            success: true,
            data: filteredResult,
            metadata: {
                model: 'example-model-v1.0',
                version: '1.0.0',
                timestamp: new Date().toISOString()
            }
        });

    } catch (error) {
        console.error('AI 처리 오류:', error);
        
        logSecurityEvent(req, 'ai_processing_failed', {
            error: error.message
        });

        res.status(500).json({
            error: 'AI 처리 중 오류가 발생했습니다.',
            code: 'PROCESSING_ERROR'
        });
    }
});

// AI 처리 시뮬레이션
async function simulateAIProcessing(input, options) {
    // 실제로는 AI API 호출
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                output: `처리된 결과: ${input} (AI 처리 완료)`,
                explanation: '이 결과는 입력 텍스트를 분석하여 생성되었습니다.',
                processingTime: 500,
                confidence: 0.95
            });
        }, 500);
    });
}

// 헬스 체크 엔드포인트
app.get('/api/health', (req, res) => {
    res.json({
        status: 'healthy',
        timestamp: new Date().toISOString(),
        version: '1.0.0'
    });
});

// 404 핸들러
app.use((req, res) => {
    res.status(404).json({
        error: '엔드포인트를 찾을 수 없습니다.',
        code: 'NOT_FOUND'
    });
});

// 에러 핸들러
app.use((err, req, res, next) => {
    console.error('서버 오류:', err);
    
    res.status(500).json({
        error: '서버 내부 오류가 발생했습니다.',
        code: 'INTERNAL_ERROR'
    });
});

// 서버 시작
app.listen(PORT, () => {
    console.log(`서버가 포트 ${PORT}에서 실행 중입니다.`);
    console.log(`환경: ${process.env.NODE_ENV || 'development'}`);
});

module.exports = app;

