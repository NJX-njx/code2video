'use client';

import { useState } from 'react';
import { Save, RotateCcw, Plus, Trash2, ChevronDown, ChevronUp } from 'lucide-react';

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

interface StoryboardEditorProps {
  storyboard: Storyboard;
  slug: string;
  onSave: (storyboard: Storyboard) => Promise<void>;
}

export default function StoryboardEditor({ storyboard: initialStoryboard, slug, onSave }: StoryboardEditorProps) {
  const [storyboard, setStoryboard] = useState<Storyboard>(initialStoryboard);
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());
  const [saving, setSaving] = useState(false);
  const [hasChanges, setHasChanges] = useState(false);

  // 切换章节展开/折叠
  const toggleSection = (id: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(id)) {
      newExpanded.delete(id);
    } else {
      newExpanded.add(id);
    }
    setExpandedSections(newExpanded);
  };

  // 更新主题
  const updateTopic = (topic: string) => {
    setStoryboard({ ...storyboard, topic });
    setHasChanges(true);
  };

  // 更新章节标题
  const updateSectionTitle = (id: string, title: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === id ? { ...s, title } : s
      ),
    });
    setHasChanges(true);
  };

  // 更新讲义笔记
  const updateLectureLine = (sectionId: string, index: number, value: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? {
              ...s,
              lecture_lines: s.lecture_lines.map((l, i) => (i === index ? value : l)),
            }
          : s
      ),
    });
    setHasChanges(true);
  };

  // 添加讲义笔记
  const addLectureLine = (sectionId: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? { ...s, lecture_lines: [...s.lecture_lines, ''] }
          : s
      ),
    });
    setHasChanges(true);
  };

  // 删除讲义笔记
  const removeLectureLine = (sectionId: string, index: number) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? { ...s, lecture_lines: s.lecture_lines.filter((_, i) => i !== index) }
          : s
      ),
    });
    setHasChanges(true);
  };

  // 更新动画描述
  const updateAnimation = (sectionId: string, index: number, value: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? {
              ...s,
              animations: s.animations.map((a, i) => (i === index ? value : a)),
            }
          : s
      ),
    });
    setHasChanges(true);
  };

  // 添加动画描述
  const addAnimation = (sectionId: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? { ...s, animations: [...s.animations, ''] }
          : s
      ),
    });
    setHasChanges(true);
  };

  // 删除动画描述
  const removeAnimation = (sectionId: string, index: number) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? { ...s, animations: s.animations.filter((_, i) => i !== index) }
          : s
      ),
    });
    setHasChanges(true);
  };

  // 添加新章节
  const addSection = () => {
    const newId = `section_${storyboard.sections.length + 1}`;
    setStoryboard({
      ...storyboard,
      sections: [
        ...storyboard.sections,
        {
          id: newId,
          title: '新章节',
          lecture_lines: [''],
          animations: [''],
        },
      ],
    });
    setExpandedSections(new Set([...expandedSections, newId]));
    setHasChanges(true);
  };

  // 删除章节
  const removeSection = (id: string) => {
    if (!confirm('确定要删除这个章节吗？')) return;
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.filter(s => s.id !== id),
    });
    setHasChanges(true);
  };

  // 保存
  const handleSave = async () => {
    setSaving(true);
    try {
      await onSave(storyboard);
      setHasChanges(false);
    } catch (error) {
      alert('保存失败: ' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setSaving(false);
    }
  };

  // 重置
  const handleReset = () => {
    if (!confirm('确定要放弃所有更改吗？')) return;
    setStoryboard(initialStoryboard);
    setHasChanges(false);
  };

  return (
    <div className="space-y-6">
      {/* 工具栏 */}
      <div className="flex items-center justify-between bg-manim-surface rounded-xl p-4">
        <div className="flex items-center gap-4">
          <span className="text-sm text-gray-400">
            {storyboard.sections.length} 个章节
          </span>
          {hasChanges && (
            <span className="text-sm text-manim-warning">● 有未保存的更改</span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <button
            onClick={handleReset}
            disabled={!hasChanges || saving}
            className="flex items-center gap-2 px-4 py-2 text-gray-400 hover:text-white hover:bg-manim-bg rounded-lg disabled:opacity-50 transition-colors"
          >
            <RotateCcw size={16} />
            重置
          </button>
          <button
            onClick={handleSave}
            disabled={!hasChanges || saving}
            className="flex items-center gap-2 px-4 py-2 bg-manim-accent text-manim-bg rounded-lg hover:opacity-90 disabled:opacity-50 transition-opacity"
          >
            <Save size={16} />
            {saving ? '保存中...' : '保存'}
          </button>
        </div>
      </div>

      {/* 主题编辑 */}
      <div className="bg-manim-surface rounded-xl p-4">
        <label className="block text-sm font-medium mb-2">主题</label>
        <input
          type="text"
          value={storyboard.topic}
          onChange={(e) => updateTopic(e.target.value)}
          className="w-full px-4 py-2 bg-manim-bg border border-gray-700 rounded-lg focus:outline-none focus:border-manim-accent"
        />
      </div>

      {/* 章节列表 */}
      <div className="space-y-4">
        {storyboard.sections.map((section, sectionIndex) => (
          <div key={section.id} className="bg-manim-surface rounded-xl overflow-hidden">
            {/* 章节头部 */}
            <div
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-700/50"
              onClick={() => toggleSection(section.id)}
            >
              <div className="flex items-center gap-3">
                {expandedSections.has(section.id) ? (
                  <ChevronUp size={20} />
                ) : (
                  <ChevronDown size={20} />
                )}
                <span className="text-sm text-gray-400">#{sectionIndex + 1}</span>
                <span className="font-medium">{section.title}</span>
              </div>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  removeSection(section.id);
                }}
                className="p-2 text-gray-400 hover:text-manim-error hover:bg-red-900/30 rounded-lg transition-colors"
              >
                <Trash2 size={16} />
              </button>
            </div>

            {/* 章节内容 */}
            {expandedSections.has(section.id) && (
              <div className="p-4 pt-0 space-y-4 border-t border-gray-700">
                {/* 标题 */}
                <div>
                  <label className="block text-sm font-medium mb-2">标题</label>
                  <input
                    type="text"
                    value={section.title}
                    onChange={(e) => updateSectionTitle(section.id, e.target.value)}
                    className="w-full px-4 py-2 bg-manim-bg border border-gray-700 rounded-lg focus:outline-none focus:border-manim-accent"
                  />
                </div>

                {/* 讲义笔记 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium">讲义笔记</label>
                    <button
                      onClick={() => addLectureLine(section.id)}
                      className="flex items-center gap-1 text-sm text-manim-accent hover:underline"
                    >
                      <Plus size={14} />
                      添加
                    </button>
                  </div>
                  <div className="space-y-2">
                    {section.lecture_lines.map((line, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <input
                          type="text"
                          value={line}
                          onChange={(e) => updateLectureLine(section.id, index, e.target.value)}
                          placeholder={`笔记 ${index + 1}`}
                          className="flex-1 px-4 py-2 bg-manim-bg border border-gray-700 rounded-lg focus:outline-none focus:border-manim-accent"
                        />
                        <button
                          onClick={() => removeLectureLine(section.id, index)}
                          className="p-2 text-gray-400 hover:text-manim-error transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 动画描述 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-sm font-medium">动画描述</label>
                    <button
                      onClick={() => addAnimation(section.id)}
                      className="flex items-center gap-1 text-sm text-manim-accent hover:underline"
                    >
                      <Plus size={14} />
                      添加
                    </button>
                  </div>
                  <div className="space-y-2">
                    {section.animations.map((anim, index) => (
                      <div key={index} className="flex items-center gap-2">
                        <input
                          type="text"
                          value={anim}
                          onChange={(e) => updateAnimation(section.id, index, e.target.value)}
                          placeholder={`动画 ${index + 1}`}
                          className="flex-1 px-4 py-2 bg-manim-bg border border-gray-700 rounded-lg focus:outline-none focus:border-manim-accent"
                        />
                        <button
                          onClick={() => removeAnimation(section.id, index)}
                          className="p-2 text-gray-400 hover:text-manim-error transition-colors"
                        >
                          <Trash2 size={14} />
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* 添加章节按钮 */}
      <button
        onClick={addSection}
        className="w-full flex items-center justify-center gap-2 py-4 border-2 border-dashed border-gray-600 rounded-xl text-gray-400 hover:text-white hover:border-manim-accent transition-colors"
      >
        <Plus size={20} />
        添加新章节
      </button>
    </div>
  );
}
