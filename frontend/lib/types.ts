/**
 * 统一类型定义
 * 所有组件共享的数据结构
 */

// ============ 项目相关 ============

export interface Project {
  slug: string;
  topic: string;
  created_at: string | null;
  sections_count: number;
  has_videos: boolean;
}

export interface ProjectListResponse {
  projects: Project[];
  total: number;
}

// ============ Storyboard 相关 ============

export interface Section {
  id: string;
  title: string;
  lecture_lines: string[];
  animations: string[];
}

export interface Storyboard {
  topic: string;
  sections: Section[];
}

// ============ 视频相关 ============

export interface VideoInfo {
  name: string;
  section: string;
  path: string;
  full_path?: string;
}

export interface ScriptInfo {
  name: string;
  path: string;
  content: string;
}

// ============ 生成相关 ============

export interface GenerateRequest {
  prompt?: string;
  topic?: string;
  render?: boolean;
}

export interface GenerateResponse {
  success: boolean;
  message: string;
  slug: string | null;
  task_id: string | null;
}

// ============ 日志相关 ============

export interface LogMessage {
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: Date;
}

export type GenerateStatus = 'idle' | 'running' | 'completed' | 'failed';

// ============ Refiner 相关 ============

export interface CritiqueResponse {
  success: boolean;
  has_issues: boolean;
  suggestion: string | null;
  video_path: string | null;
}

export interface RefineRequest {
  section_id: string;
  custom_suggestion?: string;
}

export interface RefineResponse {
  success: boolean;
  message: string;
  suggestion: string | null;
  refined: boolean;
}

// ============ Tab 相关 ============

export type TabType = 'videos' | 'storyboard' | 'scripts';
