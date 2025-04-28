import json
from abc import ABC, abstractmethod
from typing import List, Dict
import pandas as pd
import networkx as nx
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime

# Configuration
CONFIG = {
    "speed_limits": {
        "MG Road": 60,
        "School Zone": 30,
        "Highway": 100,
        "default": 80
    },
    "signal_hysteresis": {
        "green_threshold": 25,
        "red_threshold": 10
    }
}

class TrafficManager(ABC):
    @abstractmethod
    def adjust_signals(self, signals: List[Dict]) -> List[Dict]:
        pass

class RuleBasedTraffic(TrafficManager):
    def adjust_signals(self, signals: List[Dict]) -> List[Dict]:
        for signal in signals:
            current_status = signal['signal_status']
            vehicles = signal['vehicles_waiting']
            
            if current_status == 'red' and vehicles > CONFIG['signal_hysteresis']['green_threshold']:
                signal['signal_status'] = 'green'
            elif current_status == 'green' and vehicles < CONFIG['signal_hysteresis']['red_threshold']:
                signal['signal_status'] = 'red'
        return signals

class MLTraffic(TrafficManager):
    def __init__(self, model_path: str = None):
        self.model = self._load_model(model_path)
        self.features = ['hour', 'vehicles_waiting', 'adjacent_congestion']
        
        if model_path is None:
            self._train_dummy_model()

    def _load_model(self, path: str):
        return RandomForestClassifier() if path is None else pd.read_pickle(path)
    
    def _train_dummy_model(self):
        X_dummy = pd.DataFrame({
            'hour': [8, 8, 18, 18, 12, 12],
            'vehicles_waiting': [30, 5, 35, 8, 25, 15],
            'adjacent_congestion': [0.8, 0.3, 0.9, 0.2, 0.6, 0.4]
        })
        y_dummy = [1, 0, 1, 0, 1, 0]
        self.model.fit(X_dummy, y_dummy)

    def _prepare_features(self, signals: List[Dict]) -> pd.DataFrame:
        return pd.DataFrame([{
            'hour': datetime.now().hour,
            'vehicles_waiting': s['vehicles_waiting'],
            'adjacent_congestion': self._get_adjacent_congestion(s['node_id'])
        } for s in signals])

    def _get_adjacent_congestion(self, node_id: str) -> float:
        # Replace with actual API call to traffic sensors
        return 0.7

    def adjust_signals(self, signals: List[Dict]) -> List[Dict]:
        X = self._prepare_features(signals)
        try:
            predictions = self.model.predict(X)
            for signal, pred in zip(signals, predictions):
                signal['signal_status'] = 'green' if pred == 1 else 'red'
        except Exception as e:
            # Fallback to rule-based if ML fails
            return RuleBasedTraffic().adjust_signals(signals)
        return signals

class EmergencyHandler:
    def __init__(self, city_graph: nx.Graph):
        self.city_graph = city_graph

    def prioritize_emergencies(self, emergencies: List[Dict], signals: List[Dict]) -> List[Dict]:
        # Prioritize by emergency type and proximity
        sorted_emergencies = sorted(emergencies,
            key=lambda x: (x['type'] != 'ambulance', x['distance_to_destination']))
        
        for ev in sorted_emergencies:
            try:
                path = nx.shortest_path(self.city_graph,
                                       ev['current_node'],
                                       ev['destination_node'])
                for s in signals:
                    if s['node_id'] in path and s['signal_status'] != 'green':
                        s['signal_status'] = 'green'
                        break  # Prevent overriding by lower priority emergencies
            except nx.NetworkXNoPath:
                continue
        return signals

class RouteAdvisor:
    def __init__(self, city_graph: nx.Graph):
        self.city_graph = city_graph
        self.congestion = {}

    def update_congestion(self, node_id: str, vehicles: int):
        self.congestion[node_id] = vehicles * 0.8  # Convert to congestion score

    def suggest_route(self, origin: str, destination: str) -> List[str]:
        for u, v, d in self.city_graph.edges(data=True):
            d['weight'] = self.congestion.get(v, 0)
        
        try:
            return nx.shortest_path(self.city_graph, origin, destination, weight='weight')
        except nx.NetworkXNoPath:
            return []

class ITMS:
    def __init__(self, strategy: TrafficManager, city_graph: nx.Graph):
        self.strategy = strategy
        self.city_graph = city_graph
        self.emergency_handler = EmergencyHandler(city_graph)
        self.route_advisor = RouteAdvisor(city_graph)

    def process_data(self, data: Dict) -> Dict:
        # 1. Adjust signals
        data['traffic_signals'] = self.strategy.adjust_signals(data['traffic_signals'])
        
        # 2. Handle emergencies with priority
        data['traffic_signals'] = self.emergency_handler.prioritize_emergencies(
            data['emergency_vehicles'], data['traffic_signals'])
        
        # 3. Detect violations with zone-aware speed limits
        violations = []
        for vm in data['vehicle_movements']:
            speed_limit = CONFIG['speed_limits'].get(vm['zone'], CONFIG['speed_limits']['default'])
            if vm['speed'] > speed_limit:
                violations.append(f"Speed violation ({vm['speed']}km/h in {vm['zone']})")
            if vm['direction'] == 'wrong-way':
                violations.append("Wrong-way driving")
        
        # 4. Update routing and suggest paths
        route_suggestions = {}
        for signal in data['traffic_signals']:
            self.route_advisor.update_congestion(signal['node_id'], signal['vehicles_waiting'])
        
        for vm in data['vehicle_movements']:
            route = self.route_advisor.suggest_route(vm['current_node'], vm['destination_node'])
            route_suggestions[vm['vehicle_id']] = route
        
        return {
            'adjusted_signals': data['traffic_signals'],
            'violations': violations,
            'route_suggestions': route_suggestions,
            'emergency_priorities': [ev['id'] for ev in data['emergency_vehicles']]
        }

# Example Usage
if __name__ == "__main__":
    # Geo-aware city graph
    city_graph = nx.DiGraph()
    city_graph.add_nodes_from([
        ('MG1', {'pos': (12.9716, 77.5946), 'type': 'signal'}),
        ('BR1', {'pos': (12.9754, 77.6058), 'type': 'signal'}),
        ('HOSP', {'pos': (12.9789, 77.6092), 'type': 'landmark'})
    ])
    city_graph.add_edges_from([('MG1', 'BR1'), ('BR1', 'HOSP')])
    
    # Initialize system
    itms = ITMS(MLTraffic(), city_graph)
    
    # Sample input
    input_data = {
        "traffic_signals": [
            {"node_id": "MG1", "vehicles_waiting": 30, "signal_status": "red"},
            {"node_id": "BR1", "vehicles_waiting": 5, "signal_status": "green"}
        ],
        "emergency_vehicles": [
            {"id": "AMB-101", "type": "ambulance", 
             "current_node": "MG1", "destination_node": "HOSP",
             "distance_to_destination": 2.5}
        ],
        "vehicle_movements": [
            {"vehicle_id": "KA01AB1234", "speed": 65, "direction": "correct",
             "current_node": "MG1", "destination_node": "BR1", "zone": "MG Road"},
            {"vehicle_id": "KA02CD5678", "speed": 90, "direction": "wrong-way",
             "current_node": "BR1", "destination_node": "HOSP", "zone": "School Zone"}
        ]
    }
    
    # Process and output
    result = itms.process_data(input_data)
    print(json.dumps(result, indent=2))