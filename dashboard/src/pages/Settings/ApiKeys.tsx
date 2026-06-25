import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../lib/api';
import { Layout } from '../../components/Layout';
import type { StoreModel } from '../Stores/StoreList';
import { 
  Key, Plus, Trash2, ShieldCheck, AlertCircle, Copy, Check, Eye, EyeOff, 
  ArrowLeft, RefreshCw, Lock, Terminal
} from 'lucide-react';

interface APIKeyModel {
  id: number;
  key: string;
  name: string;
  is_active: boolean;
  created_at: string;
  last_used_at?: string;
}

export const ApiKeys: React.FC = () => {
  const { storeId } = useParams<{ storeId: string }>();
  
  // States
  const [store, setStore] = useState<StoreModel | null>(null);
  const [stores, setStores] = useState<StoreModel[]>([]);
  const [apiKeys, setApiKeys] = useState<APIKeyModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [keysLoading, setKeysLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  // Key Generation
  const [newKeyName, setNewKeyName] = useState('');
  const [newKeyEnv, setNewKeyEnv] = useState<'production' | 'development'>('production');
  const [creatingKey, setCreatingKey] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // UI States
  const [showKeys, setShowKeys] = useState<Record<number, boolean>>({});
  const [copiedText, setCopiedText] = useState<string | null>(null);

  const fetchStoreData = async () => {
    if (!storeId) return;
    try {
      const data = await api.get<StoreModel>(`/stores/${storeId}`);
      setStore(data);
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
      fetchApiKeys();
      fetchStores();
    }
  }, [storeId]);

  const handleGenerateKey = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKeyName.trim() || !storeId) return;

    setCreatingKey(true);
    try {
      // Create key on the backend
      const newKey = await api.post<APIKeyModel>(`/stores/${storeId}/keys`, {
        name: `${newKeyName} (${newKeyEnv})`,
        is_active: true
      });
      setApiKeys((prev) => [newKey, ...prev]);
      setNewKeyName('');
      setIsModalOpen(false);
    } catch (err: any) {
      alert(err.message || 'Failed to generate key');
    } finally {
      setCreatingKey(false);
    }
  };

  const handleRevokeKey = async (keyId: number) => {
    if (!confirm('Are you sure you want to revoke this API key? Apps using it will immediately lose access.') || !storeId) return;

    try {
      await api.delete(`/stores/${storeId}/keys/${keyId}`);
      setApiKeys((prev) => prev.filter((k) => k.id !== keyId));
    } catch (err: any) {
      alert(err.message || 'Failed to revoke key');
    }
  };

  const triggerCopy = (text: string, identifier: string) => {
    navigator.clipboard.writeText(text);
    setCopiedText(identifier);
    setTimeout(() => setCopiedText(null), 2000);
  };

  const toggleShowKey = (id: number) => {
    setShowKeys((prev) => ({ ...prev, [id]: !prev[id] }));
  };

  if (loading) {
    return (
      <Layout stores={stores} selectedStoreId={storeId}>
        <div className="flex flex-col items-center justify-center py-32 space-y-4">
          <RefreshCw className="w-8 h-8 animate-spin text-brand" />
          <h2 className="text-sm font-semibold text-neutral-mediumgray">Loading keys console...</h2>
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
          <h2 className="text-lg font-bold text-neutral-charcoal mb-2">Failed to load Storefront Keys</h2>
          <p className="text-xs text-neutral-mediumgray mb-6">{error || 'The requested storefront could not be located.'}</p>
          <Link to="/stores" className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-black text-white text-xs font-bold rounded-xl transition-all">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to My Stores
          </Link>
        </div>
      </Layout>
    );
  }
  const primaryApiKey = apiKeys[0]?.key || 'vt_live_pk_********************';

  return (
    <Layout stores={stores} selectedStoreId={store.id}>
      <div className="max-w-5xl mx-auto space-y-8 pb-16">
        
        {/* Header Hero Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm">
          <div className="space-y-1">
            <div className="flex items-center gap-2">
              <Link to={`/stores/${store.id}`} className="text-neutral-mediumgray hover:text-neutral-charcoal transition-all">
                <ArrowLeft className="w-4 h-4" />
              </Link>
              <span className="text-[10px] text-neutral-mediumgray uppercase font-bold tracking-wider">
                Developer Credentials Scope
              </span>
            </div>
            <h1 className="text-2xl font-black text-neutral-charcoal tracking-tight">API Key Manager</h1>
            <p className="text-xs text-neutral-mediumgray">Manage private access tokens to query Velt semantic search indices.</p>
          </div>

          <button
            onClick={() => setIsModalOpen(true)}
            className="px-4 py-2.5 bg-brand hover:bg-brand-dark text-white font-bold rounded-xl text-xs flex items-center gap-1.5 transition-all shadow-md shadow-brand/10 shrink-0 cursor-pointer"
          >
            <Plus className="w-4 h-4" /> Generate API Key
          </button>
        </div>

        {/* Credentials Table / Grid */}
        <div className="bg-white border border-slate-200/80 rounded-2xl overflow-hidden shadow-sm">
          <div className="p-6 border-b border-slate-100 flex items-center justify-between">
            <div className="space-y-1">
              <h2 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2">
                <Key className="w-4 h-4 text-brand" /> Active Private Keys
              </h2>
              <p className="text-xs text-neutral-mediumgray">Tokens that grant query access to your indexed store catalog database.</p>
            </div>
            
            <button
              onClick={fetchApiKeys}
              className="p-1.5 hover:bg-slate-50 border border-slate-200 rounded-lg text-neutral-mediumgray hover:text-slate-800 transition-all bg-white cursor-pointer"
              title="Refresh API Keys List"
            >
              <RefreshCw className="w-3.5 h-3.5" />
            </button>
          </div>

          {keysLoading ? (
            <div className="p-16 flex flex-col items-center justify-center space-y-2">
              <RefreshCw className="w-6 h-6 animate-spin text-brand" />
              <span className="text-xs text-neutral-mediumgray font-semibold">Fetching security credentials...</span>
            </div>
          ) : apiKeys.length === 0 ? (
            <div className="p-16 text-center">
              <Lock className="w-12 h-12 text-slate-350 mx-auto mb-4" />
              <h4 className="text-xs font-bold text-slate-800">No generated API keys</h4>
              <p className="text-[11px] text-neutral-mediumgray mt-1 max-w-sm mx-auto leading-relaxed">
                You haven't generated any private access keys for this storefront. Generate a key to begin integrating client search scripts.
              </p>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-neutral-mediumgray font-extrabold border-b border-slate-100 uppercase tracking-wider text-[9px]">
                    <th className="px-6 py-3">Key Name</th>
                    <th className="px-6 py-3">Private Token</th>
                    <th className="px-6 py-3">Created</th>
                    <th className="px-6 py-3">Last Used</th>
                    <th className="px-6 py-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-semibold text-slate-700">
                  {apiKeys.map((keyObj) => {
                    const isShown = showKeys[keyObj.id] || false;
                    const isEnvDev = keyObj.name.toLowerCase().includes('(development)') || keyObj.name.toLowerCase().includes('dev');
                    return (
                      <tr key={keyObj.id} className="hover:bg-slate-50/50 transition-all">
                        <td className="px-6 py-4 truncate max-w-[150px]">
                          <div className="space-y-1">
                            <span className="text-slate-800 font-bold block">{keyObj.name}</span>
                            <span className={`inline-block text-[9px] px-1.5 py-0.5 font-bold uppercase rounded border ${
                              isEnvDev 
                                ? 'bg-amber-50 text-amber-700 border-amber-150' 
                                : 'bg-green-50 text-green-700 border-green-150'
                            }`}>
                              {isEnvDev ? 'Development' : 'Production'}
                            </span>
                          </div>
                        </td>
                        <td className="px-6 py-4 font-mono text-[10.5px]">
                          <div className="flex items-center gap-2">
                            <div className="bg-slate-50 border border-slate-200/80 px-2 py-1 rounded text-slate-700 select-all overflow-x-auto max-w-xs md:max-w-sm">
                              {isShown ? keyObj.key : `vt_live_pk_${keyObj.key.slice(11, 15)}*******************`}
                            </div>
                            <button
                              onClick={() => toggleShowKey(keyObj.id)}
                              className="p-1 hover:bg-slate-150 rounded border border-slate-200 bg-white text-neutral-mediumgray hover:text-slate-800 transition-all cursor-pointer shrink-0"
                              title={isShown ? 'Hide Key' : 'Reveal Key'}
                            >
                              {isShown ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                            </button>
                            <button
                              onClick={() => triggerCopy(keyObj.key, `key-${keyObj.id}`)}
                              className="p-1 hover:bg-slate-150 rounded border border-slate-200 bg-white text-neutral-mediumgray hover:text-slate-800 transition-all cursor-pointer shrink-0"
                              title="Copy Key to Clipboard"
                            >
                              {copiedText === `key-${keyObj.id}` ? <Check className="w-3.5 h-3.5 text-green-600" /> : <Copy className="w-3.5 h-3.5" />}
                            </button>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-neutral-mediumgray">
                          {new Date(keyObj.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 text-neutral-mediumgray">
                          {keyObj.last_used_at ? new Date(keyObj.last_used_at).toLocaleDateString() : 'Never used'}
                        </td>
                        <td className="px-6 py-4 text-right">
                          <button
                            onClick={() => handleRevokeKey(keyObj.id)}
                            className="p-1.5 hover:bg-red-50 border border-transparent hover:border-red-100 text-neutral-mediumgray hover:text-red-600 rounded-lg transition-all cursor-pointer inline-flex items-center"
                            title="Revoke and delete API Key"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Security / Documentation Block Split */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 items-start">
          {/* Security Best Practices */}
          <div className="bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm space-y-4">
            <h3 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2">
              <ShieldCheck className="w-4.5 h-4.5 text-green-600" />
              <span>Velt Credentials Policy</span>
            </h3>
            
            <ul className="space-y-3 text-xs text-neutral-mediumgray leading-relaxed list-disc pl-4 font-semibold">
              <li>
                <strong>Client vs Server:</strong> Private keys (`vt_live_pk_...`) carry read and write permissions to index databases. Ensure they are masked inside server architectures.
              </li>
              <li>
                <strong>Revocation Warning:</strong> Revoking a key deletes it from active routers immediately. Connected storefront widgets using deleted keys will fail queries.
              </li>
              <li>
                <strong>Token Rotation:</strong> We advise rotating keys every 90 days in critical production stores.
              </li>
            </ul>
          </div>

          {/* Quick cURL lookup */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 text-slate-100 shadow-xl space-y-3 relative overflow-hidden">
            <div className="absolute right-0 top-0 w-24 h-24 bg-brand/5 rounded-full blur-xl"></div>
            
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-350 flex items-center gap-1.5">
              <Terminal className="w-4 h-4 text-brand-light" />
              <span>cURL Query Sandbox</span>
            </h3>
            
            <p className="text-[11px] text-slate-400 leading-relaxed">
              Verify vector query operations on your catalog indices directly via cURL:
            </p>
            
            <div className="relative group">
              <button
                onClick={() => triggerCopy(`curl -X POST http://localhost:8000/v1/search \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: ${primaryApiKey}" \\
  -d '{"query": "summer apparel", "store_id": "${store.id}"}'`, 'curl')}
                className="absolute right-2 top-2 p-1 bg-slate-800 hover:bg-slate-700 rounded text-slate-350 hover:text-white border border-slate-700/60 transition-all cursor-pointer"
              >
                {copiedText === 'curl' ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
              </button>
              <pre className="bg-black/50 border border-slate-800 rounded-xl p-3.5 font-mono text-[9.5px] text-slate-300 overflow-x-auto select-all leading-relaxed">
{`curl -X POST http://localhost:8000/v1/search \\
  -H "Content-Type: application/json" \\
  -H "X-API-Key: ${primaryApiKey}" \\
  -d '{"query": "summer apparel", "store_id": "${store.id}"}'`}
              </pre>
            </div>
          </div>
        </div>

        {/* Create API Key Modal Overlay */}
        {isModalOpen && (
          <div className="fixed inset-0 bg-neutral-charcoal/30 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-white rounded-3xl max-w-md w-full shadow-2xl border border-slate-200/80 overflow-hidden animate-slide-up">
              
              {/* Modal Header */}
              <div className="px-6 py-4.5 border-b border-slate-100 flex items-center gap-2">
                <Key className="w-4.5 h-4.5 text-brand" />
                <h3 className="font-extrabold text-neutral-charcoal text-base">Generate Developer Key</h3>
              </div>

              {/* Form body */}
              <form onSubmit={handleGenerateKey} className="p-6 space-y-5">
                <div className="space-y-2">
                  <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                    Key Name / Identifier
                  </label>
                  <input
                    type="text"
                    required
                    value={newKeyName}
                    onChange={(e) => setNewKeyName(e.target.value)}
                    className="block w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-neutral-charcoal text-sm font-semibold focus:outline-none focus:border-brand focus:ring-4 focus:ring-brand/10 transition-all animate-slide-up"
                    placeholder="e.g. Production Mobile SDK"
                  />
                </div>

                <div className="space-y-2">
                  <label className="block text-[10px] font-bold text-neutral-mediumgray uppercase tracking-wider">
                    Scope Environment
                  </label>
                  <select
                    value={newKeyEnv}
                    onChange={(e) => setNewKeyEnv(e.target.value as any)}
                    className="block w-full px-4 py-3 bg-white border border-slate-200 rounded-xl text-neutral-charcoal text-sm font-semibold focus:outline-none focus:border-brand focus:ring-4 focus:ring-brand/10 transition-all cursor-pointer"
                  >
                    <option value="production">Production Environment</option>
                    <option value="development">Development Sandbox</option>
                  </select>
                </div>

                <div className="flex justify-end gap-2.5 pt-4 border-t border-slate-100">
                  <button
                    type="button"
                    onClick={() => setIsModalOpen(false)}
                    className="px-4 py-2.5 border border-slate-200 hover:bg-slate-50 rounded-xl text-xs font-bold text-neutral-darkgray transition-all cursor-pointer"
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={creatingKey}
                    className="px-5 py-2.5 bg-brand text-white font-bold rounded-xl hover:bg-brand-dark transition-all cursor-pointer flex items-center gap-1.5 disabled:opacity-50 text-xs shadow-md shadow-brand/10"
                  >
                    {creatingKey ? 'Generating...' : 'Create Key'}
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
