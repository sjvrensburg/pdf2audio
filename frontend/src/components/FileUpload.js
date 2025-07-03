import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { DocumentArrowUpIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

const FileUpload = ({ onUpload }) => {
  const [error, setError] = useState(null);
  const [isUploading, setIsUploading] = useState(false);

  const onDrop = useCallback(async (acceptedFiles, rejectedFiles) => {
    setError(null);
    
    if (rejectedFiles.length > 0) {
      const rejection = rejectedFiles[0];
      if (rejection.errors.some(e => e.code === 'file-too-large')) {
        setError('File is too large. Maximum size is 100MB.');
      } else if (rejection.errors.some(e => e.code === 'file-invalid-type')) {
        setError('Invalid file type. Please upload a PDF file.');
      } else {
        setError('File upload failed. Please try again.');
      }
      return;
    }

    if (acceptedFiles.length === 0) {
      setError('No valid files selected.');
      return;
    }

    const file = acceptedFiles[0];
    setIsUploading(true);
    
    try {
      await onUpload(file);
    } catch (err) {
      setError(err.message || 'Upload failed. Please try again.');
    } finally {
      setIsUploading(false);
    }
  }, [onUpload]);

  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragReject
  } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: false,
    disabled: isUploading
  });

  const dropzoneClass = `
    dropzone relative border-2 border-dashed rounded-lg p-8 text-center cursor-pointer
    transition-all duration-200 ease-in-out
    ${isDragActive && !isDragReject ? 'border-primary-500 bg-primary-50' : ''}
    ${isDragReject ? 'border-error-500 bg-error-50' : ''}
    ${!isDragActive && !isDragReject ? 'border-gray-300 hover:border-gray-400' : ''}
    ${isUploading ? 'opacity-50 cursor-not-allowed' : ''}
  `.trim();

  return (
    <div className="max-w-2xl mx-auto">
      <div {...getRootProps({ className: dropzoneClass })}>
        <input {...getInputProps()} aria-label="Upload PDF file" />
        
        <div className="space-y-4">
          <div className="flex justify-center">
            <DocumentArrowUpIcon 
              className={`w-16 h-16 ${
                isDragActive ? 'text-primary-500' : 'text-gray-400'
              }`} 
            />
          </div>
          
          <div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              {isUploading ? 'Uploading...' : 'Upload your PDF'}
            </h3>
            
            {isDragActive ? (
              <p className="text-primary-600 font-medium">
                {isDragReject ? 'Invalid file type' : 'Drop your PDF here'}
              </p>
            ) : (
              <div className="space-y-2">
                <p className="text-gray-600">
                  Drag and drop your PDF file here, or click to browse
                </p>
                <p className="text-sm text-gray-500">
                  Supports academic papers with mathematical content • Max 100MB
                </p>
              </div>
            )}
          </div>
          
          {!isUploading && (
            <button
              type="button"
              className="btn-primary"
              disabled={isUploading}
            >
              Choose File
            </button>
          )}
          
          {isUploading && (
            <div className="flex items-center justify-center space-x-2">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-600"></div>
              <span className="text-primary-600 font-medium">Processing...</span>
            </div>
          )}
        </div>
      </div>

      {error && (
        <div className="mt-4 p-4 bg-error-50 border border-error-200 rounded-lg fade-in">
          <div className="flex items-center space-x-2">
            <ExclamationTriangleIcon className="w-5 h-5 text-error-500 flex-shrink-0" />
            <p className="text-error-700 font-medium">{error}</p>
          </div>
        </div>
      )}

      {/* Accessibility instructions */}
      <div className="sr-only">
        <p>
          Upload a PDF file by dragging and dropping it onto the upload area, 
          or click the upload area to open a file browser. 
          Only PDF files up to 100MB are accepted.
        </p>
      </div>
    </div>
  );
};

export default FileUpload;