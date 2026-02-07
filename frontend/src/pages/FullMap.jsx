import { useState, useEffect, useRef } from 'react'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'
import axios from 'axios'
import { MapPin, Navigation, AlertTriangle, Search, ChevronLeft } from 'lucide-react'
import clsx from 'clsx'
import { Link } from 'react-router-dom'

// Mock Geocoding for demo
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
    'default_start': { lat: 19.0596, lon: 72.8295 }, // Bandra
    'default_end': { lat: 19.1136, lon: 72.8697 }   // Andheri
};

function FullMap() {
    const mapContainer = useRef(null)
    const map = useRef(null)
    const [startLoc, setStartLoc] = useState('')
    const [destLoc, setDestLoc] = useState('')
    const [routeData, setRouteData] = useState(null)
    const [congestionLevel, setCongestionLevel] = useState(null)
    const [isNavigating, setIsNavigating] = useState(false)
    const [loading, setLoading] = useState(false)

    useEffect(() => {
        if (map.current) return;

        map.current = new maplibregl.Map({
            container: mapContainer.current,
            // Use Raster OSM tiles + CSS filter for reliability and look
            style: {
                version: 8,
                sources: {
                    'osm': {
                        type: 'raster',
                        tiles: ['https://a.tile.openstreetmap.org/{z}/{x}/{y}.png'],
                        tileSize: 256,
                        attribution: '&copy; OpenStreetMap Contributors',
                    }
                },
                layers: [{
                    id: 'osm',
                    type: 'raster',
                    source: 'osm',
                    paint: {
                        'raster-fade-duration': 0
                    }
                }]
            },
            center: [72.8777, 19.0760], // Mumbai
            zoom: 11
        });

        // Add controls to verify map instance is running
        map.current.addControl(new maplibregl.NavigationControl(), 'top-right');
        map.current.addControl(new maplibregl.GeolocateControl({
            positionOptions: { enableHighAccuracy: true },
            trackUserLocation: true
        }), 'top-right');

        // Force resize after mount to handle layout flow
        const resizeMap = () => {
            if (map.current) map.current.resize();
        };

        const timeoutId = setTimeout(resizeMap, 200);
        window.addEventListener('resize', resizeMap);

        // Also use ResizeObserver for container size changes
        const resizeObserver = new ResizeObserver(() => {
            resizeMap();
        });
        if (mapContainer.current) {
            resizeObserver.observe(mapContainer.current);
        }

        return () => {
            clearTimeout(timeoutId);
            window.removeEventListener('resize', resizeMap);
            resizeObserver.disconnect();
        };

        map.current.on('error', (e) => {
            console.error("Map error:", e);
            alert("Map Rendering Error: " + (e.error?.message || e.message || "Check console"));
        });

        // Ensure load event handler is attached
        map.current.on('load', () => {
            // Add source for route
            if (!map.current.getSource('route')) {
                map.current.addSource('route', {
                    'type': 'geojson',
                    'data': {
                        'type': 'Feature',
                        'properties': {},
                        'geometry': {
                            'type': 'LineString',
                            'coordinates': []
                        }
                    }
                });
            }

            // Outer Glow
            if (!map.current.getLayer('route-glow')) {
                map.current.addLayer({
                    'id': 'route-glow',
                    'type': 'line',
                    'source': 'route',
                    'layout': { 'line-join': 'round', 'line-cap': 'round' },
                    'paint': {
                        'line-color': '#22c55e',
                        'line-width': 12,
                        'line-opacity': 0.4,
                        'line-blur': 12
                    }
                });
            }

            // Core Line
            if (!map.current.getLayer('route')) {
                map.current.addLayer({
                    'id': 'route',
                    'type': 'line',
                    'source': 'route',
                    'layout': { 'line-join': 'round', 'line-cap': 'round' },
                    'paint': {
                        'line-color': '#22c55e',
                        'line-width': 4,
                        'line-opacity': 1
                    }
                });
            }

            // Heatmap Source & Layer
            if (!map.current.getSource('traffic')) {
                map.current.addSource('traffic', {
                    'type': 'geojson',
                    'data': {
                        'type': 'FeatureCollection',
                        'features': [] // Populated dynamically
                    }
                });

                map.current.addLayer({
                    id: 'traffic-heat',
                    type: 'heatmap',
                    source: 'traffic',
                    paint: {
                        'heatmap-radius': 25,
                        'heatmap-intensity': 1.2,
                        'heatmap-color': [
                            'interpolate',
                            ['linear'],
                            ['heatmap-density'],
                            0, 'rgba(0,0,0,0)',
                            0.3, 'rgba(250, 255, 0, 0.5)', // Yellow
                            0.6, 'rgba(255, 140, 0, 0.6)', // Orange
                            1, 'rgba(255, 20, 20, 0.8)'    // Red
                        ]
                    }
                });
            }
        });
    }, []);

    const getCoords = async (query) => {
        const key = query.toLowerCase().trim();
        // Try mock first for instant demo feel
        if (MOCK_LOCATIONS[key]) return MOCK_LOCATIONS[key];

        // If not in mock, use Nominatim (Free OSM Geocoder)
        try {
            // Bias search towards India/Mumbai by appending context if needed, or rely on viewport.
            // Adding '&countrycodes=in' restricts to India.
            const response = await axios.get(`https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&countrycodes=in&limit=1`);
            if (response.data && response.data.length > 0) {
                return {
                    lat: parseFloat(response.data[0].lat),
                    lon: parseFloat(response.data[0].lon)
                };
            }
        } catch (e) {
            console.error("Geocoding failed", e);
        }
        return null;
    }

    const handleRoute = async () => {
        setLoading(true);
        setRouteData(null); // Reset previous route
        setCongestionLevel(null);

        let startCoords = await getCoords(startLoc || 'bandra');
        let destCoords = await getCoords(destLoc || 'andheri');

        if (!startCoords || !destCoords) {
            alert("Could not find one of the locations. Please try a more specific name (e.g. 'Powai Mumbai').");
            setLoading(false);
            return;
        }

        try {
            const response = await axios.post('http://localhost:8000/api/route', {
                start: startCoords,
                destination: destCoords
            });

            const data = response.data;
            setRouteData(data);
            setIsNavigating(true);

            if (map.current) {
                // Clear existing markers
                const oldMarkers = document.getElementsByClassName('maplibregl-marker');
                while (oldMarkers[0]) {
                    oldMarkers[0].parentNode.removeChild(oldMarkers[0]);
                }

                // Add Start Marker (Green)
                new maplibregl.Marker({ color: '#22c55e' })
                    .setLngLat([startCoords.lon, startCoords.lat])
                    .setPopup(new maplibregl.Popup().setText('Start: ' + (startLoc || 'Start')))
                    .addTo(map.current);

                // Add Destination Marker (Red)
                new maplibregl.Marker({ color: '#ef4444' })
                    .setLngLat([destCoords.lon, destCoords.lat])
                    .setPopup(new maplibregl.Popup().setText('Destination: ' + (destLoc || 'Destination')))
                    .addTo(map.current);

                const geojson = {
                    'type': 'Feature',
                    'properties': {},
                    'geometry': {
                        'type': 'LineString',
                        'coordinates': data.route
                    }
                };

                // SAFETY CHECK: Ensure source exists
                if (!map.current.getSource('route')) {
                    map.current.addSource('route', {
                        'type': 'geojson',
                        'data': geojson
                    });
                } else {
                    map.current.getSource('route').setData(geojson);
                }

                // SAFETY CHECK: Ensure Layers exist
                // Outer Glow
                if (!map.current.getLayer('route-glow')) {
                    map.current.addLayer({
                        'id': 'route-glow',
                        'type': 'line',
                        'source': 'route',
                        'layout': { 'line-join': 'round', 'line-cap': 'round' },
                        'paint': {
                            'line-color': '#22c55e',
                            'line-width': 12,
                            'line-opacity': 0.4,
                            'line-blur': 12
                        }
                    });
                }
                // Core Line
                if (!map.current.getLayer('route')) {
                    map.current.addLayer({
                        'id': 'route',
                        'type': 'line',
                        'source': 'route',
                        'layout': { 'line-join': 'round', 'line-cap': 'round' },
                        'paint': {
                            'line-color': '#22c55e',
                            'line-width': 4,
                            'line-opacity': 1
                        }
                    });
                }

                // Adjust camera
                const bounds = new maplibregl.LngLatBounds();
                data.route.forEach(coord => bounds.extend(coord));
                map.current.fitBounds(bounds, { padding: 100 });

                // Update Color
                const prediction = data.congestion[0]?.congestion_level || 'low';
                let color = '#22c55e'; // low
                if (prediction === 'medium') color = '#eab308';
                if (prediction === 'high') color = '#ef4444';
                if (prediction === 'critical') color = '#7f1d1d';

                // Safety check for paint properties
                if (map.current.getLayer('route')) map.current.setPaintProperty('route', 'line-color', color);
                if (map.current.getLayer('route-glow')) map.current.setPaintProperty('route-glow', 'line-color', color);

                setCongestionLevel(prediction);
            }

        } catch (error) {
            console.error("Routing failed:", error);
            alert(`Routing failed: ${error.message || "Unknown error"}. Check console for details.`);
        } finally {
            setLoading(false);
        }
    };

    // Debugging: Log when coordinates are found
    useEffect(() => {
        if (routeData) console.log("Route Data Updated:", routeData);
    }, [routeData]);

    return (
        <div className="relative w-full flex-1 bg-gray-100 overflow-hidden">
            {/* Map Container */}
            <div ref={mapContainer} className="absolute inset-0 z-0 h-full w-full" />

            {/* Top Control Bar */}
            <div className="absolute top-4 left-4 z-10 flex flex-col gap-4 w-96 pointer-events-none">
                <div className="pointer-events-auto">
                    <Link to="/" className="flex items-center gap-2 text-gray-700 hover:text-black bg-white/90 backdrop-blur px-4 py-2 rounded-lg w-fit border border-gray-200 transition-all shadow-md">
                        <ChevronLeft className="w-4 h-4" /> Back to Dashboard
                    </Link>

                    <div className="bg-white/90 backdrop-blur-md border border-gray-200 rounded-xl p-4 shadow-2xl">
                        <div className="space-y-3">
                            <div className="relative">
                                <MapPin className="absolute left-3 top-3 w-5 h-5 text-gray-500" />
                                <input
                                    type="text"
                                    placeholder="Start (e.g. Bandra)"
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 pl-10 pr-4 focus:ring-2 focus:ring-blue-500 outline-none text-gray-800 placeholder-gray-400"
                                    value={startLoc}
                                    onChange={(e) => setStartLoc(e.target.value)}
                                />
                            </div>

                            <div className="relative">
                                <Search className="absolute left-3 top-3 w-5 h-5 text-gray-500" />
                                <input
                                    type="text"
                                    placeholder="Destination (e.g. Andheri)"
                                    className="w-full bg-gray-50 border border-gray-200 rounded-lg py-2 pl-10 pr-4 focus:ring-2 focus:ring-blue-500 outline-none text-gray-800 placeholder-gray-400"
                                    value={destLoc}
                                    onChange={(e) => setDestLoc(e.target.value)}
                                />
                            </div>

                            <button
                                onClick={handleRoute}
                                disabled={loading}
                                className={clsx(
                                    "w-full font-bold py-2 rounded-lg shadow-lg transition-all flex justify-center items-center gap-2",
                                    loading ? "bg-gray-200 cursor-wait text-gray-500" : "bg-blue-600 hover:bg-blue-700 text-white hover:scale-[1.02]"
                                )}
                            >
                                {loading ? <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" /> : null}
                                {isNavigating ? 'Recalculate Route' : 'Find Best Route'}
                            </button>
                        </div>

                        {/* Status Panel - Only show if route data exists */}
                        {routeData && (
                            <div className="mt-4 border-t border-gray-200 pt-4 animate-in fade-in">
                                <div className="grid grid-cols-2 gap-4 mb-4">
                                    <div className="bg-gray-100 p-2 rounded-lg text-center">
                                        <p className="text-gray-500 text-xs uppercase">Est. Time</p>
                                        <p className="text-xl font-mono text-blue-600 font-bold">{(routeData.duration / 60).toFixed(0)} <span className="text-sm text-gray-500">min</span></p>
                                    </div>
                                    <div className="bg-gray-100 p-2 rounded-lg text-center">
                                        <p className="text-gray-500 text-xs uppercase">Distance</p>
                                        <p className="text-xl font-mono text-gray-800 font-bold">{routeData.distance} <span className="text-sm text-gray-500">km</span></p>
                                    </div>
                                </div>

                                <div className={clsx(
                                    "p-3 rounded-lg flex items-center gap-3 border",
                                    congestionLevel === 'low' && "bg-green-100 border-green-300 text-green-700",
                                    congestionLevel === 'medium' && "bg-yellow-100 border-yellow-300 text-yellow-700",
                                    congestionLevel === 'high' && "bg-red-100 border-red-300 text-red-700",
                                    (!congestionLevel || congestionLevel === 'critical') && "bg-red-200 border-red-400 text-red-900"
                                )}>
                                    <AlertTriangle className="w-5 h-5 flex-shrink-0" />
                                    <div>
                                        <p className="font-bold text-sm uppercase">{congestionLevel} Congestion</p>
                                        <p className="text-xs opacity-80">
                                            {congestionLevel === 'low' ? 'Smooth traffic flow.' :
                                                congestionLevel === 'medium' ? 'Expect minor delays.' :
                                                    'Significant delays. Rerouting active.'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    )
}

export default FullMap
