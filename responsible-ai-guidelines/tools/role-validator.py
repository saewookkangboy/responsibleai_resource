#!/usr/bin/env python3
"""
역할별 가이드라인 검증 도구

이 스크립트는 특정 역할의 가이드라인 준수 여부를 검증합니다.
"""

import argparse
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class RoleValidator:
    """역할별 가이드라인 검증 클래스"""
    
    def __init__(self, guidelines_dir: str = "guidelines"):
        self.guidelines_dir = Path(guidelines_dir)
        self.roles = {
            'developer': 'developer.md',
            'data-scientist': 'data-scientist.md',
            'ml-engineer': 'ml-engineer.md',
            'project-manager': 'project-manager.md',
            'qa-tester': 'qa-tester.md',
            'product-manager': 'product-manager.md'
        }
    
    def get_role_guidelines(self, role: str) -> Dict:
        """역할별 가이드라인 가져오기"""
        if role not in self.roles:
            return {'error': f'알 수 없는 역할: {role}'}
        
        guideline_file = self.guidelines_dir / self.roles[role]
        
        if not guideline_file.exists():
            return {'error': f'가이드라인 파일을 찾을 수 없습니다: {guideline_file}'}
        
        with open(guideline_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 체크리스트 항목 추출
        checklist_items = []
        current_section = None
        
        for line in content.split('\n'):
            line = line.strip()
            
            if line.startswith('##') or line.startswith('###'):
                current_section = line.lstrip('#').strip()
            
            if line.startswith('- [ ]') or line.startswith('- [x]'):
                item_text = line[5:].strip()
                checklist_items.append({
                    'text': item_text,
                    'section': current_section
                })
        
        return {
            'role': role,
            'guideline_file': str(guideline_file),
            'checklist_items': checklist_items,
            'total_items': len(checklist_items)
        }
    
    def validate_role(self, role: str) -> Dict:
        """역할별 가이드라인 검증"""
        guidelines = self.get_role_guidelines(role)
        
        if 'error' in guidelines:
            return guidelines
        
        # 간단한 검증 (실제로는 프로젝트 코드를 분석해야 함)
        validation_result = {
            'role': role,
            'timestamp': datetime.now().isoformat(),
            'guidelines_found': True,
            'total_checklist_items': guidelines['total_items'],
            'recommendations': []
        }
        
        # 역할별 권장 사항
        recommendations = {
            'developer': [
                '공정성 검증 코드 작성 확인',
                '프라이버시 보호 코드 작성 확인',
                '테스트 커버리지 80% 이상 확인',
                '코드 문서화 완성도 확인'
            ],
            'data-scientist': [
                '데이터 편향 분석 수행 확인',
                '공정성 메트릭 측정 확인',
                '모델 설명 가능성 검증 확인',
                '데이터 프라이버시 보호 확인'
            ],
            'ml-engineer': [
                '모델 모니터링 시스템 구축 확인',
                '공정성 메트릭 추적 확인',
                '데이터 드리프트 감지 확인',
                '모델 버전 관리 확인'
            ],
            'project-manager': [
                '프로젝트 일정에 윤리 검증 단계 포함 확인',
                '리스크 레지스터 작성 확인',
                '이해관계자 커뮤니케이션 계획 확인',
                '품질 게이트 설정 확인'
            ],
            'qa-tester': [
                '공정성 테스트 케이스 작성 확인',
                '보안 테스트 수행 확인',
                '설명 가능성 테스트 확인',
                '다양한 그룹에 대한 테스트 확인'
            ],
            'product-manager': [
                '제품 전략에 AI 윤리 원칙 포함 확인',
                '사용자 피드백 수집 메커니즘 확인',
                '프라이버시 정책 작성 확인',
                '제품 제한사항 명시 확인'
            ]
        }
        
        validation_result['recommendations'] = recommendations.get(role, [])
        
        return validation_result
    
    def print_report(self, result: Dict):
        """검증 결과 리포트 출력"""
        if 'error' in result:
            print(f"❌ 오류: {result['error']}")
            return
        
        print("\n" + "="*60)
        print(f"역할별 가이드라인 검증 리포트")
        print("="*60)
        print(f"역할: {result['role']}")
        print(f"가이드라인 파일 발견: {'✅' if result.get('guidelines_found') else '❌'}")
        print(f"체크리스트 항목 수: {result.get('total_checklist_items', 0)}")
        print("="*60)
        
        if result.get('recommendations'):
            print("\n📋 권장 사항:")
            for i, rec in enumerate(result['recommendations'], 1):
                print(f"  {i}. {rec}")
        
        print("\n💡 다음 단계:")
        print(f"  1. {result['role']} 가이드라인 문서를 검토하세요")
        print(f"  2. 체크리스트를 사용하여 진행 상황을 추적하세요")
        print(f"  3. 정기적으로 가이드라인 준수 여부를 검토하세요")
        print()

def main():
    parser = argparse.ArgumentParser(
        description='역할별 가이드라인 검증 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 개발자 가이드라인 검증
  python role-validator.py --role developer
  
  # 사용 가능한 역할 목록
  python role-validator.py --list-roles
        """
    )
    
    parser.add_argument(
        '--role',
        choices=['developer', 'data-scientist', 'ml-engineer', 
                'project-manager', 'qa-tester', 'product-manager'],
        help='검증할 역할'
    )
    
    parser.add_argument(
        '--list-roles',
        action='store_true',
        help='사용 가능한 역할 목록 출력'
    )
    
    parser.add_argument(
        '--guidelines-dir',
        default='guidelines',
        help='가이드라인 디렉토리 경로 (기본값: guidelines)'
    )
    
    args = parser.parse_args()
    
    validator = RoleValidator(guidelines_dir=args.guidelines_dir)
    
    if args.list_roles:
        print("\n사용 가능한 역할:")
        for role in validator.roles.keys():
            print(f"  - {role}")
        print()
    elif args.role:
        result = validator.validate_role(args.role)
        validator.print_report(result)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

