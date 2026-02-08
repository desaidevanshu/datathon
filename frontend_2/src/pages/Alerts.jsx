import { useEffect, useState } from 'react';
import axios from 'axios';
import { AlertTriangle, Info, AlertCircle, ExternalLink, Clock, MapPin, TrendingUp } from 'lucide-react';
import clsx from 'clsx';

const Alerts = () => {
    const [events, setEvents] = useState([]);
    const [filteredEvents, setFilteredEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [timeFilter, setTimeFilter] = useState('all'); // 'all', '24h', '7d'

    useEffect(() => {
        const fetchEvents = async () => {
            try {
                const response = await axios.get('http://localhost:8005/api/predict?city=Mumbai');
                const data = response.data;
                const eventData = data?.context?.events || {};

                // Extract events array from new structure
                const eventsList = eventData.Details?.Events || [];
                setEvents(eventsList);
                setFilteredEvents(eventsList); // Initially show all
            } catch (error) {
                console.error("Failed to fetch events:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchEvents();
        const interval = setInterval(fetchEvents, 30000); // Poll every 30 seconds
        return () => clearInterval(interval);
    }, []);

    // Apply time filter whenever events or filter changes
    useEffect(() => {
        if (timeFilter === 'all') {
            setFilteredEvents(events);
        } else {
            const now = new Date();
            const filtered = events.filter(event => {
                try {
                    const eventDate = new Date(event.Time);
                    const diffHours = (now - eventDate) / (1000 * 60 * 60);

                    if (timeFilter === '24h') return diffHours <= 24;
                    if (timeFilter === '7d') return diffHours <= 168; // 7 days
                    return true;
                } catch {
                    return true; // Include events with invalid dates
                }
            });
            setFilteredEvents(filtered);
        }
    }, [events, timeFilter]);

    const getImpactColor = (impact) => {
        switch (impact?.toLowerCase()) {
            case 'high': return 'red';
            case 'medium': return 'yellow';
            default: return 'blue';
        }
    };

    const getImpactIcon = (impact) => {
        switch (impact?.toLowerCase()) {
            case 'high': return AlertTriangle;
            case 'medium': return AlertCircle;
            default: return Info;
        }
    };

    if (loading) {
        return (
            <div className="p-10 flex items-center justify-center">
                <div className="text-white flex items-center gap-3">
                    <div className="w-6 h-6 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin" />
                    <span>Loading Live Alerts...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 lg:p-10 max-w-[1400px] mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                        <TrendingUp className="w-8 h-8 text-cyan-400" />
                        Live Traffic Alerts
                    </h1>
                    <p className="text-gray-400 mt-2">Real-time event updates from Google News</p>
                </div>
                <div className="text-right">
                    <p className="text-sm text-gray-500">Last Updated</p>
                    <p className="text-white font-mono">{new Date().toLocaleTimeString()}</p>
                </div>
            </div>

            {/* Filter Buttons */}
            <div className="flex gap-3 items-center">
                <span className="text-sm text-gray-400">Filter by:</span>
                <button
                    onClick={() => setTimeFilter('all')}
                    className={clsx(
                        "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                        timeFilter === 'all'
                            ? "bg-cyan-500 text-white"
                            : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                    )}
                >
                    All Events ({events.length})
                </button>
                <button
                    onClick={() => setTimeFilter('24h')}
                    className={clsx(
                        "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                        timeFilter === '24h'
                            ? "bg-cyan-500 text-white"
                            : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                    )}
                >
                    Last 24 Hours
                </button>
                <button
                    onClick={() => setTimeFilter('7d')}
                    className={clsx(
                        "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                        timeFilter === '7d'
                            ? "bg-cyan-500 text-white"
                            : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                    )}
                >
                    Last 7 Days
                </button>
            </div>

            {/* Alerts List */}
            {filteredEvents.length === 0 ? (
                <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-12 text-center">
                    <Info className="w-16 h-16 text-green-500 mx-auto mb-4" />
                    <h2 className="text-xl font-bold text-white mb-2">All Clear!</h2>
                    <p className="text-gray-400">No major traffic incidents detected {timeFilter !== 'all' ? 'in this time range' : 'at this time'}.</p>
                </div>
            ) : (
                <div className="space-y-4">
                    {filteredEvents.map((event, idx) => {
                        const color = getImpactColor(event.Impact);
                        const Icon = getImpactIcon(event.Impact);

                        return (
                            <div
                                key={idx}
                                className={clsx(
                                    "bg-gray-900/50 border rounded-2xl p-6 hover:border-gray-700 transition-all",
                                    color === 'red' && "border-red-500/30 bg-red-500/5",
                                    color === 'yellow' && "border-yellow-500/30 bg-yellow-500/5",
                                    color === 'blue' && "border-blue-500/30 bg-blue-500/5"
                                )}
                            >
                                <div className="flex gap-4">
                                    {/* Icon */}
                                    <div className={clsx(
                                        "p-3 rounded-xl h-fit",
                                        color === 'red' && "bg-red-500/10",
                                        color === 'yellow' && "bg-yellow-500/10",
                                        color === 'blue' && "bg-blue-500/10"
                                    )}>
                                        <Icon className={clsx(
                                            "w-6 h-6",
                                            color === 'red' && "text-red-400",
                                            color === 'yellow' && "text-yellow-400",
                                            color === 'blue' && "text-blue-400"
                                        )} />
                                    </div>

                                    {/* Content */}
                                    <div className="flex-1">
                                        <div className="flex items-start justify-between gap-4 mb-3">
                                            <div>
                                                <div className="flex items-center gap-2 mb-2">
                                                    <span className={clsx(
                                                        "text-xs font-bold px-2 py-1 rounded-full uppercase",
                                                        color === 'red' && "bg-red-500/20 text-red-300",
                                                        color === 'yellow' && "bg-yellow-500/20 text-yellow-300",
                                                        color === 'blue' && "bg-blue-500/20 text-blue-300"
                                                    )}>
                                                        {event.Impact} Impact
                                                    </span>
                                                    <span className="text-xs text-gray-500">{event.Source}</span>
                                                </div>
                                                <h3 className="text-lg font-bold text-white leading-tight">
                                                    {event.Name}
                                                </h3>
                                            </div>
                                        </div>

                                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3 mb-4">
                                            <div className="flex items-center gap-2 text-sm">
                                                <MapPin className="w-4 h-4 text-gray-500" />
                                                <span className="text-gray-300">{event.Location}</span>
                                            </div>
                                            {event.Time && (
                                                <div className="flex items-center gap-2 text-sm">
                                                    <Clock className="w-4 h-4 text-gray-500" />
                                                    <span className="text-gray-300">{new Date(event.Time).toLocaleString()}</span>
                                                </div>
                                            )}
                                        </div>

                                        {event.AffectedAreas && event.AffectedAreas.length > 0 && (
                                            <div className="mb-4">
                                                <p className="text-xs text-gray-500 mb-2">Affected Areas</p>
                                                <div className="flex flex-wrap gap-2">
                                                    {event.AffectedAreas.map((area, i) => (
                                                        <span key={i} className="text-xs bg-gray-800 text-gray-300 px-2 py-1 rounded">
                                                            {area}
                                                        </span>
                                                    ))}
                                                </div>
                                            </div>
                                        )}

                                        {event.Link && (
                                            <a
                                                href={event.Link}
                                                target="_blank"
                                                rel="noopener noreferrer"
                                                className="inline-flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300 transition-colors"
                                            >
                                                <ExternalLink className="w-4 h-4" />
                                                Read Full Story
                                            </a>
                                        )}
                                    </div>
                                </div>
                            </div>
                        );
                    })}
                </div>
            )}
        </div>
    );
};

export default Alerts;
