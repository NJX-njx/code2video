'use client';

import { useState, useEffect, useCallback } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import { 
  ArrowLeft, 
  Play, 
  FileCode, 
  FileJson, 
  Video,
  ChevronDown,
  ChevronUp,
  Eye
} from 'lucide-react';
import VideoPlayer from '@/components/VideoPlayer';
import StoryboardEditor from '@/components/StoryboardEditor';
import RefinerPanel from '@/components/RefinerPanel';

interface Section {
  id: string;
  title: string;
  lecture_lines: string[];
  animations: string[];
}

interface Storyboard {
  topic: string;
  sections: Section[];
}

interface VideoInfo {
  name: string;
  section: string;
  path: string;
}

interface ScriptInfo {
  name: string;
  path: string;
  content: string;
}

type TabType = 'videos' | 'storyboard' | 'scripts';

export default function ProjectPage() {
  const params = useParams();
  const router = useRouter();
  const slug = params.slug as string;

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [storyboard, setStoryboard] = useState<Storyboard | null>(null);
  const [videos, setVideos] = useState<VideoInfo[]>([]);
  const [scripts, setScripts] = useState<ScriptInfo[]>([]);
  const [activeTab, setActiveTab] = useState<TabType>('videos');
  const [selectedSection, setSelectedSection] = useState<string | null>(null);
  const [expandedScript, setExpandedScript] = useState<string | null>(null);

  // 加载项目数据
  const loadProjectData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      // 并行加载数据
      const [storyboardRes, videosRes, scriptsRes] = await Promise.all([
        fetch(`/api/projects/${slug}/storyboard`),
        fetch(`/api/projects/${slug}/videos`),
        fetch(`/api/projects/${slug}/scripts`),
      ]);

      if (!storyboardRes.ok) {
        throw new Error('加载 Storyboard 失败');
      }

      const storyboardData = await storyboardRes.json();
      const videosData = await videosRes.json();
      const scriptsData = await scriptsRes.json();

      setStoryboard(storyboardData);
      setVideos(videosData.videos || []);
      setScripts(scriptsData.scripts || []);

      // 默认选择第一个 section
      if (storyboardData.sections?.length > 0) {
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

  // 保存 Storyboard
  const handleSaveStoryboard = async (newStoryboard: Storyboard) => {
    const response = await fetch(`/api/projects/${slug}/storyboard`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newStoryboard),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || '保存失败');
    }

    setStoryboard(newStoryboard);
  };

  // 获取当前 section 的视频
  const currentVideo = videos.find(v => v.section === selectedSection);
  const currentScript = scripts.find(s => s.name === `${selectedSection}.py`);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-manim-accent border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="bg-red-900/30 border border-red-500/50 rounded-xl p-8 text-center">
          <p className="text-manim-error mb-4">{error}</p>
          <Link
            href="/"
            className="px-4 py-2 bg-manim-surface rounded-lg hover:bg-gray-700"
          >
            返回首页
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-8">
      {/* 顶部导航 */}
      <header className="max-w-7xl mx-auto mb-8">
        <div className="flex items-center gap-4">
          <Link
            href="/"
            className="p-2 hover:bg-manim-surface rounded-lg transition-colors"
          >
            <ArrowLeft size={20} />
          </Link>
          <div>
            <h1 className="text-2xl font-bold">{storyboard?.topic || slug}</h1>
            <p className="text-sm text-gray-400">
              {storyboard?.sections.length || 0} 个章节
            </p>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto">
        {/* 章节选择器 */}
        <div className="bg-manim-surface rounded-xl p-4 mb-6">
          <div className="flex items-center gap-2 overflow-x-auto pb-2">
            {storyboard?.sections.map((section, index) => (
              <button
                key={section.id}
                onClick={() => setSelectedSection(section.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg whitespace-nowrap transition-colors ${
                  selectedSection === section.id
                    ? 'bg-manim-accent text-manim-bg'
                    : 'hover:bg-manim-bg'
                }`}
              >
                <span className="text-sm opacity-60">#{index + 1}</span>
                {section.title}
              </button>
            ))}
          </div>
        </div>

        {/* Tab 切换 */}
        <div className="flex gap-4 mb-6">
          <button
            onClick={() => setActiveTab('videos')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'videos'
                ? 'bg-manim-accent text-manim-bg'
                : 'bg-manim-surface hover:bg-gray-700'
            }`}
          >
            <Video size={18} />
            视频预览
          </button>
          <button
            onClick={() => setActiveTab('storyboard')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'storyboard'
                ? 'bg-manim-accent text-manim-bg'
                : 'bg-manim-surface hover:bg-gray-700'
            }`}
          >
            <FileJson size={18} />
            Storyboard
          </button>
          <button
            onClick={() => setActiveTab('scripts')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              activeTab === 'scripts'
                ? 'bg-manim-accent text-manim-bg'
                : 'bg-manim-surface hover:bg-gray-700'
            }`}
          >
            <FileCode size={18} />
            代码
          </button>
        </div>

        {/* 内容区域 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* 主内容 */}
          <div className="lg:col-span-2">
            {activeTab === 'videos' && (
              <div className="space-y-4">
                {currentVideo ? (
                  <VideoPlayer
                    src={currentVideo.path}
                    title={storyboard?.sections.find(s => s.id === selectedSection)?.title}
                  />
                ) : (
                  <div className="bg-manim-surface rounded-xl p-12 text-center">
                    <Video size={48} className="mx-auto mb-4 text-gray-500" />
                    <p className="text-gray-400">
                      该章节暂无视频，请先渲染
                    </p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'storyboard' && storyboard && (
              <StoryboardEditor
                storyboard={storyboard}
                slug={slug}
                onSave={handleSaveStoryboard}
              />
            )}

            {activeTab === 'scripts' && (
              <div className="space-y-4">
                {scripts.length === 0 ? (
                  <div className="bg-manim-surface rounded-xl p-12 text-center">
                    <FileCode size={48} className="mx-auto mb-4 text-gray-500" />
                    <p className="text-gray-400">暂无生成的脚本</p>
                  </div>
                ) : (
                  scripts.map((script) => (
                    <div
                      key={script.name}
                      className="bg-manim-surface rounded-xl overflow-hidden"
                    >
                      <div
                        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-700/50"
                        onClick={() =>
                          setExpandedScript(
                            expandedScript === script.name ? null : script.name
                          )
                        }
                      >
                        <div className="flex items-center gap-3">
                          <FileCode size={18} className="text-manim-accent" />
                          <span className="font-medium">{script.name}</span>
                        </div>
                        {expandedScript === script.name ? (
                          <ChevronUp size={18} />
                        ) : (
                          <ChevronDown size={18} />
                        )}
                      </div>
                      {expandedScript === script.name && (
                        <div className="border-t border-gray-700">
                          <pre className="p-4 bg-manim-bg overflow-x-auto text-sm">
                            <code className="text-gray-300">{script.content}</code>
                          </pre>
                        </div>
                      )}
                    </div>
                  ))
                )}
              </div>
            )}
          </div>

          {/* 侧边栏 */}
          <div className="space-y-6">
            {/* 章节信息 */}
            {selectedSection && storyboard && (
              <div className="bg-manim-surface rounded-xl p-6">
                <h3 className="font-semibold mb-4">
                  {storyboard.sections.find(s => s.id === selectedSection)?.title}
                </h3>
                
                <div className="space-y-4 text-sm">
                  <div>
                    <p className="text-gray-400 mb-2">讲义笔记：</p>
                    <ul className="list-disc list-inside space-y-1">
                      {storyboard.sections
                        .find(s => s.id === selectedSection)
                        ?.lecture_lines.map((line, i) => (
                          <li key={i}>{line}</li>
                        ))}
                    </ul>
                  </div>
                  
                  <div>
                    <p className="text-gray-400 mb-2">动画描述：</p>
                    <ul className="list-disc list-inside space-y-1">
                      {storyboard.sections
                        .find(s => s.id === selectedSection)
                        ?.animations.map((anim, i) => (
                          <li key={i}>{anim}</li>
                        ))}
                    </ul>
                  </div>
                </div>
              </div>
            )}

            {/* Refiner 面板 */}
            {selectedSection && currentVideo && (
              <RefinerPanel
                slug={slug}
                sectionId={selectedSection}
                onRefineComplete={loadProjectData}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
