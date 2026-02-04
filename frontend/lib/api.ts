/**
 * API 客户端工具函数
 * 提供与后端 API 交互的封装
 */

const API_BASE_URL = '/api';

/**
 * 通用 API 请求函数
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...options,
    headers: {
      ...defaultHeaders,
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `API Error: ${response.status}`);
  }

  return response.json();
}

// ============ 项目相关 API ============

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

/**
 * 获取项目列表
 */
export async function getProjects(): Promise<ProjectListResponse> {
  return apiRequest<ProjectListResponse>('/projects/');
}

/**
 * 获取项目详情
 */
export async function getProject(slug: string): Promise<Project> {
  return apiRequest<Project>(`/projects/${slug}`);
}

/**
 * 删除项目
 */
export async function deleteProject(slug: string): Promise<void> {
  await apiRequest(`/projects/${slug}`, { method: 'DELETE' });
}

// ============ Storyboard 相关 API ============

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

/**
 * 获取项目的 Storyboard
 */
export async function getStoryboard(slug: string): Promise<Storyboard> {
  return apiRequest<Storyboard>(`/projects/${slug}/storyboard`);
}

/**
 * 更新项目的 Storyboard
 */
export async function updateStoryboard(slug: string, storyboard: Storyboard): Promise<void> {
  await apiRequest(`/projects/${slug}/storyboard`, {
    method: 'PUT',
    body: JSON.stringify(storyboard),
  });
}

// ============ 视频相关 API ============

export interface VideoInfo {
  name: string;
  section: string;
  path: string;
  full_path: string;
}

/**
 * 获取项目的视频列表
 */
export async function getVideos(slug: string): Promise<{ videos: VideoInfo[] }> {
  return apiRequest<{ videos: VideoInfo[] }>(`/projects/${slug}/videos`);
}

// ============ 生成相关 API ============

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

/**
 * 启动视频生成任务
 */
export async function startGeneration(request: GenerateRequest): Promise<GenerateResponse> {
  return apiRequest<GenerateResponse>('/generate/', {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

// ============ Refiner 相关 API ============

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

/**
 * 对章节进行视觉分析
 */
export async function critiqueSection(slug: string, sectionId: string): Promise<CritiqueResponse> {
  return apiRequest<CritiqueResponse>(`/refiner/${slug}/critique/${sectionId}`, {
    method: 'POST',
  });
}

/**
 * 根据建议优化章节代码
 */
export async function refineSection(slug: string, request: RefineRequest): Promise<RefineResponse> {
  return apiRequest<RefineResponse>(`/refiner/${slug}/refine`, {
    method: 'POST',
    body: JSON.stringify(request),
  });
}

/**
 * 重新渲染章节
 */
export async function renderSection(slug: string, sectionId: string): Promise<{ success: boolean; message: string }> {
  return apiRequest(`/refiner/${slug}/render/${sectionId}`, {
    method: 'POST',
  });
}

// ============ WebSocket 工具 ============

/**
 * 创建 WebSocket 连接用于接收生成日志
 */
// 生成 WebSocket 基础地址
function getWebSocketBaseUrl(): string {
  // 客户端侧优先使用当前页面的协议与主机名，避免非 localhost 访问时连接失败
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.hostname || 'localhost';
    return `${protocol}://${host}:8000`;
  }
  return 'ws://localhost:8000';
}

export function createLogWebSocket(
  taskId: string,
  onMessage: (data: any) => void,
  onError?: (error: Event) => void,
  onClose?: () => void
): WebSocket {
  const baseUrl = getWebSocketBaseUrl();
  const ws = new WebSocket(`${baseUrl}/api/generate/ws/${taskId}`);

  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      console.error('Failed to parse WebSocket message:', e);
    }
  };

  if (onError) {
    ws.onerror = onError;
  }

  if (onClose) {
    ws.onclose = onClose;
  }

  return ws;
}
