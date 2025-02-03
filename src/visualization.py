import osmnx as ox
import matplotlib.pyplot as plt
import networkx as nx

def plot_routes(route_nodes, location="Marzahn-Hellersdorf, Berlin, Germany"):
    """
    Wizualizuje trasy na mapie ulic za pomocą biblioteki OSMnx.
    Każda trasa jest rysowana w innym kolorze, obliczając najkrótszą ścieżkę
    między węzłami w grafie dla kolejnych etapów trasy.
    
    Parametry:
    - route_nodes (dict): Słownik z trasami pojazdów i koordynatami.
    - location (str): Obszar do pobrania.
    """
    
    # mapa dla określonej lokalizacji, sieć drogowa
    G = ox.graph_from_place(location, network_type="drive")

    # znajdź najbliższy węzeł OSM dla koordynatów każdego przystanku
    node_routes = {}
    for vehicle, coordinates in route_nodes.items():
        node_routes[vehicle] = [
        ox.distance.nearest_nodes(G, lon, lat) for lat, lon in coordinates
    ]

    # przygotowanie grafu z trasami pojazdów
    fig, ax = ox.plot_graph(G, show=False, close=False) 

    # określenie mapy kolorów dla każdego pojazdu
    colors = plt.cm.tab20.colors  
    for i, (vehicle, node_list) in enumerate(node_routes.items()):
        color = colors[i % len(colors)] 

        # Wizualizacja najkrótszej trasy dla kolejnych wężłów na trasie
        for u, v in zip(node_list[:-1], node_list[1:]):
            if nx.has_path(G, u, v):  # sprawdzenie czy istnieje połączenie
                path = nx.shortest_path(G, source=u, target=v, weight="length")
                path_edges = list(zip(path[:-1], path[1:]))
                for edge_u, edge_v in path_edges:
                    # sprawdzenie czy istnieje krawędź
                    if G.has_edge(edge_u, edge_v):
                        edge_data = G.get_edge_data(edge_u, edge_v)[0]
                        if "geometry" in edge_data:
                            xs, ys = edge_data["geometry"].xy
                            ax.plot(xs, ys, color=color, linewidth=2)
                        else:
                            x = [G.nodes[edge_u]['x'], G.nodes[edge_v]['x']]
                            y = [G.nodes[edge_u]['y'], G.nodes[edge_v]['y']]
                            ax.plot(x, y, color=color, linewidth=2)

        lats, lons = zip(*[(G.nodes[node]['y'], G.nodes[node]['x']) for node in node_list])
        ax.scatter(lons, lats, color=[color], marker='o', label=f"{vehicle} Stops", zorder=3)

    ax.legend(loc='upper left', fontsize='small', title="Pojazdy")

    plt.title("Trasy na mapie ulic")
    plt.show()
