import React from 'react'

export default function Console({messages=[]}){
  return (
    <div className="glass p-4 rounded-[28px] border border-white/10 bg-black/20 shadow-[0_24px_80px_rgba(0,0,0,0.16)]">
      <div className="text-sm uppercase tracking-[0.28em] text-gray-500">AI analysis console</div>
      <div className="mt-4 space-y-2 h-40 overflow-auto pr-2 text-sm text-white/90">
        {messages.map((m,i)=>(
          <div key={i} className="leading-6">{m}</div>
        ))}
      </div>
    </div>
  )
}
