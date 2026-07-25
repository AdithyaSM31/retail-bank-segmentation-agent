import React from 'react';
import { motion } from 'framer-motion';

export const KineticText = ({ text, className, style }) => {
  const letters = text.split("");

  return (
    <h1 style={{ display: 'flex', flexWrap: 'wrap', overflow: 'hidden', ...style }} className={className}>
      {letters.map((char, index) => (
        <motion.span
          key={index}
          initial={{ y: "100%", opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          transition={{
            type: "spring",
            damping: 20,
            stiffness: 100,
            delay: index * 0.03,
          }}
          style={{ display: 'inline-block' }}
        >
          {char === " " ? "\u00A0" : char}
        </motion.span>
      ))}
    </h1>
  );
};
