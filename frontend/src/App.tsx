import { useState, useRef, useEffect } from 'react'
import { AudioRecorder } from './components/AudioRecorder'
import { TranscriptionDisplay } from './components/TranscriptionDisplay'
import { LanguageSelector } from './components/LanguageSelector'
import { Stethoscope, Mic, FileText, Sun, Moon, Upload } from 'lucide-react'

function App() {
  const [currentTranscription, setCurrentTranscription] = useState<string>('')
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en-US')
  const [lastRecording, setLastRecording] = useState<Blob | null>(null)
  const [uploadBusy, setUploadBusy] = useState(false)
  const [isPlayingRecording, setIsPlayingRecording] = useState(false)
  const [theme, setTheme] = useState<'light' | 'dark'>(() => (document.documentElement.getAttribute('data-theme') as 'light' | 'dark') || 'light')
  const audioRef = useRef<HTMLAudioElement | null>(null)

  useEffect(() => {
    document.title = 'Healtcare Translation WebApp'
  }, [])

  const handleLanguageChange = (language: string) => {
    setSelectedLanguage(language)
  }

  const toggleTheme = () => {
    const next = theme === 'light' ? 'dark' : 'light'
    setTheme(next)
    document.documentElement.setAttribute('data-theme', next)
    localStorage.setItem('hw_theme', next)
  }

  // Auto-upload when a fresh recording is completed
  const handleRecordingComplete = (blob: Blob) => {
    setLastRecording(blob)
    uploadRecordedBlob(blob).catch((e) => {
      console.error('Auto-upload failed:', e)
    })
  }

  const playLastRecording = () => {
    if (!lastRecording || isPlayingRecording) return
    const url = URL.createObjectURL(lastRecording)
    const audio = new Audio(url)
    audioRef.current = audio
    setIsPlayingRecording(true)
    audio.onended = () => {
      setIsPlayingRecording(false)
      URL.revokeObjectURL(url)
      if (audioRef.current === audio) audioRef.current = null
    }
    audio.onerror = () => {
      setIsPlayingRecording(false)
      URL.revokeObjectURL(url)
      if (audioRef.current === audio) audioRef.current = null
    }
    audio.play().catch(() => {
      setIsPlayingRecording(false)
      URL.revokeObjectURL(url)
      if (audioRef.current === audio) audioRef.current = null
    })
  }

  // Upload a Blob produced by our recorder (auto path)
  const uploadRecordedBlob = async (blob: Blob) => {
    setUploadBusy(true)
    try {
      const fileToUpload = new File([blob], 'recording.webm', { type: 'audio/webm' })
      const form = new FormData()
      form.append('file', fileToUpload)
      form.append('language', selectedLanguage)

      const res = await fetch('http://localhost:8000/api/stt/transcribe', {
        method: 'POST',
        body: form,
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Upload failed (${res.status})`)
      }
      const data = await res.json()
      if (data && data.transcript) {
        setCurrentTranscription(data.transcript)
      }
    } finally {
      setUploadBusy(false)
    }
  }

  // New: Upload an existing audio file from the system and transcribe
  const uploadExistingAudio = async () => {
    try {
      const input = document.createElement('input')
      input.type = 'file'
      input.accept = 'audio/*'
      const picked = await new Promise<File | null>((resolve) => {
        input.onchange = () => {
          const f = input.files && input.files[0] ? input.files[0] : null
          resolve(f)
        }
        input.click()
      })
      if (!picked) return

      setUploadBusy(true)
      const form = new FormData()
      form.append('file', picked)
      form.append('language', selectedLanguage)

      const res = await fetch('http://localhost:8000/api/stt/transcribe', {
        method: 'POST',
        body: form
      })
      if (!res.ok) {
        const err = await res.json().catch(() => ({}))
        throw new Error(err.detail || `Upload failed (${res.status})`)
      }
      const data = await res.json()
      if (data && data.transcript) {
        setCurrentTranscription(data.transcript)
      }
    } catch (e:any) {
      console.error('Upload failed:', e)
      alert(e.message || 'Upload failed')
    } finally {
      setUploadBusy(false)
    }
  }

  return (
    <div className="app-container min-h-screen">
      {/* Header */}
      <header className="sticky top-0 z-30 backdrop-blur supports-[backdrop-filter]:bg-white/60 dark:supports-[backdrop-filter]:bg-black/30">
        <div className="mx-auto px-3 sm:px-4">
          <div className="flex items-center justify-between h-14">
            <div className="flex items-center gap-2">
              <Stethoscope className="h-7 w-7 text-[color:var(--brand)]" aria-hidden="true" />
              <h1 className="hidden sm:block text-lg sm:text-xl lg:text-2xl font-semibold truncate max-w-[60vw]">Healtcare Translation WebApp</h1>
            </div>
            <div className="flex items-center gap-2">
              <LanguageSelector selectedLanguage={selectedLanguage} onLanguageChange={handleLanguageChange} />
              <button aria-label="Toggle theme" onClick={toggleTheme} className="btn theme-toggle" title="Toggle light/dark">
                {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="mx-auto px-3 sm:px-4 py-4 sm:py-6">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-3 sm:gap-5">
          {/* Recorder */}
          <div className="space-y-4 sm:space-y-6">
            <div className="card card-accent overflow-hidden">
              <div className="flex items-center gap-2 p-4 sm:p-6 pb-2 sm:pb-4">
                <div className={`mic-wrap ${uploadBusy ? '' : ''}`}>
                  <Mic className={`h-5 w-5 text-[color:var(--brand-2)] ${lastRecording ? '' : ''}`} aria-hidden="true" />
                </div>
                <h2 className="text-base sm:text-lg font-semibold">Voice Recording</h2>
              </div>
              <div className="px-0 pb-2">
                <div className="flex items-center justify-between px-4">
                  {/* Pulsing circle when recording: implemented inside the recorder button via CSS class */}
                </div>
                <div className="px-4 pb-4">
                  <AudioRecorder onRecordingComplete={handleRecordingComplete} />
                </div>
              </div>
            </div>

            {/* Quick Actions */}
            <div className="card p-4 sm:p-6">
              <h3 className="text-base sm:text-lg font-semibold mb-3 sm:mb-4">Quick Actions</h3>
              <div className="space-y-2 sm:space-y-3">
                <button onClick={uploadExistingAudio} disabled={uploadBusy} className="btn w-full">
                  <Upload className="h-4 w-4" />
                  <span>{uploadBusy ? 'Uploading...' : 'Upload Existing Audio'}</span>
                </button>
                <button onClick={playLastRecording} disabled={!lastRecording || isPlayingRecording} className="btn w-full">
                  <span>{isPlayingRecording ? 'Playing...' : 'Play Last Recording'}</span>
                </button>
              </div>
            </div>
          </div>

          {/* Transcription & Enhancement */}
          <div>
            <div className="card border-l-4" style={{borderLeftColor: 'var(--brand)'}}>
              <div className="flex items-center gap-2 p-4 sm:p-6 pb-2 sm:pb-4">
                <FileText className="h-5 w-5 text-[color:var(--brand)]" aria-hidden="true" />
                <h2 className="text-base sm:text-lg font-semibold">Transcription & Enhancement</h2>
              </div>
              <div className="px-0 pb-0">
                <TranscriptionDisplay currentTranscription={currentTranscription} language={selectedLanguage} />
              </div>
            </div>
          </div>
        </div>
        {/* Footer */}
        <footer className="mt-8 text-center text-[color:var(--muted-text)] text-xs sm:text-sm px-2 pb-6">
          <p>Made by Waiz — waizqazi2@gmail.com</p>
        </footer>
      </main>
    </div>
  )
}

export default App
