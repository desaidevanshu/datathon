import { useState, useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import axios from 'axios'
import { MapPin, Navigation, Navigation2, AlertTriangle, Search, ChevronLeft, Fuel, Banknote, Clock, Leaf } from 'lucide-react'
import clsx from 'clsx'
import { Link } from 'react-router-dom'

// Mock Geocoding for Mumbai
const MOCK_LOCATIONS = {
    'mumbai': { lat: 19.0760, lon: 72.8777 },
    'bandra': { lat: 19.0596, lon: 72.8295 },
    'andheri': { lat: 19.1136, lon: 72.8697 },
    'juhu': { lat: 19.1075, lon: 72.8263 },
    'dadar': { lat: 19.0178, lon: 72.8478 },
    'churchgate': { lat: 18.9322, lon: 72.8264 },
    'thane': { lat: 19.2183, lon: 72.9781 },
    'navi mumbai': { lat: 19.0330, lon: 73.0297 },
    'powai': { lat: 19.1176, lon: 72.9060 },
    'worli': { lat: 19.0166, lon: 72.8123 }
};

// Helper functions for cost calculations
const calculateCost = (distanceKm, engineType) => {
    const fuelPrices = {
        'Petrol': 100,
        'Diesel': 90,
        'CNG': 75,
        'EV': 10
    };
    const efficiency = {
        'Petrol': 15, // km/L
        'Diesel': 20,
        'CNG': 18,
        'EV': 5 // km/kWh
    };
    const consumption = distanceKm / efficiency[engineType];
    return Math.round(consumption * fuelPrices[engineType]);
};

const calculateFuel = (distanceKm, engineType) => {
    const efficiency = {
        'Petrol': 15,
        'Diesel': 20,
        'CNG': 18,
        'EV': 5
    };
    return distanceKm / efficiency[engineType]; // Return number for calculations
};

function FullMap() {
    const mapContainer = useRef(null)
    const map = useRef(null)
    const [startLoc, setStartLoc] = useState('')
    const [destLoc, setDestLoc] = useState('')

    // New State for Multi-Route
    const [allRoutes, setAllRoutes] = useState([])
    const [selectedRouteIndex, setSelectedRouteIndex] = useState(0)
    const [congestionPrediction, setCongestionPrediction] = useState(null)
    const [smartInsights, setSmartInsights] = useState(null)
    const [aiExplanation, setAiExplanation] = useState(null)

    const [isNavigating, setIsNavigating] = useState(false)
    const [loading, setLoading] = useState(false)

    const [engineType, setEngineType] = useState('Petrol') // Petrol, Diesel, EV, CNG
    const [recentSearches, setRecentSearches] = useState([])

    // Dynamic Data Simulation
    const [dynamicStats, setDynamicStats] = useState({ delay: 0, fuel_adj: 0 })

    useEffect(() => {
        const saved = localStorage.getItem('recentSearches');
        if (saved) setRecentSearches(JSON.parse(saved));
    }, []);

    const saveRecentSearch = (start, dest) => {
        const newSearch = { start, dest, timestamp: Date.now() };
        const updated = [newSearch, ...recentSearches.filter(s =>
            !(s.start === start && s.dest === dest)
        )].slice(0, 5); // Keep last 5
        setRecentSearches(updated);
        localStorage.setItem('recentSearches', JSON.stringify(updated));
    };

    const handleSwap = () => {
        setStartLoc(destLoc);
        setDestLoc(startLoc);
    };

    const handleCurrentLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(async (position) => {
                const { latitude, longitude } = position.coords;
                // Reverse Geocoding (Mock or Real)
                try {
                    const response = await axios.get(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}`);
                    if (response.data && response.data.display_name) {
                        // Extract a shorter name for display if possible, or use full
                        const name = response.data.address.suburb || response.data.address.city || "Current Location";
                        setStartLoc(name);
                    } else {
                        setStartLoc(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
                    }
                } catch (e) {
                    setStartLoc(`${latitude.toFixed(4)}, ${longitude.toFixed(4)}`);
                }
            }, (error) => {
                console.error("Geolocation error:", error);
                alert("Could not pull current location.");
            });
        }
    };

    useEffect(() => {
        if (map.current) return;

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            style: {
                version: 8,
                sources: {
                    'osm': {
                        type: 'raster',
                        tiles: [
                            'https://a.tile.openstreetmap.org/{z}/{x}/{y}.png',
                            'https://b.tile.openstreetmap.org/{z}/{x}/{y}.png',
                            'https://c.tile.openstreetmap.org/{z}/{x}/{y}.png'
                        ],
                        tileSize: 256,
                        attribution: '&copy; OpenStreetMap Contributors',
                        maxzoom: 19
                    }
                },
                layers: [{
                    id: 'osm',
                    type: 'raster',
                    source: 'osm',
                    minzoom: 0,
                    maxzoom: 19,
                    paint: {
                        'raster-fade-duration': 0
                    }
                }]
            },
            center: [72.8777, 19.0760], // Mumbai
            zoom: 11,
            maxZoom: 19, // Limit zoom to prevent 400 errors from OSM tiles
            minZoom: 0
        });

        map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
        map.current.addControl(new maplibregl.GeolocateControl({
            positionOptions: { enableHighAccuracy: true },
            trackUserLocation: true
        }), 'top-right');

        // Initial Resize
        setTimeout(() => { map.current?.resize() }, 100);
    }, []);

    // Ensure map resizes correctly after animations/layout changes
    useEffect(() => {
        const resizeMap = () => { if (map.current) map.current.resize(); };
        const interval = setInterval(resizeMap, 500); // Check repeatedly for a short time
        setTimeout(() => clearInterval(interval), 2000);
        window.addEventListener('resize', resizeMap);
        return () => window.removeEventListener('resize', resizeMap);
    }, []);

    // Simulate Live Traffic Updates
    useEffect(() => {
        if (!isNavigating) return;

        const interval = setInterval(() => {
            // Randomly fluctuate delay (0-5 mins) and fuel efficiency slightly
            setDynamicStats({
                delay: Math.floor(Math.random() * 5),
                fuel_adj: (Math.random() * 0.1 - 0.05) // +/- 0.05L
            });
        }, 5000);

        return () => clearInterval(interval);
    }, [isNavigating]);

    // Update map when selected route changes
    useEffect(() => {
        if (!map.current || allRoutes.length === 0) return;
        renderRoutesOnMap();
    }, [selectedRouteIndex, allRoutes]);

    const getCoords = async (query) => {
        const key = query.toLowerCase().trim();
        if (MOCK_LOCATIONS[key]) return MOCK_LOCATIONS[key];
        try {
            const response = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=in&limit=1`);
            if (response.data?.[0]) {
                return { lat: parseFloat(response.data[0].lat), lon: parseFloat(response.data[0].lon) };
            }
        } catch (e) {
            console.error("Geocoding failed", e);
        }
        return null;
    }

    const renderRoutesOnMap = () => {
        // Clear old route layers
        // Note: MapLibre doesn't easily allow removing layers/sources cleanly without check, 
        // so we'll just update data if possible or remove if we track IDs.
        // For simplicity, we assume generic names 'route-0', 'route-1' etc.

        allRoutes.forEach((route, index) => {
            const layerId = `route-${index}`;
            const isSelected = index === selectedRouteIndex;

            // Distinct colors for top 3 routes
            const routeColors = ['#22c55e', '#3b82f6', '#f97316']; // Green, Blue, Orange
            const baseColor = routeColors[index % routeColors.length];

            const color = isSelected ? baseColor : '#9ca3af'; // Selected gets color, others gray (or we can keep them colored but dim)
            // User asked for "proper colour", implying visibility. Let's make them all colored but utilize opacity/width for selection.
            const displayColor = baseColor;

            const opacity = isSelected ? 1 : 0.6;
            const width = isSelected ? 6 : 4;
            const zIndex = isSelected ? 10 : 5;

            // GeoJSON Data
            const geojson = {
                'type': 'Feature',
                'properties': {},
                'geometry': {
                    'type': 'LineString',
                    'coordinates': route.geometry
                }
            };

            if (!map.current.getSource(layerId)) {
                map.current.addSource(layerId, { type: 'geojson', data: geojson });

                // Add Layer
                map.current.addLayer({
                    'id': layerId,
                    'type': 'line',
                    'source': layerId,
                    'layout': { 'line-join': 'round', 'line-cap': 'round' },
                    'paint': {
                        'line-color': displayColor,
                        'line-width': width,
                        'line-opacity': opacity
                    }
                });

                // Add Glow for selected only (dynamic)
                if (isSelected) {
                    if (!map.current.getLayer('route-glow')) {
                        map.current.addLayer({
                            'id': 'route-glow',
                            'type': 'line',
                            'source': layerId,
                            'layout': { 'line-join': 'round', 'line-cap': 'round' },
                            'paint': {
                                'line-color': '#22c55e',
                                'line-width': 12,
                                'line-opacity': 0.4,
                                'line-blur': 12
                            }
                        }, layerId); // Put glow *under* the line
                    } else {
                        // Update glow source
                        map.current.getSource('route-glow').setData(geojson);
                    }
                }

                // Click to select
                map.current.on('click', layerId, () => {
                    setSelectedRouteIndex(index);
                });

                // Hover effect
                map.current.on('mouseenter', layerId, () => map.current.getCanvas().style.cursor = 'pointer');
                map.current.on('mouseleave', layerId, () => map.current.getCanvas().style.cursor = '');

            } else {
                // Update existing
                map.current.getSource(layerId).setData(geojson);
                map.current.setPaintProperty(layerId, 'line-color', displayColor);
                map.current.setPaintProperty(layerId, 'line-width', width);
                map.current.setPaintProperty(layerId, 'line-opacity', opacity);

                if (isSelected) {
                    map.current.moveLayer(layerId); // Bring to top
                    // Update glow
                    if (map.current.getSource('route-glow')) {
                        map.current.getSource('route-glow').setData(geojson);
                    }
                }
            }
        });

        // Fit bounds to ALL routes - only if we haven't just loaded them
        // (to avoid double-fitting when routes first load)
        if (allRoutes.length > 0 && allRoutes[0].geometry && allRoutes[0].geometry.length > 0) {
            const bounds = new maplibregl.LngLatBounds();
            allRoutes.forEach(route => {
                if (route.geometry && Array.isArray(route.geometry)) {
                    route.geometry.forEach(coord => {
                        // coord is [lon, lat]
                        if (Array.isArray(coord) && coord.length >= 2) {
                            bounds.extend(coord);
                        }
                    });
                }
            });

            if (!bounds.isEmpty()) {
                map.current.fitBounds(bounds, {
                    padding: 100,
                    maxZoom: 15
                });
            }
        }
    }

    const handleRoute = async () => {
        setLoading(true);
        setAllRoutes([]);
        setCongestionPrediction(null);

        let startCoords = await getCoords(startLoc || 'bandra');
        let destCoords = await getCoords(destLoc || 'andheri');

        if (!startCoords || !destCoords) {
            alert("Could not find location.");
            setLoading(false);
            return;
        }

        try {
            const response = await axios.post('https://datathon-w1z4.onrender.com/api/route', {
                start: startCoords,
                destination: destCoords,
                engine_type: engineType // Send Engine Type
            });

            const data = response.data;

            // Start/End Markers
            // Clean up old markers
            const oldMarkers = document.getElementsByClassName('maplibregl-marker');
            while (oldMarkers[0]) oldMarkers[0].parentNode.removeChild(oldMarkers[0]);

            new maplibregl.Marker({ color: '#22c55e' })
                .setLngLat([startCoords.lon, startCoords.lat])
                .addTo(map.current);
            new maplibregl.Marker({ color: '#ef4444' })
                .setLngLat([destCoords.lon, destCoords.lat])
                .addTo(map.current);

            // Transform backend response to match expected structure
            // Process routes from backend new structure
            const routes = (data.routes || []).map((r, idx) => ({
                id: `route-${idx}`,
                geometry: r.points || r.geometry, // Backend uses 'points' or 'geometry'
                duration_min: r.eta_min,
                distance_km: r.distance_km,
                estimated_cost_inr: calculateCost(r.distance_km, engineType),
                fuel_consumption_liters: calculateFuel(r.distance_km, engineType),
                is_fastest: idx === 0,
                is_eco: idx === 1, // Assume 2nd is eco for now if available
                congestion_level: r.congestion_level
            }));

            // Fallback for old structure if data.routes is missing (just in case)
            if (routes.length === 0 && data.route) {
                routes.push({
                    id: 'route-main',
                    geometry: data.route,
                    duration_min: Math.round(data.duration / 60),
                    distance_km: (data.distance || 10),
                    estimated_cost_inr: calculateCost((data.distance || 10), engineType),
                    fuel_consumption_liters: calculateFuel((data.distance || 10), engineType),
                    is_fastest: true,
                    is_eco: false
                });

                if (data.alternates && data.alternates.length > 0) {
                    data.alternates.forEach((altRoute, i) => {
                        routes.push({
                            id: `alt-route-${i}`,
                            geometry: altRoute,
                            duration_min: Math.round((data.duration / 60) * 1.15),
                            distance_km: (data.distance * 1.1),
                            estimated_cost_inr: calculateCost((data.distance * 1.1), engineType),
                            fuel_consumption_liters: calculateFuel((data.distance * 1.1), engineType),
                            is_fastest: false,
                            is_eco: i === 0
                        });
                    });
                }
            }

            setAllRoutes(routes);
            setSelectedRouteIndex(0);
            setCongestionPrediction(data.congestion || []);
            console.log("Backend Response Data:", data);

            // Smart Recommendations
            if (data.analysis_context && data.analysis_context.smart_recommendations) {
                setSmartInsights(data.analysis_context.smart_recommendations);
            } else {
                setSmartInsights(null);
            }

            console.log("AI Insight Raw:", data.ai_insight);
            setAiExplanation(data.ai_insight || data.route_analysis?.ai_explanation || data.route_analysis?.ai_route_briefing || null);
            setIsNavigating(true);
            saveRecentSearch(startLoc || 'Bandra', destLoc || 'Andheri');

            // Immediately fit bounds to show the route
            if (routes.length > 0 && routes[0].geometry && routes[0].geometry.length > 0) {
                const bounds = new maplibregl.LngLatBounds();
                routes.forEach(route => {
                    if (route.geometry && Array.isArray(route.geometry)) {
                        route.geometry.forEach(coord => {
                            // coord is [lon, lat]
                            if (Array.isArray(coord) && coord.length >= 2) {
                                bounds.extend(coord);
                            }
                        });
                    }
                });

                // Fit bounds with padding
                setTimeout(() => {
                    if (map.current && !bounds.isEmpty()) {
                        map.current.fitBounds(bounds, {
                            padding: 80,
                            maxZoom: 15,
                            duration: 1000
                        });
                    }
                }, 100);
            }

        } catch (error) {
            console.error("Routing failed:", error);
            alert("Routing failed. Check console.");
        } finally {
            setLoading(false);
        }
    };

    const activeRoute = allRoutes[selectedRouteIndex] || null;

    return (
        <div className="relative w-full h-full bg-gray-100 overflow-hidden">
            <div ref={mapContainer} className="absolute inset-0 z-0 h-full w-full" />

            <div className="absolute top-4 left-20 z-10 flex flex-col gap-4 w-[400px] pointer-events-none">
                <div className="pointer-events-auto space-y-4 max-h-[calc(100vh-2rem)] overflow-y-auto pr-2 pb-10 scrollbar-hide">
                    <Link to="/" className="flex items-center gap-2 text-gray-700 hover:text-black bg-white/90 backdrop-blur px-4 py-2 rounded-lg w-fit border border-gray-200 transition-all shadow-md">
                        <ChevronLeft className="w-4 h-4" /> Back to Dashboard
                    </Link>

                    <div className="bg-white/95 backdrop-blur-md border border-gray-200 rounded-2xl p-5 shadow-2xl">
                        {/* Inputs */}
                        <div className="space-y-3 mb-6 relative">
                            {/* Swap Button */}
                            <button
                                onClick={handleSwap}
                                className="absolute right-4 top-[52px] z-20 p-2 bg-white hover:bg-gray-50 rounded-full shadow-lg border border-gray-100 text-gray-600 transition-all hover:scale-110 active:scale-95"
                                title="Swap Locations"
                            >
                                <Navigation className="w-4 h-4 rotate-45 text-blue-600" />
                            </button>

                            <div className="relative group">
                                <div className="absolute left-3 top-3 w-2 h-2 rounded-full bg-green-500 ring-4 ring-green-100 group-focus-within:ring-green-200 transition-all" />
                                <input
                                    type="text"
                                    placeholder="Start Location"
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl py-2.5 pl-10 pr-10 focus:ring-2 focus:ring-blue-500 outline-none text-gray-800 font-medium"
                                    value={startLoc}
                                    onChange={(e) => setStartLoc(e.target.value)}
                                />
                                <button
                                    onClick={handleCurrentLocation}
                                    className="absolute right-3 top-2.5 text-blue-500 hover:text-blue-700 transition-colors p-1 hover:bg-blue-50 rounded-lg"
                                    title="Use Current Location"
                                >
                                    <MapPin size={18} />
                                </button>
                            </div>

                            <div className="relative group">
                                <div className="absolute left-3 top-3 w-2 h-2 rounded-full bg-red-500 ring-4 ring-red-100 group-focus-within:ring-red-200 transition-all" />
                                <input
                                    type="text"
                                    placeholder="Destination"
                                    className="w-full bg-gray-50 border border-gray-200 rounded-xl py-2.5 pl-10 pr-4 focus:ring-2 focus:ring-blue-500 outline-none text-gray-800 font-medium"
                                    value={destLoc}
                                    onChange={(e) => setDestLoc(e.target.value)}
                                />
                            </div>

                            {/* Engine Type Selector */}
                            <div className="relative">
                                <select
                                    value={engineType}
                                    onChange={(e) => setEngineType(e.target.value)}
                                    className="w-full appearance-none bg-gray-50 border border-gray-200 rounded-xl py-2.5 px-4 focus:ring-2 focus:ring-blue-500 outline-none text-gray-700 font-medium cursor-pointer"
                                >
                                    <option value="Petrol">Petrol (₹100/L)</option>
                                    <option value="Diesel">Diesel (₹90/L)</option>
                                    <option value="CNG">CNG (₹75/kg)</option>
                                    <option value="EV">EV (₹10/unit)</option>
                                </select>
                                <div className="absolute right-4 top-3.5 pointer-events-none text-gray-500">
                                    <Fuel size={16} />
                                </div>
                            </div>

                            <button
                                onClick={handleRoute}
                                disabled={loading}
                                className={clsx(
                                    "w-full font-bold py-3.5 rounded-xl shadow-lg transition-all flex justify-center items-center gap-2 transform active:scale-[0.98]",
                                    loading
                                        ? "bg-gray-100 cursor-wait text-gray-400 border border-gray-200"
                                        : "bg-gradient-to-r from-indigo-600 via-blue-600 to-cyan-600 hover:from-indigo-500 hover:to-cyan-500 text-white shadow-blue-500/25 ring-1 ring-white/20"
                                )}
                            >
                                {loading ? (
                                    <>
                                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                                        <span>Calculating Route...</span>
                                    </>
                                ) : (
                                    <>
                                        <Navigation2 className="w-5 h-5" />
                                        <span>{isNavigating ? 'Update Route' : 'Find Best Route'}</span>
                                    </>
                                )}
                            </button>
                        </div>

                    </div>

                    {/* AI Traffic Insights (Moved Top) */}
                    {aiExplanation && (
                        <div className="mb-6 p-4 bg-gradient-to-br from-indigo-50 to-blue-50 rounded-xl border border-indigo-100 shadow-sm animate-in fade-in slide-in-from-bottom-2 duration-500">
                            <div className="flex items-start gap-3">
                                <div className="p-2.5 bg-indigo-600 text-white rounded-xl shadow-indigo-200 shadow-lg flex-shrink-0">
                                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                                    </svg>
                                </div>
                                <div className="flex-1">
                                    <div className="flex items-center gap-2 mb-1.5">
                                        <p className="text-xs font-bold text-indigo-700 uppercase tracking-wider">Smart Traffic Pilot</p>
                                        <span className="text-[10px] bg-indigo-100 text-indigo-700 px-2 py-0.5 rounded-full font-bold border border-indigo-200">AI LIVE</span>
                                    </div>
                                    <p className="text-sm text-gray-700 leading-relaxed font-medium">
                                        {aiExplanation}
                                    </p>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Smart Mobility Suggestions (New) */}
                    {smartInsights && (
                        <div className="mb-6 p-4 bg-gradient-to-br from-emerald-50 to-teal-50 rounded-xl border border-emerald-100 shadow-sm animate-in fade-in slide-in-from-bottom-3 duration-700">
                            <div className="flex items-center gap-2 mb-3">
                                <div className="p-1.5 bg-emerald-500 text-white rounded-lg shadow-sm">
                                    <Activity className="w-4 h-4" />
                                </div>
                                <h3 className="text-sm font-bold text-emerald-800 uppercase tracking-wide">Smart Mobility</h3>
                            </div>
                            <div className="space-y-3">
                                {smartInsights.optimal_departure && (
                                    <div className="p-3 bg-white rounded-lg border border-emerald-100 shadow-sm">
                                        <div className="text-xs text-emerald-600 font-bold uppercase mb-1">Optimal Departure</div>
                                        <div className="text-sm text-gray-700 font-medium">{smartInsights.optimal_departure}</div>
                                    </div>
                                )}
                                {smartInsights.smart_break && (
                                    <div className="p-3 bg-white rounded-lg border border-blue-100 shadow-sm">
                                        <div className="text-xs text-blue-600 font-bold uppercase mb-1">Smart BreakLogic</div>
                                        <div className="text-sm text-gray-700 font-medium">{smartInsights.smart_break}</div>
                                    </div>
                                )}
                            </div>
                        </div>
                    )}

                    {/* Recent Searches */}
                    {!isNavigating && recentSearches.length > 0 && (
                        <div className="mb-4">
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider mb-2">Recent Searches</h3>
                            <div className="space-y-2">
                                {recentSearches.map((search, idx) => (
                                    <div
                                        key={idx}
                                        onClick={() => {
                                            setStartLoc(search.start);
                                            setDestLoc(search.dest);
                                        }}
                                        className="flex items-center justify-between p-2 rounded-lg bg-gray-50 hover:bg-gray-100 cursor-pointer transition-colors border border-transparent hover:border-gray-200"
                                    >
                                        <div className="flex items-center gap-2 overflow-hidden">
                                            <Clock size={12} className="text-gray-400 flex-shrink-0" />
                                            <span className="text-sm text-gray-700 truncate">{search.start} <span className="text-gray-400">→</span> {search.dest}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Route Options List */}
                    {allRoutes.length > 0 && (
                        <div className="space-y-3 animate-in slide-in-from-left duration-300">
                            <h3 className="text-xs font-bold text-gray-400 uppercase tracking-wider">Alternative Routes ({allRoutes.length})</h3>
                            {(() => {
                                const routeColors = ['#22c55e', '#3b82f6', '#f97316'];
                                return allRoutes.map((route, idx) => (
                                    <div
                                        key={route.id}
                                        onClick={() => setSelectedRouteIndex(idx)}
                                        className={clsx(
                                            "p-3 rounded-xl border transition-all cursor-pointer relative overflow-hidden",
                                            selectedRouteIndex === idx
                                                ? "bg-white border-gray-300 shadow-md ring-2 ring-opacity-50"
                                                : "bg-white border-gray-100 hover:bg-gray-50 hover:border-gray-200"
                                        )}
                                        style={{ borderColor: selectedRouteIndex === idx ? routeColors[idx % 3] : '' }}
                                    >
                                        <div className="absolute left-0 top-0 bottom-0 w-1.5" style={{ backgroundColor: routeColors[idx % 3] }}></div>
                                        <div className="flex justify-between items-start mb-2 pl-2">
                                            <div>
                                                <div className="flex items-center gap-2 mb-1">
                                                    <span className={clsx("text-lg font-bold font-mono", selectedRouteIndex === idx ? "text-blue-700" : "text-gray-700")}>
                                                        {Math.round(route.duration_min + (selectedRouteIndex === idx ? dynamicStats.delay : 0))} min
                                                    </span>
                                                    {route.is_eco && (
                                                        <span className="bg-green-100 text-green-700 text-[10px] font-bold px-2 py-0.5 rounded-full flex items-center gap-1">
                                                            <Leaf className="w-3 h-3" /> ECO
                                                        </span>
                                                    )}
                                                    {route.is_fastest && (
                                                        <span className="bg-blue-100 text-blue-700 text-[10px] font-bold px-2 py-0.5 rounded-full">FASTEST</span>
                                                    )}
                                                </div>
                                                <p className="text-xs font-semibold text-gray-600">{route.label || `Route ${idx + 1}`}</p>
                                                <p className="text-xs text-gray-500">{route.distance_km} km • {route.congestion_level} congestion</p>

                                                {/* AI Prediction for this route */}
                                                {route.ai_prediction && (
                                                    <div className="mt-2 p-2 bg-blue-50 rounded-lg border border-blue-100">
                                                        <div className="flex items-start gap-2">
                                                            <svg className="w-3 h-3 text-blue-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                                                            </svg>
                                                            <p className="text-[10px] text-blue-700 leading-relaxed">{route.ai_prediction}</p>
                                                        </div>
                                                        {route.confidence_score && (
                                                            <p className="text-[9px] text-blue-500 mt-1">Confidence: {route.confidence_score}%</p>
                                                        )}
                                                    </div>
                                                )}
                                            </div>
                                            <div className="text-right">
                                                <p className="text-sm font-bold text-gray-800">₹{Math.round(route.estimated_cost_inr)}</p>
                                            </div>
                                        </div>

                                        {/* Detailed Stats for Selected */}
                                        {selectedRouteIndex === idx && (
                                            <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-100/80">
                                                <div className="flex flex-col items-center p-2 rounded-lg bg-blue-50/50">
                                                    <Fuel className="w-4 h-4 text-blue-600 mb-1" />
                                                    <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wide">{engineType === 'EV' ? 'Power' : 'Fuel'}</p>
                                                    <p className="text-sm font-bold text-gray-800">
                                                        {(Number(route.fuel_consumption_liters) + dynamicStats.fuel_adj).toFixed(1)} <span className="text-xs font-normal text-gray-500">{engineType === 'CNG' ? 'kg' : engineType === 'EV' ? 'kWh' : 'L'}</span>
                                                    </p>
                                                </div>
                                                <div className="flex flex-col items-center p-2 rounded-lg bg-green-50/50">
                                                    <Banknote className="w-4 h-4 text-green-600 mb-1" />
                                                    <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wide">Cost</p>
                                                    <p className="text-sm font-bold text-gray-800">₹{route.estimated_cost_inr}</p>
                                                </div>
                                                <div className="flex flex-col items-center p-2 rounded-lg bg-orange-50/50">
                                                    <Clock className="w-4 h-4 text-orange-600 mb-1" />
                                                    <p className="text-[10px] text-gray-500 font-semibold uppercase tracking-wide">Delay</p>
                                                    <p className="text-sm font-bold text-red-600">+{dynamicStats.delay}m</p>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                ))
                            })()}
                        </div>
                    )}

                    {/* Congestion Alert */}
                    {congestionPrediction && activeRoute && (
                        <div className="mt-4 p-3 bg-gray-50 rounded-xl border border-gray-100 flex items-center gap-3">
                            <div className="p-2 bg-yellow-100 text-yellow-600 rounded-lg">
                                <AlertTriangle className="w-5 h-5" />
                            </div>
                            <div>
                                <p className="text-xs font-bold text-gray-500 uppercase">Live Traffic</p>
                                <p className="text-sm font-medium text-gray-800">
                                    {congestionPrediction[0]?.congestion_level || 'Moderate'} Congestion detected ahead.
                                </p>
                            </div>
                        </div>
                    )}


                </div>
            </div>
        </div>
    )
}

export default FullMap
