import React, { useState, useRef, useEffect } from 'react';
import { 
  PlayIcon, 
  PauseIcon, 
  ArrowDownTrayIcon,
  SpeakerWaveIcon,
  SpeakerXMarkIcon
} from '@heroicons/react/24/outline';

const AudioPlayer = ({ taskId, result }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(1);
  const [isMuted, setIsMuted] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  
  const audioRef = useRef(null);
  const progressRef = useRef(null);

  const audioUrl = `/audio/${taskId}`;
  const downloadUrl = `/audio/${taskId}?download=true`;

  useEffect(() => {
    const audio = audioRef.current;
    if (!audio) return;

    const handleLoadedMetadata = () => {
      setDuration(audio.duration);
      setIsLoading(false);
    };

    const handleTimeUpdate = () => {
      setCurrentTime(audio.currentTime);
    };

    const handleEnded = () => {
      setIsPlaying(false);
      setCurrentTime(0);
    };

    const handleError = () => {
      setError('Failed to load audio file');
      setIsLoading(false);
    };

    const handleCanPlay = () => {
      setIsLoading(false);
    };

    audio.addEventListener('loadedmetadata', handleLoadedMetadata);
    audio.addEventListener('timeupdate', handleTimeUpdate);
    audio.addEventListener('ended', handleEnded);
    audio.addEventListener('error', handleError);
    audio.addEventListener('canplay', handleCanPlay);

    return () => {
      audio.removeEventListener('loadedmetadata', handleLoadedMetadata);
      audio.removeEventListener('timeupdate', handleTimeUpdate);
      audio.removeEventListener('ended', handleEnded);
      audio.removeEventListener('error', handleError);
      audio.removeEventListener('canplay', handleCanPlay);
    };
  }, []);

  const togglePlayPause = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isPlaying) {
      audio.pause();
    } else {
      audio.play().catch(err => {
        console.error('Playback failed:', err);
        setError('Playback failed');
      });
    }
    setIsPlaying(!isPlaying);
  };

  const handleProgressClick = (e) => {
    const audio = audioRef.current;
    const progressBar = progressRef.current;
    if (!audio || !progressBar) return;

    const rect = progressBar.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const newTime = (clickX / rect.width) * duration;
    
    audio.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const handleVolumeChange = (e) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (audioRef.current) {
      audioRef.current.volume = newVolume;
    }
    setIsMuted(newVolume === 0);
  };

  const toggleMute = () => {
    const audio = audioRef.current;
    if (!audio) return;

    if (isMuted) {
      audio.volume = volume;
      setIsMuted(false);
    } else {
      audio.volume = 0;
      setIsMuted(true);
    }
  };

  const formatTime = (time) => {
    if (isNaN(time)) return '0:00';
    
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const progressPercentage = duration > 0 ? (currentTime / duration) * 100 : 0;

  if (error) {
    return (
      <div className="card bg-error-50 border-error-200">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-error-900 mb-2">
            Audio Error
          </h3>
          <p className="text-error-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">
          Audio Generated Successfully
        </h3>
        
        {result && (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
            <div>
              <span className="font-medium">Text Length:</span>
              <br />
              {result.text_length?.toLocaleString()} characters
            </div>
            <div>
              <span className="font-medium">Voice:</span>
              <br />
              {result.voice_used || 'Default'}
            </div>
            <div>
              <span className="font-medium">Duration:</span>
              <br />
              {formatTime(duration)}
            </div>
            <div>
              <span className="font-medium">Status:</span>
              <br />
              <span className="text-success-600 font-medium">Ready</span>
            </div>
          </div>
        )}
      </div>

      {/* Audio Element */}
      <audio
        ref={audioRef}
        src={audioUrl}
        preload="metadata"
        className="hidden"
      />

      {/* Custom Audio Controls */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-4">
        {/* Progress Bar */}
        <div className="space-y-2">
          <div
            ref={progressRef}
            className="w-full h-2 bg-gray-200 rounded-full cursor-pointer relative overflow-hidden"
            onClick={handleProgressClick}
            role="slider"
            aria-label="Audio progress"
            aria-valuemin="0"
            aria-valuemax={duration}
            aria-valuenow={currentTime}
            tabIndex="0"
            onKeyDown={(e) => {
              if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                const audio = audioRef.current;
                if (!audio) return;
                
                const step = 10; // 10 seconds
                const newTime = e.key === 'ArrowLeft' 
                  ? Math.max(0, currentTime - step)
                  : Math.min(duration, currentTime + step);
                
                audio.currentTime = newTime;
                setCurrentTime(newTime);
              }
            }}
          >
            <div
              className="h-full bg-primary-600 transition-all duration-100 ease-out"
              style={{ width: `${progressPercentage}%` }}
            />
            {isLoading && (
              <div className="absolute inset-0 bg-gray-300 animate-pulse" />
            )}
          </div>
          
          <div className="flex justify-between text-xs text-gray-500">
            <span>{formatTime(currentTime)}</span>
            <span>{formatTime(duration)}</span>
          </div>
        </div>

        {/* Controls */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {/* Play/Pause Button */}
            <button
              onClick={togglePlayPause}
              disabled={isLoading}
              className="flex items-center justify-center w-12 h-12 bg-primary-600 text-white rounded-full hover:bg-primary-700 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              aria-label={isPlaying ? 'Pause audio' : 'Play audio'}
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : isPlaying ? (
                <PauseIcon className="w-6 h-6" />
              ) : (
                <PlayIcon className="w-6 h-6 ml-0.5" />
              )}
            </button>

            {/* Volume Control */}
            <div className="flex items-center space-x-2">
              <button
                onClick={toggleMute}
                className="text-gray-600 hover:text-gray-900 transition-colors"
                aria-label={isMuted ? 'Unmute audio' : 'Mute audio'}
              >
                {isMuted ? (
                  <SpeakerXMarkIcon className="w-5 h-5" />
                ) : (
                  <SpeakerWaveIcon className="w-5 h-5" />
                )}
              </button>
              
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={isMuted ? 0 : volume}
                onChange={handleVolumeChange}
                className="w-20 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
                aria-label="Volume control"
              />
            </div>
          </div>

          {/* Download Button */}
          <a
            href={downloadUrl}
            download={`audio_${taskId}.wav`}
            className="btn-secondary"
            aria-label="Download audio file"
          >
            <ArrowDownTrayIcon className="w-5 h-5 mr-2" />
            Download
          </a>
        </div>
      </div>

      {/* Accessibility Instructions */}
      <div className="sr-only">
        <p>
          Audio player controls: Use the play/pause button to control playback. 
          Click on the progress bar to seek to a specific time. 
          Use the volume slider to adjust audio level. 
          Download button saves the audio file to your device.
        </p>
      </div>
    </div>
  );
};

export default AudioPlayer;