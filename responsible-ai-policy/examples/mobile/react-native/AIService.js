// React Native Responsible AI 서비스 예제

import AsyncStorage from '@react-native-async-storage/async-storage';
import Keychain from 'react-native-keychain';
import { Platform } from 'react-native';

class ResponsibleAIService {
    constructor() {
        this.apiBaseUrl = 'https://api.example.com';
        this.apiKeyStorageKey = 'api_key';
    }

    /**
     * API 키를 안전하게 저장 (Keychain/Keystore 사용)
     */
    async saveAPIKey(apiKey) {
        try {
            if (Platform.OS === 'ios') {
                await Keychain.setInternetCredentials(
                    'ai_service',
                    'api_key',
                    apiKey
                );
            } else {
                await Keychain.setInternetCredentials(
                    'ai_service',
                    'api_key',
                    apiKey
                );
            }
            return true;
        } catch (error) {
            console.error('API 키 저장 실패:', error);
            return false;
        }
    }

    /**
     * 저장된 API 키 가져오기
     */
    async getAPIKey() {
        try {
            const credentials = await Keychain.getInternetCredentials('ai_service');
            if (credentials) {
                return credentials.password;
            }
            return null;
        } catch (error) {
            console.error('API 키 가져오기 실패:', error);
            return null;
        }
    }

    /**
     * AI 요청 처리 (입력 검증 포함)
     */
    async processWithAI(input, options = {}) {
        // 입력 검증
        if (!this.validateInput(input)) {
            throw new Error('입력이 정책에 위배됩니다.');
        }

        // 사용자 동의 확인
        const consent = await this.getAIConsent();
        if (!consent) {
            throw new Error('AI 사용 동의가 필요합니다.');
        }

        try {
            const apiKey = await this.getAPIKey();
            if (!apiKey) {
                throw new Error('API 키가 설정되지 않았습니다.');
            }

            const response = await fetch(`${this.apiBaseUrl}/ai/process`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${apiKey}`,
                },
                body: JSON.stringify({
                    input: input,
                    options: options,
                }),
            });

            if (!response.ok) {
                throw new Error(`API 오류: ${response.status}`);
            }

            const result = await response.json();
            
            // 응답 필터링
            const filteredResult = this.filterResponse(result);
            
            // 이벤트 로깅
            await this.logEvent('ai_processing_completed', {
                inputLength: input.length,
                success: true,
            });

            return filteredResult;
        } catch (error) {
            await this.logEvent('ai_processing_failed', {
                error: error.message,
            });
            throw error;
        }
    }

    /**
     * 입력 검증
     */
    validateInput(input) {
        if (!input || typeof input !== 'string') {
            return false;
        }

        // 유해 콘텐츠 패턴 검사
        const harmfulPatterns = [
            /violence/i,
            /hate/i,
            /illegal/i,
        ];

        for (const pattern of harmfulPatterns) {
            if (pattern.test(input)) {
                this.logEvent('harmful_content_detected');
                return false;
            }
        }

        // 크기 제한
        if (input.length > 10000) {
            return false;
        }

        return true;
    }

    /**
     * 응답 필터링
     */
    filterResponse(response) {
        // 유해 콘텐츠 제거
        if (response.output) {
            // 필터링 로직 (실제 구현 필요)
            response.output = this.filterHarmfulContent(response.output);
        }

        // 개인정보 제거
        if (response.metadata) {
            delete response.metadata.userId;
            delete response.metadata.ipAddress;
        }

        return response;
    }

    /**
     * 유해 콘텐츠 필터링
     */
    filterHarmfulContent(content) {
        // 실제 필터링 로직 구현
        return content;
    }

    /**
     * AI 사용 동의 가져오기
     */
    async getAIConsent() {
        try {
            const consent = await AsyncStorage.getItem('ai_consent');
            return consent === 'true';
        } catch (error) {
            console.error('동의 정보 가져오기 실패:', error);
            return false;
        }
    }

    /**
     * AI 사용 동의 저장
     */
    async setAIConsent(consent) {
        try {
            await AsyncStorage.setItem('ai_consent', consent.toString());
            await this.logEvent('ai_consent_updated', { consent });
            return true;
        } catch (error) {
            console.error('동의 정보 저장 실패:', error);
            return false;
        }
    }

    /**
     * 사용자 설정 저장
     */
    async saveUserSettings(settings) {
        try {
            await AsyncStorage.setItem('user_settings', JSON.stringify(settings));
            await this.logEvent('settings_saved', settings);
            return true;
        } catch (error) {
            console.error('설정 저장 실패:', error);
            return false;
        }
    }

    /**
     * 사용자 설정 가져오기
     */
    async getUserSettings() {
        try {
            const settings = await AsyncStorage.getItem('user_settings');
            return settings ? JSON.parse(settings) : {};
        } catch (error) {
            console.error('설정 가져오기 실패:', error);
            return {};
        }
    }

    /**
     * 사용자 데이터 가져오기
     */
    async getUserData() {
        try {
            const consent = await this.getAIConsent();
            const settings = await this.getUserSettings();
            const events = await this.getUserEvents();

            return {
                consent,
                settings,
                events: events.slice(-10), // 최근 10개만
                lastUpdated: new Date().toISOString(),
            };
        } catch (error) {
            console.error('사용자 데이터 가져오기 실패:', error);
            return null;
        }
    }

    /**
     * 사용자 데이터 삭제
     */
    async deleteUserData() {
        try {
            await AsyncStorage.removeItem('ai_consent');
            await AsyncStorage.removeItem('user_settings');
            await AsyncStorage.removeItem('user_events');
            await this.logEvent('data_deleted');
            return true;
        } catch (error) {
            console.error('데이터 삭제 실패:', error);
            return false;
        }
    }

    /**
     * 이벤트 로깅
     */
    async logEvent(eventName, data = {}) {
        try {
            const event = {
                name: eventName,
                timestamp: new Date().toISOString(),
                data: data,
                platform: Platform.OS,
                // 개인 식별 정보는 포함하지 않음
            };

            const events = await this.getUserEvents();
            events.push(event);

            // 최대 100개 이벤트만 보관
            if (events.length > 100) {
                events.shift();
            }

            await AsyncStorage.setItem('user_events', JSON.stringify(events));
        } catch (error) {
            console.error('이벤트 로깅 실패:', error);
        }
    }

    /**
     * 사용자 이벤트 가져오기
     */
    async getUserEvents() {
        try {
            const events = await AsyncStorage.getItem('user_events');
            return events ? JSON.parse(events) : [];
        } catch (error) {
            console.error('이벤트 가져오기 실패:', error);
            return [];
        }
    }
}

export default new ResponsibleAIService();

