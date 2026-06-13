import streamlit as st
import numpy as np
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="Hybrid Acoustic Simulation",
    page_icon="🎵",
    layout="wide"
)

# ── Custom CSS ──
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #1A1A2E 0%, #2E86AB 100%);
        padding: 2rem;
        border-radius: 12px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .audio-card {
        background: white;
        border-radius: 12px;
        padding: 1.2rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.08);
        border-top: 4px solid #2E86AB;
        margin-bottom: 1rem;
        text-align: center;
    }
    .receiver-info {
        background: #F0F4F8;
        border-radius: 10px;
        padding: 1rem;
        border-left: 4px solid #2E86AB;
        margin-bottom: 1rem;
    }
    .selected-badge {
        background: #2E86AB;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: bold;
    }
    h2 { color: #1A1A2E; }
    h3 { color: #2E86AB; }
</style>
""", unsafe_allow_html=True)

# ════════════════════════════════
# DATA — Room geometry + positions
# ════════════════════════════════

# Room corners
ROOM_CORNERS_X = [0.0, 5.51566, 6.21333, 0.0,     0.0    ]
ROOM_CORNERS_Y = [0.0, 0.0,     4.01907, 5.09763, 0.0    ]

# Sources
SOURCES = {
    "S1": {"pos": [1.04, 2.59], "label": "Source 1"},
    "S2": {"pos": [1.36, 3.76], "label": "Source 2"},
}

# Receivers
RECEIVERS = {
    "R1":  {"pos": [3.26, 1.76], "label": "Receiver 1"},
    "R2":  {"pos": [2.03, 0.50], "label": "Receiver 2"},
    "R11": {"pos": [3.80, 2.77], "label": "Receiver 11"},
    "R13": {"pos": [0.50, 4.50], "label": "Receiver 13"},
}

# Scenario panels
PANELS = {
    "Scenario 1": [
        # Front wall panels
        {"x": [0.5, 2.6, 2.6, 0.5, 0.5],   "y": [0, 0, 0, 0, 0]},
        {"x": [3.41, 4.01, 4.01, 3.41, 3.41], "y": [0, 0, 0, 0, 0]},
        {"x": [4.79, 5.39, 5.39, 4.79, 4.79], "y": [0, 0, 0, 0, 0]},
    ],
    "Scenario 2": [
        {"x": [0.5, 2.6, 2.6, 0.5, 0.5], "y": [0, 0, 0, 0, 0]},
    ],
    "Empty Room": []
}

# Audio file mapping
# Format: audio/{scenario}/{source}_{receiver}.wav
def get_audio_path(scenario, source, receiver, model):
    """Get path to audio file"""
    scenario_key = scenario.lower().replace(" ", "_").replace("—", "").strip()
    filename = f"{model}_{source}{receiver}.wav"
    return os.path.join("audio", scenario_key, filename)

# ════════════════════════════════
# HEADER
# ════════════════════════════════
st.markdown("""
<div class="main-header">
    <h1>🎵 Hybrid Acoustic Simulation</h1>
    <p style="font-size: 1.1rem; opacity: 0.9; margin: 0.5rem 0 0 0;">
        Click a receiver position on the map to listen to the room acoustics
    </p>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════
# CONTROLS ROW
# ════════════════════════════════
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])

with col_ctrl1:
    scenario = st.selectbox(
        "🏠 Room Scenario",
        ["Empty Room", "Scenario 1 — Panels + Carpet", "Scenario 2 — Fewer Panels"],
        key="scenario"
    )

with col_ctrl2:
    source = st.selectbox(
        "🔊 Sound Source",
        list(SOURCES.keys()),
        format_func=lambda x: f"{x} — {SOURCES[x]['label']}",
        key="source"
    )

with col_ctrl3:
    selected_receiver = st.selectbox(
        "🎧 Receiver Position",
        list(RECEIVERS.keys()),
        format_func=lambda x: f"{x} — {RECEIVERS[x]['label']}",
        key="receiver"
    )

st.markdown("---")

# ════════════════════════════════
# MAIN LAYOUT — Map + Audio
# ════════════════════════════════
col_map, col_audio = st.columns([1.2, 1])

# ── LEFT: Interactive Room Map ──
with col_map:
    st.markdown("### 🏠 Room Layout")
    st.markdown("*Select a receiver from the dropdown above or click on the map*")

    # Get scenario key for panels
    scenario_key = "Empty Room"
    if "Scenario 1" in scenario:
        scenario_key = "Scenario 1"
    elif "Scenario 2" in scenario:
        scenario_key = "Scenario 2"

    fig = go.Figure()

    # ── Room outline ──
    fig.add_trace(go.Scatter(
        x=ROOM_CORNERS_X,
        y=ROOM_CORNERS_Y,
        fill='toself',
        fillcolor='rgba(173, 216, 230, 0.2)',
        line=dict(color='#1A1A2E', width=3),
        name='Room',
        hoverinfo='skip'
    ))

    # ── Panels ──
    for i, panel in enumerate(PANELS[scenario_key]):
        fig.add_trace(go.Scatter(
            x=panel["x"], y=panel["y"],
            fill='toself',
            fillcolor='rgba(76, 175, 80, 0.6)',
            line=dict(color='green', width=2),
            name='Acoustic Panel' if i == 0 else None,
            showlegend=(i == 0),
            hoverinfo='name',
            hovertemplate='Acoustic Panel<extra></extra>'
        ))

    # ── Sources ──
    for src_name, src_data in SOURCES.items():
        is_selected = (src_name == source)
        fig.add_trace(go.Scatter(
            x=[src_data["pos"][0]],
            y=[src_data["pos"][1]],
            mode='markers+text',
            marker=dict(
                size=20 if is_selected else 14,
                color='#F44336',
                symbol='star',
                line=dict(color='white', width=2)
            ),
            text=[src_name],
            textposition='top center',
            textfont=dict(size=12, color='#F44336'),
            name=f'Source {src_name}',
            hovertemplate=f'<b>{src_data["label"]}</b><br>'
                         f'x={src_data["pos"][0]:.2f}m, '
                         f'y={src_data["pos"][1]:.2f}m<extra></extra>'
        ))

    # ── Receivers ──
    for rec_name, rec_data in RECEIVERS.items():
        is_selected = (rec_name == selected_receiver)
        fig.add_trace(go.Scatter(
            x=[rec_data["pos"][0]],
            y=[rec_data["pos"][1]],
            mode='markers+text',
            marker=dict(
                size=22 if is_selected else 14,
                color='#2E86AB' if is_selected else '#90CAF9',
                symbol='circle',
                line=dict(
                    color='white' if is_selected else '#2E86AB',
                    width=3 if is_selected else 1
                )
            ),
            text=[rec_name],
            textposition='top center',
            textfont=dict(
                size=13 if is_selected else 11,
                color='#2E86AB'
            ),
            name=f'Receiver {rec_name}',
            hovertemplate=f'<b>{rec_data["label"]}</b><br>'
                         f'x={rec_data["pos"][0]:.2f}m, '
                         f'y={rec_data["pos"][1]:.2f}m<extra></extra>'
        ))

    # ── Line from source to selected receiver ──
    src_pos = SOURCES[source]["pos"]
    rec_pos = RECEIVERS[selected_receiver]["pos"]
    fig.add_trace(go.Scatter(
        x=[src_pos[0], rec_pos[0]],
        y=[src_pos[1], rec_pos[1]],
        mode='lines',
        line=dict(color='#FF9800', width=2, dash='dot'),
        name='Source → Receiver',
        hoverinfo='skip'
    ))

    # ── Distance annotation ──
    dist = np.sqrt(
        (src_pos[0]-rec_pos[0])**2 +
        (src_pos[1]-rec_pos[1])**2
    )
    td = dist / 343 * 1000

    fig.update_layout(
        xaxis=dict(
            range=[-0.3, 7],
            scaleanchor="y",
            title="X (m)",
            showgrid=True,
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            range=[-0.3, 6],
            title="Y (m)",
            showgrid=True,
            gridcolor='#f0f0f0'
        ),
        height=520,
        plot_bgcolor='white',
        paper_bgcolor='white',
        legend=dict(
            x=0.01, y=0.99,
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#ddd',
            borderwidth=1,
            font=dict(size=11)
        ),
        margin=dict(l=10, r=10, t=10, b=10),
        hovermode='closest'
    )

    st.plotly_chart(fig, use_container_width=True)

    # ── Position info ──
    st.markdown(f"""
    <div class="receiver-info">
        <b>📍 Selected:</b> Source <b>{source}</b> → 
        Receiver <b>{selected_receiver}</b><br>
        <b>📏 Distance:</b> {dist:.3f}m  | 
        <b>⏱️ Direct sound arrival:</b> {td:.2f}ms
    </div>
    """, unsafe_allow_html=True)

# ── RIGHT: Audio Players ──
with col_audio:
    st.markdown("### 🎧 Listen to Room Acoustics")
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <span class="selected-badge">
            {source} → {selected_receiver} | {scenario.split('—')[0].strip()}
        </span>
    </div>
    """, unsafe_allow_html=True)

    st.info("🎧 Use headphones for binaural listening")

    # Audio models to display
    audio_models = [
        ("🎯 RAVEN Reference",  "raven",  "#FF5722"),
        ("📐 Geometric Model",  "geo",    "#2196F3"),
        ("🌊 Wave Model",       "wave",   "#4CAF50"),
        ("🔀 Hybrid Model",     "hybrid", "#FF9800"),
    ]

    for label, model, colour in audio_models:
        audio_path = get_audio_path(
            scenario_key, source, selected_receiver, model
        )

        st.markdown(f"""
        <div class="audio-card" style="border-top-color: {colour};">
            <h4 style="color: {colour}; margin: 0 0 0.5rem 0;">
                {label}
            </h4>
        """, unsafe_allow_html=True)

        if os.path.exists(audio_path):
            with open(audio_path, "rb") as f:
                st.audio(f.read(), format="audio/wav")
        else:
            st.markdown(f"""
            <p style="color: #999; font-size: 0.85rem; margin: 0;">
                ⏳ Audio not yet available for this position
            </p>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════
# BOTTOM — Quick Stats
# ════════════════════════════════
st.markdown("---")
st.markdown("### 📊 Quick Statistics")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Source",    source)
col2.metric("Receiver",  selected_receiver)
col3.metric("Distance",  f"{dist:.2f}m")
col4.metric("Direct td", f"{td:.2f}ms")
col5.metric("Scenario",  scenario.split("—")[0].strip())