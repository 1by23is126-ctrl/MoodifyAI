import React from 'react';
import { motion } from 'framer-motion';
import { MOOD_COLORS } from '../hooks/useMoodTheme';

const EMOTION_COLORS = {
  Sadness: '#60a5fa',
  Melancholy: '#7dd3fc',
  Nostalgia: '#c4b5fd',
  Calmness: '#2dd4bf',
  Loneliness: '#94a3b8',
  Anxiety: '#f59e0b',
  Hopefulness: '#fde68a',
  Excitement: '#fb7185',
  Anger: '#ef4444',
  Confidence: '#facc15',
  'Romantic Warmth': '#f472b6',
  Energy: '#10b981',
  Introspection: '#a78bfa',
  Serenity: '#99f6e4',
  Motivation: '#fb923c'
};

const DIMENSION_LABELS = {
  energy: 'Energy',
  introspection: 'Introspection',
  emotionalDepth: 'Depth',
  socialWarmth: 'Warmth',
  mentalIntensity: 'Mental Load'
};

export default function MoodSpectrum({ scores, dimensions, primary, secondary, confidence }) {
  const sortedScores = Object.entries(scores || {})
    .sort(([,a], [,b]) => b - a)
    .filter(([,score]) => score >= 3);

  const dimensionEntries = dimensions
    ? Object.entries(DIMENSION_LABELS).map(([key, label]) => [label, dimensions[key]]).filter(([, value]) => typeof value === 'number')
    : [];

  if (sortedScores.length === 0) return null;

  return (
    <div className="glass-card rounded-[22px] p-6 md:p-7" data-testid="mood-spectrum">
      <div className="flex items-start justify-between gap-4 mb-6">
        <div>
          <h3 className="analytics-label text-[10px] mb-2">
            Emotional spectrum
          </h3>
          {(primary || secondary) && (
            <p className="text-[0.86rem] text-secondary font-medium">
              {primary}
              {secondary && (
                <>
                  <span className="mx-1.5 text-muted/60">·</span>
                  <span className="editorial-italic text-muted">{secondary}</span>
                </>
              )}
            </p>
          )}
        </div>
        {confidence && (
          <span className="spectrum-confidence rounded-full px-2.5 py-1 text-[10px] uppercase tracking-[0.18em] font-semibold">
            {Math.round(confidence * 100)}%
          </span>
        )}
      </div>

      <div className="flex flex-col gap-3.5">
        {sortedScores.map(([mood, score], index) => {
          const color = EMOTION_COLORS[mood] || MOOD_COLORS[mood]?.primary || MOOD_COLORS['Chill'].primary;

          return (
            <div key={mood} className="flex flex-col gap-1.5">
              <div className="flex justify-between items-center">
                <span className="text-[0.82rem] font-medium text-stellar tracking-[-0.005em]">{mood}</span>
                <span className="text-[0.74rem] font-medium tabular-nums text-muted">{score.toFixed(1)}<span className="opacity-50">%</span></span>
              </div>

              <div className="spectrum-track w-full">
                <motion.div
                  className="spectrum-fill"
                  style={{ background: `linear-gradient(90deg, ${color}, color-mix(in srgb, ${color} 58%, white))`, color }}
                  initial={{ width: 0 }}
                  animate={{ width: `${score}%` }}
                  transition={{
                    duration: 0.95,
                    delay: 0.3 + (index * 0.08),
                    ease: [0.16, 1, 0.3, 1]
                  }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {dimensionEntries.length > 0 && (
        <div className="spectrum-dimensions mt-7 pt-5 grid grid-cols-2 gap-2.5">
          {dimensionEntries.map(([label, value]) => (
            <div key={label} className="spectrum-dimension rounded-xl px-3 py-2.5">
              <div className="flex items-center justify-between gap-3">
                <span className="text-[9.5px] uppercase tracking-[0.16em] text-muted font-semibold">{label}</span>
                <span className="text-[0.78rem] font-semibold text-stellar tabular-nums">{value}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
