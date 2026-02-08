import { AlertTriangle, TrendingUp, Users, Navigation2, Activity } from 'lucide-react';
import clsx from 'clsx';

const RouteAnalysisPanel = ({ routeAnalysis, source, destination }) => {
    if (!routeAnalysis) return null;

    const {
        alerts_24hr = [],
        community_reports = [],
        bottlenecks = [],
        route_impact_score = 0,
        ai_route_briefing = ""
    } = routeAnalysis;

    const hasData = alerts_24hr.length > 0 || community_reports.length > 0 || bottlenecks.length > 0;

    if (!hasData && !ai_route_briefing) return null;

    return (
        <div className="absolute left-4 top-4 bottom-4 w-96 bg-gray-900/95 backdrop-blur-md rounded-2xl border border-gray-700 overflow-hidden flex flex-col z-10 shadow-2xl">
            {/* Header */}
            <div className="p-4 border-b border-gray-700">
                <h2 className="text-lg font-bold text-white mb-1">Route Intelligence</h2>
                <p className="text-sm text-gray-400">
                    {source} → {destination}
                </p>
                {route_impact_score > 0 && (
                    <div className="mt-2">
                        <div className="flex items-center justify-between text-xs mb-1">
                            <span className="text-gray-400">Impact Score</span>
                            <span className={clsx(
                                "font-bold",
                                route_impact_score > 0.7 ? "text-red-400" : route_impact_score > 0.4 ? "text-yellow-400" : "text-green-400"
                            )}>
                                {(route_impact_score * 100).toFixed(0)}%
                            </span>
                        </div>
                        <div className="w-full bg-gray-800 rounded-full h-2">
                            <div
                                className={clsx(
                                    "h-2 rounded-full transition-all",
                                    route_impact_score > 0.7 ? "bg-red-500" : route_impact_score > 0.4 ? "bg-yellow-500" : "bg-green-500"
                                )}
                                style={{ width: `${route_impact_score * 100}%` }}
                            />
                        </div>
                    </div>
                )}
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">

                {/* AI Route Briefing */}
                {ai_route_briefing && (
                    <div className="bg-gradient-to-r from-cyan-900/30 to-blue-900/30 border border-cyan-500/30 rounded-xl p-4">
                        <div className="flex items-start gap-3">
                            <div className="w-10 h-10 rounded-lg bg-cyan-500/20 flex items-center justify-center flex-shrink-0">
                                <Activity className="w-5 h-5 text-cyan-400" />
                            </div>
                            <div className="flex-1">
                                <h3 className="text-sm font-bold text-white mb-1 flex items-center gap-2">
                                    AI Route Briefing
                                    <span className="px-1.5 py-0.5 bg-cyan-500/20 text-cyan-400 text-[10px] font-bold rounded border border-cyan-500/50">
                                        POWERED BY AI
                                    </span>
                                </h3>
                                <p className="text-sm text-gray-300 leading-relaxed">
                                    {ai_route_briefing}
                                </p>
                            </div>
                        </div>
                    </div>
                )}

                {/* Smart Recommendations (New Feature) */}
                {routeAnalysis.smart_recommendations && (
                    <div className="bg-gradient-to-br from-emerald-900/40 to-teal-900/30 border border-emerald-500/40 rounded-xl p-4 shadow-lg shadow-emerald-900/10">
                        <div className="flex items-center gap-2 mb-3">
                            <div className="p-1 bg-emerald-500/20 rounded-lg">
                                <TrendingUp className="w-4 h-4 text-emerald-400" />
                            </div>
                            <h3 className="text-sm font-bold text-white tracking-wide">SMART MOBILITY</h3>
                        </div>

                        <div className="space-y-3">
                            {/* Viability Alert */}
                            {routeAnalysis.smart_recommendations.viability_alert && (
                                <div className="p-3 bg-red-500/10 rounded-lg border border-red-500/30 flex gap-3 items-start">
                                    <AlertTriangle className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                                    <div>
                                        <div className="text-xs text-red-300 font-bold uppercase mb-0.5">Congestion Alert</div>
                                        <div className="text-sm text-gray-200">{routeAnalysis.smart_recommendations.viability_alert}</div>
                                    </div>
                                </div>
                            )}

                            {/* Optimal Departure */}
                            {routeAnalysis.smart_recommendations.optimal_departure && (
                                <div className="p-3 bg-emerald-500/10 rounded-lg border border-emerald-500/30">
                                    <div className="text-xs text-emerald-300 font-bold uppercase mb-0.5 tracking-wider">Optimal Departure</div>
                                    <div className="text-sm text-white font-medium">{routeAnalysis.smart_recommendations.optimal_departure}</div>
                                </div>
                            )}

                            {/* Smart Break */}
                            {routeAnalysis.smart_recommendations.smart_break && (
                                <div className="p-3 bg-blue-500/10 rounded-lg border border-blue-500/30">
                                    <div className="text-xs text-blue-300 font-bold uppercase mb-0.5 tracking-wider">Smart Break Logic</div>
                                    <div className="text-sm text-white font-medium">{routeAnalysis.smart_recommendations.smart_break}</div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Bottlenecks */}
                {bottlenecks.length > 0 && (
                    <div className="bg-gray-800/50 rounded-xl p-4 border border-red-500/30">
                        <div className="flex items-center gap-2 mb-3">
                            <AlertTriangle className="w-5 h-5 text-red-400" />
                            <h3 className="text-sm font-bold text-white">Future Bottlenecks ({bottlenecks.length})</h3>
                        </div>
                        <div className="space-y-2">
                            {bottlenecks.map((bottleneck, idx) => (
                                <div key={idx} className="bg-gray-900/50 rounded-lg p-3 border border-red-500/20">
                                    <div className="flex items-start justify-between mb-1">
                                        <span className="text-sm font-medium text-white">{bottleneck.location}</span>
                                        <span className={clsx(
                                            "text-xs px-2 py-0.5 rounded-full font-bold",
                                            bottleneck.congestion_forecast === "Critical" ? "bg-red-500/20 text-red-400" : "bg-orange-500/20 text-orange-400"
                                        )}>
                                            {bottleneck.congestion_forecast}
                                        </span>
                                    </div>
                                    <div className="text-xs text-gray-400 mb-1">
                                        ETA: {bottleneck.eta_minutes} min • Probability: {(bottleneck.probability * 100).toFixed(0)}%
                                    </div>
                                    <div className="text-xs text-gray-300">
                                        {bottleneck.reason}
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Active Alerts */}
                {alerts_24hr.length > 0 && (
                    <div className="bg-gray-800/50 rounded-xl p-4 border border-yellow-500/30">
                        <div className="flex items-center gap-2 mb-3">
                            <TrendingUp className="w-5 h-5 text-yellow-400" />
                            <h3 className="text-sm font-bold text-white">Active Alerts (24h)</h3>
                            <span className="ml-auto text-xs bg-yellow-500/20 text-yellow-400 px-2 py-0.5 rounded-full font-bold">
                                {alerts_24hr.length}
                            </span>
                        </div>
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                            {alerts_24hr.slice(0, 5).map((alert, idx) => (
                                <div key={idx} className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
                                    <div className="flex items-start justify-between mb-1">
                                        <span className="text-xs font-bold text-yellow-400">{alert.Category}</span>
                                        {alert.distance_to_route_km !== undefined && (
                                            <span className="text-xs text-gray-500">{alert.distance_to_route_km}km away</span>
                                        )}
                                    </div>
                                    <div className="text-sm text-white font-medium mb-1">{alert.Name}</div>
                                    <div className="text-xs text-gray-400">{alert.Location}</div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Community Reports */}
                {community_reports.length > 0 && (
                    <div className="bg-gray-800/50 rounded-xl p-4 border border-blue-500/30">
                        <div className="flex items-center gap-2 mb-3">
                            <Users className="w-5 h-5 text-blue-400" />
                            <h3 className="text-sm font-bold text-white">Community Reports</h3>
                            <span className="ml-auto text-xs bg-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full font-bold">
                                {community_reports.length}
                            </span>
                        </div>
                        <div className="space-y-2 max-h-60 overflow-y-auto">
                            {community_reports.slice(0, 5).map((report, idx) => (
                                <div key={idx} className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
                                    <div className="flex items-start justify-between mb-1">
                                        <span className="text-xs font-bold text-blue-400">{report.category}</span>
                                        <span className="text-xs text-gray-500">+{report.netScore}</span>
                                    </div>
                                    <div className="text-sm text-white font-medium mb-1">{report.title}</div>
                                    <div className="text-xs text-gray-400 mb-1">{report.description.substring(0, 80)}...</div>
                                    <div className="flex items-center justify-between text-xs text-gray-500">
                                        <span>{report.location}</span>
                                        <span>{report.userName}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* No Data Message */}
                {!hasData && (
                    <div className="text-center py-8 text-gray-500">
                        <Navigation2 className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">No route-specific alerts or reports at this time</p>
                    </div>
                )}
            </div>
        </div>
    );
};

export default RouteAnalysisPanel;
