'use client';

import { useState } from 'react';
import { Save, RotateCcw, Plus, Trash2, ChevronDown, ChevronUp, GripVertical } from 'lucide-react';
import { Card, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import type { Storyboard } from '@/lib/types';

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

  const toggleSection = (id: string) => {
    const next = new Set(expandedSections);
    next.has(id) ? next.delete(id) : next.add(id);
    setExpandedSections(next);
  };

  const updateTopic = (topic: string) => {
    setStoryboard({ ...storyboard, topic });
    setHasChanges(true);
  };

  const updateSectionTitle = (id: string, title: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s => s.id === id ? { ...s, title } : s),
    });
    setHasChanges(true);
  };

  const updateLectureLine = (sectionId: string, index: number, value: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? { ...s, lecture_lines: s.lecture_lines.map((l, i) => (i === index ? value : l)) }
          : s
      ),
    });
    setHasChanges(true);
  };

  const addLectureLine = (sectionId: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId ? { ...s, lecture_lines: [...s.lecture_lines, ''] } : s
      ),
    });
    setHasChanges(true);
  };

  const removeLectureLine = (sectionId: string, index: number) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId ? { ...s, lecture_lines: s.lecture_lines.filter((_, i) => i !== index) } : s
      ),
    });
    setHasChanges(true);
  };

  const updateAnimation = (sectionId: string, index: number, value: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId
          ? { ...s, animations: s.animations.map((a, i) => (i === index ? value : a)) }
          : s
      ),
    });
    setHasChanges(true);
  };

  const addAnimation = (sectionId: string) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId ? { ...s, animations: [...s.animations, ''] } : s
      ),
    });
    setHasChanges(true);
  };

  const removeAnimation = (sectionId: string, index: number) => {
    setStoryboard({
      ...storyboard,
      sections: storyboard.sections.map(s =>
        s.id === sectionId ? { ...s, animations: s.animations.filter((_, i) => i !== index) } : s
      ),
    });
    setHasChanges(true);
  };

  const addSection = () => {
    const newId = `section_${storyboard.sections.length + 1}`;
    setStoryboard({
      ...storyboard,
      sections: [...storyboard.sections, { id: newId, title: '新章节', lecture_lines: [''], animations: [''] }],
    });
    setExpandedSections(new Set([...expandedSections, newId]));
    setHasChanges(true);
  };

  const removeSection = (id: string) => {
    setStoryboard({ ...storyboard, sections: storyboard.sections.filter(s => s.id !== id) });
    setHasChanges(true);
  };

  const handleSave = async () => {
    setSaving(true);
    try { await onSave(storyboard); setHasChanges(false); }
    catch (e) { alert('保存失败: ' + (e instanceof Error ? e.message : '未知错误')); }
    finally { setSaving(false); }
  };

  const handleReset = () => {
    setStoryboard(initialStoryboard);
    setHasChanges(false);
  };

  return (
    <div className="space-y-4">
      {/* 工具栏 */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <span className="text-sm text-muted-foreground">
            {storyboard.sections.length} 个章节
          </span>
          {hasChanges && (
            <Badge variant="warning" className="text-xs">未保存</Badge>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button variant="ghost" size="sm" onClick={handleReset} disabled={!hasChanges || saving}>
            <RotateCcw className="h-4 w-4 mr-1.5" />
            重置
          </Button>
          <Button size="sm" onClick={handleSave} disabled={!hasChanges || saving}>
            <Save className="h-4 w-4 mr-1.5" />
            {saving ? '保存中...' : '保存'}
          </Button>
        </div>
      </div>

      {/* 主题 */}
      <Card>
        <CardContent className="p-4">
          <label className="text-xs font-medium text-muted-foreground mb-1.5 block">主题</label>
          <Input value={storyboard.topic} onChange={(e) => updateTopic(e.target.value)} />
        </CardContent>
      </Card>

      {/* 章节列表 */}
      <div className="space-y-3">
        {storyboard.sections.map((section, sIdx) => (
          <Card key={section.id}>
            {/* 章节头 */}
            <div
              className="flex items-center justify-between p-4 cursor-pointer hover:bg-accent/50 transition-colors rounded-t-xl"
              onClick={() => toggleSection(section.id)}
            >
              <div className="flex items-center gap-2.5">
                <GripVertical className="h-4 w-4 text-muted-foreground/50" />
                {expandedSections.has(section.id) ? (
                  <ChevronUp className="h-4 w-4 text-muted-foreground" />
                ) : (
                  <ChevronDown className="h-4 w-4 text-muted-foreground" />
                )}
                <Badge variant="outline" className="text-xs font-mono">
                  {sIdx + 1}
                </Badge>
                <span className="font-medium">{section.title}</span>
              </div>
              <Button
                variant="ghost"
                size="icon"
                className="h-8 w-8 text-muted-foreground hover:text-destructive"
                onClick={(e) => { e.stopPropagation(); removeSection(section.id); }}
              >
                <Trash2 className="h-3.5 w-3.5" />
              </Button>
            </div>

            {/* 章节内容 */}
            {expandedSections.has(section.id) && (
              <CardContent className="pt-0 pb-4 space-y-4 border-t border-border">
                <div className="pt-4">
                  <label className="text-xs font-medium text-muted-foreground mb-1.5 block">标题</label>
                  <Input
                    value={section.title}
                    onChange={(e) => updateSectionTitle(section.id, e.target.value)}
                  />
                </div>

                {/* 讲义笔记 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-medium text-muted-foreground">讲义笔记</label>
                    <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => addLectureLine(section.id)}>
                      <Plus className="h-3 w-3 mr-1" />
                      添加
                    </Button>
                  </div>
                  <div className="space-y-1.5">
                    {section.lecture_lines.map((line, i) => (
                      <div key={i} className="flex items-center gap-1.5">
                        <Input
                          value={line}
                          onChange={(e) => updateLectureLine(section.id, i, e.target.value)}
                          placeholder={`笔记 ${i + 1}`}
                          className="h-9 text-sm"
                        />
                        <Button variant="ghost" size="icon" className="h-9 w-9 shrink-0 text-muted-foreground hover:text-destructive"
                          onClick={() => removeLectureLine(section.id, i)}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>

                {/* 动画描述 */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <label className="text-xs font-medium text-muted-foreground">动画描述</label>
                    <Button variant="ghost" size="sm" className="h-7 text-xs" onClick={() => addAnimation(section.id)}>
                      <Plus className="h-3 w-3 mr-1" />
                      添加
                    </Button>
                  </div>
                  <div className="space-y-1.5">
                    {section.animations.map((anim, i) => (
                      <div key={i} className="flex items-center gap-1.5">
                        <Input
                          value={anim}
                          onChange={(e) => updateAnimation(section.id, i, e.target.value)}
                          placeholder={`动画 ${i + 1}`}
                          className="h-9 text-sm"
                        />
                        <Button variant="ghost" size="icon" className="h-9 w-9 shrink-0 text-muted-foreground hover:text-destructive"
                          onClick={() => removeAnimation(section.id, i)}>
                          <Trash2 className="h-3.5 w-3.5" />
                        </Button>
                      </div>
                    ))}
                  </div>
                </div>
              </CardContent>
            )}
          </Card>
        ))}
      </div>

      {/* 添加章节 */}
      <button
        onClick={addSection}
        className="w-full flex items-center justify-center gap-2 py-4 border-2 border-dashed border-border rounded-xl text-muted-foreground hover:text-foreground hover:border-primary transition-colors"
      >
        <Plus className="h-5 w-5" />
        添加新章节
      </button>
    </div>
  );
}
