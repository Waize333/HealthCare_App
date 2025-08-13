import React, { useState } from 'react';
import { Wand2, FileText, BookOpen, Loader2, CheckCircle, AlertCircle } from 'lucide-react';

interface EnhancementMode {
  mode: string;
  name: string;
  description: string;
  icon: React.ReactNode;
}

interface EnhancementResult {
  original_text: string;
  enhanced_text: string;
  enhancement_mode: string;
  success: boolean;
  analysis?: {
    original_length: number;
    enhanced_length: number;
    enhancement_type: string;
    has_medical_terms: boolean;
  };
  error?: string;
}

interface EnhancementPanelProps {
  inputText?: string;
  onEnhancementComplete?: (result: EnhancementResult) => void;
}

export const EnhancementPanel: React.FC<EnhancementPanelProps> = ({
  inputText = '',
  onEnhancementComplete,
}) => {
  const [selectedMode, setSelectedMode] = useState<string>('correction');
  const [isProcessing, setIsProcessing] = useState<boolean>(false);
  const [inputValue, setInputValue] = useState<string>(inputText);
  const [enhancementResult, setEnhancementResult] = useState<EnhancementResult | null>(null);
  const [language, setLanguage] = useState<string>('en');

  const enhancementModes: EnhancementMode[] = [
    {
      mode: 'correction',
      name: 'Medical Correction',
      description: 'Correct medical terminology, expand abbreviations, and improve formatting',
      icon: <FileText className="h-4 w-4" />
    },
    {
      mode: 'explanation',
      name: 'Medical Explanation',
      description: 'Provide detailed explanations of medical terms and procedures',
      icon: <BookOpen className="h-4 w-4" />
    },
    {
      mode: 'rephrase',
      name: 'Professional Rephrasing',
      description: 'Rephrase using alternative medical language for better clarity',
      icon: <Wand2 className="h-4 w-4" />
    }
  ];

  const enhanceText = async () => {
    if (!inputValue.trim()) {
      return;
    }

    setIsProcessing(true);
    setEnhancementResult(null);

    try {
      const response = await fetch('http://localhost:8000/api/enhance/medical', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputValue,
          mode: selectedMode,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result: EnhancementResult = await response.json();
      setEnhancementResult(result);

      if (onEnhancementComplete) {
        onEnhancementComplete(result);
      }

    } catch (error) {
      console.error('Enhancement error:', error);
      setEnhancementResult({
        original_text: inputValue,
        enhanced_text: '',
        enhancement_mode: selectedMode,
        success: false,
        error: error instanceof Error ? error.message : 'Enhancement failed',
      });
    } finally {
      setIsProcessing(false);
    }
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // Could add toast notification here
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const clearResults = () => {
    setEnhancementResult(null);
    setInputValue('');
  };

  return (
    <div className="space-y-3 sm:space-y-4 h-full flex flex-col p-3 sm:p-4">
      {/* Input Text Area */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Text to Enhance
        </label>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter medical text to enhance, or select text from transcription..."
          className="w-full h-20 sm:h-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent resize-none text-sm"
          disabled={isProcessing}
        />
        <div className="text-xs text-gray-500 mt-1">
          {inputValue.length}/2000 characters
        </div>
      </div>

      {/* Enhancement Mode Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Enhancement Mode
        </label>
        <div className="space-y-2">
          {enhancementModes.map((mode) => (
            <label
              key={mode.mode}
              className={`flex items-start space-x-3 p-3 border rounded-lg cursor-pointer transition-colors ${
                selectedMode === mode.mode
                  ? 'border-purple-500 bg-purple-50'
                  : 'border-gray-200 hover:border-gray-300'
              }`}
            >
              <input
                type="radio"
                name="enhancementMode"
                value={mode.mode}
                checked={selectedMode === mode.mode}
                onChange={(e) => setSelectedMode(e.target.value)}
                className="mt-1 flex-shrink-0"
                disabled={isProcessing}
              />
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-2">
                  {mode.icon}
                  <span className="font-medium text-sm truncate">{mode.name}</span>
                </div>
                <p className="text-xs text-gray-600 mt-1 leading-relaxed">{mode.description}</p>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Language Selection */}
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Language
        </label>
        <select
          value={language}
          onChange={(e) => setLanguage(e.target.value)}
          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent text-sm"
          disabled={isProcessing}
        >
          <option value="en">English</option>
          <option value="es">Spanish</option>
          <option value="fr">French</option>
          <option value="de">German</option>
          <option value="it">Italian</option>
        </select>
      </div>

      {/* Action Buttons */}
      <div className="flex flex-col sm:flex-row gap-2 sm:space-x-2 sm:gap-0">
        <button
          onClick={enhanceText}
          disabled={!inputValue.trim() || isProcessing}
          className="flex-1 flex items-center justify-center space-x-2 px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors text-sm sm:text-base"
        >
          {isProcessing ? (
            <Loader2 className="h-4 w-4 animate-spin" />
          ) : (
            <Wand2 className="h-4 w-4" />
          )}
          <span>{isProcessing ? 'Processing...' : 'Enhance Text'}</span>
        </button>
        
        {enhancementResult && (
          <button
            onClick={clearResults}
            className="px-4 py-3 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm sm:text-base"
          >
            Clear
          </button>
        )}
      </div>

      {/* Enhancement Result */}
      {enhancementResult && (
        <div className="flex-1 border-t pt-3 sm:pt-4 space-y-3 sm:space-y-4 overflow-hidden">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
            <h3 className="text-sm font-medium text-gray-900">Enhancement Result</h3>
            <div className="flex items-center space-x-1">
              {enhancementResult.success ? (
                <>
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span className="text-xs text-green-600">Success</span>
                </>
              ) : (
                <>
                  <AlertCircle className="h-4 w-4 text-red-600" />
                  <span className="text-xs text-red-600">Failed</span>
                </>
              )}
            </div>
          </div>

          {enhancementResult.success ? (
            <div className="space-y-3 overflow-y-auto max-h-80">
              {/* Enhanced Text */}
              <div className="bg-green-50 border border-green-200 rounded-lg p-3 sm:p-4">
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2 gap-2">
                  <span className="text-sm font-medium text-green-800">Enhanced Text</span>
                  <button
                    onClick={() => copyToClipboard(enhancementResult.enhanced_text)}
                    className="text-xs text-green-600 hover:text-green-800 underline self-start sm:self-auto"
                  >
                    Copy
                  </button>
                </div>
                <div className="text-sm text-green-900 leading-relaxed break-words">
                  {enhancementResult.enhanced_text}
                </div>
              </div>

              {/* Analysis */}
              {enhancementResult.analysis && (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                  <div className="text-xs font-medium text-gray-700 mb-2">Analysis</div>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-xs text-gray-600">
                    <div>
                      <span className="font-medium">Original:</span> {enhancementResult.analysis.original_length} chars
                    </div>
                    <div>
                      <span className="font-medium">Enhanced:</span> {enhancementResult.analysis.enhanced_length} chars
                    </div>
                    <div className="sm:col-span-2">
                      <span className="font-medium">Medical Terms:</span> {enhancementResult.analysis.has_medical_terms ? 'Yes' : 'No'}
                    </div>
                  </div>
                </div>
              )}

              {/* Original Text for Comparison */}
              <details className="bg-gray-50 border border-gray-200 rounded-lg">
                <summary className="px-3 sm:px-4 py-2 text-sm font-medium text-gray-700 cursor-pointer hover:bg-gray-100">
                  Show Original Text
                </summary>
                <div className="px-3 sm:px-4 pb-3 sm:pb-4 text-sm text-gray-600 leading-relaxed break-words">
                  {enhancementResult.original_text}
                </div>
              </details>
            </div>
          ) : (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3 sm:p-4">
              <div className="text-sm text-red-800 break-words">
                <span className="font-medium">Error:</span> {enhancementResult.error}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
