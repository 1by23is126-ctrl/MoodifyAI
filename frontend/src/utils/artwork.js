const DEFAULT_ALBUM_ART = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 320 320'%3E%3Cdefs%3E%3ClinearGradient id='g' x1='0' x2='1' y1='0' y2='1'%3E%3Cstop stop-color='%2320293f'/%3E%3Cstop offset='0.54' stop-color='%23424d66'/%3E%3Cstop offset='1' stop-color='%230b0d14'/%3E%3C/linearGradient%3E%3C/defs%3E%3Crect width='320' height='320' fill='url(%23g)'/%3E%3Ccircle cx='160' cy='160' r='92' fill='none' stroke='rgba(255,255,255,0.22)' stroke-width='18'/%3E%3Ccircle cx='160' cy='160' r='26' fill='rgba(255,255,255,0.26)'/%3E%3Cpath d='M216 82v102c0 18-17 32-38 32-16 0-29-8-29-20 0-13 15-23 34-23 6 0 12 1 17 3v-62l-86 18v72c0 18-17 32-38 32-16 0-29-8-29-20 0-13 15-23 34-23 6 0 12 1 17 3V110l118-28z' fill='rgba(255,255,255,0.74)'/%3E%3C/svg%3E";

const normalizeUrl = (value) => {
  if (typeof value !== 'string') return '';
  const trimmed = value.trim();
  return trimmed.startsWith('http://') || trimmed.startsWith('https://') || trimmed.startsWith('data:') ? trimmed : '';
};

const collectArtworkCandidates = (source, artistImage) => {
  const candidates = [];
  const spotifyImages = source?.album?.images || source?.spotifyAlbum?.images || source?.spotify?.album?.images;
  if (Array.isArray(spotifyImages)) {
    for (const image of spotifyImages) {
      const url = normalizeUrl(image?.url);
      if (url) candidates.push(url);
    }
  }

  for (const key of [
    'albumArtHD',
    'albumArtMedium',
    'albumArtThumb',
    'albumArt',
    'album_art',
    'artworkUrl',
    'artwork_url',
    'cover',
    'coverUrl',
    'cover_url',
    'image',
    'thumbnail'
  ]) {
    const value = normalizeUrl(source?.[key]);
    if (value) candidates.push(value);
  }

  const artistUrl = normalizeUrl(artistImage);
  if (artistUrl) candidates.push(artistUrl);

  return [...new Set(candidates)];
};

export function resolveArtworkUrl(source, artistImage) {
  const candidates = collectArtworkCandidates(source, artistImage);
  if (!candidates.length) return DEFAULT_ALBUM_ART;

  const useHighRes = typeof window !== 'undefined' && (window.devicePixelRatio >= 1.5 || window.innerWidth >= 960);
  const preferred = source?.albumArtHD || source?.albumArtMedium || source?.albumArtThumb || source?.albumArt || source?.album_art || '';
  if (normalizeUrl(preferred)) {
    return useHighRes ? normalizeUrl(source?.albumArtHD || source?.albumArtMedium || source?.albumArtThumb || preferred) : normalizeUrl(source?.albumArtMedium || source?.albumArtHD || source?.albumArtThumb || preferred);
  }

  return candidates[0];
}

export function getArtworkPlaceholder() {
  return DEFAULT_ALBUM_ART;
}

export function getArtworkLoadingStrategy(index = 0) {
  return {
    loading: index < 4 ? 'eager' : 'lazy',
    fetchPriority: index < 4 ? 'high' : 'auto'
  };
}
