#!/usr/bin/env python3
"""
체크리스트 검증 도구

이 스크립트는 역할별, 단계별 체크리스트를 검증하고 진행 상황을 추적합니다.
"""

import argparse
import json
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class ChecklistValidator:
    """체크리스트 검증 클래스"""
    
    def __init__(self, checklist_dir: str = "checklists"):
        self.checklist_dir = Path(checklist_dir)
        self.progress_file = Path(".checklist_progress.json")
        self.progress = self._load_progress()
    
    def _load_progress(self) -> Dict:
        """진행 상황 로드"""
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_progress(self):
        """진행 상황 저장"""
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(self.progress, f, indent=2, ensure_ascii=False)
    
    def _parse_checklist(self, checklist_path: Path) -> List[Dict]:
        """체크리스트 파일 파싱"""
        items = []
        current_section = None
        
        with open(checklist_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # 섹션 헤더 감지
                if line.startswith('##') or line.startswith('###'):
                    current_section = line.lstrip('#').strip()
                
                # 체크리스트 항목 감지
                if line.startswith('- [ ]') or line.startswith('- [x]'):
                    item_text = line[5:].strip()
                    is_checked = line.startswith('- [x]')
                    items.append({
                        'text': item_text,
                        'checked': is_checked,
                        'section': current_section
                    })
        
        return items
    
    def validate_checklist(self, phase: str, role: Optional[str] = None) -> Dict:
        """체크리스트 검증"""
        checklist_file = self.checklist_dir / f"{phase}.md"
        
        if not checklist_file.exists():
            return {
                'error': f"체크리스트 파일을 찾을 수 없습니다: {checklist_file}"
            }
        
        items = self._parse_checklist(checklist_file)
        total = len(items)
        checked = sum(1 for item in items if item['checked'])
        
        # 진행 상황 저장
        key = f"{role}_{phase}" if role else phase
        self.progress[key] = {
            'total': total,
            'checked': checked,
            'percentage': (checked / total * 100) if total > 0 else 0,
            'last_updated': datetime.now().isoformat()
        }
        self._save_progress()
        
        return {
            'phase': phase,
            'role': role,
            'total': total,
            'checked': checked,
            'unchecked': total - checked,
            'percentage': (checked / total * 100) if total > 0 else 0,
            'items': items
        }
    
    def get_progress_summary(self) -> Dict:
        """전체 진행 상황 요약"""
        if not self.progress:
            return {'message': '진행 상황이 없습니다.'}
        
        summary = {
            'total_phases': len(self.progress),
            'phases': []
        }
        
        for key, data in self.progress.items():
            summary['phases'].append({
                'key': key,
                'checked': data['checked'],
                'total': data['total'],
                'percentage': data['percentage'],
                'last_updated': data['last_updated']
            })
        
        return summary
    
    def print_report(self, result: Dict):
        """검증 결과 리포트 출력"""
        if 'error' in result:
            print(f"❌ 오류: {result['error']}")
            return
        
        print("\n" + "="*60)
        print(f"체크리스트 검증 리포트")
        print("="*60)
        print(f"단계: {result['phase']}")
        if result.get('role'):
            print(f"역할: {result['role']}")
        print(f"전체 항목: {result['total']}")
        print(f"완료 항목: {result['checked']}")
        print(f"미완료 항목: {result['unchecked']}")
        print(f"진행률: {result['percentage']:.1f}%")
        print("="*60)
        
        # 진행률 바
        bar_length = 40
        filled = int(bar_length * result['percentage'] / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"[{bar}] {result['percentage']:.1f}%")
        
        # 미완료 항목 목록
        unchecked_items = [item for item in result['items'] if not item['checked']]
        if unchecked_items:
            print(f"\n⚠️  미완료 항목 ({len(unchecked_items)}개):")
            for item in unchecked_items[:10]:  # 최대 10개만 표시
                section = f"[{item['section']}] " if item['section'] else ""
                print(f"  - {section}{item['text']}")
            if len(unchecked_items) > 10:
                print(f"  ... 외 {len(unchecked_items) - 10}개 항목")
        
        print()

def main():
    parser = argparse.ArgumentParser(
        description='AI 윤리 체크리스트 검증 도구',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 개발 단계 체크리스트 검증
  python checklist-validator.py --phase development
  
  # 개발자 역할의 개발 단계 체크리스트 검증
  python checklist-validator.py --role developer --phase development
  
  # 전체 진행 상황 요약
  python checklist-validator.py --summary
        """
    )
    
    parser.add_argument(
        '--phase',
        choices=['pre-project', 'development', 'testing', 'pre-deployment', 'post-deployment'],
        help='검증할 프로젝트 단계'
    )
    
    parser.add_argument(
        '--role',
        choices=['developer', 'data-scientist', 'ml-engineer', 'project-manager', 'qa-tester', 'product-manager'],
        help='역할 (선택사항)'
    )
    
    parser.add_argument(
        '--summary',
        action='store_true',
        help='전체 진행 상황 요약 출력'
    )
    
    parser.add_argument(
        '--checklist-dir',
        default='checklists',
        help='체크리스트 디렉토리 경로 (기본값: checklists)'
    )
    
    args = parser.parse_args()
    
    validator = ChecklistValidator(checklist_dir=args.checklist_dir)
    
    if args.summary:
        summary = validator.get_progress_summary()
        print("\n" + "="*60)
        print("전체 진행 상황 요약")
        print("="*60)
        for phase in summary.get('phases', []):
            print(f"\n{phase['key']}:")
            print(f"  진행률: {phase['percentage']:.1f}% ({phase['checked']}/{phase['total']})")
            print(f"  마지막 업데이트: {phase['last_updated']}")
        print()
    elif args.phase:
        result = validator.validate_checklist(args.phase, args.role)
        validator.print_report(result)
    else:
        parser.print_help()

if __name__ == '__main__':
    main()

