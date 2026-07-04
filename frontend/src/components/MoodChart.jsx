import React from 'react'
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer } from 'recharts'

export default function MoodChart({scores={}}){
  const data = Object.keys(scores).map(k=>({subject: k.charAt(0).toUpperCase()+k.slice(1), A: Math.round(scores[k])}))
  return (
    <div style={{width:'100%',height:260}}>
      <ResponsiveContainer>
        <RadarChart data={data} outerRadius={90}>
          <PolarGrid strokeOpacity={0.06} />
          <PolarAngleAxis dataKey="subject" tick={{fill:'#cbd5e1'}} />
          <PolarRadiusAxis angle={30} domain={[0,100]} tickCount={4} />
          <Radar name="You" dataKey="A" stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.25} />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  )
}
