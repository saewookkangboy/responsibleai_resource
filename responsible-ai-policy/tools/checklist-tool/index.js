#!/usr/bin/env node

/**
 * Responsible AI 체크리스트 도구
 * 
 * 이 도구는 Responsible AI 체크리스트를 대화형으로 실행하거나
 * JSON 파일로 저장된 체크리스트를 검증합니다.
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import inquirer from 'inquirer';
import chalk from 'chalk';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// 체크리스트 항목
const checklistItems = {
    planning: {
        title: '기획 단계',
        items: [
            { id: 'p1', text: 'AI 사용 목적이 명확히 정의되었는가?', category: '목적 및 범위' },
            { id: 'p2', text: 'AI가 해결하려는 문제가 명확한가?', category: '목적 및 범위' },
            { id: 'p3', text: 'AI 사용이 필요한지 검토되었는가?', category: '목적 및 범위' },
            { id: 'p4', text: '윤리적 문제가 없는지 검토했는가?', category: '윤리적 검토' },
            { id: 'p5', text: '잠재적 해악을 식별했는가?', category: '윤리적 검토' },
            { id: 'p6', text: '관련 법규를 확인했는가?', category: '법적 검토' },
            { id: 'p7', text: '개인정보보호법을 준수하는가?', category: '법적 검토' },
            { id: 'p8', text: '사용자에게 미치는 영향을 분석했는가?', category: '사용자 영향' },
        ]
    },
    design: {
        title: '설계 단계',
        items: [
            { id: 'd1', text: '모듈화된 설계인가?', category: '아키텍처' },
            { id: 'd2', text: '오류 처리가 설계되었는가?', category: '아키텍처' },
            { id: 'd3', text: '모니터링이 설계되었는가?', category: '아키텍처' },
            { id: 'd4', text: '필요한 최소한의 데이터만 수집하는가?', category: '데이터' },
            { id: 'd5', text: '데이터 암호화 계획이 있는가?', category: '데이터' },
            { id: 'd6', text: '편향 방지가 고려되었는가?', category: '모델' },
            { id: 'd7', text: '설명 가능성이 고려되었는가?', category: '모델' },
            { id: 'd8', text: '보안 설계가 포함되었는가?', category: '보안' },
        ]
    },
    development: {
        title: '개발 단계',
        items: [
            { id: 'dev1', text: '다양한 데이터 소스를 사용하는가?', category: '데이터 준비' },
            { id: 'dev2', text: '데이터 품질을 검증했는가?', category: '데이터 준비' },
            { id: 'dev3', text: '편향 테스트를 수행했는가?', category: '모델 개발' },
            { id: 'dev4', text: '안전한 API를 구현했는가?', category: '시스템 구현' },
            { id: 'dev5', text: '입력 검증을 구현했는가?', category: '시스템 구현' },
            { id: 'dev6', text: '로깅을 구현했는가?', category: '시스템 구현' },
        ]
    },
    testing: {
        title: '테스트 단계',
        items: [
            { id: 't1', text: '단위 테스트를 작성했는가?', category: '기능 테스트' },
            { id: 't2', text: '통합 테스트를 수행했는가?', category: '기능 테스트' },
            { id: 't3', text: '편향 테스트를 수행했는가?', category: '윤리 테스트' },
            { id: 't4', text: '안전성 테스트를 수행했는가?', category: '윤리 테스트' },
            { id: 't5', text: '사용성 테스트를 수행했는가?', category: '사용자 테스트' },
        ]
    },
    deployment: {
        title: '배포 단계',
        items: [
            { id: 'dep1', text: '문서화를 완료했는가?', category: '배포 준비' },
            { id: 'dep2', text: '롤백 계획을 수립했는가?', category: '배포 준비' },
            { id: 'dep3', text: '모니터링을 설정했는가?', category: '배포' },
            { id: 'dep4', text: '피드백 채널을 구축했는가?', category: '배포' },
        ]
    },
    operations: {
        title: '운영 단계',
        items: [
            { id: 'o1', text: '성능을 모니터링하는가?', category: '모니터링' },
            { id: 'o2', text: '편향을 모니터링하는가?', category: '모니터링' },
            { id: 'o3', text: '정기적으로 업데이트하는가?', category: '유지보수' },
            { id: 'o4', text: '정기적으로 감사를 수행하는가?', category: '감사' },
        ]
    }
};

// 원칙별 체크리스트
const principleChecklist = {
    fairness: {
        title: '공정성 (Fairness)',
        items: [
            { id: 'f1', text: '다양한 그룹을 대표하는 데이터를 사용하는가?' },
            { id: 'f2', text: '편향 테스트를 수행했는가?' },
            { id: 'f3', text: '공정성 지표를 모니터링하는가?' },
        ]
    },
    transparency: {
        title: '투명성 (Transparency)',
        items: [
            { id: 'tr1', text: 'AI 사용을 명시하는가?' },
            { id: 'tr2', text: '의사결정 과정을 설명할 수 있는가?' },
            { id: 'tr3', text: '모델의 한계를 명시하는가?' },
        ]
    },
    privacy: {
        title: '프라이버시 (Privacy)',
        items: [
            { id: 'pr1', text: '최소한의 데이터만 수집하는가?' },
            { id: 'pr2', text: '데이터를 암호화하는가?' },
            { id: 'pr3', text: '사용자 동의를 획득하는가?' },
        ]
    }
};

class ChecklistTool {
    constructor() {
        this.results = {};
    }

    async runInteractive() {
        console.log(chalk.blue.bold('\n📋 Responsible AI 체크리스트 도구\n'));

        const { mode } = await inquirer.prompt([
            {
                type: 'list',
                name: 'mode',
                message: '체크리스트 모드를 선택하세요:',
                choices: [
                    { name: '개발 단계별 체크리스트', value: 'stages' },
                    { name: '원칙별 체크리스트', value: 'principles' },
                    { name: '전체 체크리스트', value: 'all' }
                ]
            }
        ]);

        if (mode === 'stages') {
            await this.runStageChecklist();
        } else if (mode === 'principles') {
            await this.runPrincipleChecklist();
        } else {
            await this.runAllChecklist();
        }

        await this.saveResults();
        this.printSummary();
    }

    async runStageChecklist() {
        const stages = Object.keys(checklistItems);
        
        for (const stage of stages) {
            const stageData = checklistItems[stage];
            console.log(chalk.yellow(`\n${stageData.title}`));
            
            const answers = await inquirer.prompt(
                stageData.items.map(item => ({
                    type: 'confirm',
                    name: item.id,
                    message: item.text,
                    default: false
                }))
            );

            this.results[stage] = answers;
        }
    }

    async runPrincipleChecklist() {
        const principles = Object.keys(principleChecklist);
        
        for (const principle of principles) {
            const principleData = principleChecklist[principle];
            console.log(chalk.yellow(`\n${principleData.title}`));
            
            const answers = await inquirer.prompt(
                principleData.items.map(item => ({
                    type: 'confirm',
                    name: item.id,
                    message: item.text,
                    default: false
                }))
            );

            this.results[principle] = answers;
        }
    }

    async runAllChecklist() {
        await this.runStageChecklist();
        await this.runPrincipleChecklist();
    }

    async saveResults() {
        const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
        const filename = `checklist-results-${timestamp}.json`;
        const filepath = path.join(process.cwd(), filename);

        const output = {
            timestamp: new Date().toISOString(),
            results: this.results,
            summary: this.calculateSummary()
        };

        fs.writeFileSync(filepath, JSON.stringify(output, null, 2));
        console.log(chalk.green(`\n✅ 결과가 저장되었습니다: ${filename}`));
    }

    calculateSummary() {
        const summary = {
            total: 0,
            passed: 0,
            failed: 0,
            percentage: 0
        };

        for (const stage in this.results) {
            const answers = this.results[stage];
            for (const key in answers) {
                summary.total++;
                if (answers[key]) {
                    summary.passed++;
                } else {
                    summary.failed++;
                }
            }
        }

        summary.percentage = summary.total > 0 
            ? Math.round((summary.passed / summary.total) * 100) 
            : 0;

        return summary;
    }

    printSummary() {
        const summary = this.calculateSummary();
        
        console.log(chalk.blue.bold('\n📊 체크리스트 요약\n'));
        console.log(`전체 항목: ${summary.total}`);
        console.log(chalk.green(`✅ 통과: ${summary.passed}`));
        console.log(chalk.red(`❌ 미통과: ${summary.failed}`));
        console.log(chalk.cyan(`완료율: ${summary.percentage}%`));

        if (summary.percentage === 100) {
            console.log(chalk.green.bold('\n🎉 모든 항목을 완료했습니다!'));
        } else if (summary.percentage >= 80) {
            console.log(chalk.yellow.bold('\n⚠️  대부분의 항목을 완료했습니다. 남은 항목을 확인하세요.'));
        } else {
            console.log(chalk.red.bold('\n🚨 많은 항목이 완료되지 않았습니다. 개선이 필요합니다.'));
        }
    }

    async checkFromFile(filepath) {
        if (!fs.existsSync(filepath)) {
            console.error(chalk.red(`파일을 찾을 수 없습니다: ${filepath}`));
            process.exit(1);
        }

        const data = JSON.parse(fs.readFileSync(filepath, 'utf-8'));
        this.results = data.results || data;
        
        this.printSummary();
    }
}

// CLI 실행
const tool = new ChecklistTool();
const args = process.argv.slice(2);

if (args.includes('--interactive') || args.length === 0) {
    tool.runInteractive().catch(console.error);
} else if (args.includes('--check')) {
    const fileIndex = args.indexOf('--check') + 1;
    const filepath = args[fileIndex] || 'checklist-results.json';
    tool.checkFromFile(filepath).catch(console.error);
} else {
    console.log(`
사용법:
  node index.js [옵션]

옵션:
  --interactive    대화형 모드로 체크리스트 실행 (기본값)
  --check [파일]   저장된 체크리스트 결과 확인

예제:
  node index.js --interactive
  node index.js --check checklist-results.json
    `);
}

