'use client';

import { useState, useEffect, useCallback } from 'react';
import { invoke } from '@tauri-apps/api/core';
import { Loader2, CheckCircle2, XCircle, ExternalLink, RefreshCw } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';

interface EnvStatus {
  conda_installed: boolean;
  conda_version: string | null;
  mathvideo_env_exists: boolean;
  python_version: string | null;
  ffmpeg_installed: boolean;
  ffmpeg_version: string | null;
  all_ready: boolean;
}

interface SetupWizardProps {
  onReady: () => void;
}

const CHECK_ITEMS = [
  { key: 'conda_installed', label: 'Conda 包管理器', versionKey: 'conda_version', helpUrl: 'https://docs.conda.io/en/latest/miniconda.html' },
  { key: 'mathvideo_env_exists', label: 'mathvideo 环境', versionKey: 'python_version', helpUrl: null },
  { key: 'ffmpeg_installed', label: 'FFmpeg', versionKey: 'ffmpeg_version', helpUrl: 'https://ffmpeg.org/download.html' },
] as const;

export default function SetupWizard({ onReady }: SetupWizardProps) {
  const [checking, setChecking] = useState(true);
  const [status, setStatus] = useState<EnvStatus | null>(null);
  const [error, setError] = useState<string | null>(null);

  const runCheck = useCallback(async () => {
    setChecking(true);
    setError(null);
    try {
      const result = await invoke<EnvStatus>('check_environment');
      setStatus(result);
      if (result.all_ready) {
        // 短暂延迟后跳转，让用户看到全部绿灯
        setTimeout(() => onReady(), 1200);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setChecking(false);
    }
  }, [onReady]);

  useEffect(() => {
    runCheck();
  }, [runCheck]);

  const readyCount = status
    ? [status.conda_installed, status.mathvideo_env_exists, status.ffmpeg_installed].filter(Boolean).length
    : 0;

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <Card className="w-full max-w-lg">
        <CardHeader className="text-center pb-4">
          <div className="mx-auto w-14 h-14 rounded-2xl bg-primary/10 flex items-center justify-center mb-3">
            <span className="text-2xl">🎬</span>
          </div>
          <CardTitle className="text-xl">环境检测</CardTitle>
          <CardDescription>
            MathVideo 需要以下依赖才能运行
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-5">
          {/* 进度条 */}
          <Progress value={(readyCount / 3) * 100} className="h-2" />

          {/* 检测项列表 */}
          <div className="space-y-3">
            {CHECK_ITEMS.map((item) => {
              const installed = status?.[item.key] ?? false;
              const version = status?.[item.versionKey] ?? null;

              return (
                <div
                  key={item.key}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/30"
                >
                  <div className="flex items-center gap-3">
                    {checking ? (
                      <Loader2 className="h-4 w-4 animate-spin text-muted-foreground" />
                    ) : installed ? (
                      <CheckCircle2 className="h-4 w-4 text-emerald-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-destructive" />
                    )}
                    <div>
                      <p className="text-sm font-medium">{item.label}</p>
                      {version && (
                        <p className="text-xs text-muted-foreground">{version}</p>
                      )}
                    </div>
                  </div>

                  {!checking && !installed && item.helpUrl && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-xs gap-1"
                      onClick={() => window.open(item.helpUrl!, '_blank')}
                    >
                      安装指南 <ExternalLink className="h-3 w-3" />
                    </Button>
                  )}

                  {!checking && installed && (
                    <Badge variant="success" className="text-xs">就绪</Badge>
                  )}
                </div>
              );
            })}
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/20 text-sm text-destructive">
              {error}
            </div>
          )}

          {/* 操作按钮 */}
          <div className="flex justify-center gap-3 pt-2">
            <Button
              variant="outline"
              onClick={runCheck}
              disabled={checking}
              className="gap-1.5"
            >
              <RefreshCw className={`h-3.5 w-3.5 ${checking ? 'animate-spin' : ''}`} />
              重新检测
            </Button>

            {status?.all_ready && (
              <Button onClick={onReady} className="gap-1.5">
                <CheckCircle2 className="h-3.5 w-3.5" />
                开始使用
              </Button>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
