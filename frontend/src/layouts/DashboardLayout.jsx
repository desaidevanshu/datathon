import React, { useState, useEffect } from 'react';
import { Outlet, useLocation, useNavigate } from 'react-router-dom';
import { LayoutDashboard, Map as MapIcon, Car, Bell, FileText, Settings, Search, Menu, User } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import clsx from 'clsx';

const DashboardLayout = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [isLoading, setIsLoading] = useState(true);

    // Navigation Items
    const navItems = [
        { path: '/dashboard/monitoring', label: 'Overview', icon: LayoutDashboard },
        { path: '/dashboard/map', label: 'Live Map', icon: MapIcon },
        { path: '/dashboard/analysis', label: 'Predictive AI', icon: Car },
        { path: '/dashboard/alerts', label: 'Alerts', icon: Bell },
        { path: '/dashboard/reports', label: 'Reports', icon: FileText },
    ];

    // Simulate System Initialization
    useEffect(() => {
        const timer = setTimeout(() => setIsLoading(false), 2000);
        return () => clearTimeout(timer);
    }, []);

    if (isLoading) {
        return <LoadingScreen />;
    }

    return (
        <div className="min-h-screen bg-black text-white font-sans selection:bg-cyan-500/30">
            {/* Top Navigation Bar */}
            <header className="fixed top-0 left-0 right-0 z-50 h-16 bg-black/80 backdrop-blur-md border-b border-white/10 flex items-center justify-between px-6">

                {/* Logo */}
                <div className="flex items-center gap-3 cursor-pointer" onClick={() => navigate('/')}>
                    <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.4)]">
                        <MapIcon className="w-5 h-5 text-white" />
                    </div>
                    <span className="text-xl font-bold tracking-wide">CITY<span className="text-cyan-400">BRAIN</span></span>
                </div>

                {/* Center Tabs */}
                <nav className="hidden md:flex items-center gap-1 bg-white/5 rounded-full p-1 border border-white/5">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        return (
                            <button
                                key={item.path}
                                onClick={() => navigate(item.path)}
                                className={clsx(
                                    "px-4 py-1.5 rounded-full text-sm font-medium transition-all duration-300 relative",
                                    isActive ? "text-white" : "text-gray-400 hover:text-white"
                                )}
                            >
                                {isActive && (
                                    <motion.div
                                        layoutId="activeTab"
                                        className="absolute inset-0 bg-cyan-600/20 border border-cyan-500/50 rounded-full shadow-[0_0_10px_rgba(6,182,212,0.3)]"
                                        initial={false}
                                        transition={{ type: "spring", stiffness: 500, damping: 30 }}
                                    />
                                )}
                                <span className="relative z-10 flex items-center gap-2">
                                    {/* <item.icon size={14} /> */}{/* Icons optional in top nav usually */}
                                    {item.label}
                                </span>
                            </button>
                        );
                    })}
                </nav>

                {/* Right Side Actions */}
                <div className="flex items-center gap-4">
                    <div className="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-full bg-green-500/10 border border-green-500/20">
                        <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
                        <span className="text-xs font-bold text-green-400 uppercase tracking-wider">System Online</span>
                    </div>
                    <div className="w-8 h-8 rounded-full bg-gray-800 border border-white/10 flex items-center justify-center hover:bg-gray-700 cursor-pointer transition-colors">
                        <User size={16} className="text-gray-400" />
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className={clsx(
                "pt-16 min-h-screen transition-all duration-300",
                location.pathname.includes('/map') ? "p-0 overflow-hidden h-screen" : "px-6 pb-6 pt-20"
            )}>
                <AnimatePresence mode="wait">
                    <motion.div
                        key={location.pathname}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                        className="h-full"
                    >
                        <Outlet />
                    </motion.div>
                </AnimatePresence>
            </main>
        </div>
    );
};

const LoadingScreen = () => (
    <div className="fixed inset-0 bg-black z-[100] flex flex-col items-center justify-center">
        <div className="relative w-24 h-24 mb-8">
            <div className="absolute inset-0 border-4 border-cyan-900/30 rounded-full"></div>
            <div className="absolute inset-0 border-4 border-t-cyan-500 rounded-full animate-spin"></div>
            <div className="absolute inset-4 bg-cyan-500/10 rounded-full blur-md animate-pulse"></div>
            <MapIcon className="absolute inset-0 m-auto text-cyan-500 w-8 h-8 animate-bounce" />
        </div>
        <div className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600 mb-2">
            CITYBRAIN
        </div>
        <div className="text-gray-500 font-mono text-sm animate-pulse">
            INITIALIZING SYSTEM MODULES...
        </div>

        {/* Loading Progress Bar */}
        <div className="w-64 h-1 bg-gray-900 rounded-full mt-6 overflow-hidden relative">
            <motion.div
                className="absolute inset-y-0 left-0 bg-cyan-500"
                initial={{ width: "0%" }}
                animate={{ width: "100%" }}
                transition={{ duration: 2, ease: "easeInOut" }}
            />
        </div>
    </div>
);

export default DashboardLayout;
