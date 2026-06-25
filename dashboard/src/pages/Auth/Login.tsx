import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { KeyRound, Mail, AlertCircle } from 'lucide-react';

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
            <svg className="h-8 w-8 animate-pulse shrink-0" fill="none" viewBox="0 0 48 46" xmlns="http://www.w3.org/2000/svg">
              <path fill="#863bff" d="M25.946 44.938c-.664.845-2.021.375-2.021-.698V33.937a2.26 2.26 0 0 0-2.262-2.262H10.287c-.92 0-1.456-1.04-.92-1.788l7.48-10.471c1.07-1.497 0-3.578-1.842-3.578H1.237c-.92 0-1.456-1.04-.92-1.788L10.013.474c.214-.297.556-.474.92-.474h28.894c.92 0 1.456 1.04.92 1.788l-7.48 10.471c-1.07 1.498 0 3.579 1.842 3.579h11.377c.943 0 1.473 1.088.89 1.83L25.947 44.94z" style={{ fill: '#863bff', fillOpacity: 1 }}/>
              <mask id="a" width="48" height="46" x="0" y="0" maskUnits="userSpaceOnUse" style={{ maskType: 'alpha' }}>
                <path fill="#000" d="M25.842 44.938c-.664.844-2.021.375-2.021-.698V33.937a2.26 2.26 0 0 0-2.262-2.262H10.183c-.92 0-1.456-1.04-.92-1.788l7.48-10.471c1.07-1.498 0-3.579-1.842-3.579H1.133c-.92 0-1.456-1.04-.92-1.787L9.91.473c.214-.297.556-.474.92-.474h28.894c.92 0 1.456 1.04.92 1.788l-7.48 10.471c-1.07 1.498 0 3.578 1.842 3.578h11.377c.943 0 1.473 1.088.89 1.832L25.843 44.94z" style={{ fill: '#000', fillOpacity: 1 }}/>
              </mask>
              <g mask="url(#a)">
                <g filter="url(#b)">
                  <ellipse cx="5.508" cy="14.704" fill="#ede6ff" rx="5.508" ry="14.704" style={{ fill: '#ede6ff', fillOpacity: 1 }} transform="matrix(.00324 1 1 -.00324 -4.47 31.516)"/>
                </g>
                <g filter="url(#c)">
                  <ellipse cx="10.399" cy="29.851" fill="#ede6ff" rx="10.399" ry="29.851" style={{ fill: '#ede6ff', fillOpacity: 1 }} transform="matrix(.00324 1 1 -.00324 -39.328 7.883)"/>
                </g>
                <g filter="url(#d)">
                  <ellipse cx="5.508" cy="30.487" fill="#7e14ff" rx="5.508" ry="30.487" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(89.814 -25.913 -14.639)scale(1 -1)"/>
                </g>
                <g filter="url(#e)">
                  <ellipse cx="5.508" cy="30.599" fill="#7e14ff" rx="5.508" ry="30.599" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(89.814 -32.644 -3.334)scale(1 -1)"/>
                </g>
                <g filter="url(#f)">
                  <ellipse cx="5.508" cy="30.599" fill="#7e14ff" rx="5.508" ry="30.599" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="matrix(.00324 1 1 -.00324 -34.34 30.47)"/>
                </g>
                <g filter="url(#g)">
                  <ellipse cx="14.072" cy="22.078" fill="#ede6ff" rx="14.072" ry="22.078" style={{ fill: '#ede6ff', fillOpacity: 1 }} transform="rotate(93.35 24.506 48.493)scale(-1 1)"/>
                </g>
                <g filter="url(#h)">
                  <ellipse cx="3.47" cy="21.501" fill="#7e14ff" rx="3.47" ry="21.501" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(89.009 28.708 47.59)scale(-1 1)"/>
                </g>
                <g filter="url(#i)">
                  <ellipse cx="3.47" cy="21.501" fill="#7e14ff" rx="3.47" ry="21.501" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(89.009 28.708 47.59)scale(-1 1)"/>
                </g>
                <g filter="url(#j)">
                  <ellipse cx=".387" cy="8.972" fill="#7e14ff" rx="4.407" ry="29.108" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(39.51 .387 8.972)"/>
                </g>
                <g filter="url(#k)">
                  <ellipse cx="47.523" cy="-6.092" fill="#7e14ff" rx="4.407" ry="29.108" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(37.892 47.523 -6.092)"/>
                </g>
                <g filter="url(#l)">
                  <ellipse cx="41.412" cy="6.333" fill="#47bfff" rx="5.971" ry="9.665" style={{ fill: '#47bfff', fillOpacity: 1 }} transform="rotate(37.892 41.412 6.333)"/>
                </g>
                <g filter="url(#m)">
                  <ellipse cx="-1.879" cy="38.332" fill="#7e14ff" rx="4.407" ry="29.108" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(37.892 -1.88 38.332)"/>
                </g>
                <g filter="url(#n)">
                  <ellipse cx="-1.879" cy="38.332" fill="#7e14ff" rx="4.407" ry="29.108" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(37.892 -1.88 38.332)"/>
                </g>
                <g filter="url(#o)">
                  <ellipse cx="35.651" cy="29.907" fill="#7e14ff" rx="4.407" ry="29.108" style={{ fill: '#7e14ff', fillOpacity: 1 }} transform="rotate(37.892 35.651 29.907)"/>
                </g>
                <g filter="url(#p)">
                  <ellipse cx="38.418" cy="32.4" fill="#47bfff" rx="5.971" ry="15.297" style={{ fill: '#47bfff', fillOpacity: 1 }} transform="rotate(37.892 38.418 32.4)"/>
                </g>
              </g>
              <defs>
                <filter id="b" width="60.045" height="41.654" x="-19.77" y="16.149" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="7.659"/>
                </filter>
                <filter id="c" width="90.34" height="51.437" x="-54.613" y="-7.533" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="7.659"/>
                </filter>
                <filter id="d" width="79.355" height="29.4" x="-49.64" y="2.03" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="e" width="79.579" height="29.4" x="-45.045" y="20.029" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="f" width="79.579" height="29.4" x="-43.513" y="21.178" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="g" width="74.749" height="58.852" x="15.756" y="-17.901" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="7.659"/>
                </filter>
                <filter id="h" width="61.377" height="25.362" x="23.548" y="2.284" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="i" width="61.377" height="25.362" x="23.548" y="2.284" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="j" width="56.045" height="63.649" x="-27.636" y="-22.853" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="k" width="54.814" height="64.646" x="20.116" y="-38.415" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="l" width="33.541" height="35.313" x="24.641" y="-11.323" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="m" width="54.814" height="64.646" x="-29.286" y="6.009" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="n" width="54.814" height="64.646" x="-29.286" y="6.009" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="o" width="54.814" height="64.646" x="8.244" y="-2.416" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
                <filter id="p" width="39.409" height="43.623" x="18.713" y="10.588" colorInterpolationFilters="sRGB" filterUnits="userSpaceOnUse">
                  <feFlood floodOpacity="0" result="BackgroundImageFix"/>
                  <feBlend in="SourceGraphic" in2="BackgroundImageFix" result="shape"/>
                  <feGaussianBlur result="effect1_foregroundBlur_2002_17158" stdDeviation="4.596"/>
                </filter>
              </defs>
            </svg>
            <span className="text-xl font-bold">Velt</span>
          </Link>
          <h2 className="text-2xl font-extrabold text-neutral-charcoal tracking-tight mt-2">Welcome Back</h2>
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
          Don't have an account?{' '}
          <Link to="/signup" className="text-brand hover:underline font-bold">
            Create an account
          </Link>
        </div>
      </div>
    </div>
  );
};
