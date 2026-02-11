'use client';

import { useEffect, useRef, useMemo } from 'react';
import { Terminal, ClipboardList, ImageIcon, Code2, Film, Sparkles } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getWebSocketBaseUrl } from '@/lib/api';
import type { LogMessage, GenerateStatus, CompletionData } from '@/lib/types';

interface LogViewerProps {
  taskId: string | null;
  logs: LogMessage[];
  status?: GenerateStatus;
  rendered?: boolean;
  onLog: (level: LogMessage['level'], message: string) => void;
  onStatusChange: (status: GenerateStatus, data?: CompletionData) => void;
}

export default function LogViewer({ taskId, logs, status, rendered, onLog, onStatusChange }: LogViewerProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);
  const connectedTaskIdRef = useRef<string | null>(null);

  // 自动滚动
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  // 稳定化回调引用
  const onLogRef = useRef(onLog);
  const onStatusChangeRef = useRef(onStatusChange);
  useEffect(() => {
    onLogRef.current = onLog;
    onStatusChangeRef.current = onStatusChange;
  }, [onLog, onStatusChange]);

  // WebSocket 连接
  useEffect(() => {
    if (!taskId) return;
    if (connectedTaskIdRef.current === taskId && wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      return;
    }

    if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
    if (heartbeatRef.current) { clearInterval(heartbeatRef.current); heartbeatRef.current = null; }

    connectedTaskIdRef.current = taskId;
    const baseUrl = getWebSocketBaseUrl();
    const ws = new WebSocket(`${baseUrl}/api/generate/ws/${taskId}`);
    wsRef.current = ws;

    ws.onopen = () => onLogRef.current('info', '已连接到服务器，等待日志...');

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
          onLogRef.current(data.level || 'info', data.message);
        } else if (data.type === 'status') {
          onStatusChangeRef.current(data.status, data.data);
          if (data.status === 'completed') {
            onLogRef.current('success', '所有任务已完成！');
          } else if (data.status === 'failed') {
            onLogRef.current('error', `任务失败: ${data.data?.error || '未知错误'}`);
          }
        }
      } catch (e) {
        console.error('Failed to parse WS message:', e);
      }
    };

    ws.onerror = () => onLogRef.current('error', 'WebSocket 连接错误');
    ws.onclose = () => onLogRef.current('info', '连接已断开');

    heartbeatRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) ws.send('ping');
    }, 25000);

    return () => {
      if (heartbeatRef.current) { clearInterval(heartbeatRef.current); heartbeatRef.current = null; }
      if (wsRef.current) { wsRef.current.close(); wsRef.current = null; }
    };
  }, [taskId]);

  const getLevelClass = (level: LogMessage['level']) => {
    switch (level) {
      case 'success': return 'log-success';
      case 'warning': return 'log-warning';
      case 'error': return 'log-error';
      default: return 'log-info';
    }
  };

  const formatTime = (date: Date) =>
    date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' });

  // 阶段进度检测
  const STAGES = [
    { key: 'plan', label: '规划', icon: ClipboardList, patterns: ['planner', '规划', '分镜', 'storyboard'] },
    { key: 'asset', label: '资产', icon: ImageIcon, patterns: ['asset', '资产', '图标', 'icon'] },
    { key: 'code', label: '代码', icon: Code2, patterns: ['coder', '代码', '生成代码', 'section_'] },
    { key: 'render', label: '渲染', icon: Film, patterns: ['render', '渲染', 'manim', 'mp4'], requiresRender: true },
    { key: 'refine', label: '优化', icon: Sparkles, patterns: ['critic', 'refin', '优化', '视觉'], requiresRender: true },
  ] as const;

  const currentStage = useMemo(() => {
    const allText = logs.map(l => l.message.toLowerCase()).join(' ');
    let lastIdx = -1;
    STAGES.forEach((stage, idx) => {
      if (stage.patterns.some(p => allText.includes(p))) {
        lastIdx = idx;
      }
    });
    return lastIdx;
  }, [logs]);

  return (
    <div className="space-y-3">
      {/* 阶段进度条 */}
      {logs.length > 0 && (
        <div className="flex items-center gap-1">
          {STAGES.map((stage, i) => {
            const Icon = stage.icon;
            const needsRender = 'requiresRender' in stage && stage.requiresRender;
            // 判断该阶段是否被跳过（需要渲染但实际未渲染）
            const isSkipped = status === 'completed' && rendered === false && needsRender;
            // 完成态：所有非跳过阶段标记为完成
            const isCompleted = status === 'completed' ? !isSkipped : i < currentStage;
            // 运行态：当前阶段高亮
            const isActive = status !== 'completed' && i === currentStage;
            return (
              <div key={stage.key} className="flex items-center flex-1">
                <div className={`flex items-center gap-1.5 px-2 py-1.5 rounded-md text-xs font-medium transition-colors w-full justify-center ${
                  isSkipped ? 'text-muted-foreground/30 line-through' :
                  isActive ? 'bg-primary/10 text-primary' :
                  isCompleted ? 'text-emerald-600 dark:text-emerald-400' :
                  'text-muted-foreground/50'
                }`}>
                  <Icon className={`h-3.5 w-3.5 ${isActive ? 'animate-pulse' : ''}`} />
                  <span className="hidden sm:inline">{stage.label}</span>
                </div>
                {i < STAGES.length - 1 && (
                  <div className={`h-px w-3 shrink-0 ${
                    isSkipped ? 'bg-border/50' :
                    isCompleted ? 'bg-emerald-400' : 'bg-border'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
      )}

      <Card className="overflow-hidden">
      {/* macOS 风格标题栏 */}
      <div className="px-4 py-3 border-b border-border flex items-center gap-3">
        <div className="flex items-center gap-1.5">
          <div className="w-3 h-3 rounded-full bg-red-400/80" />
          <div className="w-3 h-3 rounded-full bg-yellow-400/80" />
          <div className="w-3 h-3 rounded-full bg-green-400/80" />
        </div>
        <div className="flex items-center gap-2 text-sm text-muted-foreground">
          <Terminal className="h-3.5 w-3.5" />
          <span>生成日志</span>
        </div>
        <span className="ml-auto text-xs text-muted-foreground">{logs.length} 条</span>
      </div>

      <ScrollArea className="h-80">
        <div className="p-4 font-mono text-sm bg-card">
          {logs.length === 0 ? (
            <div className="text-muted-foreground text-center py-12">
              等待日志输出...
            </div>
          ) : (
            <div className="space-y-0.5">
              {logs.map((log, index) => (
                <div key={index} className={`${getLevelClass(log.level)} flex animate-fade-in`}>
                  <span className="text-muted-foreground mr-3 shrink-0 select-none">
                    {formatTime(log.timestamp)}
                  </span>
                  <span className="whitespace-pre-wrap break-all">{log.message}</span>
                </div>
              ))}
              <div ref={bottomRef} />
            </div>
          )}
        </div>
      </ScrollArea>
    </Card>
    </div>
  );
}
