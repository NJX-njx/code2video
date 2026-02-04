'use client';

import { useEffect, useRef, useCallback } from 'react';

interface LogMessage {
  level: 'info' | 'success' | 'warning' | 'error';
  message: string;
  timestamp: Date;
}

interface LogViewerProps {
  taskId: string | null;
  logs: LogMessage[];
  onLog: (level: LogMessage['level'], message: string) => void;
  onStatusChange: (status: 'idle' | 'running' | 'completed' | 'failed') => void;
}

// 生成 WebSocket 基础地址
function getWebSocketBaseUrl(): string {
  if (typeof window !== 'undefined') {
    const protocol = window.location.protocol === 'https:' ? 'wss' : 'ws';
    const host = window.location.hostname || 'localhost';
    return `${protocol}://${host}:8000`;
  }
  return 'ws://localhost:8000';
}

export default function LogViewer({ taskId, logs, onLog, onStatusChange }: LogViewerProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);
  // 用于追踪当前连接的 taskId，防止 StrictMode 重复连接
  const connectedTaskIdRef = useRef<string | null>(null);

  // 自动滚动到底部
  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [logs]);

  // 稳定化回调
  const onLogRef = useRef(onLog);
  const onStatusChangeRef = useRef(onStatusChange);
  useEffect(() => {
    onLogRef.current = onLog;
    onStatusChangeRef.current = onStatusChange;
  }, [onLog, onStatusChange]);

  // WebSocket 连接
  useEffect(() => {
    if (!taskId) return;

    // 如果已经为这个 taskId 建立了连接，跳过（解决 StrictMode 双重挂载问题）
    if (connectedTaskIdRef.current === taskId && wsRef.current && wsRef.current.readyState !== WebSocket.CLOSED) {
      return;
    }

    // 关闭旧连接（如果有）
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }

    connectedTaskIdRef.current = taskId;

    const baseUrl = getWebSocketBaseUrl();
    const wsUrl = `${baseUrl}/api/generate/ws/${taskId}`;
    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      onLogRef.current('info', '📡 已连接到服务器，等待日志...');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'log') {
          onLogRef.current(data.level || 'info', data.message);
        } else if (data.type === 'status') {
          onStatusChangeRef.current(data.status);
          if (data.status === 'completed') {
            onLogRef.current('success', '🎉 所有任务已完成！');
          } else if (data.status === 'failed') {
            onLogRef.current('error', `💥 任务失败: ${data.data?.error || '未知错误'}`);
          }
        }
        // connected / heartbeat / pong 消息忽略
      } catch (e) {
        console.error('Failed to parse WebSocket message:', e);
      }
    };

    ws.onerror = () => {
      onLogRef.current('error', '❌ WebSocket 连接错误');
    };

    ws.onclose = () => {
      onLogRef.current('info', '📡 连接已断开');
    };

    // 心跳保活
    heartbeatRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send('ping');
      }
    }, 25000);

    return () => {
      // cleanup 时只清理，不再重置 connectedTaskIdRef（避免 StrictMode 再次触发连接）
      if (heartbeatRef.current) {
        clearInterval(heartbeatRef.current);
        heartbeatRef.current = null;
      }
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [taskId]);

  // 获取日志级别对应的样式类
  const getLevelClass = (level: LogMessage['level']) => {
    switch (level) {
      case 'success':
        return 'log-success';
      case 'warning':
        return 'log-warning';
      case 'error':
        return 'log-error';
      default:
        return 'log-info';
    }
  };

  // 格式化时间
  const formatTime = (date: Date) => {
    return date.toLocaleTimeString('zh-CN', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  return (
    <div className="bg-manim-surface rounded-xl overflow-hidden">
      <div className="px-4 py-3 border-b border-gray-700 flex items-center justify-between">
        <h3 className="font-medium">生成日志</h3>
        <span className="text-sm text-gray-400">{logs.length} 条消息</span>
      </div>
      
      <div
        ref={containerRef}
        className="h-96 overflow-y-auto p-4 font-mono text-sm bg-manim-bg"
      >
        {logs.length === 0 ? (
          <div className="text-gray-500 text-center py-8">
            等待日志输出...
          </div>
        ) : (
          <div className="space-y-1">
            {logs.map((log, index) => (
              <div key={index} className={`${getLevelClass(log.level)} flex`}>
                <span className="text-gray-500 mr-3 shrink-0">
                  [{formatTime(log.timestamp)}]
                </span>
                <span className="whitespace-pre-wrap break-all">{log.message}</span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
