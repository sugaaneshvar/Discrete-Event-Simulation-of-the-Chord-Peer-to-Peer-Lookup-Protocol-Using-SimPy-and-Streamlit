# Chord Peer-to-Peer Lookup Protocol Using SimPy and Streamlit

## Objective

This activity implements the Chord peer-to-peer lookup protocol as a discrete-event simulation. The simulator models an `N`-node ring, computes finger tables, routes lookups hop-by-hop, and visualizes the effect of joins and departures on lookup behavior.

## Implementation Summary

The simulator uses a fixed `m`-bit identifier space and randomly places nodes on the ring. Each node stores:

- Its identifier
- Its predecessor and successor
- A finger table with `m` entries

Key lookups are modeled as `SimPy` processes. Every hop consumes one configurable latency unit. The routing rule follows Chord's idea of forwarding the request to the closest preceding finger until the responsible successor is reached.

## Visual Components

- Ring topology view for all active nodes
- Finger table table for any selected node
- Hop-by-hop lookup animation
- Optional churn controls for node joins and departures
- Lookup scaling chart comparing average hops against `log2(N)`

## Observation

The scaling chart shows that average lookup hops grow slowly as the network size increases. This matches the expected `O(log N)` behavior of Chord because each node's finger table allows the lookup to skip large portions of the ring instead of following only immediate successors.

## How To Run

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

## Conclusion

The project demonstrates that Chord provides efficient decentralized key lookup with logarithmic routing cost, while also showing how routing paths can change when peers join or leave during execution.
