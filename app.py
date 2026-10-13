import os
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------------------------
# Page config — MUST be the very first Streamlit call
# ---------------------------------------------------------------------------

st.set_page_config(
    layout="wide",
    page_title="⚽ Football Analytics Dashboard",
    page_icon="⚽",
)

# ---------------------------------------------------------------------------
# Custom CSS — dark green pitch theme
# ---------------------------------------------------------------------------

st.markdown(
    """
    <style>
    /* ── App background ── */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* ── Sidebar background ── */
    [data-testid="stSidebar"] {
        background-color: #1a1a2e;
    }
    [data-testid="stSidebar"] * {
        color: #ffffff;
    }

    /* ── Headings ── */
    h1, h2, h3 {
        color: #00ff88 !important;
    }

    /* ── KPI / metric cards ── */
    [data-testid="stMetric"] {
        background-color: #16213e;
        border-radius: 8px;
        padding: 12px 16px;
        border-left: 4px solid #00ff88;
    }
    [data-testid="stMetricLabel"] {
        color: #a0aec0 !important;
    }
    [data-testid="stMetricValue"] {
        color: #ffffff !important;
    }

    /* ── Divider ── */
    hr {
        border-color: #1a472a;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Synthetic Data Generation
# ---------------------------------------------------------------------------

_TEAMS = [
    "Ironclad FC",
    "Volta United",
    "Silverpeak City",
    "Harbour Wolves",
    "Redstone Athletic",
    "Crestfall FC",
    "Northern Blaze",
    "Cobalt Rangers",
    "Stormway SC",
    "Phoenix Wanderers",
]

_SEASONS = ["2021-22", "2022-23", "2023-24"]

# Position distribution: 10 GK, 30 DEF, 40 MID, 20 FWD = 100 players
_POSITIONS = (
    ["GK"] * 10
    + ["DEF"] * 30
    + ["MID"] * 40
    + ["FWD"] * 20
)

# Per-position stat ranges (min, max)
_STAT_RANGES = {
    #              goals  assists  shots  tackles  interceptions  clean_sheets  passes   pass_acc  key_passes
    "GK":  dict(goals=(0, 0),   assists=(0, 2),   shots=(0, 1),   tackles=(5, 30),   interceptions=(5, 25),  clean_sheets=(0, 20), passes=(400, 900),  pass_accuracy=(55, 80), key_passes=(0, 10)),
    "DEF": dict(goals=(0, 5),   assists=(0, 8),   shots=(2, 20),  tackles=(30, 120), interceptions=(20, 80), clean_sheets=(0, 15), passes=(600, 1800), pass_accuracy=(65, 88), key_passes=(0, 30)),
    "MID": dict(goals=(1, 15),  assists=(2, 18),  shots=(10, 80), tackles=(15, 80),  interceptions=(10, 50), clean_sheets=(0, 0),  passes=(800, 2500), pass_accuracy=(70, 92), key_passes=(10, 100)),
    "FWD": dict(goals=(3, 30),  assists=(1, 15),  shots=(20, 150),tackles=(2, 30),   interceptions=(2, 20),  clean_sheets=(0, 0),  passes=(200, 900),  pass_accuracy=(60, 85), key_passes=(5, 80)),
}

_FIRST_NAMES = [
    "Luca", "Marco", "Carlos", "James", "Ali", "Yusuf", "Diego", "Ivan",
    "Kai", "Leon", "Rafael", "Emre", "Omar", "Finn", "Hugo", "Theo",
    "Noel", "Soren", "Tomas", "Arjan", "Bruno", "Cesc", "David", "Emil",
    "Felix", "Gael", "Henri", "Igor", "Javier", "Kemal", "Luis", "Mateo",
    "Niko", "Oscar", "Pedro", "Quentin", "Rik", "Stefan", "Tiago", "Umar",
    "Vito", "Wael", "Xavi", "Yannis", "Zach", "Abel", "Bart", "Cole",
    "Dani", "Erik",
]
_LAST_NAMES = [
    "Silva", "Rossi", "Muller", "Torres", "Hassan", "Yilmaz", "Gomez",
    "Petrov", "Werner", "Blanc", "Ferreira", "Cruz", "Diallo", "Berg",
    "Matos", "Ramos", "Klein", "Nkosi", "Sousa", "Tanaka", "Vasquez",
    "Wolf", "Xu", "Yamamoto", "Zahra", "Adesanya", "Becker", "Conte",
    "Diaz", "Einarsson", "Fonseca", "Giggs", "Huth", "Ibarra", "Janssen",
    "Kovac", "Lund", "Mane", "Neves", "Olsen", "Pinto", "Quinn",
    "Reyna", "Santos", "Tadic", "Ulloa", "Vieira", "Walsh", "Xhaka", "Zola",
]


def generate_data() -> None:
    """Generate football_players.csv with 300 rows (100 players × 3 seasons)."""
    np.random.seed(42)

    n_players = 100
    positions = _POSITIONS[:]  # already 100 entries

    # Assign each player a fixed name, team, and base age
    player_ids = list(range(1, n_players + 1))
    first = np.random.choice(_FIRST_NAMES, size=n_players, replace=True)
    last = np.random.choice(_LAST_NAMES, size=n_players, replace=True)
    names = [f"{f} {l}" for f, l in zip(first, last)]
    teams = np.random.choice(_TEAMS, size=n_players, replace=True)
    base_ages = np.random.randint(18, 36, size=n_players)

    rows = []
    for season_idx, season in enumerate(_SEASONS):
        for i in range(n_players):
            pos = positions[i]
            r = _STAT_RANGES[pos]
            appearances = int(np.random.randint(5, 38))
            minutes_played = int(appearances * np.random.randint(60, 95))
            goals = int(np.random.randint(r["goals"][0], r["goals"][1] + 1))
            assists = int(np.random.randint(r["assists"][0], r["assists"][1] + 1))
            shots = int(np.random.randint(max(goals, r["shots"][0]), r["shots"][1] + 1))
            shots_on_target = int(np.random.randint(goals, shots + 1))
            passes = int(np.random.randint(r["passes"][0], r["passes"][1] + 1))
            pass_accuracy = round(float(np.random.uniform(r["pass_accuracy"][0], r["pass_accuracy"][1])), 1)
            key_passes = int(np.random.randint(r["key_passes"][0], r["key_passes"][1] + 1))
            tackles = int(np.random.randint(r["tackles"][0], r["tackles"][1] + 1))
            interceptions = int(np.random.randint(r["interceptions"][0], r["interceptions"][1] + 1))
            clean_sheets = int(np.random.randint(r["clean_sheets"][0], r["clean_sheets"][1] + 1))
            yellow_cards = int(np.random.randint(0, 11))
            red_cards = int(np.random.randint(0, 4))

            rows.append({
                "player_id": player_ids[i],
                "name": names[i],
                "team": teams[i],
                "position": pos,
                "season": season,
                "age": int(base_ages[i]) + season_idx,
                "appearances": appearances,
                "minutes_played": minutes_played,
                "goals": goals,
                "assists": assists,
                "shots": shots,
                "shots_on_target": shots_on_target,
                "passes": passes,
                "pass_accuracy": pass_accuracy,
                "key_passes": key_passes,
                "tackles": tackles,
                "interceptions": interceptions,
                "clean_sheets": clean_sheets,
                "yellow_cards": yellow_cards,
                "red_cards": red_cards,
                "rating": 0.0,  # placeholder; computed below
            })

    df = pd.DataFrame(rows)

    # ------------------------------------------------------------------
    # Compute rating: weighted composite of normalised goals, assists,
    # pass_accuracy, and tackles — clipped to [5.0, 9.5].
    # ------------------------------------------------------------------
    def _norm(series: pd.Series) -> pd.Series:
        lo, hi = series.min(), series.max()
        if hi == lo:
            return pd.Series(0.5, index=series.index)
        return (series - lo) / (hi - lo)

    rating_raw = (
        0.35 * _norm(df["goals"])
        + 0.20 * _norm(df["assists"])
        + 0.25 * _norm(df["pass_accuracy"])
        + 0.20 * _norm(df["tackles"])
    )
    # Scale from [0,1] to [5.0, 9.5]
    df["rating"] = (rating_raw * 4.5 + 5.0).clip(5.0, 9.5).round(2)

    df.to_csv("football_players.csv", index=False)
    print(f"Generated football_players.csv — {len(df)} rows, {len(df.columns)} columns.")


# ---------------------------------------------------------------------------
# Data Loading
# ---------------------------------------------------------------------------

@st.cache_data
def load_data() -> pd.DataFrame:
    """Load football_players.csv, generating it first if absent. Returns cleaned DataFrame."""
    if not os.path.exists("football_players.csv"):
        generate_data()
    df = pd.read_csv("football_players.csv")
    df = df.fillna(0)
    return df


# ---------------------------------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------------------------------

def get_sidebar_filters(df: pd.DataFrame):
    """
    Render sidebar filter widgets and return a filtered DataFrame.
    Returns None if the filtered DataFrame is empty.
    """
    st.sidebar.markdown("## 🔍 Filters")

    # ── Season ──────────────────────────────────────────────────────────────
    all_seasons = sorted(df["season"].unique().tolist())
    selected_seasons = st.sidebar.multiselect(
        "Season",
        options=all_seasons,
        default=all_seasons,
    )
    if not selected_seasons:
        selected_seasons = all_seasons

    season_df = df[df["season"].isin(selected_seasons)]

    # ── Team (narrows based on selected seasons) ─────────────────────────────
    all_teams = sorted(season_df["team"].unique().tolist())
    selected_teams = st.sidebar.multiselect(
        "Team",
        options=all_teams,
        default=all_teams,
    )
    if not selected_teams:
        selected_teams = all_teams

    # ── Position ─────────────────────────────────────────────────────────────
    position_order = ["GK", "DEF", "MID", "FWD"]
    selected_positions = st.sidebar.multiselect(
        "Position",
        options=position_order,
        default=position_order,
    )
    if not selected_positions:
        selected_positions = position_order

    # ── Player (narrows based on team + position) ─────────────────────────────
    candidate_df = season_df[
        season_df["team"].isin(selected_teams)
        & season_df["position"].isin(selected_positions)
    ]
    all_players = sorted(candidate_df["name"].unique().tolist())
    selected_players = st.sidebar.multiselect(
        "Player",
        options=all_players,
        default=all_players,
    )
    if not selected_players:
        selected_players = all_players

    # ── Apply all filters ─────────────────────────────────────────────────────
    filtered_df = df[
        df["season"].isin(selected_seasons)
        & df["team"].isin(selected_teams)
        & df["position"].isin(selected_positions)
        & df["name"].isin(selected_players)
    ]

    if filtered_df.empty:
        st.sidebar.warning("No players match the selected filters.")
        return None

    return filtered_df


# ---------------------------------------------------------------------------
# Page Navigation
# ---------------------------------------------------------------------------

_PAGES = [
    "📊 Overview",
    "👤 Player Analysis",
    "🏟️ Team Analysis",
    "📐 Position Analysis",
]


def get_page_selection() -> str:
    st.sidebar.markdown("---")
    st.sidebar.markdown("## 📂 Navigation")
    return st.sidebar.radio("Go to", _PAGES, label_visibility="collapsed")


# ---------------------------------------------------------------------------
# Page render stubs (filled in subsequent sub-tasks)
# ---------------------------------------------------------------------------

def render_overview(filtered_df: pd.DataFrame) -> None:
    st.title("📊 Overview")

    n_players = filtered_df["player_id"].nunique()
    n_seasons = filtered_df["season"].nunique()
    st.caption(
        f"Showing **{n_players} players** across **{n_seasons} season(s)** "
        f"based on the current sidebar filters."
    )

    st.markdown("---")

    # ── KPI cards ────────────────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Players", n_players)
    c2.metric("Total Goals", int(filtered_df["goals"].sum()))
    c3.metric("Total Assists", int(filtered_df["assists"].sum()))
    c4.metric(
        "Total Minutes Played",
        f"{int(filtered_df['minutes_played'].sum()):,}",
    )
    c5.metric(
        "Avg Rating",
        f"{filtered_df['rating'].mean():.2f}",
    )

    st.markdown("---")

    # ── Helper: shared dark-theme layout update ───────────────────────────────
    def _dark_layout(fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            template="plotly_dark",
        )
        return fig

    # ── Top 10 Scorers ────────────────────────────────────────────────────────
    top_scorers = (
        filtered_df.groupby("name")["goals"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    fig_scorers = px.bar(
        top_scorers,
        x="goals",
        y="name",
        orientation="h",
        color="goals",
        color_continuous_scale="Greens",
        title="Top 10 Scorers",
        labels={"goals": "Goals", "name": "Player"},
    )
    fig_scorers.update_yaxes(autorange="reversed")
    fig_scorers = _dark_layout(fig_scorers)

    # ── Top 10 Assisters ─────────────────────────────────────────────────────
    top_assisters = (
        filtered_df.groupby("name")["assists"]
        .sum()
        .nlargest(10)
        .reset_index()
    )
    fig_assisters = px.bar(
        top_assisters,
        x="assists",
        y="name",
        orientation="h",
        color="assists",
        color_continuous_scale="Blues",
        title="Top 10 Assisters",
        labels={"assists": "Assists", "name": "Player"},
    )
    fig_assisters.update_yaxes(autorange="reversed")
    fig_assisters = _dark_layout(fig_assisters)

    # ── Side-by-side layout ───────────────────────────────────────────────────
    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(fig_scorers, use_container_width=True)
        st.caption("Total goals scored per player across the selected seasons and filters.")
    with col_r:
        st.plotly_chart(fig_assisters, use_container_width=True)
        st.caption("Total assists provided per player across the selected seasons and filters.")

    # ── Goals + Assists combined (full width) ─────────────────────────────────
    combined = (
        filtered_df.groupby("name")[["goals", "assists"]]
        .sum()
        .assign(total=lambda d: d["goals"] + d["assists"])
        .nlargest(10, "total")
        .drop(columns="total")
        .reset_index()
        .melt(id_vars="name", var_name="metric", value_name="count")
    )
    fig_combined = px.bar(
        combined,
        x="name",
        y="count",
        color="metric",
        barmode="group",
        title="Top 10 Players by Goals + Assists Combined",
        labels={"name": "Player", "count": "Count", "metric": "Metric"},
        color_discrete_map={"goals": "#00ff88", "assists": "#3b82d4"},
    )
    fig_combined = _dark_layout(fig_combined)
    st.plotly_chart(fig_combined, use_container_width=True)
    st.caption(
        "Side-by-side comparison of goals and assists for the top 10 players "
        "ranked by their combined goal contributions."
    )


def render_player_analysis(filtered_df: pd.DataFrame) -> None:
    st.title("👤 Player Analysis")

    # ── Helper: shared dark-theme layout update ───────────────────────────────
    def _dark_layout(fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            template="plotly_dark",
        )
        return fig

    # ── Player comparison multiselect ─────────────────────────────────────────
    st.subheader("🔎 Player Comparison")

    all_player_names = sorted(filtered_df["name"].unique().tolist())
    top5_default = (
        filtered_df.groupby("name")["rating"]
        .mean()
        .nlargest(5)
        .index.tolist()
    )
    # Keep only defaults that are present in the current filtered set
    top5_default = [p for p in top5_default if p in all_player_names]

    selected_players = st.multiselect(
        "Select up to 5 players to compare",
        options=all_player_names,
        default=top5_default[:5],
        max_selections=5,
    )
    if not selected_players:
        selected_players = top5_default[:5]

    comparison_cols = [
        "name", "team", "position", "season", "appearances",
        "goals", "assists", "shots", "passes", "pass_accuracy",
        "tackles", "rating",
    ]
    comparison_df = filtered_df[filtered_df["name"].isin(selected_players)][comparison_cols]
    st.dataframe(comparison_df, use_container_width=True)

    st.markdown("---")

    # ── Scatter plots side-by-side ────────────────────────────────────────────
    fig_ga = px.scatter(
        filtered_df,
        x="assists",
        y="goals",
        color="position",
        size="minutes_played",
        hover_data=["name", "team", "season"],
        title="Goals vs Assists",
    )
    fig_ga = _dark_layout(fig_ga)

    fig_sg = px.scatter(
        filtered_df,
        x="shots",
        y="goals",
        color="position",
        trendline="ols",
        hover_data=["name", "team"],
        title="Shots vs Goals (with OLS Trendline)",
    )
    fig_sg = _dark_layout(fig_sg)

    col_l, col_r = st.columns(2)
    with col_l:
        st.plotly_chart(fig_ga, use_container_width=True)
        st.caption("Bubble size represents minutes played. Colour represents player position.")
    with col_r:
        st.plotly_chart(fig_sg, use_container_width=True)
        st.caption("OLS trendline shows the linear relationship between shots taken and goals scored.")

    st.markdown("---")

    # ── Full statistics table ─────────────────────────────────────────────────
    st.subheader("📋 Full Player Statistics")

    st.dataframe(
        filtered_df,
        use_container_width=True,
        column_config={
            "player_id":       st.column_config.NumberColumn("ID",            format="%d"),
            "age":             st.column_config.NumberColumn("Age",           format="%d"),
            "appearances":     st.column_config.NumberColumn("Apps",          format="%d"),
            "minutes_played":  st.column_config.NumberColumn("Minutes",       format="%d"),
            "goals":           st.column_config.NumberColumn("Goals",         format="%d"),
            "assists":         st.column_config.NumberColumn("Assists",       format="%d"),
            "shots":           st.column_config.NumberColumn("Shots",         format="%d"),
            "shots_on_target": st.column_config.NumberColumn("SoT",           format="%d"),
            "passes":          st.column_config.NumberColumn("Passes",        format="%d"),
            "pass_accuracy":   st.column_config.NumberColumn("Pass Acc %",    format="%.1f"),
            "key_passes":      st.column_config.NumberColumn("Key Passes",    format="%d"),
            "tackles":         st.column_config.NumberColumn("Tackles",       format="%d"),
            "interceptions":   st.column_config.NumberColumn("Interceptions", format="%d"),
            "clean_sheets":    st.column_config.NumberColumn("Clean Sheets",  format="%d"),
            "yellow_cards":    st.column_config.NumberColumn("Yellow Cards",  format="%d"),
            "red_cards":       st.column_config.NumberColumn("Red Cards",     format="%d"),
            "rating":          st.column_config.NumberColumn("Rating",        format="%.2f"),
        },
    )

    # ── CSV download ──────────────────────────────────────────────────────────
    st.download_button(
        label="⬇️ Download Filtered Data as CSV",
        data=filtered_df.to_csv(index=False).encode("utf-8"),
        file_name="football_players_filtered.csv",
        mime="text/csv",
    )


def render_team_analysis(filtered_df: pd.DataFrame) -> None:
    st.title("🏟️ Team Analysis")

    # ── Helper: shared dark-theme layout update ───────────────────────────────
    def _dark_layout(fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            template="plotly_dark",
        )
        return fig

    # ── Aggregate team stats ──────────────────────────────────────────────────
    team_df = (
        filtered_df.groupby('team')
        .agg(
            goals=('goals', 'sum'),
            assists=('assists', 'sum'),
            players=('player_id', 'nunique'),
            avg_rating=('rating', 'mean'),
            total_minutes=('minutes_played', 'sum'),
        )
        .reset_index()
    )
    team_df['avg_rating'] = team_df['avg_rating'].round(2)

    # ── Grouped bar chart: Goals & Assists per team (full width) ──────────────
    ga_long = team_df.melt(
        id_vars='team',
        value_vars=['goals', 'assists'],
        var_name='variable',
        value_name='value',
    )
    fig_ga = px.bar(
        ga_long,
        x='team',
        y='value',
        color='variable',
        barmode='group',
        title='Goals & Assists per Team',
        labels={'team': 'Team', 'value': 'Count', 'variable': 'Metric'},
        color_discrete_map={'goals': '#00ff88', 'assists': '#3b82d4'},
    )
    fig_ga = _dark_layout(fig_ga)
    st.plotly_chart(fig_ga, use_container_width=True)

    # ── Squad size + avg rating side-by-side ──────────────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        fig_squad = px.bar(
            team_df,
            x='team',
            y='players',
            color='players',
            color_continuous_scale='Greens',
            title='Squad Size per Team',
            labels={'team': 'Team', 'players': 'Players'},
        )
        fig_squad = _dark_layout(fig_squad)
        st.plotly_chart(fig_squad, use_container_width=True)

    with col_r:
        fig_rating = px.bar(
            team_df,
            x='team',
            y='avg_rating',
            color='avg_rating',
            color_continuous_scale='RdYlGn',
            title='Average Player Rating per Team',
            labels={'team': 'Team', 'avg_rating': 'Avg Rating'},
        )
        fig_rating = _dark_layout(fig_rating)
        st.plotly_chart(fig_rating, use_container_width=True)

    # ── Team league table ─────────────────────────────────────────────────────
    st.subheader("📋 Team Summary Table")
    st.dataframe(
        team_df.sort_values('goals', ascending=False),
        use_container_width=True,
    )

    # ── CSV download ──────────────────────────────────────────────────────────
    st.download_button(
        label="⬇️ Download Team Stats as CSV",
        data=team_df.to_csv(index=False).encode('utf-8'),
        file_name="team_stats.csv",
        mime="text/csv",
    )


def render_position_analysis(filtered_df: pd.DataFrame) -> None:
    st.title("📐 Position Analysis")

    # ── Constants ────────────────────────────────────────────────────────────
    POS_COLORS = {
        "GK":  "#f59e0b",
        "DEF": "#3b82f6",
        "MID": "#10b981",
        "FWD": "#ef4444",
    }
    POS_ORDER = ["GK", "DEF", "MID", "FWD"]

    # ── Helper: shared dark-theme layout ─────────────────────────────────────
    def _dark_layout(fig):
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            template="plotly_dark",
        )
        return fig

    # ── KPI cards: one column per position ───────────────────────────────────
    st.subheader("📊 Position Averages")
    kpi_cols = st.columns(4)
    for col_widget, pos in zip(kpi_cols, POS_ORDER):
        pos_data = filtered_df[filtered_df['position'] == pos]
        if pos_data.empty:
            avg_rating = avg_goals = avg_assists = 0.0
        else:
            avg_rating   = round(pos_data['rating'].mean(), 2)
            avg_goals    = round(pos_data['goals'].mean(), 2)
            avg_assists  = round(pos_data['assists'].mean(), 2)
        with col_widget:
            st.metric(f"{pos} Avg Rating",  avg_rating)
            st.metric(f"{pos} Avg Goals",   avg_goals)
            st.metric(f"{pos} Avg Assists", avg_assists)

    st.markdown("---")

    # ── Box plot: rating distribution by position (full width) ───────────────
    fig_box = px.box(
        filtered_df,
        x='position',
        y='rating',
        color='position',
        color_discrete_map=POS_COLORS,
        category_orders={'position': POS_ORDER},
        title='Rating Distribution by Position',
        labels={'position': 'Position', 'rating': 'Rating'},
    )
    fig_box = _dark_layout(fig_box)
    st.plotly_chart(fig_box, use_container_width=True)

    # ── Side-by-side: avg goals | avg defensive stats ─────────────────────────
    col_l, col_r = st.columns(2)

    with col_l:
        # Average goals per position
        goals_df = (
            filtered_df.groupby('position', as_index=False)['goals']
            .mean()
            .rename(columns={'goals': 'avg_goals'})
        )
        goals_df['avg_goals'] = goals_df['avg_goals'].round(2)
        fig_goals = px.bar(
            goals_df,
            x='position',
            y='avg_goals',
            color='position',
            color_discrete_map=POS_COLORS,
            category_orders={'position': POS_ORDER},
            title='Avg Goals by Position',
            labels={'position': 'Position', 'avg_goals': 'Avg Goals'},
        )
        fig_goals = _dark_layout(fig_goals)
        st.plotly_chart(fig_goals, use_container_width=True)

    with col_r:
        # Average tackles + interceptions per position
        def_df = (
            filtered_df.groupby('position', as_index=False)[['tackles', 'interceptions']]
            .mean()
            .round(2)
        )
        def_long = def_df.melt(
            id_vars='position',
            value_vars=['tackles', 'interceptions'],
            var_name='variable',
            value_name='value',
        )
        fig_def = px.bar(
            def_long,
            x='position',
            y='value',
            color='variable',
            barmode='group',
            category_orders={'position': POS_ORDER},
            title='Avg Defensive Stats by Position',
            labels={'position': 'Position', 'value': 'Average', 'variable': 'Metric'},
            color_discrete_map={'tackles': '#3b82d4', 'interceptions': '#10b981'},
        )
        fig_def = _dark_layout(fig_def)
        st.plotly_chart(fig_def, use_container_width=True)

    st.markdown("---")

    # ── Radar chart: all 4 positions (full width) ─────────────────────────────
    available_positions = filtered_df['position'].unique().tolist()
    if len(available_positions) < 2:
        st.info("Select at least 2 positions for the radar chart.")
    else:
        radar_cols = ['goals', 'assists', 'pass_accuracy', 'tackles', 'rating']
        theta_labels = ['Goals', 'Assists', 'Pass Acc', 'Tackles', 'Rating']

        pos_df = (
            filtered_df.groupby('position')[radar_cols]
            .mean()
        )

        # Normalise each column to [0, 1]
        pos_norm = pos_df.copy()
        for col in radar_cols:
            col_min = pos_df[col].min()
            col_max = pos_df[col].max()
            pos_norm[col] = (pos_df[col] - col_min) / (col_max - col_min)
        pos_norm = (
            pos_norm
            .replace([np.inf, -np.inf], 0)
            .fillna(0)
        )

        radar_fig = go.Figure()
        for pos in POS_ORDER:
            if pos not in pos_norm.index:
                continue
            values = pos_norm.loc[pos, radar_cols].tolist()
            # Close the polygon
            values_closed  = values + [values[0]]
            theta_closed   = theta_labels + [theta_labels[0]]
            radar_fig.add_trace(
                go.Scatterpolar(
                    r=values_closed,
                    theta=theta_closed,
                    fill='toself',
                    name=pos,
                    line_color=POS_COLORS.get(pos, '#ffffff'),
                    fillcolor=POS_COLORS.get(pos, '#ffffff'),
                    opacity=0.4,
                )
            )

        radar_fig.update_layout(
            title='Position Comparison — Normalised Stats Radar',
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#ffffff",
            template="plotly_dark",
            polar=dict(
                bgcolor="#0e1117",
                radialaxis=dict(visible=True, range=[0, 1]),
            ),
            legend=dict(font=dict(color="#ffffff")),
        )
        st.plotly_chart(radar_fig, use_container_width=True)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Synthetic data disclaimer
    st.markdown(
        """
        <div style="background-color:#1a472a;border-left:4px solid #00ff88;
                    padding:10px 16px;border-radius:6px;margin-bottom:16px;">
        ⚠️ <strong style="color:#00ff88;">Synthetic Data</strong>
        <span style="color:#ffffff;"> — All statistics are computer-generated for
        demonstration purposes only. Not real-world football results.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    df = load_data()

    # Page selection rendered before filters so nav sits at the top
    page = get_page_selection()

    filtered_df = get_sidebar_filters(df)

    if filtered_df is None or filtered_df.empty:
        st.warning("No players match the selected filters. Please adjust the sidebar filters.")
        st.stop()

    if page == "📊 Overview":
        render_overview(filtered_df)
    elif page == "👤 Player Analysis":
        render_player_analysis(filtered_df)
    elif page == "🏟️ Team Analysis":
        render_team_analysis(filtered_df)
    elif page == "📐 Position Analysis":
        render_position_analysis(filtered_df)


# ---------------------------------------------------------------------------
# Module-level entry point (Streamlit runs the module directly)
# ---------------------------------------------------------------------------

main()


# ---------------------------------------------------------------------------
# Script entry point for pre-generating the CSV
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    generate_data()
