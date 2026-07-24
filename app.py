import streamlit as st
import numpy as np
import plotly.graph_objects as go
import os
import random
import base64

# ── Only ONE set_page_config, at the very top ──
st.set_page_config(page_title="HYBRID ACOUSTIC SIMULATION", layout="wide")

# ── Load Wobbly font ──
with open("font/wobbly.ttf", "rb") as f:
    font_data = base64.b64encode(f.read()).decode()

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@300;400&display=swap');

@font-face {{
    font-family: 'Wobbly';
    src: url(data:font/truetype;base64,{font_data}) format('truetype');
}}

/* Body font — IBM Plex Mono everywhere except the header */
html, body, [class*="css"], .stSelectbox, .stMarkdown, p, div {{
    font-family: 'IBM Plex Mono', monospace !important;
    font-weight: 300;
}}
</style>
""", unsafe_allow_html=True)

# ── Wobbly header ──
def wobbly_spans(text, seed=42):
    random.seed(seed)
    spans = []
    for ch in text:
        if ch == " ":
            spans.append('<span style="display:inline-block; width:0.5em;"></span>')
        else:
            rot = random.uniform(-4, 4)
            dy  = random.uniform(-4, 4)
            spans.append(
                f'<span style="display:inline-block; '
                f'transform: rotate({rot:.1f}deg) translateY({dy:.1f}px); '
                f'font-family: Wobbly, cursive !important; '
                f'font-size: 3.5rem; '
                f'color: black; '
                f'">{ch}</span>'
            )
    return "".join(spans)
st.markdown(f"""
<div class="wobbly-header" style="border-bottom: 2px solid black; padding: 1.5rem 0 1rem 0; text-align: left; margin-bottom: 2rem;">
    <div style="display:flex; justify-content:left; flex-wrap:wrap; gap:1px;">
        {wobbly_spans("HYBRID ACOUSTIC SIMULATION")}
    </div>
    ...
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════
# DRY SIGNAL — always visible reference player
# ════════════════════════════════
st.markdown("""
<div class="audio-card" style="border-top-color: #000000; margin-bottom: 1.5rem;">
    <h4 style="color: #000000; margin: 0 0 0.5rem 0;">
        DRY SIGNAL (REFERENCE)
    </h4>
</div>
""", unsafe_allow_html=True)

dry_signal_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "audio", "dry_signal.wav"
)

if os.path.exists(dry_signal_path):
    with open(dry_signal_path, "rb") as f:
        st.audio(f.read(), format="audio/wav")
else:
    st.markdown("""
    <p style="color: #999; font-size: 0.85rem; margin: 0;">
        Dry signal not found at audio/dry_signal.wav
    </p>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── All other CSS in one block ──

st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    .wobbly-header span {
        font-family: Wobbly, cursive !important;
    }
    .stSelectbox > div > div {
        border: 1px solid black;
        border-radius: 8px;
        background: white;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 300;
    }
    [data-testid="metric-container"] {
        background: none;
        border-top: 1px solid black;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 300;
    }
    .audio-card {
        background: white;
        border-radius: 0;
        color: #129f10;
        border: none;
        border-top: 1px solid black;
        box-shadow: none;
        padding: 1rem 0;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 300;
    }
    .receiver-info {
        background: none;
        border-left: 1px solid black;
        border-radius: 0;
        font-family: 'IBM Plex Mono', monospace;
        font-weight: 300;
    }
    .selected-badge {
        background: #129f10;
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 300;
        font-family: 'IBM Plex Mono', monospace;
    }
    h2, h3 { 
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 300;
        color: #129f10;
    }
</style>
""", unsafe_allow_html=True)
# ════════════════════════════════
# DATA — Room geometry + positions
# ════════════════════════════════

# Room corners
ROOM_CORNERS_X = [0.0, 5.51566, 6.21333, 0.0,     0.0    ]
ROOM_CORNERS_Y = [0.0, 0.0,     4.01907, 5.09763, 0.0    ]

SHOEBOX_CORNERS_X = [0.0, 5.0, 5.0, 0.0, 0.0]
SHOEBOX_CORNERS_Y = [0.0, 0.0, 4.0, 4.0, 0.0]

# Sources
SOURCES = {
    "S2": {"pos": [1.36, 3.76], "label": "SOURCE 2"},
}

# Receivers
RECEIVERS = {
    "R1":  {"pos": [3.26, 1.76], "label": "RECEIVER 1"},
    "R2":  {"pos": [2.03, 0.50], "label": "RECEIVER 2"},
    "R3": {"pos": [3.80, 2.77], "label": "RECEIVER 3"},
    "R4": {"pos": [5.46, 2.57], "label": "RECEIVER 4"},
    "R5": {"pos": [0.50, 4.50], "label": "RECEIVER 5"},
}

SOURCES_SHOEBOX = {
    "S1": {"pos": [1.04, 2.59], "label": "SOURCE 1"},
    "S2": {"pos": [1.0, 1.0], "label": "SOURCE 2"},
    "S3": {"pos": [1.2, 1.5], "label": "SOURCE 3"},
}

RECEIVERS_SHOEBOX = {
    "R1": {"pos": [3.26, 1.76], "label": "RECEIVER 1"},
    "R2": {"pos": [4.0, 3.0], "label": "RECEIVER 2"},
    "R3": {"pos": [3.1, 2.0], "label": "RECEIVER 3"},
}

VALID_PAIRS_SHOEBOX = {
    "S1": ["R1"],
    "S2": ["R2"],
    "S3": ["R3"],
}

VALID_PAIRS_PENTAGON = {
    "S2": ["R1", "R2", "R3", "R4", "R5"],
}

# Scenario panels
PANELS = {
    "Scenario 1": [
        # Front wall panels
        {"x": [3.41566, 4.01566], "y": [0, 0]},
        {"x": [4.79566, 5.39566], "y": [0, 0]},
        # Rear wall panels
        {"x": [5.82908, 4.64676], "y": [4.08577, 4.29100]},
        {"x": [2.73904, 1.55672], "y": [4.62216, 4.82740]},
        {"x": [1.35967, 0.17735], "y": [4.86161, 5.06684]},
        # Left wall panels
        {"x": [0.0, 0.0], "y": [3.32763, 4.52763]},
        {"x": [0.0, 0.0], "y": [0.0, 2.7]},
    ],
    "Scenario 2": [
        {"x": [5.82891, 4.64659], "y": [4.08479, 4.29002]},
        {"x": [2.73887, 1.55655], "y": [4.62118, 4.82642]},
        {"x": [0.001, 0.001], "y": [0.0, 2.70]},
    ],
    "Shoebox": [],    
}

# Audio file mapping
# Format: audio/{scenario}/{source}_{receiver}.wav
def get_audio_path(scenario_folder, source, receiver, model):
    """Get path to audio file"""
    filename = f"{model}_{source}{receiver}.wav"
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, "audio", scenario_folder, filename)


# ════════════════════════════════
# CONTROLS ROW
# ════════════════════════════════
col_ctrl1, col_ctrl2, col_ctrl3 = st.columns([2, 2, 2])

with col_ctrl1:
    scenario = st.selectbox(
        "ROOM SCENARIO",
        ["SCENARIO 1", "SCENARIO 2", "SHOEBOX 5x4x3"],
        key="scenario"
    )

# Get scenario key for panels
scenario_key = "Empty Room"
if "SCENARIO 1" in scenario:
    scenario_key = "Scenario 1"
    scenario_folder = "scenario_1"
    corners_x, corners_y = ROOM_CORNERS_X, ROOM_CORNERS_Y
elif "SCENARIO 2" in scenario:
    scenario_key = "Scenario 2"
    scenario_folder = "scenario_2"
    corners_x, corners_y = ROOM_CORNERS_X, ROOM_CORNERS_Y
else:
    scenario_key = "Shoebox"
    scenario_folder = "shoebox"
    corners_x, corners_y = SHOEBOX_CORNERS_X, SHOEBOX_CORNERS_Y

if "SHOEBOX" in scenario: 
    active_sources = SOURCES_SHOEBOX
    active_receivers = RECEIVERS_SHOEBOX
else: 
    active_sources = SOURCES
    active_receivers = RECEIVERS

with col_ctrl2:
    source = st.selectbox(
        "SOUND SOURCE",
        list(active_sources.keys()),
        format_func=lambda x: f"{x} — {active_sources[x]['label']}",
        key="source"
    )

with col_ctrl3:
    valid_pairs = VALID_PAIRS_SHOEBOX if "SHOEBOX" in scenario else VALID_PAIRS_PENTAGON 
    valid_receivers = valid_pairs[source]
    selected_receiver = st.selectbox(
        "RECEIVER POSITION",
        list(valid_receivers),
        format_func=lambda x: f"{x} — {active_receivers[x]['label']}",
        key="receiver"
    )

st.markdown("---")

# ════════════════════════════════
# MAIN LAYOUT — Map + Audio
# ════════════════════════════════
col_map, col_audio = st.columns([1.2, 1])

# ── LEFT: Interactive Room Map ──
with col_map:
    st.markdown("ROOM LAYOUT")
    
    fig = go.Figure()

    # ── Room outline ──
    fig.add_trace(go.Scatter(
        x=corners_x,
        y=corners_y,
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
            line=dict(color='limegreen', width=4),
            name='Acoustic Panel' if i == 0 else None,
            showlegend=(i == 0),
            hoverinfo='name',
            hovertemplate='Acoustic Panel<extra></extra>'
        ))

    # ── Sources ──
    for src_name, src_data in active_sources.items():
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
    for rec_name, rec_data in active_receivers.items():
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
    src_pos = active_sources[source]["pos"]
    rec_pos = active_receivers[selected_receiver]["pos"]
    fig.add_trace(go.Scatter(
        x=[src_pos[0], rec_pos[0]],
        y=[src_pos[1], rec_pos[1]],
        mode='lines',
        line=dict(color='#FF9800', width=2, dash='dot'),
        name='SOURCE → RECEIVER',
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
            range=[-0.3, max(corners_x)+1],
            scaleanchor="y",
            title="X (m)",
            showgrid=True,
            gridcolor='#f0f0f0'
        ),
        yaxis=dict(
            range=[-0.3, max(corners_y)+1],
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
        <b>SELECTED:</b> SOURCE <b>{source}</b> → 
        RECEIVER <b>{selected_receiver}</b><br>
        <b>DISTANCE:</b> {dist:.3f}m  | 
        <b>DIRECT SOUND ARRIVAL:</b> {td:.2f}ms
    </div>
    """, unsafe_allow_html=True)

# ── RIGHT: Audio Players ──
with col_audio:
    st.markdown("LISTEN TO ROOM ACOUSTICS")
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 1rem;">
        <span class="selected-badge">
            {source} → {selected_receiver} | {scenario.split('—')[0].strip()}
        </span>
    </div>
    """, unsafe_allow_html=True)

    # Audio models to display
    audio_models = [
        ("RAVEN",  "raven",  "#000000"),
        ("HYBRID",     "hybrid", "#000000"),
    ]

    for label, model, colour in audio_models:
        audio_path = get_audio_path(
            scenario_folder, source, selected_receiver, model
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
                 Audio not yet available for this position
            </p>
            """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

# ════════════════════════════════
# BOTTOM — Quick Stats
# ════════════════════════════════
st.markdown("---")
st.markdown("Quick Statistics")

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("SOURCE",    source)
col2.metric("RECEIVER",  selected_receiver)
col3.metric("DISTANCE",  f"{dist:.2f}m")
col4.metric("DIRECT SOUND ARRIVAL", f"{td:.2f}ms")
col5.metric("SCENARIO",  scenario.split("—")[0].strip())