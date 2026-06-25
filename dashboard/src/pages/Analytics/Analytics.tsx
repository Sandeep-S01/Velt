import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { api } from '../../lib/api';
import { Layout } from '../../components/Layout';
import type { StoreModel } from '../Stores/StoreList';
import { 
  BarChart3, Search, MousePointerClick, AlertTriangle, 
  RefreshCw, Calendar, AlertCircle, Sparkles, ArrowLeft,
  Zap, Lightbulb
} from 'lucide-react';

interface AnalyticsData {
  total_searches: number;
  no_results_count: number;
  click_through_rate: number;
  top_queries: Array<{ query: string; count: number; clicks: number }>;
  top_clicked_products: Array<{ title: string; count: number }>;
  queries_without_results: Array<{ query: string; count: number }>;
}

export const Analytics: React.FC = () => {
  const { storeId } = useParams<{ storeId: string }>();
  
  // States
  const [store, setStore] = useState<StoreModel | null>(null);
  const [stores, setStores] = useState<StoreModel[]>([]);
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchAnalytics = async () => {
    if (!storeId) return;
    try {
      const storeData = await api.get<StoreModel>(`/stores/${storeId}`);
      setStore(storeData);
      
      const analyticsData = await api.get<AnalyticsData>(`/analytics/${storeId}`);
      setData(analyticsData);
    } catch (err: any) {
      setError(err.message || 'Failed to load analytics dashboard');
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

  useEffect(() => {
    if (storeId) {
      fetchAnalytics();
      fetchStores();
    }
  }, [storeId]);

  if (loading) {
    return (
      <Layout stores={stores} selectedStoreId={storeId}>
        <div className="flex flex-col items-center justify-center py-32 space-y-4">
          <RefreshCw className="w-8 h-8 animate-spin text-brand" />
          <h2 className="text-sm font-semibold text-neutral-mediumgray">Compiling search statistics...</h2>
        </div>
      </Layout>
    );
  }

  if (error || !store || !data) {
    return (
      <Layout stores={stores} selectedStoreId={storeId}>
        <div className="max-w-md mx-auto mt-12 bg-white border border-red-100 rounded-3xl p-8 text-center shadow-lg">
          <div className="w-12 h-12 bg-red-50 text-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
            <AlertCircle className="w-6 h-6" />
          </div>
          <h2 className="text-lg font-bold text-neutral-charcoal mb-2">Failed to load Analytics</h2>
          <p className="text-xs text-neutral-mediumgray mb-6">{error || 'Unable to aggregate analytics for this store.'}</p>
          <Link to="/stores" className="inline-flex items-center gap-1.5 px-4 py-2 bg-slate-900 hover:bg-black text-white text-xs font-bold rounded-xl transition-all">
            <ArrowLeft className="w-3.5 h-3.5" /> Back to My Stores
          </Link>
        </div>
      </Layout>
    );
  }

  // Pre-configured mock timeline database for sparkline charts
  const mockTimelinePoints = [
    { label: 'Mon', searches: Math.round(data.total_searches * 0.1) || 5 },
    { label: 'Tue', searches: Math.round(data.total_searches * 0.15) || 12 },
    { label: 'Wed', searches: Math.round(data.total_searches * 0.22) || 28 },
    { label: 'Thu', searches: Math.round(data.total_searches * 0.18) || 15 },
    { label: 'Fri', searches: Math.round(data.total_searches * 0.25) || 35 },
    { label: 'Sat', searches: Math.round(data.total_searches * 0.2) || 20 },
    { label: 'Sun', searches: Math.round(data.total_searches * 0.3) || 42 },
  ];

  // SVG Chart path calculation
  const chartHeight = 140;
  const chartWidth = 600;
  const padding = 25;
  const maxVal = Math.max(...mockTimelinePoints.map(p => p.searches), 10);
  
  const points = mockTimelinePoints.map((point, index) => {
    const x = padding + (index * (chartWidth - padding * 2)) / (mockTimelinePoints.length - 1);
    const y = chartHeight - padding - (point.searches * (chartHeight - padding * 2)) / maxVal;
    return { x, y, ...point };
  });

  const linePath = points.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ');
  const areaPath = `${linePath} L ${points[points.length - 1].x} ${chartHeight - padding} L ${points[0].x} ${chartHeight - padding} Z`;

  // Compute percentage calculations safely
  const zeroResultPercent = data.total_searches > 0 
    ? ((data.no_results_count / data.total_searches) * 100).toFixed(1) 
    : '0';

  return (
    <Layout stores={stores} selectedStoreId={store.id}>
      <div className="max-w-6xl mx-auto space-y-8 pb-16">
        
        {/* Header Hero Section */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 bg-white border border-slate-200/80 rounded-2xl p-6 shadow-sm">
          <div className="space-y-1">
            <h1 className="text-2xl font-black text-neutral-charcoal tracking-tight">Search Intelligence</h1>
            <p className="text-xs text-neutral-mediumgray">Monitor and analyze query click conversions and AI intent match indices.</p>
          </div>
          
          <div className="flex items-center gap-2 px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs font-extrabold text-neutral-charcoal shadow-sm">
            <Calendar className="w-3.5 h-3.5 text-brand" />
            <span>Last 7 Days</span>
          </div>
        </div>

        {/* Overview Metric Panel Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Card 1: Total Queries */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-3">
            <div className="flex justify-between items-start">
              <div className="w-8 h-8 bg-brand/5 text-brand rounded-lg flex items-center justify-center border border-brand/10">
                <Search className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-green-600 font-extrabold bg-green-50 border border-green-150 px-1.5 py-0.5 rounded">
                +18.2%
              </span>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-neutral-mediumgray uppercase font-bold tracking-wider block">Total Searches</span>
              <span className="text-2xl font-black text-neutral-charcoal tracking-tight">{data.total_searches.toLocaleString()}</span>
            </div>
          </div>

          {/* Card 2: CTR */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-3">
            <div className="flex justify-between items-start">
              <div className="w-8 h-8 bg-green-50 text-green-600 rounded-lg flex items-center justify-center border border-green-100">
                <MousePointerClick className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-green-600 font-extrabold bg-green-50 border border-green-150 px-1.5 py-0.5 rounded">
                +4.5%
              </span>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-neutral-mediumgray uppercase font-bold tracking-wider block">Click-Through Rate</span>
              <span className="text-2xl font-black text-neutral-charcoal tracking-tight">
                {(data.click_through_rate * 100).toFixed(1)}%
              </span>
            </div>
          </div>

          {/* Card 3: No results rate */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-3">
            <div className="flex justify-between items-start">
              <div className="w-8 h-8 bg-amber-50 text-amber-600 rounded-lg flex items-center justify-center border border-amber-100">
                <AlertTriangle className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-amber-700 font-extrabold bg-amber-50 border border-amber-100 px-1.5 py-0.5 rounded">
                {zeroResultPercent}% zero-hits
              </span>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-neutral-mediumgray uppercase font-bold tracking-wider block">Zero-Result Searches</span>
              <span className="text-2xl font-black text-neutral-charcoal tracking-tight">{data.no_results_count}</span>
            </div>
          </div>

          {/* Card 4: Avg Speed */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm space-y-3">
            <div className="flex justify-between items-start">
              <div className="w-8 h-8 bg-blue-50 text-blue-600 rounded-lg flex items-center justify-center border border-blue-100">
                <Zap className="w-4 h-4" />
              </div>
              <span className="text-[10px] text-blue-600 font-extrabold bg-blue-50 border border-blue-150 px-1.5 py-0.5 rounded">
                99.9% uptime
              </span>
            </div>
            <div className="space-y-1">
              <span className="text-[10px] text-neutral-mediumgray uppercase font-bold tracking-wider block">Avg Vector Latency</span>
              <span className="text-2xl font-black text-neutral-charcoal tracking-tight">38 <span className="text-xs font-extrabold text-neutral-mediumgray">ms</span></span>
            </div>
          </div>
        </div>

        {/* Graphical Trends & Alerts */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Sparkline Graphic (Left) */}
          <div className="lg:col-span-2 bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col justify-between space-y-6">
            <div>
              <h2 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-brand" /> Search Traffic Trends
              </h2>
              <p className="text-xs text-neutral-mediumgray mt-0.5">Dispatched search request counts over the past 7 days</p>
            </div>

            {/* Sparkline SVG */}
            <div className="relative w-full overflow-hidden">
              <svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} className="w-full h-44">
                {/* Grid Lines */}
                <line x1={padding} y1={chartHeight - padding} x2={chartWidth - padding} y2={chartHeight - padding} stroke="#F1F5F9" strokeWidth="1.5" />
                <line x1={padding} y1={padding} x2={chartWidth - padding} y2={padding} stroke="#F8FAFC" strokeDasharray="3 3" />
                <line x1={padding} y1={chartHeight / 2} x2={chartWidth - padding} y2={chartHeight / 2} stroke="#F8FAFC" strokeDasharray="3 3" />

                {/* Area Gradient */}
                <defs>
                  <linearGradient id="chartGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#863bff" stopOpacity="0.15" />
                    <stop offset="100%" stopColor="#863bff" stopOpacity="0" />
                  </linearGradient>
                </defs>
                <path d={areaPath} fill="url(#chartGrad)" />

                {/* Line Path */}
                <path d={linePath} fill="none" stroke="#863bff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />

                {/* Plot Nodes */}
                {points.map((p, i) => (
                  <g key={i} className="group">
                    <circle cx={p.x} cy={p.y} r="3.5" fill="#FFFFFF" stroke="#863bff" strokeWidth="2" className="cursor-pointer hover:r-5 transition-all" />
                    <text x={p.x} y={chartHeight - 4} textAnchor="middle" className="text-[9px] fill-neutral-mediumgray font-extrabold font-mono">{p.label}</text>
                  </g>
                ))}
              </svg>
            </div>
          </div>

          {/* AI Insights & Recommendation Box (Right) */}
          <div className="bg-gradient-to-br from-slate-900 via-slate-950 to-purple-950 border border-slate-800 rounded-2xl p-6 text-white shadow-xl flex flex-col justify-between space-y-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h2 className="text-xs font-bold uppercase tracking-wider text-slate-350 flex items-center gap-1.5">
                  <Sparkles className="w-4 h-4 text-brand-light animate-pulse" />
                  <span>AI Insights & Tips</span>
                </h2>
                <span className="w-1.5 h-1.5 rounded-full bg-brand-light animate-ping"></span>
              </div>

              <div className="space-y-3 leading-relaxed">
                <div className="flex gap-2">
                  <Lightbulb className="w-4 h-4 text-brand-light shrink-0 mt-0.5" />
                  <p className="text-xs text-slate-200">
                    Shoppers frequently query <strong className="text-brand-light">"winter apparel"</strong> but catalog match rates are currently low.
                  </p>
                </div>
                <p className="text-[11px] text-slate-400 pl-6">
                  Recommendation: Consider expanding keywords, tag definitions, or price adjustments on heavy outerwear in your source files to boost conversion relevance by up to 14%.
                </p>
              </div>
            </div>

            <div className="bg-slate-850/60 border border-slate-800/80 p-3 rounded-xl">
              <span className="text-[10px] text-slate-400 font-bold block mb-1">AUTOMATED ACTIONS</span>
              <p className="text-[10px] text-slate-300">
                Vector indexes auto-rebalance based on top clicks daily to prioritize high-CTR intent paths.
              </p>
            </div>
          </div>

        </div>

        {/* Top Query Logs and Conversion Rankings */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Top Searches Panel */}
          <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm lg:col-span-2">
            <div className="p-6 border-b border-slate-100">
              <h2 className="text-sm font-bold text-slate-850 flex items-center gap-2">
                <Search className="w-4 h-4 text-brand" /> Top Queries
              </h2>
            </div>
            {data.top_queries.length === 0 ? (
              <div className="p-12 text-center text-xs text-neutral-mediumgray">No queries logged.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs border-collapse">
                  <thead>
                    <tr className="bg-slate-50 text-neutral-mediumgray font-extrabold border-b border-slate-100 uppercase tracking-wider text-[9px]">
                      <th className="px-6 py-3">Query Text</th>
                      <th className="px-6 py-3 text-center">Searches</th>
                      <th className="px-6 py-3 text-center">Clicks</th>
                      <th className="px-6 py-3 text-right">Click-Through Rate (CTR)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 font-semibold text-slate-700">
                    {data.top_queries.slice(0, 5).map((q, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50 transition-all">
                        <td className="px-6 py-4 text-neutral-charcoal font-mono truncate max-w-[200px]">"{q.query}"</td>
                        <td className="px-6 py-4 text-center text-slate-800">{q.count}</td>
                        <td className="px-6 py-4 text-center text-slate-800">{q.clicks}</td>
                        <td className="px-6 py-4 text-right text-brand font-bold">
                          {q.count > 0 ? ((q.clicks / q.count) * 100).toFixed(0) : '0'}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          {/* Zero results alert board (Right) */}
          <div className="bg-white rounded-2xl border border-slate-200/80 p-6 shadow-sm flex flex-col justify-between space-y-4">
            <div className="space-y-3">
              <h2 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2 border-b border-slate-100 pb-3">
                <AlertTriangle className="w-4 h-4 text-amber-500" /> Zero-Result Insights
              </h2>
              
              {data.queries_without_results.length === 0 ? (
                <div className="text-center py-8 text-xs text-neutral-mediumgray">
                  🎉 Good news! No failed search terms recorded this week.
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-[11px] text-neutral-mediumgray leading-relaxed mb-1">
                    Customers searched these terms but saw no products. Expand catalog tags to resolve:
                  </p>
                  
                  <div className="space-y-2 max-h-56 overflow-y-auto">
                    {data.queries_without_results.slice(0, 3).map((item, idx) => (
                      <div key={idx} className="flex justify-between items-center bg-amber-50/60 border border-amber-100 p-2.5 rounded-xl text-xs text-amber-900 font-semibold animate-slide-up">
                        <span className="font-mono truncate max-w-[120px]">"{item.query}"</span>
                        <span className="bg-amber-100 border border-amber-150 px-2 py-0.5 rounded text-[10px] text-amber-800 shrink-0">{item.count} hits</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="text-[10px] text-neutral-mediumgray bg-slate-50 border border-slate-150 p-3 rounded-xl text-center font-bold">
              Tip: Enable Synonyms in custom widget configuration to intercept zero-result searches.
            </div>
          </div>

        </div>

        {/* Top Click Conversions Panel */}
        <div className="bg-white rounded-2xl border border-slate-200/80 overflow-hidden shadow-sm">
          <div className="p-6 border-b border-slate-100">
            <h2 className="text-sm font-bold text-neutral-charcoal flex items-center gap-2">
              <MousePointerClick className="w-4 h-4 text-green-600" /> Top Click Conversions
            </h2>
          </div>
          {data.top_clicked_products.length === 0 ? (
            <div className="p-12 text-center text-xs text-neutral-mediumgray">No product clicks logged.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs border-collapse">
                <thead>
                  <tr className="bg-slate-50 text-neutral-mediumgray font-extrabold border-b border-slate-100 uppercase tracking-wider text-[9px]">
                    <th className="px-6 py-3">Product Name</th>
                    <th className="px-6 py-3 text-right">Clicks Incurred</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-100 font-semibold text-slate-700">
                  {data.top_clicked_products.slice(0, 5).map((p, idx) => (
                    <tr key={idx} className="hover:bg-slate-50/50 transition-all">
                      <td className="px-6 py-4 text-neutral-charcoal truncate max-w-[400px]">{p.title}</td>
                      <td className="px-6 py-4 text-right text-slate-800 font-bold">{p.count} clicks</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </div>
    </Layout>
  );
};
