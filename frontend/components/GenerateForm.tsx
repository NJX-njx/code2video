'use client';

import { useState } from 'react';
import { Sparkles, Loader2 } from 'lucide-react';

interface GenerateFormProps {
  onGenerateStart: (taskId: string) => void;
  disabled?: boolean;
}

export default function GenerateForm({ onGenerateStart, disabled }: GenerateFormProps) {
  const [prompt, setPrompt] = useState('');
  const [render, setRender] = useState(true);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // 示例输入
  const examples = [
    '请讲解勾股定理的证明思路',
    '已知圆的半径为 r，解释圆面积公式的来源',
    '这张图里的三角形面积如何计算？',
    '解释二次函数顶点与对称轴',
    '给出等差数列通项公式的推导',
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!prompt.trim() && !imageFile) {
      setError('请输入文本或上传图片');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      let response: Response;
      if (imageFile) {
        const formData = new FormData();
        formData.append('prompt', prompt.trim());
        formData.append('render', render ? 'true' : 'false');
        formData.append('image', imageFile);
        response = await fetch('/api/generate/', {
          method: 'POST',
          body: formData,
        });
      } else {
        response = await fetch('/api/generate/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ prompt: prompt.trim(), render }),
        });
      }

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
          <label htmlFor="prompt" className="block text-sm font-medium mb-2">
            输入内容（主题/问题/描述）
          </label>
          <textarea
            id="prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            placeholder="例如：请解释勾股定理的证明步骤，或描述一个题目场景..."
            className="w-full min-h-[96px] px-4 py-3 bg-manim-bg border border-gray-700 rounded-lg focus:outline-none focus:border-manim-accent transition-colors"
            disabled={disabled || loading}
          />
        </div>

        {/* 图片输入 */}
        <div>
          <label htmlFor="image" className="block text-sm font-medium mb-2">
            上传图片（可选）
          </label>
          <input
            id="image"
            type="file"
            accept="image/*"
            onChange={(e) => setImageFile(e.target.files?.[0] ?? null)}
            className="block w-full text-sm text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-manim-bg file:text-gray-200 hover:file:bg-gray-700"
            disabled={disabled || loading}
          />
          {imageFile && (
            <p className="mt-2 text-xs text-gray-400">
              已选择：{imageFile.name}
            </p>
          )}
        </div>

        {/* 快速选择示例 */}
        <div>
          <p className="text-sm text-gray-400 mb-2">快速选择：</p>
          <div className="flex flex-wrap gap-2">
            {examples.map((example) => (
              <button
                key={example}
                type="button"
                onClick={() => setPrompt(example)}
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
          disabled={disabled || loading || (!prompt.trim() && !imageFile)}
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
