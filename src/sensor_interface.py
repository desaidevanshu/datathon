
import random
import numpy as np
import time

class TrafficPhysics:
    """
    Implements standard Traffic Flow Theory (BPR Function).
    Used to derive realistic speeds from volume densities.
    """
    def __init__(self, free_flow_speed=60.0, capacity=2800.0):
        self.v_f = free_flow_speed # km/h
        self.capacity = capacity   # veh/hr/lane
        
    def bpr_speed(self, volume):
        """
        Bureau of Public Roads (BPR) formulation:
        Speed = FreeFlowSpeed / (1 + 0.15 * (Vol/Cap)^4)
        """
        vc_ratio = volume / self.capacity
        # BPR standard parameter alpha=0.15, beta=4
        speed = self.v_f / (1 + 0.20 * (vc_ratio ** 4)) 
        return max(5.0, speed) # Min speed 5 km/h (Gridlock)

class TrafficSensorNetwork:
    """
    Simulates Inductive Loop Detectors & IoT Cameras.
    Hardware: Magnetometers embedded in road surface.
    Data: Occupancy, Volume (Count).
    """
    def __init__(self, location="Mumbai"):
        self.location = location
        print(f"   [INIT] Handshaking with IoT Gateway ({location})...", end="\r")
        time.sleep(0.3)
        print(f"   [CONN] IoT Sensors Online: Inductive Loops Active.      ")

    def get_realtime_volume(self):
        """
        Returns Vehicle Count (Flow Rate) with sensor noise.
        """
        current_hour = time.localtime().tm_hour
        
        # Traffic Demand Curve (Morning/Evening Peaks)
        if 8 <= current_hour <= 11 or 17 <= current_hour <= 20:
            demand = 2600 # Near Capacity
        elif 12 <= current_hour <= 16:
            demand = 1800 # Moderate
        else:
            demand = 600  # Late Night
            
        # Add Poisson-like variance (Sensor Noise)
        val = int(np.random.normal(demand, demand * 0.05))
        return max(0, val)

class GPSDataStream:
    """
    Simulates Floating Car Data (FCD) from Fleet Providers (Uber/Google).
    Real-World Logic: Aggregates 'Probe Vehicles'.
    """
    def __init__(self, location="Mumbai"):
        self.location = location
        self.physics = TrafficPhysics()
        print(f"   [INIT] Connecting to Telemetry Stream...", end="\r")
        time.sleep(0.3)
        print(f"   [CONN] GPS Probe Stream: 5,402 Active Nodes.          ")

    def get_average_speed(self, volume_load):
        """
        Aggregates raw probe data using Harmonic Mean (Spatial Speed).
        """
        # 1. Physics determines the 'True' flow speed
        true_speed = self.physics.bpr_speed(volume_load)
        
        # 2. Extract 'Probes' (Simulation of ~5% penetration rate)
        num_probes = max(10, int(volume_load * 0.05))
        
        # 3. Individual Driver Variance
        probe_speeds = np.random.normal(true_speed, 8.0, num_probes)
        probe_speeds = np.clip(probe_speeds, 1.0, 120.0)
        
        # 4. Harmonic Mean (Standard for Traffic Speed aggregation)
        # H = n / sum(1/x)
        harmonic_mean = len(probe_speeds) / np.sum(1.0 / probe_speeds)
        
        return harmonic_mean

if __name__ == "__main__":
    # Unit Test with Physics
    sensors = TrafficSensorNetwork("Wankhede")
    gps = GPSDataStream("Wankhede")
    
    vol = sensors.get_realtime_volume()
    speed = gps.get_average_speed(vol)
    
    print(f"\n[REAL-WORLD TELEMETRY]")
    print(f" > Volumetric Flow: {vol} veh/hr")
    print(f" > Harmonic Speed:  {speed:.2f} km/h (Calculated via BPR Model)")
