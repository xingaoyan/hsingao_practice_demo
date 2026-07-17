import { db } from '../src/db';
import { 
  subjects, 
  chapters, 
  documents, 
  sections, 
  knowledgePoints, 
  questions,
  sourceReferences 
} from '../src/db/schema';
import { count, eq, isNull } from 'drizzle-orm';

interface ValidationResult {
  check: string;
  status: 'pass' | 'fail' | 'warning';
  message: string;
  count?: number;
}

async function validateImport(): Promise<ValidationResult[]> {
  const results: ValidationResult[] = [];
  
  // 1. 检查科目数量
  const subjectCount = await db.select({ count: count() }).from(subjects);
  results.push({
    check: '科目数量',
    status: subjectCount[0].count >= 3 ? 'pass' : 'fail',
    message: `数据库中有 ${subjectCount[0].count} 个科目`,
    count: subjectCount[0].count,
  });
  
  // 2. 检查章节数量
  const chapterCount = await db.select({ count: count() }).from(chapters);
  results.push({
    check: '章节数量',
    status: chapterCount[0].count >= 10 ? 'pass' : 'warning',
    message: `数据库中有 ${chapterCount[0].count} 个章节`,
    count: chapterCount[0].count,
  });
  
  // 3. 检查知识点数量
  const kpCount = await db.select({ count: count() }).from(knowledgePoints);
  results.push({
    check: '知识点数量',
    status: kpCount[0].count >= 20 ? 'pass' : 'warning',
    message: `数据库中有 ${kpCount[0].count} 个知识点`,
    count: kpCount[0].count,
  });
  
  // 4. 检查题目数量
  const questionCount = await db.select({ count: count() }).from(questions);
  results.push({
    check: '题目数量',
    status: questionCount[0].count >= 5 ? 'pass' : 'warning',
    message: `数据库中有 ${questionCount[0].count} 道题目`,
    count: questionCount[0].count,
  });
  
  // 5. 检查孤立知识点（没有关联章节的）
  const orphanKPs = await db.select({ count: count() })
    .from(knowledgePoints)
    .where(isNull(knowledgePoints.chapterId));
  results.push({
    check: '孤立知识点',
    status: orphanKPs[0].count === 0 ? 'pass' : 'warning',
    message: `有 ${orphanKPs[0].count} 个知识点没有关联章节`,
    count: orphanKPs[0].count,
  });
  
  // 6. 检查文档数量
  const docCount = await db.select({ count: count() }).from(documents);
  results.push({
    check: '文档数量',
    status: docCount[0].count > 0 ? 'pass' : 'warning',
    message: `数据库中有 ${docCount[0].count} 个文档`,
    count: docCount[0].count,
  });
  
  return results;
}

async function main() {
  console.log('Validating imported data...\n');
  
  const results = await validateImport();
  
  let passCount = 0;
  let failCount = 0;
  let warningCount = 0;
  
  for (const result of results) {
    const icon = result.status === 'pass' ? '✓' : result.status === 'fail' ? '✗' : '⚠';
    console.log(`${icon} ${result.check}: ${result.message}`);
    
    if (result.status === 'pass') passCount++;
    else if (result.status === 'fail') failCount++;
    else warningCount++;
  }
  
  console.log(`\nSummary: ${passCount} passed, ${failCount} failed, ${warningCount} warnings`);
  
  if (failCount > 0) {
    process.exit(1);
  }
}

main().catch(console.error);
