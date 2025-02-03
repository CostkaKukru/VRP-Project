from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from .solver_utils import create_data_model, print_solution
import pandas as pd

def solve_vrp_bab(time_csv, trips_file):
    """
    Rozwiązuje problem Vehicle Routing Problem z użyciem Google OR-Tools z Branch and Bound.
    Parametry:
    time_csv - plik z czasami tras
    dist_csv - plik z dystansami tras
    trips_file - plik z informacjami o przystankach

    Zwraca:
    route_nodes - lista wierzchołków trasy
    """
    data = create_data_model(time_csv, trips_file)

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
        Zwraca czas podróży między dwoma węzłami.

        Parametry:
        - from_ index, to_index: indeksy wierzchołków

        Zwraca:
        - czas podróży jeśli znaleziono rozwiązanie
        - None w przeciwnym wypadku
        """
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['time_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(time_callback)

    # wymiar czasu
    routing.AddDimension(
        transit_callback_index,
        0,                # No slack
        10_000_000,       # Arbitrarily large upper limit for cumulative time
        True,             # Start cumulative time at zero
        "Time"
    )
    time_dimension = routing.GetDimensionOrDie("Time")

    # maksymalny czas podróży dla trasu
    max_route_length = 10_000_000
    best_solution = None
    best_max_route_length = float("inf")

    # konfiguracja algorytmu
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.local_search_metaheuristic = (
        routing_enums_pb2.LocalSearchMetaheuristic.SIMULATED_ANNEALING
    )
    search_parameters.time_limit.seconds = 150

    while max_route_length > 0:
        # stworzenie zmiennej do przechowywania maksymalnego czasu podrózy
        max_route_var = routing.solver().IntVar(0, max_route_length, "max_route_var")

        # dodanie kryterium ograniczajacego czas podrózy dla każdego pojazdu <= max_route_var
        for vehicle_id in range(data['num_vehicles']):
            end_index = routing.End(vehicle_id)
            routing.solver().Add(time_dimension.CumulVar(end_index) <= max_route_var)

        # dodanie kryterium do minimalizacji maz_route_length
        routing.solver().Minimize(max_route_var, 1)

        # Rozwiązanie problemu
        solution = routing.SolveWithParameters(search_parameters)

        if solution:
            # Ewaluacja
            max_time = max(
                solution.Value(time_dimension.CumulVar(routing.End(vehicle_id)))
                for vehicle_id in range(data['num_vehicles'])
            )

            if max_time < best_max_route_length:
                best_max_route_length = max_time
                best_solution = solution

            max_route_length = max_time - 1
        else:
            break  
    if best_solution:
        route_nodes = print_solution(data, manager, routing, best_solution, stop_names)
        return route_nodes
    else:
        print("Nie znaleziono rozwiązania.")
