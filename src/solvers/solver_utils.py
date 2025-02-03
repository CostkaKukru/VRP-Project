import joblib
import pandas as pd
import numpy as np

def create_data_model(time_csv, trips_file):
    """
    Wczytuje travel_time_matrix z plików CSV, a następnie tworzy dict.
    Generuje dynamiczne dane dla liczby pojazdów, startu, końca na podstawie trips_file.
    Parametry:
    - time_csv: ścieżka do pliku CSV z czasami podróży
    - trips_file: ścieżka do pliku CSV z informacjami o przystankach

    Zwraca:
    - data: dict zawierajacy dynamiczne dane
    """
    time_df = pd.read_csv(time_csv, index_col=0)
    trips_df = pd.read_csv(trips_file)

    data = {}
    data['time_matrix'] = time_df.values.tolist()
    data['num_vehicles'] = trips_df['trip_id'].nunique()
    data['num_locations'] = len(trips_df.index)

    # Mapowanie węzłów startowych i końcowych dla każdego pojazdu
    starts = [
        trips_df.index.get_loc(group[group['stop_sequence'] == group['stop_sequence'].min()].index[0])
        for trip_id, group in trips_df.groupby('trip_id')
    ]
    ends = [
        trips_df.index.get_loc(group[group['stop_sequence'] == group['stop_sequence'].max()].index[0])
        for trip_id, group in trips_df.groupby('trip_id')
    ]
    data['starts'] = starts
    data['ends'] = ends

    # Count frequent stops
    data['frequent_stops'] = trips_df['stop_name'].value_counts()[lambda x: x > 1].index.tolist()

    # Stop coordinates (replace NaN with 0)
    data['stop_coordinates'] = trips_df[['stop_lat', 'stop_lon']].fillna(0).values.tolist()    
    return data

def print_solution(data, manager, routing, solution, stop_names):
    """
    Publikuje rozwiązanie w konsoli, pokazując trasę dla każdego pojazdu według nazwy przystanku
    i całkowity czas podróży. Konstruuje słownik route_nodes z koordynatami.
    Parametry:
    - data: dict z danymi problemu
    - manager: objekt RoutingIndexManager
    - routing: objekt RoutingModel
    - solution: objekt RoutingSolution
    - stop_names: lista z nazwami przystanków

    Zwraca:
    - route_nodes: dict z koordynatami przystanków dla każdej trasy
    """
    if solution is None:
        print("Nie znaleziono rozwiązania.")
        return

    total_time = 0
    route_nodes = {}

    for vehicle_id in range(data['num_vehicles']):
        vehicle_number = vehicle_id + 1
        index = routing.Start(vehicle_id)
        print(f"\nTrasa {vehicle_number}:")        

        route_list = []
        route_coords = []
        route_time = 0

        while not routing.IsEnd(index):
            # mapowanie indeksu na węzeł i dodanie nazwy przystanku
            from_node = manager.IndexToNode(index)
            route_list.append(stop_names[from_node])  

            # dodaje koordynaty przystanku do listy
            route_coords.append(data['stop_coordinates'][from_node])

            next_index = solution.Value(routing.NextVar(index))
            to_node = manager.IndexToNode(next_index)

            # kalkuluje czas podróży między przystankami bazując na macierzy czasu
            if from_node < len(data['time_matrix']) and to_node < len(data['time_matrix'][from_node]):
                route_time += data['time_matrix'][from_node][to_node]

            index = next_index

        # dodaje ostatni przystanek do trasy
        end_node = manager.IndexToNode(index)
        route_list.append(stop_names[end_node])
        route_coords.append(data['stop_coordinates'][end_node])

        route_nodes[f"Pojazd {vehicle_number}"] = route_coords

        print(f"Trasa dla pojazdu {vehicle_number}: {' -> '.join(route_list)}")
        print(f"Czas podróży dla pojazdu {vehicle_number}: {route_time} min.")
        total_time += route_time

    print(f"\nSumaryczny czas podróży: {total_time} min.")
    return route_nodes

# ładuje model i encoder
model = joblib.load('src/RFR model/delay_prediction_model.pkl')
encoder = joblib.load('src/RFR model/time_of_day_encoder.pkl')

# mapowanie natężenia ruchu z uczenia
traffic_mapping = {'low': 1, 'moderate': 2, 'heavy': 3}

def predict_delays(trips_df, time_matrix, traffic_level, model, encoder):
    """
    Przewiduje opóźnienie na podstawie danych i ruchu.
    Dynamicznie dopasowuje macierz czasu.
    
    Parametry:
    - trips_df: DataFrame zawierający informacje o trasach.
    - time_matrix: Macierz czasu.
    - traffic_level: Poziom matężenia ruchu ('low', 'moderate', 'heavy').
    - model: Model predykcji opóźnienia.
    - encoder: Encoder czasu.

    Zwraca:
    - Nowa macierz czasu z opóźnieniami w zależności od natężenia ruchu.
    """

    # mapowanie ruchu
    traffic_mapping = {'low': 1, 'moderate': 2, 'heavy': 3}
    
    features = []
    for i, row in trips_df.iterrows():
        for j, col in trips_df.iterrows():
            if i != j:  
                feature = {
                    'from_x': row['stop_lon'],
                    'from_y': row['stop_lat'],
                    'to_x': col['stop_lon'],
                    'to_y': col['stop_lat'],
                    'timestamp': 'morning',  
                    'traffic': traffic_mapping[traffic_level]  
                }
                features.append(feature)

    feature_df = pd.DataFrame(features)
    feature_df['Traffic Level (Numerical)'] = feature_df['traffic']
    time_of_day_encoded = encoder.transform(feature_df[['timestamp']])
    X = np.hstack([time_of_day_encoded, feature_df[['Traffic Level (Numerical)']].values])
    delays = model.predict(X)

    # obliczenie nowej macierzy czasu
    adjusted_time_matrix = time_matrix.copy()
    index = 0
    for i in range(len(time_matrix)):
        for j in range(len(time_matrix)):
            if i != j:
                adjusted_time_matrix[i][j] += int(round(delays[index]))
                index += 1

    return adjusted_time_matrix
