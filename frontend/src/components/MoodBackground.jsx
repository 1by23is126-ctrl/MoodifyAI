import React from 'react';

export default function MoodBackground({ mood }) {
  return (
    <div className="fixed inset-0 z-0 pointer-events-none overflow-hidden transition-colors duration-1000">
      {/* Primary animated gradient blob */}
      <div
        className="mood-background-blob absolute top-[-18%] left-[-12%] w-[55%] h-[55%] rounded-full opacity-[0.22] animate-[float_14s_ease-in-out_infinite]"
        style={{ background: 'radial-gradient(circle, var(--mood-primary), transparent 70%)' }}
      />

      {/* Secondary animated gradient blob */}
      <div
        className="mood-background-blob absolute bottom-[-18%] right-[-12%] w-[55%] h-[55%] rounded-full opacity-[0.16] animate-[float_18s_ease-in-out_infinite_2s]"
        style={{ background: 'radial-gradient(circle, var(--mood-secondary), transparent 70%)' }}
      />

      {/* Mid accent blob */}
      <div
        className="mood-background-blob absolute top-[35%] left-[42%] w-[28%] h-[28%] rounded-full opacity-[0.12] animate-[float_22s_ease-in-out_infinite_5s]"
        style={{ background: 'radial-gradient(circle, var(--mood-primary), transparent 70%)' }}
      />

      {/* Subtle vignette overlay */}
      <div className="readability-vignette absolute inset-0 pointer-events-none" />
    </div>
  );
}
