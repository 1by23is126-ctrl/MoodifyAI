import React, { useEffect, useMemo, useState } from 'react';
import {
  clearMoodHistory,
  deleteMoodHistoryEntry,
  filterMoodHistory,
  getUniqueHistoryValues,
  loadMoodHistory
} from '../utils/storage';

const PAGE_SIZE = 12;

export default function HistoryPanel({ onBack }) {
  const [history, setHistory] = useState([]);
  const [search, setSearch] = useState('');
  const [moodFilter, setMoodFilter] = useState('');
  const [languageFilter, setLanguageFilter] = useState('');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [historyVersion, setHistoryVersion] = useState(0);

  const availableFilters = useMemo(() => getUniqueHistoryValues(), [historyVersion]);

  const filtered = useMemo(() => {
    return filterMoodHistory({
      search,
      mood: moodFilter,
      language: languageFilter,
      startDate,
      endDate
    });
  }, [search, moodFilter, languageFilter, startDate, endDate, historyVersion]);

  const pagedHistory = useMemo(() => {
    const start = 0;
    const end = page * PAGE_SIZE;
    return filtered.slice(start, end);
  }, [filtered, page]);

  const hasMore = pagedHistory.length < filtered.length;

  useEffect(() => {
    setLoading(true);
    setError('');
    try {
      loadMoodHistory();
      setHistoryVersion((prev) => prev + 1);
    } catch (err) {
      setError('Unable to load mood history.');
    } finally {
      setLoading(false);
    }
  }, []);

  const handleDelete = (id) => {
    deleteMoodHistoryEntry(id);
    setHistoryVersion((prev) => prev + 1);
  };

  const handleClear = () => {
    clearMoodHistory();
    setHistoryVersion((prev) => prev + 1);
  };

  const resetFilters = () => {
    setSearch('');
    setMoodFilter('');
    setLanguageFilter('');
    setStartDate('');
    setEndDate('');
    setPage(1);
  };

  return (
    <div className="w-full max-w-6xl mx-auto pb-20 px-4">
      <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div>
          <p className="readable-kicker text-[10px] tracking-[0.24em] uppercase text-muted">History</p>
          <h2 className="text-[2rem] md:text-[2.4rem] font-display font-semibold tracking-[-0.025em] mt-1">Mood timeline</h2>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <button
            type="button"
            onClick={onBack}
            className="btn-secondary px-5 py-2.5 rounded-full text-[0.78rem] font-semibold tracking-[0.04em]"
          >
            Back
          </button>
          <button
            type="button"
            onClick={handleClear}
            className="btn-secondary px-5 py-2.5 rounded-full text-[0.78rem] font-semibold tracking-[0.04em]"
          >
            Clear all
          </button>
        </div>
      </div>

      <section className="glass-card rounded-3xl border border-white/10 bg-[rgba(12,14,20,0.85)] p-6 mb-6">
        <div className="grid gap-4 lg:grid-cols-[1.2fr_1fr_1fr]">
          <label className="block text-sm text-white">
            Search history
            <input
              value={search}
              onChange={(event) => { setSearch(event.target.value); setPage(1); }}
              className="input-field mt-2"
              placeholder="Search by prompt, mood, or notes"
            />
          </label>
          <label className="block text-sm text-white">
            Mood filter
            <select
              value={moodFilter}
              onChange={(event) => { setMoodFilter(event.target.value); setPage(1); }}
              className="input-field mt-2"
            >
              <option value="">All moods</option>
              {availableFilters.moods.map((mood) => (
                <option key={mood} value={mood}>{mood}</option>
              ))}
            </select>
          </label>
          <label className="block text-sm text-white">
            Language filter
            <select
              value={languageFilter}
              onChange={(event) => { setLanguageFilter(event.target.value); setPage(1); }}
              className="input-field mt-2"
            >
              <option value="">All languages</option>
              {availableFilters.languages.map((language) => (
                <option key={language} value={language}>{language}</option>
              ))}
            </select>
          </label>
        </div>

        <div className="mt-4 grid gap-4 md:grid-cols-2">
          <label className="block text-sm text-white">
            From
            <input
              type="date"
              value={startDate}
              onChange={(event) => { setStartDate(event.target.value); setPage(1); }}
              className="input-field mt-2"
            />
          </label>
          <label className="block text-sm text-white">
            To
            <input
              type="date"
              value={endDate}
              onChange={(event) => { setEndDate(event.target.value); setPage(1); }}
              className="input-field mt-2"
            />
          </label>
        </div>

        <button
          type="button"
          onClick={resetFilters}
          className="btn-ghost mt-4 px-4 py-2 rounded-full text-[0.78rem] font-semibold"
        >
          Reset filters
        </button>
      </section>

      {loading ? (
        <div className="flex justify-center py-24 text-sm text-muted">Loading mood history…</div>
      ) : error ? (
        <div className="text-sm text-rose-400">{error}</div>
      ) : pagedHistory.length === 0 ? (
        <div className="text-sm text-muted py-24 text-center">No mood history matched your filters.</div>
      ) : (
        <div className="grid gap-4">
          {pagedHistory.map((entry) => (
            <article key={entry.id} className="glass-card rounded-3xl border border-white/10 p-6">
              <div className="flex flex-wrap items-start justify-between gap-3 mb-4">
                <div className="min-w-0">
                  <p className="text-sm uppercase tracking-[0.16em] text-muted">{entry.mood}</p>
                  <h3 className="text-xl font-semibold mt-1 truncate">{entry.prompt}</h3>
                </div>
                <div className="text-right text-xs text-muted">
                  <div>{entry.language}</div>
                  <div>{entry.timestamp ? new Date(entry.timestamp).toLocaleString() : 'Unknown'}</div>
                </div>
              </div>
              {entry.confidence !== null && entry.confidence !== undefined && (
                <div className="mb-3 text-sm text-secondary">Confidence: {Math.round(entry.confidence * 100)}%</div>
              )}
              {entry.recommended_songs?.length > 0 && (
                <div className="mb-4 text-sm text-muted">
                  Recommended songs: {entry.recommended_songs.slice(0, 4).map((song, index) => (typeof song === 'string' ? song : song.title || song.name || song.id || `Track ${index + 1}`)).join(', ')}{entry.recommended_songs.length > 4 ? ' …' : ''}
                </div>
              )}
              <div className="flex flex-wrap gap-3">
                <button
                  type="button"
                  onClick={() => handleDelete(entry.id)}
                  className="btn-ghost rounded-full px-4 py-2 text-[0.78rem] font-semibold"
                >
                  Delete
                </button>
              </div>
            </article>
          ))}

          {hasMore && (
            <button
              type="button"
              onClick={() => setPage((prev) => prev + 1)}
              className="mx-auto btn-secondary px-6 py-3 rounded-full text-[0.9rem] font-semibold"
            >
              Load more
            </button>
          )}
        </div>
      )}
    </div>
  );
}
