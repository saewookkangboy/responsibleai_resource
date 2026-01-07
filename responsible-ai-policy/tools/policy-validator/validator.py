#!/usr/bin/env python3
"""
Responsible AI 정책 검증 도구

이 도구는 서비스가 Responsible AI 정책을 준수하는지 검증합니다.
"""

import json
import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime

class PolicyValidator:
    def __init__(self):
        self.checks = []
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
    
    def check_privacy_policy(self, config: Dict) -> Tuple[bool, str]:
        """프라이버시 정책 검증"""
        required_fields = [
            'data_collection',
            'data_storage',
            'data_sharing',
            'user_rights'
        ]
        
        missing = [field for field in required_fields if field not in config.get('privacy', {})]
        
        if missing:
            return False, f"프라이버시 정책에 필수 필드가 없습니다: {', '.join(missing)}"
        
        return True, "프라이버시 정책이 올바르게 설정되었습니다."
    
    def check_security_policy(self, config: Dict) -> Tuple[bool, str]:
        """보안 정책 검증"""
        security = config.get('security', {})
        
        if not security.get('encryption'):
            return False, "데이터 암호화가 설정되지 않았습니다."
        
        if not security.get('authentication'):
            return False, "인증 메커니즘이 설정되지 않았습니다."
        
        if not security.get('rate_limiting'):
            return False, "Rate limiting이 설정되지 않았습니다."
        
        return True, "보안 정책이 올바르게 설정되었습니다."
    
    def check_bias_policy(self, config: Dict) -> Tuple[bool, str]:
        """편향 방지 정책 검증"""
        bias = config.get('bias_prevention', {})
        
        if not bias.get('testing'):
            return False, "편향 테스트가 설정되지 않았습니다."
        
        if not bias.get('monitoring'):
            return False, "편향 모니터링이 설정되지 않았습니다."
        
        return True, "편향 방지 정책이 올바르게 설정되었습니다."
    
    def check_transparency_policy(self, config: Dict) -> Tuple[bool, str]:
        """투명성 정책 검증"""
        transparency = config.get('transparency', {})
        
        if not transparency.get('ai_disclosure'):
            return False, "AI 사용 고지가 설정되지 않았습니다."
        
        if not transparency.get('explainability'):
            return False, "설명 가능성이 설정되지 않았습니다."
        
        return True, "투명성 정책이 올바르게 설정되었습니다."
    
    def check_data_minimization(self, config: Dict) -> Tuple[bool, str]:
        """데이터 최소화 원칙 검증"""
        data = config.get('data', {})
        
        if not data.get('minimization'):
            return False, "데이터 최소화 원칙이 적용되지 않았습니다."
        
        if not data.get('purpose_limitation'):
            return False, "목적 제한 원칙이 적용되지 않았습니다."
        
        return True, "데이터 최소화 원칙이 올바르게 적용되었습니다."
    
    def check_user_consent(self, config: Dict) -> Tuple[bool, str]:
        """사용자 동의 관리 검증"""
        consent = config.get('consent', {})
        
        if not consent.get('explicit_consent'):
            return False, "명시적 동의가 설정되지 않았습니다."
        
        if not consent.get('withdrawal'):
            return False, "동의 철회 메커니즘이 설정되지 않았습니다."
        
        return True, "사용자 동의 관리가 올바르게 설정되었습니다."
    
    def check_monitoring(self, config: Dict) -> Tuple[bool, str]:
        """모니터링 시스템 검증"""
        monitoring = config.get('monitoring', {})
        
        if not monitoring.get('performance'):
            return False, "성능 모니터링이 설정되지 않았습니다."
        
        if not monitoring.get('security'):
            return False, "보안 모니터링이 설정되지 않았습니다."
        
        return True, "모니터링 시스템이 올바르게 설정되었습니다."
    
    def validate(self, config_path: str) -> Dict:
        """정책 검증 실행"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except FileNotFoundError:
            return {
                'error': f'설정 파일을 찾을 수 없습니다: {config_path}'
            }
        except json.JSONDecodeError as e:
            return {
                'error': f'JSON 파싱 오류: {str(e)}'
            }
        
        # 검증 체크 실행
        checks = [
            ('프라이버시 정책', self.check_privacy_policy),
            ('보안 정책', self.check_security_policy),
            ('편향 방지 정책', self.check_bias_policy),
            ('투명성 정책', self.check_transparency_policy),
            ('데이터 최소화', self.check_data_minimization),
            ('사용자 동의', self.check_user_consent),
            ('모니터링', self.check_monitoring),
        ]
        
        for name, check_func in checks:
            passed, message = check_func(config)
            if passed:
                self.results['passed'].append({
                    'check': name,
                    'message': message
                })
            else:
                self.results['failed'].append({
                    'check': name,
                    'message': message
                })
        
        return self.results
    
    def print_report(self, results: Dict):
        """검증 결과 리포트 출력"""
        print("\n" + "="*60)
        print("Responsible AI 정책 검증 결과")
        print("="*60)
        print(f"검증 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print()
        
        if 'error' in results:
            print(f"❌ 오류: {results['error']}")
            return
        
        total = len(results['passed']) + len(results['failed'])
        passed_count = len(results['passed'])
        failed_count = len(results['failed'])
        
        print(f"전체 검사: {total}")
        print(f"✅ 통과: {passed_count}")
        print(f"❌ 실패: {failed_count}")
        print()
        
        if results['passed']:
            print("✅ 통과한 검사:")
            for item in results['passed']:
                print(f"  - {item['check']}: {item['message']}")
            print()
        
        if results['failed']:
            print("❌ 실패한 검사:")
            for item in results['failed']:
                print(f"  - {item['check']}: {item['message']}")
            print()
        
        # 종합 평가
        if failed_count == 0:
            print("🎉 모든 검사를 통과했습니다!")
        elif failed_count <= 2:
            print("⚠️  일부 검사를 통과하지 못했습니다. 개선이 필요합니다.")
        else:
            print("🚨 많은 검사를 통과하지 못했습니다. 즉시 개선이 필요합니다.")
        
        print("="*60)


def create_example_config(output_path: str):
    """예제 설정 파일 생성"""
    example_config = {
        "privacy": {
            "data_collection": {
                "minimization": True,
                "purpose_limitation": True,
                "explicit_consent": True
            },
            "data_storage": {
                "encryption": True,
                "retention_period": 365,
                "auto_deletion": True
            },
            "data_sharing": {
                "third_party": False,
                "anonymization": True
            },
            "user_rights": {
                "access": True,
                "modification": True,
                "deletion": True,
                "portability": True
            }
        },
        "security": {
            "encryption": {
                "in_transit": True,
                "at_rest": True,
                "algorithm": "AES-256"
            },
            "authentication": {
                "api_key": True,
                "oauth": True,
                "multi_factor": False
            },
            "rate_limiting": {
                "enabled": True,
                "requests_per_minute": 100
            }
        },
        "bias_prevention": {
            "testing": {
                "enabled": True,
                "frequency": "quarterly"
            },
            "monitoring": {
                "enabled": True,
                "metrics": ["fairness", "accuracy"]
            }
        },
        "transparency": {
            "ai_disclosure": {
                "enabled": True,
                "location": "user_interface"
            },
            "explainability": {
                "enabled": True,
                "method": "feature_importance"
            }
        },
        "data": {
            "minimization": True,
            "purpose_limitation": True,
            "anonymization": True
        },
        "consent": {
            "explicit_consent": True,
            "withdrawal": True,
            "granular": True
        },
        "monitoring": {
            "performance": {
                "enabled": True,
                "metrics": ["response_time", "accuracy"]
            },
            "security": {
                "enabled": True,
                "alerts": True
            }
        }
    }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(example_config, f, indent=2, ensure_ascii=False)
    
    print(f"예제 설정 파일이 생성되었습니다: {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Responsible AI 정책 검증 도구'
    )
    parser.add_argument(
        '--config',
        type=str,
        default='policy-config.json',
        help='검증할 설정 파일 경로 (기본값: policy-config.json)'
    )
    parser.add_argument(
        '--create-example',
        action='store_true',
        help='예제 설정 파일 생성'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='결과를 JSON 파일로 저장할 경로'
    )
    
    args = parser.parse_args()
    
    if args.create_example:
        create_example_config(args.config)
        return
    
    validator = PolicyValidator()
    results = validator.validate(args.config)
    
    validator.print_report(results)
    
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n결과가 저장되었습니다: {args.output}")
    
    # 실패한 검사가 있으면 종료 코드 1 반환
    if 'error' in results or len(results.get('failed', [])) > 0:
        sys.exit(1)


if __name__ == '__main__':
    main()

