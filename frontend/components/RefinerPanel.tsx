'use client';

import { useState } from 'react';
import { Eye, Sparkles, RotateCcw, Loader2 } from 'lucide-react';

interface RefinerPanelProps {
  slug: string;
  sectionId: string;
  onRefineComplete?: () => void;
}

export default function RefinerPanel({ slug, sectionId, onRefineComplete }: RefinerPanelProps) {
  const [loading, setLoading] = useState(false);
  const [critiquing, setCritiquing] = useState(false);
  const [rendering, setRendering] = useState(false);
  const [suggestion, setSuggestion] = useState<string | null>(null);
  const [customSuggestion, setCustomSuggestion] = useState('');
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  // 执行视觉分析
  const handleCritique = async () => {
    setCritiquing(true);
    setSuggestion(null);
    setResult(null);

    try {
      const response = await fetch(`/api/refiner/${slug}/critique/${sectionId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '视觉分析失败');
      }

      const data = await response.json();
      if (data.has_issues && data.suggestion) {
        setSuggestion(data.suggestion);
      } else {
        setResult({ success: true, message: '✅ 视觉检查通过，无需优化' });
      }
    } catch (err) {
      setResult({ 
        success: false, 
        message: err instanceof Error ? err.message : '未知错误' 
      });
    } finally {
      setCritiquing(false);
    }
  };

  // 执行代码优化
  const handleRefine = async (useSuggestion: string) => {
    setLoading(true);
    setResult(null);

    try {
      const response = await fetch(`/api/refiner/${slug}/refine`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          section_id: sectionId,
          custom_suggestion: useSuggestion || undefined,
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '代码优化失败');
      }

      const data = await response.json();
      setResult({
        success: data.success && data.refined,
        message: data.message,
      });

      if (data.refined) {
        onRefineComplete?.();
      }
    } catch (err) {
      setResult({
        success: false,
        message: err instanceof Error ? err.message : '未知错误',
      });
    } finally {
      setLoading(false);
    }
  };

  // 重新渲染
  const handleRender = async () => {
    setRendering(true);
    setResult(null);

    try {
      const response = await fetch(`/api/refiner/${slug}/render/${sectionId}`, {
        method: 'POST',
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || '渲染失败');
      }

      const data = await response.json();
      setResult({
        success: data.success,
        message: data.success ? '✅ 渲染成功' : `❌ ${data.error || '渲染失败'}`,
      });

      if (data.success) {
        onRefineComplete?.();
      }
    } catch (err) {
      setResult({
        success: false,
        message: err instanceof Error ? err.message : '未知错误',
      });
    } finally {
      setRendering(false);
    }
  };

  return (
    <div className="bg-manim-surface rounded-xl p-6 space-y-4">
      <h3 className="text-lg font-semibold flex items-center gap-2">
        <Sparkles size={20} className="text-manim-accent" />
        视觉优化
      </h3>

      <p className="text-sm text-gray-400">
        使用 AI 视觉模型分析视频质量，自动优化布局和样式。
      </p>

      {/* 操作按钮 */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={handleCritique}
          disabled={critiquing || loading}
          className="flex items-center gap-2 px-4 py-2 bg-manim-bg rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
        >
          {critiquing ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <Eye size={16} />
          )}
          {critiquing ? '分析中...' : '视觉分析'}
        </button>

        <button
          onClick={handleRender}
          disabled={rendering || loading}
          className="flex items-center gap-2 px-4 py-2 bg-manim-bg rounded-lg hover:bg-gray-700 disabled:opacity-50 transition-colors"
        >
          {rendering ? (
            <Loader2 size={16} className="animate-spin" />
          ) : (
            <RotateCcw size={16} />
          )}
          {rendering ? '渲染中...' : '重新渲染'}
        </button>
      </div>

      {/* 分析结果/建议 */}
      {suggestion && (
        <div className="p-4 bg-manim-warning/10 border border-manim-warning/30 rounded-lg">
          <p className="text-sm font-medium text-manim-warning mb-2">发现问题：</p>
          <p className="text-sm text-gray-300 mb-4">{suggestion}</p>
          <button
            onClick={() => handleRefine(suggestion)}
            disabled={loading}
            className="flex items-center gap-2 px-4 py-2 bg-manim-accent text-manim-bg rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            {loading ? (
              <Loader2 size={16} className="animate-spin" />
            ) : (
              <Sparkles size={16} />
            )}
            {loading ? '优化中...' : '应用建议'}
          </button>
        </div>
      )}

      {/* 自定义建议 */}
      <div>
        <label className="block text-sm font-medium mb-2">
          或输入自定义优化建议：
        </label>
        <div className="flex gap-2">
          <input
            type="text"
            value={customSuggestion}
            onChange={(e) => setCustomSuggestion(e.target.value)}
            placeholder="例如：将标题移到左上角，增大字体..."
            className="flex-1 px-4 py-2 bg-manim-bg border border-gray-700 rounded-lg focus:outline-none focus:border-manim-accent"
            disabled={loading}
          />
          <button
            onClick={() => handleRefine(customSuggestion)}
            disabled={loading || !customSuggestion.trim()}
            className="px-4 py-2 bg-manim-accent text-manim-bg rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            应用
          </button>
        </div>
      </div>

      {/* 结果提示 */}
      {result && (
        <div
          className={`p-4 rounded-lg ${
            result.success
              ? 'bg-manim-success/10 border border-manim-success/30 text-manim-success'
              : 'bg-manim-error/10 border border-manim-error/30 text-manim-error'
          }`}
        >
          {result.message}
        </div>
      )}
    </div>
  );
}
