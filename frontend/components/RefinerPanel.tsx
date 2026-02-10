'use client';

import { useState } from 'react';
import { Eye, Sparkles, RotateCcw, Loader2 } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { critiqueSection, refineSection, renderSection } from '@/lib/api';

interface RefinerPanelProps {
  slug: string;
  sectionId: string;
  onRefineComplete?: () => void;
}

export default function RefinerPanel({ slug, sectionId, onRefineComplete }: RefinerPanelProps) {
  const [critiquing, setCritiquing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [customSuggestion, setCustomSuggestion] = useState('');
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const handleCritique = async () => {
    setCritiquing(true);
    setSuggestion(null);
    setResult(null);
    try {
      const data = await critiqueSection(slug, sectionId);
      if (data.has_issues && data.suggestion) {
        setSuggestion(data.suggestion);
      } else {
        setResult({ success: true, message: '视觉检查通过，无需优化' });
      }
    } catch (err) {
      setResult({ success: false, message: err instanceof Error ? err.message : '未知错误' });
    } finally {
      setCritiquing(false);
    }
  };

  const handleRefine = async (useSuggestion: string) => {
    setLoading(true);
    setResult(null);
    try {
      const data = await refineSection(slug, sectionId, useSuggestion || undefined);
      setResult({ success: data.success && data.refined, message: data.message });
      if (data.refined) onRefineComplete?.();
    } catch (err) {
      setResult({ success: false, message: err instanceof Error ? err.message : '未知错误' });
    } finally {
      setLoading(false);
    }
  };

  const handleRender = async () => {
    setRendering(true);
    setResult(null);
    try {
      const data = await renderSection(slug, sectionId);
      setResult({ success: data.success, message: data.success ? '渲染成功' : '渲染失败' });
      if (data.success) onRefineComplete?.();
    } catch (err) {
      setResult({ success: false, message: err instanceof Error ? err.message : '未知错误' });
    } finally {
      setRendering(false);
    }
  };

  return (
    <Card>
      <CardHeader className="pb-3">
        <CardTitle className="text-base flex items-center gap-2">
          <Sparkles className="h-4 w-4 text-primary" />
          视觉优化
        </CardTitle>
        <CardDescription>AI 分析视频质量，优化布局和样式</CardDescription>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* 操作按钮 */}
        <div className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={handleCritique} disabled={critiquing || loading}>
            {critiquing ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" /> : <Eye className="h-3.5 w-3.5 mr-1.5" />}
            {critiquing ? '分析中...' : '视觉分析'}
          </Button>
          <Button variant="outline" size="sm" onClick={handleRender} disabled={rendering || loading}>
            {rendering ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" /> : <RotateCcw className="h-3.5 w-3.5 mr-1.5" />}
            {rendering ? '渲染中...' : '重新渲染'}
          </Button>
        </div>

        {/* 分析结果 */}
        {suggestion && (
          <div className="p-3 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800/40 space-y-2.5">
            <div className="flex items-center gap-1.5">
              <Badge variant="warning" className="text-xs">发现问题</Badge>
            </div>
            <p className="text-sm leading-relaxed">{suggestion}</p>
            <Button size="sm" onClick={() => handleRefine(suggestion)} disabled={loading}>
              {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1.5" /> : <Sparkles className="h-3.5 w-3.5 mr-1.5" />}
              {loading ? '优化中...' : '应用建议'}
            </Button>
          </div>
        )}

        {/* 自定义建议 */}
        <div className="space-y-2">
          <label className="text-xs font-medium text-muted-foreground">自定义建议</label>
          <div className="flex gap-2">
            <Input
              value={customSuggestion}
              onChange={(e) => setCustomSuggestion(e.target.value)}
              placeholder="例如：增大标题字号..."
              className="h-9 text-sm"
              disabled={loading}
            />
            <Button size="sm" onClick={() => handleRefine(customSuggestion)} disabled={loading || !customSuggestion.trim()}>
              应用
            </Button>
          </div>
        </div>

        {/* 结果提示 */}
        {result && (
          <div className={`p-3 rounded-lg text-sm ${
            result.success
              ? 'bg-emerald-50 dark:bg-emerald-900/20 border border-emerald-200 dark:border-emerald-800/40 text-emerald-700 dark:text-emerald-400'
              : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800/40 text-red-700 dark:text-red-400'
          }`}>
            {result.message}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
