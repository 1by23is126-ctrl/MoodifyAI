import React, { useMemo } from 'react';
import { motion } from 'framer-motion';
import { MOOD_COLORS } from '../hooks/useMoodTheme';

export default function Particles({ mood, phase }) {
  const isMobile = typeof window !== 'undefined' && window.innerWidth < 768;
  // Reduced count for refined, less busy aesthetic
  const particleCount = isMobile ? 10 : 20;

  const colors = MOOD_COLORS[mood] || MOOD_COLORS['Chill'];

  const particles = useMemo(() => {
    return Array.from({ length: particleCount }).map((_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 2 + 0.6,
      duration: Math.random() * 22 + 14,
      delay: Math.random() * 5,
      driftX: Math.random() * 40 - 20
    }));
  }, [particleCount]);

  if (phase === 'results' || phase === 'analytics') return null;

  return (
    <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
      {particles.map((p) => (
        <motion.div
          key={p.id}
          className="absolute rounded-full mix-blend-screen"
          style={{
            left: `${p.x}%`,
            top: `${p.y}%`,
            width: p.size,
            height: p.size,
            backgroundColor: p.id % 2 === 0 ? colors.primary : colors.secondary,
            boxShadow: `0 0 ${p.size * 4}px ${colors.glow}`
          }}
          animate={{
            y: [0, -80, 0],
            x: [0, p.driftX, 0],
            opacity: [0.05, 0.5, 0.05],
            scale: [0.8, 1.3, 0.8]
          }}
          transition={{
            duration: p.duration,
            delay: p.delay,
            repeat: Infinity,
            ease: 'easeInOut'
          }}
        />
      ))}
    </div>
  );
}
