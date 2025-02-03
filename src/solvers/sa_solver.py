from ortools.constraint_solver import pywrapcp, routing_enums_pb2
from .solver_utils import create_data_model, print_solution, predict_delays
import pandas as pd
import numpy as np

def solve_vrp_sa(time_csv, trips_file, traffic_level=None, model=None, encoder=None):
    """
    Rozwiązuje problem Vehicle Routing Problem z użyciem Google OR-Tools z Simulated Annealing.
    Uwzlędnia opóźnienie jeżeli pliki traffic_csv, model i encoder są podane.
    Parametry:
    time_csv - plik z czasami tras
    trips_file - plik z informacjami o przystankach
    traffic_level - poziom matęzienia ruchu ('low', 'moderate', 'heavy')
    model - model predykcji opóźnienia
    encoder - encoder czasu

    Zwraca:
    route_nodes - lista wierzchołków trasy
    """
    trips_df = pd.read_csv(trips_file)
    stop_names = trips_df['stop_name'].tolist()  #

    data = create_data_model(time_csv, trips_file)

    if traffic_level and model and encoder:
        data['time_matrix'] = predict_delays(trips_df, data['time_matrix'], traffic_level, model, encoder)    

    manager = pywrapcp.RoutingIndexManager(
        data['num_locations'],
        data['num_vehicles'],
        data['starts'],
        data['ends']
    )

    routing = pywrapcp.RoutingModel(manager)

    def time_callback(from_index, to_index):
        """
        Zwraca czas podróży między dwoma węzłami.

        Parametry:
        - from_ index, to_index: indeksy wierzchołków

        Zwraca:
        - czas podróży jeśli znaleziono rozwiązanie
        - None w przeciwnym wypadku
        """
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        if from_node < len(data['time_matrix']) and to_node < len(data['time_matrix'][from_node]):
            return data['time_matrix'][from_node][to_node]

        return 10_000_000  
    
    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    data['time_matrix'] = np.where(
        np.array(data['time_matrix']) == 0, 
        10_000_000, 
        np.array(data['time_matrix'])
    ).tolist()

    # wymiar czasu
    routing.AddDimension(
        transit_callback_index,
        0,               # 0 brak czasu oczekiwania pomiędzy węzłami (przystankami)
        10_000_000,      # wysoki limit czasu
        True,            # początkowy czas = 0
        "Time"
    )

    time_dimension = routing.GetDimensionOrDie("Time")
    solver = routing.solver()

    # uniknięcie tras tylko z dwoma przystankami
    for vehicle_id in range(data['num_vehicles']):
        start_index = routing.Start(vehicle_id)
        end_index = routing.End(vehicle_id)
        solver.Add(routing.NextVar(start_index) != end_index)

    # Każdy powtarzający się przystanek musi być obsługiwany przez inny pojazd // jeżeli w pliku występuje zbyt dużo powtarzających się przystanków, to warunek jest zbyt skomplikowany i skrypt nie kończy obliczeń
    # for stop in data['frequent_stops']:
    #     stop_indices = trips_df[trips_df['stop_name'] == stop].index.tolist()
    #     routing_indices = [manager.NodeToIndex(idx) for idx in stop_indices]
    #     solver.Add(solver.AllDifferent([routing.VehicleVar(idx) for idx in routing_indices]))

    # wykluczenie nieprawidłowych par przystanków (pomiędzy start i end z różnych tras)
    exclude_pairs = [
        (start, end)
        for start, assigned_end in zip(data['starts'], data['ends'])  
        for end in data['ends']  
        if end != assigned_end 
    ] + [
        (start1, start2)
        for i, start1 in enumerate(data['starts'])
        for start2 in data['starts'][i+1:] 
    ]

    # Obliczanie maksymalnego czasu trasy
    longest_travel_time = sum(
        data['time_matrix'][0][j]
        for j in range(len(data['time_matrix'][0]))
        if (0, j) not in exclude_pairs
    )

    # maksymalny średni czas pojedyńczej trasy
    singular_route_time = longest_travel_time // data['num_vehicles']

    # Czas przejazdu między przystankami dla każdego pojazdu musi być mniejszy niż max_route_time
    max_route_time = solver.IntVar(0, int(singular_route_time), "max_route_time")

    for vehicle_id in range(data['num_vehicles']):
        end_index = routing.End(vehicle_id)
        solver.Add(time_dimension.CumulVar(end_index) <= max_route_time)

    solver.Minimize(max_route_time, 1)
    # Parametry wyszukiwania -> Simulated Annealing
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING
    )
    search_parameters.time_limit.seconds = 60
    search_parameters.log_search = True

    # Rozwiązanie problemu
    solution = routing.SolveWithParameters(search_parameters)
    if solution:
        route_nodes = print_solution(data, manager, routing, solution, stop_names)
        return route_nodes
    else:
        print("Nie znaleziono rozwiązania.")
        return None
