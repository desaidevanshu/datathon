
import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, ScatterChart, Scatter, ZAxis } from 'recharts';
import { Brain, TrendingUp, AlertTriangle, Coffee, Clock, ArrowRight } from 'lucide-react';
import PageTransition from '../components/PageTransition';

const Analysis = () => {
    const [zones, setZones] = React.useState(["Bandra-Kurla Complex", "Western Express Highway", "Linking Road"]);
    const [selectedZone, setSelectedZone] = React.useState("");
    const [loading, setLoading] = React.useState(true);
    const [bottleneckData, setBottleneckData] = React.useState(null);
    const [smartBreakData, setSmartBreakData] = React.useState(null);
    const [smartRecommendation, setSmartRecommendation] = React.useState(null);

    // 1. Fetch Locations from Backend
    React.useEffect(() => {
        const fetchLocations = async () => {
            try {
                const response = await fetch('https://datathon-w1z4.onrender.com/api/locations');
                const data = await response.json();
                if (data.locations && data.locations.length > 0) {
                    setZones(data.locations);
                    setSelectedZone(data.locations[0]); // Select first by default
                } else {
                    setSelectedZone("Bandra-Kurla Complex"); // Fallback if API returns empty
                }
            } catch (error) {
                console.error("Failed to fetch locations:", error);
                setSelectedZone("Bandra-Kurla Complex"); // Fallback on error
            }
        };
        fetchLocations();
    }, []);

    // 2. Fetch Analysis Data when Zone Changes
    React.useEffect(() => {
        if (!selectedZone) return; // Don't fetch analysis until a zone is selected

        const fetchData = async () => {
            try {
                setLoading(true);
                const response = await fetch(`https://datathon-w1z4.onrender.com/api/predict?city=${encodeURIComponent(selectedZone)}`);
                const data = await response.json();
                console.log("Analysis Data:", data);

                if (data.forecast && data.forecast.length > 0) {
                    // Transform forecast to chart data
                    const chartData = data.forecast.map(f => ({
                        time: f.step, // e.g., +1h
                        density: f.congestion_level === 'High' || f.congestion_level === 'Critical' ? 85 :
                            (f.congestion_level === 'Medium' || f.congestion_level === 'Moderate' ? 60 : 30),
                        prediction: f.confidence,
                        isBottleneck: f.is_bottleneck
                    }));
                    setBottleneckData(chartData);
                } else {
                    // Fallback Mock Data if API returns empty forecast
                    setBottleneckData([
                        { time: 'Now', density: 45, prediction: 50 },
                        { time: '+1h', density: 85, prediction: 90 },
                        { time: '+2h', density: 60, prediction: 55 },
                        { time: '+3h', density: 50, prediction: 45 },
                    ]);
                }

                if (data.smart_analysis && Object.keys(data.smart_analysis).length > 0) {
                    setSmartRecommendation(data.smart_analysis);
                    // Use timeline if available, or fallback
                    if (data.smart_analysis.timeline) {
                        const coloredTimeline = data.smart_analysis.timeline.map(item => {
                            let color = '#22c55e'; // Green
                            if (item.traffic > 80) color = '#ef4444'; // Red
                            else if (item.traffic > 60) color = '#f97316'; // Orange
                            else if (item.traffic > 50) color = '#eab308'; // Yellow
                            return { ...item, color };
                        });
                        setSmartBreakData(coloredTimeline);
                    } else {
                        setSmartBreakData([
                            { time: 'Now', traffic: 50, recommendation: 'Go', color: '#22c55e' },
                            { time: '+1h', traffic: 60, recommendation: 'OK', color: '#eab308' },
                        ]);
                    }
                } else {
                    // Fallback Smart Recommendation
                    setSmartRecommendation({
                        viability_alert: "Moderate Traffic",
                        smart_break: "Traffic is standard. No specific break needed.",
                        optimal_departure: "Leave anytime."
                    });
                    setSmartBreakData([
                        { time: 'Now', traffic: 50, recommendation: 'Go', color: '#22c55e' },
                        { time: '+1h', traffic: 60, recommendation: 'OK', color: '#eab308' },
                    ]);
                }
            } catch (error) {
                console.error("Error fetching analysis:", error);
                // Fallback on error
                setBottleneckData([
                    { time: 'Error', density: 0, prediction: 0 }
                ]);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, [selectedZone]);

    return (
        <div className="p-6 md:p-10 min-h-screen text-gray-100 pb-20">
            <div className="mb-8">
                <h1 className="text-3xl font-bold mb-2 flex items-center gap-3">
                    <Brain className="text-cyan-400" size={32} />
                    Traffic Analysis & Predictions
                </h1>
                <p className="text-gray-400">AI-driven insights for future bottlenecks and smart travel planning.</p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

                {/* 1. Future Bottleneck Prediction */}
                <div className="bg-gray-900/50 border border-white/10 p-6 rounded-2xl lg:col-span-2">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-lg font-bold flex items-center gap-2">
                            <TrendingUp size={18} className="text-cyan-400" /> Future Bottleneck Prediction
                        </h3>
                        <select
                            value={selectedZone}
                            onChange={(e) => setSelectedZone(e.target.value)}
                            className="bg-black/30 border border-white/10 rounded-lg px-3 py-1 text-sm outline-none focus:border-cyan-500"
                        >
                            <option>Bandra-Kurla Complex</option>
                            <option>Western Express Highway</option>
                            <option>Linking Road</option>
                        </select>
                    </div>

                    <div className="h-72 w-full">
                        {bottleneckData ? (
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={bottleneckData}>
                                    <defs>
                                        <linearGradient id="colorPred" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#06b6d4" stopOpacity={0} />
                                        </linearGradient>
                                        <linearGradient id="colorDen" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="5%" stopColor="#f472b6" stopOpacity={0.3} />
                                            <stop offset="95%" stopColor="#f472b6" stopOpacity={0} />
                                        </linearGradient>
                                    </defs>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" vertical={false} />
                                    <XAxis dataKey="time" stroke="#9ca3af" fontSize={12} />
                                    <YAxis stroke="#9ca3af" fontSize={12} label={{ value: 'Density %', angle: -90, position: 'insideLeft', fill: '#6b7280' }} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#f3f4f6' }}
                                        itemStyle={{ color: '#f3f4f6' }}
                                    />
                                    <Legend />
                                    <Area type="monotone" dataKey="prediction" stroke="#06b6d4" fillOpacity={1} fill="url(#colorPred)" name="AI Prediction" strokeWidth={2} />
                                    <Area type="monotone" dataKey="density" stroke="#f472b6" fillOpacity={1} fill="url(#colorDen)" name="Historical Avg" strokeWidth={2} strokeDasharray="5 5" />

                                    {/* Bottleneck Threshold Line */}
                                    <Scatter data={[{ x: '08:00', y: 80 }, { x: '20:00', y: 80 }]} line={{ stroke: 'red', strokeWidth: 1, strokeDasharray: '3 3' }} shape={() => null} legendType="none" />
                                </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="text-center py-10 text-gray-500 animate-pulse">Loading traffic forecast...</div>
                        )}
                    </div>
                    <div className="mt-4 flex gap-4 text-xs text-gray-400">
                        <div className="flex items-center gap-1">
                            <div className="w-3 h-3 rounded-full bg-cyan-500/50"></div> AI Predicted Density
                        </div>
                        <div className="flex items-center gap-1">
                            <div className="w-3 h-3 rounded-full bg-pink-500/50"></div> Historical Average
                        </div>
                        <div className="flex items-center gap-1">
                            <div className="w-3 h-0.5 bg-red-500 border-t border-dashed border-red-500"></div> Critical Bottleneck Threshold (80%)
                        </div>
                    </div>
                </div>

                {/* 2. Smart Break Logic (Recommendation) */}
                <div className="flex flex-col gap-6">
                    <div className="bg-gradient-to-br from-green-900/40 to-black border border-green-500/30 p-6 rounded-2xl relative overflow-hidden group">
                        <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
                            <Coffee size={100} />
                        </div>

                        <h3 className="text-lg font-bold mb-4 flex items-center gap-2 z-10 relative">
                            <Coffee size={18} className="text-green-400" /> Smart Break Logic
                        </h3>

                        <div className="space-y-4 z-10 relative">
                            {smartRecommendation ? (
                                <>
                                    <div className="bg-black/40 p-3 rounded-xl border border-white/5">
                                        <p className="text-xs text-gray-400 mb-1">Current Status</p>
                                        <div className="flex justify-between items-center">
                                            <span className="text-xl font-bold text-red-500">
                                                {smartRecommendation.viability_alert || "Moderate Traffic"}
                                            </span>
                                            <span className="text-xs font-medium bg-red-500/20 text-red-400 px-2 py-1 rounded">
                                                Live Analysis
                                            </span>
                                        </div>
                                        <p className="text-sm text-gray-300 mt-2">
                                            {smartRecommendation.viability_alert && smartRecommendation.viability_alert.includes("Severe")
                                                ? "Significant delays expected."
                                                : "Traffic flow is manageable."}
                                        </p>
                                    </div>

                                    <div className="flex items-center gap-3">
                                        <div className="h-8 w-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                                            <ArrowRight size={16} />
                                        </div>
                                        <div>
                                            <p className="text-xs text-gray-400">AI Recommendation</p>
                                            <p className="text-sm font-medium text-white">
                                                {smartRecommendation.smart_break || "No specific break recommended."}
                                            </p>
                                        </div>
                                    </div>

                                    {smartRecommendation.optimal_departure && (
                                        <div className="p-2 bg-blue-500/10 rounded border border-blue-500/30 text-xs text-blue-200">
                                            Optimal Departure: <span className="font-bold text-white">{smartRecommendation.optimal_departure}</span>
                                        </div>
                                    )}
                                </>
                            ) : (
                                <div className="text-center py-4 text-gray-400 animate-pulse">Analyzing traffic patterns...</div>
                            )}

                            <button className="w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2">
                                <Clock size={14} /> Schedule Deviation
                            </button>
                        </div>
                    </div>

                    {/* Timeline Recommendation */}
                    <div className="bg-gray-900/50 border border-white/10 p-5 rounded-2xl flex-1">
                        <h4 className="text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider">Departure Planner</h4>
                        <div className="space-y-3">
                            {smartBreakData ? (
                                smartBreakData.map((item, idx) => (
                                    <div key={idx} className="flex items-center gap-3">
                                        <div className="w-16 text-xs text-gray-500 font-mono text-right">{item.time}</div>
                                        <div className="flex-1 h-3 bg-gray-700/50 rounded-full overflow-hidden">
                                            <div
                                                className="h-full rounded-full transition-all"
                                                style={{ width: `${item.traffic}%`, backgroundColor: item.color }}
                                            />
                                        </div>
                                        <div className="w-24 text-xs font-bold text-right" style={{ color: item.color }}>
                                            {item.recommendation}
                                        </div>
                                    </div>
                                ))
                            ) : (
                                <div className="text-center py-4 text-gray-500 italic text-xs">Loading departure insights...</div>
                            )}
                        </div>
                        <p className="text-[10px] text-gray-500 mt-4 text-center">
                            *Predicted based on live sensor data & historical patterns.
                        </p>
                    </div>
                </div>

            </div>
        </div>
    );
};

export default Analysis;
