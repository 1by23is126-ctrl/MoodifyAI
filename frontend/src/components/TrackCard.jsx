import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getArtworkLoadingStrategy, getArtworkPlaceholder, resolveArtworkUrl } from '../utils/artwork';

export default function TrackCard({ track, song, item, index }) {
  const [imageFailed, setImageFailed] = useState(false);
  const [imageLoaded, setImageLoaded] = useState(false);
  const source = track || song || item || {};

  const title = String(source?.title || source?.name || 'Untitled track');
  const artist = String(source?.artist || source?.artists || 'Unknown artist');
  const searchQuery = encodeURIComponent(`${artist} ${title}`);
  const language = source?.language ? String(source.language) : 'English';
  const artistImage = source?.artistImage || '';
  const resolvedArtwork = resolveArtworkUrl(source, artistImage);
  const shouldUseOfficialArtwork = Boolean(resolvedArtwork && resolvedArtwork !== getArtworkPlaceholder());
  const hasImage = Boolean(shouldUseOfficialArtwork && !imageFailed);
  const displayImage = hasImage ? resolvedArtwork : getArtworkPlaceholder();
  const spotifyUrl = source?.spotifyUrl || source?.spotify_url || source?.url || `https://open.spotify.com/search/${searchQuery}`;
  const missingArtworkLogged = useRef(false);
  const imageLoading = getArtworkLoadingStrategy(index);

  useEffect(() => {
    if (!hasImage && !missingArtworkLogged.current) {
      missingArtworkLogged.current = true;
      console.warn('[TrackCard] Missing artwork', {
        title,
        artist,
        spotifyUrl
      });
    }
  }, [hasImage, title, artist, spotifyUrl]);

  return (
    <a
      href={spotifyUrl}
      target="_blank"
      rel="noopener noreferrer"
      className="block focus:outline-none focus-visible:ring-2 focus-visible:ring-white/30 rounded-[18px]"
      aria-label={`Open ${title} by ${artist} on Spotify`}
      data-testid={`track-card-${index}`}
    >
      <motion.div
        className="flex h-[64px] items-center gap-3 overflow-hidden rounded-[18px] border-b border-white/10 bg-[rgba(12,14,20,0.82)] px-3 shadow-sm transition-transform duration-300"
        whileHover={{ y: -3 }}
        transition={{ duration: 0.35, ease: [0.16, 1, 0.3, 1] }}
      >
        <div className="relative h-12 w-12 flex-shrink-0 overflow-hidden rounded-xl bg-slate-900">
          <img
            src={displayImage}
            alt={hasImage ? `${title} album artwork` : 'MoodifyAI placeholder artwork'}
            className={`h-full w-full object-cover ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
            crossOrigin="anonymous"
            loading={imageLoading.loading}
            decoding="async"
            fetchpriority={imageLoading.fetchPriority}
            onLoad={() => setImageLoaded(true)}
            onError={() => {
              setImageFailed(true);
              setImageLoaded(false);
            }}
          />
          {!imageLoaded && (
            <div className="absolute inset-0 bg-slate-800/80" />
          )}
        </div>

        <div className="min-w-0 flex-1 overflow-hidden">
          <h4 className="text-sm font-semibold text-white truncate" title={title}>{title}</h4>
          <p className="text-[0.82rem] text-slate-400 truncate" title={artist}>{artist}</p>
        </div>

        <div className="flex-shrink-0">
          <svg width="20" height="20" viewBox="0 0 168 168" fill="none" aria-hidden="true">
            <circle cx="84" cy="84" r="84" fill="#1DB954" />
            <path fillRule="evenodd" clipRule="evenodd" d="M42 56.9c49.2-28.2 86.7-9.7 99.7 0.9 2.5 1.7 3.1 5.1 1.4 7.6-1.7 2.5-5.1 3.1-7.6 1.4-10.5-7.1-42.7-22.2-78.7-1.7-2.9 1.7-6.7 0.9-8.5-2.1-1-1.5-0.9-3.5 0.7-4.9zm3.3 25.8c43.2-25 81.9-8.6 94.1 0.7 2.5 1.8 3.2 5.2 1.4 7.7-1.8 2.5-5.2 3.2-7.7 1.4-8.2-6-35.8-19.3-76.6-1.7-3.2 1.8-7.1 0.9-8.9-2.3-1.4-3.4-0.5-7.6 7.7-10.1zm1.3 26.5c33.7-19.3 71.1-6.6 83.4 0.9 2.7 1.6 3.6 5.2 2 7.8-1.6 2.7-5.2 3.6-7.8 2-9.2-5.5-45.5-15.2-76.2 1.1-3.5 1.9-7.8 1-9.7-2.4-1.9-3.4-1-7.7 7.7-10.3z" fill="#fff" />
          </svg>
        </div>
      </motion.div>
    </a>
  );
}
