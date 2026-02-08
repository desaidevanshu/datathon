import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, CartesianGrid } from 'recharts';
import { ArrowUp, ArrowDown, Zap, AlertTriangle, Clock, Activity, Cloud } from 'lucide-react';
import clsx from 'clsx';
import { useRef, useEffect, useState } from 'react';
import maplibregl from 'maplibre-gl';
import { useNavigate } from 'react-router-dom';
import { Map as MapIcon } from 'lucide-react';
import AuthButton from '../components/AuthButton';

const StatCard = ({ title, value, subtext, trend, icon: Icon, color }) => (
    <div className="bg-gray-900/50 backdrop-blur-sm border border-gray-800/50 p-5 rounded-2xl hover:border-gray-700 transition-all group">
        <div className="flex justify-between items-start mb-4">
            <div className={clsx("p-3 rounded-xl bg-opacity-10", `bg-${color}-500`)}>
                <Icon className={clsx("w-6 h-6", `text-${color}-500`)} />
            </div>
            {trend && (
                <div className={clsx("flex items-center gap-1 text-xs font-medium px-2 py-1 rounded-full bg-opacity-10", trend > 0 ? "bg-green-500 text-green-400" : "bg-red-500 text-red-400")}>
                    {trend > 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                    {Math.abs(trend)}%
                </div>
            )}
        </div>
        <h3 className="text-gray-400 text-sm font-medium mb-1">{title}</h3>
        <p className="text-2xl font-bold text-gray-100">{value}</p>
        {subtext && <p className="text-xs text-gray-500 mt-2">{subtext}</p>}
    </div>
);

const MiniMap = () => {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const navigate = useNavigate();

    useEffect(() => {
        if (map.current) return;

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: {
                version: 8,
                sources: {
                    'osm': {
                        type: 'raster',
                        tiles: [
                            'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
                            'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
                            'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
                        ],
                        tileSize: 256,
                        attribution: '&copy; OpenStreetMap Contributors',
                        maxzoom: 19
                    }
                },
                layers: [{
                    id: 'osm',
                    type: 'raster',
                    source: 'osm',
                    minzoom: 0,
                    maxzoom: 19,
                    paint: { 'raster-fade-duration': 0 }
                }]
            },
            center: [72.8777, 19.0760],
            zoom: 11,
            maxZoom: 19,
            minZoom: 0,
            interactive: false
        });

        // Add click handler to navigate to full map
        map.current.on('click', () => {
            navigate('/map');
        });

    }, []);

    return (
        <div className="relative w-full h-full rounded-2xl overflow-hidden cursor-pointer group" onClick={() => navigate('/map')}>
            <div ref={mapContainer} className="absolute inset-0 z-0 opacity-40 transition-all duration-500 group-hover:scale-110" />
            <div className="absolute inset-0 bg-gradient-to-t from-gray-900 via-transparent to-transparent opacity-80" />
            <div className="absolute bottom-4 left-4 z-10">
                <h4 className="text-white font-bold text-lg flex items-center gap-2">
                    <MapIcon className="w-5 h-5 text-cyan-400" />
                    Live Traffic Map
                </h4>
                <p className="text-gray-300 text-xs">Click to view real-time congestion</p>
            </div>
        </div>
    );
}

const Dashboard = () => {
    const [prediction, setPrediction] = useState(null);
    const [loading, setLoading] = useState(true);

    // Initial Mock Trend (will be replaced or augmented by real data ideally)
    const [trendData, setTrendData] = useState([
        { time: '06:00', speed: 85, congestion: 10 },
        { time: '09:00', speed: 25, congestion: 85 },
        { time: '12:00', speed: 45, congestion: 50 },
        { time: '15:00', speed: 55, congestion: 40 },
        { time: '18:00', speed: 20, congestion: 95 },
        { time: '21:00', speed: 70, congestion: 20 },
    ]);

    useEffect(() => {
        const fetchPrediction = async () => {
            try {
                // Fetch from our local backend (Port 8002)
                const response = await axios.get('http://localhost:8005/api/predict?city=Mumbai');
                const data = await response.data;
                setPrediction(data);

                if (data.forecast) {
                    const futureTrends = data.forecast.map(f => ({
                        time: `${f.hour}:00`,
                        congestion: f.congestion_level === 'High' ? 90 : f.congestion_level === 'Medium' ? 60 : 30,
                        speed: f.congestion_level === 'High' ? 20 : f.congestion_level === 'Medium' ? 40 : 80
                    }));
                    setTrendData(futureTrends);
                }
            } catch (error) {
                console.error("Failed to fetch prediction:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchPrediction();
        // Poll every 30 seconds
        const interval = setInterval(fetchPrediction, 30000);
        return () => clearInterval(interval);
    }, []);

    if (loading) return <div className="p-10 text-white">Loading Intelligence Engine...</div>;

    const pred = prediction?.prediction || {};
    const ctx = prediction?.context || {};
    const live = prediction?.live_data || {};
    const analysis = prediction?.analysis || {};
    const forecasts = prediction?.forecast || [];
    const futureBottleneck = forecasts.find(f => f.is_bottleneck);

    return (
        <div className="p-6 lg:p-10 max-w-[1600px] mx-auto space-y-8">
            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <div className="flex items-center gap-2 mb-2">
                        <h1 className="text-3xl font-bold text-white">Mumbai Traffic Overview</h1>
                        {analysis.unique_insight && (
                            <span className="bg-purple-500/20 text-purple-400 text-xs font-bold px-2 py-1 rounded-full border border-purple-500/50 animate-pulse">
                                UNIQUE INSIGHT DETECTED
                            </span>
                        )}
                        {futureBottleneck && (
                            <span className="bg-red-500/20 text-red-400 text-xs font-bold px-2 py-1 rounded-full border border-red-500/50 animate-pulse flex items-center gap-1">
                                <AlertTriangle className="w-3 h-3" />
                                FUTURE BOTTLENECK: +{futureBottleneck.step}
                            </span>
                        )}
                    </div>
                    <p className="text-gray-400">
                        Real-time analysis: <span className="text-cyan-400">{ctx.weather?.Condition || 'Clear'}</span> •
                        Events: <span className="text-yellow-400">{ctx.events?.Details?.Name || 'None'}</span>
                    </p>
                </div>
                <div className="flex gap-3">
                    <AuthButton />
                    <button onClick={() => window.location.reload()} className="bg-gray-800 hover:bg-gray-700 text-gray-300 font-medium rounded-lg text-sm px-4 py-2 transition-all">
                        Refresh Data
                    </button>
                </div>
            </div>

            {/* AI Traffic Bulletin */}
            {prediction?.traffic_bulletin && (
                <div className="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 border border-cyan-500/30 rounded-2xl p-6 backdrop-blur-sm">
                    <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                            <Activity className="w-6 h-6 text-cyan-400" />
                        </div>
                        <div className="flex-1">
                            <div className="flex items-center gap-2 mb-2">
                                <h3 className="text-lg font-bold text-white">Traffic News Anchor</h3>
                                <span className="px-2 py-0.5 bg-cyan-500/20 text-cyan-400 text-xs font-bold rounded-full border border-cyan-500/50">
                                    AI POWERED
                                </span>
                            </div>
                            <p className="text-gray-300 leading-relaxed">
                                {prediction.traffic_bulletin}
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Congestion Level"
                    value={pred.congestion_level || "Loading..."}
                    subtext={analysis.insight_message}
                    trend={pred.congestion_level === '2' ? 15 : -5}
                    icon={Zap}
                    color={pred.congestion_level === '2' ? "red" : "green"}
                />
                <StatCard
                    title="Confidence Score"
                    value={`${pred.confidence_score || 0}%`}
                    subtext=" AI Certainty Metric"
                    trend={2}
                    icon={Activity}
                    color="blue"
                />
                <StatCard
                    title="Avg Traffic Speed"
                    value={`${live.current_speed || 0} km/h`}
                    subtext={`Volume: ${live.current_volume || 0} vehicles`}
                    trend={live.current_speed < 30 ? -10 : 5}
                    icon={Clock}
                    color="yellow"
                />
                <StatCard
                    title="Novelty Score"
                    value={pred.novelty_score || 0}
                    subtext={pred.novelty_score > 0.6 ? "High Anomaly Detected" : "Stable Pattern"}
                    trend={pred.novelty_score > 0.5 ? 10 : -2}
                    icon={Cloud}
                    color="purple"
                />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
                {/* Charts Area */}
                <div className="lg:col-span-2 bg-gray-900/50 border border-gray-800/50 rounded-2xl p-6 flex flex-col">
                    <h3 className="text-lg font-bold text-white mb-6">
                        Traffic Forecast (Next 3 Hours)
                        {futureBottleneck && <span className="text-red-400 text-sm ml-2">- Bottleneck Likely at {futureBottleneck.hour}:00</span>}
                    </h3>
                    <div className="flex-1 w-full min-h-0">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={trendData}>
                                <defs>
                                    <linearGradient id="colorCongestion" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                                    </linearGradient>
                                    <linearGradient id="colorSpeed" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                                <XAxis dataKey="time" stroke="#9ca3af" axisLine={false} tickLine={false} />
                                <YAxis stroke="#9ca3af" axisLine={false} tickLine={false} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#111827', border: '1px solid #374151', borderRadius: '8px' }}
                                    itemStyle={{ color: '#e5e7eb' }}
                                />
                                <Area type="monotone" dataKey="congestion" stroke="#ef4444" strokeWidth={3} fillOpacity={1} fill="url(#colorCongestion)" name="Congestion %" />
                                <Area type="monotone" dataKey="speed" stroke="#06b6d4" strokeWidth={3} fillOpacity={1} fill="url(#colorSpeed)" name="Avg Speed (km/h)" />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Map Preview */}
                <div className="bg-gray-900/50 border border-gray-800/50 rounded-2xl p-1 relative overflow-hidden">
                    <MiniMap />
                </div>
            </div>
        </div>
    )
}

export default Dashboard;
