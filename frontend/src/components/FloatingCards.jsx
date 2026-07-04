import React from 'react'
import { motion } from 'framer-motion'

export default function FloatingCards({ tracks = [] }) {
  if (!tracks.length) {
    return (
      <div className="mt-8 rounded-[32px] border border-white/10 bg-white/[0.02] p-12 text-center text-warm-gray font-light text-[13px] tracking-[0.28em] uppercase">
        Awaiting emotional resonance — the playlist will materialize once the AI completes its scan.
      </div>
    )
  }

  return (
    <div className="mt-10 grid gap-6">
      {tracks.map((track, index) => (
        <motion.div
          key={track.id || track.spotify_url || index}
          initial={{ opacity: 0, y: 20, filter: 'blur(20px)' }}
          animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
          transition={{ delay: 0.9 + index * 0.12, duration: 1.4, ease: [0.22, 1, 0.36, 1] }}
          whileHover={{ y: -4 }}
          className="relative overflow-hidden rounded-[32px] border border-white/10 bg-gradient-to-br from-white/[0.03] to-transparent p-6 shadow-[0_30px_70px_rgba(0,0,0,0.35)]"
        >
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_top_left,rgba(255,255,255,0.08),transparent_28%),radial-gradient(circle_at_bottom_right,rgba(255,175,90,0.06),transparent_32%)] opacity-60" />
          <div className="pointer-events-none absolute inset-x-6 top-6 h-1 rounded-full bg-gradient-to-r from-[#ffb6a1]/50 via-white/15 to-transparent" />

          <div className="relative grid gap-4 lg:grid-cols-[0.95fr_0.5fr] items-start">
            <div>
              <div className="text-sm uppercase tracking-[0.35em] text-warm-gray/80">{track.album || 'Curated track'}</div>
              <h3 className="mt-3 text-2xl font-semibold text-soft-ivory tracking-tight">{track.name || track.title || 'Untitled track'}</h3>
              <p className="mt-2 text-sm leading-7 text-warm-gray">{track.artist || track.artists || 'Unknown artist'}</p>
            </div>

            <div className="grid gap-2 text-[11px] uppercase tracking-[0.35em] text-soft-ivory/80">
              {track.mood && <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">{track.mood}</span>}
              {track.energy != null && <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">Energy {Math.round(track.energy * 100)}%</span>}
              {track.valence != null && <span className="rounded-full border border-white/10 bg-white/5 px-3 py-2">Warmth {Math.round(track.valence * 100)}%</span>}
            </div>
          </div>

          <div className="mt-6 rounded-[28px] border border-white/10 bg-black/15 p-5 text-sm leading-7 text-warm-gray">
            {track.emotionalReason || 'Selected for polished emotional resonance and cinematic flow.'}
          </div>

          {track.spotify_url && (
            <a
              href={track.spotify_url}
              rel="noreferrer"
              target="_blank"
              className="mt-5 inline-flex items-center gap-2 text-[12px] uppercase tracking-[0.35em] text-soft-ivory/90"
            >
              Play on Spotify
              <span aria-hidden="true">→</span>
            </a>
          )}
        </motion.div>
      ))}
    </div>
  )
}

