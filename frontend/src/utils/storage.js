const STORAGE_KEYS = {
  history: 'moodify_history_entries',
  journal: 'moodify_journal_entries',
  analyticsCache: 'moodify_analytics_cache'
};

const safeParse = (value, fallback) => {
  try {
    return value ? JSON.parse(value) : fallback;
  } catch (error) {
    console.warn('[storage] invalid JSON, resetting key', error);
    return fallback;
  }
};

const getStorage = (key) => {
  if (typeof window === 'undefined') return null;
  return safeParse(window.localStorage.getItem(key), null);
};

const setStorage = (key, value) => {
  if (typeof window === 'undefined') return;
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.warn('[storage] failed to persist data', error);
  }
};

const createId = () => `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

const normalizeTrack = (track) => {
  if (!track || typeof track !== 'object') return null;
  return {
    id: track.id || track.track_id || track.spotify_id || `${track.title || track.name || 'track'}-${Math.random().toString(36).slice(2, 5)}`,
    title: track.title || track.name || track.track || 'Unknown track',
    artists: Array.isArray(track.artists)
      ? track.artists
      : typeof track.artist === 'string'
      ? [track.artist]
      : typeof track.artist === 'object' && Array.isArray(track.artist?.names)
      ? track.artist.names
      : track.artist
      ? [String(track.artist)]
      : [],
    language: track.language || track.lang || 'English',
    preview_url: track.preview_url || track.previewUrl || null,
    spotify_url: track.spotifyUrl || track.spotify_url || track.url || null,
    album: track.album || null,
    artwork: track.image || track.artwork || track.album?.images?.[0]?.url || null
  };
};

const flattenTracks = (source) => {
  if (!source) return [];
  if (Array.isArray(source)) {
    return source.map(normalizeTrack).filter(Boolean);
  }
  if (typeof source === 'object') {
    return Object.values(source)
      .flat()
      .map(normalizeTrack)
      .filter(Boolean);
  }
  return [];
};

const loadEntries = (key) => {
  const stored = getStorage(key);
  if (!Array.isArray(stored)) return [];
  return stored
    .filter((item) => item && typeof item === 'object')
    .map((item) => ({ ...item }))
    .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
};

const saveEntries = (key, entries) => {
  setStorage(key, Array.isArray(entries) ? entries : []);
};

const runWithEntries = (key, updater) => {
  const entries = loadEntries(key);
  const updated = updater(entries) || entries;
  saveEntries(key, updated);
  return updated;
};

const createTimestamp = () => new Date().toISOString();

export const loadMoodHistory = () => loadEntries(STORAGE_KEYS.history);

export const saveMoodHistoryEntry = (entry) => {
  if (!entry || typeof entry !== 'object') return null;
  const timestamp = createTimestamp();
  return runWithEntries(STORAGE_KEYS.history, (entries) => {
    const prepared = {
      id: entry.id || createId(),
      timestamp: entry.timestamp || timestamp,
      updatedAt: createTimestamp(),
      prompt: String(entry.prompt || '').trim(),
      mood: String(entry.mood || 'Chill').trim(),
      language: String(entry.language || 'English').trim(),
      recommended_songs: flattenTracks(entry.recommended_songs),
      top_recommendation: normalizeTrack(entry.top_recommendation) || null,
      confidence: typeof entry.confidence === 'number' ? entry.confidence : null,
      note: String(entry.note || '').trim()
    };
    const existingIndex = entries.findIndex((item) => item.id === prepared.id);
    if (existingIndex >= 0) {
      entries[existingIndex] = { ...entries[existingIndex], ...prepared };
      return entries;
    }
    return [prepared, ...entries];
  });
};

export const deleteMoodHistoryEntry = (entryId) =>
  runWithEntries(STORAGE_KEYS.history, (entries) => entries.filter((entry) => entry.id !== entryId));

export const clearMoodHistory = () => saveEntries(STORAGE_KEYS.history, []);

export const loadJournalEntries = () => loadEntries(STORAGE_KEYS.journal);

export const saveJournalEntry = (entry) => {
  if (!entry || typeof entry !== 'object') return null;
  const timestamp = createTimestamp();
  return runWithEntries(STORAGE_KEYS.journal, (entries) => {
    const prepared = {
      id: entry.id || createId(),
      timestamp: entry.timestamp || timestamp,
      updatedAt: createTimestamp(),
      mood: String(entry.mood || 'Chill').trim(),
      prompt: String(entry.prompt || '').trim(),
      note: String(entry.note || '').trim(),
      recommended_songs: flattenTracks(entry.recommended_songs),
      language: String(entry.language || 'English').trim()
    };
    const existingIndex = entries.findIndex((item) => item.id === prepared.id);
    if (existingIndex >= 0) {
      entries[existingIndex] = { ...entries[existingIndex], ...prepared };
      return entries;
    }
    return [prepared, ...entries];
  });
};

export const deleteJournalEntry = (entryId) =>
  runWithEntries(STORAGE_KEYS.journal, (entries) => entries.filter((entry) => entry.id !== entryId));

const buildHistoryHash = (entries) =>
  entries
    .map((entry) => `${entry.id}:${entry.updatedAt || entry.timestamp || ''}`)
    .join('|');

const getAnalyticsCache = () => getStorage(STORAGE_KEYS.analyticsCache) || null;

const setAnalyticsCache = (value) => setStorage(STORAGE_KEYS.analyticsCache, value);

const safeNumber = (value) => (typeof value === 'number' && Number.isFinite(value) ? value : 0);

const groupBy = (entries, keyFn) =>
  entries.reduce((acc, entry) => {
    const key = keyFn(entry);
    if (!key) return acc;
    acc[key] = (acc[key] || 0) + 1;
    return acc;
  }, {});

export const computeMoodAnalytics = (entries) => {
  const now = new Date();
  const cleanEntries = Array.isArray(entries) ? entries.slice().sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp)) : [];
  const totalEntries = cleanEntries.length;
  const moodCounts = groupBy(cleanEntries, (entry) => entry.mood || 'Unknown');
  const languageCounts = groupBy(cleanEntries, (entry) => entry.language || 'Unknown');
  const dayCounts = groupBy(cleanEntries, (entry) => {
    const date = new Date(entry.timestamp);
    return Number.isNaN(date.getTime()) ? null : date.toISOString().slice(0, 10);
  });
  const weekdayCounts = groupBy(cleanEntries, (entry) => {
    const date = new Date(entry.timestamp);
    return Number.isNaN(date.getTime()) ? null : date.toLocaleDateString(undefined, { weekday: 'long' });
  });
  const monthCounts = groupBy(cleanEntries, (entry) => {
    const date = new Date(entry.timestamp);
    return Number.isNaN(date.getTime()) ? null : date.toISOString().slice(0, 7);
  });

  const artistCounts = cleanEntries.reduce((acc, entry) => {
    const songs = Array.isArray(entry.recommended_songs) ? entry.recommended_songs : [];
    songs.forEach((track) => {
      const artists = Array.isArray(track.artists) ? track.artists : [track.artist].filter(Boolean);
      artists.forEach((artist) => {
        const name = String(artist || 'Unknown artist').trim();
        if (!name) return;
        acc[name] = (acc[name] || 0) + 1;
      });
    });
    return acc;
  }, {});

  const moodDistribution = Object.entries(moodCounts).map(([mood, count]) => ({ mood, count }));
  const favoriteMood = Object.entries(moodCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || null;
  const favoriteLanguage = Object.entries(languageCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || null;
  const mostRecommendedArtists = Object.entries(artistCounts)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 4)
    .map(([artist]) => artist);
  const weeklyTrend = Array.from({ length: 7 }, (_, index) => {
    const date = new Date(now);
    date.setDate(now.getDate() - (6 - index));
    const day = date.toISOString().slice(0, 10);
    return { date, count: safeNumber(dayCounts[day]) };
  });

  const monthlyTrend = Array.from({ length: 6 }, (_, index) => {
    const date = new Date(now.getFullYear(), now.getMonth() - (5 - index), 1);
    const month = date.toISOString().slice(0, 7);
    return { month, count: safeNumber(monthCounts[month]) };
  });

  let streak = 0;
  let lastDate = null;
  cleanEntries.forEach((entry) => {
    const date = new Date(entry.timestamp);
    if (Number.isNaN(date.getTime())) return;
    const dayString = date.toISOString().slice(0, 10);
    if (!lastDate) {
      streak = 1;
      lastDate = dayString;
    } else {
      const previous = new Date(lastDate);
      previous.setDate(previous.getDate() + 1);
      if (dayString === previous.toISOString().slice(0, 10)) {
        streak += 1;
        lastDate = dayString;
      } else if (dayString !== lastDate) {
        lastDate = dayString;
      }
    }
  });

  const bestWeekday = Object.entries(weekdayCounts).sort((a, b) => b[1] - a[1])[0]?.[0] || null;
  const frequentMoodByDay = Object.fromEntries(
    Object.entries(weekdayCounts).sort((a, b) => b[1] - a[1])
  );

  const insights = [];
  if (totalEntries > 0) {
    insights.push(`You've analyzed your mood ${totalEntries} time${totalEntries === 1 ? '' : 's'}.`);
  }
  if (bestWeekday) {
    insights.push(`You were most active on ${bestWeekday}.`);
  }
  if (favoriteLanguage) {
    insights.push(`You mostly explore ${favoriteLanguage} songs.`);
  }
  if (favoriteMood) {
    insights.push(`Your most frequent mood is ${favoriteMood}.`);
  }
  if (streak > 1) {
    insights.push(`You're on a ${streak}-day mood streak.`);
  }

  return {
    totalEntries,
    moodCounts,
    languageCounts,
    moodDistribution,
    weeklyTrend,
    monthlyTrend,
    favoriteMood,
    favoriteLanguage,
    mostRecommendedArtists,
    currentStreak: streak,
    insights,
    bestWeekday,
    frequentMoodByDay,
    hottestMonth: monthlyTrend.slice().sort((a, b) => b.count - a.count)[0]?.month || null
  };
};

export const getMoodAnalytics = () => {
  const historyEntries = loadMoodHistory();
  const cache = getAnalyticsCache();
  const historyHash = buildHistoryHash(historyEntries);
  if (cache && cache.historyHash === historyHash && cache.data) {
    return cache.data;
  }
  const data = computeMoodAnalytics(historyEntries);
  setAnalyticsCache({ historyHash, data, updatedAt: createTimestamp() });
  return data;
};

export const filterMoodHistory = ({ search, mood, language, startDate, endDate }) => {
  const entries = loadMoodHistory();
  return entries.filter((entry) => {
    const matchSearch = !search || [entry.prompt, entry.mood, entry.language, entry.note]
      .some((value) => String(value || '').toLowerCase().includes(String(search || '').toLowerCase()));
    const matchMood = !mood || entry.mood === mood;
    const matchLanguage = !language || entry.language === language;
    const timestamp = new Date(entry.timestamp).getTime();
    const matchStart = !startDate || timestamp >= new Date(startDate).getTime();
    const matchEnd = !endDate || timestamp <= new Date(endDate).getTime();
    return matchSearch && matchMood && matchLanguage && matchStart && matchEnd;
  });
};

export const filterJournalEntries = ({ search, mood, month }) => {
  const entries = loadJournalEntries();
  return entries.filter((entry) => {
    const matchSearch = !search || [entry.prompt, entry.note, entry.mood, entry.language]
      .some((value) => String(value || '').toLowerCase().includes(String(search || '').toLowerCase()));
    const matchMood = !mood || entry.mood === mood;
    const matchMonth = !month || (entry.timestamp || '').startsWith(month);
    return matchSearch && matchMood && matchMonth;
  });
};

export const getUniqueHistoryValues = () => {
  const entries = loadMoodHistory();
  return {
    moods: Array.from(new Set(entries.map((entry) => entry.mood).filter(Boolean))),
    languages: Array.from(new Set(entries.map((entry) => entry.language).filter(Boolean)))
  };
};

export const getUniqueJournalValues = () => {
  const entries = loadJournalEntries();
  return {
    moods: Array.from(new Set(entries.map((entry) => entry.mood).filter(Boolean))),
    months: Array.from(new Set(entries.map((entry) => (entry.timestamp || '').slice(0, 7)).filter(Boolean))).sort((a, b) => b.localeCompare(a))
  };
};
