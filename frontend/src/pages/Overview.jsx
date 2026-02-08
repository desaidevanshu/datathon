import React, { useRef, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Activity, Shield, Cpu, ArrowRight, Zap, Globe, BarChart3, Brain, Map as MapIcon, ChevronDown, MousePointer2 } from 'lucide-react';
import { motion, useScroll, useTransform, useInView, useSpring } from 'framer-motion';

// --- Custom Cursor Component ---
const CustomCursor = () => {
    const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
    const [isHovering, setIsHovering] = useState(false);

    useEffect(() => {
        const updateMousePosition = (e) => {
            setMousePosition({ x: e.clientX, y: e.clientY });
        };

        const handleMouseOver = (e) => {
            if (e.target.tagName === 'BUTTON' || e.target.tagName === 'A' || e.target.closest('button')) {
                setIsHovering(true);
            } else {
                setIsHovering(false);
            }
        };

        window.addEventListener('mousemove', updateMousePosition);
        window.addEventListener('mouseover', handleMouseOver);

        return () => {
            window.removeEventListener('mousemove', updateMousePosition);
            window.removeEventListener('mouseover', handleMouseOver);
        };
    }, []);

    return (
        <>
            <motion.div
                className="fixed top-0 left-0 w-8 h-8 rounded-full border border-cyan-400 pointer-events-none z-[100] hidden md:block mix-blend-difference"
                animate={{
                    x: mousePosition.x - 16,
                    y: mousePosition.y - 16,
                    scale: isHovering ? 1.5 : 1,
                    borderColor: isHovering ? '#fff' : '#22d3ee'
                }}
                transition={{ type: "spring", stiffness: 500, damping: 28 }}
            />
            <motion.div
                className="fixed top-0 left-0 w-2 h-2 bg-cyan-400 rounded-full pointer-events-none z-[100] hidden md:block"
                animate={{
                    x: mousePosition.x - 4,
                    y: mousePosition.y - 4,
                }}
                transition={{ type: "spring", stiffness: 1500, damping: 50 }}
            />
        </>
    );
};

const ScrollSection = ({ children, className }) => {
    const ref = useRef(null);
    const isInView = useInView(ref, { amount: 0.5, once: false });

    return (
        <motion.div
            ref={ref}
            initial={{ opacity: 0, filter: 'blur(10px)', y: 50 }}
            animate={isInView ? { opacity: 1, filter: 'blur(0px)', y: 0 } : { opacity: 0, filter: 'blur(10px)', y: 50 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className={`min-h-screen flex flex-col items-center justify-center p-6 ${className}`}
        >
            {children}
        </motion.div>
    );
};

const Overview = () => {
    const navigate = useNavigate();

    return (
        <div className="relative bg-[#050505] text-white font-sans selection:bg-cyan-500/30 overflow-x-hidden curser-none">
            {/* Fonts Import - Removed to match Dashboard */}
            <style>{`
                body { cursor: default; } /* Hide default cursor if implementing fully custom one, else keep default */
            `}</style>

            <CustomCursor />

            {/* Dynamic Background */}
            <div className="fixed inset-0 z-0 pointer-events-none">
                <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-slate-900 via-[#050505] to-black" />
                <div className="absolute top-0 left-0 w-full h-full bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay"></div>

                {/* Moving Grid */}
                <div
                    className="absolute inset-0 opacity-20"
                    style={{
                        backgroundImage: 'linear-gradient(rgba(0, 255, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.1) 1px, transparent 1px)',
                        backgroundSize: '40px 40px',
                        transform: 'perspective(500px) rotateX(60deg)',
                        transformOrigin: 'top center',
                        maskImage: 'linear-gradient(to bottom, transparent, black 10%, black 90%, transparent)'
                    }}
                />
            </div>

            {/* Content Container */}
            <div className="relative z-10">

                {/* SECTION 1: HERO */}
                <ScrollSection>
                    <motion.div
                        initial={{ opacity: 0, scale: 0.5 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 1, type: "spring" }}
                        className="mb-10 relative group"
                    >
                        <div className="absolute inset-0 bg-cyan-500 blur-[100px] opacity-30 rounded-full animate-pulse group-hover:opacity-50 transition-opacity duration-500"></div>
                        <div className="relative bg-black/40 backdrop-blur-2xl border border-cyan-500/30 p-8 rounded-[2rem] shadow-[0_0_50px_rgba(6,182,212,0.2)] hover:shadow-[0_0_80px_rgba(6,182,212,0.4)] transition-all duration-500 border-t-cyan-400/50">
                            <Activity className="w-24 h-24 text-cyan-400 drop-shadow-[0_0_15px_rgba(34,211,238,0.8)]" />
                        </div>
                    </motion.div>

                    <h1 className="text-7xl md:text-9xl font-black tracking-tighter mb-4 text-center bg-clip-text text-transparent bg-gradient-to-b from-white via-cyan-100 to-cyan-900 drop-shadow-[0_0_30px_rgba(34,211,238,0.3)]">
                        CITY<span className="text-cyan-400">BRAIN</span>
                    </h1>

                    <div className="flex items-center gap-4 mb-12">
                        <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-cyan-500"></div>
                        <p className="text-xl md:text-3xl text-cyan-100/70 max-w-3xl text-center font-bold tracking-tight uppercase">
                            AI-Driven Traffic Neural Network
                        </p>
                        <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-cyan-500"></div>
                    </div>

                    <motion.div
                        animate={{ y: [0, 10, 0], opacity: [0.5, 1, 0.5] }}
                        transition={{ repeat: Infinity, duration: 2 }}
                        className="absolute bottom-10"
                    >
                        <ChevronDown className="text-cyan-400 w-10 h-10 drop-shadow-[0_0_10px_cyan]" />
                    </motion.div>
                </ScrollSection>

                {/* SECTION 2: LIVE METRICS */}
                <ScrollSection>
                    <div className="text-center mb-20">
                        <h2 className="text-5xl md:text-6xl font-black tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-green-400 to-emerald-600">System Status</h2>
                        <p className="text-emerald-100/60 text-xl font-medium">Real-time neural grid metrics.</p>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-3 gap-8 w-full max-w-6xl px-4">
                        <StatusCard
                            icon={<Shield className="w-10 h-10 text-emerald-400" />}
                            label="Grid Integrity"
                            value="100%"
                            sub="Secure & Online"
                            color="bg-emerald-500"
                            shadow="shadow-emerald-500/20"
                            delay={0.1}
                        />
                        <StatusCard
                            icon={<Cpu className="w-10 h-10 text-cyan-400" />}
                            label="AI Latency"
                            value="12ms"
                            sub="Optimal"
                            color="bg-cyan-500"
                            shadow="shadow-cyan-500/20"
                            delay={0.2}
                        />
                        <StatusCard
                            icon={<Globe className="w-10 h-10 text-violet-400" />}
                            label="Nodes Active"
                            value="1,204"
                            sub="Synced"
                            color="bg-violet-500"
                            shadow="shadow-violet-500/20"
                            delay={0.3}
                        />
                    </div>
                </ScrollSection>

                {/* SECTION 3: INTELLIGENT ROUTING */}
                <ScrollSection className="flex-row gap-12">
                    <div className="flex flex-col md:flex-row items-center gap-16 max-w-7xl w-full px-4">
                        <div className="flex-1 space-y-8 text-left relative z-10">
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-cyan-950/50 border border-cyan-500/50 text-cyan-300 text-sm font-bold uppercase tracking-wider shadow-[0_0_20px_rgba(6,182,212,0.3)]">
                                <MapIcon size={16} /> Quantum Routing
                            </div>
                            <h2 className="text-6xl md:text-7xl font-black tracking-tight leading-none">
                                Navigate <br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-600">Without Limits.</span>
                            </h2>
                            <p className="text-2xl text-cyan-100/60 leading-relaxed font-normal">
                                Vehicle-specific routing engine. Optimized for EV, Petrol, Diesel.
                                <span className="text-cyan-400 font-semibold"> The most cost-effective path, calculated in milliseconds.</span>
                            </p>
                            <ul className="space-y-6 text-xl text-gray-300 font-medium">
                                <li className="flex items-center gap-4 group">
                                    <div className="p-2 rounded-lg bg-yellow-900/20 border border-yellow-500/30 group-hover:bg-yellow-500/20 transition-colors">
                                        <Zap className="text-yellow-400" />
                                    </div>
                                    Real-time Fuel Cost Estimation
                                </li>
                                <li className="flex items-center gap-4 group">
                                    <div className="p-2 rounded-lg bg-blue-900/20 border border-blue-500/30 group-hover:bg-blue-500/20 transition-colors">
                                        <Globe className="text-blue-400" />
                                    </div>
                                    Multi-modal Route Comparison
                                </li>
                            </ul>
                        </div>
                        <div className="flex-1 relative group perspective-1000">
                            <div className="absolute inset-0 bg-gradient-to-tr from-cyan-500 to-blue-600 blur-[120px] opacity-20 group-hover:opacity-40 transition-opacity duration-700"></div>
                            <div className="relative bg-black/60 backdrop-blur-xl border border-white/10 rounded-[3rem] p-12 aspect-square flex items-center justify-center transform group-hover:rotate-y-6 transition-transform duration-700 border-t-white/20 shadow-2xl">
                                <MapIcon className="w-40 h-40 text-cyan-500 drop-shadow-[0_0_30px_rgba(6,182,212,0.5)]" />
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="px-6 py-2 bg-black/80 rounded-full border border-cyan-500/30 text-cyan-400 font-mono text-xs uppercase tracking-widest backdrop-blur-md">
                                        Map Visualization
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ScrollSection>

                {/* SECTION 4: AI PREDICTION */}
                <ScrollSection>
                    <div className="flex flex-col md:flex-row-reverse items-center gap-16 max-w-7xl w-full px-4">
                        <div className="flex-1 space-y-8 text-left relative z-10">
                            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-fuchsia-950/50 border border-fuchsia-500/50 text-fuchsia-300 text-sm font-bold uppercase tracking-wider shadow-[0_0_20px_rgba(232,121,249,0.3)]">
                                <Brain size={16} /> Predictive AI
                            </div>
                            <h2 className="text-6xl md:text-7xl font-black tracking-tight leading-none">
                                See the Future <br />
                                <span className="text-transparent bg-clip-text bg-gradient-to-r from-fuchsia-400 to-purple-600">Before it Happens.</span>
                            </h2>
                            <p className="text-2xl text-fuchsia-100/60 leading-relaxed font-normal">
                                LSTM Neural Layouts analyze historical vectors to predict bottlenecks hours in advance.
                                <span className="text-fuchsia-400 font-semibold"> "Smart Break" technology recommends the optimal departure time.</span>
                            </p>
                            <ul className="space-y-6 text-xl text-gray-300 font-medium">
                                <li className="flex items-center gap-4 group">
                                    <div className="p-2 rounded-lg bg-pink-900/20 border border-pink-500/30 group-hover:bg-pink-500/20 transition-colors">
                                        <BarChart3 className="text-pink-400" />
                                    </div>
                                    94% Prediction Accuracy
                                </li>
                                <li className="flex items-center gap-4 group">
                                    <div className="p-2 rounded-lg bg-green-900/20 border border-green-500/30 group-hover:bg-green-500/20 transition-colors">
                                        <ArrowRight className="text-green-400" />
                                    </div>
                                    Smart Departure Recommendations
                                </li>
                            </ul>
                        </div>
                        <div className="flex-1 relative group perspective-1000">
                            <div className="absolute inset-0 bg-gradient-to-bl from-fuchsia-500 to-purple-600 blur-[120px] opacity-20 group-hover:opacity-40 transition-opacity duration-700"></div>
                            <div className="relative bg-black/60 backdrop-blur-xl border border-white/10 rounded-[3rem] p-12 aspect-square flex items-center justify-center transform group-hover:-rotate-y-6 transition-transform duration-700 border-t-white/20 shadow-2xl">
                                <Brain className="w-40 h-40 text-fuchsia-500 drop-shadow-[0_0_30px_rgba(232,121,249,0.5)]" />
                                <div className="absolute inset-0 flex items-center justify-center">
                                    <div className="px-6 py-2 bg-black/80 rounded-full border border-fuchsia-500/30 text-fuchsia-400 font-mono text-xs uppercase tracking-widest backdrop-blur-md">
                                        Neural Network
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </ScrollSection>

                {/* SECTION 5: CTA */}
                <ScrollSection>
                    <div className="relative">
                        <div className="absolute inset-0 bg-cyan-500 blur-[150px] opacity-20"></div>
                        <h2 className="text-6xl md:text-8xl font-black mb-12 text-center tracking-tight leading-tight relative z-10">
                            Ready to take <br /> <span className="text-transparent bg-clip-text bg-gradient-to-b from-white to-cyan-500 drop-shadow-[0_0_30px_rgba(34,211,238,0.5)]">Control?</span>
                        </h2>
                    </div>

                    <button
                        onClick={() => navigate('/dashboard')}
                        className="group relative px-12 py-6 bg-white text-black text-2xl font-black rounded-full transition-all duration-300 transform hover:scale-105 hover:shadow-[0_0_60px_rgba(255,255,255,0.4)] flex items-center gap-6 cursor-none z-20 overflow-hidden"
                    >
                        <div className="absolute inset-0 bg-gradient-to-r from-cyan-200 via-white to-cyan-200 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                        <span className="relative z-10">LAUNCH SYSTEM</span>
                        <ArrowRight className="w-8 h-8 relative z-10 group-hover:translate-x-2 transition-transform" />
                    </button>

                    <div className="mt-12 flex items-center gap-6 text-gray-500 text-sm font-mono uppercase tracking-widest">
                        <span className="flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" /> Mainnet Online</span>
                        <span>•</span>
                        <span>v2.4.0 Stable</span>
                    </div>
                </ScrollSection>
            </div>
        </div>
    );
};

const StatusCard = ({ icon, label, value, sub, color, shadow, delay }) => (
    <motion.div
        initial={{ y: 50, opacity: 0 }}
        whileInView={{ y: 0, opacity: 1 }}
        transition={{ delay, duration: 0.8, type: "spring" }}
        className={`bg-black/40 backdrop-blur-xl border border-white/5 p-10 rounded-[2.5rem] flex flex-col items-center gap-6 hover:bg-white/5 transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl ${shadow}`}
    >
        <div className={`p-6 rounded-3xl mb-2 border border-white/5 shadow-inner ${color} bg-opacity-10`}>
            {icon}
        </div>
        <div className="text-center space-y-2">
            <div className="text-sm text-gray-400 uppercase tracking-[0.2em] font-bold">{label}</div>
            <div className="text-5xl font-black text-white">{value}</div>
            <div className="flex items-center justify-center gap-2 px-3 py-1 bg-white/5 rounded-full border border-white/5">
                <div className={`w-2 h-2 rounded-full ${color} animate-pulse shadow-[0_0_10px_currentColor]`}></div>
                <span className="text-sm text-gray-300 font-medium">{sub}</span>
            </div>
        </div>
    </motion.div>
);

export default Overview;
