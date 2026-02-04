'use client';

import { useState, useEffect } from 'react';
import { Trash2, Play, FolderOpen, Video, FileCode } from 'lucide-react';
import Link from 'next/link';

interface Project {
  slug: string;
  topic: string;
  created_at: string | null;
  sections_count: number;
  has_videos: boolean;
}

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // 加载项目列表
  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch('/api/projects/');
      if (!response.ok) {
        throw new Error('加载项目列表失败');
      }
      const data = await response.json();
      setProjects(data.projects);
    } catch (err) {
      setError(err instanceof Error ? err.message : '未知错误');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadProjects();
  }, []);

  // 删除项目
  const handleDelete = async (slug: string) => {
    if (!confirm(`确定要删除项目 "${slug}" 吗？此操作不可撤销。`)) {
      return;
    }

    try {
      const response = await fetch(`/api/projects/${slug}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) {
        throw new Error('删除失败');
      }
      
      // 重新加载列表
      loadProjects();
    } catch (err) {
      alert(err instanceof Error ? err.message : '删除失败');
    }
  };

  // 格式化日期
  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '未知';
    const date = new Date(dateStr);
    return date.toLocaleDateString('zh-CN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="w-8 h-8 border-2 border-manim-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-6 text-center">
        <p className="text-manim-error mb-4">{error}</p>
        <button
          onClick={loadProjects}
          className="px-4 py-2 bg-manim-surface rounded-lg hover:bg-gray-700"
        >
          重试
        </button>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="bg-manim-surface rounded-xl p-12 text-center">
        <FolderOpen size={48} className="mx-auto mb-4 text-gray-500" />
        <h3 className="text-xl font-semibold mb-2">暂无项目</h3>
        <p className="text-gray-400">
          开始生成你的第一个数学视频吧！
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold">项目列表</h2>
        <span className="text-gray-400">共 {projects.length} 个项目</span>
      </div>

      <div className="grid gap-4">
        {projects.map((project) => (
          <div
            key={project.slug}
            className="bg-manim-surface rounded-xl p-6 hover:bg-gray-700/50 transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <Link 
                  href={`/projects/${project.slug}`}
                  className="text-xl font-semibold text-manim-accent hover:underline"
                >
                  {project.topic}
                </Link>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                  <span className="flex items-center gap-1">
                    <FileCode size={14} />
                    {project.sections_count} 个章节
                  </span>
                  {project.has_videos && (
                    <span className="flex items-center gap-1 text-manim-success">
                      <Video size={14} />
                      已渲染
                    </span>
                  )}
                  <span>{formatDate(project.created_at)}</span>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Link
                  href={`/projects/${project.slug}`}
                  className="p-2 hover:bg-manim-bg rounded-lg transition-colors"
                  title="查看详情"
                >
                  <Play size={18} />
                </Link>
                <button
                  onClick={() => handleDelete(project.slug)}
                  className="p-2 hover:bg-red-900/50 rounded-lg transition-colors text-gray-400 hover:text-manim-error"
                  title="删除项目"
                >
                  <Trash2 size={18} />
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
