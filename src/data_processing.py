
import pandas as pd

def create_data_model(time_csv, dist_csv, trips_file):
    """
    Create a data model for VRP solvers.
    """
    time_df = pd.read_csv(time_csv, index_col=0)
    dist_df = pd.read_csv(dist_csv, index_col=0)
    trips_df = pd.read_csv(trips_file)

    data = {
        'time_matrix': time_df.values.tolist(),
        'distance_matrix': dist_df.values.tolist(),
        'num_vehicles': trips_df['trip_id'].nunique(),
        'num_locations': len(trips_df.index),
        'starts': [
            trips_df.index.get_loc(group[group['stop_sequence'] == group['stop_sequence'].min()].index[0])
            for _, group in trips_df.groupby('trip_id')
        ],
        'ends': [
            trips_df.index.get_loc(group[group['stop_sequence'] == group['stop_sequence'].max()].index[0])
            for _, group in trips_df.groupby('trip_id')
        ],
        'stop_coordinates': trips_df[['stop_lat', 'stop_lon']].values.tolist()
    }
    return data


    