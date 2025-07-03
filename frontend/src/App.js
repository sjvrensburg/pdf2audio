import React, { useState, useEffect } from 'react';
import { SpeakerWaveIcon, DocumentTextIcon, Cog6ToothIcon } from '@heroicons/react/24/outline';
import FileUpload from './components/FileUpload';
import ProcessingStatus from './components/ProcessingStatus';
import AudioPlayer from './components/AudioPlayer';
import VoiceSettings from './components/VoiceSettings';
import { useApi } from './hooks/useApi';

function App() {
  const [currentTask, setCurrentTask] = useState(null);
  const [voiceSettings, setVoiceSettings] = useState({
    language: 'en',
    voice: 'en_US-lessac-medium',
    speed: 1.0
  });
  const [showSettings, setShowSettings] = useState(false);
  const { uploadFile, getTaskStatus, getVoices } = useApi();

  const handleFileUpload = async (file) => {
    try {
      const response = await uploadFile(file, voiceSettings);
      setCurrentTask({
        id: response.task_id,
        status: 'started',
        stage: 'queued',
        progress: 0,
        message: 'Processing started...'
      });
    } catch (error) {
      console.error('Upload failed:', error);
      // Handle error (show notification, etc.)
    }
  };

  const handleNewUpload = () => {
    setCurrentTask(null);
  };

  // Poll for task status updates
  useEffect(() => {
    if (!currentTask || currentTask.status === 'completed' || currentTask.status === 'failed') {
      return;
    }

    const pollInterval = setInterval(async () => {
      try {
        const status = await getTaskStatus(currentTask.id);
        setCurrentTask(prev => ({
          ...prev,
          ...status
        }));

        if (status.state === 'SUCCESS' || status.state === 'FAILURE') {
          clearInterval(pollInterval);
        }
      } catch (error) {
        console.error('Status polling failed:', error);
        clearInterval(pollInterval);
      }
    }, 2000);

    return () => clearInterval(pollInterval);
  }, [currentTask, getTaskStatus]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-10 h-10 bg-primary-600 rounded-lg">
                <SpeakerWaveIcon className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">PDF2Audio</h1>
                <p className="text-sm text-gray-600">Academic PDF to Speech Converter</p>
              </div>
            </div>
            
            <button
              onClick={() => setShowSettings(!showSettings)}
              className="btn-secondary"
              aria-label="Voice settings"
            >
              <Cog6ToothIcon className="w-5 h-5 mr-2" />
              Settings
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Voice Settings Panel */}
        {showSettings && (
          <div className="mb-8 fade-in">
            <VoiceSettings
              settings={voiceSettings}
              onChange={setVoiceSettings}
              onClose={() => setShowSettings(false)}
            />
          </div>
        )}

        {/* Main Processing Area */}
        <div className="space-y-8">
          {!currentTask ? (
            /* Upload Section */
            <div className="text-center">
              <div className="mb-8">
                <DocumentTextIcon className="mx-auto w-16 h-16 text-gray-400 mb-4" />
                <h2 className="text-3xl font-bold text-gray-900 mb-2">
                  Convert Academic PDFs to Audio
                </h2>
                <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                  Upload your research papers, textbooks, or academic documents with mathematical content. 
                  Our AI will extract the text and mathematics, then convert it to natural-sounding speech.
                </p>
              </div>
              
              <FileUpload onUpload={handleFileUpload} />
              
              {/* Features */}
              <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="card text-center">
                  <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <DocumentTextIcon className="w-6 h-6 text-primary-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Text Extraction</h3>
                  <p className="text-gray-600">
                    Advanced PDF parsing with GROBID extracts text and mathematical formulas accurately.
                  </p>
                </div>
                
                <div className="card text-center">
                  <div className="w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <SpeakerWaveIcon className="w-6 h-6 text-success-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Natural Speech</h3>
                  <p className="text-gray-600">
                    High-quality text-to-speech with proper pronunciation of mathematical expressions.
                  </p>
                </div>
                
                <div className="card text-center">
                  <div className="w-12 h-12 bg-warning-100 rounded-lg flex items-center justify-center mx-auto mb-4">
                    <Cog6ToothIcon className="w-6 h-6 text-warning-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Customizable</h3>
                  <p className="text-gray-600">
                    Choose from multiple voices, languages, and adjust speech speed to your preference.
                  </p>
                </div>
              </div>
            </div>
          ) : (
            /* Processing/Results Section */
            <div className="space-y-6">
              <ProcessingStatus task={currentTask} />
              
              {currentTask.state === 'SUCCESS' && (
                <div className="fade-in">
                  <AudioPlayer taskId={currentTask.id} result={currentTask.result} />
                  
                  <div className="mt-6 text-center">
                    <button
                      onClick={handleNewUpload}
                      className="btn-primary"
                    >
                      Convert Another PDF
                    </button>
                  </div>
                </div>
              )}
              
              {currentTask.state === 'FAILURE' && (
                <div className="card bg-error-50 border-error-200 fade-in">
                  <div className="text-center">
                    <h3 className="text-lg font-semibold text-error-900 mb-2">
                      Processing Failed
                    </h3>
                    <p className="text-error-700 mb-4">
                      {currentTask.message || 'An error occurred while processing your PDF.'}
                    </p>
                    <button
                      onClick={handleNewUpload}
                      className="btn-primary"
                    >
                      Try Again
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 bg-white border-t border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center text-gray-600">
            <p className="mb-2">
              Built with open-source tools: GROBID, MathJax SRE, Piper TTS
            </p>
            <p className="text-sm">
              Files are automatically deleted after 24 hours for privacy.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;