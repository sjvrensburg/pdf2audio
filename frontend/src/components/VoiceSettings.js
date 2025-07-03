import React, { useState, useEffect } from 'react';
import { XMarkIcon, SpeakerWaveIcon } from '@heroicons/react/24/outline';
import { useApi } from '../hooks/useApi';

const VoiceSettings = ({ settings, onChange, onClose }) => {
  const [availableVoices, setAvailableVoices] = useState({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);
  const { getVoices } = useApi();

  useEffect(() => {
    const loadVoices = async () => {
      try {
        setIsLoading(true);
        const voicesData = await getVoices();
        setAvailableVoices(voicesData.voices || {});
      } catch (err) {
        console.error('Failed to load voices:', err);
        setError('Failed to load available voices');
        // Fallback to default voices
        setAvailableVoices({
          en: [
            { id: 'en_US-lessac-medium', name: 'Lessac (US English)', gender: 'male' }
          ]
        });
      } finally {
        setIsLoading(false);
      }
    };

    loadVoices();
  }, [getVoices]);

  const handleLanguageChange = (language) => {
    const voicesForLanguage = availableVoices[language] || [];
    const defaultVoice = voicesForLanguage[0]?.id || settings.voice;
    
    onChange({
      ...settings,
      language,
      voice: defaultVoice
    });
  };

  const handleVoiceChange = (voice) => {
    onChange({
      ...settings,
      voice
    });
  };

  const handleSpeedChange = (speed) => {
    onChange({
      ...settings,
      speed: parseFloat(speed)
    });
  };

  const languages = Object.keys(availableVoices);
  const currentLanguageVoices = availableVoices[settings.language] || [];

  const getLanguageName = (code) => {
    const names = {
      en: 'English',
      es: 'Spanish',
      fr: 'French',
      de: 'German',
      it: 'Italian'
    };
    return names[code] || code.toUpperCase();
  };

  const getSpeedLabel = (speed) => {
    if (speed < 0.8) return 'Very Slow';
    if (speed < 1.0) return 'Slow';
    if (speed === 1.0) return 'Normal';
    if (speed <= 1.2) return 'Fast';
    return 'Very Fast';
  };

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 bg-primary-100 rounded-lg flex items-center justify-center">
            <SpeakerWaveIcon className="w-5 h-5 text-primary-600" />
          </div>
          <h3 className="text-lg font-semibold text-gray-900">
            Voice Settings
          </h3>
        </div>
        
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 transition-colors"
          aria-label="Close voice settings"
        >
          <XMarkIcon className="w-6 h-6" />
        </button>
      </div>

      {error && (
        <div className="mb-4 p-3 bg-warning-50 border border-warning-200 rounded-lg">
          <p className="text-warning-700 text-sm">{error}</p>
        </div>
      )}

      <div className="space-y-6">
        {/* Language Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Language
          </label>
          {isLoading ? (
            <div className="animate-pulse bg-gray-200 h-10 rounded-md"></div>
          ) : (
            <select
              value={settings.language}
              onChange={(e) => handleLanguageChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              aria-label="Select language"
            >
              {languages.map(lang => (
                <option key={lang} value={lang}>
                  {getLanguageName(lang)}
                </option>
              ))}
            </select>
          )}
        </div>

        {/* Voice Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Voice
          </label>
          {isLoading ? (
            <div className="animate-pulse bg-gray-200 h-10 rounded-md"></div>
          ) : (
            <select
              value={settings.voice}
              onChange={(e) => handleVoiceChange(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500"
              aria-label="Select voice"
              disabled={currentLanguageVoices.length === 0}
            >
              {currentLanguageVoices.map(voice => (
                <option key={voice.id} value={voice.id}>
                  {voice.name} ({voice.gender})
                </option>
              ))}
              {currentLanguageVoices.length === 0 && (
                <option value="">No voices available</option>
              )}
            </select>
          )}
          
          {currentLanguageVoices.length > 0 && (
            <p className="mt-1 text-xs text-gray-500">
              {currentLanguageVoices.find(v => v.id === settings.voice)?.name || 'Voice description'}
            </p>
          )}
        </div>

        {/* Speed Control */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Speech Speed
          </label>
          <div className="space-y-2">
            <input
              type="range"
              min="0.5"
              max="2.0"
              step="0.1"
              value={settings.speed}
              onChange={(e) => handleSpeedChange(e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              aria-label="Speech speed"
            />
            <div className="flex justify-between text-xs text-gray-500">
              <span>0.5x</span>
              <span className="font-medium text-gray-700">
                {settings.speed}x ({getSpeedLabel(settings.speed)})
              </span>
              <span>2.0x</span>
            </div>
          </div>
        </div>

        {/* Preview Section */}
        <div className="pt-4 border-t border-gray-200">
          <h4 className="text-sm font-medium text-gray-700 mb-2">
            Preview Settings
          </h4>
          <div className="bg-gray-50 rounded-lg p-3 space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600">Language:</span>
              <span className="font-medium">{getLanguageName(settings.language)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Voice:</span>
              <span className="font-medium">
                {currentLanguageVoices.find(v => v.id === settings.voice)?.name || 'Default'}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Speed:</span>
              <span className="font-medium">{settings.speed}x</span>
            </div>
          </div>
        </div>
      </div>

      {/* Accessibility note */}
      <div className="sr-only">
        <p>
          Voice settings panel. Use the language dropdown to select the speech language, 
          voice dropdown to choose a specific voice, and speed slider to adjust playback speed.
        </p>
      </div>
    </div>
  );
};

export default VoiceSettings;