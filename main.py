from src.solvers.sa_solver import solve_vrp_sa
from src.solvers.bab_solver import solve_vrp_bab
from src.visualization import plot_routes
import joblib
import pandas as pd

def main():
    route_nodes = None
    print("Choose file:")
    print("1. Short test 1 - synthetic data")
    print("2. Short test 2 - Berlin (3 routes, 26 stops)")
    print("3. Berlin, full dataset")
    print("4. Your own file")
    print("0. Exit")
    
    choice_file_map = {
        "1": ("test/synthetic data/test_Trips_with_Stops_and_Departures.csv",
              "test/synthetic data/test_time_matrix.csv"
              ),
        "2": ("test/test_berlin/short_test2_Trips_with_Stops_and_Departures.csv",
              "test/test_berlin/short_test2_travel_time_matrix.csv"
              ),
        "3": ("data/Trips_with_Stops_and_Departures.csv",
              "data/travel_time_matrix.csv"),
        "4": (None, None, None)
    }
    choice_file = input("Choose option: ").strip()
    if choice_file == "0":
        exit()
    elif choice_file not in choice_file_map:
        print("Wrong choice!")
        return
    elif choice_file == "4":
        trips_file = input("Introduce the path for the file: ")
        time_csv = input("Introduce the path for the time matrix: ")
    else:
        trips_file, time_csv = choice_file_map[choice_file]

    # Loading data
    time_matrix = pd.read_csv(time_csv, index_col=0)
    trips_df = pd.read_csv(trips_file)
    
    # Time matrix control
    assert time_matrix.shape[0] == time_matrix.shape[1], "Time matrix must be square!"
    assert (time_matrix >= 0).all().all(), "Time matrix must be non-negative!"
    assert (time_matrix.values.diagonal() == 0).all(), "Values on the diagonal must be 0!"
    print("Time matrix is correct.")
    
    # Columns control in the trip file
    required_columns = ["trip_id", "route_id", "stop_sequence", "stop_name"]
    assert all(col in trips_df.columns for col in required_columns), f"Missing columns: {set(required_columns) - set(trips_df.columns)}"

    # Stop sequence control
    for trip_id, group in trips_df.groupby("trip_id"):
        assert (group["stop_sequence"].sort_values().values == range(len(group))).all(), f"Incorrect sequence: stop_sequence in column: trip_id: {trip_id}"

    # Latitudes and longitudes control
    if choice_file != "1":
        assert trips_df["stop_lat"].between(-90, 90).all(), "File contains incorrect latitudes!"
        assert trips_df["stop_lon"].between(-180, 180).all(), "File contains incorrect longitudes!"

    print("File with routes correct.")
    
    print("Choose the algorithm:")
    print("1. Simulated Annealing")
    print("2. Branch and Bound")
    print("3. Simulated Annealing with delay prediction")
    print("0. Exit")

    choice_alg = input("Choose option: ")
    if choice_alg == "0":
        exit()
    elif choice_alg not in ["1", "2", "3"]:
        print("Incorrect choice!")
        return
    
    encoder, model = None, None

    if choice_alg in ["1"]:
        print("\nSolving with Simulated Annealing...")
        route_nodes = solve_vrp_sa(time_csv, trips_file)
    if choice_file != "1" and route_nodes is not None:
        print("\nPlotting routes...")
        plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany")

    if choice_alg in ["2"]:
        print("\nSolving with Branch and Bound...")
        route_nodes = solve_vrp_bab(time_csv, trips_file)
        if choice_file != "1" and route_nodes is not None:
            print("\nPlotting routes...")
            plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany")
    
    if choice_alg in ["3"]:
        print("\nSolving with SA and delay prediction...")
        print("Loading model and encoder for 'Time of Day'...")
        model = joblib.load("src/RFR model/delay_prediction_model.pkl")
        encoder = joblib.load("src/RFR model/time_of_day_encoder.pkl")
        traffic_map = {'1': 'low', '2': 'moderate', '3': 'heavy'}
        traffic_input = input("Introduce the traffic level: 1 - low, 2 - moderate, 3 - heavy: ").strip()
        traffic_level = traffic_map[traffic_input]

        route_nodes = solve_vrp_sa(time_csv, trips_file, traffic_level, model, encoder)
        if choice_file != "1" and route_nodes is not None:
            print("\nPlotting routes...")
            plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany")

if __name__ == "__main__":
    main()

