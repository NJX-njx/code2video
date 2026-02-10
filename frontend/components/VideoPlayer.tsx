'use client';

import { useRef, useState } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react';
import { Card } from '@/components/ui/card';

interface VideoPlayerProps {
  src: string;
  title?: string;
}

export default function VideoPlayer({ src, title }: VideoPlayerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isMuted, setIsMuted] = useState(false);
  const [progress, setProgress] = useState(0);
  const [duration, setDuration] = useState(0);

  const togglePlay = () => {
    if (!videoRef.current) return;
    if (isPlaying) videoRef.current.pause();
    else videoRef.current.play();
    setIsPlaying(!isPlaying);
  };

  const toggleMute = () => {
    if (!videoRef.current) return;
    videoRef.current.muted = !isMuted;
    setIsMuted(!isMuted);
  };

  const handleTimeUpdate = () => {
    if (!videoRef.current) return;
    setProgress((videoRef.current.currentTime / videoRef.current.duration) * 100);
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!videoRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    videoRef.current.currentTime = ((e.clientX - rect.left) / rect.width) * videoRef.current.duration;
  };

  const handleFullscreen = () => {
    if (!videoRef.current) return;
    document.fullscreenElement ? document.exitFullscreen() : videoRef.current.requestFullscreen();
  };

  const formatTime = (s: number) => {
    const mins = Math.floor(s / 60);
    const secs = Math.floor(s % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <Card className="overflow-hidden">
      {title && (
        <div className="px-4 py-2.5 border-b border-border">
          <h4 className="font-medium text-sm">{title}</h4>
        </div>
      )}

      <div className="relative group bg-black">
        <video
          ref={videoRef}
          src={src}
          className="w-full aspect-video"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={() => setDuration(videoRef.current?.duration ?? 0)}
          onEnded={() => setIsPlaying(false)}
          onClick={togglePlay}
        />

        {/* 控制栏 — 毛玻璃 */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          {/* 进度条 */}
          <div
            className="h-1 bg-white/20 rounded-full cursor-pointer mb-3 group/bar"
            onClick={handleSeek}
          >
            <div
              className="h-full bg-primary rounded-full relative"
              style={{ width: `${progress}%` }}
            >
              <div className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-white shadow-md opacity-0 group-hover/bar:opacity-100 transition-opacity" />
            </div>
          </div>

          <div className="flex items-center justify-between text-white">
            <div className="flex items-center gap-2">
              <button onClick={togglePlay} className="p-1 hover:text-primary transition-colors">
                {isPlaying ? <Pause className="h-5 w-5" /> : <Play className="h-5 w-5" />}
              </button>
              <button onClick={toggleMute} className="p-1 hover:text-primary transition-colors">
                {isMuted ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
              </button>
              <span className="text-xs text-white/70 ml-1">
                {formatTime((progress / 100) * duration)} / {formatTime(duration)}
              </span>
            </div>
            <button onClick={handleFullscreen} className="p-1 hover:text-primary transition-colors">
              <Maximize className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* 播放按钮覆盖 */}
        {!isPlaying && (
          <div
            className="absolute inset-0 flex items-center justify-center cursor-pointer"
            onClick={togglePlay}
          >
            <div className="w-16 h-16 rounded-full bg-primary/90 flex items-center justify-center hover:scale-110 transition-transform shadow-2xl">
              <Play className="h-7 w-7 text-primary-foreground ml-1" />
            </div>
          </div>
        )}
      </div>
    </Card>
  );
}
