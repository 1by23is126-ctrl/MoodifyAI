import React, { useRef, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { Sphere, MeshDistortMaterial, Environment, Float } from '@react-three/drei';
import * as THREE from 'three';

function OrbMesh({ phase, colors }) {
  const materialRef = useRef();
  const meshRef = useRef();

  // Convert hex to THREE.Color
  const color1 = useMemo(() => new THREE.Color(colors.primary || '#3b82f6'), [colors.primary]);
  const color2 = useMemo(() => new THREE.Color(colors.secondary || '#7c3aed'), [colors.secondary]);

  useFrame((state) => {
    if (!materialRef.current) return;
    
    const t = state.clock.getElapsedTime();
    
    // Animate material properties based on phase
    const targetDistort = phase === 'analyzing' ? 0.6 : (phase === 'results' ? 0.2 : 0.4);
    const targetSpeed = phase === 'analyzing' ? 4 : (phase === 'results' ? 1 : 2);
    
    materialRef.current.distort = THREE.MathUtils.lerp(materialRef.current.distort, targetDistort, 0.05);
    materialRef.current.speed = THREE.MathUtils.lerp(materialRef.current.speed, targetSpeed, 0.05);
    
    // Shift color slightly over time
    const lerpFactor = (Math.sin(t * 0.5) + 1) / 2;
    materialRef.current.color.lerpColors(color1, color2, lerpFactor);
    
    // Pulse scale during analysis
    if (phase === 'analyzing' && meshRef.current) {
      const scale = 1 + Math.sin(t * 4) * 0.05;
      meshRef.current.scale.setScalar(scale);
    } else if (meshRef.current) {
      meshRef.current.scale.lerp(new THREE.Vector3(1, 1, 1), 0.1);
    }
  });

  return (
    <Float speed={phase === 'analyzing' ? 3 : 1.5} rotationIntensity={phase === 'analyzing' ? 2 : 1} floatIntensity={1}>
      <Sphere ref={meshRef} args={[1, 64, 64]}>
        <MeshDistortMaterial
          ref={materialRef}
          color={color1}
          envMapIntensity={1.35}
          clearcoat={1}
          clearcoatRoughness={0.1}
          metalness={0.8}
          roughness={0.28}
          distort={0.4}
          speed={2}
        />
      </Sphere>
    </Float>
  );
}

export default function AiOrb({ phase, mood, colors }) {
  // Hide orb during results and analytics to let cards take focus
  // Actually, keep it visible but faded in background, handled in App.jsx layout
  
  return (
    <div className="w-[300px] h-[300px] md:w-[500px] md:h-[500px] relative transition-opacity duration-1000">
      {/* Underlying glow */}
      <div 
        className="orb-halo absolute inset-0 rounded-full transition-colors duration-1000"
        style={{ background: `radial-gradient(circle, ${colors.primary} 0%, transparent 70%)` }}
      />
      
      <Canvas camera={{ position: [0, 0, 3], fov: 45 }} gl={{ antialias: true, alpha: true }}>
        <ambientLight intensity={0.28} />
        <directionalLight position={[10, 10, 5]} intensity={0.88} color={colors.primary} />
        <directionalLight position={[-10, -10, -5]} intensity={0.54} color={colors.secondary} />
        <pointLight position={[0, 0, 0]} intensity={0.72} color={colors.primary} />

        <OrbMesh phase={phase} colors={colors} />
        <Environment preset="city" />
      </Canvas>
    </div>
  );
}
