// Responsible AI 웹 서비스 예제 - JavaScript

class ResponsibleAIService {
    constructor() {
        this.initializeEventListeners();
        this.loadUserPreferences();
    }

    initializeEventListeners() {
        // AI 동의 체크박스
        const aiConsent = document.getElementById('aiConsent');
        const processBtn = document.getElementById('processBtn');
        
        aiConsent.addEventListener('change', (e) => {
            processBtn.disabled = !e.target.checked;
            if (e.target.checked) {
                this.logEvent('ai_consent_given');
            }
        });

        // 처리 버튼
        processBtn.addEventListener('click', () => {
            this.processWithAI();
        });

        // 설정 저장
        document.getElementById('saveSettings').addEventListener('click', () => {
            this.saveSettings();
        });

        // 데이터 관리
        document.getElementById('viewData').addEventListener('click', () => {
            this.viewUserData();
        });

        document.getElementById('exportData').addEventListener('click', () => {
            this.exportUserData();
        });

        document.getElementById('deleteData').addEventListener('click', () => {
            this.deleteUserData();
        });
    }

    async processWithAI() {
        const userInput = document.getElementById('userInput').value.trim();
        
        if (!userInput) {
            alert('텍스트를 입력해주세요.');
            return;
        }

        // 입력 검증
        if (!this.validateInput(userInput)) {
            alert('입력이 정책에 위배됩니다. 다시 입력해주세요.');
            return;
        }

        try {
            // 로딩 표시
            const processBtn = document.getElementById('processBtn');
            processBtn.disabled = true;
            processBtn.textContent = '처리 중...';

            // AI 처리 시뮬레이션 (실제로는 API 호출)
            const result = await this.simulateAIProcessing(userInput);
            
            // 결과 표시
            this.displayResult(result);
            
            // 이벤트 로깅
            this.logEvent('ai_processing_completed', {
                inputLength: userInput.length,
                processingTime: result.processingTime
            });

        } catch (error) {
            console.error('AI 처리 오류:', error);
            alert('처리 중 오류가 발생했습니다. 다시 시도해주세요.');
        } finally {
            const processBtn = document.getElementById('processBtn');
            processBtn.disabled = false;
            processBtn.textContent = '처리하기';
        }
    }

    validateInput(input) {
        // 유해 콘텐츠 필터링 (간단한 예제)
        const harmfulPatterns = [
            /violence/i,
            /hate/i,
            /illegal/i
        ];

        for (const pattern of harmfulPatterns) {
            if (pattern.test(input)) {
                this.logEvent('harmful_content_detected', { pattern: pattern.toString() });
                return false;
            }
        }

        return true;
    }

    async simulateAIProcessing(input) {
        // 실제로는 API 호출
        // 예제에서는 시뮬레이션
        return new Promise((resolve) => {
            setTimeout(() => {
                resolve({
                    output: `처리된 결과: ${input} (AI 처리 완료)`,
                    explanation: '이 결과는 입력 텍스트를 분석하여 생성되었습니다. AI 모델은 자연어 처리 기술을 사용하여 텍스트를 처리했습니다.',
                    processingTime: 500,
                    confidence: 0.95,
                    model: 'example-model-v1.0'
                });
            }, 500);
        });
    }

    displayResult(result) {
        const outputSection = document.getElementById('outputSection');
        const output = document.getElementById('output');
        const explanation = document.getElementById('explanation');

        output.textContent = result.output;
        explanation.textContent = result.explanation;

        outputSection.style.display = 'block';
        outputSection.scrollIntoView({ behavior: 'smooth' });
    }

    saveSettings() {
        const settings = {
            dataCollection: document.getElementById('dataCollection').checked,
            analytics: document.getElementById('analytics').checked,
            personalization: document.getElementById('personalization').checked
        };

        // 로컬 스토리지에 저장 (실제로는 서버에 저장)
        localStorage.setItem('userSettings', JSON.stringify(settings));
        
        this.logEvent('settings_saved', settings);
        alert('설정이 저장되었습니다.');
    }

    loadUserPreferences() {
        const savedSettings = localStorage.getItem('userSettings');
        if (savedSettings) {
            const settings = JSON.parse(savedSettings);
            document.getElementById('dataCollection').checked = settings.dataCollection || false;
            document.getElementById('analytics').checked = settings.analytics || false;
            document.getElementById('personalization').checked = settings.personalization || false;
        }
    }

    viewUserData() {
        const userData = {
            collectedData: this.getCollectedData(),
            settings: JSON.parse(localStorage.getItem('userSettings') || '{}'),
            lastUpdated: new Date().toISOString()
        };

        const dataInfo = document.getElementById('dataInfo');
        dataInfo.innerHTML = `
            <h3>내 데이터 정보</h3>
            <pre>${JSON.stringify(userData, null, 2)}</pre>
            <p><small>마지막 업데이트: ${userData.lastUpdated}</small></p>
        `;

        this.logEvent('data_viewed');
    }

    exportUserData() {
        const userData = {
            collectedData: this.getCollectedData(),
            settings: JSON.parse(localStorage.getItem('userSettings') || '{}'),
            exportDate: new Date().toISOString()
        };

        const dataStr = JSON.stringify(userData, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `user-data-${Date.now()}.json`;
        link.click();

        this.logEvent('data_exported');
        alert('데이터가 내보내졌습니다.');
    }

    deleteUserData() {
        if (!confirm('모든 데이터를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
            return;
        }

        // 로컬 스토리지 삭제
        localStorage.removeItem('userSettings');
        localStorage.removeItem('userEvents');
        
        // UI 초기화
        document.getElementById('dataCollection').checked = false;
        document.getElementById('analytics').checked = false;
        document.getElementById('personalization').checked = false;
        document.getElementById('aiConsent').checked = false;
        document.getElementById('processBtn').disabled = true;
        document.getElementById('outputSection').style.display = 'none';
        document.getElementById('dataInfo').innerHTML = '';

        this.logEvent('data_deleted');
        alert('모든 데이터가 삭제되었습니다.');
    }

    getCollectedData() {
        // 수집된 데이터 반환 (예제)
        const events = JSON.parse(localStorage.getItem('userEvents') || '[]');
        return {
            events: events,
            eventCount: events.length
        };
    }

    logEvent(eventName, data = {}) {
        const event = {
            name: eventName,
            timestamp: new Date().toISOString(),
            data: data,
            userAgent: navigator.userAgent,
            // 개인 식별 정보는 포함하지 않음
        };

        const events = JSON.parse(localStorage.getItem('userEvents') || '[]');
        events.push(event);
        
        // 최대 100개 이벤트만 보관
        if (events.length > 100) {
            events.shift();
        }
        
        localStorage.setItem('userEvents', JSON.stringify(events));
    }
}

// 서비스 초기화
document.addEventListener('DOMContentLoaded', () => {
    new ResponsibleAIService();
});

