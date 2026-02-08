import { MapIcon, Zap, Shield, TrendingUp, ArrowRight } from 'lucide-react';
import { signInWithGoogle } from '../services/authService';
import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const Landing = () => {
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSignIn = async () => {
        setLoading(true);
        try {
            await signInWithGoogle();
            navigate('/');
        } catch (error) {
            console.error('Sign in error:', error);
            alert('Failed to sign in. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gray-950 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-cyan-900/20 via-gray-950 to-gray-950 flex items-center justify-center p-6">
            <div className="max-w-4xl w-full">
                {/* Hero Section */}
                <div className="text-center mb-12">
                    <div className="flex justify-center mb-6">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-2xl shadow-cyan-500/50 animate-pulse">
                            <MapIcon className="w-12 h-12 text-white" />
                        </div>
                    </div>
                    <h1 className="text-5xl md:text-6xl font-bold text-white mb-4 bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-500">
                        TrafficAI
                    </h1>
                    <p className="text-xl text-gray-400 mb-8 max-w-2xl mx-auto">
                        AI-powered traffic prediction and community-driven reports for smarter commutes in Mumbai
                    </p>

                    <button
                        onClick={handleSignIn}
                        disabled={loading}
                        className="group relative px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-600 hover:to-blue-700 text-white font-bold rounded-xl transition-all disabled:opacity-50 shadow-lg shadow-cyan-500/30 hover:shadow-cyan-500/50 flex items-center gap-3 mx-auto"
                    >
                        <svg className="w-6 h-6" viewBox="0 0 24 24">
                            <path fill="currentColor" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" />
                            <path fill="currentColor" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" />
                            <path fill="currentColor" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" />
                            <path fill="currentColor" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" />
                        </svg>
                        {loading ? 'Signing in...' : 'Sign in with Google'}
                        <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                    </button>
                </div>

                {/* Features Grid */}
                <div className="grid md:grid-cols-3 gap-6 mt-16">
                    <FeatureCard
                        icon={Zap}
                        title="Real-time Predictions"
                        description="LSTM-powered traffic forecasting with 81% accuracy"
                        color="cyan"
                    />
                    <FeatureCard
                        icon={TrendingUp}
                        title="Community Reports"
                        description="Crowdsourced traffic updates with voting system"
                        color="blue"
                    />
                    <FeatureCard
                        icon={Shield}
                        title="Anonymous & Secure"
                        description="Your identity stays private, data stays safe"
                        color="purple"
                    />
                </div>

                {/* Footer */}
                <p className="text-center text-gray-500 text-sm mt-12">
                    Powered by AI • Built for Mumbai Commuters
                </p>
            </div>
        </div>
    );
};

const FeatureCard = ({ icon: Icon, title, description, color }) => (
    <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-6 hover:border-gray-700 transition-all group">
        <div className={`w-12 h-12 rounded-xl bg-${color}-500/10 flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}>
            <Icon className={`w-6 h-6 text-${color}-400`} />
        </div>
        <h3 className="text-white font-bold text-lg mb-2">{title}</h3>
        <p className="text-gray-400 text-sm">{description}</p>
    </div>
);

export default Landing;
