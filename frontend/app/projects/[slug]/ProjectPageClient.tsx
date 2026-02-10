'use client';

import { useState, useEffect, useCallback, useMemo } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft,
  FileCode,
  FileJson,
  Video,
  BookOpen,
  Clapperboard,
  Film,
  Pencil,
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import dynamic from 'next/dynamic';
import VideoPlayer from '@/components/VideoPlayer';

// 动态导入 Monaco Editor，避免 SSR 问题
const MonacoEditor = dynamic(() => import('@monaco-editor/react'), { ssr: false });
import StoryboardEditor from '@/components/StoryboardEditor';
import RefinerPanel from '@/components/RefinerPanel';
import { ThemeToggle } from '@/components/ThemeToggle';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Separator } from '@/components/ui/separator';
import { Skeleton } from '@/components/ui/skeleton';
import { getStoryboard, getVideos, getScripts, getStaticBaseUrl, updateStoryboard } from '@/lib/api';
import { useTheme } from 'next-themes';
import type { Storyboard, VideoInfo, ScriptInfo, TabType } from '@/lib/types';

export default function ProjectPageClient() {
  const params = useParams();
  const slug = params.slug as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [storyboard, setStoryboard] = useState<Storyboard | null>(null);
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [scripts, setScripts] = useState<ScriptInfo[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>('videos');
  // null = 某个 section，'__all__' = 总视频
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [editingStoryboard, setEditingStoryboard] = useState(false);
  const { resolvedTheme } = useTheme();

  const loadProjectData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [storyboardData, videosData, scriptsData] = await Promise.all([
        getStoryboard(slug),
        getVideos(slug),
        getScripts(slug),
      ]);
      setStoryboard(storyboardData);
      setVideos(videosData.videos || []);
      setScripts(scriptsData.scripts || []);
      if (storyboardData.sections?.length > 0 && !selectedSection) {
        setSelectedSection(storyboardData.sections[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '加载失败');
    } finally {
      setLoading(false);
    }
  }, [slug]);

  useEffect(() => {
    loadProjectData();
  }, [loadProjectData]);

  const handleSaveStoryboard = async (newStoryboard: Storyboard) => {
    await updateStoryboard(slug, newStoryboard);
    setStoryboard(newStoryboard);
  };

  const isAllView = selectedSection === '__all__';
  const currentVideo = isAllView ? null : videos.find((v) => v.section === selectedSection);
  const currentSection = isAllView ? null : storyboard?.sections.find((s) => s.id === selectedSection);
  const currentScript = useMemo(() => {
    if (isAllView || !selectedSection) return null;
    // 匹配 section_1 -> section_1.py
    return scripts.find((s) => s.name === `${selectedSection}.py`) || null;
  }, [scripts, selectedSection, isAllView]);

  // 总视频路径
  const finalVideoPath = `${getStaticBaseUrl()}/${slug}/final_merged.mp4`;

  // --- 加载状态 ---
  if (loading) {
    return (
      <div className="min-h-screen bg-background">
        <header className="sticky top-0 z-30 glass border-b border-border/40">
          <div className="max-w-7xl mx-auto flex items-center justify-between h-14 px-6">
            <Skeleton className="h-5 w-40" />
            <Skeleton className="h-8 w-8 rounded-full" />
          </div>
        </header>
        <div className="max-w-7xl mx-auto p-6 space-y-6">
          <div className="flex gap-2">
            {[1, 2, 3].map((i) => (<Skeleton key={i} className="h-9 w-28 rounded-lg" />))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <Skeleton className="lg:col-span-2 h-80 rounded-xl" />
            <Skeleton className="h-60 rounded-xl" />
          </div>
        </div>
      </div>
    );
  }

  // --- 错误状态 ---
  if (error) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Card className="max-w-md w-full">
          <CardContent className="pt-8 pb-6 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-destructive/10 flex items-center justify-center mx-auto">
              <span className="text-destructive text-xl">!</span>
            </div>
            <p className="text-sm text-muted-foreground">{error}</p>
            <Button asChild variant="outline">
              <Link href="/">返回首页</Link>
            </Button>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      {/* 顶部导航 */}
      <header className="sticky top-0 z-30 glass border-b border-border/40">
        <div className="max-w-7xl mx-auto flex items-center justify-between h-14 px-6">
          <div className="flex items-center gap-3">
            <Button asChild variant="ghost" size="icon" className="h-8 w-8">
              <Link href="/"><ArrowLeft className="h-4 w-4" /></Link>
            </Button>
            <Separator orientation="vertical" className="h-5" />
            <div>
              <h1 className="text-sm font-semibold leading-tight">{storyboard?.topic || slug}</h1>
              <p className="text-xs text-muted-foreground">{storyboard?.sections.length || 0} 个章节</p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-6 py-6">
        {/* 章节选择 */}
        <ScrollArea className="mb-6">
          <div className="flex items-center gap-2 pb-2">
            {/* 总视频按钮 */}
            <button
              onClick={() => setSelectedSection('__all__')}
              className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                isAllView
                  ? 'bg-primary text-primary-foreground shadow-sm'
                  : 'bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground'
              }`}
            >
              <Film className="h-3.5 w-3.5" />
              总视频
            </button>
            <Separator orientation="vertical" className="h-6" />
            {storyboard?.sections.map((section, index) => (
              <button
                key={section.id}
                onClick={() => setSelectedSection(section.id)}
                className={`flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm whitespace-nowrap transition-all ${
                  selectedSection === section.id
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'bg-muted/50 hover:bg-muted text-muted-foreground hover:text-foreground'
                }`}
              >
                <Badge variant="outline" className={`text-[10px] px-1.5 py-0 ${
                  selectedSection === section.id ? 'border-primary-foreground/30 text-primary-foreground' : ''
                }`}>
                  {index + 1}
                </Badge>
                {section.title}
              </button>
            ))}
          </div>
        </ScrollArea>

        {/* 主内容 + 侧栏 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 主内容 */}
          <div className="lg:col-span-2">
            {isAllView ? (
              /* 总视频视图 */
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base flex items-center gap-2">
                    <Film className="h-4 w-4" />
                    完整视频
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <VideoPlayer
                    src={finalVideoPath}
                    title={storyboard?.topic || '完整视频'}
                  />
                </CardContent>
              </Card>
            ) : (
              /* 分镜视图 */
              <Tabs value={activeTab} onValueChange={(v) => setActiveTab(v as TabType)}>
                <TabsList className="mb-4">
                  <TabsTrigger value="videos" className="gap-1.5">
                    <Video className="h-3.5 w-3.5" /> 视频
                  </TabsTrigger>
                  <TabsTrigger value="storyboard" className="gap-1.5">
                    <FileJson className="h-3.5 w-3.5" /> Storyboard
                  </TabsTrigger>
                  <TabsTrigger value="scripts" className="gap-1.5">
                    <FileCode className="h-3.5 w-3.5" /> 代码
                  </TabsTrigger>
                </TabsList>

                <TabsContent value="videos">
                  <AnimatePresence mode="wait">
                    {currentVideo ? (
                      <motion.div
                        key={currentVideo.path}
                        initial={{ opacity: 0, y: 8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        transition={{ duration: 0.2 }}
                      >
                        <VideoPlayer
                          src={currentVideo.path}
                          title={currentSection?.title}
                        />
                      </motion.div>
                    ) : (
                      <Card>
                        <CardContent className="py-16 text-center">
                          <Clapperboard className="h-10 w-10 mx-auto mb-3 text-muted-foreground/40" />
                          <p className="text-sm text-muted-foreground">该章节暂无视频，请先渲染</p>
                        </CardContent>
                      </Card>
                    )}
                  </AnimatePresence>
                </TabsContent>

                <TabsContent value="storyboard">
                  {editingStoryboard && storyboard ? (
                    <div className="space-y-3">
                      <div className="flex justify-end">
                        <Button variant="outline" size="sm" onClick={() => setEditingStoryboard(false)}>
                          完成编辑
                        </Button>
                      </div>
                      <StoryboardEditor
                        storyboard={storyboard}
                        slug={slug}
                        onSave={handleSaveStoryboard}
                      />
                    </div>
                  ) : currentSection ? (
                    <Card>
                      <CardHeader className="pb-3 flex flex-row items-center justify-between">
                        <CardTitle className="text-base">{currentSection.title}</CardTitle>
                        <Button variant="ghost" size="sm" className="gap-1.5 text-xs" onClick={() => setEditingStoryboard(true)}>
                          <Pencil className="h-3 w-3" /> 编辑全部
                        </Button>
                      </CardHeader>
                      <CardContent className="space-y-4 text-sm">
                        <div>
                          <div className="flex items-center gap-1.5 mb-2 text-muted-foreground">
                            <BookOpen className="h-3.5 w-3.5" />
                            <span className="text-xs font-medium">讲义笔记</span>
                          </div>
                          <ul className="space-y-1.5 pl-4">
                            {currentSection.lecture_lines.map((line, i) => (
                              <li key={i} className="text-sm leading-relaxed list-disc marker:text-muted-foreground/50">
                                {line}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <Separator />
                        <div>
                          <div className="flex items-center gap-1.5 mb-2 text-muted-foreground">
                            <Clapperboard className="h-3.5 w-3.5" />
                            <span className="text-xs font-medium">动画描述</span>
                          </div>
                          <ul className="space-y-1.5 pl-4">
                            {currentSection.animations.map((anim, i) => (
                              <li key={i} className="text-sm leading-relaxed list-disc marker:text-primary/50">
                                {anim}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </CardContent>
                    </Card>
                  ) : (
                    <Card>
                      <CardContent className="py-16 text-center">
                        <FileJson className="h-10 w-10 mx-auto mb-3 text-muted-foreground/40" />
                        <p className="text-sm text-muted-foreground">暂无 Storyboard 数据</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>

                <TabsContent value="scripts">
                  {currentScript ? (
                    <Card className="overflow-hidden">
                      <CardHeader className="pb-3 flex flex-row items-center justify-between">
                        <div className="flex items-center gap-2.5">
                          <FileCode className="h-4 w-4 text-primary" />
                          <CardTitle className="text-sm font-medium">{currentScript.name}</CardTitle>
                        </div>
                      </CardHeader>
                      <Separator />
                      <div className="h-[450px]">
                        <MonacoEditor
                          height="100%"
                          language="python"
                          value={currentScript.content}
                          theme={resolvedTheme === 'dark' ? 'vs-dark' : 'light'}
                          options={{
                            readOnly: true,
                            minimap: { enabled: false },
                            fontSize: 13,
                            lineNumbers: 'on',
                            scrollBeyondLastLine: false,
                            wordWrap: 'on',
                            padding: { top: 12, bottom: 12 },
                          }}
                        />
                      </div>
                    </Card>
                  ) : (
                    <Card>
                      <CardContent className="py-16 text-center">
                        <FileCode className="h-10 w-10 mx-auto mb-3 text-muted-foreground/40" />
                        <p className="text-sm text-muted-foreground">该章节暂无脚本</p>
                      </CardContent>
                    </Card>
                  )}
                </TabsContent>
              </Tabs>
            )}
          </div>

          {/* 侧栏 */}
          <div className="space-y-4">
            {/* Refiner 面板 */}
            {!isAllView && selectedSection && currentVideo && (
              <RefinerPanel
                slug={slug}
                sectionId={selectedSection}
                onRefineComplete={loadProjectData}
              />
            )}

            {/* 总览信息 */}
            {isAllView && storyboard && (
              <Card>
                <CardHeader className="pb-3">
                  <CardTitle className="text-base">项目概览</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">主题</span>
                    <span className="font-medium">{storyboard.topic}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">章节数</span>
                    <span className="font-medium">{storyboard.sections.length}</span>
                  </div>
                  <Separator />
                  <div className="flex justify-between">
                    <span className="text-muted-foreground">已渲染</span>
                    <span className="font-medium">{videos.length} / {storyboard.sections.length}</span>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
