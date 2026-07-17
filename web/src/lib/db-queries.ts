import { db } from '@/db';
import { 
  subjects, 
  chapters, 
  knowledgePoints, 
  questions, 
  learningRecords,
  wrongQuestions,
  notes,
  sections,
  questionAttempts
} from '@/db/schema';
import { eq, and, desc, count, sql } from 'drizzle-orm';

// 获取所有科目
export async function getSubjects() {
  return db.select().from(subjects);
}

// 获取科目的章节
export async function getChaptersBySubject(subjectId: string) {
  return db.select()
    .from(chapters)
    .where(eq(chapters.subjectId, subjectId))
    .orderBy(chapters.orderIndex);
}

// 获取章节的知识点
export async function getKnowledgePointsByChapter(chapterId: string) {
  return db.select()
    .from(knowledgePoints)
    .where(eq(knowledgePoints.chapterId, chapterId))
    .orderBy(knowledgePoints.importance);
}

// 获取单个知识点
export async function getKnowledgePoint(id: string) {
  const result = await db.select()
    .from(knowledgePoints)
    .where(eq(knowledgePoints.id, id))
    .limit(1);
  return result[0] || null;
}

// 获取知识点的学习记录
export async function getLearningRecord(userId: string, knowledgePointId: string) {
  const result = await db.select()
    .from(learningRecords)
    .where(and(
      eq(learningRecords.userId, userId),
      eq(learningRecords.knowledgePointId, knowledgePointId)
    ))
    .limit(1);
  return result[0] || null;
}

// 更新学习状态
export async function updateLearningStatus(
  userId: string, 
  knowledgePointId: string, 
  status: string,
  progressPercent: number = 0
) {
  const existing = await getLearningRecord(userId, knowledgePointId);
  
  if (existing) {
    await db.update(learningRecords)
      .set({
        status,
        progressPercent,
        lastStudiedAt: new Date().toISOString(),
        completedAt: status === 'completed' ? new Date().toISOString() : existing.completedAt,
      })
      .where(eq(learningRecords.id, existing.id));
  } else {
    await db.insert(learningRecords).values({
      userId,
      knowledgePointId,
      status,
      progressPercent,
      firstStartedAt: new Date().toISOString(),
      lastStudiedAt: new Date().toISOString(),
      completedAt: status === 'completed' ? new Date().toISOString() : null,
    });
  }
}

// 获取题目列表
export async function getQuestions(options?: {
  subjectId?: string;
  chapterId?: string;
  questionType?: string;
  limit?: number;
  offset?: number;
}) {
  let query = db.select().from(questions);
  
  // TODO: 添加过滤条件
  
  return query.limit(options?.limit || 20).offset(options?.offset || 0);
}

// 获取单个题目
export async function getQuestion(id: string) {
  const result = await db.select()
    .from(questions)
    .where(eq(questions.id, id))
    .limit(1);
  return result[0] || null;
}

// 记录答题
export async function recordQuestionAttempt(
  userId: string,
  questionId: string,
  submittedAnswer: string,
  isCorrect: boolean,
  durationSeconds: number
) {
  await db.insert(questionAttempts).values({
    userId,
    questionId,
    submittedAnswer,
    isCorrect,
    durationSeconds,
  });
  
  // 如果答错，加入错题本
  if (!isCorrect) {
    await addToWrongQuestions(userId, questionId);
  }
}

// 添加到错题本
export async function addToWrongQuestions(userId: string, questionId: string) {
  const existing = await db.select()
    .from(wrongQuestions)
    .where(and(
      eq(wrongQuestions.userId, userId),
      eq(wrongQuestions.questionId, questionId)
    ))
    .limit(1);
  
  if (existing.length > 0 && existing[0]) {
    await db.update(wrongQuestions)
      .set({
        wrongCount: (existing[0].wrongCount || 0) + 1,
        lastWrongAt: new Date().toISOString(),
      })
      .where(eq(wrongQuestions.id, existing[0].id));
  } else {
    await db.insert(wrongQuestions).values({
      userId,
      questionId,
      wrongCount: 1,
      lastWrongAt: new Date().toISOString(),
    });
  }
}

// 获取错题本
export async function getWrongQuestions(userId: string) {
  return db.select({
    id: wrongQuestions.id,
    questionId: wrongQuestions.questionId,
    wrongCount: wrongQuestions.wrongCount,
    wrongReason: wrongQuestions.wrongReason,
    reviewStatus: wrongQuestions.reviewStatus,
    nextReviewAt: wrongQuestions.nextReviewAt,
    lastWrongAt: wrongQuestions.lastWrongAt,
    questionText: questions.questionText,
    questionType: questions.questionType,
  })
    .from(wrongQuestions)
    .leftJoin(questions, eq(wrongQuestions.questionId, questions.id))
    .where(eq(wrongQuestions.userId, userId))
    .orderBy(desc(wrongQuestions.lastWrongAt));
}

// 获取笔记
export async function getNotes(userId: string, knowledgePointId?: string) {
  if (knowledgePointId) {
    return db.select()
      .from(notes)
      .where(and(
        eq(notes.userId, userId),
        eq(notes.knowledgePointId, knowledgePointId)
      ))
      .orderBy(desc(notes.updatedAt));
  }
  
  return db.select()
    .from(notes)
    .where(eq(notes.userId, userId))
    .orderBy(desc(notes.updatedAt));
}

// 保存笔记
export async function saveNote(
  userId: string,
  knowledgePointId: string,
  content: string
) {
  const existing = await db.select()
    .from(notes)
    .where(and(
      eq(notes.userId, userId),
      eq(notes.knowledgePointId, knowledgePointId)
    ))
    .limit(1);
  
  if (existing.length > 0) {
    await db.update(notes)
      .set({
        content,
        updatedAt: new Date().toISOString(),
      })
      .where(eq(notes.id, existing[0].id));
  } else {
    await db.insert(notes).values({
      userId,
      knowledgePointId,
      content,
    });
  }
}

// 获取学习统计
export async function getLearningStats(userId: string) {
  // 总知识点数
  const totalKP = await db.select({ count: count() }).from(knowledgePoints);
  
  // 已完成知识点数
  const completedKP = await db.select({ count: count() })
    .from(learningRecords)
    .where(and(
      eq(learningRecords.userId, userId),
      eq(learningRecords.status, 'completed')
    ));
  
  // 学习中知识点数
  const learningKP = await db.select({ count: count() })
    .from(learningRecords)
    .where(and(
      eq(learningRecords.userId, userId),
      eq(learningRecords.status, 'learning')
    ));
  
  // 错题数
  const wrongCount = await db.select({ count: count() })
    .from(wrongQuestions)
    .where(eq(wrongQuestions.userId, userId));
  
  // 答题总数
  const totalAttempts = await db.select({ count: count() })
    .from(questionAttempts)
    .where(eq(questionAttempts.userId, userId));
  
  // 正确答题数
  const correctAttempts = await db.select({ count: count() })
    .from(questionAttempts)
    .where(and(
      eq(questionAttempts.userId, userId),
      eq(questionAttempts.isCorrect, true)
    ));
  
  return {
    totalKnowledgePoints: totalKP[0].count,
    completedKnowledgePoints: completedKP[0].count,
    learningKnowledgePoints: learningKP[0].count,
    wrongQuestionCount: wrongCount[0].count,
    totalAttempts: totalAttempts[0].count,
    correctAttempts: correctAttempts[0].count,
    accuracy: totalAttempts[0].count > 0 
      ? Math.round((correctAttempts[0].count / totalAttempts[0].count) * 100) 
      : 0,
  };
}

// 获取章节统计
export async function getChapterStats(chapterId: string, userId: string) {
  const totalKP = await db.select({ count: count() })
    .from(knowledgePoints)
    .where(eq(knowledgePoints.chapterId, chapterId));
  
  const completedKP = await db.select({ count: count() })
    .from(learningRecords)
    .leftJoin(knowledgePoints, eq(learningRecords.knowledgePointId, knowledgePoints.id))
    .where(and(
      eq(knowledgePoints.chapterId, chapterId),
      eq(learningRecords.userId, userId),
      eq(learningRecords.status, 'completed')
    ));
  
  return {
    total: totalKP[0].count,
    completed: completedKP[0].count,
    progress: totalKP[0].count > 0 
      ? Math.round((completedKP[0].count / totalKP[0].count) * 100) 
      : 0,
  };
}
