'use client';

import { useEffect, useRef } from 'react';
import { Terminal } from 'lucide-react';
import { Card } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { getWebSocketBaseUrl } from '@/lib/api';
import type { LogMessage, GenerateStatus } from '@/lib/types';

interface LogViewerProps {
  taskId: string | null;
  logs: LogMessage[];
  onLog: (level: LogMessage['level'], message: string) => void;
  onStatusChange: (status: GenerateStatus) => void;
}

export default function LogViewer({ taskId, logs, onLog, onStatusChange }: LogViewerProps) {
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
          onStatusChangeRef.current(data.status);
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

  return (
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
  );
}
