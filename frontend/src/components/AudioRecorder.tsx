import React, { useState, useRef, useEffect } from 'react';
import { Mic, Square } from 'lucide-react';

interface AudioRecorderProps {
  onRecordingComplete?: (blob: Blob) => void;
}

export const AudioRecorder: React.FC<AudioRecorderProps> = ({
  onRecordingComplete,
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [status, setStatus] = useState<string>('Ready to record');
  
  const streamRef = useRef<MediaStream | null>(null);
  const timerRef = useRef<number | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const mediaChunksRef = useRef<Blob[]>([]);

  useEffect(() => {
    checkMicrophonePermission();
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
      if (streamRef.current) streamRef.current.getTracks().forEach(t => t.stop());
    };
  }, []);

  const checkMicrophonePermission = async () => {
    try {
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        setStatus('Microphone not supported');
        return;
      }
      if (typeof navigator.permissions?.query === 'function') {
        const permission = await navigator.permissions.query({ name: 'microphone' as PermissionName });
        if (permission.state === 'denied') setStatus('Microphone access denied');
        else setStatus('Ready to record');
      } else {
        setStatus('Ready to record');
      }
    } catch (error) {
      console.error('Error checking microphone permission:', error);
      setStatus('Error checking microphone');
    }
  };

  const startRecording = async () => {
    try {
      setStatus('Requesting microphone access...');
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { channelCount: 1, echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      });
      streamRef.current = stream;

      const mr = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
      mediaRecorderRef.current = mr;
      mediaChunksRef.current = [];
      mr.ondataavailable = (e: BlobEvent) => { if (e.data && e.data.size > 0) mediaChunksRef.current.push(e.data); };
      mr.onstop = () => {
        try {
          if (mediaChunksRef.current.length) {
            const blob = new Blob(mediaChunksRef.current, { type: 'audio/webm' });
            onRecordingComplete && onRecordingComplete(blob);
            setStatus('Recording saved');
          }
        } catch (err) {
          console.error('Error creating recording blob:', err);
          setStatus('Error saving recording');
        }
      };
      mr.start(1000);

      setIsRecording(true);
      setStatus('Recording... Speak now');
      timerRef.current = window.setInterval(() => setRecordingTime((prev) => prev + 1), 1000);

    } catch (error) {
      console.error('Error starting recording:', error);
      setStatus(`Error starting recording`);
    }
  };

  const stopRecording = () => {
    if (!isRecording) return;
    setIsRecording(false);

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try { mediaRecorderRef.current.stop(); } catch {}
    }
    if (timerRef.current) { clearInterval(timerRef.current); timerRef.current = null; }
    if (streamRef.current) { streamRef.current.getTracks().forEach(track => track.stop()); }
    setRecordingTime(0);
  };

  return (
    <div className="space-y-3">
      <div className="text-sm text-[color:var(--muted-text)]" aria-live="polite">{status}</div>
      <div className="flex items-center gap-3">
        <button
          onClick={isRecording ? stopRecording : startRecording}
          className={`btn ${isRecording ? 'btn-primary mic-pulse' : ''}`}
          aria-label={isRecording ? 'Stop recording' : 'Start recording'}
          title={isRecording ? 'Stop recording' : 'Start recording'}
        >
          {isRecording ? <Square className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
          <span className="text-sm">{isRecording ? 'Stop' : 'Record'}</span>
        </button>
        {isRecording && (
          <span className="text-sm text-[color:var(--muted-text)]">{recordingTime}s</span>
        )}
      </div>
    </div>
  );
};
