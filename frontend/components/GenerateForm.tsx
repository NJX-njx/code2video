'use client';

import { useState, useRef } from 'react';
import { Sparkles, Loader2, Upload, X, ImageIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Switch } from '@/components/ui/switch';
import { startGeneration } from '@/lib/api';

interface GenerateFormProps {
  onGenerateStart: (taskId: string) => void;
  disabled?: boolean;
}

export default function GenerateForm({ onGenerateStart, disabled }: GenerateFormProps) {
  const [prompt, setPrompt] = useState('');
  const [render, setRender] = useState(true);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const examples = [
    '勾股定理的证明',
    '圆面积公式推导',
    '二次函数图像',
    '等差数列通项',
    '正弦定理证明',
  ];

  const handleImageSelect = (file: File) => {
    setImageFile(file);
    const reader = new FileReader();
    reader.onload = (e) => setImagePreview(e.target?.result as string);
    reader.readAsDataURL(file);
  };

  const clearImage = () => {
    setImageFile(null);
    setImagePreview(null);
    if (fileInputRef.current) fileInputRef.current.value = '';
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const file = e.dataTransfer.files[0];
    if (file?.type.startsWith('image/')) handleImageSelect(file);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim() && !imageFile) {
      setError('请输入文本或上传图片');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const data = await startGeneration(prompt.trim(), render, imageFile);
      onGenerateStart(data.task_id!);
    } catch (err) {
      const msg = err instanceof Error ? err.message : '未知错误';
      // "Failed to fetch" 通常表示后端不可达或网络问题
      if (msg === 'Failed to fetch') {
        setError('无法连接到后端服务，请确认后端已启动 (端口 8000)');
      } else {
        setError(msg);
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="border-dashed">
      <CardContent className="p-6 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-5">
          {/* 输入区 */}
          <div>
            <Textarea
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              placeholder="输入数学主题、问题或描述..."
              className="min-h-[100px] text-base"
              disabled={disabled || loading}
            />
          </div>

          {/* 快速示例 */}
          <div className="flex flex-wrap gap-2">
            {examples.map((ex) => (
              <Badge
                key={ex}
                variant="outline"
                className="cursor-pointer hover:bg-accent transition-colors py-1"
                onClick={() => setPrompt(ex)}
              >
                {ex}
              </Badge>
            ))}
          </div>

          {/* 图片上传区 */}
          <div
            onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
            onDragLeave={() => setIsDragging(false)}
            onDrop={handleDrop}
            className={`relative rounded-lg border-2 border-dashed transition-colors ${
              isDragging
                ? 'border-primary bg-primary/5'
                : 'border-border hover:border-muted-foreground/50'
            } ${imagePreview ? 'p-3' : 'p-6'}`}
          >
            {imagePreview ? (
              <div className="flex items-center gap-3">
                <img
                  src={imagePreview}
                  alt="预览"
                  className="h-16 w-16 rounded-md object-cover"
                />
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{imageFile?.name}</p>
                  <p className="text-xs text-muted-foreground">
                    {((imageFile?.size ?? 0) / 1024).toFixed(1)} KB
                  </p>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  onClick={clearImage}
                  className="shrink-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            ) : (
              <div
                className="flex flex-col items-center gap-2 cursor-pointer text-muted-foreground"
                onClick={() => fileInputRef.current?.click()}
              >
                <ImageIcon className="h-8 w-8" />
                <p className="text-sm">拖拽图片到这里，或点击上传</p>
              </div>
            )}
            <input
              ref={fileInputRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) handleImageSelect(file);
              }}
              disabled={disabled || loading}
            />
          </div>

          {/* 底部操作栏 */}
          <div className="flex items-center justify-between pt-2">
            <label className="flex items-center gap-2.5 cursor-pointer">
              <Switch
                checked={render}
                onCheckedChange={setRender}
                disabled={disabled || loading}
              />
              <span className="text-sm text-muted-foreground">自动渲染视频</span>
            </label>

            <Button
              type="submit"
              disabled={disabled || loading || (!prompt.trim() && !imageFile)}
              size="lg"
            >
              {loading ? (
                <>
                  <Loader2 className="h-4 w-4 animate-spin mr-2" />
                  启动中...
                </>
              ) : (
                <>
                  <Sparkles className="h-4 w-4 mr-2" />
                  开始生成
                </>
              )}
            </Button>
          </div>

          {/* 错误提示 */}
          {error && (
            <div className="p-3 rounded-lg bg-destructive/10 border border-destructive/30 text-destructive text-sm">
              {error}
            </div>
          )}
        </form>
      </CardContent>
    </Card>
  );
}
