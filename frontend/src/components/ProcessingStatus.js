import React from 'react';
import { 
  DocumentTextIcon, 
  CogIcon, 
  SpeakerWaveIcon, 
  CheckCircleIcon,
  ExclamationCircleIcon 
} from '@heroicons/react/24/outline';

const ProcessingStatus = ({ task }) => {
  const stages = [
    { id: 'analyzing', label: 'Analyzing PDF', icon: DocumentTextIcon },
    { id: 'extracting', label: 'Extracting Text', icon: DocumentTextIcon },
    { id: 'processing', label: 'Processing Content', icon: CogIcon },
    { id: 'synthesizing', label: 'Generating Audio', icon: SpeakerWaveIcon },
    { id: 'completed', label: 'Completed', icon: CheckCircleIcon }
  ];

  const getCurrentStageIndex = () => {
    const currentStage = task.stage || 'queued';
    const index = stages.findIndex(stage => stage.id === currentStage);
    return index >= 0 ? index : 0;
  };

  const currentStageIndex = getCurrentStageIndex();
  const progress = task.progress || 0;

  const getStageStatus = (index) => {
    if (task.state === 'FAILURE') {
      return index <= currentStageIndex ? 'error' : 'pending';
    }
    
    if (index < currentStageIndex) return 'completed';
    if (index === currentStageIndex) return 'current';
    return 'pending';
  };

  const getStageClasses = (status) => {
    switch (status) {
      case 'completed':
        return 'bg-success-100 text-success-600 border-success-200';
      case 'current':
        return 'bg-primary-100 text-primary-600 border-primary-200 animate-pulse-slow';
      case 'error':
        return 'bg-error-100 text-error-600 border-error-200';
      default:
        return 'bg-gray-100 text-gray-400 border-gray-200';
    }
  };

  return (
    <div className="card">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">
            Processing Status
          </h3>
          <span className="text-sm text-gray-500">
            Task ID: {task.id?.slice(0, 8)}...
          </span>
        </div>
        
        {/* Progress Bar */}
        <div className="progress-bar mb-2">
          <div 
            className="progress-fill"
            style={{ width: `${progress}%` }}
            role="progressbar"
            aria-valuenow={progress}
            aria-valuemin="0"
            aria-valuemax="100"
            aria-label={`Processing progress: ${progress}%`}
          />
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-600">
            {task.message || 'Processing...'}
          </span>
          <span className="font-medium text-gray-900">
            {progress}%
          </span>
        </div>
      </div>

      {/* Stage Indicators */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-gray-700 mb-3">
          Processing Stages
        </h4>
        
        <div className="space-y-3">
          {stages.map((stage, index) => {
            const status = getStageStatus(index);
            const Icon = stage.icon;
            
            return (
              <div
                key={stage.id}
                className={`flex items-center space-x-3 p-3 rounded-lg border transition-all duration-200 ${getStageClasses(status)}`}
              >
                <div className="flex-shrink-0">
                  {status === 'completed' ? (
                    <CheckCircleIcon className="w-5 h-5" />
                  ) : status === 'error' ? (
                    <ExclamationCircleIcon className="w-5 h-5" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>
                
                <div className="flex-1">
                  <p className="font-medium">
                    {stage.label}
                  </p>
                  {status === 'current' && task.message && (
                    <p className="text-xs mt-1 opacity-75">
                      {task.message}
                    </p>
                  )}
                </div>
                
                <div className="flex-shrink-0">
                  {status === 'completed' && (
                    <CheckCircleIcon className="w-4 h-4 text-success-500" />
                  )}
                  {status === 'current' && (
                    <div className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
                  )}
                  {status === 'error' && (
                    <ExclamationCircleIcon className="w-4 h-4 text-error-500" />
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Live region for screen readers */}
      <div 
        className="sr-only" 
        aria-live="polite" 
        aria-atomic="true"
      >
        {task.message && `Processing update: ${task.message}`}
      </div>
    </div>
  );
};

export default ProcessingStatus;