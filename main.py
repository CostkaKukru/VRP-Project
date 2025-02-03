from src.solvers.sa_solver import solve_vrp_sa
from src.solvers.bab_solver import solve_vrp_bab
from src.visualization import plot_routes
import joblib
import pandas as pd
import re

def main():
    route_nodes = None
    print("Wybierz plik z danymi:")
    print("1. Short test 1 - dane syntetyczne")
    print("2. Short test 2 - Berlin (3 trasy, 26 przystanków)")
    print("3. Berlin, pełen dataset")
    print("4. Własny plik")
    print("0. Wyjście")
    
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
    choice_file = input("Wybierz opcję: ").strip()
    if choice_file == "0":
        exit()
    elif choice_file not in choice_file_map:
        print("Nieprawidłowy wybór!")
        return
    elif choice_file == "4":
        trips_file = input("Podaj ścieżkę do pliku z danymi: ")
        time_csv = input("Podaj ścieżkę do pliku z macierzą czasu: ")
    else:
        trips_file, time_csv = choice_file_map[choice_file]

    # Ładowanie i kontrola plików
    time_matrix = pd.read_csv(time_csv, index_col=0)
    trips_df = pd.read_csv(trips_file)
    
    # Kontrola macierzy czasu
    assert time_matrix.shape[0] == time_matrix.shape[1], "Macierz czasu musi być kwadratowa!"
    assert (time_matrix >= 0).all().all(), "Macierz czasu nie może zawierać liczb ujemnych!"
    assert (time_matrix.values.diagonal() == 0).all(), "Wartości po przekątnych muszą równać się 0!"
    print("Macierz czasu prawidłowa.")
    
    # Kontrola wymaganych kolumn
    required_columns = ["trip_id", "route_id", "stop_sequence", "stop_name"]
    assert all(col in trips_df.columns for col in required_columns), f"Brakujące kolumny: {set(required_columns) - set(trips_df.columns)}"

    # Kontrola sekwencji przystanków
    for trip_id, group in trips_df.groupby("trip_id"):
        assert (group["stop_sequence"].sort_values().values == range(len(group))).all(), f"Nieprawidłowa sekwencja: stop_sequence w kolumnie: trip_id: {trip_id}"

    # Kontrola wartości geograficznych
    if choice_file != "1":
        assert trips_df["stop_lat"].between(-90, 90).all(), "Plik zawiera nieprawidłowe szerokości geograficzne!"
        assert trips_df["stop_lon"].between(-180, 180).all(), "Plik zawiera nieprawidłowe długości geograficzne!"

    print("Plik z trasami prawidłowy.")
    
    print("Wybierz algorytm:")
    print("1. Simulated Annealing")
    print("2. Branch and Bound")
    print("3. Simulated Annealing z przewidywaniem opóźnienia")
    print("0. Wyjście")

    choice_alg = input("Wybierz opcję: ")
    if choice_alg == "0":
        exit()
    elif choice_alg not in ["1", "2", "3"]:
        print("Nieprawidłowy wybór!")
        return
    
    encoder, model = None, None

    if choice_alg in ["1"]:
        print("\nRozwiązywanie z Simulated Annealing...")
        route_nodes = solve_vrp_sa(time_csv, trips_file)
    if choice_file != "1" and route_nodes is not None:
        print("\nWizualizacja tras...")
        plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany")

    if choice_alg in ["2"]:
        print("\nRozwiązywanie z Branch and Bound...")
        route_nodes = solve_vrp_bab(time_csv, trips_file)
        if choice_file != "1" and route_nodes is not None:
            print("\nWizualizacja tras...")
            plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany")
    
    if choice_alg in ["3"]:
        print("\nRozwiązywanie z SA i przewidywaniem opóźnienia...")
        print("Ładowanie modelu i kodera dla 'Time of Day'...")
        model = joblib.load("src/RFR model/delay_prediction_model.pkl")
        encoder = joblib.load("src/RFR model/time_of_day_encoder.pkl")
        traffic_map = {'1': 'low', '2': 'moderate', '3': 'heavy'}
        traffic_input = input("Podaj poziom natężenia ruchu: mały: 1, umiarkowany: 2, duży: 3: ").strip()
        traffic_level = traffic_map[traffic_input]

        route_nodes = solve_vrp_sa(time_csv, trips_file, traffic_level, model, encoder)
        if choice_file != "1" and route_nodes is not None:
            print("\nWizualizacja tras...")
            plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany")

if __name__ == "__main__":
    main()
