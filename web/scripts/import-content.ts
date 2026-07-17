import { db } from '../src/db';
import { 
  subjects, 
  chapters, 
  documents, 
  sections, 
  knowledgePoints, 
  questions, 
  questionOptions,
  sourceReferences 
} from '../src/db/schema';
import fs from 'fs';
import path from 'path';
import { parse } from 'csv-parse/sync';

const DATA_DIR = path.resolve(__dirname, '../../data');

interface ImportStats {
  inserted: number;
  updated: number;
  skipped: number;
  failed: number;
}

async function importSubjects(): Promise<ImportStats> {
  const stats: ImportStats = { inserted: 0, updated: 0, skipped: 0, failed: 0 };
  
  const subjectData = [
    { id: 'comprehensive', title: '综合知识', description: '上午选择题考试内容' },
    { id: 'case-analysis', title: '案例分析', description: '下午案例分析题考试内容' },
    { id: 'essay', title: '论文', description: '下午论文写作考试内容' },
  ];
  
  for (const subject of subjectData) {
    try {
      await db.insert(subjects).values(subject)
        .onConflictDoUpdate({
          target: subjects.id,
          set: { title: subject.title, description: subject.description },
        });
      stats.inserted++;
    } catch (error) {
      console.error(`Failed to import subject ${subject.id}:`, error);
      stats.failed++;
    }
  }
  
  return stats;
}

async function importChapters(): Promise<ImportStats> {
  const stats: ImportStats = { inserted: 0, updated: 0, skipped: 0, failed: 0 };
  
  const configPath = path.resolve(__dirname, '../../pipeline/config/course_outline.yml');
  if (!fs.existsSync(configPath)) {
    console.log('Course outline config not found, skipping chapters import');
    return stats;
  }
  
  // 简化的章节导入
  const chapterData = [
    { id: 'computer-system', subjectId: 'comprehensive', title: '计算机系统基础', orderIndex: 1 },
    { id: 'software-engineering', subjectId: 'comprehensive', title: '软件工程', orderIndex: 2 },
    { id: 'architecture-design', subjectId: 'comprehensive', title: '软件架构设计', orderIndex: 3 },
    { id: 'database', subjectId: 'comprehensive', title: '数据库系统', orderIndex: 4 },
    { id: 'network-security', subjectId: 'comprehensive', title: '网络与信息安全', orderIndex: 5 },
    { id: 'project-management', subjectId: 'comprehensive', title: '项目管理', orderIndex: 6 },
    { id: 'system-analysis', subjectId: 'comprehensive', title: '系统分析', orderIndex: 7 },
    { id: 'system-design', subjectId: 'comprehensive', title: '系统设计', orderIndex: 8 },
    { id: 'software-quality', subjectId: 'comprehensive', title: '软件质量', orderIndex: 9 },
    { id: 'legal-regulations', subjectId: 'comprehensive', title: '法律法规与标准', orderIndex: 10 },
    { id: 'mathematics', subjectId: 'comprehensive', title: '数学与经济管理', orderIndex: 11 },
    { id: 'architecture-case', subjectId: 'case-analysis', title: '软件架构设计案例', orderIndex: 1 },
    { id: 'database-case', subjectId: 'case-analysis', title: '数据库设计案例', orderIndex: 2 },
    { id: 'security-case', subjectId: 'case-analysis', title: '系统安全案例', orderIndex: 3 },
    { id: 'web-case', subjectId: 'case-analysis', title: 'Web应用案例', orderIndex: 4 },
    { id: 'embedded-case', subjectId: 'case-analysis', title: '嵌入式系统案例', orderIndex: 5 },
    { id: 'essay-method', subjectId: 'essay', title: '论文写作方法', orderIndex: 1 },
    { id: 'essay-topics', subjectId: 'essay', title: '论文专题', orderIndex: 2 },
    { id: 'essay-examples', subjectId: 'essay', title: '论文范文', orderIndex: 3 },
  ];
  
  for (const chapter of chapterData) {
    try {
      await db.insert(chapters).values(chapter)
        .onConflictDoUpdate({
          target: chapters.id,
          set: { title: chapter.title, orderIndex: chapter.orderIndex },
        });
      stats.inserted++;
    } catch (error) {
      console.error(`Failed to import chapter ${chapter.id}:`, error);
      stats.failed++;
    }
  }
  
  return stats;
}

async function importDocuments(): Promise<ImportStats> {
  const stats: ImportStats = { inserted: 0, updated: 0, skipped: 0, failed: 0 };
  
  const manifestPath = path.resolve(DATA_DIR, 'manifest/materials_manifest.jsonl');
  if (!fs.existsSync(manifestPath)) {
    console.log('Materials manifest not found, skipping documents import');
    return stats;
  }
  
  const content = fs.readFileSync(manifestPath, 'utf-8');
  const lines = content.split('\n').filter(line => line.trim());
  
  for (const line of lines) {
    try {
      const doc = JSON.parse(line);
      await db.insert(documents).values({
        id: doc.file_id,
        title: doc.filename,
        sourcePath: doc.relative_path,
        fileType: doc.file_type,
        pageCount: 0,
        characterCount: 0,
        parseStatus: doc.parse_status,
      }).onConflictDoNothing();
      stats.inserted++;
    } catch (error) {
      stats.failed++;
    }
  }
  
  return stats;
}

async function importSections(): Promise<ImportStats> {
  const stats: ImportStats = { inserted: 0, updated: 0, skipped: 0, failed: 0 };
  
  const structuredDir = path.resolve(DATA_DIR, 'structured');
  if (!fs.existsSync(structuredDir)) {
    console.log('Structured data directory not found, skipping sections import');
    return stats;
  }
  
  // 遍历所有 sections.jsonl 文件
  for (const docDir of fs.readdirSync(structuredDir)) {
    const sectionsPath = path.join(structuredDir, docDir, 'sections.jsonl');
    if (!fs.existsSync(sectionsPath)) continue;
    
    const content = fs.readFileSync(sectionsPath, 'utf-8');
    const lines = content.split('\n').filter(line => line.trim());
    
    for (const line of lines) {
      try {
        const sec = JSON.parse(line);
        await db.insert(sections).values({
          id: sec.section_id,
          documentId: sec.document_id,
          chapterId: sec.predicted_chapter,
          title: sec.title,
          headingLevel: sec.heading_level,
          contentMarkdown: sec.content_markdown,
          orderIndex: sec.order_index,
          sourcePageStart: sec.source_page_start,
          sourcePageEnd: sec.source_page_end,
          contentType: sec.content_type,
          reviewStatus: sec.review_status,
        }).onConflictDoNothing();
        stats.inserted++;
      } catch (error) {
        stats.failed++;
      }
    }
  }
  
  return stats;
}

async function importKnowledgePoints(): Promise<ImportStats> {
  const stats: ImportStats = { inserted: 0, updated: 0, skipped: 0, failed: 0 };
  
  const kpsPath = path.resolve(DATA_DIR, 'structured/knowledge_points.jsonl');
  if (!fs.existsSync(kpsPath)) {
    console.log('Knowledge points file not found, skipping');
    return stats;
  }
  
  const content = fs.readFileSync(kpsPath, 'utf-8');
  const lines = content.split('\n').filter(line => line.trim());
  
  // 获取所有有效的 section IDs
  const validSections = await db.select({ id: sections.id }).from(sections);
  const validSectionIds = new Set(validSections.map(s => s.id));
  
  for (const line of lines) {
    try {
      const kp = JSON.parse(line);
      
      // 检查 sectionId 是否存在
      let sectionId = null;
      if (kp.section_id && validSectionIds.has(kp.section_id)) {
        sectionId = kp.section_id;
      }
      
      await db.insert(knowledgePoints).values({
        id: kp.knowledge_point_id,
        title: kp.title,
        subjectId: kp.subject_id,
        chapterId: kp.chapter_id,
        sectionId: sectionId,
        summary: kp.summary,
        contentMarkdown: kp.content_markdown,
        importance: kp.importance,
        difficulty: kp.difficulty,
        tags: JSON.stringify(kp.tags),
        examPoints: JSON.stringify(kp.exam_points),
        reviewStatus: kp.review_status,
      }).onConflictDoNothing();
      stats.inserted++;
    } catch (error) {
      console.error(`Failed to import knowledge point:`, error);
      stats.failed++;
    }
  }
  
  return stats;
}

async function importQuestions(): Promise<ImportStats> {
  const stats: ImportStats = { inserted: 0, updated: 0, skipped: 0, failed: 0 };
  
  const questionsPath = path.resolve(DATA_DIR, 'questions/questions.jsonl');
  if (!fs.existsSync(questionsPath)) {
    console.log('Questions file not found, skipping');
    return stats;
  }
  
  const content = fs.readFileSync(questionsPath, 'utf-8');
  const lines = content.split('\n').filter(line => line.trim());
  
  for (const line of lines) {
    try {
      const q = JSON.parse(line);
      await db.insert(questions).values({
        id: q.question_id,
        questionType: q.question_type,
        sourceType: q.source_type,
        year: q.year,
        subjectId: q.subject_id,
        questionText: q.question_text,
        correctAnswer: JSON.stringify(q.correct_answer),
        analysis: q.analysis,
        difficulty: q.difficulty,
        reviewStatus: q.review_status,
      }).onConflictDoNothing();
      
      // 导入选项
      if (q.options && q.options.length > 0) {
        for (const option of q.options) {
          await db.insert(questionOptions).values({
            questionId: q.question_id,
            key: option.key,
            text: option.text,
          }).onConflictDoNothing();
        }
      }
      
      stats.inserted++;
    } catch (error) {
      stats.failed++;
    }
  }
  
  return stats;
}

async function main() {
  console.log('Starting data import...\n');
  
  console.log('1. Importing subjects...');
  const subjectStats = await importSubjects();
  console.log(`   Subjects: ${subjectStats.inserted} inserted, ${subjectStats.failed} failed\n`);
  
  console.log('2. Importing chapters...');
  const chapterStats = await importChapters();
  console.log(`   Chapters: ${chapterStats.inserted} inserted, ${chapterStats.failed} failed\n`);
  
  console.log('3. Importing documents...');
  const docStats = await importDocuments();
  console.log(`   Documents: ${docStats.inserted} inserted, ${docStats.failed} failed\n`);
  
  console.log('4. Importing sections...');
  const sectionStats = await importSections();
  console.log(`   Sections: ${sectionStats.inserted} inserted, ${sectionStats.failed} failed\n`);
  
  console.log('5. Importing knowledge points...');
  const kpStats = await importKnowledgePoints();
  console.log(`   Knowledge Points: ${kpStats.inserted} inserted, ${kpStats.failed} failed\n`);
  
  console.log('6. Importing questions...');
  const questionStats = await importQuestions();
  console.log(`   Questions: ${questionStats.inserted} inserted, ${questionStats.failed} failed\n`);
  
  console.log('Import completed!');
}

main().catch(console.error);
