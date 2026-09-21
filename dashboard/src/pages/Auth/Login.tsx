import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/useAuth';
import { KeyRound, Mail, AlertCircle } from 'lucide-react';
import { VeltLogo } from '../../components/VeltLogo';

export const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      await login(email, password);
      navigate('/');
    } catch (err: any) {
      setError(err.message || 'Failed to sign in. Please verify your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const containerRef = useRef<HTMLDivElement>(null);

  // Mouse move effect for radial gradients
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      const container = containerRef.current;
      if (container) {
        const rect = container.getBoundingClientRect();
        const x = ((e.clientX - rect.left) / rect.width) * 100;
        const y = ((e.clientY - rect.top) / rect.height) * 100;
        container.style.setProperty('--mouse-x', `${x}%`);
        container.style.setProperty('--mouse-y', `${y}%`);
      }
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  return (
    <div 
      ref={containerRef}
      className="min-h-screen flex items-center justify-center bg-neutral-background p-6 relative overflow-hidden"
    >
      {/* Dynamic gradient background */}
      <div className="absolute inset-0 hero-dynamic-gradient -z-10"></div>

      <div className="w-full max-w-md bg-white/40 border border-white/60 backdrop-blur-2xl shadow-xl rounded-3xl p-8 relative z-10">
        
        {/* Brand */}
        <div className="text-center mb-8">
          <Link className="inline-flex font-sans text-2xl font-bold tracking-tighter text-brand items-center gap-2 mb-3" to="/">
            <VeltLogo className="h-8 w-8 shrink-0" animated />
            <span className="text-xl font-bold">Velt</span>
          </Link>
          <h1 className="text-2xl font-extrabold text-neutral-charcoal tracking-tight mt-2">Welcome Back</h1>
          <p className="text-sm text-neutral-mediumgray font-semibold mt-1">Log in to manage your AI search console</p>
        </div>

        {/* Error Alert */}
        {error && (
          <div className="mb-6 p-4 rounded-xl bg-red-50 border border-red-200 flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-red-600 shrink-0 mt-0.5" />
            <span className="text-sm text-red-700 font-semibold">{error}</span>
          </div>
        )}

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-xs font-bold text-neutral-darkgray uppercase tracking-wider mb-2">
              Email Address
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-neutral-mediumgray">
                <Mail className="w-4 h-4" />
              </span>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="block w-full pl-10 pr-4 py-3 bg-white/50 border border-white/60 rounded-xl text-neutral-charcoal placeholder-neutral-mediumgray text-sm focus:outline-none focus:border-brand focus:ring-4 focus:ring-brand/15 transition-all font-medium"
                placeholder="you@example.com"
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-bold text-neutral-darkgray uppercase tracking-wider mb-2">
              Password
            </label>
            <div className="relative">
              <span className="absolute inset-y-0 left-0 pl-3.5 flex items-center text-neutral-mediumgray">
                <KeyRound className="w-4 h-4" />
              </span>
              <input
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="block w-full pl-10 pr-4 py-3 bg-white/50 border border-white/60 rounded-xl text-neutral-charcoal placeholder-neutral-mediumgray text-sm focus:outline-none focus:border-brand focus:ring-4 focus:ring-brand/15 transition-all font-medium"
                placeholder="••••••••"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3.5 px-4 bg-brand text-white font-bold rounded-xl shadow-md hover:bg-brand-dark transition-all flex items-center justify-center gap-2 cursor-pointer disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin"></div>
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-neutral-mediumgray font-semibold">
          Have a beta invitation?{' '}
          <Link to="/signup" className="text-brand hover:underline font-bold">
            Redeem it
          </Link>
        </div>
      </div>
    </div>
  );
};
