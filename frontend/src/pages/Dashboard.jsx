import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, AreaChart, Area, CartesianGrid } from 'recharts';
import { ArrowUp, ArrowDown, Zap, AlertTriangle, Clock } from 'lucide-react';
import clsx from 'clsx';
import { useRef, useEffect } from 'react';
import maplibregl from 'maplibre-gl';
import { useNavigate } from 'react-router-dom';

const mockTrendData = [
    { time: '06:00', speed: 85, congestion: 10 },
    { time: '09:00', speed: 25, congestion: 85 }, // Morning Rush
    { time: '12:00', speed: 45, congestion: 50 },
    { time: '15:00', speed: 55, congestion: 40 },
    { time: '18:00', speed: 20, congestion: 95 }, // Evening Rush
    { time: '21:00', speed: 70, congestion: 20 },
];

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
                        tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
                        tileSize: 256,
                        attribution: '&copy; OpenStreetMap Contributors',
                    }
                },
                layers: [{
                    id: 'osm',
                    type: 'raster',
                    source: 'osm',
                    paint: {
                        'raster-saturation': 0,
                        'raster-contrast': 0
                    } // Full color
                }]
            },
            center: [72.8777, 19.0760], // Mumbai
            zoom: 11,
            interactive: false // Static preview
        });

        // Add click handler to navigate to full map
        map.current.on('click', () => {
            navigate('/map');
        });

    }, []);

    return (
        <div className="relative w-full h-full rounded-2xl overflow-hidden cursor-pointer group" onClick={() => navigate('/map')}>
            {/* Mini Map Background - Full Color */}
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
import { Map as MapIcon } from 'lucide-react'; // Fix import

const Dashboard = () => {
    return (
        <div className="p-6 lg:p-10 max-w-[1600px] mx-auto space-y-8">
            {/* Header */}
            <div className="flex justify-between items-end">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">Mumbai Traffic Overview</h1>
                    <p className="text-gray-400">Real-time analysis and forecasting</p>
                </div>
                <div className="flex gap-3">
                    <select className="bg-gray-900 border border-gray-700 text-gray-300 text-sm rounded-lg focus:ring-cyan-500 focus:border-cyan-500 block p-2.5">
                        <option>Last 2 Weeks</option>
                        <option>Last 24 Hours</option>
                    </select>
                    <button className="bg-cyan-600 hover:bg-cyan-500 text-white font-medium rounded-lg text-sm px-5 py-2.5 transition-all shadow-lg shadow-cyan-500/20">
                        Export Report
                    </button>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard title="Avg Congestion Data" value="58%" subtext="High congestion alert in CBD" trend={-4} icon={Zap} color="cyan" />
                <StatCard title="Active Incidents" value="12" subtext="3 major accidents reported" trend={-12} icon={AlertTriangle} color="red" />
                <StatCard title="Avg Transit Delay" value="18 min" subtext="+3 min above baseline" trend={-2} icon={Clock} color="yellow" />
                <StatCard title="Traffic Health Score" value="72/100" subtext="Improving since morning rush" trend={5} icon={ArrowUp} color="green" />
            </div>

            {/* Main Content Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[500px]">
                {/* Charts Area */}
                <div className="lg:col-span-2 bg-gray-900/50 border border-gray-800/50 rounded-2xl p-6 flex flex-col">
                    <h3 className="text-lg font-bold text-white mb-6">Daily Congestion Trends</h3>
                    <div className="flex-1 w-full min-h-0">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={mockTrendData}>
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
