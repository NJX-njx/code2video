'use client';

import { useState, useEffect } from 'react';
import { Trash2, Play, FolderOpen, Video, FileCode, AlertTriangle } from 'lucide-react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Skeleton } from '@/components/ui/skeleton';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';
import { getProjects, deleteProject } from '@/lib/api';
import type { Project } from '@/lib/types';

export default function ProjectList() {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [deleteSlug, setDeleteSlug] = useState<string | null>(null);

  const loadProjects = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getProjects();
      setProjects(data.projects);
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadProjects(); }, []);

  const handleDelete = async () => {
    if (!deleteSlug) return;
    try {
      await deleteProject(deleteSlug);
      setDeleteSlug(null);
      loadProjects();
    } catch (err) {
      alert(err instanceof Error ? err.message : '删除失败');
    }
  };

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return '未知';
    return new Date(dateStr).toLocaleDateString('zh-CN', {
      year: 'numeric', month: 'short', day: 'numeric',
      hour: '2-digit', minute: '2-digit',
    });
  };

  if (loading) {
    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-6">
          <Skeleton className="h-8 w-32" />
          <Skeleton className="h-5 w-24" />
        </div>
        {[1, 2, 3].map((i) => (
          <Card key={i}>
            <CardContent className="p-6">
              <div className="flex items-start justify-between">
                <div className="space-y-2">
                  <Skeleton className="h-6 w-48" />
                  <Skeleton className="h-4 w-64" />
                </div>
                <Skeleton className="h-9 w-9 rounded-lg" />
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  if (error) {
    return (
      <Card className="border-destructive/50">
        <CardContent className="p-8 text-center">
          <p className="text-destructive mb-4">{error}</p>
          <Button variant="outline" onClick={loadProjects}>重试</Button>
        </CardContent>
      </Card>
    );
  }

  if (projects.length === 0) {
    return (
      <Card>
        <CardContent className="p-12 text-center">
          <FolderOpen className="h-12 w-12 mx-auto mb-4 text-muted-foreground" />
          <h3 className="text-xl font-semibold mb-2">暂无项目</h3>
          <p className="text-muted-foreground">开始生成你的第一个数学视频吧</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-2">
        <h2 className="text-2xl font-bold tracking-tight">项目列表</h2>
        <span className="text-sm text-muted-foreground">{projects.length} 个项目</span>
      </div>

      <div className="grid gap-3">
        {projects.map((project) => (
          <Card key={project.slug} className="group">
            <CardContent className="p-5">
              <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                  <Link
                    href={`/projects/${project.slug}`}
                    className="text-lg font-semibold hover:text-primary transition-colors"
                  >
                    {project.topic}
                  </Link>
                  <div className="flex items-center gap-3 mt-1.5 text-sm text-muted-foreground">
                    <span className="flex items-center gap-1">
                      <FileCode className="h-3.5 w-3.5" />
                      {project.sections_count} 个章节
                    </span>
                    {project.has_videos ? (
                      <Badge variant="success" className="text-xs">
                        <Video className="h-3 w-3 mr-1" />
                        已渲染
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-xs">待渲染</Badge>
                    )}
                    <span>{formatDate(project.created_at)}</span>
                  </div>
                </div>

                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <Button variant="ghost" size="icon" asChild>
                    <Link href={`/projects/${project.slug}`}>
                      <Play className="h-4 w-4" />
                    </Link>
                  </Button>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="text-muted-foreground hover:text-destructive"
                    onClick={() => setDeleteSlug(project.slug)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* 删除确认弹窗 */}
      <Dialog open={!!deleteSlug} onOpenChange={(open) => !open && setDeleteSlug(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-destructive" />
              确认删除
            </DialogTitle>
            <DialogDescription>
              确定要删除项目 "{deleteSlug}" 吗？此操作不可撤销。
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDeleteSlug(null)}>取消</Button>
            <Button variant="destructive" onClick={handleDelete}>删除</Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
