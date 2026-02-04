'use client';

import { useRef, useState } from 'react';
import { Play, Pause, Volume2, VolumeX, Maximize } from 'lucide-react';

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
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      const current = videoRef.current.currentTime;
      const total = videoRef.current.duration;
      setProgress((current / total) * 100);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setDuration(videoRef.current.duration);
    }
  };

  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (videoRef.current) {
      const rect = e.currentTarget.getBoundingClientRect();
      const pos = (e.clientX - rect.left) / rect.width;
      videoRef.current.currentTime = pos * videoRef.current.duration;
    }
  };

  const handleFullscreen = () => {
    if (videoRef.current) {
      if (document.fullscreenElement) {
        document.exitFullscreen();
      } else {
        videoRef.current.requestFullscreen();
      }
    }
  };

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div className="bg-manim-bg rounded-xl overflow-hidden">
      {title && (
        <div className="px-4 py-2 border-b border-gray-700">
          <h4 className="font-medium text-sm">{title}</h4>
        </div>
      )}
      
      <div className="relative group">
        <video
          ref={videoRef}
          src={src}
          className="w-full aspect-video bg-black"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onEnded={() => setIsPlaying(false)}
          onClick={togglePlay}
        />

        {/* 控制栏 */}
        <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/80 to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity">
          {/* 进度条 */}
          <div
            className="h-1 bg-gray-600 rounded-full cursor-pointer mb-3"
            onClick={handleSeek}
          >
            <div
              className="h-full bg-manim-accent rounded-full"
              style={{ width: `${progress}%` }}
            />
          </div>

          {/* 控制按钮 */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <button
                onClick={togglePlay}
                className="p-1 hover:text-manim-accent transition-colors"
              >
                {isPlaying ? <Pause size={20} /> : <Play size={20} />}
              </button>
              <button
                onClick={toggleMute}
                className="p-1 hover:text-manim-accent transition-colors"
              >
                {isMuted ? <VolumeX size={20} /> : <Volume2 size={20} />}
              </button>
              <span className="text-sm text-gray-400">
                {formatTime((progress / 100) * duration)} / {formatTime(duration)}
              </span>
            </div>

            <button
              onClick={handleFullscreen}
              className="p-1 hover:text-manim-accent transition-colors"
            >
              <Maximize size={20} />
            </button>
          </div>
        </div>

        {/* 播放按钮覆盖层 */}
        {!isPlaying && (
          <div
            className="absolute inset-0 flex items-center justify-center cursor-pointer"
            onClick={togglePlay}
          >
            <div className="w-16 h-16 bg-manim-accent/80 rounded-full flex items-center justify-center hover:bg-manim-accent transition-colors">
              <Play size={32} className="text-manim-bg ml-1" />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
