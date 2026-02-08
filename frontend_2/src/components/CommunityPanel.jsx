import React, { useState, useEffect } from 'react';
import { MessageSquare, MapPin, Send, AlertTriangle, Users } from 'lucide-react';
import axios from 'axios';
import clsx from 'clsx';
import { formatDistanceToNow } from 'date-fns';

const CommunityPanel = ({ currentLocation }) => {
    const [reports, setReports] = useState([]);
    const [newReport, setNewReport] = useState('');
    const [loading, setLoading] = useState(false);
    const [sending, setSending] = useState(false);
    const [severity, setSeverity] = useState('Moderate');

    // Fetch reports on mount and periodically
    useEffect(() => {
        fetchReports();
        const interval = setInterval(fetchReports, 30000); // Poll every 30s
        return () => clearInterval(interval);
    }, [currentLocation]);

    const fetchReports = async () => {
        try {
            const loc = currentLocation || "Mumbai";
            const response = await axios.get(`http://localhost:8005/api/community/feed`, {
                params: { location: loc }
            });
            if (response.data.reports) {
                setReports(response.data.reports);
            }
        } catch (error) {
            console.error("Failed to fetch community reports:", error);
        }
    };

    const submitReport = async () => {
        if (!newReport.trim()) return;
        setSending(true);

        try {
            await axios.post('http://localhost:8005/api/community/report', {
                location: currentLocation || "Mumbai",
                feedback: newReport,
                severity: severity
            });
            setNewReport('');
            fetchReports(); // Refresh immediately
        } catch (error) {
            console.error("Failed to submit report:", error);
        } finally {
            setSending(false);
        }
    };

    return (
        <div className="bg-gray-900/90 backdrop-blur-md border border-gray-700/50 rounded-2xl p-5 shadow-2xl flex flex-col h-[500px]">
            {/* Header */}
            <div className="flex items-center gap-2 border-b border-gray-700 pb-3 mb-3">
                <div className="p-1.5 bg-orange-500/10 rounded-lg">
                    <Users className="w-5 h-5 text-orange-400" />
                </div>
                <div>
                    <h3 className="text-gray-200 font-bold">Community Intel</h3>
                    <p className="text-[10px] text-gray-500 uppercase tracking-wider font-bold">
                        {currentLocation || "City-Wide"} Feed
                    </p>
                </div>
                <div className="ml-auto flex items-center gap-1 bg-green-500/10 px-2 py-0.5 rounded-full border border-green-500/20">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></div>
                    <span className="text-[10px] text-green-400 font-bold">LIVE</span>
                </div>
            </div>

            {/* Feed List */}
            <div className="flex-1 overflow-y-auto custom-scrollbar space-y-3 pr-2">
                {reports.length === 0 ? (
                    <div className="text-center py-10 opacity-50">
                        <MessageSquare className="w-8 h-8 mx-auto text-gray-600 mb-2" />
                        <p className="text-sm text-gray-500">No reports yet.</p>
                        <p className="text-xs text-gray-600">Be the first to share intel!</p>
                    </div>
                ) : (
                    reports.map((report) => (
                        <div key={report.id} className="bg-gray-800/40 rounded-xl p-3 border border-gray-700 hover:border-gray-600 transition-colors">
                            <div className="flex justify-between items-start mb-1">
                                <span className={clsx(
                                    "text-[10px] px-1.5 py-0.5 rounded border font-bold uppercase",
                                    report.severity === 'High' ? "bg-red-500/10 text-red-400 border-red-500/30" :
                                        report.severity === 'Moderate' ? "bg-yellow-500/10 text-yellow-400 border-yellow-500/30" :
                                            "bg-blue-500/10 text-blue-400 border-blue-500/30"
                                )}>
                                    {report.severity} Priority
                                </span>
                                <span className="text-[10px] text-gray-500">{report.ago}</span>
                            </div>
                            <p className="text-sm text-gray-300 leading-snug">{report.report}</p>
                            <div className="mt-2 flex items-center gap-2 text-[10px] text-gray-500">
                                <MapPin className="w-3 h-3" />
                                {report.location}
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Input Area */}
            <div className="mt-3 pt-3 border-t border-gray-700 bg-gray-900/50 -mx-1 px-1">
                <div className="flex gap-2 mb-2">
                    {['Low', 'Moderate', 'High'].map((sev) => (
                        <button
                            key={sev}
                            onClick={() => setSeverity(sev)}
                            className={clsx(
                                "flex-1 py-1 rounded text-[10px] font-bold border transition-all",
                                severity === sev
                                    ? (sev === 'High' ? "bg-red-500/20 border-red-500 text-red-400" :
                                        sev === 'Moderate' ? "bg-yellow-500/20 border-yellow-500 text-yellow-400" :
                                            "bg-blue-500/20 border-blue-500 text-blue-400")
                                    : "bg-gray-800 border-gray-700 text-gray-500 hover:bg-gray-700"
                            )}
                        >
                            {sev}
                        </button>
                    ))}
                </div>
                <div className="flex gap-2">
                    <input
                        type="text"
                        value={newReport}
                        onChange={(e) => setNewReport(e.target.value)}
                        placeholder="Report traffic info..."
                        className="flex-1 bg-gray-950/50 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 focus:ring-1 focus:ring-orange-500/50 outline-none"
                        onKeyPress={(e) => e.key === 'Enter' && submitReport()}
                    />
                    <button
                        onClick={submitReport}
                        disabled={!newReport.trim() || sending}
                        className="bg-orange-600 hover:bg-orange-500 text-white p-2 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {sending ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <Send className="w-4 h-4" />}
                    </button>
                </div>
            </div>
        </div>
    );
};

export default CommunityPanel;
