#!/usr/bin/env python3
"""
AI 윤리 감사 도구

이 스크립트는 프로젝트의 AI 윤리 및 Responsible AI 준수 상황을 감사합니다.
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import re

class EthicsAuditor:
    """AI 윤리 감사 클래스"""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.audit_results = {
            'timestamp': datetime.now().isoformat(),
            'project_path': str(self.project_path),
            'checks': []
        }
    
    def check_fairness_code(self) -> Dict:
        """공정성 검증 코드 존재 여부 확인"""
        check_result = {
            'name': '공정성 검증 코드',
            'status': 'warning',
            'details': []
        }
        
        fairness_keywords = [
            'fairness', 'bias', 'demographic', 'equalized',
            '공정성', '편향', '그룹별'
        ]
        
        code_files = list(self.project_path.rglob('*.py'))
        found_files = []
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in fairness_keywords):
                        found_files.append(str(file_path.relative_to(self.project_path)))
            except:
                pass
        
        if found_files:
            check_result['status'] = 'pass'
            check_result['details'] = found_files[:5]  # 최대 5개만 표시
        else:
            check_result['details'] = ['공정성 검증 코드를 찾을 수 없습니다.']
        
        return check_result
    
    def check_privacy_code(self) -> Dict:
        """프라이버시 보호 코드 존재 여부 확인"""
        check_result = {
            'name': '프라이버시 보호 코드',
            'status': 'warning',
            'details': []
        }
        
        privacy_keywords = [
            'mask', 'encrypt', 'anonymize', 'pii', 'privacy',
            '마스킹', '암호화', '익명화', '개인정보'
        ]
        
        code_files = list(self.project_path.rglob('*.py'))
        found_files = []
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in privacy_keywords):
                        found_files.append(str(file_path.relative_to(self.project_path)))
            except:
                pass
        
        if found_files:
            check_result['status'] = 'pass'
            check_result['details'] = found_files[:5]
        else:
            check_result['details'] = ['프라이버시 보호 코드를 찾을 수 없습니다.']
        
        return check_result
    
    def check_explainability_code(self) -> Dict:
        """설명 가능성 코드 존재 여부 확인"""
        check_result = {
            'name': '설명 가능성 코드',
            'status': 'warning',
            'details': []
        }
        
        explainability_keywords = [
            'shap', 'lime', 'explain', 'feature_importance',
            '설명', '특성 중요도'
        ]
        
        code_files = list(self.project_path.rglob('*.py'))
        found_files = []
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if any(keyword in content for keyword in explainability_keywords):
                        found_files.append(str(file_path.relative_to(self.project_path)))
            except:
                pass
        
        if found_files:
            check_result['status'] = 'pass'
            check_result['details'] = found_files[:5]
        else:
            check_result['details'] = ['설명 가능성 코드를 찾을 수 없습니다.']
        
        return check_result
    
    def check_test_coverage(self) -> Dict:
        """테스트 커버리지 확인"""
        check_result = {
            'name': '테스트 커버리지',
            'status': 'warning',
            'details': []
        }
        
        test_files = list(self.project_path.rglob('test_*.py'))
        test_files.extend(list(self.project_path.rglob('*_test.py')))
        
        if test_files:
            check_result['status'] = 'pass'
            check_result['details'] = [
                f'테스트 파일 {len(test_files)}개 발견',
                *[str(f.relative_to(self.project_path)) for f in test_files[:5]]
            ]
        else:
            check_result['details'] = ['테스트 파일을 찾을 수 없습니다.']
        
        return check_result
    
    def check_documentation(self) -> Dict:
        """문서화 확인"""
        check_result = {
            'name': '문서화',
            'status': 'warning',
            'details': []
        }
        
        doc_files = []
        doc_patterns = ['README.md', '*.md', 'docs/**/*.md']
        
        for pattern in doc_patterns:
            doc_files.extend(list(self.project_path.rglob(pattern)))
        
        if doc_files:
            check_result['status'] = 'pass'
            check_result['details'] = [
                f'문서 파일 {len(doc_files)}개 발견',
                *[str(f.relative_to(self.project_path)) for f in doc_files[:5]]
            ]
        else:
            check_result['details'] = ['문서 파일을 찾을 수 없습니다.']
        
        return check_result
    
    def check_secrets(self) -> Dict:
        """비밀 정보 노출 확인"""
        check_result = {
            'name': '비밀 정보 보안',
            'status': 'pass',
            'details': []
        }
        
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
        ]
        
        code_files = list(self.project_path.rglob('*.py'))
        found_issues = []
        
        for file_path in code_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    for pattern in secret_patterns:
                        matches = re.findall(pattern, content, re.IGNORECASE)
                        if matches:
                            found_issues.append({
                                'file': str(file_path.relative_to(self.project_path)),
                                'pattern': pattern
                            })
            except:
                pass
        
        if found_issues:
            check_result['status'] = 'fail'
            check_result['details'] = [
                f'⚠️ 비밀 정보가 하드코딩된 파일 {len(found_issues)}개 발견',
                '환경 변수나 비밀 관리 시스템 사용을 권장합니다.'
            ]
        else:
            check_result['details'] = ['비밀 정보 하드코딩이 발견되지 않았습니다.']
        
        return check_result
    
    def run_audit(self) -> Dict:
        """전체 감사 실행"""
        print("🔍 AI 윤리 감사를 시작합니다...\n")
        
        checks = [
            self.check_fairness_code(),
            self.check_privacy_code(),
            self.check_explainability_code(),
            self.check_test_coverage(),
            self.check_documentation(),
            self.check_secrets(),
        ]
        
        self.audit_results['checks'] = checks
        
        return self.audit_results
    
    def print_report(self):
        """감사 결과 리포트 출력"""
        print("\n" + "="*60)
        print("AI 윤리 감사 리포트")
        print("="*60)
        print(f"프로젝트 경로: {self.audit_results['project_path']}")
        print(f"감사 일시: {self.audit_results['timestamp']}")
        print("="*60)
        
        passed = sum(1 for check in self.audit_results['checks'] if check['status'] == 'pass')
        warnings = sum(1 for check in self.audit_results['checks'] if check['status'] == 'warning')
        failed = sum(1 for check in self.audit_results['checks'] if check['status'] == 'fail')
        
        print(f"\n✅ 통과: {passed}")
        print(f"⚠️  경고: {warnings}")
        print(f"❌ 실패: {failed}")
        print()
        
        for check in self.audit_results['checks']:
            status_icon = {
                'pass': '✅',
                'warning': '⚠️',
                'fail': '❌'
            }.get(check['status'], '❓')
            
            print(f"{status_icon} {check['name']}")
            for detail in check['details']:
                print(f"   {detail}")
            print()
        
        print("="*60)
    
    def save_report(self, output_file: str):
        """감사 결과 저장"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.audit_results, f, indent=2, ensure_ascii=False)
        print(f"\n감사 결과가 저장되었습니다: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description='AI 윤리 감사 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 프로젝트 감사
  python ethics-audit.py --project-path ./my-ai-project
  
  # 감사 결과를 파일로 저장
  python ethics-audit.py --project-path ./my-ai-project --output audit-report.json
        """
    )
    
    parser.add_argument(
        '--project-path',
        required=True,
        help='감사할 프로젝트 경로'
    )
    
    parser.add_argument(
        '--output',
        help='감사 결과를 저장할 JSON 파일 경로'
    )
    
    args = parser.parse_args()
    
    auditor = EthicsAuditor(args.project_path)
    results = auditor.run_audit()
    auditor.print_report()
    
    if args.output:
        auditor.save_report(args.output)

if __name__ == '__main__':
    main()

