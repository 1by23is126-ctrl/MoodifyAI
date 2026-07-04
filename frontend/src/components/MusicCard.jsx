import React, { useState } from 'react'
import { motion } from 'framer-motion'
import { getArtworkLoadingStrategy, getArtworkPlaceholder, resolveArtworkUrl } from '../utils/artwork'

export default function MusicCard({ track }) {
  const [imageLoaded, setImageLoaded] = useState(false)
  const [imageFailed, setImageFailed] = useState(false)
  const source = track || {}

  const albumArt = resolveArtworkUrl(source, source?.artistImage || '')
  const displayArt = imageFailed || albumArt === getArtworkPlaceholder() ? getArtworkPlaceholder() : albumArt
  const loadingStrategy = getArtworkLoadingStrategy(0)
  const spotifyUrl = source.spotifyUrl || source.spotify_url;
  const title = source.title || source.name || 'Untitled Track';
  const artist = source.artist || source.artists || 'Unknown artist';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className="group overflow-hidden rounded-[1.5rem] border border-white/10 bg-slate-950/90 shadow-[0_18px_60px_rgba(0,0,0,0.14)] transition duration-300 hover:-translate-y-0.5"
    >
      <div className="relative h-0 min-h-[220px] w-full overflow-hidden rounded-b-none rounded-[1.5rem] pb-[100%] bg-slate-900">
        {!imageLoaded && <div className="absolute inset-0 animate-pulse bg-slate-800" />}
        <img
          src={displayArt}
          alt={`${title} album artwork`}
          className={`absolute inset-0 h-full w-full object-cover transition duration-500 group-hover:scale-105 ${imageLoaded ? 'opacity-100' : 'opacity-0'}`}
          loading={loadingStrategy.loading}
          decoding="async"
          fetchPriority={loadingStrategy.fetchPriority}
          onLoad={() => setImageLoaded(true)}
          onError={() => {
            setImageFailed(true)
            setImageLoaded(false)
          }}
        />
      </div>
      <div className="space-y-2 p-4">
        <div className="text-base font-semibold text-white line-clamp-2">{title}</div>
        <div className="text-sm text-slate-400">{artist}</div>
        <div className="mt-3">
          {spotifyUrl ? (
            <a
              href={spotifyUrl}
              target="_blank"
              rel="noreferrer"
              className="inline-flex rounded-full bg-white/5 px-4 py-2 text-sm font-medium text-sky-300 transition hover:bg-white/10"
            >
              Open on Spotify
            </a>
          ) : (
            <span className="inline-flex rounded-full bg-white/5 px-4 py-2 text-sm text-slate-400">
              Preview unavailable
            </span>
          )}
        </div>
      </div>
    </motion.div>
  );
}
