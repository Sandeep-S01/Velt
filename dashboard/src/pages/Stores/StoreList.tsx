import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api } from '../../lib/api';
import { Layout } from '../../components/Layout';
import { 
  Plus, 
  Store, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle, 
  HelpCircle,
  ArrowRight,
  Clock,
  Trash2,
  Sliders,
  TrendingUp
} from 'lucide-react';

export interface StoreModel {
  id: string;
  name: string;
  platform: string;
  platform_store_id?: string;
  webhook_secret?: string;
  is_active: boolean;
  sync_frequency_hours: number;
  last_sync_at?: string;
  index_status?: string; // pending, indexing, ready, error
  index_progress_percent?: number;
  total_product_count?: number;
  indexed_product_count?: number;
}

export const StoreList: React.FC = () => {
  const [stores, setStores] = useState<StoreModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [newStoreName, setNewStoreName] = useState('');
  const [newStorePlatform, setNewStorePlatform] = useState('custom');
  const [submitting, setSubmitting] = useState(false);

  const fetchStores = async () => {
    try {
      const data = await api.get<StoreModel[]>('/stores/');
      setStores(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load stores');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStores();
  }, []);

  const handleCreateStore = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newStoreName.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      const newStore = await api.post<StoreModel>('/stores/', {
        name: newStoreName,
        platform: newStorePlatform,
        is_active: true,
        sync_frequency_hours: 24,
      });

      setStores((prev) => [newStore, ...prev]);
      setIsModalOpen(false);
      setNewStoreName('');
      setNewStorePlatform('custom');
    } catch (err: any) {
      setError(err.message || 'Failed to create store');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteStore = async (id: string, name: string) => {
    if (!confirm(`Are you sure you want to delete the store "${name}"? All product indexes and API configurations will be permanently removed.`)) {
      return;
    }
    
    try {
      await api.delete(`/stores/${id}`);
      setStores((prev) => prev.filter((s) => s.id !== id));
    } catch (err: any) {
      alert(err.message || 'Failed to delete store');
    }
  };

  const getStatusBadge = (status?: string) => {
    switch (status) {
      case 'ready':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-green-50 text-green-700 border border-green-200">
            <CheckCircle2 className="w-3 h-3" /> Ready
          </span>
        );
      case 'indexing':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-brand/10 text-brand border border-brand/20 animate-pulse">
            <RefreshCw className="w-3 h-3 animate-spin" /> Indexing
          </span>
        );
      case 'error':
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-red-50 text-red-700 border border-red-200">
            <AlertTriangle className="w-3 h-3" /> Error
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-50 text-neutral-mediumgray border border-neutral-lightgray">
            <HelpCircle className="w-3 h-3" /> Pending
          </span>
        );
    }
  };

  // Aggregate Metrics Calculations
  const totalStores = stores.length;
  const totalProducts = stores.reduce((acc, s) => acc + (s.indexed_product_count || 0), 0);
  const mockSearchesToday = totalStores > 0 ? totalStores * 4180 : 0;
  const mockLatency = totalStores > 0 ? "42ms" : "--";

  return (
    <Layout stores={stores}>
      <div className="max-w-7xl mx-auto space-y-8 animate-fade-in">
        
        {/* Header Block */}
        <div className="flex flex-col sm:flex-row justify-between sm:items-center gap-4">
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight text-neutral-charcoal">My Stores</h1>
            <p className="text-sm text-neutral-mediumgray mt-1">Connect and configure AI-powered storefront search widgets</p>
          </div>
          <button
            onClick={() => setIsModalOpen(true)}
            className="flex items-center gap-2 px-5 py-3 bg-brand hover:bg-brand-dark text-white text-sm font-bold rounded-xl transition-all shadow-md shadow-brand/10 active:scale-95 cursor-pointer"
          >
            <Plus className="w-4 h-4" />
            Add Store
          </button>
        </div>

        {/* Global Summary Statistics Row */}
        {stores.length > 0 && (
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="bg-white rounded-2xl border border-neutral-lightgray/80 p-5 shadow-sm space-y-2">
              <div className="text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">Total Stores</div>
              <div className="text-2xl font-black text-neutral-charcoal">{totalStores}</div>
              <span className="text-[10px] text-brand font-semibold block">Connected workspaces</span>
            </div>
            <div className="bg-white rounded-2xl border border-neutral-lightgray/80 p-5 shadow-sm space-y-2">
              <div className="text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">Indexed Products</div>
              <div className="text-2xl font-black text-neutral-charcoal">{totalProducts.toLocaleString()}</div>
              <span className="text-[10px] text-green-600 font-semibold block">Sync status complete</span>
            </div>
            <div className="bg-white rounded-2xl border border-neutral-lightgray/80 p-5 shadow-sm space-y-2">
              <div className="text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">Searches Today</div>
              <div className="text-2xl font-black text-neutral-charcoal">{mockSearchesToday.toLocaleString()}</div>
              <span className="text-[10px] text-green-600 font-semibold flex items-center gap-1">
                <TrendingUp className="w-3.5 h-3.5" /> +14.2% increase
              </span>
            </div>
            <div className="bg-white rounded-2xl border border-neutral-lightgray/80 p-5 shadow-sm space-y-2">
              <div className="text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">Average response</div>
              <div className="text-2xl font-black text-neutral-charcoal">{mockLatency}</div>
              <span className="text-[10px] text-neutral-mediumgray font-semibold block">Vector search latency</span>
            </div>
          </div>
        )}

        {/* Loading and Empty State Panels */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[1, 2, 3].map((n) => (
              <div key={n} className="bg-white rounded-3xl border border-neutral-lightgray/80 p-6 shadow-sm animate-pulse-soft space-y-4">
                <div className="h-6 w-1/3 bg-slate-100 rounded"></div>
                <div className="h-4 w-3/4 bg-slate-100 rounded"></div>
                <div className="h-10 bg-slate-50 rounded mt-6"></div>
              </div>
            ))}
          </div>
        ) : error ? (
          <div className="bg-red-50 border border-red-200 rounded-2xl p-5 flex gap-3 text-red-700 font-medium">
            <AlertTriangle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        ) : stores.length === 0 ? (
          <div className="text-center py-20 bg-white border border-dashed border-neutral-lightgray rounded-3xl p-8 max-w-2xl mx-auto space-y-6">
            <div className="w-16 h-16 bg-brand/5 text-brand rounded-2xl flex items-center justify-center mx-auto shadow-sm border border-brand/10">
              <Store className="w-8 h-8" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-neutral-charcoal">Connect your first store</h3>
              <p className="text-sm text-neutral-mediumgray mt-2 max-w-sm mx-auto">
                Integrate your Shopify store catalog, connect WooCommerce, or upload a custom CSV catalogue to start searching semantically.
              </p>
            </div>
            <div className="flex flex-wrap justify-center gap-3">
              <button
                onClick={() => {
                  setNewStorePlatform('shopify');
                  setIsModalOpen(true);
                }}
                className="px-5 py-2.5 bg-brand hover:bg-brand-dark text-white font-bold text-sm rounded-xl transition-all cursor-pointer shadow-md"
              >
                Connect Shopify Store
              </button>
              <button
                onClick={() => {
                  setNewStorePlatform('custom');
                  setIsModalOpen(true);
                }}
                className="px-5 py-2.5 bg-slate-50 hover:bg-slate-100 border border-neutral-lightgray text-neutral-charcoal font-bold text-sm rounded-xl transition-all cursor-pointer"
              >
                Upload CSV / Custom Ingestion
              </button>
            </div>
          </div>
        ) : (
          /* Cards Grid */
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {stores.map((store) => (
              <div
                key={store.id}
                className="bg-white rounded-3xl border border-neutral-lightgray/80 overflow-hidden shadow-sm hover:shadow-md hover:border-brand/20 transition-all flex flex-col justify-between"
              >
                <div className="p-6 space-y-5">
                  {/* Status header */}
                  <div className="flex justify-between items-center">
                    <span className="px-2 py-0.5 rounded bg-slate-50 border border-neutral-lightgray text-[9px] font-bold uppercase tracking-wider text-neutral-mediumgray">
                      {store.platform} Ingestion
                    </span>
                    {getStatusBadge(store.index_status)}
                  </div>

                  {/* Info Header */}
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand to-brand-dark flex items-center justify-center text-white font-black text-sm shadow-md shadow-brand/10">
                      {store.name[0].toUpperCase()}
                    </div>
                    <div className="overflow-hidden">
                      <h3 className="text-lg font-black text-neutral-charcoal truncate">{store.name}</h3>
                      <p className="text-[10px] text-neutral-mediumgray font-mono truncate">{store.id}</p>
                    </div>
                  </div>

                  {/* Sync status parameters */}
                  <div className="bg-slate-50 border border-neutral-lightgray/60 rounded-2xl p-4.5 space-y-2.5 text-xs">
                    <div className="flex justify-between">
                      <span className="text-neutral-mediumgray font-semibold">Indexed Catalog:</span>
                      <span className="font-bold text-neutral-charcoal">
                        {store.indexed_product_count || 0} / {store.total_product_count || 0} items
                      </span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-neutral-mediumgray font-semibold">Sync Period:</span>
                      <span className="font-bold text-neutral-charcoal flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5 text-neutral-mediumgray" />
                        Every {store.sync_frequency_hours} hours
                      </span>
                    </div>

                    {store.index_status === 'indexing' && store.index_progress_percent !== undefined && (
                      <div className="pt-2">
                        <div className="flex justify-between text-[10px] font-bold text-brand uppercase tracking-wider mb-1.5">
                          <span>Vector indexing...</span>
                          <span>{store.index_progress_percent}%</span>
                        </div>
                        <div className="w-full bg-slate-200 rounded-full h-1.5 overflow-hidden">
                          <div
                            className="bg-brand h-1.5 rounded-full transition-all duration-300"
                            style={{ width: `${store.index_progress_percent}%` }}
                          ></div>
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                {/* Card Controls */}
                <div className="bg-slate-50/50 px-6 py-4.5 border-t border-neutral-lightgray/80 flex items-center justify-between">
                  <button
                    onClick={() => handleDeleteStore(store.id, store.name)}
                    className="p-2 border border-neutral-lightgray hover:border-red-200 hover:bg-red-50 text-neutral-mediumgray hover:text-red-500 rounded-xl transition-all cursor-pointer"
                    title="Remove storefront"
                  >
                    <Trash2 className="w-4 h-4" />
                  </button>

                  <div className="flex items-center gap-3">
                    <Link
                      to={`/stores/${store.id}/settings`}
                      className="inline-flex items-center gap-1.5 px-3 py-2 border border-neutral-lightgray hover:border-neutral-darkgray/30 bg-white rounded-xl text-xs font-bold text-neutral-darkgray transition-all shadow-sm"
                    >
                      <Sliders className="w-3.5 h-3.5 text-neutral-mediumgray" /> Design
                    </Link>
                    <Link
                      to={`/stores/${store.id}`}
                      className="inline-flex items-center gap-1 px-3 py-2 bg-brand hover:bg-brand-dark text-white rounded-xl text-xs font-bold transition-all shadow-sm"
                    >
                      Console <ArrowRight className="w-3.5 h-3.5" />
                    </Link>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Connect Store Modal */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-neutral-charcoal/30 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-neutral-lightgray overflow-hidden animate-slide-up">
              
              {/* Header */}
              <div className="px-6 py-4.5 border-b border-neutral-lightgray flex items-center gap-2">
                <Store className="w-5 h-5 text-brand" />
                <h3 className="font-extrabold text-neutral-charcoal text-base">Connect New Storefront</h3>
              </div>

              <form onSubmit={handleCreateStore} className="p-6 space-y-5">
                <div>
                  <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider mb-2">
                    Store Name
                  </label>
                  <input
                    type="text"
                    required
                    value={newStoreName}
                    onChange={(e) => setNewStoreName(e.target.value)}
                    className="block w-full px-4 py-3 bg-white border border-neutral-lightgray rounded-xl text-neutral-charcoal text-sm font-semibold focus:outline-none focus:border-brand focus:ring-4 focus:ring-brand/10 transition-all"
                    placeholder="e.g. Gems and Ornaments"
                  />
                </div>

                <div>
                  <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider mb-2">
                    E-Commerce Platform
                  </label>
                  <select
                    value={newStorePlatform}
                    onChange={(e) => setNewStorePlatform(e.target.value)}
                    className="block w-full px-4 py-3 bg-white border border-neutral-lightgray rounded-xl text-neutral-charcoal text-sm font-semibold focus:outline-none focus:border-brand focus:ring-4 focus:ring-brand/10 transition-all cursor-pointer"
                  >
                    <option value="custom">Custom Ingestion (CSV / JSON API)</option>
                    <option value="shopify">Shopify Integration</option>
                    <option value="woocommerce">WooCommerce (Coming soon)</option>
                  </select>
                </div>

                {newStorePlatform === 'shopify' && (
                  <div className="p-3 bg-brand/5 border border-brand/15 text-[11px] font-semibold text-brand-dark rounded-xl leading-relaxed">
                    Note: Shopify integration requires installing the Velt Connector application in your Shopify admin panel once registered.
                  </div>
                )}

                <div className="flex justify-end gap-3 pt-4 border-t border-neutral-lightgray">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2.5 border border-neutral-lightgray hover:bg-slate-50 rounded-xl text-xs font-bold text-neutral-darkgray transition-all cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting}
                    className="px-5 py-2.5 bg-brand text-white font-bold rounded-xl hover:bg-brand-dark transition-all cursor-pointer flex items-center gap-2 disabled:opacity-50 text-xs shadow-md shadow-brand/10"
                  >
                    {submitting ? 'Registering...' : 'Register Store'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </Layout>
  );
};
