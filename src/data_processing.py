
import pandas as pd

def create_data_model(time_csv, dist_csv, trips_file):
    """
    Create a data model for VRP solvers.

    Parameters
    ----------
    time_csv : str
        Path to the CSV file containing the time matrix.
    dist_csv : str
        Path to the CSV file containing the distance matrix.
    trips_file : str
        Path to the CSV file containing the trip data.

    Returns
    -------
    dict
        A data model for the VRP solvers, containing the time matrix, distance matrix, number of vehicles, number of locations, start and end nodes for each route, and the coordinates of each stop.

    """
    time_df = pd.read_csv(time_csv, index_col=0)
    dist_df = pd.read_csv(dist_csv, index_col=0)
    trips_df = pd.read_csv(trips_file)

    data = {
        # Time matrix
        'time_matrix': time_df.values.tolist(),
        # Distance matrix
        'distance_matrix': dist_df.values.tolist(),
        # Number of vehicles
        'num_vehicles': trips_df['trip_id'].nunique(),
        # Number of locations
        'num_locations': len(trips_df.index),
        # Start and end nodes for each route
        'starts': [
            trips_df.index.get_loc(group[group['stop_sequence'] == group['stop_sequence'].min()].index[0])
            for _, group in trips_df.groupby('trip_id')
        ],
        'ends': [
            trips_df.index.get_loc(group[group['stop_sequence'] == group['stop_sequence'].max()].index[0])
            for _, group in trips_df.groupby('trip_id')
        ],
        # Coordinates of each stop
        'stop_coordinates': trips_df[['stop_lat', 'stop_lon']].values.tolist()
    }
    return data


    