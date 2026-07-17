CREATE TABLE `chapters` (
	`id` text PRIMARY KEY NOT NULL,
	`subject_id` text NOT NULL,
	`title` text NOT NULL,
	`description` text,
	`order_index` integer DEFAULT 0,
	FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `documents` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`source_path` text,
	`file_type` text,
	`page_count` integer,
	`character_count` integer,
	`parse_status` text DEFAULT 'pending'
);
--> statement-breakpoint
CREATE TABLE `favorites` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`user_id` text NOT NULL,
	`item_type` text NOT NULL,
	`item_id` text NOT NULL,
	`created_at` text DEFAULT 'CURRENT_TIMESTAMP'
);
--> statement-breakpoint
CREATE TABLE `knowledge_point_relations` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`source_id` text NOT NULL,
	`target_id` text NOT NULL,
	`relation_type` text NOT NULL,
	FOREIGN KEY (`source_id`) REFERENCES `knowledge_points`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`target_id`) REFERENCES `knowledge_points`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `knowledge_points` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`subject_id` text NOT NULL,
	`chapter_id` text NOT NULL,
	`section_id` text,
	`summary` text,
	`content_markdown` text,
	`importance` integer DEFAULT 3,
	`difficulty` integer DEFAULT 3,
	`tags` text,
	`exam_points` text,
	`review_status` text DEFAULT 'pending',
	FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`chapter_id`) REFERENCES `chapters`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`section_id`) REFERENCES `sections`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `learning_records` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`user_id` text NOT NULL,
	`knowledge_point_id` text NOT NULL,
	`status` text DEFAULT 'not_started',
	`progress_percent` integer DEFAULT 0,
	`first_started_at` text,
	`last_studied_at` text,
	`completed_at` text,
	FOREIGN KEY (`knowledge_point_id`) REFERENCES `knowledge_points`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `notes` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`user_id` text NOT NULL,
	`knowledge_point_id` text NOT NULL,
	`content` text,
	`created_at` text DEFAULT 'CURRENT_TIMESTAMP',
	`updated_at` text DEFAULT 'CURRENT_TIMESTAMP',
	FOREIGN KEY (`knowledge_point_id`) REFERENCES `knowledge_points`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `question_attempts` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`user_id` text NOT NULL,
	`question_id` text NOT NULL,
	`submitted_answer` text,
	`is_correct` integer,
	`duration_seconds` integer,
	`created_at` text DEFAULT 'CURRENT_TIMESTAMP',
	FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `question_knowledge_points` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`question_id` text NOT NULL,
	`knowledge_point_id` text NOT NULL,
	FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`knowledge_point_id`) REFERENCES `knowledge_points`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `question_options` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`question_id` text NOT NULL,
	`key` text NOT NULL,
	`text` text NOT NULL,
	FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `questions` (
	`id` text PRIMARY KEY NOT NULL,
	`question_type` text NOT NULL,
	`source_type` text NOT NULL,
	`year` integer,
	`subject_id` text,
	`question_text` text NOT NULL,
	`correct_answer` text,
	`analysis` text,
	`difficulty` integer DEFAULT 3,
	`review_status` text DEFAULT 'pending',
	FOREIGN KEY (`subject_id`) REFERENCES `subjects`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `sections` (
	`id` text PRIMARY KEY NOT NULL,
	`document_id` text NOT NULL,
	`chapter_id` text,
	`title` text NOT NULL,
	`heading_level` integer,
	`content_markdown` text,
	`order_index` integer DEFAULT 0,
	`source_page_start` integer,
	`source_page_end` integer,
	`content_type` text DEFAULT '教材正文',
	`review_status` text DEFAULT 'pending',
	FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`chapter_id`) REFERENCES `chapters`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `source_references` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`knowledge_point_id` text,
	`document_id` text NOT NULL,
	`page_start` integer,
	`page_end` integer,
	FOREIGN KEY (`knowledge_point_id`) REFERENCES `knowledge_points`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`document_id`) REFERENCES `documents`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `study_sessions` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`user_id` text NOT NULL,
	`knowledge_point_id` text,
	`start_time` text NOT NULL,
	`end_time` text,
	`duration_seconds` integer,
	FOREIGN KEY (`knowledge_point_id`) REFERENCES `knowledge_points`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `subjects` (
	`id` text PRIMARY KEY NOT NULL,
	`title` text NOT NULL,
	`description` text
);
--> statement-breakpoint
CREATE TABLE `wrong_questions` (
	`id` integer PRIMARY KEY AUTOINCREMENT NOT NULL,
	`user_id` text NOT NULL,
	`question_id` text NOT NULL,
	`wrong_count` integer DEFAULT 1,
	`wrong_reason` text,
	`review_status` text DEFAULT 'pending',
	`next_review_at` text,
	`last_wrong_at` text DEFAULT 'CURRENT_TIMESTAMP',
	FOREIGN KEY (`question_id`) REFERENCES `questions`(`id`) ON UPDATE no action ON DELETE no action
);
