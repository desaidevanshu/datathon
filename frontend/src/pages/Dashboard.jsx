import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, BarChart, Bar, LineChart, Line } from 'recharts';
import { ArrowUp, ArrowDown, Zap, AlertTriangle, Clock, Map as MapIcon, Menu, Bell, Search, User, Filter, Layers, Navigation, Sun, Moon, Activity, Play } from 'lucide-react';
import clsx from 'clsx';
import { useRef, useEffect, useState } from 'react';
import maplibregl from 'maplibre-gl';
import 'maplibre-gl/dist/maplibre-gl.css';
import { useNavigate } from 'react-router-dom';
import AuthButton from '../components/AuthButton';

// Mock data removed - fetching from API


const GlassCard = ({ children, className }) => (
    <div className={clsx(
        "bg-black/40 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden shadow-2xl",
        className
    )}>
        {children}
    </div>
);

const StatItem = ({ label, value, unit, trend, color = "blue" }) => (
    <div className="flex flex-col">
        <span className="text-gray-400 text-xs uppercase tracking-wider mb-1">{label}</span>
        <div className="flex items-end gap-2">
            <span className="text-2xl font-bold text-white font-mono">{value}</span>
            <span className="text-xs text-gray-500 mb-1">{unit}</span>
        </div>
        {trend && (
            <div className={clsx("flex items-center gap-1 text-xs mt-1", trend > 0 ? "text-green-400" : "text-red-400")}>
                {trend > 0 ? <ArrowUp className="w-3 h-3" /> : <ArrowDown className="w-3 h-3" />}
                {Math.abs(trend)}%
            </div>
        )}
    </div>
);

const Dashboard = () => {
    const mapContainer = useRef(null);
    const map = useRef(null);
    const navigate = useNavigate();
    const [currentTime, setCurrentTime] = useState(new Date());

    // Clock
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);
    const [selectedRoute, setSelectedRoute] = useState(null);
    const [darkMode, setDarkMode] = useState(true); // Default to Dark Mode
    const [dashboardData, setDashboardData] = useState(null);
    const [loading, setLoading] = useState(true);

    // Fetch Dashboard Data
    useEffect(() => {
        const fetchPrediction = async () => {
            try {
                // Fetch from our local backend (Port 8005)
                const response = await fetch('https://datathon-w1z4.onrender.com/api/predict?city=Mumbai');
                if (response.ok) {
                    const data = await response.json();
                    setDashboardData(data);
                }
            } catch (error) {
                console.error("Failed to fetch prediction:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchPrediction();
        const interval = setInterval(fetchPrediction, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    // Use data or fallbacks
    const pred = dashboardData?.prediction || {};
    const live = dashboardData?.live_data || {};
    const analysis = dashboardData?.analysis || {};

    // Extract events from backend response (scraped news, marathons, road diversions, etc.)
    const eventsData = dashboardData?.context?.events?.Details?.Events || [];

    // Map backend data to dashboard stats format
    const stats = {
        congestion_level: pred.congestion_level || "Loading...",
        active_cars: live.current_volume || 0,
        avg_speed: live.current_speed || 0,
        incidents: eventsData.length
    };

    // Theme Styles
    const theme = {
        glass: darkMode ? "bg-black/60 backdrop-blur-xl border-white/10 text-white" : "bg-white/80 backdrop-blur-xl border-black/10 text-gray-900 shadow-xl",
        text: darkMode ? "text-gray-300" : "text-gray-600",
        textHead: darkMode ? "text-white" : "text-gray-900",
        accent: "text-cyan-400",
        icon: darkMode ? "text-cyan-400" : "text-blue-600",
        chartGrid: darkMode ? "#333" : "#e5e7eb",
        chartTooltip: darkMode ? "#1f2937" : "#ffffff",
    };

    // Background Map Initialization
    useEffect(() => {
        console.log("Map Effect Running");
        if (map.current) return; // Initialize only once

        try {
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
                            'raster-fade-duration': 0
                        }
                    }]
                },
                center: [72.8777, 19.0760], // Mumbai
                zoom: 12.5,
                pitch: 45, // 3D perspective
                bearing: -17.6,
                interactive: true // Allow panning background
            });

            // Resize handler to ensure map renders correctly
            const resizeMap = () => { if (map.current) map.current.resize(); };
            setTimeout(resizeMap, 500);
            window.addEventListener('resize', resizeMap);
        } catch (e) {
            console.error("Map Error:", e);
        }
    }, []);

    const trafficData = (dashboardData?.forecast || []).map(f => ({
        time: `${f.hour}:00`,
        congestion: f.congestion_level === 'High' ? 90 : f.congestion_level === 'Medium' ? 60 : 30,
        prediction: (f.congestion_level === 'High' ? 90 : f.congestion_level === 'Medium' ? 60 : 30) * (1 + (Math.random() - 0.5) * 0.2) // Mock prediction
    }));

    return (
        <div className={`relative w-full h-full overflow-hidden font-sans transition-colors duration-500 ${darkMode ? 'text-gray-200' : 'text-gray-900'}`}>
            {/* Background Map - Full Visibility & Interactive */}
            <div
                className="absolute inset-0 z-0 cursor-pointer group"
                onClick={() => navigate('/dashboard/map')}
                title="Click to open Live Map"
            >
                {/* 
                  Dark Mode: Invert + Grayscale
                  Light Mode: No filter (Standard OSM)
                */}
                <div
                    ref={mapContainer}
                    className={`absolute inset-0 z-0 transition-all duration-700 ${darkMode ? 'opacity-50 grayscale invert' : 'opacity-100'}`}
                />

                {/* Subtle overlay */}
                <div className={`absolute inset-0 pointer-events-none transition-colors duration-500 ${darkMode ? 'bg-transparent group-hover:bg-black/5' : 'bg-white/10 group-hover:bg-white/0'}`} />
            </div>

            {/* UI Overlay Container */}
            <div className="relative z-10 p-6 pl-20 h-full flex flex-col pointer-events-none text-left">

                {/* Top Header Bar */}
                <header className="flex justify-between items-center mb-6 pointer-events-auto">
                    <div className="flex items-center gap-4">
                        <div className={`h-10 w-1 bg-gradient-to-b ${darkMode ? 'from-cyan-400 to-blue-600' : 'from-blue-600 to-cyan-400'} rounded-full`} />
                        <h1 className={`text-2xl font-bold tracking-tight ${theme.textHead}`}>
                            CITY<span className={theme.icon}>BRAIN</span>
                        </h1>
                    </div>

                    <div className="flex items-center gap-4">
                        <AuthButton />
                        {/* Theme Toggle */}
                        <button
                            onClick={() => setDarkMode(!darkMode)}
                            className={`p-2 rounded-full transition-all duration-300 ${darkMode ? 'bg-white/10 hover:bg-white/20 text-yellow-300' : 'bg-black/5 hover:bg-black/10 text-orange-500 shadow-sm'}`}
                            title="Toggle Theme"
                        >
                            {darkMode ? <Sun size={20} /> : <Moon size={20} />}
                        </button>

                        <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border ${darkMode ? 'bg-black/40 border-green-500/30 text-green-400' : 'bg-white/80 border-green-200 text-green-700 shadow-sm'}`}>
                            <span className="relative flex h-2 w-2">
                                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                            </span>
                            <span className="text-xs font-bold tracking-wide">System Online</span>
                        </div>
                        <div className="text-right">
                            <div className={`text-2xl font-mono leading-none ${theme.textHead}`}>
                                {new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                            </div>
                            <div className={`text-xs font-medium ${theme.text}`}>
                                {new Date().toLocaleDateString()}
                            </div>
                        </div>
                        <div className={`h-10 w-10 rounded-full bg-gradient-to-tr ${darkMode ? 'from-cyan-500 to-blue-500' : 'from-blue-500 to-cyan-500'} shadow-lg ring-2 ${darkMode ? 'ring-black' : 'ring-white'}`} />
                    </div>
                </header>

                <div className="grid grid-cols-12 gap-6 flex-1 min-h-0">

                    {/* Left Column: Stats & Trends */}
                    <div className="col-span-12 lg:col-span-3 flex flex-col gap-6 min-h-0">
                        {/* District Traffic Card */}
                        <div className={`flex-1 rounded-3xl p-5 border flex flex-col pointer-events-auto ${theme.glass}`}>
                            <div className="flex justify-between items-start mb-4">
                                <div className="flex items-center gap-2">
                                    <div className={`p-2 rounded-xl ${darkMode ? 'bg-cyan-500/10' : 'bg-blue-50'}`}>
                                        <Activity size={18} className={theme.icon} />
                                    </div>
                                    <h3 className={`font-bold text-sm tracking-widest uppercase ${theme.accent}`}>District Traffic</h3>
                                </div>
                                <select className={`bg-transparent text-xs font-medium border rounded-lg px-2 py-1 outline-none cursor-pointer ${darkMode ? 'border-white/20 text-gray-300' : 'border-gray-300 text-gray-700'}`}>
                                    <option>Mumbai (All)</option>
                                    <option>Bandra</option>
                                    <option>Andheri</option>
                                </select>
                            </div>

                            <div className="grid grid-cols-2 gap-4 mb-6">
                                <div>
                                    <div className={`text-[10px] font-bold tracking-wider uppercase mb-1 ${theme.text}`}>Congestion</div>
                                    <div className={`text-2xl font-black ${theme.textHead}`}>
                                        {stats.congestion_level} <span className="text-xs font-medium text-gray-500 ml-1">LVL</span>
                                    </div>
                                    {/* Progress Bar */}
                                    <div className="w-full h-1.5 bg-gray-700/50 rounded-full mt-2 overflow-hidden">
                                        <div className="h-full bg-gradient-to-r from-green-400 via-yellow-400 to-red-500 w-[85%]" />
                                    </div>
                                </div>
                                <div>
                                    <div className={`text-[10px] font-bold tracking-wider uppercase mb-1 ${theme.text}`}>Active Cars</div>
                                    <div className={`text-2xl font-black ${theme.textHead}`}>
                                        {stats.active_cars.toLocaleString()} <span className="text-xs font-medium text-gray-500 ml-1">VOL</span>
                                    </div>
                                    <div className="text-xs font-bold text-red-400 mt-1 flex items-center gap-1">
                                        ↓ 5%
                                    </div>
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <div className={`text-[10px] font-bold tracking-wider uppercase mb-1 ${theme.text}`}>Avg Speed</div>
                                    <div className={`text-xl font-bold ${theme.textHead}`}>
                                        {stats.avg_speed} <span className="text-[10px] text-gray-500">KM/H</span>
                                    </div>
                                </div>
                                <div>
                                    <div className={`text-[10px] font-bold tracking-wider uppercase mb-1 ${theme.text}`}>Incidents</div>
                                    <div className={`text-xl font-bold ${theme.textHead}`}>
                                        {String(stats.incidents).padStart(2, '0')} <span className="text-[10px] text-gray-500">ACT</span>
                                    </div>
                                    <div className="text-[10px] font-bold text-green-400">↑ 2%</div>
                                </div>
                            </div>
                        </div>

                        {/* Predictive Trend Chart */}
                        <div className={`flex-[1.5] rounded-3xl p-5 border flex flex-col pointer-events-auto ${theme.glass}`}>
                            <div className="flex justify-between items-center mb-4">
                                <h3 className={`font-bold text-xs tracking-widest uppercase ${theme.text}`}>Predictive Trend (12h)</h3>
                            </div>
                            <div className="flex-1 w-full min-h-[150px]">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={trafficData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke={theme.chartGrid} vertical={false} />
                                        <XAxis
                                            dataKey="time"
                                            tick={{ fill: darkMode ? '#9ca3af' : '#6b7280', fontSize: 10 }}
                                            axisLine={false}
                                            tickLine={false}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: theme.chartTooltip,
                                                borderColor: darkMode ? '#374151' : '#e5e7eb',
                                                borderRadius: '8px',
                                                color: darkMode ? '#fff' : '#000'
                                            }}
                                            itemStyle={{ color: darkMode ? '#fff' : '#000' }}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="congestion"
                                            stroke="#22d3ee"
                                            strokeWidth={2}
                                            dot={false}
                                            activeDot={{ r: 4, fill: '#fff' }}
                                        />
                                        <Line
                                            type="monotone"
                                            dataKey="prediction"
                                            stroke="#ef4444"
                                            strokeWidth={2}
                                            strokeDasharray="4 4"
                                            dot={false}
                                        />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>

                    {/* Center: Clean Map View */}
                    <div className="col-span-12 lg:col-span-6 flex flex-col justify-end pointer-events-none">
                        {/* Live Feed removed as per request */}
                    </div>

                    {/* Right Column: Alerts & Actions */}
                    <div className="col-span-12 lg:col-span-3 flex flex-col gap-4 min-h-0 pointer-events-none">

                        {/* Search Bar */}
                        <div className={`relative pointer-events-auto group`}>
                            <div className={`absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none ${theme.text}`}>
                                <Search size={16} />
                            </div>
                            <input
                                type="text"
                                placeholder="Search junction or cameras..."
                                className={`w-full pl-10 pr-4 py-3 rounded-xl border text-sm font-medium outline-none focus:ring-2 transition-all ${darkMode
                                    ? 'bg-black/50 border-white/10 text-white placeholder-gray-500 focus:ring-cyan-500/50 focus:border-cyan-500'
                                    : 'bg-white/80 border-gray-200 text-gray-900 placeholder-gray-400 focus:ring-blue-500/50 focus:border-blue-500 shadow-sm'
                                    }`}
                            />
                        </div>

                        {/* Critical Alerts */}
                        <div className={`flex-1 rounded-3xl p-5 border overflow-hidden pointer-events-auto flex flex-col ${theme.glass}`}>
                            <div className="flex justify-between items-center mb-4">
                                <div className="flex items-center gap-2">
                                    <AlertTriangle size={16} className="text-red-500" />
                                    <h3 className="font-bold text-sm text-red-400 tracking-widest uppercase">Critical Alerts</h3>
                                </div>
                                <span className="bg-red-500/20 text-red-400 px-2 py-0.5 rounded text-[10px] font-bold">
                                    {((dashboardData?.alerts || []).length + eventsData.length)} New
                                </span>
                            </div>

                            <div className="space-y-3 overflow-y-auto pr-1 custom-scrollbar flex-1">
                                {/* Display Backend Alerts */}
                                {(dashboardData?.alerts || []).map((alert, i) => (
                                    <div key={`alert-${i}`} className={`p-3 rounded-xl border transition-colors cursor-pointer ${darkMode ? 'bg-white/5 border-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100 border-gray-200'}`}>
                                        <div className="flex justify-between items-start mb-1">
                                            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${alert.type === 'CRITICAL' ? 'bg-red-500 text-white' :
                                                alert.type === 'WARNING' ? 'bg-orange-500 text-white' : 'bg-blue-500 text-white'
                                                }`}>
                                                {alert.type}
                                            </span>
                                            <span className={`text-[10px] ${theme.text}`}>{alert.time}</span>
                                        </div>
                                        <div className={`text-sm font-bold mb-0.5 ${theme.textHead}`}>{alert.title}</div>
                                        <div className={`text-xs ${theme.text} line-clamp-2`}>{alert.desc}</div>
                                    </div>
                                ))}

                                {/* Display Scraped Events (Marathons, Road Diversions, etc.) */}
                                {eventsData.map((event, i) => (
                                    <div key={`event-${i}`} className={`p-3 rounded-xl border transition-colors cursor-pointer ${darkMode ? 'bg-white/5 border-white/5 hover:bg-white/10' : 'bg-gray-50 hover:bg-gray-100 border-gray-200'}`}>
                                        <div className="flex justify-between items-start mb-1">
                                            <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded ${event.Impact === 'High' ? 'bg-red-500 text-white' :
                                                event.Impact === 'Medium' ? 'bg-orange-500 text-white' : 'bg-blue-500 text-white'
                                                }`}>
                                                {event.Impact?.toUpperCase() || 'INFO'}
                                            </span>
                                            <span className={`text-[10px] ${theme.text}`}>{event.Time || 'Live'}</span>
                                        </div>
                                        <div className={`text-sm font-bold mb-0.5 ${theme.textHead}`}>{event.Name}</div>
                                        <div className={`text-xs ${theme.text} mb-2`}>{event.Location}</div>
                                        {event.AffectedAreas && event.AffectedAreas.length > 0 && (
                                            <div className={`text-[10px] ${theme.text} italic`}>
                                                Affected: {event.AffectedAreas.slice(0, 2).join(', ')}
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="grid grid-cols-2 gap-3 pointer-events-auto mt-auto">
                            <button className="bg-cyan-600 hover:bg-cyan-500 text-white p-4 rounded-2xl font-bold text-sm shadow-lg shadow-cyan-900/20 flex flex-col items-center gap-2 transition-all hover:scale-[1.02]">
                                <Navigation size={20} />
                                Deploy Drone
                            </button>
                            <button className={`p-4 rounded-2xl font-bold text-sm border flex flex-col items-center gap-2 transition-all hover:scale-[1.02] ${darkMode ? 'bg-black/40 border-white/10 text-gray-300 hover:bg-white/5' : 'bg-white border-gray-200 text-gray-700 hover:bg-gray-50 shadow-sm'}`}>
                                <Filter size={20} />
                                Filters
                            </button>
                        </div>
                    </div>
                </div>

                {/* Vehicle Distribution - Bottom Left floating */}
                <div className={`absolute bottom-6 left-20 w-80 rounded-3xl p-5 border pointer-events-auto ${theme.glass}`}>
                    <h3 className={`font-bold text-xs tracking-widest uppercase mb-3 ${theme.text}`}>Vehicle Distribution</h3>
                    <div className="space-y-3">
                        {[
                            { label: 'Cars', val: 40, color: 'bg-blue-500' },
                            { label: 'Transport', val: 30, color: 'bg-purple-500' },
                            { label: 'Micromobility', val: 20, color: 'bg-orange-500' }
                        ].map((item, i) => (
                            <div key={i}>
                                <div className="flex justify-between text-xs font-medium mb-1">
                                    <span className={theme.textHead}>{item.label}</span>
                                    <span className={theme.text}>{item.val}%</span>
                                </div>
                                <div className={`h-1.5 w-full rounded-full overflow-hidden ${darkMode ? 'bg-gray-700' : 'bg-gray-200'}`}>
                                    <div className={`h-full ${item.color}`} style={{ width: `${item.val}%` }} />
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Dashboard;
