import React, { useState, useEffect } from 'react';
import { AlertTriangle, Shield, CloudRain, Info, CheckCircle, Clock, Calendar, Filter } from 'lucide-react';

const Alerts = () => {
    const [dashboardData, setDashboardData] = useState(null);
    const [timeFilter, setTimeFilter] = useState('24h'); // '24h' or '7d'
    const [loading, setLoading] = useState(true);

    // Fetch data from backend
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch('http://localhost:8005/api/predict?city=Mumbai');
                if (response.ok) {
                    const data = await response.json();
                    setDashboardData(data);
                }
            } catch (error) {
                console.error("Failed to fetch alerts:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    // Extract events and alerts from backend
    const eventsData = dashboardData?.context?.events?.Details?.Events || [];
    const alertsData = dashboardData?.alerts || [];

    // Combine alerts and events
    const allAlerts = [
        ...alertsData.map(alert => ({
            id: `alert-${alert.title}`,
            type: alert.type || 'INFO',
            title: alert.title,
            desc: alert.desc,
            time: alert.time || 'Just now',
            source: 'System',
            timestamp: new Date() // Mock timestamp
        })),
        ...eventsData.map(event => ({
            id: `event-${event.Name}`,
            type: event.Impact || 'INFO',
            title: event.Name,
            desc: `Location: ${event.Location}${event.AffectedAreas?.length ? ` | Affected: ${event.AffectedAreas.join(', ')}` : ''}`,
            time: event.Time || 'Live',
            source: event.Source || 'News',
            timestamp: new Date() // Mock timestamp
        }))
    ];

    // Filter by time
    const filteredAlerts = allAlerts.filter(alert => {
        // For demo purposes, show all alerts
        // In production, you'd filter by actual timestamp
        return true;
    });

    // Get icon based on type
    const getIcon = (type) => {
        const typeUpper = type?.toUpperCase();
        if (typeUpper === 'CRITICAL' || typeUpper === 'HIGH') {
            return <AlertTriangle className="text-red-500" />;
        } else if (typeUpper === 'WARNING' || typeUpper === 'MEDIUM') {
            return <Info className="text-orange-500" />;
        } else if (typeUpper === 'WEATHER') {
            return <CloudRain className="text-blue-400" />;
        } else if (typeUpper === 'SUCCESS') {
            return <CheckCircle className="text-green-500" />;
        } else {
            return <Shield className="text-gray-400" />;
        }
    };

    // Get color based on type
    const getColor = (type) => {
        const typeUpper = type?.toUpperCase();
        if (typeUpper === 'CRITICAL' || typeUpper === 'HIGH') {
            return 'border-l-4 border-red-500 bg-red-500/10';
        } else if (typeUpper === 'WARNING' || typeUpper === 'MEDIUM') {
            return 'border-l-4 border-orange-500 bg-orange-500/10';
        } else if (typeUpper === 'WEATHER') {
            return 'border-l-4 border-blue-500 bg-blue-500/10';
        } else if (typeUpper === 'SUCCESS') {
            return 'border-l-4 border-green-500 bg-green-500/10';
        } else {
            return 'border-l-4 border-gray-500 bg-gray-500/10';
        }
    };

    return (
        <div className="p-6 md:p-10 min-h-screen text-gray-100">
            <div className="flex justify-between items-start mb-8">
                <div>
                    <h1 className="text-3xl font-bold mb-2">System Alerts & Events</h1>
                    <p className="text-gray-400">Real-time notifications, incidents, and scraped news across Mumbai.</p>
                </div>

                {/* Time Filter Buttons */}
                <div className="flex gap-2">
                    <button
                        onClick={() => setTimeFilter('24h')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${timeFilter === '24h'
                                ? 'bg-cyan-600 text-white shadow-lg'
                                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                            }`}
                    >
                        <Clock size={16} />
                        24 Hours
                    </button>
                    <button
                        onClick={() => setTimeFilter('7d')}
                        className={`flex items-center gap-2 px-4 py-2 rounded-lg font-semibold text-sm transition-all ${timeFilter === '7d'
                                ? 'bg-cyan-600 text-white shadow-lg'
                                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                            }`}
                    >
                        <Calendar size={16} />
                        7 Days
                    </button>
                </div>
            </div>

            {/* Stats Summary */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="bg-gray-900 border border-white/5 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-red-500/20 rounded-lg">
                            <AlertTriangle className="text-red-500" size={20} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold">{filteredAlerts.filter(a => a.type?.toUpperCase() === 'CRITICAL' || a.type?.toUpperCase() === 'HIGH').length}</div>
                            <div className="text-xs text-gray-400">Critical Alerts</div>
                        </div>
                    </div>
                </div>
                <div className="bg-gray-900 border border-white/5 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-orange-500/20 rounded-lg">
                            <Info className="text-orange-500" size={20} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold">{filteredAlerts.filter(a => a.type?.toUpperCase() === 'WARNING' || a.type?.toUpperCase() === 'MEDIUM').length}</div>
                            <div className="text-xs text-gray-400">Warnings</div>
                        </div>
                    </div>
                </div>
                <div className="bg-gray-900 border border-white/5 rounded-lg p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-blue-500/20 rounded-lg">
                            <Filter className="text-blue-500" size={20} />
                        </div>
                        <div>
                            <div className="text-2xl font-bold">{filteredAlerts.length}</div>
                            <div className="text-xs text-gray-400">Total Events</div>
                        </div>
                    </div>
                </div>
            </div>

            {/* Alerts List */}
            {loading ? (
                <div className="text-center py-12">
                    <div className="text-gray-400">Loading alerts...</div>
                </div>
            ) : (
                <div className="space-y-4 max-w-4xl">
                    {filteredAlerts.length === 0 ? (
                        <div className="text-center py-12 bg-gray-900 rounded-lg border border-white/5">
                            <Shield className="mx-auto mb-4 text-gray-600" size={48} />
                            <p className="text-gray-400">No alerts for the selected time period</p>
                        </div>
                    ) : (
                        filteredAlerts.map(alert => (
                            <div key={alert.id} className={`p-4 rounded-lg bg-gray-900 border border-white/5 flex gap-4 items-start hover:bg-gray-800 transition-colors ${getColor(alert.type)}`}>
                                <div className="mt-1 p-2 bg-black/20 rounded-full">
                                    {getIcon(alert.type)}
                                </div>
                                <div className="flex-1">
                                    <div className="flex justify-between items-start">
                                        <h3 className="font-bold text-lg">{alert.title}</h3>
                                        <span className="text-xs text-gray-500 flex items-center gap-1">
                                            <Clock size={12} /> {alert.time}
                                        </span>
                                    </div>
                                    <p className="text-gray-400 text-sm mt-1">{alert.desc}</p>
                                    <div className="flex gap-2 mt-3">
                                        <span className="inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded bg-black/30 text-gray-400">
                                            {alert.type}
                                        </span>
                                        <span className="inline-block text-[10px] uppercase font-bold tracking-wider px-2 py-1 rounded bg-black/30 text-cyan-400">
                                            {alert.source}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))
                    )}
                </div>
            )}

            {/* Filter Info */}
            <div className="mt-8 text-center text-sm text-gray-500">
                Showing alerts from the last <span className="font-bold text-cyan-400">{timeFilter === '24h' ? '24 hours' : '7 days'}</span>
                {' • '}
                Auto-refreshes every 30 seconds
            </div>
        </div>
    );
};

export default Alerts;
