import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';

export default function CustomCursor() {
  const [pos, setPos] = useState({ x: -100, y: -100 });
  const [isPointer, setIsPointer] = useState(false);
  const [isVisible, setIsVisible] = useState(false);
  const [isTouch, setIsTouch] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') return;
    if ('ontouchstart' in window || navigator.maxTouchPoints > 0) {
      setIsTouch(true);
      return;
    }

    const onMove = (e) => {
      setPos({ x: e.clientX, y: e.clientY });
      setIsVisible(true);

      const target = e.target;
      const isInteractive =
        target.tagName.toLowerCase() === 'a' ||
        target.tagName.toLowerCase() === 'button' ||
        target.tagName.toLowerCase() === 'textarea' ||
        target.tagName.toLowerCase() === 'input' ||
        target.closest('button') !== null ||
        target.closest('a') !== null;

      setIsPointer(isInteractive);
    };

    const onLeave = () => setIsVisible(false);

    window.addEventListener('mousemove', onMove);
    document.addEventListener('mouseleave', onLeave);
    return () => {
      window.removeEventListener('mousemove', onMove);
      document.removeEventListener('mouseleave', onLeave);
    };
  }, []);

  if (isTouch) return null;

  return (
    <motion.div
      className="fixed pointer-events-none z-[9999] mix-blend-screen"
      style={{ opacity: isVisible ? 1 : 0, transition: 'opacity 200ms ease' }}
      animate={{
        x: pos.x - (isPointer ? 20 : 12),
        y: pos.y - (isPointer ? 20 : 12)
      }}
      transition={{ type: 'spring', stiffness: 600, damping: 32, mass: 0.4 }}
    >
      <motion.div
        className="rounded-full"
        style={{
          backgroundColor: 'var(--mood-primary)',
          boxShadow: '0 0 18px var(--mood-glow)',
          opacity: 0.32
        }}
        animate={{
          width: isPointer ? 40 : 24,
          height: isPointer ? 40 : 24
        }}
        transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
      />
      <motion.div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 rounded-full bg-white"
        style={{ boxShadow: '0 0 8px rgba(255,255,255,0.8)' }}
        animate={{
          width: isPointer ? 3 : 5,
          height: isPointer ? 3 : 5
        }}
        transition={{ duration: 0.22 }}
      />
    </motion.div>
  );
}
