# Screen-Recorded Walkthrough Script

## Intro

In this project, I implemented the Chord peer-to-peer lookup protocol using a discrete-event simulation in SimPy and a visual interface in Streamlit. The app shows how nodes form a ring, how finger tables are constructed, and how a lookup is routed hop-by-hop to the responsible node.

## Code Walkthrough

1. Open `chord_sim.py`.
2. Explain the `Node`, `FingerEntry`, `LookupStep`, and `LookupRecord` data classes.
3. Explain how `ChordNetwork.generate()` creates random node IDs in the identifier space.
4. Show `rebuild_routing()` and explain predecessor, successor, and finger table construction.
5. Show `closest_preceding_finger()` and `simulate_lookup()` to explain lookup routing and SimPy event scheduling.
6. Open `app.py`.
7. Explain the sidebar controls, ring visualization, finger table view, and scaling experiment chart.

## Live Demo

1. Run `streamlit run app.py`.
2. Show the initial ring with a selected node.
3. Inspect a finger table and explain how each finger points to a successor.
4. Run a lookup without churn and animate the message path.
5. Enable churn, set one join and one departure event, and rerun the lookup.
6. Show that the route can change after churn.
7. Scroll to the scaling chart and explain that average hops grow roughly with `log2(N)`.

## Closing

This simulation demonstrates the main idea behind Chord: decentralized routing with logarithmic lookup complexity, supported by compact finger tables instead of global routing knowledge.
