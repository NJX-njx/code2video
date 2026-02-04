'use client';

import { useState, useEffect, useCallback } from 'react';
import { Play, FolderOpen, Plus } from 'lucide-react';
import GenerateForm from '@/components/GenerateForm';
import ProjectList from '@/components/ProjectList';
import LogViewer from '@/components/LogViewer';

// 日志消息类型
interface LogMessage {
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: Date;
}

// 生成状态类型
type GenerateStatus = 'idle' | 'running' | 'completed' | 'failed';

export default function Home() {
  // 当前视图状态：'home' | 'generate' | 'projects'
  const [view, setView] = useState<'home' | 'generate' | 'projects'>('home');
  
  // 生成任务状态
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<GenerateStatus>('idle');
  const [logs, setLogs] = useState<LogMessage[]>([]);

  // 处理生成任务开始
  const handleGenerateStart = (newTaskId: string) => {
    setTaskId(newTaskId);
    setStatus('running');
    setLogs([]);
    setView('generate');
  };

  // 添加日志
  const addLog = useCallback((level: LogMessage['level'], message: string) => {
    setLogs(prev => [...prev, { level, message, timestamp: new Date() }]);
  }, []);

  // 处理状态更新
  const handleStatusUpdate = useCallback((newStatus: GenerateStatus) => {
    setStatus(newStatus);
  }, []);

  return (
    <main className="min-h-screen p-8">
      {/* 顶部导航 */}
      <header className="max-w-6xl mx-auto mb-8">
        <div className="flex items-center justify-between">
          <h1 
            className="text-3xl font-bold text-manim-accent cursor-pointer"
            onClick={() => setView('home')}
          >
            📐 MathVideo
          </h1>
          <nav className="flex gap-4">
            <button
              onClick={() => setView('home')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                view === 'home' ? 'bg-manim-accent text-manim-bg' : 'hover:bg-manim-surface'
              }`}
            >
              <Plus size={18} />
              新建
            </button>
            <button
              onClick={() => setView('projects')}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                view === 'projects' ? 'bg-manim-accent text-manim-bg' : 'hover:bg-manim-surface'
              }`}
            >
              <FolderOpen size={18} />
              项目
            </button>
          </nav>
        </div>
      </header>

      {/* 主内容区 */}
      <div className="max-w-6xl mx-auto">
        {view === 'home' && (
          <div className="space-y-8">
            {/* 欢迎区域 */}
            <div className="text-center py-12">
              <h2 className="text-4xl font-bold mb-4">
                自动化数学视频生成器
              </h2>
              <p className="text-gray-400 text-lg max-w-2xl mx-auto">
                输入任何数学主题，AI 将自动生成教学分镜、Manim 动画代码，并渲染成精美的教学视频。
              </p>
            </div>

            {/* 生成表单 */}
            <GenerateForm 
              onGenerateStart={handleGenerateStart}
              disabled={status === 'running'}
            />

            {/* 功能特性 */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-12">
              <div className="bg-manim-surface rounded-xl p-6">
                <div className="text-3xl mb-4">🤖</div>
                <h3 className="text-xl font-semibold mb-2">智能规划</h3>
                <p className="text-gray-400">
                  使用 Claude AI 自动将数学主题拆解为结构化的分镜脚本
                </p>
              </div>
              <div className="bg-manim-surface rounded-xl p-6">
                <div className="text-3xl mb-4">🎬</div>
                <h3 className="text-xl font-semibold mb-2">代码生成</h3>
                <p className="text-gray-400">
                  自动生成 Manim Python 动画代码，支持错误自动修复
                </p>
              </div>
              <div className="bg-manim-surface rounded-xl p-6">
                <div className="text-3xl mb-4">👁️</div>
                <h3 className="text-xl font-semibold mb-2">视觉反馈</h3>
                <p className="text-gray-400">
                  使用视觉大模型分析生成的视频，自动优化布局和样式
                </p>
              </div>
            </div>
          </div>
        )}

        {view === 'generate' && (
          <div className="space-y-6">
            {/* 状态指示器 */}
            <div className="bg-manim-surface rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold">
                  {status === 'running' && '🔄 正在生成...'}
                  {status === 'completed' && '✅ 生成完成'}
                  {status === 'failed' && '❌ 生成失败'}
                  {status === 'idle' && '⏳ 准备就绪'}
                </h2>
                {status === 'running' && (
                  <div className="w-6 h-6 border-2 border-manim-accent border-t-transparent rounded-full animate-spin" />
                )}
              </div>
              
              {taskId && (
                <p className="text-gray-400">
                  任务 ID: <code className="bg-manim-bg px-2 py-1 rounded">{taskId}</code>
                </p>
              )}
            </div>

            {/* 日志查看器 */}
            <LogViewer 
              taskId={taskId}
              logs={logs}
              onLog={addLog}
              onStatusChange={handleStatusUpdate}
            />

            {/* 完成后的操作 */}
            {status === 'completed' && taskId && (
              <div className="bg-manim-surface rounded-xl p-6">
                <h3 className="text-lg font-semibold mb-4">下一步操作</h3>
                <div className="flex gap-4">
                  <button
                    onClick={() => window.location.href = `/projects/${taskId}`}
                    className="flex items-center gap-2 px-4 py-2 bg-manim-accent text-manim-bg rounded-lg hover:opacity-90"
                  >
                    <Play size={18} />
                    查看项目
                  </button>
                  <button
                    onClick={() => {
                      setView('home');
                      setStatus('idle');
                      setTaskId(null);
                      setLogs([]);
                    }}
                    className="px-4 py-2 border border-gray-600 rounded-lg hover:bg-manim-surface"
                  >
                    生成新项目
                  </button>
                </div>
              </div>
            )}
          </div>
        )}

        {view === 'projects' && (
          <ProjectList />
        )}
      </div>
    </main>
  );
}
