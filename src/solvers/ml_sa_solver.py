import joblib
import numpy as np
import pandas as pd
from ortools.constraint_solver import pywrapcp
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from matplotlib import pyplot as plt
from src.solvers.solver_utils import create_data_model

# Load the trained model
model = joblib.load('traffic_delay_model_linear.pkl')

def predict_delays(trips_df, time_df, traffic_df):
    """
    Predicts delays based on the given data and the trained model.
    Adjusts the travel time matrix dynamically.
    """
    # Prepare the feature DataFrame for prediction
    features = []
    for i, row in trips_df.iterrows():
        for j, col in trips_df.iterrows():
            if i != j:  # Skip diagonal elements
                feature = {
                    'from_x': row['stop_lon'],
                    'from_y': row['stop_lat'],
                    'to_x': col['stop_lon'],
                    'to_y': col['stop_lat'],
                    'timestamp': 'morning',  # Use actual timestamp if available
                    'traffic': traffic_df.loc[i, j] if not traffic_df.empty else 'moderate'  # Example traffic level
                }
                features.append(feature)

    # Convert features to DataFrame
    feature_df = pd.DataFrame(features)

    # Perform one-hot encoding for categorical variables
    feature_df = pd.get_dummies(feature_df, columns=['timestamp', 'traffic'], drop_first=True)

    # Predict delays
    delays = model.predict(feature_df)

    # Update time matrix with predicted delays
    adjusted_time_matrix = time_df.copy()
    index = 0
    for i in range(len(time_df)):
        for j in range(len(time_df)):
            if i != j:
                adjusted_time_matrix[i][j] += delays[index]
                index += 1

    return adjusted_time_matrix

def solve_vrp_with_predictions(time_csv, dist_csv, trips_file, traffic_csv=None):
    """
    Solves the VRP problem, dynamically adjusting travel times using delay predictions.
    """
    # Load data
    time_df = pd.read_csv(time_csv, index_col=0)
    trips_df = pd.read_csv(trips_file)
    traffic_df = pd.read_csv(traffic_csv, index_col=0) if traffic_csv else pd.DataFrame()

    # Predict delays and adjust time matrix
    adjusted_time_matrix = predict_delays(trips_df, time_df, traffic_df)

    # Update the time_matrix in the data model
    data = create_data_model(time_csv, dist_csv, trips_file)
    data['time_matrix'] = adjusted_time_matrix.tolist()

    # Solve VRP using the adjusted time matrix
    solve_vrp_core(data)

def solve_vrp_core(data):
    """
    Core VRP solving logic (uses the adjusted time matrix from `data`).
    """
    trips_df = pd.read_csv(trips_file)
    stop_names = trips_df['stop_name'].tolist()

    manager = pywrapcp.RoutingIndexManager(
        data['num_locations'],
        data['num_vehicles'],
        data['starts'],
        data['ends']
    )

    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        """
        Returns adjusted travel time between two nodes.
        """
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # Add dimensions and constraints as before
    routing.AddDimension(
        transit_callback_index,
        0,               # 0 slack time
        10_000_000,      # large maximum travel time
        True,            # start cumul to zero
        "Time"
    )

    # Solve the problem as before
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        route_nodes = print_solution(data, manager, routing, solution, stop_names)
        plot_routes(route_nodes)
    else:
        print("Nie znaleziono rozwiązania.")
