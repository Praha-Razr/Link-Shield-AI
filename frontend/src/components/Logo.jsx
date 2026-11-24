import React from 'react';

export default function Logo({ size = 'default', showTagline = true, className = '' }) {
  const isSmall = size === 'small';

  return (
    <div className={`flex items-center gap-3 select-none ${className}`}>
      {/* Shield + Link / Check SVG */}
      <div className="relative flex-shrink-0">
        <svg
          className={`${isSmall ? 'w-8 h-8' : 'w-10 h-10'} text-electric-cyan drop-shadow-[0_0_12px_rgba(6,182,212,0.4)]`}
          viewBox="0 0 36 36"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          {/* Outer Shield Outline */}
          <path
            d="M18 3L5 8.5V17.5C5 25.5 10.5 32.5 18 34.5C25.5 32.5 31 25.5 31 17.5V8.5L18 3Z"
            fill="url(#shield-grad)"
            stroke="#38bdf8"
            strokeWidth="1.8"
            strokeLinejoin="round"
          />
          {/* Inner Link / Check Motif */}
          <path
            d="M11 18.5L16 23.5L25 13"
            stroke="#ffffff"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
          <path
            d="M14 12H20M16 26H20"
            stroke="#06b6d4"
            strokeWidth="1.5"
            strokeLinecap="round"
            opacity="0.8"
          />
          <defs>
            <linearGradient id="shield-grad" x1="5" y1="3" x2="31" y2="34.5" gradientUnits="userSpaceOnUse">
              <stop stopColor="#1e3a8a" />
              <stop offset="0.6" stopColor="#0369a1" />
              <stop offset="1" stopColor="#0891b2" />
            </linearGradient>
          </defs>
        </svg>
      </div>

      {/* Brand Name & Tagline */}
      <div>
        <div className="flex items-center gap-1.5 font-extrabold tracking-wider leading-none text-white">
          <span className="text-white text-lg tracking-wide font-black">LINKSHIELD</span>
          <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent text-lg font-black">AI</span>
        </div>
        {showTagline && (
          <p className="text-[10px] uppercase tracking-widest text-slate-400 font-semibold mt-1">
            Detect. Explain. Investigate. Protect.
          </p>
        )}
      </div>
    </div>
  );
}
