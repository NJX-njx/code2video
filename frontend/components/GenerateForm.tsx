'use client';

import { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';

interface GenerateFormProps {
  onGenerateStart: (taskId: string) => void;
  disabled?: boolean;
}

export default function GenerateForm({ onGenerateStart, disabled }: GenerateFormProps) {
  const [topic, setTopic] = useState('');
  const [render, setRender] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 示例主题
  const examples = [
    '勾股定理',
    '圆的面积',
    '三角形面积',
    '二次函数',
    '等差数列',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      setError('请输入数学主题');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('/api/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ topic: topic.trim(), render }),
      });

      if (!response.ok) {
        const data = await response.json();
        throw new Error(data.detail || '生成请求失败');
      }

      const data = await response.json();
      onGenerateStart(data.task_id);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-manim-surface rounded-xl p-8">
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* 主题输入 */}
        <div>
          <label htmlFor="topic" className="block text-sm font-medium mb-2">
            数学主题
          </label>
          <input
            id="topic"
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="例如：勾股定理、圆的面积、二次函数..."
            className="w-full px-4 py-3 bg-manim-bg border border-gray-700 rounded-lg focus:outline-none focus:border-manim-accent transition-colors"
            disabled={disabled || loading}
          />
        </div>

        {/* 快速选择示例 */}
        <div>
          <p className="text-sm text-gray-400 mb-2">快速选择：</p>
          <div className="flex flex-wrap gap-2">
            {examples.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setTopic(example)}
                className="px-3 py-1 text-sm bg-manim-bg rounded-full hover:bg-gray-700 transition-colors"
                disabled={disabled || loading}
              >
                {example}
              </button>
            ))}
          </div>
        </div>

        {/* 渲染选项 */}
        <div className="flex items-center gap-3">
          <input
            id="render"
            type="checkbox"
            checked={render}
            onChange={(e) => setRender(e.target.checked)}
            className="w-4 h-4 rounded border-gray-600 bg-manim-bg text-manim-accent focus:ring-manim-accent"
            disabled={disabled || loading}
          />
          <label htmlFor="render" className="text-sm">
            生成后自动渲染视频
          </label>
        </div>

        {/* 错误提示 */}
        {error && (
          <div className="p-4 bg-red-900/30 border border-red-500/50 rounded-lg text-manim-error">
            {error}
          </div>
        )}

        {/* 提交按钮 */}
        <button
          type="submit"
          disabled={disabled || loading || !topic.trim()}
          className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-manim-accent text-manim-bg font-semibold rounded-lg hover:opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
        >
          {loading ? (
            <>
              <Loader2 size={20} className="animate-spin" />
              启动中...
            </>
          ) : (
            <>
              <Sparkles size={20} />
              开始生成
            </>
          )}
        </button>
      </form>
    </div>
  );
}
