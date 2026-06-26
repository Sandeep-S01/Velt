import React, { useState, useEffect, useRef } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api, API_BASE_URL, getApiDocsUrl } from '../../lib/api';

import { Layout } from '../../components/Layout';
import type { StoreModel } from '../Stores/StoreList';
import { 
  UploadCloud, FileSpreadsheet, RefreshCw, Key, 
  Database, ShieldCheck, AlertCircle, Sparkles, ShoppingBag,
  Code, Copy, Check, Eye, EyeOff, Search, 
  ChevronRight, ArrowLeft, ArrowUpRight
} from 'lucide-react';

interface ProductModel {
  id: string;
  title: string;
  price?: number;
  category?: string;
  brand?: string;
  image_url?: string;
  inventory_count: number;
}

interface APIKeyModel {
  id: number;
  key: string;
  name: string;
  is_active: boolean;
  created_at: string;
  last_used_at?: string;
}

type TabType = 'html' | 'react' | 'vue' | 'api';

export const StoreDetail: React.FC = () => {
  const { storeId } = useParams<{ storeId: string }>();
  
  // States
  const [store, setStore] = useState<StoreModel | null>(null);
  const [stores, setStores] = useState<StoreModel[]>([]);
  const [products, setProducts] = useState<ProductModel[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKeyModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [productsLoading, setProductsLoading] = useState(true);
  const [keysLoading, setKeysLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // File Upload State
  const [dragActive, setDragActive] = useState(false);
  const [uploadFile, setUploadFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [uploadSuccess, setUploadSuccess] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);


  // UX Interactive States
  const [activeSnippetTab, setActiveSnippetTab] = useState<TabType>('html');
  const [envMode, setEnvMode] = useState<'production' | 'development'>('production');
  const [showApiKey, setShowApiKey] = useState(false);
  const [copiedText, setCopiedText] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('all');

  const fetchStoreData = async () => {
    if (!storeId) return;
    try {
      const data = await api.get<StoreModel>(`/stores/${storeId}`);
      setStore(data);
      
      // If indexing, poll for updates
      if (data.index_status === 'indexing') {
        setTimeout(fetchStoreData, 3000);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load store data');
    } finally {
      setLoading(false);
    }
  };

  const fetchStores = async () => {
    try {
      const data = await api.get<StoreModel[]>('/stores/');
      setStores(data);
    } catch (err) {
      console.error('Failed to load stores list', err);
    }
  };

  const fetchProducts = async () => {
    if (!storeId) return;
    try {
      setProductsLoading(true);
      const data = await api.get<ProductModel[]>(`/products/store/${storeId}`);
      setProducts(data);
    } catch (err: any) {
      console.error('Failed to load products', err);
    } finally {
      setProductsLoading(false);
    }
  };

  const fetchApiKeys = async () => {
    if (!storeId) return;
    try {
      setKeysLoading(true);
      const data = await api.get<APIKeyModel[]>(`/stores/${storeId}/keys`);
      setApiKeys(data);
    } catch (err: any) {
      console.error('Failed to load API keys', err);
    } finally {
      setKeysLoading(false);
    }
  };

  useEffect(() => {
    if (storeId) {
      fetchStoreData();
      fetchProducts();
      fetchApiKeys();
      fetchStores();
    }
  }, [storeId]);

  // Drag & Drop Handlers
  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (file.size > 10 * 1024 * 1024) {
        setUploadError('File size exceeds the 10MB limit.');
        return;
      }
      if (file.name.endsWith('.csv') || file.name.endsWith('.json')) {
        setUploadFile(file);
        setUploadError(null);
        setUploadSuccess(false);
      } else {
        setUploadError('Only CSV or JSON files are supported.');
      }
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (file.size > 10 * 1024 * 1024) {
        setUploadError('File size exceeds the 10MB limit.');
        return;
      }
      setUploadFile(file);
      setUploadError(null);
      setUploadSuccess(false);
    }
  };

  const handleUploadSubmit = async () => {
    if (!uploadFile || !storeId) return;
    setUploading(true);
    setUploadError(null);
    setUploadSuccess(false);

    const formData = new FormData();
    formData.append('file', uploadFile);
    formData.append('store_id', storeId);

    try {
      let api_key = apiKeys[0]?.key;
      if (!api_key) {
        // If no keys exist, auto-generate a default key
        const generatedKey = await api.post<APIKeyModel>(`/stores/${storeId}/keys`, {
          name: 'Default Ingestion Key',
          is_active: true
        });
        setApiKeys((prev) => [generatedKey, ...prev]);
        api_key = generatedKey.key;
      }

      await api.post('/upload', formData, {
        headers: {
          'X-API-Key': api_key
        }
      });
      setUploadSuccess(true);
      setUploadFile(null);
      
      // Force reload store metadata & products
      fetchStoreData();
      setTimeout(fetchProducts, 4000);
    } catch (err: any) {
      setUploadError(err.message || 'File upload failed');
    } finally {
      setUploading(false);
    }
  };

  const triggerCopy = (text: string, identifier: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(identifier);
    setTimeout(() => setCopiedText(null), 2000);
  };

  if (loading) {
    return (
      <Layout stores={stores} selectedStoreId={storeId}>
        <div className="flex flex-col items-center justify-center py-32 space-y-4">
          <RefreshCw className="w-8 h-8 animate-spin text-brand" />
          <h2 className="text-sm font-semibold text-neutral-mediumgray">Loading workspace details...</h2>
        </div>
      </Layout>
    );
  }

  if (error || !store) {
    return (
      <Layout stores={stores} selectedStoreId={storeId}>
        <div className="max-w-md mx-auto mt-12 bg-white border border-red-100 rounded-3xl p-8 text-center shadow-lg">
          <div className="w-12 h-12 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-neutral-charcoal mb-2">Failed to load Storefront</h2>
          <p className="text-xs text-neutral-mediumgray mb-6">{error || 'The requested storefront could not be located.'}</p>
          <Link to="/stores" className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-black text-white text-xs font-bold rounded-xl transition-all">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to My Stores
          </Link>
        </div>
      </Layout>
    );
  }

  // Code Snippet generation templates
  const primaryApiKey = apiKeys[0]?.key || 'vt_live_pk_********************';
  const getEmbedCode = (tab: TabType) => {
    const cleanStoreId = store.id;
    const currentOrigin = window.location.origin;
    const apiV1Base = API_BASE_URL;
    
    switch(tab) {
      case 'html':
        return `<!-- Place this snippet inside your website's header or footer HTML -->
<!-- 1. Include the search widget script -->
<script src="${currentOrigin}/widget.js" id="ss-widget-script"></script>

<!-- 2. Initialize the widget with your credentials -->
<script>
  window.addEventListener('load', () => {
    window.ssWidgetInstance = new window.SmartSearchWidget(
      "${cleanStoreId}",
      "${apiV1Base}"
    );
  });
</script>`;
      case 'react':
        return `// Velt Search overlay drop-in React Component
import { useEffect } from 'react';

export function VeltSearchWidget() {
  useEffect(() => {
    const script = document.createElement('script');
    script.src = "${currentOrigin}/widget.js";
    script.async = true;
    script.onload = () => {
      window.ssWidgetInstance = new window.SmartSearchWidget('${cleanStoreId}', '${apiV1Base}');
    };
    document.body.appendChild(script);
    
    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return null;
}`;
      case 'vue':
        return `<!-- VeltSearchWidget.vue (Vue 3 Composition API) -->
<template>
  <div id="velt-search-root"></div>
</template>

<script setup>
import { onMounted, onUnmounted } from 'vue';

let widgetInstance = null;

onMounted(() => {
  const script = document.createElement('script');
  script.src = "${currentOrigin}/widget.js";
  script.async = true;
  script.onload = () => {
    widgetInstance = new window.SmartSearchWidget('${cleanStoreId}', '${apiV1Base}');
  };
  document.body.appendChild(script);
  
  onUnmounted(() => {
    document.body.removeChild(script);
  });
});
</script>`;
      case 'api':
        return `// Direct fetch lookup using Velt AI Semantic Search Endpoint
const searchCatalog = async (userQuery) => {
  const response = await fetch('${apiV1Base}/search', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-API-Key': '${primaryApiKey}'
    },
    body: JSON.stringify({
      query: userQuery,
      limit: 5
    })
  });
  return await response.json();
};`;

      default:
        return '';
    }
  };

  // Filtered Products
  const filteredProducts = products.filter(prod => {
    const matchesSearch = prod.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
                          prod.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          (prod.brand && prod.brand.toLowerCase().includes(searchQuery.toLowerCase()));
    const matchesCategory = categoryFilter === 'all' || prod.category === categoryFilter;
    return matchesSearch && matchesCategory;
  });

  // Unique categories list
  const categories = ['all', ...Array.from(new Set(products.map(p => p.category).filter(Boolean)))];

  // Dynamic Onboarding Step Resolution

  const isSyncInProgress = store.index_status === 'indexing';
  const isCatalogReady = store.index_status === 'ready' && (store.indexed_product_count || 0) > 0;
  
  const currentStep = isCatalogReady ? 3 : (isSyncInProgress ? 2 : 1);

  return (
    <Layout stores={stores} selectedStoreId={store.id}>
      <div className="max-w-6xl mx-auto space-y-8 pb-16">
        
        {/* Workspace Title Hero Bar */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm">
          <div className="space-y-1 flex-1">
            <div className="flex items-center gap-2">
              <Link to="/stores" className="text-neutral-mediumgray hover:text-neutral-charcoal transition-all">
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <span className="px-2 py-0.5 bg-brand/5 border border-brand/10 text-brand text-[10px] uppercase font-bold rounded-md">
                {store.platform} integration
              </span>
            </div>
            <h1 className="text-2xl font-black text-neutral-charcoal tracking-tight">{store.name}</h1>
            <p className="text-xs text-neutral-mediumgray">
              Linked Platform Catalog Key: <code className="bg-slate-100 px-1.5 py-0.5 rounded text-[10px] font-mono font-bold text-slate-700">{store.id}</code>
            </p>
          </div>

          <div className="flex items-center gap-6 divide-x divide-slate-100">
            <div className="px-4 first:pl-0">
              <span className="text-[10px] uppercase font-bold tracking-wider text-neutral-mediumgray block">Vector Database Size</span>
              <span className="text-2xl font-black text-neutral-charcoal mt-0.5">
                {store.indexed_product_count || 0} <span className="text-xs font-semibold text-neutral-mediumgray">SKUs</span>
              </span>
            </div>
            <div className="pl-6">
              <span className="text-[10px] uppercase font-bold tracking-wider text-neutral-mediumgray block">Catalog Status</span>
              <div className="flex items-center gap-2 mt-1">
                <span className={`w-2.5 h-2.5 rounded-full ${
                  store.index_status === 'ready' ? 'bg-green-500 shadow-sm shadow-green-200' :
                  store.index_status === 'indexing' ? 'bg-purple-500 animate-pulse' :
                  'bg-amber-400'
                }`}></span>
                <span className="text-xs font-extrabold text-neutral-charcoal capitalize">
                  {store.index_status === 'ready' ? 'Ready' : store.index_status === 'indexing' ? 'Syncing...' : 'Pending Sync'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* 3-Step Visual Onboarding Flow Guide */}
        <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm">
          <div className="text-xs font-bold text-slate-800 mb-6 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-brand" />
            <span>Storefront Setup Progress</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
            
            {/* Step 1: Connect */}
            <div className="flex gap-4 relative z-10">
              <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center font-bold text-xs ${
                currentStep >= 1 ? 'bg-brand text-white' : 'bg-slate-100 text-slate-400'
              }`}>
                {currentStep > 1 ? <Check className="w-4 h-4" /> : '1'}
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-slate-900">Connect Storefront</h4>
                <p className="text-[11px] text-neutral-mediumgray leading-relaxed">
                  Platform integration database linked. Ready for initial upload ingestion.
                </p>
                <span className="inline-flex items-center text-[10px] font-bold text-green-600 bg-green-50 border border-green-150 px-1.5 py-0.5 rounded">
                  Connected
                </span>
              </div>
            </div>

            {/* Step 2: Processing */}
            <div className="flex gap-4 relative z-10">
              <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center font-bold text-xs ${
                currentStep >= 2 ? 'bg-brand text-white' : 'bg-slate-100 text-slate-400'
              }`}>
                {currentStep > 2 ? <Check className="w-4 h-4" /> : '2'}
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-slate-900">Compile Search Index</h4>
                <p className="text-[11px] text-neutral-mediumgray leading-relaxed">
                  Ingest files to generate semantic vectors & build fast search embeddings.
                </p>
                {isSyncInProgress ? (
                  <span className="inline-flex items-center text-[10px] font-bold text-purple-600 bg-purple-50 border border-purple-150 px-1.5 py-0.5 rounded animate-pulse">
                    Vectorizing...
                  </span>
                ) : store.indexed_product_count && store.indexed_product_count > 0 ? (
                  <span className="inline-flex items-center text-[10px] font-bold text-green-600 bg-green-50 border border-green-150 px-1.5 py-0.5 rounded">
                    Indexed
                  </span>
                ) : (
                  <span className="inline-flex items-center text-[10px] font-bold text-amber-600 bg-amber-50 border border-amber-150 px-1.5 py-0.5 rounded">
                    Awaiting Ingestion
                  </span>
                )}
              </div>
            </div>

            {/* Step 3: Embed */}
            <div className="flex gap-4 relative z-10">
              <div className={`w-8 h-8 rounded-full shrink-0 flex items-center justify-center font-bold text-xs ${
                currentStep === 3 ? 'bg-brand text-white' : 'bg-slate-100 text-slate-400'
              }`}>
                3
              </div>
              <div className="space-y-1">
                <h4 className="text-xs font-bold text-slate-900">Embed Widgets Live</h4>
                <p className="text-[11px] text-neutral-mediumgray leading-relaxed">
                  Add script bundle or widget builder components to launch search autocomplete on site.
                </p>
                {isCatalogReady ? (
                  <span className="inline-flex items-center text-[10px] font-bold text-green-600 bg-green-50 border border-green-150 px-1.5 py-0.5 rounded">
                    Widget Ready
                  </span>
                ) : (
                  <span className="inline-flex items-center text-[10px] font-bold text-slate-400 bg-slate-50 border border-slate-200/60 px-1.5 py-0.5 rounded">
                    Inactive
                  </span>
                )}
              </div>
            </div>

          </div>
        </div>

        {/* Real-time Indexing Progress Banner */}
        {isSyncInProgress && (
          <div className="bg-purple-50 border border-purple-100 rounded-2xl p-6 shadow-sm space-y-3">
            <div className="flex items-center justify-between">
              <h3 className="text-sm font-bold text-purple-950 flex items-center gap-2">
                <RefreshCw className="w-4 h-4 animate-spin text-brand" />
                <span>Vector Indexing in progress...</span>
              </h3>
              <span className="text-xs font-mono font-bold text-brand">
                {store.index_progress_percent || 0}% Complete
              </span>
            </div>
            <p className="text-xs text-purple-800 leading-relaxed max-w-2xl">
              Velt AI is parsing your product descriptions, converting titles & tags to 1536-dimension embeddings, and indexing them in our vector engine. Do not navigate away.
            </p>
            <div className="w-full bg-purple-100 rounded-full h-2 overflow-hidden">
              <div 
                className="bg-brand h-full rounded-full transition-all duration-700" 
                style={{ width: `${store.index_progress_percent || 0}%` }}
              ></div>
            </div>
            <div className="text-[10px] text-purple-700 font-semibold flex justify-between">
              <span>Status: indexing products</span>
              <span>{store.indexed_product_count || 0} / {store.total_product_count || 0} lines vectorized</span>
            </div>
          </div>
        )}

        {/* Core Layout Split columns */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 items-start">
          
          {/* Main Actions Column */}
          <div className="lg:col-span-2 space-y-8">
            
            {/* CSV/JSON Manual Ingestor */}
            <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm space-y-4">
              <div>
                <h3 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2">
                  <UploadCloud className="w-4 h-4 text-brand" />
                  <span>Manual Ingestion Feed</span>
                </h3>
                <p className="text-xs text-neutral-mediumgray mt-1 leading-relaxed">
                  Directly ingest store items. Drag and drop a product spreadsheet (CSV or JSON) to quickly load your inventory data.
                </p>
              </div>

              <div
                onDragEnter={handleDrag}
                onDragOver={handleDrag}
                onDragLeave={handleDrag}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                className={`border border-dashed rounded-xl p-8 text-center cursor-pointer transition-all flex flex-col items-center justify-center space-y-3 ${
                  dragActive 
                    ? 'border-brand bg-brand/5 shadow-inner' 
                    : 'border-slate-300/80 hover:border-brand/40 bg-slate-50/50 hover:bg-slate-50'
                }`}
              >
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleFileChange}
                  accept=".csv,.json"
                  className="hidden"
                />
                
                <div className="w-10 h-10 rounded-full bg-white border border-slate-200 flex items-center justify-center shadow-sm text-neutral-mediumgray group-hover:text-brand">
                  <FileSpreadsheet className="w-5 h-5 text-neutral-mediumgray" />
                </div>
                
                <div className="space-y-1">
                  <p className="text-xs font-bold text-neutral-charcoal">
                    {uploadFile ? uploadFile.name : 'Select product feed spreadsheet'}
                  </p>
                  <p className="text-[10px] text-neutral-mediumgray">
                    Supports .csv or .json formatted datasets up to 10 MB limit
                  </p>
                </div>
              </div>

              {uploadError && (
                <div className="p-3 bg-red-50 border border-red-150 rounded-xl text-[11px] text-red-700 flex gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 mt-0.5 text-red-500" />
                  <span>{uploadError}</span>
                </div>
              )}

              {uploadSuccess && (
                <div className="p-3 bg-green-50 border border-green-150 rounded-xl text-[11px] text-green-700 flex gap-2">
                  <ShieldCheck className="w-4 h-4 shrink-0 mt-0.5 text-green-600" />
                  <span>Ingested spreadsheet lines. Embedding vector compilation launched in background!</span>
                </div>
              )}

              {uploadFile && (
                <div className="flex items-center justify-end gap-2 pt-2 border-t border-slate-100">
                  <button
                    onClick={() => setUploadFile(null)}
                    className="px-3 py-1.5 text-xs font-bold border border-slate-200 text-slate-600 hover:bg-slate-50 rounded-xl cursor-pointer"
                  >
                    Discard
                  </button>
                  <button
                    onClick={handleUploadSubmit}
                    disabled={uploading}
                    className="px-4 py-1.5 text-xs font-bold text-white bg-brand hover:bg-brand-dark rounded-xl flex items-center gap-1.5 cursor-pointer disabled:opacity-50"
                  >
                    {uploading ? (
                      <>
                        <RefreshCw className="w-3.5 h-3.5 animate-spin" /> Ingesting...
                      </>
                    ) : (
                      'Launch Vectors Sync'
                    )}
                  </button>
                </div>
              )}
            </div>

            {/* Smart Product Catalog List */}
            <div className="bg-white border border-slate-200/80 rounded-2xl overflow-hidden shadow-sm">
              <div className="p-6 border-b border-slate-100 flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h3 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2">
                    <Database className="w-4 h-4 text-brand" />
                    <span>Product Catalog List</span>
                  </h3>
                  <p className="text-xs text-neutral-mediumgray mt-0.5">
                    Previewing vectorized items available for instant overlay client searches.
                  </p>
                </div>

                <div className="flex items-center gap-3">
                  <div className="relative">
                    <Search className="w-4 h-4 absolute left-3 top-2.5 text-neutral-mediumgray" />
                    <input
                      type="text"
                      placeholder="Search title, SKU, brand..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="pl-9 pr-4 py-2 bg-slate-50 border border-slate-200 hover:border-slate-350 focus:border-brand rounded-xl text-xs text-slate-800 focus:outline-none transition-all w-48 md:w-56"
                    />
                  </div>

                  <select
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                    className="px-3 py-2 bg-slate-50 border border-slate-200 hover:border-slate-300 rounded-xl text-xs text-slate-800 focus:outline-none transition-all cursor-pointer font-semibold capitalize animate-slide-up"
                  >
                    {categories.map((cat) => (
                      <option key={cat} value={cat}>
                        {cat === 'all' ? 'All Categories' : cat}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {productsLoading ? (
                <div className="p-16 flex flex-col items-center justify-center space-y-2">
                  <RefreshCw className="w-6 h-6 animate-spin text-brand" />
                  <span className="text-xs text-neutral-mediumgray font-semibold">Updating indexes table...</span>
                </div>
              ) : filteredProducts.length === 0 ? (
                <div className="p-16 text-center">
                  <ShoppingBag className="w-12 h-12 text-slate-300 mx-auto mb-4" />
                  <h4 className="text-xs font-bold text-slate-800">No items matched search parameters</h4>
                  <p className="text-[11px] text-neutral-mediumgray mt-1 leading-relaxed max-w-sm mx-auto">
                    Try altering filters, query inputs, or upload a store dataset to expand search query targets.
                  </p>
                </div>
              ) : (
                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs border-collapse">
                    <thead>
                      <tr className="bg-slate-50 border-b border-slate-100 font-bold text-neutral-mediumgray">
                        <th className="px-6 py-3 font-extrabold uppercase tracking-wider text-[10px]">SKU / ID</th>
                        <th className="px-6 py-3 font-extrabold uppercase tracking-wider text-[10px]">Item</th>
                        <th className="px-6 py-3 font-extrabold uppercase tracking-wider text-[10px]">Category</th>
                        <th className="px-6 py-3 font-extrabold uppercase tracking-wider text-[10px]">Brand</th>
                        <th className="px-6 py-3 font-extrabold uppercase tracking-wider text-[10px]">Status</th>
                        <th className="px-6 py-3 font-extrabold uppercase tracking-wider text-[10px] text-right">Price</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                      {filteredProducts.slice(0, 15).map((prod) => (
                        <tr key={prod.id} className="hover:bg-slate-50/50 transition-all">
                          <td className="px-6 py-4 font-mono font-bold text-[10px] text-neutral-mediumgray">{prod.id}</td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              {prod.image_url ? (
                                <img src={prod.image_url} alt={prod.title} className="w-8 h-8 rounded-lg border border-slate-100 object-cover shrink-0" />
                              ) : (
                                <div className="w-8 h-8 rounded-lg bg-slate-100 border border-slate-200/60 flex items-center justify-center text-[10px] text-slate-400 shrink-0">
                                  📦
                                </div>
                              )}
                              <span className="font-semibold text-slate-800 truncate max-w-[180px]">{prod.title}</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 font-semibold text-neutral-mediumgray capitalize">{prod.category || '--'}</td>
                          <td className="px-6 py-4 text-neutral-mediumgray">{prod.brand || '--'}</td>
                          <td className="px-6 py-4">
                            <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-700 border border-green-150">
                              <span className="w-1.5 h-1.5 bg-green-500 rounded-full"></span> Indexed
                            </span>
                          </td>
                          <td className="px-6 py-4 font-bold text-slate-800 text-right">
                            {prod.price !== undefined ? `$${prod.price.toFixed(2)}` : '--'}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>

                  {filteredProducts.length > 15 && (
                    <div className="p-4 bg-slate-50 border-t border-slate-100 text-center text-xs font-bold text-neutral-mediumgray">
                      Showing top 15 results. {filteredProducts.length} items currently match filters.
                    </div>
                  )}
                </div>
              )}
            </div>

          </div>

          {/* Widgets Integration Right Side Sidebar */}
          <div className="space-y-8">
            
            {/* Copy-Paste Widget Integrator Card */}
            <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-white shadow-xl space-y-4 relative overflow-hidden">
              <div className="absolute right-0 top-0 w-32 h-32 bg-brand/10 rounded-full blur-2xl pointer-events-none"></div>
              
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <h3 className="text-sm font-bold flex items-center gap-1.5 text-slate-150">
                    <Code className="w-4 h-4 text-brand-light" />
                    <span>Widget Embed Setup</span>
                  </h3>
                  
                  {/* Environment Switcher */}
                  <div className="bg-slate-850 p-0.5 rounded-lg border border-slate-750 flex">
                    <button
                      onClick={() => setEnvMode('production')}
                      className={`px-2 py-0.5 text-[9px] font-extrabold rounded-md uppercase tracking-wider transition-all ${
                        envMode === 'production' 
                          ? 'bg-brand text-white shadow-sm' 
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Prod
                    </button>
                    <button
                      onClick={() => setEnvMode('development')}
                      className={`px-2 py-0.5 text-[9px] font-extrabold rounded-md uppercase tracking-wider transition-all ${
                        envMode === 'development' 
                          ? 'bg-brand text-white shadow-sm' 
                          : 'text-slate-400 hover:text-white'
                      }`}
                    >
                      Dev
                    </button>
                  </div>
                </div>
                <p className="text-[11px] text-slate-400 leading-relaxed">
                  Paste the snippet at the bottom of your HTML document before the closing body tag.
                </p>
              </div>

              {/* Snippet Tabs */}
              <div className="border-b border-slate-800 flex gap-2">
                {(['html', 'react', 'vue', 'api'] as TabType[]).map((tab) => (
                  <button
                    key={tab}
                    onClick={() => setActiveSnippetTab(tab)}
                    className={`pb-2 px-1 text-xs font-bold transition-all border-b-2 uppercase tracking-wide cursor-pointer ${
                      activeSnippetTab === tab 
                        ? 'border-brand text-brand-light font-extrabold' 
                        : 'border-transparent text-slate-400 hover:text-slate-200'
                    }`}
                  >
                    {tab}
                  </button>
                ))}
              </div>

              {/* Code Container */}
              <div className="relative group">
                <button
                  onClick={() => triggerCopy(getEmbedCode(activeSnippetTab), 'snippet')}
                  className="absolute right-3 top-3 p-1.5 bg-slate-800 hover:bg-slate-700 rounded-lg text-slate-350 hover:text-white border border-slate-700/80 transition-all cursor-pointer"
                >
                  {copiedText === 'snippet' ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
                
                <pre className="bg-black/50 border border-slate-800 rounded-xl p-4 font-mono text-[10px] text-slate-300 leading-relaxed overflow-x-auto select-all max-h-56">
                  <code>{getEmbedCode(activeSnippetTab)}</code>
                </pre>
              </div>

              <div className="pt-2 flex justify-between items-center text-[10px] text-slate-400 border-t border-slate-800/80">
                <Link to={`/stores/${store.id}/settings`} className="flex items-center gap-1 hover:text-white font-bold transition-all text-brand-light">
                  <span>Customizer widget UI settings</span>
                  <ChevronRight className="w-3.5 h-3.5" />
                </Link>
                 <a href={getApiDocsUrl()} target="_blank" rel="noreferrer" className="flex items-center gap-1 hover:text-white font-bold transition-all">
                  <span>Open API Specs</span>
                  <ArrowUpRight className="w-3.5 h-3.5" />
                </a>

              </div>
            </div>

            {/* Quick Live API Key Manager */}
            <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2">
                    <Key className="w-4 h-4 text-brand" />
                    <span>Velt API Keys</span>
                  </h3>
                  <p className="text-[11px] text-neutral-mediumgray mt-0.5">
                    Authorized private connection tokens.
                  </p>
                </div>
                
                <Link 
                  to={`/stores/${store.id}/keys`}
                  className="text-[11px] font-bold text-brand hover:underline flex items-center gap-0.5 shrink-0"
                >
                  <span>Manage Keys</span>
                  <ChevronRight className="w-3 h-3" />
                </Link>
              </div>

              {keysLoading ? (
                <div className="h-10 bg-slate-50 animate-pulse rounded-xl"></div>
              ) : apiKeys.length === 0 ? (
                <div className="text-center py-6 border border-dashed border-slate-200 rounded-xl bg-slate-50/50">
                  <p className="text-[11px] text-neutral-mediumgray font-semibold">No active API keys created yet.</p>
                </div>
              ) : (
                <div className="space-y-3">
                  {apiKeys.slice(0, 2).map((keyObj) => (
                    <div key={keyObj.id} className="p-3 border border-slate-150 rounded-xl space-y-2 relative bg-slate-50/40 hover:border-brand/40 transition-all">
                      <div className="flex items-center justify-between pr-8">
                        <span className="text-[11px] font-bold text-slate-800 truncate">{keyObj.name}</span>
                        <span className="text-[9px] font-bold uppercase px-1.5 py-0.5 bg-green-50 text-green-700 rounded border border-green-150 shrink-0">
                          Active
                        </span>
                      </div>

                      <div className="flex items-center gap-2">
                        <div className="font-mono text-[10px] bg-white border border-slate-150 px-2 py-1 rounded text-slate-700 select-all overflow-x-auto flex-1">
                          {showApiKey ? keyObj.key : `vt_live_pk_${keyObj.key.slice(11, 15)}*******************`}
                        </div>
                        <button
                          onClick={() => setShowApiKey(!showApiKey)}
                          className="p-1.5 hover:bg-slate-150 rounded-lg text-neutral-mediumgray hover:text-slate-800 border border-slate-200 bg-white transition-all cursor-pointer shrink-0"
                          title={showApiKey ? 'Hide credentials' : 'Show credentials'}
                        >
                          {showApiKey ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                        </button>
                        <button
                          onClick={() => triggerCopy(keyObj.key, `key-${keyObj.id}`)}
                          className="p-1.5 hover:bg-slate-150 rounded-lg text-neutral-mediumgray hover:text-slate-800 border border-slate-200 bg-white transition-all cursor-pointer shrink-0"
                          title="Copy API key"
                        >
                          {copiedText === `key-${keyObj.id}` ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                        </button>
                      </div>
                    </div>
                  ))}

                  {apiKeys.length > 2 && (
                    <Link to={`/stores/${store.id}/keys`} className="block text-center text-[10px] font-bold text-neutral-mediumgray hover:text-slate-800 bg-slate-50 border border-slate-250/60 rounded-lg py-1.5 hover:bg-slate-100 transition-all">
                      View all {apiKeys.length} generated credentials
                    </Link>
                  )}
                </div>
              )}

              {/* Warning Alert */}
              <div className="p-3 bg-amber-50 border border-amber-100 rounded-xl flex gap-2.5">
                <AlertCircle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
                <p className="text-[10px] text-amber-800 leading-relaxed font-semibold">
                  <strong>Security Note:</strong> These are private live authentication tokens. Do not expose private keys in public code repositories or client-side Javascript. Use them on secure server actions.
                </p>
              </div>
            </div>

          </div>
        </div>

      </div>
    </Layout>
  );
};
