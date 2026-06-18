import { useEffect, useState } from 'react';
import logoImg from '@/assets/logo.png';

interface SplashScreenProps {
  onFinished: () => void;
  /** Duration in ms before the splash fades out */
  duration?: number;
}

const SplashScreen = ({ onFinished, duration = 2400 }: SplashScreenProps) => {
  const [progress, setProgress] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // Animate progress bar
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        // Accelerating progress curve
        const increment = prev < 60 ? 3 : prev < 85 ? 2 : 1;
        return Math.min(prev + increment, 100);
      });
    }, duration / 60);

    // Start fade out near the end
    const fadeTimer = setTimeout(() => {
      setFadeOut(true);
    }, duration - 500);

    // Signal finished after fade completes
    const finishTimer = setTimeout(() => {
      onFinished();
    }, duration);

    return () => {
      clearInterval(interval);
      clearTimeout(fadeTimer);
      clearTimeout(finishTimer);
    };
  }, [duration, onFinished]);

  return (
    <div
      className={`fixed inset-0 z-[9999] flex items-center justify-center transition-opacity duration-500 ${
        fadeOut ? 'opacity-0' : 'opacity-100'
      }`}
      style={{ background: 'linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)' }}
    >
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <div
            key={i}
            className="absolute rounded-full opacity-10"
            style={{
              width: `${60 + i * 40}px`,
              height: `${60 + i * 40}px`,
              background: i % 2 === 0
                ? 'radial-gradient(circle, #10b981, transparent)'
                : 'radial-gradient(circle, #f97316, transparent)',
              top: `${15 + i * 14}%`,
              left: `${10 + i * 15}%`,
              animation: `splash-float ${3 + i * 0.5}s ease-in-out infinite alternate`,
              animationDelay: `${i * 0.3}s`,
            }}
          />
        ))}
      </div>

      <div className="flex flex-col items-center gap-8 relative">
        {/* Logo with animated ring */}
        <div className="relative">
          {/* Outer spinning ring */}
          <div
            className="absolute -inset-4 rounded-full"
            style={{
              border: '2px solid transparent',
              borderTopColor: '#10b981',
              borderRightColor: '#f97316',
              animation: 'splash-spin 1.5s linear infinite',
            }}
          />
          {/* Inner glow */}
          <div
            className="absolute -inset-2 rounded-full opacity-30"
            style={{
              background: 'radial-gradient(circle, rgba(16, 185, 129, 0.3), transparent 70%)',
              animation: 'splash-pulse 2s ease-in-out infinite',
            }}
          />
          {/* Logo */}
          <img
            src={logoImg}
            alt="CVMatch AI"
            className="w-28 h-28 rounded-full object-cover relative z-10"
            style={{
              boxShadow: '0 0 40px rgba(16, 185, 129, 0.3), 0 0 80px rgba(16, 185, 129, 0.1)',
              animation: 'splash-logo-in 0.8s ease-out forwards',
            }}
          />
        </div>

        {/* App name */}
        <div
          className="text-center"
          style={{ animation: 'splash-text-in 0.8s ease-out 0.3s both' }}
        >
          <h1
            className="text-3xl font-bold tracking-tight"
            style={{
              background: 'linear-gradient(135deg, #10b981, #34d399, #f97316)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            CVMatch AI
          </h1>
          <p className="text-slate-400 text-sm mt-1 tracking-widest uppercase">
            AI Scoring System
          </p>
        </div>

        {/* Progress bar */}
        <div
          className="w-48"
          style={{ animation: 'splash-text-in 0.6s ease-out 0.6s both' }}
        >
          <div className="h-1 bg-slate-700/50 rounded-full overflow-hidden backdrop-blur-sm">
            <div
              className="h-full rounded-full transition-all duration-100 ease-out"
              style={{
                width: `${progress}%`,
                background: 'linear-gradient(90deg, #10b981, #34d399, #f97316)',
                boxShadow: '0 0 12px rgba(16, 185, 129, 0.5)',
              }}
            />
          </div>
          <p className="text-slate-500 text-xs text-center mt-3 font-mono">
            {progress < 100 ? 'Chargement...' : 'Prêt'}
          </p>
        </div>
      </div>

      {/* Keyframe animations */}
      <style>{`
        @keyframes splash-spin {
          to { transform: rotate(360deg); }
        }
        @keyframes splash-pulse {
          0%, 100% { opacity: 0.2; transform: scale(1); }
          50% { opacity: 0.4; transform: scale(1.15); }
        }
        @keyframes splash-float {
          0% { transform: translateY(0) scale(1); }
          100% { transform: translateY(-20px) scale(1.1); }
        }
        @keyframes splash-logo-in {
          0% { opacity: 0; transform: scale(0.5); }
          100% { opacity: 1; transform: scale(1); }
        }
        @keyframes splash-text-in {
          0% { opacity: 0; transform: translateY(15px); }
          100% { opacity: 1; transform: translateY(0); }
        }
      `}</style>
    </div>
  );
};

export default SplashScreen;
