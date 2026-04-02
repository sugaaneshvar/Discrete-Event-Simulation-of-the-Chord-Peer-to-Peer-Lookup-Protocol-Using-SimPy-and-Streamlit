# Chord Peer-to-Peer Lookup Protocol Simulator

This project builds a discrete-event simulation of the Chord Distributed Hash Table protocol using `SimPy` and visualizes it with `Streamlit`.

## Features

- Models an `N`-node Chord ring in an `m`-bit identifier space
- Builds and displays each node's finger table
- Simulates key lookups hop-by-hop as a discrete-event process
- Visualizes ring topology and animated lookup paths
- Supports optional node joins and departures during a lookup
- Shows lookup scaling against a `log2(N)` reference curve

## Project Files

- `app.py`: Streamlit interface and charts
- `chord_sim.py`: Chord network model and SimPy event simulation
- `requirements.txt`: Python dependencies
- `REPORT.md`: submission-ready markdown summary
- `WALKTHROUGH_SCRIPT.md`: suggested script for the required screen-recorded demo

## Run Locally

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

## Suggested Demo Flow

1. Show the generated Chord ring and explain the identifier space.
2. Select a node and inspect its finger table.
3. Run a lookup without churn and step through the hop animation.
4. Enable churn, trigger a join and departure, and rerun the lookup.
5. Scroll to the scaling chart and explain why lookup hops follow `O(log N)`.

## GitHub And Submission

- Push this folder to your GitHub repository and paste the repository URL into your submission portal.
- Export `REPORT.md` to PDF and upload that PDF to VTOP.
