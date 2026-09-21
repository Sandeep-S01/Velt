import React, { useId } from 'react';

interface VeltLogoProps {
  className?: string;
  animated?: boolean;
  title?: string;
}

/** Velt's flowing V mark. */
export const VeltLogo: React.FC<VeltLogoProps> = ({
  className = 'h-8 w-8',
  animated = false,
  title,
}) => {
  const instanceId = useId().replace(/:/g, '');
  const gradientId = `velt-gradient-${instanceId}`;

  return (
    <svg
      className={`${className}${animated ? ' animate-pulse motion-reduce:animate-none' : ''}`}
      viewBox="0 0 48 48"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role={title ? 'img' : undefined}
      aria-hidden={title ? undefined : true}
      aria-label={title}
    >
      {title && <title>{title}</title>}
      <defs>
        <linearGradient id={gradientId} x1="3" y1="9" x2="45" y2="15" gradientUnits="userSpaceOnUse">
          <stop stopColor="#6D28D9" />
          <stop offset="0.48" stopColor="#863BFF" />
          <stop offset="1" stopColor="#47BFFF" />
        </linearGradient>
      </defs>
      <path
        d="M7.8 7.6C12.5 5.8 16.8 7.5 19.7 13L24 21.1C25.5 24 28.5 24 30.1 21.1L35 12.7C37.8 8.7 42.6 7.3 45.7 8.9C48 10.2 47.4 13.3 44.2 14.3C42 15 40.4 16.6 39 19.2L30.5 36.9C27.2 43.8 18.7 44.2 14.2 37.2L2.7 17.7C.2 13.4 2.8 9.5 7.8 7.6Z"
        fill={`url(#${gradientId})`}
      />
    </svg>
  );
};
