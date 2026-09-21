import React, { useCallback, useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../lib/api';
import { Layout } from '../../components/Layout';
import type { StoreModel } from '../Stores/StoreList';
import { 
  Eye, Sliders, CheckCircle, RefreshCw, AlertCircle, Laptop, 
  ArrowLeft, Sparkles, Sun, Moon, Search, ShoppingCart, Footprints, Smartphone
} from 'lucide-react';

interface WidgetConfig {
  theme: string;
  primary_color: string;
  position: string;
  border_radius: 'sm' | 'md' | 'lg';
  placeholder_text: string;
  show_filters: boolean;
  show_price: boolean;
  show_rating: boolean;
  enable_autocomplete: boolean;
}

interface SearchConfig {
  min_score_threshold: number;
  exclude_out_of_stock: boolean;
}

export const WidgetSettings: React.FC = () => {
  const { storeId } = useParams<{ storeId: string }>();
  
  // States
  const [store, setStore] = useState<StoreModel | null>(null);
  const [stores, setStores] = useState<StoreModel[]>([]);
  const [config, setConfig] = useState<WidgetConfig>({
    theme: 'light',
    primary_color: '#863bff',
    position: 'bottom-right',
    border_radius: 'md',
    placeholder_text: 'Search for products...',
    show_filters: false,
    show_price: true,
    show_rating: false,
    enable_autocomplete: true,
  });
  const [searchConfig, setSearchConfig] = useState<SearchConfig>({
    min_score_threshold: 0.25,
    exclude_out_of_stock: false,
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // UX Extra States for Customizer Preview
  const [previewDevice, setPreviewDevice] = useState<'desktop' | 'mobile'>('desktop');
  const [themePreset, setThemePreset] = useState<'minimal' | 'modern' | 'brand'>('modern');

  const fetchConfig = useCallback(async () => {
    if (!storeId) return;
    try {
      const storeData = await api.get<StoreModel>(`/stores/${storeId}`);
      setStore(storeData);
      
      const stored = storeData.widget_config || {};
      const configData: WidgetConfig = {
        theme: stored.theme === 'dark' ? 'dark' : 'light',
        primary_color: /^#[0-9a-f]{6}$/i.test(stored.primary_color || '')
          ? stored.primary_color!
          : '#4F46E5',
        position: stored.position === 'bottom-left' ? 'bottom-left' : 'bottom-right',
        border_radius: ['sm', 'md', 'lg'].includes(stored.border_radius || '')
          ? stored.border_radius!
          : 'md',
        placeholder_text: String(stored.placeholder_text || 'Search for products...').slice(0, 100),
        show_filters: false,
        show_price: stored.show_price !== false,
        show_rating: false,
        enable_autocomplete: stored.enable_autocomplete !== false,
      };
      setConfig(configData);
      setSearchConfig({
        min_score_threshold: Math.max(
          0,
          Math.min(1, Number(storeData.search_config?.min_score_threshold ?? 0.25)),
        ),
        exclude_out_of_stock: storeData.search_config?.exclude_out_of_stock === true,
      });
      
      // Attempt to auto-resolve border radius and theme presets based on fetched values
      if (configData.primary_color === '#863bff') {
        setThemePreset('brand');
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load configuration');
    } finally {
      setLoading(false);
    }
  }, [storeId]);

  const fetchStores = useCallback(async () => {
    try {
      const data = await api.get<StoreModel[]>('/stores/');
      setStores(data);
    } catch (err) {
      console.error('Failed to load stores list', err);
    }
  }, []);

  useEffect(() => {
    if (storeId) {
      fetchConfig();
      fetchStores();
    }
  }, [fetchConfig, fetchStores, storeId]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!storeId) return;

    setSaving(true);
    setSuccess(false);
    setError(null);

    try {
      // Save configuration by updating the Store model's widget_config JSON field
      await api.put(`/stores/${storeId}`, {
        widget_config: config,
        search_config: searchConfig,
      });
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      setError(err.message || 'Failed to save configuration');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <Layout stores={stores} selectedStoreId={storeId}>
        <div className="flex flex-col items-center justify-center py-32 space-y-4">
          <RefreshCw className="w-8 h-8 animate-spin text-brand" />
          <h2 className="text-sm font-semibold text-neutral-mediumgray">Loading config console...</h2>
        </div>
      </Layout>
    );
  }

  // Border Radius mapper
  const getRadiusClass = () => {
    if (config.border_radius === 'sm') return 'rounded-md';
    if (config.border_radius === 'lg') return 'rounded-2xl';
    return 'rounded-xl';
  };

  return (
    <Layout stores={stores} selectedStoreId={store?.id}>
      <div className="max-w-6xl mx-auto space-y-8 pb-16">
        
        {/* Header Hero */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Link to={`/stores/${store?.id}`} className="text-neutral-mediumgray hover:text-neutral-charcoal transition-all">
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <span className="text-[10px] text-neutral-mediumgray uppercase font-bold tracking-wider">
                Store Customizer Studio
              </span>
            </div>
            <h1 className="text-2xl font-black text-neutral-charcoal tracking-tight">Widget Builder</h1>
            <p className="text-xs text-neutral-mediumgray">Design, brand, and preview custom floating search overlays live.</p>
          </div>
        </div>

        {/* Double-Pane Split Customizer Frame */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          
          {/* Left Configuration Panel */}
          <form onSubmit={handleSave} className="lg:col-span-5 bg-white rounded-2xl border border-slate-200/80 p-4 sm:p-6 shadow-sm space-y-6">
            <div className="flex items-center gap-2 border-b border-slate-100 pb-4">
              <Sliders className="w-4 h-4 text-brand" />
              <h2 className="text-sm font-bold text-neutral-charcoal">Widget Configuration Options</h2>
            </div>

            <div className="space-y-5">
              
              {/* Theme Selection */}
              <div className="space-y-2">
                <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                  Interface Mode
                </label>
                <div className="grid grid-cols-2 gap-4">
                  <button
                    type="button"
                    onClick={() => setConfig({ ...config, theme: 'light' })}
                    className={`min-h-11 px-3 py-2.5 rounded-xl border text-xs font-bold transition-all inline-flex items-center justify-center gap-2 ${
                      config.theme === 'light'
                        ? 'border-brand bg-brand/5 text-brand shadow-sm shadow-brand/5'
                        : 'border-slate-200 hover:border-slate-350 bg-slate-50/50 text-neutral-darkgray'
                    }`}
                  >
                    <Sun className="h-4 w-4" aria-hidden="true" />
                    <span>Light UI</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setConfig({ ...config, theme: 'dark' })}
                    className={`min-h-11 px-3 py-2.5 rounded-xl border text-xs font-bold transition-all inline-flex items-center justify-center gap-2 ${
                      config.theme === 'dark'
                        ? 'border-brand bg-brand/5 text-brand shadow-sm shadow-brand/5'
                        : 'border-slate-200 hover:border-slate-350 bg-slate-50/50 text-neutral-darkgray'
                    }`}
                  >
                    <Moon className="h-4 w-4" aria-hidden="true" />
                    <span>Dark UI</span>
                  </button>
                </div>
              </div>

              {/* Theme Presets */}
              <div className="space-y-2">
                <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                  Styling Theme Preset
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['minimal', 'modern', 'brand'] as const).map((preset) => (
                    <button
                      key={preset}
                      type="button"
                      onClick={() => {
                        setThemePreset(preset);
                        if (preset === 'brand') {
                          setConfig({ ...config, primary_color: '#863bff' });
                        } else if (preset === 'minimal') {
                          setConfig({ ...config, primary_color: '#18181b' });
                        } else {
                          setConfig({ ...config, primary_color: '#4f46e5' });
                        }
                      }}
                      className={`px-2 py-2 rounded-lg border text-[11px] font-semibold text-center transition-all capitalize ${
                        themePreset === preset
                          ? 'border-slate-800 bg-slate-50 text-slate-900 font-bold'
                          : 'border-slate-200 hover:border-slate-300 text-slate-500'
                      }`}
                    >
                      {preset}
                    </button>
                  ))}
                </div>
              </div>

              {/* Accent Color */}
              <div className="space-y-2">
                <div className="flex justify-between items-center">
                  <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                    Accent Color
                  </label>
                  <span className="font-mono text-[10px] font-bold text-neutral-mediumgray">{config.primary_color}</span>
                </div>
                <div className="flex gap-3">
                  <input
                    type="color"
                    value={config.primary_color}
                    onChange={(e) => setConfig({ ...config, primary_color: e.target.value })}
                    className="w-10 h-10 p-0 border border-slate-200 rounded-xl cursor-pointer shrink-0"
                  />
                  <input
                    type="text"
                    value={config.primary_color}
                    onChange={(e) => setConfig({ ...config, primary_color: e.target.value })}
                    placeholder="#863BFF"
                    className="flex-1 px-3 py-2 bg-slate-50 border border-slate-200 hover:border-slate-350 focus:border-brand rounded-xl text-xs text-neutral-charcoal focus:outline-none transition-all font-semibold"
                  />
                </div>
              </div>

              {/* Corner Roundness */}
              <div className="space-y-2">
                <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                  Corner Roundness (Border Radius)
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {(['sm', 'md', 'lg'] as const).map((r) => (
                    <button
                      key={r}
                      type="button"
                      onClick={() => setConfig({ ...config, border_radius: r })}
                      className={`px-2 py-2 rounded-lg border text-[11px] font-semibold text-center transition-all uppercase ${
                        config.border_radius === r
                          ? 'border-slate-800 bg-slate-50 text-slate-900 font-bold'
                          : 'border-slate-200 hover:border-slate-300 text-slate-500'
                      }`}
                    >
                      {r === 'sm' ? 'Sharp' : r === 'md' ? 'Rounded' : 'Curved'}
                    </button>
                  ))}
                </div>
              </div>

              {/* Input Placeholder Text */}
              <div className="space-y-2">
                <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                  Search Placeholder Text
                </label>
                <input
                  type="text"
                  value={config.placeholder_text}
                  onChange={(e) => setConfig({ ...config, placeholder_text: e.target.value })}
                  maxLength={100}
                  placeholder="Search store catalog..."
                  className="block w-full px-3 py-2 bg-slate-50 border border-slate-200 hover:border-slate-350 focus:border-brand rounded-xl text-xs text-neutral-charcoal focus:outline-none transition-all font-semibold"
                />
              </div>

              {/* Floating Widget Position */}
              <div className="space-y-2">
                <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                  Floating Widget Position
                </label>
                <select
                  value={config.position}
                  onChange={(e) => setConfig({ ...config, position: e.target.value })}
                  className="block w-full px-3 py-2 bg-slate-50 border border-slate-200 hover:border-slate-350 focus:border-brand rounded-xl text-xs text-neutral-charcoal focus:outline-none transition-all cursor-pointer font-semibold"
                >
                  <option value="bottom-right">Bottom Right of Screen</option>
                  <option value="bottom-left">Bottom Left of Screen</option>
                </select>
              </div>

              {/* Display Options Flags */}
              <div className="space-y-3 pt-2">
                <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                  Interface Components
                </label>
                
                <div className="space-y-2.5">
                  <label className="flex items-center gap-2.5 cursor-pointer text-xs font-semibold text-neutral-darkgray select-none">
                    <input
                      type="checkbox"
                      checked={config.enable_autocomplete}
                      onChange={(e) => setConfig({ ...config, enable_autocomplete: e.target.checked })}
                      className="w-4 h-4 rounded text-brand focus:ring-brand accent-brand border-slate-300"
                    />
                    <span>Show Autocomplete Search Suggestions</span>
                  </label>

                  <label className="flex items-center gap-2.5 cursor-pointer text-xs font-semibold text-neutral-darkgray select-none">
                    <input
                      type="checkbox"
                      checked={config.show_price}
                      onChange={(e) => setConfig({ ...config, show_price: e.target.checked })}
                      className="w-4 h-4 rounded text-brand focus:ring-brand accent-brand border-slate-300"
                    />
                    <span>Render Product Price Badges</span>
                  </label>

                </div>
              </div>

              <div className="space-y-4 pt-5 border-t border-slate-100">
                <div>
                  <label htmlFor="relevance-threshold" className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                    Minimum Relevance: {Math.round(searchConfig.min_score_threshold * 100)}%
                  </label>
                  <p className="mt-1 text-[10px] leading-relaxed text-slate-500">
                    Results below this semantic match score are omitted. Lower values return more products.
                  </p>
                </div>
                <input
                  id="relevance-threshold"
                  type="range"
                  min="0"
                  max="1"
                  step="0.05"
                  value={searchConfig.min_score_threshold}
                  onChange={(e) => setSearchConfig({
                    ...searchConfig,
                    min_score_threshold: Number(e.target.value),
                  })}
                  className="w-full accent-brand"
                />
                <label className="flex items-start gap-2.5 cursor-pointer text-xs font-semibold text-neutral-darkgray select-none">
                  <input
                    type="checkbox"
                    checked={searchConfig.exclude_out_of_stock}
                    onChange={(e) => setSearchConfig({
                      ...searchConfig,
                      exclude_out_of_stock: e.target.checked,
                    })}
                    className="mt-0.5 w-4 h-4 rounded text-brand focus:ring-brand accent-brand border-slate-300"
                  />
                  <span>
                    Exclude out-of-stock products
                    <span className="block mt-0.5 text-[10px] font-medium text-slate-500">
                      Applies to widget, API, preview, and natural-language searches.
                    </span>
                  </span>
                </label>
              </div>

            </div>

            {/* Response Alerts */}
            {success && (
              <div className="p-3 bg-green-50 border border-green-150 text-green-700 text-xs rounded-xl flex items-center gap-2">
                <CheckCircle className="w-4 h-4 shrink-0 text-green-600" />
                <span>Configuration synced with Velt servers!</span>
              </div>
            )}

            {error && (
              <div className="p-3 bg-red-50 border border-red-150 text-red-700 text-xs rounded-xl flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0 text-red-500" />
                <span>{error}</span>
              </div>
            )}

            {/* Action buttons */}
            <div className="flex items-center justify-end gap-2 pt-4 border-t border-slate-100">
              <button
                type="submit"
                disabled={saving}
                className="px-4 py-2 bg-brand hover:bg-brand-dark text-white font-bold text-xs rounded-xl transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50"
              >
                {saving ? (
                  <>
                    <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Saving...
                  </>
                ) : (
                  'Apply Live Settings'
                )}
              </button>
            </div>
          </form>

          {/* Right Live Mockup Interactive Preview */}
          <div className="lg:col-span-7 min-w-0 bg-white rounded-2xl border border-slate-200/80 p-4 sm:p-6 shadow-sm flex flex-col space-y-6">
            
            {/* Header controls device preview */}
            <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-100 pb-4">
              <div className="flex items-center gap-2">
                <Eye className="w-4 h-4 text-brand" />
                <h3 className="text-sm font-bold text-neutral-charcoal">Interactive Live Preview</h3>
              </div>

              {/* View switchers */}
              <div className="bg-slate-100 p-0.5 rounded-lg flex border border-slate-200/60">
                <button
                  type="button"
                  onClick={() => setPreviewDevice('desktop')}
                  className={`p-1.5 rounded-md transition-all ${
                    previewDevice === 'desktop' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-400 hover:text-slate-700'
                  }`}
                  title="Desktop Preview"
                >
                  <Laptop className="w-4 h-4" />
                </button>
                <button
                  type="button"
                  onClick={() => setPreviewDevice('mobile')}
                  className={`p-1.5 rounded-md transition-all ${
                    previewDevice === 'mobile' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-400 hover:text-slate-700'
                  }`}
                  title="Mobile Preview"
                >
                  <Smartphone className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Dynamic Sized Container Frame */}
            <div className="bg-slate-50 border border-slate-200/80 rounded-2xl p-3 sm:p-6 xl:p-8 flex items-center justify-center min-h-[430px] sm:min-h-[500px] transition-all overflow-hidden">
              
              {/* Outer Viewport Box */}
              <div 
                className={`border bg-white shadow-xl transition-all flex flex-col justify-between overflow-hidden ${
                  previewDevice === 'mobile' 
                    ? 'w-full max-w-[320px] h-[450px] rounded-2xl'
                    : 'w-full max-w-lg h-[400px] rounded-xl'
                } ${
                  config.theme === 'dark' ? 'bg-slate-950 border-slate-850 text-slate-200' : 'bg-white border-slate-200 text-neutral-charcoal'
                }`}
              >
                
                {/* Simulated Shop Header */}
                <div className={`h-12 border-b px-4 flex items-center justify-between text-xs font-bold shrink-0 ${
                  config.theme === 'dark' ? 'bg-slate-900 border-slate-800 text-slate-200' : 'bg-slate-50 border-slate-100 text-slate-800'
                }`}>
                  <div className="flex items-center gap-2">
                    <span className="w-2.5 h-2.5 rounded-full bg-slate-300"></span>
                    <span>Merchant Storefront</span>
                  </div>
                  <div className="flex items-center gap-3 text-neutral-mediumgray" aria-label="Storefront actions">
                    <Search className="h-4 w-4" aria-hidden="true" />
                    <ShoppingCart className="h-4 w-4" aria-hidden="true" />
                  </div>
                </div>

                {/* Simulated Widget Content panel */}
                <div className={`p-4 sm:p-5 flex-1 space-y-4 flex flex-col overflow-y-auto justify-start ${
                  config.theme === 'dark' ? 'scrollbar-dark' : 'scrollbar-light'
                }`}>
                  
                  {/* Custom Search Box */}
                  <div 
                    className={`border px-3 py-2 flex items-center gap-2 shadow-sm ${getRadiusClass()} ${
                      config.theme === 'dark' ? 'bg-slate-900/40 border-slate-800' : 'bg-white border-slate-200/80'
                    }`}
                    style={{ borderLeftWidth: '3px', borderLeftColor: config.primary_color }}
                  >
                    <Search className="h-4 w-4 shrink-0 text-neutral-mediumgray" aria-hidden="true" />
                    <span className="text-xs text-neutral-mediumgray font-semibold italic">{config.placeholder_text}</span>
                  </div>

                  {/* Autocomplete Suggestion tags mockup */}
                  {config.enable_autocomplete && (
                    <div className={`border p-3 space-y-2 shadow-sm ${getRadiusClass()} ${
                      config.theme === 'dark' ? 'bg-slate-900/60 border-slate-800 text-slate-300' : 'bg-slate-50 border-slate-150 text-slate-600'
                    }`}>
                      <div className="font-extrabold text-[9px] uppercase tracking-wider text-neutral-mediumgray">Matched Autocomplete Intent</div>
                      
                      <div className="flex flex-wrap gap-1.5 pt-0.5">
                        <span 
                          className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-white border border-slate-200/80 shadow-sm"
                          style={{ borderLeft: `2.5px solid ${config.primary_color}` }}
                        >
                          Category: Shoes
                        </span>
                        <span 
                          className="inline-flex items-center gap-1 text-[10px] font-bold px-2 py-0.5 rounded-full bg-white border border-slate-200/80 shadow-sm"
                          style={{ borderLeft: `2.5px solid ${config.primary_color}` }}
                        >
                          Intent: Travel
                        </span>
                      </div>
                    </div>
                  )}

                  {/* Mock search product card */}
                  <div className={`border p-3.5 flex gap-3.5 items-center shadow-sm ${getRadiusClass()} ${
                    config.theme === 'dark' ? 'bg-slate-900/40 border-slate-800' : 'bg-white border-slate-200/80'
                  }`}>
                    <div className={`w-12 h-12 rounded-lg border flex items-center justify-center shrink-0 ${
                      config.theme === 'dark'
                        ? 'bg-slate-800 border-slate-700 text-slate-300'
                        : 'bg-slate-100 border-slate-200/60 text-slate-500'
                    }`}>
                      <Footprints className="h-5 w-5" aria-hidden="true" />
                    </div>
                    <div className="space-y-1 overflow-hidden flex-1">
                      <div className={`font-bold text-xs truncate ${config.theme === 'dark' ? 'text-white' : 'text-neutral-charcoal'}`}>
                        Pro-Run Orthotic Sneakers
                      </div>
                      
                      <div className="flex items-center justify-between">
                        {config.show_price && (
                          <div className="font-extrabold text-xs" style={{ color: config.primary_color }}>
                            $129.99
                          </div>
                        )}
                        
                        <span 
                          className="inline-flex items-center text-[9px] px-1.5 py-0.5 rounded-full font-bold uppercase tracking-wide"
                          style={{ 
                            color: config.primary_color, 
                            backgroundColor: `${config.primary_color}10`, 
                            border: `1px solid ${config.primary_color}25` 
                          }}
                        >
                          98% match
                        </span>
                      </div>
                    </div>
                  </div>

                </div>

                {/* Simulated Floating widget launcher button */}
                <div className="p-4 flex justify-end shrink-0 border-t border-slate-100/50">
                  <div
                    className="w-10 h-10 rounded-full flex items-center justify-center text-white shadow-lg cursor-pointer transform hover:scale-105 transition-all text-xs"
                    style={{
                      backgroundColor: config.primary_color,
                      alignSelf: config.position === 'bottom-right' ? 'flex-end' : 'flex-start',
                      marginLeft: config.position === 'bottom-left' ? '0' : 'auto',
                      marginRight: config.position === 'bottom-right' ? '0' : 'auto',
                      boxShadow: `0 4px 14px ${config.primary_color}45`
                    }}
                  >
                    <Search className="h-4 w-4" aria-hidden="true" />
                  </div>
                </div>

              </div>
            </div>

            <div className="p-4 bg-slate-50 border border-slate-200/80 rounded-xl flex items-center gap-2.5">
              <Sparkles className="w-4 h-4 text-brand shrink-0 animate-pulse" />
              <p className="text-[10px] text-neutral-mediumgray leading-relaxed font-semibold">
                The widget renders asynchronously as an overlay in the merchant storefront. Saved style changes appear when the widget reloads its configuration.
              </p>
            </div>
          </div>

        </div>

      </div>
    </Layout>
  );
};
