import React, { useState } from 'react';
import { CloudRain, AlertTriangle, Play, RefreshCw, TrendingUp } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';

const SimulationPanel = ({ city, onSimulationComplete }) => {
    const [scenario, setScenario] = useState(null); // 'Heavy Rain', 'Accident'
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);

    const runSimulation = async () => {
        if (!scenario) return;
        setLoading(true);
        setResult(null);

        try {
            const response = await axios.post('https://datathon-w1z4.onrender.com/api/simulate', {
                location: city || "Mumbai",
                scenario: scenario,
                intensity: 1.0
            });

            if (response.data.status === 'success') {
                setResult(response.data.result);
                if (onSimulationComplete) onSimulationComplete(response.data.result);
            }
        } catch (error) {
            console.error("Simulation failed:", error);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="bg-gray-900/90 backdrop-blur-md border border-gray-700/50 rounded-2xl p-5 shadow-2xl space-y-4">
            <div className="flex items-center gap-2 border-b border-gray-700 pb-2">
                <div className="p-1.5 bg-purple-500/10 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-purple-400" />
                </div>
                <h3 className="text-gray-200 font-bold">What-If Simulator</h3>
            </div>

            <div className="space-y-3">
                <p className="text-xs text-gray-400">Select a scenario to simulate impact:</p>

                <div className="grid grid-cols-2 gap-3">
                    <button
                        onClick={() => setScenario(scenario === 'Heavy Rain' ? null : 'Heavy Rain')}
                        className={clsx(
                            "p-3 rounded-xl border flex flex-col items-center gap-2 transition-all",
                            scenario === 'Heavy Rain'
                                ? "bg-blue-500/20 border-blue-500 text-blue-400"
                                : "bg-gray-800/50 border-gray-700 text-gray-400 hover:bg-gray-800"
                        )}
                    >
                        <CloudRain className="w-6 h-6" />
                        <span className="text-xs font-bold">Heavy Rain</span>
                    </button>

                    <button
                        onClick={() => setScenario(scenario === 'Accident' ? null : 'Accident')}
                        className={clsx(
                            "p-3 rounded-xl border flex flex-col items-center gap-2 transition-all",
                            scenario === 'Accident'
                                ? "bg-red-500/20 border-red-500 text-red-400"
                                : "bg-gray-800/50 border-gray-700 text-gray-400 hover:bg-gray-800"
                        )}
                    >
                        <AlertTriangle className="w-6 h-6" />
                        <span className="text-xs font-bold">Accident</span>
                    </button>
                </div>

                <button
                    onClick={runSimulation}
                    disabled={!scenario || loading}
                    className={clsx(
                        "w-full py-2.5 rounded-lg font-bold flex items-center justify-center gap-2 transition-all",
                        !scenario || loading
                            ? "bg-gray-800 text-gray-500 cursor-not-allowed"
                            : "bg-purple-600 hover:bg-purple-500 text-white shadow-lg shadow-purple-900/20"
                    )}
                >
                    {loading ? <RefreshCw className="w-4 h-4 animate-spin" /> : <Play className="w-4 h-4" />}
                    Run Simulation
                </button>
            </div>

            {/* Results Area */}
            {result && (
                <div className="mt-4 pt-4 border-t border-gray-700 animate-in fade-in slide-in-from-top-2">
                    <h4 className="text-xs font-bold text-gray-400 uppercase mb-2">Projected Impact</h4>

                    <div className="bg-gray-800/50 rounded-lg p-3 border border-gray-700">
                        <div className="flex justify-between items-center mb-1">
                            <span className="text-sm text-gray-300">Congestion Shift</span>
                            <span className={clsx(
                                "text-sm font-bold",
                                result.change > 0 ? "text-red-400" : "text-green-400"
                            )}>
                                {result.change > 0 ? "+" : ""}{result.change} Levels
                            </span>
                        </div>
                        <p className="text-xs text-gray-500 italic mt-2">
                            "{result.impact_description}"
                        </p>
                        <div className="mt-3 flex items-center gap-2">
                            <div className="h-1.5 flex-1 bg-gray-700 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-purple-500 rounded-full"
                                    style={{ width: `${result.confidence}%` }}
                                ></div>
                            </div>
                            <span className="text-[10px] text-gray-500">{result.confidence.toFixed(0)}% Conf.</span>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default SimulationPanel;
