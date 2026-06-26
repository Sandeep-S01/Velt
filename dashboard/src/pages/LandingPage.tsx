import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { getApiDocsUrl, WIDGET_SCRIPT_URL } from '../lib/api';
import {
  ArrowRight,
  Check,
  ChevronDown,
  ChevronUp,
  Code,
  Copy,
  Cpu,
  Database,
  ExternalLink,
  Layers,
  LayoutGrid,
  Sparkles
} from 'lucide-react';

interface SearchDemoProduct {
  title: string;
  price: string;
  image: string;
  matchScore: string;
  category: string;
  tags: string[];
}

const PRESET_QUERIES = {
  jacket: "I need a lightweight waterproof jacket",
  shoes: "black office shoes under 100",
  hoodie: "warm blue hoodie for winter"
};

const DEMO_PRODUCTS: Record<string, {
  detected: { category: string; color?: string; intent?: string; budget?: string };
  products: SearchDemoProduct[];
}> = {
  [PRESET_QUERIES.jacket]: {
    detected: { category: "Jacket", color: "Any", intent: "Waterproof / Lightweight", budget: "Any" },
    products: [
      { title: "StormShield Pro Shell", price: "$110.00", image: "🧥", matchScore: "99% Match", category: "Jacket", tags: ["Rainproof", "Active Fit"] },
      { title: "Pac-lite Windbreaker", price: "$89.00", image: "🧥", matchScore: "96% Match", category: "Jacket", tags: ["Windproof", "Breathable"] },
      { title: "Trail-Ready Raincoat", price: "$120.00", image: "🧥", matchScore: "94% Match", category: "Jacket", tags: ["Stormproof", "Tech Pack"] }
    ]
  },
  [PRESET_QUERIES.shoes]: {
    detected: { category: "Shoes", color: "Black", intent: "Office / Professional", budget: "< $100" },
    products: [
      { title: "Derby Leather Shoes", price: "$89.00", image: "👞", matchScore: "98% Match", category: "Shoes", tags: ["Leather", "Formal"] },
      { title: "Sleek Oxford Loafers", price: "$75.00", image: "👞", matchScore: "94% Match", category: "Shoes", tags: ["Slip-on", "Office"] },
      { title: "Classic Dress Brogues", price: "$95.00", image: "👞", matchScore: "91% Match", category: "Shoes", tags: ["Brogue", "Cushioned"] }
    ]
  },
  [PRESET_QUERIES.hoodie]: {
    detected: { category: "Hoodie / Apparel", color: "Blue", intent: "Winter / Insulated", budget: "Any" },
    products: [
      { title: "Alpine Thermal Hoodie", price: "$68.00", image: "👕", matchScore: "99% Match", category: "Hoodie", tags: ["Thermal", "Sherpa Lining"] },
      { title: "Polar Tech Sweatshirt", price: "$85.00", image: "🧥", matchScore: "95% Match", category: "Hoodie", tags: ["Fleece", "Warm"] },
      { title: "Classic Cozy Pullover", price: "$59.00", image: "👕", matchScore: "92% Match", category: "Hoodie", tags: ["Pullover", "Soft Cotton"] }
    ]
  }
};

export const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Sticky Navbar State
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // FAQ Accordion State
  const [openFaq, setOpenFaq] = useState<number | null>(null);

  // Hero Search Demo State
  const [heroSearchVal, setHeroSearchVal] = useState(PRESET_QUERIES.jacket);

  // Deeper Live Playground State
  const [playgroundQuery, setPlaygroundQuery] = useState(PRESET_QUERIES.shoes);

  // Copy State for script
  const [copied, setCopied] = useState(false);

  // Track scroll position
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setScrolled(true);
      } else {
        setScrolled(false);
      }
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleLaunchApp = () => {
    if (isAuthenticated) {
      navigate('/stores');
    } else {
      navigate('/signup');
    }
  };

  const handleCopyScript = () => {
    navigator.clipboard.writeText(`<script src="${WIDGET_SCRIPT_URL}" data-store-id="velt_store_demo"></script>`);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const heroRef = useRef<HTMLDivElement>(null);
  const ctaRef = useRef<HTMLDivElement>(null);

  // Mouse reactive glow coordinates
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      [heroRef, ctaRef].forEach((ref) => {
        const container = ref.current;
        if (container) {
          const rect = container.getBoundingClientRect();
          const x = ((e.clientX - rect.left) / rect.width) * 100;
          const y = ((e.clientY - rect.top) / rect.height) * 100;
          container.style.setProperty('--mouse-x', `${x}%`);
          container.style.setProperty('--mouse-y', `${y}%`);
        }
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  const handleFaqToggle = (index: number) => {
    setOpenFaq(openFaq === index ? null : index);
  };

  const faqs = [
    {
      q: "What makes Velt different from traditional search?",
      a: "Traditional e-commerce search relies on exact keyword matching. If a customer searches 'warm blue winter jumper' and your product is tagged as 'ocean knit sweatshirt,' traditional search returns zero results. Velt translates catalogs and searches into vector embeddings, finding matches based on semantic meaning, intent, synonyms, and natural speech."
    },
    {
      q: "How does semantic search work?",
      a: "Velt uses machine learning models to generate high-dimensional vector representations of your products (from titles, descriptions, and categories). When a query comes in, it generates a query vector and queries ChromaDB to find products with the highest cosine similarity, returning contextually accurate matches in under 30 milliseconds."
    },
    {
      q: "Can I integrate with Shopify?",
      a: "Yes! Velt features one-click catalog ingestion for Shopify storefronts. You can also ingest catalogs programmatically via our developer APIs or simply upload a CSV/JSON catalog file directly into the dashboard console."
    },
    {
      q: "Do I need machine learning knowledge?",
      a: "No machine learning knowledge is required. We provide a pre-trained, production-ready vector inference pipeline out of the box, along with a visual widget settings builder and analytics console."
    },
    {
      q: "How fast can I deploy Velt?",
      a: "You can go live in under five minutes. Simply sync your store catalog, customize the visual search widget options in the dashboard, and copy-paste our single-line embedding script tag into your store HTML."
    }
  ];

  return (
    <div className="bg-white text-neutral-charcoal font-sans antialiased overflow-x-hidden selection:bg-brand-light/35 selection:text-brand-dark min-h-screen">
      
      {/* Sticky Header Navigation */}
      <nav className={`fixed top-0 left-0 w-full z-50 transition-all duration-300 ${
        scrolled 
          ? 'bg-white/80 backdrop-blur-md border-b border-neutral-lightgray shadow-sm py-4' 
          : 'bg-transparent py-6'
      }`}>
        <div className="max-w-7xl mx-auto px-6 md:px-8 flex justify-between items-center">
          {/* Logo */}
          <Link className="font-sans text-2xl font-bold tracking-tighter text-brand flex items-center gap-2" to="/">
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
            <span className="text-xl font-extrabold tracking-tighter text-neutral-charcoal">Velt</span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden lg:flex items-center gap-8">
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#product">Product</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#features">Features</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#demo">Interactive Demo</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#dashboard">Dashboard</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#pricing">Pricing</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#faq">FAQ</a>
          </div>

          {/* Desktop Auth CTAs */}
          <div className="hidden lg:flex items-center gap-4">
            <Link
              to={isAuthenticated ? "/stores" : "/login"}
              className="text-sm font-semibold text-neutral-darkgray hover:text-brand px-4 py-2 transition-colors"
            >
              {isAuthenticated ? "Console" : "Login"}
            </Link>
            <button
              onClick={handleLaunchApp}
              className="bg-brand text-white text-sm font-bold px-5 py-2.5 rounded-full hover:bg-brand-dark transition-all active:scale-95 shadow-md shadow-brand/10"
            >
              {isAuthenticated ? "Dashboard" : "Get Started"}
            </button>
          </div>

          {/* Mobile Menu Button */}
          <button 
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="lg:hidden text-neutral-charcoal focus:outline-none p-1"
          >
            <span className="material-symbols-outlined text-2xl">
              {mobileMenuOpen ? 'close' : 'menu'}
            </span>
          </button>
        </div>

        {/* Mobile Menu Drawer */}
        {mobileMenuOpen && (
          <div className="lg:hidden bg-white border-b border-neutral-lightgray px-6 py-6 space-y-4 absolute top-full left-0 w-full shadow-lg z-50">
            <div className="flex flex-col gap-4">
              <a onClick={() => setMobileMenuOpen(false)} className="text-base font-semibold text-neutral-darkgray hover:text-brand" href="#product">Product</a>
              <a onClick={() => setMobileMenuOpen(false)} className="text-base font-semibold text-neutral-darkgray hover:text-brand" href="#features">Features</a>
              <a onClick={() => setMobileMenuOpen(false)} className="text-base font-semibold text-neutral-darkgray hover:text-brand" href="#demo">Interactive Demo</a>
              <a onClick={() => setMobileMenuOpen(false)} className="text-base font-semibold text-neutral-darkgray hover:text-brand" href="#dashboard">Dashboard</a>
              <a onClick={() => setMobileMenuOpen(false)} className="text-base font-semibold text-neutral-darkgray hover:text-brand" href="#pricing">Pricing</a>
              <a onClick={() => setMobileMenuOpen(false)} className="text-base font-semibold text-neutral-darkgray hover:text-brand" href="#faq">FAQ</a>
              <hr className="border-neutral-lightgray" />
              <div className="flex items-center gap-4 justify-between pt-2">
                <Link
                  onClick={() => setMobileMenuOpen(false)}
                  to={isAuthenticated ? "/stores" : "/login"}
                  className="text-base font-bold text-neutral-charcoal"
                >
                  {isAuthenticated ? "Console" : "Login"}
                </Link>
                <button
                  onClick={() => {
                    setMobileMenuOpen(false);
                    handleLaunchApp();
                  }}
                  className="bg-brand text-white text-sm font-bold px-6 py-2.5 rounded-full hover:bg-brand-dark w-fit transition-all"
                >
                  {isAuthenticated ? "Dashboard" : "Get Started"}
                </button>
              </div>
            </div>
          </div>
        )}
      </nav>

      {/* Main Content Layout */}
      <main className="max-w-[1728px] mx-auto w-full">
        
        {/* Section 1: Hero */}
        <section 
          ref={heroRef}
          className="relative pt-36 md:pt-48 pb-20 px-6 md:px-8 min-h-[95vh] flex flex-col items-center justify-center text-center overflow-hidden"
          id="product"
        >
          {/* Mouse Reactive Radial Gradient Background */}
          <div className="absolute inset-0 hero-dynamic-gradient -z-10"></div>
          
          {/* Badge */}
          <div className="inline-flex items-center gap-2 bg-brand/5 border border-brand/20 rounded-full px-4.5 py-1.5 mb-8 shadow-sm">
            <span className="bg-brand text-white font-bold text-[9px] px-2 py-0.5 rounded-full uppercase tracking-wider">NEW</span>
            <span className="text-xs font-bold text-brand">AI-powered semantic search infrastructure</span>
          </div>
          
          <h1 className="font-sans text-5xl md:text-[68px] font-extrabold leading-[1.08] tracking-tighter text-neutral-charcoal max-w-4xl mb-6">
            Turn every product search into a buying conversation.
          </h1>
          
          <p className="text-lg md:text-xl text-neutral-mediumgray max-w-2xl mb-10 font-medium leading-relaxed">
            Velt understands what shoppers mean, not just what they type. Add AI-powered vector search widgets to any storefront in minutes.
          </p>

          <div className="flex flex-col sm:flex-row items-center gap-4 mb-16">
            <button
              onClick={handleLaunchApp}
              className="bg-brand text-white font-bold text-base px-8 py-3.5 rounded-full hover:bg-brand-dark hover:scale-102 transition-all shadow-lg shadow-brand/10 active:scale-98 flex items-center gap-2 w-full sm:w-auto justify-center"
            >
              Start Building Free <ArrowRight className="w-4 h-4" />
            </button>
            <a
              href="#demo"
              className="bg-white/75 backdrop-blur-sm border border-neutral-lightgray hover:border-neutral-darkgray/30 text-neutral-charcoal font-bold text-base px-8 py-3.5 rounded-full hover:bg-white hover:scale-102 transition-all active:scale-98 w-full sm:w-auto text-center"
            >
              View Demo
            </a>
          </div>

          {/* Interactive Search Box Simulation inside Hero */}
          <div className="w-full max-w-4xl bg-white rounded-3xl border border-neutral-lightgray/80 shadow-xl shadow-slate-100 p-6 md:p-8 text-left transition-all">
            <div className="flex flex-col md:flex-row gap-6 items-start">
              
              {/* Left Side: Mock Search Bar */}
              <div className="w-full md:w-5/12 space-y-4">
                <div className="text-xs font-bold text-neutral-mediumgray uppercase tracking-wider">Try A Live Search Query</div>
                <div className="space-y-2.5">
                  {(Object.keys(PRESET_QUERIES) as Array<keyof typeof PRESET_QUERIES>).map((key) => {
                    const q = PRESET_QUERIES[key];
                    const active = heroSearchVal === q;
                    return (
                      <button
                        key={key}
                        onClick={() => {
                          setHeroSearchVal(q);
                        }}
                        className={`w-full text-left px-4 py-3 rounded-xl border text-sm font-semibold transition-all flex items-center justify-between ${
                          active 
                            ? 'border-brand bg-brand/5 text-brand shadow-sm' 
                            : 'border-neutral-lightgray bg-neutral-background hover:bg-neutral-lightgray/40 text-neutral-darkgray'
                        }`}
                      >
                        <span>"{q}"</span>
                        {active && <span className="w-2 h-2 rounded-full bg-brand"></span>}
                      </button>
                    );
                  })}
                </div>
              </div>

              {/* Right Side: Mock Ingestion Output */}
              <div className="w-full md:w-7/12 bg-neutral-background rounded-2xl border border-neutral-lightgray/80 p-5 md:p-6 space-y-4">
                <div className="flex items-center justify-between border-b border-neutral-lightgray pb-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-4 h-4 text-brand animate-pulse" />
                    <span className="text-xs font-bold text-neutral-charcoal uppercase tracking-wider">Semantic Match Engine</span>
                  </div>
                  <span className="text-[10px] font-bold text-brand uppercase tracking-wider bg-brand/10 px-2 py-0.5 rounded">Active</span>
                </div>

                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {DEMO_PRODUCTS[heroSearchVal]?.products.map((prod, index) => (
                    <div key={index} className="bg-white border border-neutral-lightgray/80 rounded-xl p-3 shadow-sm hover:shadow-md transition-all flex flex-col justify-between">
                      <div>
                        <div className="text-2xl mb-2">{prod.image}</div>
                        <div className="text-xs font-bold text-neutral-charcoal line-clamp-1">{prod.title}</div>
                        <div className="text-[10px] text-neutral-mediumgray font-semibold mt-0.5">{prod.category}</div>
                      </div>
                      <div className="mt-3 flex items-center justify-between">
                        <span className="text-xs font-black text-neutral-charcoal">{prod.price}</span>
                        <span className="text-[9px] font-bold text-brand uppercase tracking-wider">{prod.matchScore}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

            </div>
          </div>
        </section>

        {/* Section 2: Catalog Integration Pipeline */}
        <section id="features" className="py-24 px-6 md:px-8 bg-neutral-background border-t border-neutral-lightgray">
          <div className="max-w-6xl mx-auto space-y-16">
            
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Connect Catalogs</span>
              <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                Connect your catalog in minutes
              </h2>
              <p className="text-base md:text-lg text-neutral-mediumgray font-medium leading-relaxed max-w-2xl mx-auto">
                Velt synchronizes your product catalog from any commerce provider and compiles your search indexes into high-performance embeddings automatically.
              </p>
            </div>

            <div className="bg-white rounded-3xl border border-neutral-lightgray/80 p-8 md:p-12 shadow-sm">
              <div className="grid grid-cols-1 lg:grid-cols-4 gap-8 items-center relative">
                
                {/* Step 1 */}
                <div className="space-y-4 text-center lg:text-left">
                  <div className="w-12 h-12 rounded-2xl bg-brand/10 text-brand flex items-center justify-center mx-auto lg:mx-0 shadow-sm border border-brand/10">
                    <Database className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-neutral-charcoal text-base">1. Select Source</h3>
                    <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">
                      Shopify, WooCommerce, CSV, or custom JSON API endpoints.
                    </p>
                  </div>
                  <div className="flex flex-wrap justify-center lg:justify-start gap-1.5 pt-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-neutral-background border border-neutral-lightgray text-neutral-darkgray">Shopify</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-neutral-background border border-neutral-lightgray text-neutral-darkgray">CSV</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-neutral-background border border-neutral-lightgray text-neutral-darkgray">JSON API</span>
                  </div>
                </div>

                {/* Arrow */}
                <div className="hidden lg:flex justify-center text-neutral-lightgray absolute left-1/4 -translate-x-1/2">
                  <ArrowRight className="w-6 h-6 animate-pulse" />
                </div>

                {/* Step 2 */}
                <div className="space-y-4 text-center lg:text-left mt-8 lg:mt-0">
                  <div className="w-12 h-12 rounded-2xl bg-brand/10 text-brand flex items-center justify-center mx-auto lg:mx-0 shadow-sm border border-brand/10">
                    <Cpu className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-neutral-charcoal text-base">2. Vector Generation</h3>
                    <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">
                      Models process descriptions to compute high-dimensional vectors.
                    </p>
                  </div>
                  <div className="flex flex-wrap justify-center lg:justify-start gap-1.5 pt-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-brand/5 border border-brand/20 text-brand">Aura-Mini model</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-brand/5 border border-brand/20 text-brand">Synonyms Mapping</span>
                  </div>
                </div>

                {/* Arrow */}
                <div className="hidden lg:flex justify-center text-neutral-lightgray absolute left-2/4 -translate-x-1/2">
                  <ArrowRight className="w-6 h-6 animate-pulse" />
                </div>

                {/* Step 3 */}
                <div className="space-y-4 text-center lg:text-left mt-8 lg:mt-0">
                  <div className="w-12 h-12 rounded-2xl bg-brand/10 text-brand flex items-center justify-center mx-auto lg:mx-0 shadow-sm border border-brand/10">
                    <Layers className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-neutral-charcoal text-base">3. Search Indexing</h3>
                    <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">
                      Vector spaces deploy automatically inside our ChromaDB cluster.
                    </p>
                  </div>
                  <div className="flex flex-wrap justify-center lg:justify-start gap-1.5 pt-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-neutral-background border border-neutral-lightgray text-neutral-darkgray">ChromaDB Store</span>
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-neutral-background border border-neutral-lightgray text-neutral-darkgray">&lt; 30ms latency</span>
                  </div>
                </div>

                {/* Arrow */}
                <div className="hidden lg:flex justify-center text-neutral-lightgray absolute left-3/4 -translate-x-1/2">
                  <ArrowRight className="w-6 h-6 animate-pulse" />
                </div>

                {/* Step 4 */}
                <div className="space-y-4 text-center lg:text-left mt-8 lg:mt-0">
                  <div className="w-12 h-12 rounded-2xl bg-green-50 text-green-600 flex items-center justify-center mx-auto lg:mx-0 shadow-sm border border-green-200">
                    <LayoutGrid className="w-6 h-6" />
                  </div>
                  <div>
                    <h3 className="font-bold text-neutral-charcoal text-base">4. Storefront Ready</h3>
                    <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">
                      Embeddable client overlay displays results contextually.
                    </p>
                  </div>
                  <div className="flex flex-wrap justify-center lg:justify-start gap-1.5 pt-2">
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-green-50 border border-green-150 text-green-700">Client Widget Live</span>
                  </div>
                </div>

              </div>
            </div>

          </div>
        </section>

        {/* Section 3: Intent-based Search Comparison */}
        <section className="py-24 px-6 md:px-8 bg-white border-t border-neutral-lightgray">
          <div className="max-w-6xl mx-auto space-y-16">
            
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Relevance Comparison</span>
              <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                Search that understands intent
              </h2>
              <p className="text-base md:text-lg text-neutral-mediumgray font-medium leading-relaxed max-w-2xl mx-auto">
                See the contrast between traditional database query matching and Velt's semantic intelligence on a mock shopper's search.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              
              {/* Card 1: Traditional Search */}
              <div className="bg-neutral-background border border-neutral-lightgray/80 rounded-3xl p-6 md:p-8 space-y-6 flex flex-col justify-between">
                <div>
                  <div className="flex justify-between items-center pb-4 border-b border-neutral-lightgray/80">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-red-400"></span>
                      <span className="text-xs font-bold text-neutral-charcoal uppercase tracking-wider">Keyword Matching</span>
                    </div>
                    <span className="text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider bg-neutral-lightgray px-2 py-0.5 rounded">Legacy</span>
                  </div>
                  
                  <div className="mt-6 space-y-4">
                    <div className="bg-white rounded-xl border border-neutral-lightgray/80 p-3.5 flex items-center justify-between">
                      <span className="text-xs font-bold text-neutral-mediumgray">User Query:</span>
                      <span className="text-xs font-black text-neutral-charcoal">"cheap running shoes"</span>
                    </div>

                    <div className="space-y-2">
                      <div className="text-xs font-bold text-neutral-mediumgray uppercase tracking-wider">Search logs:</div>
                      <div className="bg-red-50/50 border border-red-100 rounded-xl p-3.5 text-xs text-red-800 font-semibold space-y-1.5">
                        <div>⚠️ SQL match fails for keyword: 'cheap'</div>
                        <div>⚠️ cos_similarity not supported. Skipping semantic check...</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="bg-white border border-neutral-lightgray/85 rounded-2xl p-6 text-center text-xs text-neutral-mediumgray font-medium mt-8 py-10">
                  ❌ No matching products found for "cheap"
                </div>
              </div>

              {/* Card 2: Velt Search */}
              <div className="bg-white border border-brand/20 rounded-3xl p-6 md:p-8 space-y-6 flex flex-col justify-between shadow-xl shadow-brand/5 relative overflow-hidden">
                <div className="absolute top-0 right-0 bg-brand text-white text-[9px] font-bold px-3 py-1 rounded-bl-xl uppercase tracking-wider">AI Powered</div>
                
                <div>
                  <div className="flex justify-between items-center pb-4 border-b border-neutral-lightgray/80">
                    <div className="flex items-center gap-2">
                      <span className="w-3 h-3 rounded-full bg-brand"></span>
                      <span className="text-xs font-bold text-brand uppercase tracking-wider">Velt Semantic Engine</span>
                    </div>
                  </div>
                  
                  <div className="mt-6 space-y-4">
                    <div className="bg-brand/5 rounded-xl border border-brand/20 p-3.5 flex items-center justify-between">
                      <span className="text-xs font-bold text-brand">User Query:</span>
                      <span className="text-xs font-black text-brand-dark">"cheap running shoes"</span>
                    </div>

                    <div className="space-y-2">
                      <div className="text-xs font-bold text-neutral-mediumgray uppercase tracking-wider">Velt pipeline logs:</div>
                      <div className="bg-neutral-background border border-neutral-lightgray/85 rounded-xl p-3.5 text-xs space-y-1.5 font-semibold text-neutral-darkgray">
                        <div className="flex items-center gap-1.5 text-brand"><Check className="w-3.5 h-3.5" /> Parsed: Activity ➔ Running</div>
                        <div className="flex items-center gap-1.5 text-brand"><Check className="w-3.5 h-3.5" /> Price condition matched: cheap ➔ &lt; $50</div>
                        <div className="flex items-center gap-1.5 text-brand"><Check className="w-3.5 h-3.5" /> Embedding similarity search returned 3 items</div>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mt-8">
                  <div className="bg-neutral-background border border-neutral-lightgray/80 rounded-xl p-3.5 flex flex-col justify-between">
                    <div>
                      <span className="text-lg">👟</span>
                      <div className="text-xs font-bold text-neutral-charcoal mt-1 truncate">Road Runner Pro</div>
                      <span className="text-[10px] text-neutral-mediumgray">Shoes</span>
                    </div>
                    <div className="flex justify-between items-center mt-2 pt-2 border-t border-neutral-lightgray">
                      <span className="text-xs font-bold text-neutral-charcoal">$45.00</span>
                      <span className="text-[9px] font-bold text-brand uppercase">98% Match</span>
                    </div>
                  </div>
                  <div className="bg-neutral-background border border-neutral-lightgray/80 rounded-xl p-3.5 flex flex-col justify-between">
                    <div>
                      <span className="text-lg">👟</span>
                      <div className="text-xs font-bold text-neutral-charcoal mt-1 truncate">Trail Lite Jogger</div>
                      <span className="text-[10px] text-neutral-mediumgray">Shoes</span>
                    </div>
                    <div className="flex justify-between items-center mt-2 pt-2 border-t border-neutral-lightgray">
                      <span className="text-xs font-bold text-neutral-charcoal">$49.00</span>
                      <span className="text-[9px] font-bold text-brand uppercase">95% Match</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>

          </div>
        </section>

        {/* Section 4: Developer Integration Code snippet */}
        <section className="py-24 px-6 md:px-8 bg-neutral-background border-t border-neutral-lightgray">
          <div className="max-w-6xl mx-auto space-y-16">
            
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Developer SDK</span>
              <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                Deploy anywhere
              </h2>
              <p className="text-base md:text-lg text-neutral-mediumgray font-medium leading-relaxed max-w-2xl mx-auto">
                Embed Velt search into any custom HTML storefront or headless stack using a single drop-in script integration.
              </p>
            </div>

            <div className="bg-slate-950 rounded-3xl border border-brand/20 p-6 md:p-8 text-white shadow-xl max-w-3xl mx-auto space-y-4">
              <div className="flex justify-between items-center border-b border-white/10 pb-4">
                <div className="flex items-center gap-2">
                  <Code className="w-5 h-5 text-brand-light" />
                  <span className="text-xs font-bold uppercase tracking-wider text-slate-300">Widget Embedding Script</span>
                </div>
                
                <button
                  onClick={handleCopyScript}
                  className="flex items-center gap-1.5 px-3 py-1.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-xs font-bold text-slate-300 transition-all active:scale-95"
                >
                  {copied ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-green-400" />
                      Copied!
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      Copy Snippet
                    </>
                  )}
                </button>
              </div>

              <pre className="p-4 rounded-xl bg-black/45 border border-white/5 font-mono text-xs text-brand-light select-all overflow-x-auto leading-relaxed">
{`<script 
  src="${WIDGET_SCRIPT_URL}" 
  data-store-id="velt_store_demo">
</script>`}
              </pre>

              <div className="grid grid-cols-3 gap-4 pt-4 border-t border-white/10 text-center text-slate-400 text-xs">
                <div>
                  <h4 className="font-bold text-white mb-1">Single Dependency</h4>
                  <p className="text-[10px]">No complex React or Node bindings required.</p>
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">Tailwind variables</h4>
                  <p className="text-[10px]">Widget colors match your custom primary settings.</p>
                </div>
                <div>
                  <h4 className="font-bold text-white mb-1">Headless API</h4>
                  <p className="text-[10px]">Access raw JSON vector query endpoints easily.</p>
                </div>
              </div>
            </div>

          </div>
        </section>

        {/* Section 5: Search Playground Live Demo (Deep Dive) */}
        <section id="demo" className="py-24 px-6 md:px-8 bg-white border-t border-neutral-lightgray">
          <div className="max-w-6xl mx-auto space-y-16">
            
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Interactive Playground</span>
              <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                Try the live semantic parser
              </h2>
              <p className="text-base md:text-lg text-neutral-mediumgray font-medium leading-relaxed max-w-2xl mx-auto">
                Click a customer query template to see how Velt's parser maps tokens to specific product filters and finds items immediately.
              </p>
            </div>

            <div className="bg-neutral-background border border-neutral-lightgray/80 rounded-3xl p-6 md:p-8 shadow-sm">
              <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
                
                {/* Left Side: Playground controls (5 cols) */}
                <div className="lg:col-span-5 space-y-6">
                  <div className="space-y-2">
                    <label className="text-xs font-extrabold text-neutral-charcoal uppercase tracking-wider block">Customer Search Query</label>
                    <input 
                      type="text"
                      value={playgroundQuery}
                      onChange={(e) => setPlaygroundQuery(e.target.value)}
                      className="w-full px-4 py-3 bg-white border border-neutral-lightgray rounded-xl text-sm font-semibold text-neutral-charcoal focus:outline-none focus:border-brand focus:ring-4 focus:ring-brand/10 transition-all shadow-sm"
                      placeholder="Type a custom shopping query..."
                    />
                  </div>

                  <div className="space-y-3">
                    <span className="text-xs font-extrabold text-neutral-mediumgray uppercase tracking-wider block">Query presets:</span>
                    <div className="space-y-2">
                      {(Object.keys(PRESET_QUERIES) as Array<keyof typeof PRESET_QUERIES>).map((key) => {
                        const q = PRESET_QUERIES[key];
                        return (
                          <button
                            key={key}
                            onClick={() => {
                              setPlaygroundQuery(q);
                            }}
                            className={`w-full text-left px-4.5 py-3.5 rounded-xl border text-xs font-bold transition-all flex items-center justify-between ${
                              playgroundQuery === q 
                                ? 'border-brand bg-brand/5 text-brand shadow-sm' 
                                : 'border-neutral-lightgray/70 bg-white hover:bg-neutral-lightgray/20 text-neutral-darkgray'
                            }`}
                          >
                            <span>"{q}"</span>
                            <ArrowRight className="w-3.5 h-3.5" />
                          </button>
                        );
                      })}
                    </div>
                  </div>
                </div>

                {/* Right Side: AI Ingestion Output (7 cols) */}
                <div className="lg:col-span-7 bg-white rounded-2xl border border-neutral-lightgray/80 p-6 space-y-6">
                  
                  {/* Parsing constraints block */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-neutral-charcoal uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-brand animate-pulse" /> AI Intent Classification
                    </h4>
                    
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Category</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          {DEMO_PRODUCTS[playgroundQuery]?.detected.category || "General"}
                        </div>
                      </div>
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Color</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          {DEMO_PRODUCTS[playgroundQuery]?.detected.color || "Any"}
                        </div>
                      </div>
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Intent</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          {DEMO_PRODUCTS[playgroundQuery]?.detected.intent || "General search"}
                        </div>
                      </div>
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Budget Constraint</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          {DEMO_PRODUCTS[playgroundQuery]?.detected.budget || "None"}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Matching products grid block */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-neutral-charcoal uppercase tracking-wider flex items-center gap-1.5">
                      <Layers className="w-4 h-4 text-brand" /> Matching Catalog Products
                    </h4>

                    {DEMO_PRODUCTS[playgroundQuery] ? (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        {DEMO_PRODUCTS[playgroundQuery].products.map((prod, index) => (
                          <div key={index} className="border border-neutral-lightgray/80 rounded-xl p-4 bg-neutral-background/30 flex flex-col justify-between">
                            <div>
                              <div className="text-2xl mb-2">{prod.image}</div>
                              <h5 className="font-bold text-xs text-neutral-charcoal line-clamp-1">{prod.title}</h5>
                              <div className="flex flex-wrap gap-1 mt-2">
                                {prod.tags.map((tag) => (
                                  <span key={tag} className="text-[9px] px-1.5 py-0.5 rounded bg-white border border-neutral-lightgray text-neutral-mediumgray font-semibold">
                                    {tag}
                                  </span>
                                ))}
                              </div>
                            </div>
                            <div className="mt-4 pt-3 border-t border-neutral-lightgray flex items-center justify-between">
                              <span className="text-xs font-black text-neutral-charcoal">{prod.price}</span>
                              <span className="text-[9px] font-bold text-brand uppercase tracking-wider">{prod.matchScore}</span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-10 bg-neutral-background border border-dashed border-neutral-lightgray rounded-xl">
                        <p className="text-xs text-neutral-mediumgray font-semibold">Type one of the preset search terms to see products</p>
                      </div>
                    )}
                  </div>

                </div>

              </div>
            </div>

          </div>
        </section>

        {/* Section 6: Merchant Dashboard Preview */}
        <section id="dashboard" className="py-24 px-6 md:px-8 bg-neutral-background border-t border-neutral-lightgray">
          <div className="max-w-6xl mx-auto space-y-16">
            
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Dashboard Console</span>
              <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                Designed for absolute clarity
              </h2>
              <p className="text-base md:text-lg text-neutral-mediumgray font-medium leading-relaxed max-w-2xl mx-auto">
                Manage catalogs, review queries, check widget performance settings, and watch your conversion metrics increase inside the Velt Console.
              </p>
            </div>

            {/* Dashboard Mockup Grid */}
            <div className="bg-white rounded-3xl border border-neutral-lightgray/80 shadow-md p-6 md:p-8 space-y-8">
              
              {/* Header inside mockup */}
              <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 pb-6 border-b border-neutral-lightgray">
                <div>
                  <h3 className="font-extrabold text-neutral-charcoal text-lg">Gems & Ornaments Dashboard</h3>
                  <p className="text-xs text-neutral-mediumgray mt-0.5">Semantic Search Ingestion and Analytics Console</p>
                </div>
                <div className="flex items-center gap-2 px-3 py-1.5 bg-green-50 border border-green-200 rounded-lg text-green-700 text-xs font-bold">
                  <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></span>
                  Catalog Synced 12m ago
                </div>
              </div>

              {/* Stats metric columns inside mockup */}
              <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
                <div className="bg-neutral-background border border-neutral-lightgray/60 p-4.5 rounded-2xl">
                  <div className="text-[10px] font-extrabold text-neutral-mediumgray uppercase">Products Indexed</div>
                  <div className="text-xl font-black text-neutral-charcoal mt-1">8,429</div>
                  <span className="text-[9px] font-bold text-brand mt-1 block">100% of Catalog</span>
                </div>
                <div className="bg-neutral-background border border-neutral-lightgray/60 p-4.5 rounded-2xl">
                  <div className="text-[10px] font-extrabold text-neutral-mediumgray uppercase">Avg Search Latency</div>
                  <div className="text-xl font-black text-neutral-charcoal mt-1">24ms</div>
                  <span className="text-[9px] font-bold text-green-600 mt-1 block">Sub-30ms guarantee</span>
                </div>
                <div className="bg-neutral-background border border-neutral-lightgray/60 p-4.5 rounded-2xl">
                  <div className="text-[10px] font-extrabold text-neutral-mediumgray uppercase">Zero-Result Queries</div>
                  <div className="text-xl font-black text-neutral-charcoal mt-1">0.8%</div>
                  <span className="text-[9px] font-bold text-green-600 mt-1 block">↓ 92% decrease</span>
                </div>
                <div className="bg-neutral-background border border-neutral-lightgray/60 p-4.5 rounded-2xl">
                  <div className="text-[10px] font-extrabold text-neutral-mediumgray uppercase">Conversion Increase</div>
                  <div className="text-xl font-black text-neutral-charcoal mt-1">+22.4%</div>
                  <span className="text-[9px] font-bold text-green-600 mt-1 block">↑ 4.1% this week</span>
                </div>
                <div className="bg-neutral-background border border-neutral-lightgray/60 p-4.5 rounded-2xl col-span-2 lg:col-span-1">
                  <div className="text-[10px] font-extrabold text-neutral-mediumgray uppercase">Active Ingestion Sync</div>
                  <div className="text-xl font-black text-neutral-charcoal mt-1">Auto</div>
                  <span className="text-[9px] font-bold text-neutral-mediumgray mt-1 block">Every 24 Hours</span>
                </div>
              </div>

              {/* Simulated chart log overlay */}
              <div className="border border-neutral-lightgray/80 rounded-2xl p-4.5 md:p-6 bg-neutral-background/30 space-y-4">
                <div className="flex justify-between items-center text-xs font-bold text-neutral-charcoal border-b border-neutral-lightgray pb-3">
                  <span>Recent Successful Semantic Searches</span>
                  <span className="text-brand font-semibold hover:underline cursor-pointer">View full logs</span>
                </div>

                <div className="space-y-2 text-xs">
                  <div className="flex justify-between items-center bg-white border border-neutral-lightgray/70 p-3 rounded-xl">
                    <span className="font-semibold text-neutral-darkgray">"heavy metal gold ring size 7"</span>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-bold text-brand uppercase">Cosine Sim: 0.94</span>
                      <span className="font-bold text-green-600">✓ Clicked</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center bg-white border border-neutral-lightgray/70 p-3 rounded-xl">
                    <span className="font-semibold text-neutral-darkgray">"waterproof boots for snow hiking"</span>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-bold text-brand uppercase">Cosine Sim: 0.89</span>
                      <span className="font-bold text-green-600">✓ Clicked</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>

          </div>
        </section>

        {/* Section 7: Pricing Section */}
        <section id="pricing" className="py-24 px-6 md:px-8 bg-white border-t border-neutral-lightgray">
          <div className="max-w-6xl mx-auto space-y-16">
            
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Pricing Tiers</span>
              <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                Simple, predictable pricing
              </h2>
              <p className="text-base md:text-lg text-neutral-mediumgray font-medium leading-relaxed max-w-2xl mx-auto">
                Choose the pricing structure that fits your scale. Free to start, cancel at any time.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              
              {/* Card 1: Starter */}
              <div className="border border-neutral-lightgray/80 rounded-3xl p-8 bg-neutral-background/30 flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-neutral-charcoal text-lg">Starter</h3>
                  <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">For testing and personal store projects.</p>
                  
                  <div className="my-8">
                    <span className="text-4xl font-black text-neutral-charcoal">$0</span>
                    <span className="text-xs text-neutral-mediumgray font-semibold"> / month</span>
                  </div>

                  <ul className="space-y-4 text-xs font-semibold text-neutral-darkgray">
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> 1 Catalog Connection</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Up to 10,000 Products</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Standard search widget</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Basic analytics panel</li>
                  </ul>
                </div>

                <button 
                  onClick={handleLaunchApp}
                  className="w-full bg-white hover:bg-neutral-lightgray/40 border border-neutral-lightgray/80 py-3 rounded-xl text-sm font-bold text-neutral-charcoal mt-10 transition-all active:scale-95"
                >
                  Start Building Free
                </button>
              </div>

              {/* Card 2: Professional (Highlighted) */}
              <div className="border-2 border-brand rounded-3xl p-8 bg-white flex flex-col justify-between shadow-xl shadow-brand/5 relative overflow-hidden">
                <div className="absolute top-4 right-4 bg-brand text-white text-[9px] font-bold px-3 py-1 rounded-full uppercase tracking-wider">Recommended</div>
                
                <div>
                  <h3 className="font-bold text-neutral-charcoal text-lg">Professional</h3>
                  <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">For growing brands and e-commerce stores.</p>
                  
                  <div className="my-8">
                    <span className="text-4xl font-black text-neutral-charcoal">$29</span>
                    <span className="text-xs text-neutral-mediumgray font-semibold"> / month</span>
                  </div>

                  <ul className="space-y-4 text-xs font-semibold text-neutral-darkgray">
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Unlimited Store Catalogs</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Up to 100,000 Products</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Custom CSS widget settings</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Advanced search query analytics</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Priority indexing speeds</li>
                  </ul>
                </div>

                <button 
                  onClick={handleLaunchApp}
                  className="w-full bg-brand hover:bg-brand-dark py-3 rounded-xl text-sm font-bold text-white mt-10 transition-all active:scale-95 shadow-md shadow-brand/10"
                >
                  Upgrade to Pro
                </button>
              </div>

              {/* Card 3: Enterprise */}
              <div className="border border-neutral-lightgray/80 rounded-3xl p-8 bg-neutral-background/30 flex flex-col justify-between">
                <div>
                  <h3 className="font-bold text-neutral-charcoal text-lg">Enterprise</h3>
                  <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">For large merchants with high query loads.</p>
                  
                  <div className="my-8">
                    <span className="text-4xl font-black text-neutral-charcoal">Custom</span>
                    <span className="text-xs text-neutral-mediumgray font-semibold"> pricing</span>
                  </div>

                  <ul className="space-y-4 text-xs font-semibold text-neutral-darkgray">
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Custom Product limits</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Dedicated vector DB cluster</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Custom ML synonym tuning</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> Dedicated support manager</li>
                    <li className="flex items-center gap-2"><Check className="w-4 h-4 text-brand" /> 99.9% API uptime SLA</li>
                  </ul>
                </div>

                <a 
                  href="mailto:support@velt.ai"
                  className="w-full bg-white hover:bg-neutral-lightgray/40 border border-neutral-lightgray/80 py-3 rounded-xl text-sm font-bold text-neutral-charcoal mt-10 transition-all active:scale-95 text-center"
                >
                  Contact Sales
                </a>
              </div>

            </div>

          </div>
        </section>

        {/* Section 8: FAQ Accordion */}
        <section id="faq" className="py-24 px-6 md:px-8 bg-neutral-background border-t border-neutral-lightgray">
          <div className="max-w-4xl mx-auto space-y-16">
            
            <div className="text-center space-y-4 max-w-3xl mx-auto">
              <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Frequently Asked Questions</span>
              <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                Any questions?
              </h2>
            </div>

            <div className="space-y-3 bg-white border border-neutral-lightgray/80 rounded-3xl p-6 md:p-8">
              {faqs.map((faq, index) => {
                const isOpen = openFaq === index;
                return (
                  <div 
                    key={index} 
                    className={`border-b border-neutral-lightgray last:border-0 pb-4.5 pt-4.5 first:pt-0 last:pb-0`}
                  >
                    <button
                      onClick={() => handleFaqToggle(index)}
                      className="flex justify-between items-center w-full text-left font-bold text-base text-neutral-charcoal hover:text-brand transition-colors focus:outline-none"
                    >
                      <span>{faq.q}</span>
                      {isOpen ? (
                        <ChevronUp className="w-5 h-5 text-neutral-mediumgray" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-neutral-mediumgray" />
                      )}
                    </button>
                    
                    <div 
                      className={`overflow-hidden transition-all duration-300 ease-in-out ${
                        isOpen ? 'max-h-[250px] mt-3 opacity-100' : 'max-h-0 opacity-0'
                      }`}
                    >
                      <p className="text-sm text-neutral-mediumgray leading-relaxed font-semibold">
                        {faq.a}
                      </p>
                    </div>
                  </div>
                );
              })}
            </div>

          </div>
        </section>

        {/* Section 9: Final CTA Banner */}
        <section 
          ref={ctaRef}
          className="relative py-28 px-6 md:px-8 bg-neutral-charcoal overflow-hidden flex flex-col items-center justify-center min-h-[50vh] text-center"
        >
          {/* Reactive Gradient glow overlay */}
          <div className="absolute inset-0 cta-dynamic-gradient -z-10"></div>
          
          <h2 className="font-sans text-4xl md:text-[56px] font-extrabold leading-tight text-white mb-6 drop-shadow-sm max-w-3xl">
            Upgrade your store search relevance today
          </h2>
          <p className="text-base md:text-lg text-white/80 max-w-xl mb-10 font-medium">
            Connect catalogs, generate high-accuracy vector mappings, and go live instantly.
          </p>

          <button 
            onClick={handleLaunchApp}
            className="inline-flex items-center gap-3 bg-white hover:bg-white/95 hover:scale-103 text-brand font-bold text-base px-8 py-4 rounded-full transition-all active:scale-97 shadow-lg shadow-brand-dark/20"
          >
            Start Building Free
            <ArrowRight className="w-4 h-4 text-brand" />
          </button>
        </section>

      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-neutral-lightgray py-16 text-neutral-mediumgray">
        <div className="max-w-7xl mx-auto px-6 md:px-8">
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8 pb-12 border-b border-neutral-lightgray">
            
            {/* Brand column */}
            <div className="col-span-2 space-y-4">
              <Link className="font-sans text-xl font-bold tracking-tighter text-brand flex items-center gap-2" to="/">
                <svg className="h-6 w-6 animate-pulse shrink-0 grayscale opacity-75" fill="none" viewBox="0 0 48 46" xmlns="http://www.w3.org/2000/svg">
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
                </svg>
                <span className="text-lg font-extrabold text-neutral-charcoal">Velt</span>
              </Link>
              <p className="text-xs font-semibold text-neutral-mediumgray max-w-sm leading-relaxed">
                The AI-powered semantic search infrastructure for modern storefronts. Connect your catalog and deploy under 30ms latency vector indexes instantly.
              </p>
            </div>

            {/* Product links */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Product</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li><a className="hover:text-brand" href="#product">Relevance Engine</a></li>
                <li><a className="hover:text-brand" href="#demo">Vector Database</a></li>
                <li><a className="hover:text-brand" href="#dashboard">Client Overlay Widget</a></li>
                <li><a className="hover:text-brand" href="#pricing">Pricing Plans</a></li>
              </ul>
            </div>

            {/* Solutions links */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Solutions</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li><a className="hover:text-brand" href="#">Shopify Stores</a></li>
                <li><a className="hover:text-brand" href="#">WooCommerce Integration</a></li>
                <li><a className="hover:text-brand" href="#">Custom Commerce API</a></li>
                <li><a className="hover:text-brand" href="#">B2B Catalog search</a></li>
              </ul>
            </div>

            {/* Developers links */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Developers</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li><a className="hover:text-brand flex items-center gap-1" href={getApiDocsUrl()} target="_blank" rel="noreferrer">API Documentation <ExternalLink className="w-3 h-3" /></a></li>
                <li><a className="hover:text-brand" href="#">Embed Code Snippet</a></li>
                <li><a className="hover:text-brand" href="#">Uptime Status</a></li>
                <li><a className="hover:text-brand" href="#">GitHub Repository</a></li>
              </ul>
            </div>

            {/* Resources links */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Resources</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li><a className="hover:text-brand" href="#">E-Commerce Benchmarks</a></li>
                <li><a className="hover:text-brand" href="#">Vector Embeddings 101</a></li>
                <li><a className="hover:text-brand" href="#">Privacy Policy</a></li>
                <li><a className="hover:text-brand" href="#">Terms of Service</a></li>
              </ul>
            </div>

          </div>

          <div className="pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-semibold">
            <span>&copy; {new Date().getFullYear()} Velt AI. Built for instant product discovery.</span>
            <div className="flex gap-4">
              <a className="hover:text-brand" href="#">Twitter</a>
              <a className="hover:text-brand" href="#">GitHub</a>
              <a className="hover:text-brand" href="#">Discord</a>
            </div>
          </div>
        </div>
      </footer>

    </div>
  );
};
