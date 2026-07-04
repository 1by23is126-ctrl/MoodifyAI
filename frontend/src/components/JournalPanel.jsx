import React, { useEffect, useMemo, useState } from 'react';
import { motion } from 'framer-motion';
import {
  deleteJournalEntry,
  filterJournalEntries,
  getUniqueJournalValues,
  loadJournalEntries,
  saveJournalEntry
} from '../utils/storage';

const emptyForm = { mood: '', prompt: '', note: '' };

export default function JournalPanel({ onBack }) {
  const [entries, setEntries] = useState([]);
  const [form, setForm] = useState(emptyForm);
  const [editingId, setEditingId] = useState(null);
  const [expandedId, setExpandedId] = useState(null);
  const [status, setStatus] = useState('idle');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [moodFilter, setMoodFilter] = useState('');
  const [monthFilter, setMonthFilter] = useState('');
  const [version, setVersion] = useState(0);

  const filters = useMemo(() => getUniqueJournalValues(), [version]);

  const filteredEntries = useMemo(() => {
    return filterJournalEntries({ search, mood: moodFilter, month: monthFilter });
  }, [search, moodFilter, monthFilter, version]);

  useEffect(() => {
    setLoading(true);
    try {
      loadJournalEntries();
      setVersion((prev) => prev + 1);
    } catch (err) {
      setError('Unable to load journal entries.');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadEntries = () => {
    setVersion((prev) => prev + 1);
  };

  const startEditing = (entry) => {
    setEditingId(entry.id);
    setForm({ mood: entry.mood || '', prompt: entry.prompt || '', note: entry.note || '' });
    setError('');
  };

  const cancelEditing = () => {
    setEditingId(null);
    setForm(emptyForm);
    setError('');
  };

  const handleDelete = (id) => {
    deleteJournalEntry(id);
    setVersion((prev) => prev + 1);
    if (expandedId === id) setExpandedId(null);
  };

  const handleSubmit = (event) => {
    event.preventDefault();
    if (!form.mood.trim() || !form.prompt.trim()) {
      setError('Mood and prompt are required.');
      return;
    }

    setError('');
    setStatus('saving');
    try {
      saveJournalEntry({
        id: editingId,
        mood: form.mood,
        prompt: form.prompt,
        note: form.note,
        language: '',
        recommended_songs: []
      });
      setForm(emptyForm);
      setEditingId(null);
      setStatus('saved');
      loadEntries();
      window.setTimeout(() => setStatus('idle'), 1600);
    } catch (err) {
      setError(err.message || 'Unable to save entry.');
      setStatus('idle');
    }
  };

  return (
    <div className="w-full max-w-6xl mx-auto pb-20 px-4">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <p className="readable-kicker text-[10px] tracking-[0.24em] uppercase text-muted">Journal</p>
          <h2 className="text-[2rem] md:text-[2.4rem] font-display font-semibold tracking-[-0.025em] mt-1">Mood notes</h2>
        </div>
        <button
          type="button"
          onClick={onBack}
          className="btn-secondary px-5 py-2.5 rounded-full text-[0.78rem] font-semibold tracking-[0.04em]"
        >
          Back
        </button>
      </div>

      <section className="glass-card rounded-3xl border border-white/10 bg-[rgba(12,14,20,0.85)] p-6 mb-6">
        <form className="grid gap-4" onSubmit={handleSubmit}>
          <div className="grid gap-4 lg:grid-cols-3">
            <label className="block text-sm text-white">
              Mood
              <input
                value={form.mood}
                onChange={(e) => setForm({ ...form, mood: e.target.value })}
                className="input-field mt-2"
                placeholder="Happy, Sad, Chill..."
              />
            </label>
            <label className="block text-sm text-white">
              Prompt
              <input
                value={form.prompt}
                onChange={(e) => setForm({ ...form, prompt: e.target.value })}
                className="input-field mt-2"
                placeholder="What were you feeling?"
              />
            </label>
            <label className="block text-sm text-white">
              Note
              <textarea
                value={form.note}
                onChange={(e) => setForm({ ...form, note: e.target.value })}
                className="input-field min-h-[92px] mt-2 resize-none"
                placeholder="Add anything you'd like to remember from this moment..."
              />
            </label>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <button type="submit" className="btn-primary px-6 py-3 rounded-full font-semibold">
              {editingId ? 'Update entry' : 'Save entry'}
            </button>
            {editingId && (
              <button
                type="button"
                onClick={cancelEditing}
                className="btn-ghost rounded-full px-4 py-3 text-[0.88rem] font-semibold"
              >
                Cancel
              </button>
            )}
            {status === 'saved' && <span className="text-sm text-emerald-300">Saved.</span>}
          </div>
          {error && <div className="text-sm text-rose-400">{error}</div>}
        </form>
      </section>

      <section className="glass-card rounded-3xl border border-white/10 bg-[rgba(12,14,20,0.85)] p-6 mb-6">
        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr_1fr]">
          <label className="block text-sm text-white">
            Search journal
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              className="input-field mt-2"
              placeholder="Search notes, moods, or prompts"
            />
          </label>
          <label className="block text-sm text-white">
            Mood
            <select
              value={moodFilter}
              onChange={(event) => setMoodFilter(event.target.value)}
              className="input-field mt-2"
            >
              <option value="">All moods</option>
              {filters.moods.map((mood) => (
                <option key={mood} value={mood}>{mood}</option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-white">
            Month
            <select
              value={monthFilter}
              onChange={(event) => setMonthFilter(event.target.value)}
              className="input-field mt-2"
            >
              <option value="">All months</option>
              {filters.months.map((month) => (
                <option key={month} value={month}>{month}</option>
              ))}
            </select>
          </label>
        </div>
      </section>

      {loading ? (
        <div className="text-sm text-muted py-24 text-center">Loading journal entries…</div>
      ) : filteredEntries.length === 0 ? (
        <div className="text-sm text-muted py-24 text-center">No journal entries found yet.</div>
      ) : (
        <div className="grid gap-4">
          {filteredEntries.map((entry) => {
            const isExpanded = expandedId === entry.id;
            return (
              <motion.article
                key={entry.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.25 }}
                className="glass-card rounded-3xl border border-white/10 p-6"
              >
                <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
                  <div className="min-w-0">
                    <p className="text-sm uppercase tracking-[0.16em] text-muted">{entry.mood}</p>
                    <h3 className="text-xl font-semibold mt-1 truncate">{entry.prompt}</h3>
                  </div>
                  <div className="text-right text-xs text-muted">
                    <div>{entry.timestamp ? new Date(entry.timestamp).toLocaleDateString() : 'Unknown'}</div>
                    <div>{entry.timestamp ? new Date(entry.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) : ''}</div>
                  </div>
                </div>

                <div className="grid gap-3 md:grid-cols-[1fr_auto] items-start">
                  <div className="text-sm leading-relaxed text-muted">
                    {entry.note || 'No note added.'}
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <button
                      type="button"
                      onClick={() => setExpandedId(isExpanded ? null : entry.id)}
                      className="btn-ghost rounded-full px-4 py-2 text-[0.78rem] font-semibold"
                    >
                      {isExpanded ? 'Collapse' : 'Expand'}
                    </button>
                    <button
                      type="button"
                      onClick={() => startEditing(entry)}
                      className="btn-ghost rounded-full px-4 py-2 text-[0.78rem] font-semibold"
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      onClick={() => handleDelete(entry.id)}
                      className="btn-ghost rounded-full px-4 py-2 text-[0.78rem] font-semibold"
                    >
                      Delete
                    </button>
                  </div>
                </div>

                {isExpanded && entry.recommended_songs?.length > 0 && (
                  <div className="mt-5 rounded-3xl border border-white/10 bg-slate-950/70 p-4 text-sm text-muted">
                    <div className="mb-3 text-[0.88rem] font-semibold text-white">Recommended songs</div>
                    <ul className="space-y-2">
                      {entry.recommended_songs.map((track, index) => (
                        <li key={`${entry.id}-song-${index}`} className="truncate">
                          {track.title || track.name || 'Unknown song'}
                          {track.artists?.length ? ` — ${track.artists.join(', ')}` : ''}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </motion.article>
            );
          })}
        </div>
      )}
    </div>
  );
}
