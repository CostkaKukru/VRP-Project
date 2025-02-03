
# Vehicle Routing Problem (VRP) Optimization

This project tackles the Vehicle Routing Problem (VRP) with a focus on optimizing public transport accessibility in Berlin, Germany. It leverages a grid-based scoring model and integrates advanced optimization algorithms, including Simulated Annealing (SA), Branch and Bound (BaB), and machine learning-enhanced approaches.

---

## Table of Contents
1. [Project Overview](#project-overview)
2. [Features](#features)
3. [Data Sources](#data-sources)
4. [Implemented Algorithms](#implemented-algorithms)
5. [Installation](#installation)
6. [Usage](#usage)
7. [Visualization](#visualization)
8. [Project Structure](#project-structure)
9. [Results](#results)
10. [Acknowledgments](#acknowledgments)

---

## Project Overview

The VRP project focuses on:
- Optimizing bus routes and schedules to improve public transport accessibility.
- Minimizing travel time, fuel costs, and emissions.
- Incorporating real-time traffic conditions and historical data into optimization.

The analysis is based on Berlin's bus network, considering over 7,600 bus stops and 163 lines. The solution integrates advanced algorithms to improve accessibility for low-scoring grid areas.

---

## Features

- **Simulated Annealing (SA):** Metaheuristic optimization for efficient route planning.
- **Branch and Bound (BaB):** Exact optimization for small datasets.
- **Machine Learning Integration:** Predicting delays based on traffic data.
- **Visualization:** Mapped routes using OSMnx and Matplotlib.

---

## Data Sources

1. **GTFS Data for Berlin:** Public transport schedules and stops.
2. **Synthetic Bus Traffic Data:** Simulated datasets for testing.
3. **Traffic Volume Data (2019):** Historical traffic intensity.
4. **Real-time Traffic Measurements:** Hourly traffic data for Berlin.

---

## Implemented Algorithms

### Simulated Annealing (SA)
- Optimizes travel routes by exploring a wide solution space.
- Integrates traffic delay predictions using machine learning.

### Branch and Bound (BaB)
- Systematic search for optimal solutions for smaller datasets.

### Machine Learning-enhanced SA
- Predicts traffic delays dynamically using a trained model and integrates them into the optimization process.

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repo/vrp-project.git
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Usage

1. Run the `main.py` script:
   ```bash
   python main.py
   ```
2. Follow the prompts to:
   - Select a dataset (synthetic, Berlin test set, or full dataset).
   - Choose an optimization algorithm (SA, BaB, or SA with delay predictions).

### Example Commands:
- Input custom file paths for datasets.
- Visualize routes on a Berlin map after computing solutions.

---

## Visualization

Generated routes are visualized on a Berlin map with:
- Stops and connections displayed for each bus route.
- Color-coded routes for easy differentiation.

---

## Project Structure

- **`data/`**: Stores input datasets for VRP computations.
- **`src/`**: Houses the core Python scripts for solving VRP.
- **`test/`**: Contains test data and validation scripts.
   
- **`README.md`**: Project documentation and usage instructions.
- **`distanceTimeMatrix.py`**: Handles preprocessing of distance/time matrices.
- **`main.py`**: Runs the VRP algorithm with user inputs.
- **`requirements.txt`**: Lists required Python packages.



- `main.py`: Entry point for running the project.
- `data_processing.py`: Data preprocessing and validation utilities.
- `visualization.py`: Mapping and visual representation of routes.
- `sa_solver.py`: Simulated Annealing implementation.
- `bab_solver.py`: Branch and Bound implementation.
- `ml_sa_solver.py`: Machine Learning-enhanced SA solver.
- `solver_utils.py`: Common utilities for solvers.

---

## Results

- **SA Results:**
  - Effective for smaller datasets with dynamic traffic adjustment.
- **BaB Results:**
  - Best for exact optimization with small datasets.
- **Machine Learning Integration:**
  - Successfully predicted delays, improving accessibility scoring.

---

## Acknowledgments

- **GTFS Data:** Berlin public transport.
- **OSMnx:** Mapping and graph analysis.
- **Google OR-Tools:** Optimization framework.
- **Matplotlib:** Visualization of transport routes.
```

