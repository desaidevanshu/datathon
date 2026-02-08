import { useState, useEffect } from 'react';
import { FileText, ThumbsUp, ThumbsDown, MapPin, Tag, Clock, Trash2, Send } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { createReport, subscribeToReports, toggleThumbsUp, toggleThumbsDown, deleteReport } from '../services/reportsService';
import clsx from 'clsx';

const Reports = () => {
    const { user, anonymousName, isAuthenticated } = useAuth();
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);

    // Form state
    const [title, setTitle] = useState('');
    const [description, setDescription] = useState('');
    const [location, setLocation] = useState('');
    const [category, setCategory] = useState('Traffic');
    const [submitting, setSubmitting] = useState(false);

    // Subscribe to reports
    useEffect(() => {
        const unsubscribe = subscribeToReports((reportsData) => {
            setReports(reportsData);
            setLoading(false);
        });

        return () => unsubscribe();
    }, []);

    const handleSubmit = async (e) => {
        e.preventDefault();

        if (!isAuthenticated) {
            alert('Please sign in to submit a report');
            return;
        }

        if (!title.trim() || !description.trim()) {
            alert('Please fill in title and description');
            return;
        }

        setSubmitting(true);
        try {
            await createReport({
                title: title.trim(),
                description: description.trim(),
                location: location.trim() || 'Mumbai',
                category
            }, user);

            // Reset form
            setTitle('');
            setDescription('');
            setLocation('');
            setCategory('Traffic');

            alert('Report submitted successfully!');
        } catch (error) {
            console.error('Error submitting report:', error);
            alert('Failed to submit report. Please try again.');
        } finally {
            setSubmitting(false);
        }
    };

    const handleVoteUp = async (report) => {
        if (!isAuthenticated) {
            alert('Please sign in to vote');
            return;
        }

        const hasUpvoted = report.thumbsUp?.includes(user.uid);
        const hasDownvoted = report.thumbsDown?.includes(user.uid);

        try {
            await toggleThumbsUp(report.id, user.uid, hasUpvoted, hasDownvoted);
        } catch (error) {
            alert('Failed to vote. Please try again.');
        }
    };

    const handleVoteDown = async (report) => {
        if (!isAuthenticated) {
            alert('Please sign in to vote');
            return;
        }

        const hasUpvoted = report.thumbsUp?.includes(user.uid);
        const hasDownvoted = report.thumbsDown?.includes(user.uid);

        try {
            await toggleThumbsDown(report.id, user.uid, hasUpvoted, hasDownvoted);
        } catch (error) {
            alert('Failed to vote. Please try again.');
        }
    };

    const handleDelete = async (reportId) => {
        if (confirm('Are you sure you want to delete this report?')) {
            try {
                await deleteReport(reportId);
            } catch (error) {
                alert('Failed to delete report. Please try again.');
            }
        }
    };

    const getCategoryColor = (cat) => {
        const colors = {
            Traffic: 'bg-red-500/20 text-red-300',
            Construction: 'bg-orange-500/20 text-orange-300',
            Protest: 'bg-purple-500/20 text-purple-300',
            Accident: 'bg-yellow-500/20 text-yellow-300',
            Other: 'bg-gray-500/20 text-gray-300'
        };
        return colors[cat] || colors.Other;
    };

    if (!isAuthenticated) {
        return (
            <div className="p-10 flex items-center justify-center min-h-screen">
                <div className="text-center">
                    <FileText className="w-20 h-20 text-gray-600 mx-auto mb-4" />
                    <h2 className="text-2xl font-bold text-white mb-2">Sign In Required</h2>
                    <p className="text-gray-400">Please sign in to view and submit traffic reports</p>
                </div>
            </div>
        );
    }

    return (
        <div className="p-6 lg:p-10 max-w-[1400px] mx-auto space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                    <FileText className="w-8 h-8 text-cyan-400" />
                    Community Traffic Reports
                </h1>
                <p className="text-gray-400 mt-2">Share and vote on real-time traffic updates from fellow commuters</p>
            </div>

            {/* Submit Report Form */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6">
                <h2 className="text-xl font-bold text-white mb-4">Submit New Report</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Title *</label>
                            <input
                                type="text"
                                value={title}
                                onChange={(e) => setTitle(e.target.value)}
                                placeholder="e.g., Heavy traffic on Western Express"
                                className="w-full px-4 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:outline-none focus:border-cyan-500"
                                maxLength={100}
                                required
                            />
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-400 mb-2">Location</label>
                            <input
                                type="text"
                                value={location}
                                onChange={(e) => setLocation(e.target.value)}
                                placeholder="e.g., Andheri, Mumbai"
                                className="w-full px-4 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:outline-none focus:border-cyan-500"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">Description *</label>
                        <textarea
                            value={description}
                            onChange={(e) => setDescription(e.target.value)}
                            placeholder="Describe the traffic situation..."
                            rows={3}
                            className="w-full px-4 py-2 bg-gray-800 text-white border border-gray-700 rounded-lg focus:outline-none focus:border-cyan-500 resize-none"
                            maxLength={500}
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-400 mb-2">Category</label>
                        <div className="flex gap-2 flex-wrap">
                            {['Traffic', 'Accident', 'Construction', 'Protest', 'Other'].map((cat) => (
                                <button
                                    key={cat}
                                    type="button"
                                    onClick={() => setCategory(cat)}
                                    className={clsx(
                                        "px-4 py-2 rounded-lg text-sm font-medium transition-all",
                                        category === cat
                                            ? "bg-cyan-500 text-white"
                                            : "bg-gray-800 text-gray-400 hover:bg-gray-700"
                                    )}
                                >
                                    {cat}
                                </button>
                            ))}
                        </div>
                    </div>

                    <button
                        type="submit"
                        disabled={submitting}
                        className="w-full md:w-auto px-6 py-3 bg-cyan-500 hover:bg-cyan-600 text-white font-medium rounded-lg transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                    >
                        <Send className="w-4 h-4" />
                        {submitting ? 'Submitting...' : 'Submit Report'}
                    </button>
                </form>
            </div>

            {/* Reports List */}
            <div>
                <h2 className="text-xl font-bold text-white mb-4">Recent Reports ({reports.length})</h2>
                {loading ? (
                    <div className="text-center py-12">
                        <div className="w-8 h-8 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
                        <p className="text-gray-400">Loading reports...</p>
                    </div>
                ) : reports.length === 0 ? (
                    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-12 text-center">
                        <FileText className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                        <p className="text-gray-400">No reports yet. Be the first to share!</p>
                    </div>
                ) : (
                    <div className="space-y-4">
                        {reports.map((report, index) => {
                            const hasUpvoted = report.thumbsUp?.includes(user?.uid);
                            const hasDownvoted = report.thumbsDown?.includes(user?.uid);
                            const isOwner = report.userId === user?.uid;

                            return (
                                <div
                                    key={report.id}
                                    className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-all"
                                >
                                    <div className="flex gap-4">
                                        {/* Rank Badge */}
                                        <div className="flex-shrink-0">
                                            <div className={clsx(
                                                "w-12 h-12 rounded-full flex items-center justify-center font-bold text-lg",
                                                index === 0 && "bg-yellow-500/20 text-yellow-400 border-2 border-yellow-500",
                                                index === 1 && "bg-gray-400/20 text-gray-300 border-2 border-gray-400",
                                                index === 2 && "bg-orange-500/20 text-orange-400 border-2 border-orange-500",
                                                index > 2 && "bg-gray-800 text-gray-500"
                                            )}>
                                                #{index + 1}
                                            </div>
                                        </div>

                                        {/* Content */}
                                        <div className="flex-1">
                                            <div className="flex items-start justify-between gap-4 mb-2">
                                                <div>
                                                    <h3 className="text-lg font-bold text-white mb-1">{report.title}</h3>
                                                    <div className="flex items-center gap-3 text-sm text-gray-400">
                                                        <span>{report.userName}</span>
                                                        {report.timestamp && (
                                                            <span className="flex items-center gap-1">
                                                                <Clock className="w-3 h-3" />
                                                                {new Date(report.timestamp).toLocaleString()}
                                                            </span>
                                                        )}
                                                    </div>
                                                </div>
                                                {isOwner && (
                                                    <button
                                                        onClick={() => handleDelete(report.id)}
                                                        className="p-2 text-red-400 hover:bg-red-500/10 rounded-lg transition-colors"
                                                        title="Delete report"
                                                    >
                                                        <Trash2 className="w-4 h-4" />
                                                    </button>
                                                )}
                                            </div>

                                            <p className="text-gray-300 mb-4">{report.description}</p>

                                            <div className="flex items-center flex-wrap gap-3">
                                                {report.location && (
                                                    <span className="flex items-center gap-1 text-sm text-gray-400">
                                                        <MapPin className="w-4 h-4" />
                                                        {report.location}
                                                    </span>
                                                )}
                                                <span className={clsx("px-2 py-1 rounded text-xs font-medium flex items-center gap-1", getCategoryColor(report.category))}>
                                                    <Tag className="w-3 h-3" />
                                                    {report.category}
                                                </span>
                                            </div>

                                            {/* Voting */}
                                            <div className="flex items-center gap-4 mt-4 pt-4 border-t border-gray-800">
                                                <button
                                                    onClick={() => handleVoteUp(report)}
                                                    disabled={isOwner}
                                                    className={clsx(
                                                        "flex items-center gap-2 px-3 py-2 rounded-lg transition-all",
                                                        hasUpvoted
                                                            ? "bg-green-500/20 text-green-400"
                                                            : "bg-gray-800 text-gray-400 hover:bg-gray-700",
                                                        isOwner && "opacity-50 cursor-not-allowed"
                                                    )}
                                                    title={isOwner ? "Can't vote on your own report" : "Thumbs up"}
                                                >
                                                    <ThumbsUp className="w-4 h-4" />
                                                    <span className="font-medium">{report.thumbsUp?.length || 0}</span>
                                                </button>

                                                <button
                                                    onClick={() => handleVoteDown(report)}
                                                    disabled={isOwner}
                                                    className={clsx(
                                                        "flex items-center gap-2 px-3 py-2 rounded-lg transition-all",
                                                        hasDownvoted
                                                            ? "bg-red-500/20 text-red-400"
                                                            : "bg-gray-800 text-gray-400 hover:bg-gray-700",
                                                        isOwner && "opacity-50 cursor-not-allowed"
                                                    )}
                                                    title={isOwner ? "Can't vote on your own report" : "Thumbs down"}
                                                >
                                                    <ThumbsDown className="w-4 h-4" />
                                                    <span className="font-medium">{report.thumbsDown?.length || 0}</span>
                                                </button>

                                                <div className="ml-auto flex items-center gap-2">
                                                    <span className="text-sm text-gray-500">Score:</span>
                                                    <span className={clsx(
                                                        "text-lg font-bold",
                                                        report.netScore > 0 && "text-green-400",
                                                        report.netScore < 0 && "text-red-400",
                                                        report.netScore === 0 && "text-gray-400"
                                                    )}>
                                                        {report.netScore > 0 && '+'}{report.netScore || 0}
                                                    </span>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>
        </div>
    );
};

export default Reports;
