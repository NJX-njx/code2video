'use client';

import { useState, useCallback } from 'react';
import { Plus, FolderOpen, Play, ArrowRight, Sparkles, Cpu, Eye } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ThemeToggle } from '@/components/ThemeToggle';
import GenerateForm from '@/components/GenerateForm';
import ProjectList from '@/components/ProjectList';
import LogViewer from '@/components/LogViewer';
import type { LogMessage, GenerateStatus } from '@/lib/types';

export default function Home() {
  const [view, setView] = useState<'home' | 'generate' | 'projects'>('home');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [status, setStatus] = useState<GenerateStatus>('idle');
  const [logs, setLogs] = useState<LogMessage[]>([]);

  const handleGenerateStart = (newTaskId: string) => {
    setTaskId(newTaskId);
    setStatus('running');
    setLogs([]);
    setView('generate');
  };

  const addLog = useCallback((level: LogMessage['level'], message: string) => {
    setLogs(prev => [...prev, { level, message, timestamp: new Date() }]);
  }, []);

  const handleStatusUpdate = useCallback((newStatus: GenerateStatus) => {
    setStatus(newStatus);
  }, []);

  const features = [
    {
      icon: <Sparkles className="h-5 w-5" />,
      title: '智能规划',
      description: '使用 AI 自动将数学主题拆解为结构化的分镜脚本',
    },
    {
      icon: <Cpu className="h-5 w-5" />,
      title: '代码生成',
      description: '自动生成 Manim 动画代码，支持错误自动修复',
    },
    {
      icon: <Eye className="h-5 w-5" />,
      title: '视觉反馈',
      description: '使用视觉模型分析生成的视频，优化布局和样式',
    },
  ];

  return (
    <div className="min-h-screen">
      {/* 导航栏 — 毛玻璃效果 */}
      <header className="sticky top-0 z-50 glass-strong">
        <div className="max-w-6xl mx-auto px-6 h-14 flex items-center justify-between">
          <button
            onClick={() => { setView('home'); setStatus('idle'); }}
            className="flex items-center gap-2 font-semibold text-lg tracking-tight hover:opacity-80 transition-opacity"
          >
            <span className="text-xl">📐</span>
            <span>MathVideo</span>
          </button>

          <nav className="flex items-center gap-1">
            <Button
              variant={view === 'home' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setView('home')}
              className="gap-1.5"
            >
              <Plus className="h-4 w-4" />
              新建
            </Button>
            <Button
              variant={view === 'projects' ? 'secondary' : 'ghost'}
              size="sm"
              onClick={() => setView('projects')}
              className="gap-1.5"
            >
              <FolderOpen className="h-4 w-4" />
              项目
            </Button>
            <div className="w-px h-5 bg-border mx-1" />
            <ThemeToggle />
          </nav>
        </div>
      </header>

      {/* 主内容 */}
      <main className="max-w-6xl mx-auto px-6 py-8">
        <AnimatePresence mode="wait">
          {view === 'home' && (
            <motion.div
              key="home"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="space-y-12"
            >
              {/* Hero */}
              <div className="text-center pt-12 pb-4">
                <Badge variant="secondary" className="mb-4">
                  AI-Powered
                </Badge>
                <h1 className="text-4xl sm:text-5xl font-bold tracking-tight mb-4">
                  数学视频，
                  <span className="text-primary">自动生成</span>
                </h1>
                <p className="text-muted-foreground text-lg max-w-xl mx-auto leading-relaxed">
                  输入任何数学主题，AI 自动生成教学分镜、Manim 动画代码，渲染成精美的教学视频。
                </p>
              </div>

              {/* 生成表单 */}
              <GenerateForm
                onGenerateStart={handleGenerateStart}
                disabled={status === 'running'}
              />

              {/* 功能特性 */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-4">
                {features.map((feature, i) => (
                  <Card key={i} className="group hover:-translate-y-1 transition-all duration-300">
                    <CardContent className="p-6">
                      <div className="h-10 w-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                        {feature.icon}
                      </div>
                      <h3 className="font-semibold mb-1.5">{feature.title}</h3>
                      <p className="text-sm text-muted-foreground leading-relaxed">
                        {feature.description}
                      </p>
                    </CardContent>
                  </Card>
                ))}
              </div>

              {/* 页脚 */}
              <footer className="pt-8 pb-4 border-t border-border/40">
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>MathVideo — AI 驱动的数学教学视频生成器</span>
                  <div className="flex items-center gap-4">
                    <a href="https://github.com" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">GitHub</a>
                    <a href="/api/docs" target="_blank" rel="noopener noreferrer" className="hover:text-foreground transition-colors">API 文档</a>
                  </div>
                </div>
              </footer>
            </motion.div>
          )}

          {view === 'generate' && (
            <motion.div
              key="generate"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
              className="space-y-6"
            >
              {/* 状态卡片 */}
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      {status === 'running' && (
                        <div className="h-5 w-5 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                      )}
                      <h2 className="text-lg font-semibold">
                        {status === 'running' && '正在生成...'}
                        {status === 'completed' && '✅ 生成完成'}
                        {status === 'failed' && '生成失败'}
                        {status === 'idle' && '准备就绪'}
                      </h2>
                    </div>
                    {taskId && (
                      <Badge variant="outline" className="font-mono text-xs">
                        {taskId}
                      </Badge>
                    )}
                  </div>
                </CardContent>
              </Card>

              {/* 日志 */}
              <LogViewer
                taskId={taskId}
                logs={logs}
                onLog={addLog}
                onStatusChange={handleStatusUpdate}
              />

              {/* 完成操作 */}
              {status === 'completed' && taskId && (
                <Card>
                  <CardContent className="p-6 flex items-center justify-between">
                    <p className="text-muted-foreground">视频已生成，可以查看项目详情</p>
                    <div className="flex gap-3">
                      <Button
                        variant="outline"
                        onClick={() => { setView('home'); setStatus('idle'); setTaskId(null); setLogs([]); }}
                      >
                        新建项目
                      </Button>
                      <Button onClick={() => window.location.href = `/projects/${taskId}`}>
                        <Play className="h-4 w-4 mr-1.5" />
                        查看项目
                        <ArrowRight className="h-4 w-4 ml-1.5" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              )}
            </motion.div>
          )}

          {view === 'projects' && (
            <motion.div
              key="projects"
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.2 }}
            >
              <ProjectList />
            </motion.div>
          )}
        </AnimatePresence>
      </main>
    </div>
  );
}
