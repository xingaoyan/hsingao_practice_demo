import { sqliteTable, text, integer, real } from 'drizzle-orm/sqlite-core';
import { relations } from 'drizzle-orm';

// 科目表
export const subjects = sqliteTable('subjects', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  description: text('description'),
});

// 章节表
export const chapters = sqliteTable('chapters', {
  id: text('id').primaryKey(),
  subjectId: text('subject_id').notNull().references(() => subjects.id),
  title: text('title').notNull(),
  description: text('description'),
  orderIndex: integer('order_index').default(0),
});

// 文档表
export const documents = sqliteTable('documents', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  sourcePath: text('source_path'),
  fileType: text('file_type'),
  pageCount: integer('page_count'),
  characterCount: integer('character_count'),
  parseStatus: text('parse_status').default('pending'),
});

// 章节内容表
export const sections = sqliteTable('sections', {
  id: text('id').primaryKey(),
  documentId: text('document_id').notNull().references(() => documents.id),
  chapterId: text('chapter_id').references(() => chapters.id),
  title: text('title').notNull(),
  headingLevel: integer('heading_level'),
  contentMarkdown: text('content_markdown'),
  orderIndex: integer('order_index').default(0),
  sourcePageStart: integer('source_page_start'),
  sourcePageEnd: integer('source_page_end'),
  contentType: text('content_type').default('教材正文'),
  reviewStatus: text('review_status').default('pending'),
});

// 知识点表
export const knowledgePoints = sqliteTable('knowledge_points', {
  id: text('id').primaryKey(),
  title: text('title').notNull(),
  subjectId: text('subject_id').notNull().references(() => subjects.id),
  chapterId: text('chapter_id').notNull().references(() => chapters.id),
  sectionId: text('section_id').references(() => sections.id),
  summary: text('summary'),
  contentMarkdown: text('content_markdown'),
  importance: integer('importance').default(3),
  difficulty: integer('difficulty').default(3),
  tags: text('tags'), // JSON array
  examPoints: text('exam_points'), // JSON array
  reviewStatus: text('review_status').default('pending'),
});

// 知识点关系表
export const knowledgePointRelations = sqliteTable('knowledge_point_relations', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  sourceId: text('source_id').notNull().references(() => knowledgePoints.id),
  targetId: text('target_id').notNull().references(() => knowledgePoints.id),
  relationType: text('relation_type').notNull(), // prerequisite, related, compare
});

// 来源引用表
export const sourceReferences = sqliteTable('source_references', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  knowledgePointId: text('knowledge_point_id').references(() => knowledgePoints.id),
  documentId: text('document_id').notNull().references(() => documents.id),
  pageStart: integer('page_start'),
  pageEnd: integer('page_end'),
});

// 题目表
export const questions = sqliteTable('questions', {
  id: text('id').primaryKey(),
  questionType: text('question_type').notNull(), // single_choice, multiple_choice, true_false, short_answer
  sourceType: text('source_type').notNull(), // past_exam, material_exercise, ai_generated, manual
  year: integer('year'),
  subjectId: text('subject_id').references(() => subjects.id),
  questionText: text('question_text').notNull(),
  correctAnswer: text('correct_answer'), // JSON array
  analysis: text('analysis'),
  difficulty: integer('difficulty').default(3),
  reviewStatus: text('review_status').default('pending'),
});

// 题目选项表
export const questionOptions = sqliteTable('question_options', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  questionId: text('question_id').notNull().references(() => questions.id),
  key: text('key').notNull(), // A, B, C, D
  text: text('text').notNull(),
});

// 题目知识点关联表
export const questionKnowledgePoints = sqliteTable('question_knowledge_points', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  questionId: text('question_id').notNull().references(() => questions.id),
  knowledgePointId: text('knowledge_point_id').notNull().references(() => knowledgePoints.id),
});

// 学习记录表
export const learningRecords = sqliteTable('learning_records', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: text('user_id').notNull(),
  knowledgePointId: text('knowledge_point_id').notNull().references(() => knowledgePoints.id),
  status: text('status').default('not_started'), // not_started, learning, completed, reviewing
  progressPercent: integer('progress_percent').default(0),
  firstStartedAt: text('first_started_at'),
  lastStudiedAt: text('last_studied_at'),
  completedAt: text('completed_at'),
});

// 答题记录表
export const questionAttempts = sqliteTable('question_attempts', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: text('user_id').notNull(),
  questionId: text('question_id').notNull().references(() => questions.id),
  submittedAnswer: text('submitted_answer'),
  isCorrect: integer('is_correct', { mode: 'boolean' }),
  durationSeconds: integer('duration_seconds'),
  createdAt: text('created_at').default('CURRENT_TIMESTAMP'),
});

// 错题本表
export const wrongQuestions = sqliteTable('wrong_questions', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: text('user_id').notNull(),
  questionId: text('question_id').notNull().references(() => questions.id),
  wrongCount: integer('wrong_count').default(1),
  wrongReason: text('wrong_reason'),
  reviewStatus: text('review_status').default('pending'), // pending, mastered
  nextReviewAt: text('next_review_at'),
  lastWrongAt: text('last_wrong_at').default('CURRENT_TIMESTAMP'),
});

// 笔记表
export const notes = sqliteTable('notes', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: text('user_id').notNull(),
  knowledgePointId: text('knowledge_point_id').notNull().references(() => knowledgePoints.id),
  content: text('content'),
  createdAt: text('created_at').default('CURRENT_TIMESTAMP'),
  updatedAt: text('updated_at').default('CURRENT_TIMESTAMP'),
});

// 收藏表
export const favorites = sqliteTable('favorites', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: text('user_id').notNull(),
  itemType: text('item_type').notNull(), // knowledge_point, question
  itemId: text('item_id').notNull(),
  createdAt: text('created_at').default('CURRENT_TIMESTAMP'),
});

// 学习会话表
export const studySessions = sqliteTable('study_sessions', {
  id: integer('id').primaryKey({ autoIncrement: true }),
  userId: text('user_id').notNull(),
  knowledgePointId: text('knowledge_point_id').references(() => knowledgePoints.id),
  startTime: text('start_time').notNull(),
  endTime: text('end_time'),
  durationSeconds: integer('duration_seconds'),
});

// 关系定义
export const subjectsRelations = relations(subjects, ({ many }) => ({
  chapters: many(chapters),
}));

export const chaptersRelations = relations(chapters, ({ one, many }) => ({
  subject: one(subjects, {
    fields: [chapters.subjectId],
    references: [subjects.id],
  }),
  sections: many(sections),
  knowledgePoints: many(knowledgePoints),
}));

export const documentsRelations = relations(documents, ({ many }) => ({
  sections: many(sections),
}));

export const sectionsRelations = relations(sections, ({ one }) => ({
  document: one(documents, {
    fields: [sections.documentId],
    references: [documents.id],
  }),
  chapter: one(chapters, {
    fields: [sections.chapterId],
    references: [chapters.id],
  }),
}));

export const knowledgePointsRelations = relations(knowledgePoints, ({ one, many }) => ({
  subject: one(subjects, {
    fields: [knowledgePoints.subjectId],
    references: [subjects.id],
  }),
  chapter: one(chapters, {
    fields: [knowledgePoints.chapterId],
    references: [chapters.id],
  }),
  section: one(sections, {
    fields: [knowledgePoints.sectionId],
    references: [sections.id],
  }),
  sourceReferences: many(sourceReferences),
}));

export const questionsRelations = relations(questions, ({ one, many }) => ({
  subject: one(subjects, {
    fields: [questions.subjectId],
    references: [subjects.id],
  }),
  options: many(questionOptions),
  knowledgePoints: many(questionKnowledgePoints),
}));
