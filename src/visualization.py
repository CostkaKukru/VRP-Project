import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx

def plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany"):
    """
    Plots routes on a street map using the OSMnx library.
    Every route is drawn in a different color, calculating the shortest path
    between nodes in the graph for each stage of the route.

    Parameters:
    - route_nodes (dict): Dictionary with vehicle routes and coordinates.
    - location (str): Area to download.

    Returns:
    - None
    """
    
    # Get a map for a specific location, road network
    G = ox.graph_from_place(location, network_type="drive")

    # Find the nearest OSM node for the coordinates of each stop
    node_routes = {}
    for vehicle, coordinates in route_nodes.items():
        node_routes[vehicle] = [
            ox.distance.nearest_nodes(G, lon, lat) for lat, lon in coordinates
        ]

    # Prepare the graph with vehicle routes
    fig, ax = ox.plot_graph(G, show=False, close=False) 

    # Define the color map for each vehicle
    colors = plt.cm.tab20.colors  
    node_colors = {}
    for i, (vehicle, node_list) in enumerate(node_routes.items()):
        color = colors[i % len(colors)] 
        for node in node_list:
            node_colors[node] = color

        # Plot the shortest path for each pair of nodes on the route
        for u, v in zip(node_list[:-1], node_list[1:]):
            if nx.has_path(G, u, v):  # check if there is a path between nodes
                path = nx.shortest_path(G, source=u, target=v, weight="length")
                path_edges = list(zip(path[:-1], path[1:]))
                for edge_u, edge_v in path_edges:
                    # check if the edge has a geometry attribute
                    if G.has_edge(edge_u, edge_v):
                        edge_data = G.get_edge_data(edge_u, edge_v)[0]
                        if "geometry" in edge_data:
                            xs, ys = edge_data["geometry"].xy
                            ax.plot(xs, ys, color=color, linewidth=2)
                        else:
                            x = [G.nodes[edge_u]['x'], G.nodes[edge_v]['x']]
                            y = [G.nodes[edge_u]['y'], G.nodes[edge_v]['y']]
                            ax.plot(x, y, color=color, linewidth=2)

    # Plot nodes with assigned colors and sizes
    for node in G.nodes():
        if node in node_colors:
            ax.scatter(G.nodes[node]['x'], G.nodes[node]['y'], color=node_colors[node], s=15, zorder=3)
        else:
            ax.scatter(G.nodes[node]['x'], G.nodes[node]['y'], color='none', s=0, zorder=3)

    ax.legend(loc='upper left', fontsize='small', title="Pojazdy")

    plt.title("Trasy na mapie ulic")
    plt.show()
