import React, { useState } from 'react';
import { Link, useNavigate, useLocation, useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import {
  Settings,
  BarChart3,
  LogOut,
  Store as StoreIcon,
  Database,
  Key,
  Globe,
  BookOpen,
  ChevronDown,
  Plus,
  Menu,
  X
} from 'lucide-react';

interface LayoutProps {
  children: React.ReactNode;
  stores?: Array<{ id: string; name: string }>;
  selectedStoreId?: string;
}

export const Layout: React.FC<LayoutProps> = ({
  children,
  stores = [],
  selectedStoreId,
}) => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { storeId } = useParams<{ storeId: string }>();

  const activeStoreId = storeId || selectedStoreId;
  const currentStore = stores.find((s) => s.id === activeStoreId);

  // Store selector drop state
  const [storeSelectOpen, setStoreSelectOpen] = useState(false);
  // Mobile responsive sidebar open/close state
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const isActive = (path: string) => location.pathname === path;

  const handleStoreChange = (id: string) => {
    setStoreSelectOpen(false);
    // Preserving sub-action routing if we switch stores
    if (location.pathname.includes('/analytics')) {
      navigate(`/stores/${id}/analytics`);
    } else if (location.pathname.includes('/settings')) {
      navigate(`/stores/${id}/settings`);
    } else if (location.pathname.includes('/keys')) {
      navigate(`/stores/${id}/keys`);
    } else {
      navigate(`/stores/${id}`);
    }
  };

  return (
    <div className="flex h-screen bg-slate-50 text-neutral-charcoal font-sans overflow-hidden">
      
      {/* Sidebar overlay backdrop for mobile */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-slate-900/30 backdrop-blur-xs z-30 lg:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Redesigned Sidebar: Stripe-like responsive visual layout */}
      <aside className={`fixed inset-y-0 left-0 w-72 bg-white border-r border-neutral-lightgray flex flex-col justify-between shrink-0 z-40 transform transition-transform duration-200 ease-in-out lg:relative lg:translate-x-0 ${
        sidebarOpen ? 'translate-x-0' : '-translate-x-full'
      }`}>
        <div className="flex flex-col flex-1 overflow-y-auto">
          
          {/* Logo Header */}
          <div className="h-16 flex items-center px-6 border-b border-neutral-lightgray/80 justify-between shrink-0">
            <Link className="font-sans text-xl font-bold tracking-tighter text-brand flex items-center gap-2" to="/">
              <svg className="h-6 w-6 animate-pulse shrink-0" fill="none" viewBox="0 0 48 46" xmlns="http://www.w3.org/2000/svg">
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
              <span className="text-xl font-black tracking-tighter text-neutral-charcoal">Velt</span>
            </Link>
            <div className="flex items-center gap-1.5 shrink-0">
              <span className="text-[10px] bg-brand/10 border border-brand/25 text-brand px-2 py-0.5 rounded-full font-bold uppercase">Console</span>
              <button
                type="button"
                onClick={() => setSidebarOpen(false)}
                className="p-1 text-neutral-mediumgray hover:text-neutral-charcoal lg:hidden rounded-lg hover:bg-slate-100 transition-colors"
                aria-label="Close sidebar"
              >
                <X className="w-4 h-4" />
              </button>
            </div>
          </div>

          {/* Store Selector Dropdown */}
          {stores.length > 0 && (
            <div className="px-4 py-3 border-b border-neutral-lightgray/80 relative shrink-0">
              <button
                onClick={() => setStoreSelectOpen(!storeSelectOpen)}
                className="w-full flex items-center justify-between px-3 py-2 bg-slate-50 hover:bg-slate-100/80 border border-neutral-lightgray rounded-xl text-xs font-bold text-neutral-charcoal transition-all"
              >
                <div className="flex items-center gap-2 truncate">
                  <div className="w-5 h-5 bg-brand text-white rounded-md flex items-center justify-center font-black text-[10px] shadow-sm">
                    {currentStore ? currentStore.name[0].toUpperCase() : 'S'}
                  </div>
                  <span className="truncate">{currentStore ? currentStore.name : 'Select Store...'}</span>
                </div>
                <ChevronDown className="w-3.5 h-3.5 text-neutral-mediumgray shrink-0" />
              </button>

              {/* Selector menu */}
              {storeSelectOpen && (
                <div className="absolute top-[90%] left-4 right-4 bg-white border border-neutral-lightgray/90 rounded-xl shadow-xl z-30 p-1.5 space-y-1 mt-1 animate-slide-up">
                  <div className="text-[9px] font-bold text-neutral-mediumgray px-2 py-1 uppercase tracking-wider">Switch workspace</div>
                  {stores.map((s) => (
                    <button
                      key={s.id}
                      onClick={() => handleStoreChange(s.id)}
                      className={`w-full flex items-center justify-between px-2 py-1.5 rounded-lg text-xs font-semibold text-left transition-all ${
                        s.id === activeStoreId
                          ? 'bg-brand/5 text-brand'
                          : 'hover:bg-slate-50 text-neutral-charcoal'
                      }`}
                    >
                      <span className="truncate">{s.name}</span>
                      {s.id === activeStoreId && <span className="w-1.5 h-1.5 bg-brand rounded-full"></span>}
                    </button>
                  ))}
                  <hr className="border-neutral-lightgray/80 my-1" />
                  <Link
                    to="/stores"
                    onClick={() => setStoreSelectOpen(false)}
                    className="w-full flex items-center gap-1.5 px-2 py-1.5 rounded-lg text-xs font-bold text-brand hover:bg-brand/5 text-left"
                  >
                    <Plus className="w-3.5 h-3.5" /> Connect New Store
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Navigation Links */}
          <nav className="p-4 space-y-6 flex-1">
            
            {/* Workspace section */}
            <div className="space-y-1">
              <div className="px-3 py-1 text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                Workspace
              </div>
              <Link
                to="/stores"
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  isActive('/stores')
                    ? 'bg-brand text-white shadow-md shadow-brand/10'
                    : 'text-neutral-mediumgray hover:bg-slate-50 hover:text-neutral-charcoal'
                }`}
              >
                <StoreIcon className="w-4 h-4" />
                My Stores
              </Link>
              <Link
                to={activeStoreId ? `/stores/${activeStoreId}/analytics` : '#'}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  !activeStoreId 
                    ? 'opacity-40 cursor-not-allowed text-neutral-mediumgray' 
                    : isActive(`/stores/${activeStoreId}/analytics`)
                      ? 'bg-brand text-white shadow-md shadow-brand/10'
                      : 'text-neutral-mediumgray hover:bg-slate-50 hover:text-neutral-charcoal'
                }`}
                onClick={(e) => {
                  if (!activeStoreId) {
                    e.preventDefault();
                    alert('Please select or connect a store first.');
                  }
                }}
              >
                <BarChart3 className="w-4 h-4" />
                Search Intelligence
              </Link>
            </div>

            {/* Configuration section */}
            <div className="space-y-1">
              <div className="px-3 py-1 text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                Configuration
              </div>
              <Link
                to={activeStoreId ? `/stores/${activeStoreId}` : '#'}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  !activeStoreId 
                    ? 'opacity-40 cursor-not-allowed text-neutral-mediumgray' 
                    : location.pathname === `/stores/${activeStoreId}`
                      ? 'bg-brand text-white shadow-md shadow-brand/10'
                      : 'text-neutral-mediumgray hover:bg-slate-50 hover:text-neutral-charcoal'
                }`}
                onClick={(e) => {
                  if (!activeStoreId) {
                    e.preventDefault();
                    alert('Please select or connect a store first.');
                  }
                }}
              >
                <Database className="w-4 h-4" />
                Product Catalog
              </Link>
              <Link
                to={activeStoreId ? `/stores/${activeStoreId}/settings` : '#'}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  !activeStoreId 
                    ? 'opacity-40 cursor-not-allowed text-neutral-mediumgray' 
                    : isActive(`/stores/${activeStoreId}/settings`)
                      ? 'bg-brand text-white shadow-md shadow-brand/10'
                      : 'text-neutral-mediumgray hover:bg-slate-50 hover:text-neutral-charcoal'
                }`}
                onClick={(e) => {
                  if (!activeStoreId) {
                    e.preventDefault();
                    alert('Please select or connect a store first.');
                  }
                }}
              >
                <Settings className="w-4 h-4" />
                Widget Builder
              </Link>
              <Link
                to={activeStoreId ? `/stores/${activeStoreId}/keys` : '#'}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                  !activeStoreId 
                    ? 'opacity-40 cursor-not-allowed text-neutral-mediumgray' 
                    : isActive(`/stores/${activeStoreId}/keys`)
                      ? 'bg-brand text-white shadow-md shadow-brand/10'
                      : 'text-neutral-mediumgray hover:bg-slate-50 hover:text-neutral-charcoal'
                }`}
                onClick={(e) => {
                  if (!activeStoreId) {
                    e.preventDefault();
                    alert('Please select or connect a store first.');
                  }
                }}
              >
                <Key className="w-4 h-4" />
                API Keys
              </Link>
            </div>

            {/* Developer section */}
            <div className="space-y-1">
              <div className="px-3 py-1 text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                Developer
              </div>
              <a
                href="http://localhost:8000/docs"
                target="_blank"
                rel="noreferrer"
                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-bold text-neutral-mediumgray hover:bg-slate-50 hover:text-neutral-charcoal transition-all"
              >
                <BookOpen className="w-4 h-4" />
                Documentation API
              </a>
              <div className="flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold text-neutral-mediumgray hover:bg-slate-50 hover:text-neutral-charcoal cursor-default select-none">
                <div className="flex items-center gap-3">
                  <Globe className="w-4 h-4" />
                  Webhooks Ingest
                </div>
                <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
              </div>
            </div>

          </nav>
        </div>

        {/* Profile Footer Account block */}
        <div className="p-4 border-t border-neutral-lightgray/80 bg-slate-50 shrink-0">
          <div className="flex items-center gap-3 px-2 py-1.5">
            <div className="w-8 h-8 rounded-full bg-brand flex items-center justify-center text-white font-black text-xs shadow-inner">
              {user?.full_name[0].toUpperCase() || 'U'}
            </div>
            <div className="overflow-hidden">
              <div className="text-xs font-extrabold text-neutral-charcoal truncate leading-tight">
                {user?.full_name}
              </div>
              <div className="text-[10px] font-semibold text-neutral-mediumgray truncate mt-0.5">{user?.email}</div>
            </div>
          </div>
          <button
            onClick={() => {
              logout();
              navigate('/login');
            }}
            className="flex items-center justify-center gap-1.5 w-full px-3 py-2 hover:bg-red-50 border border-transparent hover:border-red-100 rounded-xl text-xs font-bold text-red-500 transition-all mt-3 cursor-pointer"
          >
            <LogOut className="w-3.5 h-3.5" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Workspace Frame */}
      <div className="flex-1 flex flex-col overflow-hidden bg-slate-50">
        
        {/* Top Header Context bar */}
        <header className="h-16 border-b border-neutral-lightgray/80 bg-white flex items-center justify-between px-4 lg:px-8 z-10 shrink-0">
          <div className="flex items-center gap-3">
            {/* Mobile Sidebar Hamburger Toggle */}
            <button
              type="button"
              onClick={() => setSidebarOpen(true)}
              className="p-1.5 -ml-1 text-neutral-mediumgray hover:text-neutral-charcoal lg:hidden rounded-xl hover:bg-slate-50 border border-neutral-lightgray/50 transition-colors"
              aria-label="Open sidebar"
            >
              <Menu className="w-4.5 h-4.5" />
            </button>

            {currentStore ? (
              <div className="flex items-center gap-2">
                <StoreIcon className="w-4.5 h-4.5 text-brand" />
                <span className="font-extrabold text-sm text-neutral-charcoal">
                  {currentStore.name}
                </span>
                <span className="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider bg-green-50 border border-green-200 text-green-700 flex items-center gap-1">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse"></span> Active
                </span>
              </div>
            ) : (
              <div className="flex items-center gap-2 text-neutral-mediumgray font-semibold text-sm">
                <Globe className="w-4 h-4 animate-spin text-brand" />
                <span>Loading Console workspace...</span>
              </div>
            )}
          </div>

          <div className="flex items-center gap-4">
            {currentStore && (
              <span className="hidden sm:inline-block text-[10px] text-neutral-mediumgray bg-slate-50 border border-neutral-lightgray/80 px-2.5 py-1 rounded-lg font-mono font-bold select-all shadow-sm">
                Store ID: {currentStore.id}
              </span>
            )}
          </div>
        </header>

        {/* Viewport content */}
        <main className="flex-1 overflow-y-auto p-4 lg:p-8 relative">
          {children}
        </main>
      </div>

    </div>
  );
};
