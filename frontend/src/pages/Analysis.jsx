import React, { useState } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, ScatterChart, Scatter, ZAxis } from 'recharts';
import { Brain, TrendingUp, AlertTriangle, Coffee, Clock, ArrowRight } from 'lucide-react';
import PageTransition from '../components/PageTransition';

const Analysis = () => {
    const [selectedZone, setSelectedZone] = useState('Bandra-Kurla Complex');

    // Mock Prediction Data for Bottlenecks
    const bottleneckData = [
        { time: '08:00', density: 45, prediction: 50 },
        { time: '10:00', density: 85, prediction: 90 }, // Bottleneck
        { time: '12:00', density: 60, prediction: 55 },
        { time: '14:00', density: 50, prediction: 45 },
        { time: '16:00', density: 70, prediction: 80 },
        { time: '18:00', density: 95, prediction: 98 }, // Bottleneck
        { time: '20:00', density: 80, prediction: 75 },
    ];

    // Smart Break Logic Data
    const smartBreakData = [
        { time: 'Now', traffic: 92, recommendation: 'Avoid Travel', color: '#ef4444' },
        { time: '+30m', traffic: 88, recommendation: 'High Traffic', color: '#f97316' },
        { time: '+1h', traffic: 65, recommendation: 'Better', color: '#eab308' },
        { time: '+2h', traffic: 40, recommendation: 'Best Time', color: '#22c55e' },
    ];

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
                            <div className="bg-black/40 p-3 rounded-xl border border-white/5">
                                <p className="text-xs text-gray-400 mb-1">Current Status</p>
                                <div className="flex justify-between items-center">
                                    <span className="text-2xl font-bold text-red-500">Heavy Traffic</span>
                                    <span className="text-sm font-medium bg-red-500/20 text-red-400 px-2 py-1 rounded">Avg Speed: 12 km/h</span>
                                </div>
                                <p className="text-sm text-gray-300 mt-2">
                                    Traveling now will take <b className="text-white">55 mins</b> for 15 km.
                                </p>
                            </div>

                            <div className="flex items-center gap-3">
                                <div className="h-8 w-8 rounded-full bg-cyan-500/20 flex items-center justify-center text-cyan-400">
                                    <ArrowRight size={16} />
                                </div>
                                <div>
                                    <p className="text-xs text-gray-400">AI Recommendation</p>
                                    <p className="text-sm font-medium text-white">
                                        Take a <span className="text-green-400 font-bold">20 min break</span>. Traffic clearing in Andheri.
                                    </p>
                                </div>
                            </div>

                            <button className="w-full py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2">
                                <Clock size={14} /> Schedule Deviation
                            </button>
                        </div>
                    </div>

                    {/* Timeline Recommendation */}
                    <div className="bg-gray-900/50 border border-white/10 p-5 rounded-2xl flex-1">
                        <h4 className="text-sm font-bold text-gray-400 mb-4 uppercase tracking-wider">Departure Planner</h4>
                        <div className="space-y-3">
                            {smartBreakData.map((item, idx) => (
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
                            ))}
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
