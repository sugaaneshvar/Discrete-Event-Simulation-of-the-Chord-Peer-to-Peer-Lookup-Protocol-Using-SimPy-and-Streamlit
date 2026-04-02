from __future__ import annotations

import math

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from chord_sim import ChordNetwork, build_scaling_rows


st.set_page_config(
    page_title="Chord Protocol Discrete-Event Simulator",
    layout="wide",
)


def node_xy(node_id: int, ring_size: int) -> tuple[float, float]:
    angle = (2 * math.pi * node_id) / ring_size
    return math.cos(angle), math.sin(angle)


def ring_figure(network: ChordNetwork, selected_node: int | None, lookup_record=None) -> go.Figure:
    rows = pd.DataFrame(network.ring_rows())
    fig = go.Figure()

    circle_t = [2 * math.pi * i / 200 for i in range(201)]
    fig.add_trace(
        go.Scatter(
            x=[math.cos(v) for v in circle_t],
            y=[math.sin(v) for v in circle_t],
            mode="lines",
            line={"color": "#cbd5e1", "width": 2},
            hoverinfo="skip",
            showlegend=False,
        )
    )

    path_edges = []
    if lookup_record:
        for step in lookup_record.steps:
            source_x, source_y = node_xy(step.from_node, network.ring_size)
            target_x, target_y = node_xy(step.to_node, network.ring_size)
            path_edges.append(
                go.Scatter(
                    x=[source_x, target_x],
                    y=[source_y, target_y],
                    mode="lines+markers",
                    line={"color": "#ef4444", "width": 4},
                    marker={"size": 1},
                    hovertext=f"{step.from_node} -> {step.to_node} at t={step.time:.1f}",
                    hoverinfo="text",
                    showlegend=False,
                )
            )

    for edge in path_edges:
        fig.add_trace(edge)

    colors = [
        "#2563eb" if selected_node is not None and node_id == selected_node else "#0f172a"
        for node_id in rows["node_id"].tolist()
    ]
    sizes = [20 if selected_node is not None and node_id == selected_node else 14 for node_id in rows["node_id"].tolist()]
    fig.add_trace(
        go.Scatter(
            x=rows["x"],
            y=rows["y"],
            mode="markers+text",
            text=[str(node_id) for node_id in rows["node_id"]],
            textposition="top center",
            marker={"size": sizes, "color": colors, "line": {"color": "#f8fafc", "width": 1}},
            hovertemplate="Node %{text}<extra></extra>",
            showlegend=False,
        )
    )

    fig.update_layout(
        title="Chord Ring Topology",
        paper_bgcolor="#f8fafc",
        plot_bgcolor="#f8fafc",
        xaxis={"visible": False},
        yaxis={"visible": False, "scaleanchor": "x", "scaleratio": 1},
        margin={"l": 0, "r": 0, "t": 40, "b": 0},
        height=520,
    )
    return fig


def scaling_figure(rows: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=rows["node_count"],
            y=rows["avg_hops"],
            mode="lines+markers",
            name="Average hops",
            line={"color": "#2563eb", "width": 3},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=rows["node_count"],
            y=rows["log2_n"],
            mode="lines+markers",
            name="log2(N) reference",
            line={"color": "#f97316", "width": 3, "dash": "dash"},
        )
    )
    fig.update_layout(
        title="Lookup Cost Growth",
        xaxis_title="Number of nodes",
        yaxis_title="Average hops",
        paper_bgcolor="#ffffff",
        plot_bgcolor="#ffffff",
        height=360,
    )
    return fig


st.title("Chord Peer-to-Peer Lookup Protocol Simulator")
st.caption(
    "SimPy drives hop-by-hop discrete-event lookups across a Chord ring, with optional churn from joins and departures."
)

with st.sidebar:
    st.header("Simulation Controls")
    bits = st.slider("Identifier bits (m)", min_value=4, max_value=10, value=6)
    ring_size = 2**bits
    max_nodes = min(ring_size, 128)
    node_count = st.slider("Initial node count (N)", min_value=4, max_value=max_nodes, value=min(16, max_nodes))
    seed = st.number_input("Random seed", min_value=1, value=7, step=1)
    hop_latency = st.slider("Latency per hop", min_value=0.25, max_value=3.0, value=1.0, step=0.25)
    enable_churn = st.toggle("Enable join/departure during lookup", value=False)

network = ChordNetwork.generate(
    bits=bits,
    node_count=node_count,
    seed=int(seed),
    hop_latency=hop_latency,
)
node_ids = network.node_ids()

col_a, col_b = st.columns([2, 1])
with col_b:
    selected_node = st.selectbox("Inspect node", options=node_ids, index=0)
    start_node = st.selectbox(
        "Start lookup from node",
        options=node_ids,
        index=min(1, len(node_ids) - 1),
    )
    key = st.number_input("Lookup key", min_value=0, max_value=ring_size - 1, value=min(23, ring_size - 1), step=1)

    join_events = []
    leave_events = []
    if enable_churn:
        available_join_ids = [n for n in range(ring_size) if n not in node_ids]
        available_leave_ids = [n for n in node_ids if n != start_node]
        if available_join_ids:
            join_node = st.selectbox("Joining node ID", options=available_join_ids, index=0)
            join_time = st.slider("Join time", min_value=0.5, max_value=6.0, value=1.5, step=0.5)
            join_events.append({"node_id": join_node, "time": join_time})
        if available_leave_ids:
            leave_node = st.selectbox("Departing node ID", options=available_leave_ids, index=0)
            leave_time = st.slider("Departure time", min_value=0.5, max_value=6.0, value=2.5, step=0.5)
            leave_events.append({"node_id": leave_node, "time": leave_time})

    if st.button("Run lookup simulation", use_container_width=True):
        sim_network = network.clone()
        st.session_state["lookup_record"] = sim_network.simulate_lookup(
            start_node=start_node,
            key=int(key),
            join_events=join_events,
            leave_events=leave_events,
        )
        st.session_state["lookup_network"] = sim_network

lookup_record = st.session_state.get("lookup_record")
lookup_network = st.session_state.get("lookup_network", network)
selected_node_in_lookup = selected_node if selected_node in lookup_network.nodes else None

with col_a:
    st.plotly_chart(
        ring_figure(lookup_network, selected_node=selected_node_in_lookup, lookup_record=lookup_record),
        use_container_width=True,
    )

stats_cols = st.columns(4)
stats_cols[0].metric("Ring size", ring_size)
stats_cols[1].metric("Live nodes", len(lookup_network.node_ids()))
stats_cols[2].metric(
    "Selected successor",
    lookup_network.nodes[selected_node].successor if selected_node_in_lookup is not None else "departed",
)
stats_cols[3].metric(
    "Selected predecessor",
    lookup_network.nodes[selected_node].predecessor if selected_node_in_lookup is not None else "departed",
)

section_left, section_right = st.columns([1.2, 1])
with section_left:
    st.subheader(f"Finger Table for Node {selected_node}")
    if selected_node_in_lookup is None:
        st.warning("The selected node is not active after the latest churn simulation.")
    else:
        st.dataframe(
            pd.DataFrame(lookup_network.finger_table_rows(selected_node)),
            use_container_width=True,
            hide_index=True,
        )

with section_right:
    st.subheader("Lookup Walkthrough")
    if lookup_record:
        st.write(
            f"Key `{lookup_record.key}` started at node `{lookup_record.start_node}` and resolved at node "
            f"`{lookup_record.responsible_node}` after `{lookup_record.hops}` hops and `{lookup_record.latency:.1f}` time units."
        )
        if lookup_record.churn_events:
            st.write("Churn events during simulation:")
            for event in lookup_record.churn_events:
                st.write(f"- {event}")
        if lookup_record.steps:
            step_index = st.slider(
                "Animate hop",
                min_value=1,
                max_value=len(lookup_record.steps),
                value=len(lookup_record.steps),
            )
            partial_steps = lookup_record.steps[:step_index]
            partial_record = type(lookup_record)(
                key=lookup_record.key,
                start_node=lookup_record.start_node,
                responsible_node=lookup_record.responsible_node,
                hops=len(partial_steps),
                latency=partial_steps[-1].time,
                steps=partial_steps,
                churn_events=lookup_record.churn_events,
            )
            st.plotly_chart(
                ring_figure(lookup_network, selected_node=selected_node_in_lookup, lookup_record=partial_record),
                use_container_width=True,
            )
            st.dataframe(
                pd.DataFrame([step.__dict__ for step in partial_steps]),
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("This key is already handled by the starting node, so no hop was needed.")
    else:
        st.info("Run a lookup to see the hop-by-hop path.")

st.subheader("Scaling Experiment")
counts = [4, 8, 16, 32, 64]
counts = [count for count in counts if count <= max_nodes]
scaling_rows = pd.DataFrame(
    build_scaling_rows(
        bits=bits,
        seed=int(seed),
        hop_latency=hop_latency,
        counts=counts,
        trial_count=48,
    )
)
st.plotly_chart(scaling_figure(scaling_rows), use_container_width=True)
st.dataframe(scaling_rows.round(3), use_container_width=True, hide_index=True)

st.markdown(
    """
### What To Observe
- Chord keeps routing tables at `O(log N)` size through finger tables.
- Lookup latency tracks average hop count, which grows close to `log2(N)` in the experiment above.
- When churn is enabled, joins and departures rebuild the routing state and can change the lookup path mid-simulation.
"""
)
