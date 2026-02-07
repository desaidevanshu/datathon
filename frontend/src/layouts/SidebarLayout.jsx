import { LayoutDashboard, Map as MapIcon, Settings, Bell, Car, FileText } from 'lucide-react'
import { Link, useLocation } from 'react-router-dom'
import clsx from 'clsx'

const SidebarLayout = ({ children }) => {
    const location = useLocation();

    const navItems = [
        { icon: LayoutDashboard, label: 'Dashboard', path: '/' },
        { icon: MapIcon, label: 'Live Map', path: '/map' },
        { icon: Car, label: 'Traffic Analysis', path: '/analysis' }, // Placeholder
        { icon: Bell, label: 'Alerts', path: '/alerts' },           // Placeholder
        { icon: FileText, label: 'Reports', path: '/reports' },     // Placeholder
    ];

    return (
        <div className="flex h-screen bg-gray-950 text-gray-100 font-sans overflow-hidden">
            {/* Sidebar */}
            <aside className="w-20 lg:w-64 bg-gray-900 border-r border-gray-800 flex flex-col items-center lg:items-stretch py-6 transition-all duration-300">
                <div className="mb-8 px-4 flex items-center justify-center lg:justify-start gap-3">
                    <div className="w-8 h-8 rounded bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
                        <MapIcon className="w-5 h-5 text-white" />
                    </div>
                    <span className="hidden lg:block text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-gray-100 to-gray-400">TrafficAI</span>
                </div>

                <nav className="flex-1 flex flex-col gap-2 px-3">
                    {navItems.map((item) => {
                        const isActive = location.pathname === item.path;
                        const Icon = item.icon;

                        return (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={clsx(
                                    "flex items-center gap-3 px-3 py-3 rounded-xl transition-all duration-200 group",
                                    isActive
                                        ? "bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 shadow-[0_0_15px_rgba(6,182,212,0.15)]"
                                        : "text-gray-400 hover:bg-gray-800 hover:text-gray-100"
                                )}
                            >
                                <Icon className={clsx("w-5 h-5", isActive ? "text-cyan-400" : "group-hover:text-gray-100")} />
                                <span className="hidden lg:block font-medium">{item.label}</span>
                                {isActive && <div className="ml-auto w-1.5 h-1.5 rounded-full bg-cyan-400 shadow-[0_0_8px_rgba(6,182,212,0.8)] hidden lg:block" />}
                            </Link>
                        )
                    })}
                </nav>

                <div className="mt-auto px-3">
                    <button className="flex items-center gap-3 px-3 py-3 rounded-xl text-gray-400 hover:bg-gray-800 hover:text-gray-100 w-full transition-all">
                        <Settings className="w-5 h-5" />
                        <span className="hidden lg:block font-medium">Settings</span>
                    </button>
                </div>
            </aside>

            {/* Main Content */}
            <main className="flex-1 overflow-hidden relative flex flex-col bg-gray-950 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-gray-900 via-gray-950 to-gray-950">
                {children}
            </main>
        </div>
    )
}

export default SidebarLayout;
