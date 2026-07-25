import React, { useEffect, useState } from 'react';

export function AnimatedGridPattern({
  width = 40,
  height = 40,
  numSquares = 30,
  maxOpacity = 0.1,
  duration = 3,
}) {
  const [squares, setSquares] = useState([]);
  const [dimensions, setDimensions] = useState({ width: 2000, height: 2000 });

  useEffect(() => {
    // Generate random squares distributed across the grid
    const newSquares = [];
    const maxCols = Math.floor(dimensions.width / width);
    const maxRows = Math.floor(dimensions.height / height);
    
    for (let i = 0; i < numSquares; i++) {
      newSquares.push({
        id: i,
        x: Math.floor(Math.random() * maxCols),
        y: Math.floor(Math.random() * maxRows),
        duration: duration + Math.random() * 2,
        delay: Math.random() * 3,
      });
    }
    setSquares(newSquares);
  }, [numSquares, duration, width, height, dimensions]);

  return (
    <>
      {/* Base Grid */}
      <svg
        className="animated-grid"
        width="100%"
        height="100%"
        xmlns="http://www.w3.org/2000/svg"
      >
        <defs>
          <pattern
            id="grid-pattern"
            width={width}
            height={height}
            patternUnits="userSpaceOnUse"
          >
            <path
              d={`M.5 ${height}V.5H${width}`}
              fill="none"
              stroke="rgba(0, 0, 0, 0.2)"
              strokeWidth="1"
            />
          </pattern>
        </defs>
        
        <rect width="100%" height="100%" fill="url(#grid-pattern)" />
      </svg>
      
      {/* Animated HTML Squares (Hardware Accelerated) */}
      <div style={{ position: 'absolute', inset: 0, pointerEvents: 'none' }}>
        {squares.map((sq) => (
          <div
            key={sq.id}
            className="grid-square"
            style={{
              position: 'absolute',
              width: `${width - 1}px`,
              height: `${height - 1}px`,
              left: `${sq.x * width + 1}px`,
              top: `${sq.y * height + 1}px`,
              backgroundColor: "rgba(0,0,0,1)",
              '--duration': `${sq.duration}s`,
              '--delay': `${sq.delay}s`,
              '--max-opacity': maxOpacity
            }}
          />
        ))}
      </div>
    </>
  );
}
