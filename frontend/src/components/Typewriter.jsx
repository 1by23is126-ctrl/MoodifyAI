import React, {useState, useEffect} from 'react'

export default function Typewriter({lines=[], speed=30}){
  const [index,setIndex]=useState(0)
  const [text,setText]=useState('')
  useEffect(()=>{
    if(index>=lines.length) return
    let i=0
    setText('')
    const line = lines[index]
    const t = setInterval(()=>{
      setText(prev=>prev+line[i])
      i++
      if(i>=line.length){ clearInterval(t); setTimeout(()=>setIndex(idx=>idx+1),400) }
    }, speed)
    return ()=> clearInterval(t)
  },[index,lines])
  return (
    <div className="text-sm text-gray-300 font-mono whitespace-pre-wrap">
      {text}
    </div>
  )
}
