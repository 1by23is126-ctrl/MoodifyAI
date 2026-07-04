import { useEffect } from 'react';

// Centralized mood color palette
export const MOOD_COLORS = {
  Happy: { primary: '#f59e0b', secondary: '#ef4444', glow: 'rgba(245, 158, 11, 0.25)' }, // amber-500 to red-500
  Sad: { primary: '#60a5fa', secondary: '#3730a3', glow: 'rgba(96, 165, 250, 0.25)' }, // blue-400 to indigo-800
  Angry: { primary: '#ef4444', secondary: '#991b1b', glow: 'rgba(239, 68, 68, 0.25)' }, // red-500 to red-800
  Chill: { primary: '#2dd4bf', secondary: '#0369a1', glow: 'rgba(45, 212, 191, 0.25)' }, // teal-400 to sky-700
  Romantic: { primary: '#f43f5e', secondary: '#be185d', glow: 'rgba(244, 63, 94, 0.25)' }, // rose-500 to pink-700
  Motivated: { primary: '#eab308', secondary: '#ea580c', glow: 'rgba(234, 179, 8, 0.25)' }, // yellow-500 to orange-600
  Lonely: { primary: '#94a3b8', secondary: '#334155', glow: 'rgba(148, 163, 184, 0.25)' }, // slate-400 to slate-700
  Energetic: { primary: '#10b981', secondary: '#047857', glow: 'rgba(16, 185, 129, 0.25)' }, // emerald-500 to emerald-700
  Focus: { primary: '#8b5cf6', secondary: '#4338ca', glow: 'rgba(139, 92, 246, 0.25)' }, // violet-500 to indigo-700
  'Late Night': { primary: '#a855f7', secondary: '#1e1b4b', glow: 'rgba(168, 85, 247, 0.25)' }, // purple-500 to indigo-950
  Rainy: { primary: '#64748b', secondary: '#1e293b', glow: 'rgba(100, 116, 139, 0.25)' }, // slate-500 to slate-800
  Party: { primary: '#ec4899', secondary: '#7e22ce', glow: 'rgba(236, 72, 153, 0.25)' }, // pink-500 to purple-700
};

export default function useMoodTheme(mood) {
  useEffect(() => {
    const root = document.documentElement;
    const colors = MOOD_COLORS[mood] || MOOD_COLORS['Chill'];

    // Smoothly transition CSS variables
    root.style.setProperty('--mood-primary', colors.primary);
    root.style.setProperty('--mood-secondary', colors.secondary);
    root.style.setProperty('--mood-glow', colors.glow);
  }, [mood]);

  return MOOD_COLORS[mood] || MOOD_COLORS['Chill'];
}
