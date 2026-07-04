import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';

export default function VoiceMic({ onTranscript }) {
  const [isRecording, setIsRecording] = useState(false);
  const [recognition, setRecognition] = useState(null);

  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const rec = new SpeechRecognition();
      rec.continuous = false;
      rec.interimResults = true;

      rec.onresult = (event) => {
        let text = '';
        for (let i = 0; i < event.results.length; i++) {
          text += event.results[i][0].transcript;
        }
        onTranscript(text);
      };

      rec.onend = () => setIsRecording(false);

      rec.onerror = (event) => {
        console.error('Speech recognition error', event.error);
        setIsRecording(false);
      };

      setRecognition(rec);
    }
  }, [onTranscript]);

  const toggleRecording = () => {
    if (!recognition) return;

    if (isRecording) {
      recognition.stop();
    } else {
      try {
        recognition.start();
        setIsRecording(true);
      } catch (err) {
        console.error('Could not start recognition', err);
      }
    }
  };

  if (!recognition) return null;

  return (
    <button
      type="button"
      onClick={toggleRecording}
      className={`relative p-1.5 rounded-full flex items-center justify-center transition-colors ${
        isRecording
          ? 'text-rose-300 bg-rose-400/10 border border-rose-400/30'
          : 'text-muted hover:text-stellar hover:bg-white/[0.06] border border-transparent hover:border-white/10'
      }`}
      title={isRecording ? 'Stop listening' : 'Voice input'}
      aria-label={isRecording ? 'Stop voice input' : 'Start voice input'}
      data-testid="voice-mic-btn"
    >
      {isRecording && (
        <>
          <motion.div
            className="absolute inset-0 rounded-full border border-rose-400"
            animate={{ scale: [1, 1.6], opacity: [0.7, 0] }}
            transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut' }}
          />
          <motion.div
            className="absolute inset-0 rounded-full border border-rose-400/50"
            animate={{ scale: [1, 1.4], opacity: [0.5, 0] }}
            transition={{ duration: 1.4, repeat: Infinity, ease: 'easeOut', delay: 0.5 }}
          />
        </>
      )}
      <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2a3 3 0 0 0-3 3v7a3 3 0 0 0 6 0V5a3 3 0 0 0-3-3Z"/>
        <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
        <line x1="12" x2="12" y1="19" y2="22"/>
      </svg>
    </button>
  );
}
