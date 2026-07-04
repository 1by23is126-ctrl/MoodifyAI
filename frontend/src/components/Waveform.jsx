import React from 'react'

export default function Waveform(){
  return (
    <div className="w-full h-8 flex items-end">
      <div className="w-full flex items-end justify-center gap-1 animate-bars">
        {[8,12,6,10,14,7,11].map((h,i)=> (
          <div key={i} style={{height:`${h}px`, backgroundColor: 'var(--mood-primary)'}} className="w-1 rounded-full opacity-80" />
        ))}
      </div>
    </div>
  )
}
