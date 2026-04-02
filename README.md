# Discrete-Event Simulation of the Chord Peer-to-Peer Lookup Protocol Using SimPy and Streamlit

**Student Name:** Suganeshvar  
**Registration Number:** 21MID0128

## Abstract

This project implements the Chord Peer-to-Peer Lookup Protocol as a discrete-event simulation using `SimPy` and presents the results through an interactive `Streamlit` web application. The simulator models an `N`-node Chord ring, builds finger tables for every node, routes key lookups hop-by-hop, and visualizes the lookup path over the ring. The project also supports node joins and departures during execution to demonstrate how churn affects routing. The experimental results show that lookup cost increases approximately as `O(log N)`, which matches the expected behavior of the Chord protocol.

## 1. Introduction

Peer-to-peer distributed systems allow multiple machines to cooperate without relying on a centralized server. One important challenge in such systems is locating the node responsible for storing or managing a specific key. Chord is a distributed hash table protocol designed to solve this problem efficiently.

Chord arranges nodes in a logical ring and assigns both nodes and keys identifiers in the same circular identifier space. Instead of storing global routing information, each node maintains a compact routing structure called a finger table. This enables efficient routing of lookups in logarithmic time.

The purpose of this assignment is to simulate this routing process using a discrete-event approach, measure how lookup latency scales with the number of nodes, and create clear visualizations for the network topology and message forwarding process.

## 2. Objectives

The objectives of this project are:

- To build a discrete-event simulation of the Chord lookup protocol
- To model an `N`-node Chord ring with node identifiers in an `m`-bit space
- To compute predecessor, successor, and finger table entries for each node
- To simulate key lookups routed hop-by-hop through the ring
- To measure lookup latency and hop count as the number of nodes increases
- To show that lookup cost grows approximately as `O(log N)`
- To visualize the ring, finger tables, and lookup path using Streamlit
- To demonstrate routing both with and without node joins and departures

## 3. Tools and Technologies Used

The following technologies were used in this project:

- `Python` for implementing the protocol and application logic
- `SimPy` for discrete-event simulation of lookup hops and churn events
- `Streamlit` for building an interactive user interface
- `Plotly` for ring and scaling visualizations
- `Pandas` for presenting finger tables, hop traces, and experimental data

## 4. Concept of the Chord Protocol

Chord maps both nodes and keys into a circular identifier space of size `2^m`, where `m` is the number of identifier bits.

### 4.1 Node Placement

Each node is assigned a unique identifier in the range `0` to `2^m - 1`. These identifiers are arranged in increasing order on a circular ring.

### 4.2 Key Ownership

A key is stored at the first node whose identifier is equal to or follows the key in clockwise order. This node is called the successor of the key.

### 4.3 Successor and Predecessor

Each node keeps track of:

- Its predecessor node
- Its successor node

These references allow the ring to remain navigable even when nodes join or leave.

### 4.4 Finger Table

To speed up routing, every node maintains a finger table with `m` entries. For a node with identifier `n`, the start of the `i`th finger entry is:

`start(i) = (n + 2^(i-1)) mod 2^m`

Each entry points to the successor of that start value. Because these entries jump exponentially farther around the ring, lookups require only a logarithmic number of hops in the average case.

## 5. Problem Statement

The assignment requires simulation of the Chord Peer-to-Peer Lookup Protocol using discrete-event modeling and visualization. The implementation must:

- Create a Chord ring with multiple nodes
- Maintain finger tables for all nodes
- Simulate routing of key lookups hop-by-hop
- Visualize the network and the lookup path
- Support node joins and departures
- Demonstrate scaling behavior as the number of nodes grows

## 6. System Design

The system is divided into two major parts:

- The simulation engine
- The visualization layer

### 6.1 Simulation Engine

The simulation engine is implemented in `chord_sim.py`. It is responsible for:

- Generating node identifiers
- Constructing the Chord ring
- Computing predecessor and successor links
- Building finger tables
- Scheduling lookup events using SimPy
- Handling node join and departure events
- Recording hop-by-hop lookup traces
- Measuring hops and latency

### 6.2 Visualization Layer

The visualization layer is implemented in `app.py`. It provides:

- Controls for ring size, node count, seed, and hop latency
- A ring topology graph
- Finger table inspection for any selected node
- Lookup execution controls
- Hop-by-hop animation of the route
- Churn controls for joins and departures
- A scaling chart comparing measured hops with `log2(N)`

## 7. Step-by-Step Project Implementation

This section explains the complete implementation process followed in the project.

### Step 1: Create the Identifier Space

An `m`-bit identifier space is created, giving a total ring size of `2^m`. For example, if `m = 6`, the ring has `64` possible identifier positions from `0` to `63`.

### Step 2: Generate the Nodes

A chosen number of unique node identifiers are randomly sampled from the identifier space. These node identifiers are sorted and inserted into the ring.

### Step 3: Construct the Ring

After sorting the node identifiers:

- The previous node in sorted order becomes the predecessor
- The next node in sorted order becomes the successor
- Wrap-around logic is used at the ends of the ring

This establishes the circular Chord structure.

### Step 4: Build the Finger Table for Every Node

For each node:

1. Compute the `start` value for each finger entry
2. Find the first live node that succeeds that value in the ring
3. Store this node as the finger table successor

This step allows each node to maintain logarithmic routing information.

### Step 5: Simulate Lookup Routing

When a lookup begins:

1. A start node is selected
2. A key is selected
3. The simulator checks whether the current node is responsible for that key
4. If not, it forwards the request to the closest preceding finger
5. Each forwarding action consumes one event delay in SimPy
6. The process repeats until the correct responsible node is reached

Each hop is recorded with:

- Source node
- Destination node
- Key
- Simulation time
- Routing note

### Step 6: Handle Node Joins and Departures

The simulator optionally supports churn events:

- A join event inserts a new node into the ring at a chosen time
- A leave event removes an existing node at a chosen time

After each churn event, the ring structure and finger tables are rebuilt so that later hops use the updated routing state.

### Step 7: Display Results in Streamlit

The Streamlit application displays:

- The current ring topology
- The finger table of any selected node
- Lookup metrics such as total hops and latency
- The exact path followed by the lookup
- Churn events that occurred during the run

### Step 8: Run the Scaling Experiment

To verify the Chord property, the simulator is run for multiple values of `N`, such as:

- `4`
- `8`
- `16`
- `32`
- `64`

For each network size, multiple random lookups are simulated and the average hop count is calculated. These results are then compared with the theoretical reference curve `log2(N)`.

## 8. Algorithm Used

The routing logic used in this implementation is based on the Chord lookup procedure.

### 8.1 Responsible Node Check

A node is responsible for a key if the key lies in the interval between the node's predecessor and the node itself, moving clockwise on the ring.

### 8.2 Closest Preceding Finger

If the current node is not responsible for the key, the node searches its finger table from the farthest finger to the nearest finger and selects the closest preceding finger that moves the query closer to the target key.

### 8.3 Successor Fallback

If no finger offers progress, the lookup is forwarded to the immediate successor.

### 8.4 Event Scheduling

Every forwarding action is modeled as a discrete event with a configurable latency. SimPy advances simulated time whenever a hop occurs.

## 9. Important Files in the Project

### 9.1 `chord_sim.py`

This file contains the main protocol logic:

- `FingerEntry` data structure
- `Node` data structure
- `LookupStep` and `LookupRecord`
- `ChordNetwork` class
- Ring construction functions
- Finger table generation
- Lookup simulation using SimPy
- Join and departure event handling
- Scaling experiment function

### 9.2 `app.py`

This file contains the Streamlit interface:

- Sidebar controls
- Ring visualization using Plotly
- Finger table display using Pandas
- Lookup walkthrough panel
- Animation controls for hop tracing
- Scaling chart for performance observation

### 9.3 `README.md`

This file provides basic project instructions and project overview.

### 9.4 `WALKTHROUGH_SCRIPT.md`

This file contains a ready-to-use narration structure for the required screen-recorded explanation.

## 10. Working of the Program

The working of the program can be summarized as follows:

1. The user selects the identifier bit size and number of nodes.
2. The program generates a Chord ring with random live nodes.
3. The predecessor, successor, and finger tables are computed.
4. The user selects a node to inspect and a start node for lookup.
5. The user enters a key to search.
6. The program runs the lookup as a SimPy process.
7. Each hop is recorded and visualized.
8. The responsible node for the key is displayed.
9. If churn is enabled, node joins and departures occur during execution.
10. The user observes how the route changes and how average hops scale with `N`.

## 11. Sample Observations

The simulator shows the following important observations:

- Finger tables significantly reduce the number of routing hops
- Lookups do not need to travel through every node sequentially
- The average number of hops grows slowly even when the network size increases
- The scaling chart follows the general shape of `log2(N)`
- Node joins and departures may alter the lookup path, but the ring can still continue routing

## 12. Result Analysis

The experimental results indicate that Chord lookup performance is approximately logarithmic. For small values of `N`, the average hop count is also small. As `N` increases, the hop count increases much more slowly than linear growth.

This confirms the main advantage of Chord:

- Efficient decentralized routing
- Small routing table size
- Good scalability for large peer-to-peer systems

The churn experiment further demonstrates that dynamic membership affects routing, but the protocol structure can still adapt when the routing tables are updated.

## 13. Testing and Verification

The project was verified in the following ways:

- The core simulator was executed directly in Python to confirm that lookups return the correct responsible node
- The scaling experiment was run to ensure that average hop count rises gradually with node count
- The Streamlit application was launched successfully to confirm that the interface runs correctly
- Lookup traces were checked for both stable and churn-enabled scenarios

## 14. How to Run the Project

Open the project folder in the terminal and run:

```powershell
python -m pip install -r requirements.txt
streamlit run app.py
```

After launching the app:

1. Choose the identifier bit size
2. Choose the initial number of nodes
3. Select the node to inspect
4. Select the node from which the lookup begins
5. Enter a key value
6. Run the lookup simulation
7. Observe the ring, finger table, and hop animation
8. Enable churn if required and rerun the experiment
9. Check the scaling chart at the bottom of the page

## 15. Screen Recording Guide

For the required screen-recorded code walkthrough, the following structure can be used:

1. Introduce the assignment topic
2. Open `chord_sim.py` and explain the main classes and routing logic
3. Show how finger tables are built
4. Explain how SimPy is used to model hop delays
5. Open `app.py` and explain the UI controls and visualization
6. Run the application
7. Demonstrate one lookup without churn
8. Demonstrate one lookup with join and departure events
9. Explain the scaling graph and conclude that lookup growth is approximately `O(log N)`

## 16. Advantages of the Project

- Clear implementation of a real distributed systems protocol
- Combines theory with simulation and visualization
- Makes routing behavior easy to understand through animation
- Shows both stable network behavior and dynamic churn behavior
- Demonstrates the logarithmic scaling property expected from Chord

## 17. Limitations

Although the simulator demonstrates the core behavior of Chord, it is still a simplified academic model. For example:

- It assumes immediate routing table rebuild after churn events
- It does not model packet loss or network failures
- It does not include stabilization timers used in production Chord implementations
- It focuses on lookup behavior rather than full distributed storage operations

These limitations are acceptable for the purpose of this assignment because the main objective is to understand lookup routing and scaling behavior.

## 18. Conclusion

This project successfully implements the Chord Peer-to-Peer Lookup Protocol as a discrete-event simulation using SimPy and Streamlit. The simulator constructs a Chord ring, computes finger tables, routes keys hop-by-hop, and visualizes both topology and message forwarding. The scaling experiment shows that the average lookup cost grows close to `O(log N)`, which confirms the theoretical property of the protocol. The inclusion of node joins and departures further strengthens the project by showing how routing paths can change under dynamic network conditions.

## 19. Submission Note

This report is prepared in Markdown format so that it can be exported as a PDF for submission. Along with this report, the project includes source code, a Streamlit-based demonstration interface, and a script for the screen-recorded walkthrough.
