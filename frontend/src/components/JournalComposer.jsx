import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { saveJournalEntry } from '../utils/storage';

export default function JournalComposer({ moodData }) {
  const [note, setNote] = useState('');
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');

  const handleSave = async () => {
    if (!moodData || !moodData.prompt) {
      setError('Unable to save without the current mood prompt.');
      return;
    }
    if (!note.trim()) {
      setError('Please add a note before saving.');
      return;
    }

    setError('');
    setStatus('saving');
    try {
      saveJournalEntry({
        mood: moodData.mood || 'Chill',
        prompt: moodData.prompt,
        note: note.trim(),
        recommended_songs: moodData.recommendationsByLanguage || moodData.recommendations_by_language || moodData.tracks || [],
        language: moodData.selectedLanguage || moodData.language || 'English'
      });
      setStatus('saved');
      setNote('');
      window.setTimeout(() => setStatus('idle'), 2000);
    } catch (err) {
      setError(err?.message || 'Unable to save journal entry.');
      setStatus('idle');
    }
  };

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-card rounded-[28px] border border-white/10 bg-[rgba(7,11,18,0.82)] p-6 shadow-[0_40px_120px_rgba(0,0,0,0.2)]"
    >
      <div className="flex flex-col gap-3">
        <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-3">
          <div>
            <span className="readable-kicker text-[10px] tracking-[0.24em] uppercase text-muted">How are you feeling now?</span>
            <h3 className="text-[1.45rem] md:text-[1.6rem] font-display font-semibold tracking-[-0.02em] text-stellar mt-2">
              Capture this moment in your journal
            </h3>
          </div>
          <div className="text-right text-[0.82rem] text-muted">
            <div>{new Date().toLocaleDateString()}</div>
            <div>{new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</div>
          </div>
        </div>

        <p className="text-sm text-secondary leading-6">
          Save a personal note alongside your mood recommendation and the songs that came up for you.
        </p>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-white">Detected mood</label>
            <div className="glass-card rounded-3xl border border-white/10 bg-slate-950/70 p-4 text-sm">{moodData?.mood || 'Chill'}</div>
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-semibold text-white">Prompt</label>
            <div className="glass-card rounded-3xl border border-white/10 bg-slate-950/70 p-4 text-sm">{moodData?.prompt || 'No prompt available.'}</div>
          </div>
        </div>

        <label className="block text-sm font-semibold text-white">
          Your note
          <textarea
            value={note}
            onChange={(event) => setNote(event.target.value)}
            className="input-field min-h-[140px] mt-2 w-full resize-none"
            placeholder="Write how you feel, what you want to remember, or anything you want to revisit later..."
          />
        </label>

        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={handleSave}
            className="btn-primary px-6 py-3 rounded-full font-semibold"
            disabled={status === 'saving'}
          >
            {status === 'saving' ? 'Saving...' : 'Save journal entry'}
          </button>
          {status === 'saved' && <span className="text-sm text-emerald-300">Saved to your mood journal.</span>}
        </div>

        {error && <div className="text-sm text-rose-400">{error}</div>}
      </div>
    </motion.section>
  );
}
