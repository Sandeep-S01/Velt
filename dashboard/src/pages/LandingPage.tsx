import React, { useEffect, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';
import { api, getApiDocsUrl, WIDGET_SCRIPT_URL } from '../lib/api';
import { VeltLogo } from '../components/VeltLogo';
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

interface LiveDemoResponse {
  query: string;
  applied_filters: {
    price_min?: number;
    price_max?: number;
    in_stock?: boolean;
  };
  products: Array<{
    id: string;
    title: string;
    description: string;
    price: number;
    category: string;
    score: number;
  }>;
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
  const [liveDemo, setLiveDemo] = useState<LiveDemoResponse | null>(null);
  const [demoLoading, setDemoLoading] = useState(false);
  const [demoError, setDemoError] = useState<string | null>(null);

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

  useEffect(() => {
    const query = playgroundQuery.trim();
    if (query.length < 2) {
      setLiveDemo(null);
      setDemoError(null);
      return;
    }

    const controller = new AbortController();
    const timer = window.setTimeout(async () => {
      setDemoLoading(true);
      setDemoError(null);
      try {
        const result = await api.post<LiveDemoResponse>(
          '/demo/search',
          { query, limit: 3 },
          { signal: controller.signal },
        );
        setLiveDemo(result);
      } catch (err: any) {
        if (err?.name !== 'AbortError') {
          setLiveDemo(null);
          setDemoError(err?.message || 'The live demo is temporarily unavailable.');
        }
      } finally {
        if (!controller.signal.aborted) setDemoLoading(false);
      }
    }, 350);

    return () => {
      window.clearTimeout(timer);
      controller.abort();
    };
  }, [playgroundQuery]);

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
      a: "Velt generates vector representations of product titles, descriptions, and categories. It compares each shopper query with those vectors, then combines semantic similarity with catalog filters and product data. Query latency is recorded for each search and varies with the catalog, model, and deployment."
    },
    {
      q: "Can I integrate with Shopify?",
      a: "Yes. Connect a Shopify store through its authorization flow, then sync the catalog from the Velt dashboard. You can also ingest products through the API or upload a CSV or JSON catalog file."
    },
    {
      q: "Do I need machine learning knowledge?",
      a: "No machine learning knowledge is required. Velt provides a managed vector-search pipeline, widget settings builder, and analytics console."
    },
    {
      q: "How fast can I deploy Velt?",
      a: "After your catalog finishes syncing, you can configure the widget in the dashboard and add its script tag to your storefront. Setup time depends on your catalog size and commerce platform."
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
            <VeltLogo className="h-8 w-8 shrink-0" animated />
            <span className="text-xl font-extrabold tracking-tighter text-neutral-charcoal">Velt</span>
          </Link>

          {/* Desktop Navigation Links */}
          <div className="hidden lg:flex items-center gap-8">
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#product">Product</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#features">Features</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#demo">Interactive Demo</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#dashboard">Dashboard</a>
            <a className="text-sm font-semibold text-neutral-darkgray hover:text-brand transition-colors" href="#access">Beta Access</a>
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
              <a onClick={() => setMobileMenuOpen(false)} className="text-base font-semibold text-neutral-darkgray hover:text-brand" href="#access">Beta Access</a>
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
                  <span className="text-[10px] font-bold text-brand-dark uppercase tracking-wider bg-brand/10 px-2 py-0.5 rounded">Active</span>
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
                      Shopify, CSV, JSON, or custom API integrations.
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
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-brand/5 border border-brand/20 text-brand">Semantic Similarity</span>
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
                    <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-neutral-background border border-neutral-lightgray text-neutral-darkgray">Measured latency</span>
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
                    <span className="text-[10px] font-bold text-neutral-darkgray uppercase tracking-wider bg-neutral-lightgray px-2 py-0.5 rounded">Legacy</span>
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
                Enter any shopper request. This calls the same semantic engine used by storefront search and applies supported price and stock constraints.
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
                  
                  {/* Live query interpretation */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-neutral-charcoal uppercase tracking-wider flex items-center gap-1.5">
                      <Sparkles className="w-4 h-4 text-brand animate-pulse" /> Live Query Execution
                    </h4>
                    
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Search mode</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          Semantic
                        </div>
                      </div>
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Minimum price</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          {liveDemo?.applied_filters.price_min !== undefined
                            ? `$${liveDemo.applied_filters.price_min}`
                            : 'Any'}
                        </div>
                      </div>
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Maximum price</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          {liveDemo?.applied_filters.price_max !== undefined
                            ? `$${liveDemo.applied_filters.price_max}`
                            : 'Any'}
                        </div>
                      </div>
                      <div className="bg-neutral-background border border-neutral-lightgray p-3 rounded-xl text-center">
                        <div className="text-[10px] font-bold text-neutral-mediumgray uppercase">Results</div>
                        <div className="text-xs font-black text-neutral-charcoal mt-1">
                          {demoLoading ? 'Searching…' : (liveDemo?.products.length ?? 0)}
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Matching products grid block */}
                  <div className="space-y-3">
                    <h4 className="text-xs font-bold text-neutral-charcoal uppercase tracking-wider flex items-center gap-1.5">
                      <Layers className="w-4 h-4 text-brand" /> Matching Catalog Products
                    </h4>

                    {demoLoading && !liveDemo ? (
                      <div className="text-center py-10 bg-neutral-background border border-neutral-lightgray rounded-xl">
                        <p className="text-xs text-neutral-mediumgray font-semibold">Running a live semantic search…</p>
                      </div>
                    ) : demoError ? (
                      <div className="text-center py-10 bg-red-50 border border-red-100 rounded-xl">
                        <p className="text-xs text-red-700 font-semibold">{demoError}</p>
                      </div>
                    ) : liveDemo && liveDemo.products.length > 0 ? (
                      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                        {liveDemo.products.map((prod) => (
                          <div key={prod.id} className="border border-neutral-lightgray/80 rounded-xl p-4 bg-neutral-background/30 flex flex-col justify-between">
                            <div>
                              <div className="w-8 h-8 mb-2 rounded-lg bg-brand/10 text-brand flex items-center justify-center text-sm font-black">
                                {prod.title.charAt(0)}
                              </div>
                              <h5 className="font-bold text-xs text-neutral-charcoal line-clamp-1">{prod.title}</h5>
                              <div className="flex flex-wrap gap-1 mt-2">
                                <span className="text-[9px] px-1.5 py-0.5 rounded bg-white border border-neutral-lightgray text-neutral-mediumgray font-semibold">
                                  {prod.category}
                                </span>
                              </div>
                            </div>
                            <div className="mt-4 pt-3 border-t border-neutral-lightgray flex items-center justify-between">
                              <span className="text-xs font-black text-neutral-charcoal">${prod.price.toFixed(2)}</span>
                              <span className="text-[9px] font-bold text-brand uppercase tracking-wider">
                                {Math.max(0, Math.min(100, Math.round(prod.score * 100)))}% match
                              </span>
                            </div>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <div className="text-center py-10 bg-neutral-background border border-dashed border-neutral-lightgray rounded-xl">
                        <p className="text-xs text-neutral-mediumgray font-semibold">No products matched this request and its constraints.</p>
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
                Manage catalogs, review queries, configure the widget, and measure search engagement inside the Velt Console.
              </p>
            </div>

            {/* Dashboard Mockup Grid */}
            <div className="bg-white rounded-3xl border border-neutral-lightgray/80 shadow-md p-6 md:p-8 space-y-8">
              
              {/* Header inside mockup */}
              <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4 pb-6 border-b border-neutral-lightgray">
                <div>
                  <h3 className="font-extrabold text-neutral-charcoal text-lg">Example merchant dashboard</h3>
                  <p className="text-xs text-neutral-mediumgray mt-0.5">Illustrative catalog and analytics data</p>
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
                  <span className="text-[9px] font-bold text-neutral-mediumgray mt-1 block">Measured per search</span>
                </div>
                <div className="bg-neutral-background border border-neutral-lightgray/60 p-4.5 rounded-2xl">
                  <div className="text-[10px] font-extrabold text-neutral-mediumgray uppercase">Zero-Result Queries</div>
                  <div className="text-xl font-black text-neutral-charcoal mt-1">0.8%</div>
                  <span className="text-[9px] font-bold text-neutral-mediumgray mt-1 block">Based on recorded searches</span>
                </div>
                <div className="bg-neutral-background border border-neutral-lightgray/60 p-4.5 rounded-2xl">
                  <div className="text-[10px] font-extrabold text-neutral-mediumgray uppercase">Click-Through Rate</div>
                  <div className="text-xl font-black text-neutral-charcoal mt-1">Measured</div>
                  <span className="text-[9px] font-bold text-neutral-mediumgray mt-1 block">From attributed result clicks</span>
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
                      <span className="font-bold text-green-700">✓ Clicked</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center bg-white border border-neutral-lightgray/70 p-3 rounded-xl">
                    <span className="font-semibold text-neutral-darkgray">"waterproof boots for snow hiking"</span>
                    <div className="flex items-center gap-3">
                      <span className="text-[10px] font-bold text-brand uppercase">Cosine Sim: 0.89</span>
                      <span className="font-bold text-green-700">✓ Clicked</span>
                    </div>
                  </div>
                </div>
              </div>

            </div>

          </div>
        </section>

        {/* Section 7: Private beta access */}
        <section id="access" className="py-24 px-6 md:px-8 bg-white border-t border-neutral-lightgray">
          <div className="max-w-4xl mx-auto">
            <div className="border border-brand/20 rounded-3xl p-8 md:p-12 bg-brand/5 text-center space-y-8">
              <div className="space-y-4">
                <span className="text-xs font-extrabold text-brand uppercase tracking-widest">Private Beta</span>
                <h2 className="text-4xl md:text-5xl font-black text-neutral-charcoal tracking-tight">
                  Test Velt with your own catalog
                </h2>
                <p className="text-base md:text-lg text-neutral-darkgray font-medium leading-relaxed max-w-2xl mx-auto">
                  Velt is currently offered as a private beta. Pricing, catalog limits, and service commitments will be published after production usage and reliability are measured.
                </p>
              </div>

              <ul className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left text-sm font-semibold text-neutral-darkgray max-w-2xl mx-auto">
                <li className="flex items-start gap-2"><Check className="w-4 h-4 text-brand mt-0.5 shrink-0" /> Shopify, CSV, and JSON catalog ingestion</li>
                <li className="flex items-start gap-2"><Check className="w-4 h-4 text-brand mt-0.5 shrink-0" /> Semantic search with catalog constraints</li>
                <li className="flex items-start gap-2"><Check className="w-4 h-4 text-brand mt-0.5 shrink-0" /> Configurable storefront search widget</li>
                <li className="flex items-start gap-2"><Check className="w-4 h-4 text-brand mt-0.5 shrink-0" /> Query, click, and zero-result analytics</li>
              </ul>

              <button
                onClick={handleLaunchApp}
                className="inline-flex items-center justify-center gap-2 bg-brand hover:bg-brand-dark px-6 py-3 rounded-xl text-sm font-bold text-white transition-all active:scale-95 shadow-md shadow-brand/10"
              >
                Redeem Beta Invite <ArrowRight className="w-4 h-4" />
              </button>
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
            Connect a catalog, let Velt index it, and add semantic product discovery to your storefront.
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
                <VeltLogo className="h-6 w-6 shrink-0 grayscale opacity-75" animated />
                <span className="text-lg font-extrabold text-neutral-charcoal">Velt</span>
              </Link>
              <p className="text-xs font-semibold text-neutral-mediumgray max-w-sm leading-relaxed">
                Semantic search infrastructure for modern storefronts. Connect your catalog, deploy the widget, and measure real search performance.
              </p>
            </div>

            {/* Product links */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Product</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li><a className="hover:text-brand" href="#product">Relevance Engine</a></li>
                <li><a className="hover:text-brand" href="#demo">Vector Database</a></li>
                <li><a className="hover:text-brand" href="#dashboard">Client Overlay Widget</a></li>
                <li><a className="hover:text-brand" href="#access">Beta Access</a></li>
              </ul>
            </div>

            {/* Supported catalog sources */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Catalog Sources</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li>Shopify stores</li>
                <li>CSV uploads</li>
                <li>JSON uploads</li>
                <li>Product API</li>
              </ul>
            </div>

            {/* Developers links */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Developers</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li><a className="hover:text-brand flex items-center gap-1" href={getApiDocsUrl()} target="_blank" rel="noreferrer">API Documentation <ExternalLink className="w-3 h-3" /></a></li>
                <li><Link className="hover:text-brand" to="/stores">Widget setup</Link></li>
                <li><a className="hover:text-brand" href="#demo">Live API demo</a></li>
              </ul>
            </div>

            {/* Policies and support */}
            <div className="space-y-3.5">
              <h4 className="text-xs font-black text-neutral-charcoal uppercase tracking-wider">Policies</h4>
              <ul className="space-y-2 text-xs font-semibold">
                <li><Link className="hover:text-brand" to="/privacy">Privacy Policy</Link></li>
                <li><Link className="hover:text-brand" to="/terms">Terms of Service</Link></li>
                <li><Link className="hover:text-brand" to="/data-retention">Data Retention</Link></li>
                <li><Link className="hover:text-brand" to="/support">Support & Incidents</Link></li>
              </ul>
            </div>

          </div>

          <div className="pt-8 flex flex-col md:flex-row justify-between items-center gap-4 text-xs font-semibold">
            <span>&copy; {new Date().getFullYear()} Velt AI. Built for semantic product discovery.</span>
            <a className="hover:text-brand" href="mailto:support@velt.ai">support@velt.ai</a>
          </div>
        </div>
      </footer>

    </div>
  );
};
