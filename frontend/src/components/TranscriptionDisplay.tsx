import React, { useState, useEffect } from 'react';
import { Copy, Download, Trash2, Volume2 } from 'lucide-react';

interface Transcription {
  id: string;
  text: string;
  confidence: number;
  timestamp: Date;
  language: string;
  duration?: number;
}

interface TranscriptionDisplayProps {
  transcriptions?: Transcription[];
  currentTranscription?: string;
  onTextToSpeech?: (text: string) => void;
  // New: language to use for enhancement (e.g., "en-US"). We'll map to base code like "en".
  language?: string;
}

export const TranscriptionDisplay: React.FC<TranscriptionDisplayProps> = ({
  transcriptions = [],
  currentTranscription = '',
  onTextToSpeech,
  language,
}) => {
  const [isLiveTranscription, setIsLiveTranscription] = useState<boolean>(false);
  const [savedTranscriptions, setSavedTranscriptions] = useState<Transcription[]>(transcriptions);

  // Enhancement state
  const [enhanceMode, setEnhanceMode] = useState<'correction' | 'explanation' | 'rephrase'>('correction');
  const [enhancing, setEnhancing] = useState(false);
  const [enhancedText, setEnhancedText] = useState<string>('');
  const [enhanceError, setEnhanceError] = useState<string | null>(null);

  // Update live transcription status when currentTranscription changes
  useEffect(() => {
    setIsLiveTranscription(currentTranscription.length > 0);
  }, [currentTranscription]);

  // Simulate receiving live transcription updates
  useEffect(() => {
    // This would typically come from the AudioRecorder component via props
    // For now, we'll simulate it
  }, []);

  const addTranscription = (text: string, confidence: number = 0.9, language: string = 'en-US') => {
    const newTranscription: Transcription = {
      id: Date.now().toString(),
      text,
      confidence,
      timestamp: new Date(),
      language,
    };
    
    setSavedTranscriptions(prev => [newTranscription, ...prev]);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You could add a toast notification here
    } catch (error) {
      console.error('Failed to copy text:', error);
    }
  };

  const downloadTranscription = (transcription: Transcription) => {
    const content = `Healthcare Transcription
    
Date: ${transcription.timestamp.toLocaleString()}
Language: ${transcription.language}
Confidence: ${(transcription.confidence * 100).toFixed(1)}%

Transcription:
${transcription.text}`;

    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcription-${transcription.timestamp.toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const deleteTranscription = (id: string) => {
    setSavedTranscriptions(prev => prev.filter(t => t.id !== id));
  };

  const getConfidenceStyle = (confidence: number): React.CSSProperties => {
    if (confidence >= 0.8) return { color: 'var(--success)' };
    if (confidence >= 0.6) return { color: 'var(--warning)' };
    return { color: 'var(--danger)' };
  };

  const getConfidenceLabel = (confidence: number): string => {
    if (confidence >= 0.8) return 'High';
    if (confidence >= 0.6) return 'Medium';
    return 'Low';
  };

  const enhanceCurrent = async () => {
    if (!currentTranscription || enhancing) return;
    setEnhancing(true);
    setEnhanceError(null);
    setEnhancedText('');
    try {
      const lang = (language || 'en').split('-')[0];
      const res = await fetch('http://localhost:8000/api/enhance/medical', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: currentTranscription,
          mode: enhanceMode,
          language: lang,
        }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.detail || `Enhancement failed (${res.status})`);
      }
      const data = await res.json();
      if (data && data.enhanced_text) {
        setEnhancedText(data.enhanced_text);
      } else if (data && data.enhancedText) {
        setEnhancedText(data.enhancedText);
      } else {
        setEnhancedText('');
      }
    } catch (e: any) {
      console.error('Enhancement error:', e);
      setEnhanceError(e.message || 'Enhancement failed');
    } finally {
      setEnhancing(false);
    }
  };

  return (
    <div className="space-y-3 sm:space-y-4 h-full flex flex-col p-3 sm:p-4">
      {/* Live Transcription Area */}
      <div className="rounded-lg p-3 sm:p-4 border" style={{ borderColor: 'var(--card-border)', background: 'transparent' }}>
        <div className="text-xs sm:text-sm text-[color:var(--muted-text)] mb-2 flex items-center justify-between">
          <span>Live Transcription</span>
          {isLiveTranscription && (
            <div className="flex items-center space-x-1">
              <div className="w-2 h-2 rounded-full animate-pulse" style={{ background: 'var(--danger)' }}></div>
              <span className="text-xs" style={{ color: 'var(--danger)' }}>Live</span>
            </div>
          )}
        </div>
        {currentTranscription ? (
          <div className="leading-relaxed text-sm sm:text-base">
            {currentTranscription}
          </div>
        ) : (
          <div className="italic text-sm text-[color:var(--muted-text)]">
            {isLiveTranscription 
              ? 'Listening for speech...'
              : 'Start recording to see live transcription here'}
          </div>
        )}
      </div>

      {/* Quick Actions for Current Transcription */}
      {currentTranscription && (
        <div className="flex flex-col sm:flex-row justify-end gap-2 sm:space-x-2 sm:gap-0">
          <button
            onClick={() => addTranscription(currentTranscription)}
            className="btn btn-primary"
          >
            Save
          </button>
          <button
            onClick={() => copyToClipboard(currentTranscription)}
            className="btn"
          >
            Copy
          </button>
        </div>
      )}

      {/* Enhancement Controls (inline with transcription) */}
      <div className="rounded-lg p-3 sm:p-4 border" style={{ borderColor: 'var(--card-border)' }}>
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
          <div className="text-sm font-medium text-[color:var(--muted-text)]">Enhance Transcription</div>
          <div className="flex items-center gap-2">
            <select
              value={enhanceMode}
              onChange={(e) => setEnhanceMode(e.target.value as any)}
              className="field px-2 py-1 text-sm"
            >
              <option value="correction">Correction</option>
              <option value="explanation">Explanation</option>
              <option value="rephrase">Rephrase</option>
            </select>
            <button
              onClick={enhanceCurrent}
              disabled={!currentTranscription || enhancing}
              className="btn btn-primary disabled:opacity-50"
            >
              {enhancing ? 'Enhancing...' : 'Apply'}
            </button>
          </div>
        </div>
        {enhanceError && (
          <div className="text-xs text-red-500 mt-2">{enhanceError}</div>
        )}
      </div>

      {/* Enhanced Result */}
      {enhancedText && (
        <div className="rounded-lg p-3 sm:p-4 border" style={{ borderColor: 'var(--brand)' }}>
          <div className="text-xs sm:text-sm text-[color:var(--muted-text)] mb-2">Enhanced Version</div>
          <div className="text-sm sm:text-base leading-relaxed whitespace-pre-wrap">
            {enhancedText}
          </div>
        </div>
      )}

      {/* Saved Transcriptions */}
      <div className="flex-1 overflow-hidden">
        <h3 className="text-sm sm:text-base font-medium mb-3">Saved Transcriptions ({savedTranscriptions.length})</h3>
        <div className="space-y-3 max-h-80 sm:max-h-96 overflow-y-auto scrollbar-thin">
          {savedTranscriptions.length === 0 ? (
            <div className="text-center py-6 sm:py-8 text-[color:var(--muted-text)]">
              <p className="text-sm">No transcriptions yet</p>
              <p className="text-xs mt-1">Start recording to create your first transcription</p>
            </div>
          ) : (
            savedTranscriptions.map((transcription) => (
              <div
                key={transcription.id}
                className="border rounded-lg p-3 sm:p-4 shadow-sm hover:shadow-md transition-shadow"
                style={{ background: 'var(--card-bg)', borderColor: 'var(--card-border)' }}
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-2 gap-2">
                  <div className="flex flex-wrap items-center gap-1 sm:space-x-2 text-xs text-[color:var(--muted-text)]">
                    <span>{transcription.timestamp.toLocaleString()}</span>
                    <span className="hidden sm:inline">•</span>
                    <span style={getConfidenceStyle(transcription.confidence)}>
                      {getConfidenceLabel(transcription.confidence)} confidence
                    </span>
                    <span className="hidden sm:inline">•</span>
                    <span>{transcription.language}</span>
                  </div>
                  {/* Action buttons */}
                  <div className="flex items-center space-x-1 self-end sm:self-auto">
                    {onTextToSpeech && (
                      <button
                        onClick={() => onTextToSpeech(transcription.text)}
                        className="p-2 text-[color:var(--muted-text)] hover:text-[color:var(--brand)] transition-colors"
                        title="Text to Speech"
                      >
                        <Volume2 className="h-4 w-4" />
                      </button>
                    )}
                    <button
                      onClick={() => copyToClipboard(transcription.text)}
                      className="p-2 text-[color:var(--muted-text)] hover:text-[color:var(--success)] transition-colors"
                      title="Copy to clipboard"
                    >
                      <Copy className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => downloadTranscription(transcription)}
                      className="p-2 text-[color:var(--muted-text)] hover:text-[color:var(--brand)] transition-colors"
                      title="Download transcription"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                    <button
                      onClick={() => deleteTranscription(transcription.id)}
                      className="p-2 text-[color:var(--muted-text)] hover:text-[color:var(--danger)] transition-colors"
                      title="Delete transcription"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  </div>
                </div>
                {/* Transcription Text */}
                <div className="text-sm sm:text-base leading-relaxed break-words">
                  {transcription.text}
                </div>
                {/* Footer Info */}
                {transcription.duration && (
                  <div className="mt-2 text-xs text-[color:var(--muted-text)]">
                    Duration: {transcription.duration.toFixed(1)}s
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Statistics */}
      {savedTranscriptions.length > 0 && (
        <div className="pt-3 mt-4" style={{ borderTop: '1px solid var(--card-border)' }}>
          <div className="grid grid-cols-3 gap-2 sm:gap-4 text-center text-xs text-[color:var(--muted-text)]">
            <div>
              <div className="font-medium text-sm sm:text-base" style={{ color: 'var(--text)' }}>
                {savedTranscriptions.length}
              </div>
              <div className="text-xs">Total</div>
            </div>
            <div>
              <div className="font-medium text-sm sm:text-base" style={{ color: 'var(--text)' }}>
                {((savedTranscriptions.reduce((sum, t) => sum + t.confidence, 0) / savedTranscriptions.length) * 100).toFixed(0)}%
              </div>
              <div className="text-xs">Avg. Confidence</div>
            </div>
            <div>
              <div className="font-medium text-sm sm:text-base" style={{ color: 'var(--text)' }}>
                {savedTranscriptions.reduce((sum, t) => sum + t.text.split(' ').length, 0)}
              </div>
              <div className="text-xs">Total Words</div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
