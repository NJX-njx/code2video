/**
 * API 客户端工具函数
 * 提供与后端 API 交互的封装
 */

import type {
  Project,
  ProjectListResponse,
  Storyboard,
  VideoInfo,
  ScriptInfo,
  GenerateResponse,
  CritiqueResponse,
  RefineResponse,
} from './types';

/**
 * 获取 API 基础 URL
 * Tauri 桌面模式直连后端，Web 模式走 Next.js 代理
 */
function getApiBaseUrl(): string {
  if (typeof window !== 'undefined' && (window as any).__TAURI__) {
    return 'http://localhost:8000/api';
  }
  return '/api';
}

/**
 * 获取静态资源基础 URL
 */
export function getStaticBaseUrl(): string {
  if (typeof window !== 'undefined' && (window as any).__TAURI__) {
    return 'http://localhost:8000/static';
  }
  return '/static';
}

/**
 * 获取 WebSocket 基础 URL
 */
export function getWebSocketBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const isTauri = (window as any).__TAURI__;
    if (isTauri) {
      return 'ws://localhost:8000';
    }
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.hostname || 'localhost';
    return `${protocol}://${host}:8000`;
  }
  return 'ws://localhost:8000';
}

/**
 * 通用 API 请求函数
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const base = getApiBaseUrl();
  const url = `${base}${endpoint}`;

  const defaultHeaders: HeadersInit = {};
  if (!(options.body instanceof FormData)) {
    defaultHeaders['Content-Type'] = 'application/json';
  }

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

// ============ 项目 API ============

export async function getProjects(): Promise<ProjectListResponse> {
  return apiRequest<ProjectListResponse>('/projects/');
}

export async function getProject(slug: string): Promise<Project> {
  return apiRequest<Project>(`/projects/${slug}`);
}

export async function deleteProject(slug: string): Promise<void> {
  await apiRequest(`/projects/${slug}`, { method: 'DELETE' });
}

// ============ Storyboard API ============

export async function getStoryboard(slug: string): Promise<Storyboard> {
  return apiRequest<Storyboard>(`/projects/${slug}/storyboard`);
}

export async function updateStoryboard(slug: string, storyboard: Storyboard): Promise<void> {
  await apiRequest(`/projects/${slug}/storyboard`, {
    method: 'PUT',
    body: JSON.stringify(storyboard),
  });
}

// ============ 视频 API ============

export async function getVideos(slug: string): Promise<{ videos: VideoInfo[] }> {
  return apiRequest<{ videos: VideoInfo[] }>(`/projects/${slug}/videos`);
}

export async function getScripts(slug: string): Promise<{ scripts: ScriptInfo[] }> {
  return apiRequest<{ scripts: ScriptInfo[] }>(`/projects/${slug}/scripts`);
}

// ============ 生成 API ============

export async function startGeneration(
  prompt: string,
  render: boolean,
  imageFile?: File | null
): Promise<GenerateResponse> {
  if (imageFile) {
    const formData = new FormData();
    formData.append('prompt', prompt);
    formData.append('render', render ? 'true' : 'false');
    formData.append('image', imageFile);
    return apiRequest<GenerateResponse>('/generate/', {
      method: 'POST',
      body: formData,
    });
  }
  return apiRequest<GenerateResponse>('/generate/', {
    method: 'POST',
    body: JSON.stringify({ prompt, render }),
  });
}

// ============ Refiner API ============

export async function critiqueSection(slug: string, sectionId: string): Promise<CritiqueResponse> {
  return apiRequest<CritiqueResponse>(`/refiner/${slug}/critique/${sectionId}`, {
    method: 'POST',
  });
}

export async function refineSection(
  slug: string,
  sectionId: string,
  customSuggestion?: string
): Promise<RefineResponse> {
  return apiRequest<RefineResponse>(`/refiner/${slug}/refine`, {
    method: 'POST',
    body: JSON.stringify({
      section_id: sectionId,
      custom_suggestion: customSuggestion || undefined,
    }),
  });
}

export async function renderSection(
  slug: string,
  sectionId: string
): Promise<{ success: boolean; message: string }> {
  return apiRequest(`/refiner/${slug}/render/${sectionId}`, {
    method: 'POST',
  });
}

// ============ WebSocket ============

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

  if (onError) ws.onerror = onError;
  if (onClose) ws.onclose = onClose;

  return ws;
}
