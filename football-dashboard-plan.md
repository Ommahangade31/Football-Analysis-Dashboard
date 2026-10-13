# Football Player Performance Analytics Dashboard — Implementation Plan

## Top-Level Overview

Build a self-contained, portfolio-quality football analytics dashboard using Python, Streamlit, Pandas, NumPy, and Plotly.
The app loads a synthetic dataset (`football_players.csv`), calculates all KPIs at runtime, and renders four interactive pages
accessible through a sidebar navigation. The UI follows a dark, football-inspired green-pitch theme. All charts, filters, and
tables update reactively to sidebar selections. No external APIs or real-world data are required.

**Scope:**
- 4 deliverable files: `app.py`, `football_players.csv`, `requirements.txt`, `README.md`
- 5 pages/views: Overview, Player Analysis, Team Analysis, Position Analysis (inline within app.py, clearly separated by functions)
- Sidebar: season, team, position, and player filters
- CSV export button on every data view

**Non-goals:**
- No database, authentication, or backend server
- No real-world scraping or external API calls
- No multi-file module structure (keep it beginner-friendly, single `app.py`)

---

## Dataset Schema

File: `football_players.csv`
Generated once by a standalone script section at the top of `app.py` (runs only if the file is absent).
Marked with a banner: **"⚠️ Synthetic Data — Not Real-World Statistics"**

| Column | Type | Description |
|---|---|---|
| player_id | int | Unique player identifier (1–N) |
| name | str | Generated first + last name |
| team | str | One of 10 fictional club names |
| position | str | GK / DEF / MID / FWD |
| season | str | One of: 2021-22, 2022-23, 2023-24 |
| age | int | 18–38 |
| appearances | int | 1–38 |
| minutes_played | int | appearances × ~75 (±noise) |
| goals | int | Position-scaled random integer |
| assists | int | Position-scaled random integer |
| shots | int | goals-correlated random integer |
| shots_on_target | int | ≤ shots |
| passes | int | 200–2500 (position-scaled) |
| pass_accuracy | float | 60–95 % |
| key_passes | int | 0–120 |
| tackles | int | Position-scaled |
| interceptions | int | Position-scaled |
| clean_sheets | int | GK/DEF only, else 0 |
| yellow_cards | int | 0–10 |
| red_cards | int | 0–3 |
| rating | float | 5.0–9.5 (weighted composite) |

**Reproducibility:** `np.random.seed(42)` — same file every run.
**Size:** 100 players × 3 seasons = 300 rows minimum (each player appears once per season with varied stats).

---

## KPI Calculations (all derived at runtime from filtered DataFrame)

| KPI Card | Formula |
|---|---|
| Total Players | `df['player_id'].nunique()` |
| Total Goals | `df['goals'].sum()` |
| Total Assists | `df['assists'].sum()` |
| Total Minutes Played | `df['minutes_played'].sum()` |
| Average Player Rating | `df['rating'].mean()` rounded to 2 dp |

Rankings (used in Player Analysis page):
- Top Scorer: player with max `goals`
- Top Assister: player with max `assists`
- Best Passer: player with max `pass_accuracy`
- Best Rating: player with max `rating`

---

## Project File Structure

```
football-analysis-dashboard/
├── app.py                  # Single-file Streamlit application
├── football_players.csv    # Synthetic dataset (auto-generated on first run)
├── requirements.txt        # Pinned dependencies
└── README.md               # Setup, run, and deploy instructions
```

---

## Sub-Tasks

---

### Sub-Task 1 — Generate Synthetic Dataset (`football_players.csv`)

**Status:** [ ] pending

**Intent**
Create a reproducible, position-realistic synthetic dataset that can be regenerated at any time without external dependencies.
The generator lives inside `app.py` as a `generate_data()` function called at startup if the CSV is missing.

**Expected Outcomes**
- `football_players.csv` exists in the project root after first run
- Contains 300+ rows (100 players × 3 seasons) with all columns defined in the schema above
- Stats are position-realistic (GKs have 0 goals, FWDs have high shot counts, etc.)
- A visible synthetic-data disclaimer banner is shown in the app

**Todo List**
1. Write `generate_data()` function using `np.random.seed(42)`
2. Define 10 team names and assign ~10 players each
3. Define position distribution: 10 GK, 30 DEF, 40 MID, 20 FWD per season
4. Scale goal/assist/shot/tackle/pass ranges per position using a lookup dict
5. Compute `rating` as a weighted sum of normalised goals, assists, pass_accuracy, and tackles (clipped to 5.0–9.5)
6. Write to `football_players.csv` with `index=False`
7. Add `@st.cache_data` decorator to `load_data()` function that reads the CSV

**Relevant Context**
- NumPy random functions: `np.random.randint`, `np.random.uniform`, `np.random.choice`
- Pandas: `pd.DataFrame`, `df.to_csv`
- Streamlit: `st.cache_data` for caching

---

### Sub-Task 2 — App Skeleton, Theme & Sidebar Filters

**Status:** [ ] pending

**Intent**
Set up the Streamlit app shell: page config, custom CSS for the dark green theme, sidebar navigation, and all sidebar filter widgets.
This establishes the frame that every subsequent page plugs into.

**Expected Outcomes**
- App launches with `streamlit run app.py` and shows a sidebar
- Dark background (#0e1117), green accents (#00ff88 / #1a472a), white text
- Sidebar contains: Page selector, Season multiselect, Team multiselect, Position multiselect, Player multiselect
- Filters produce a `filtered_df` passed to every page renderer
- Empty-filter guard: if `filtered_df` is empty, show `st.warning` and stop

**Todo List**
1. Call `st.set_page_config(layout="wide", page_title="⚽ Football Analytics", page_icon="⚽")`
2. Inject custom CSS via `st.markdown` with `unsafe_allow_html=True` — style KPI cards, headings, sidebar
3. Build `get_sidebar_filters(df)` function returning `filtered_df`
4. Implement cascading filter logic (team list updates based on season selection, etc.)
5. Add page navigation radio/selectbox: Overview | Player Analysis | Team Analysis | Position Analysis
6. Add synthetic-data disclaimer banner using `st.info` or styled `st.markdown`

**Relevant Context**
- Streamlit docs: `st.set_page_config`, `st.sidebar`, `st.multiselect`
- CSS target: `.stApp` background, `.metric` card styling, sidebar background colour

---

### Sub-Task 3 — Overview Page (KPI Cards + Summary Charts)

**Status:** [ ] pending

**Intent**
Build the landing page that gives an at-a-glance dashboard with five KPI metric cards and two summary charts.

**Expected Outcomes**
- Five KPI cards in a single `st.columns(5)` row: Total Players, Total Goals, Total Assists, Total Minutes, Avg Rating
- Bar chart: Top 10 scorers (horizontal, coloured by position)
- Bar chart: Top 10 assisters (horizontal)
- All values calculated dynamically from `filtered_df`

**Todo List**
1. Write `render_overview(filtered_df)` function
2. Use `st.columns(5)` + `st.metric()` for KPI cards
3. Build top-10 scorer chart with `px.bar(..., orientation='h', color='position')`
4. Build top-10 assister chart similarly
5. Style charts with `template='plotly_dark'`, green colour scale, transparent background
6. Add `st.caption` under each chart explaining what it shows

**Relevant Context**
- `st.metric(label, value, delta)` supports delta arrows — use delta vs. season mean
- Plotly: `fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')`

---

### Sub-Task 4 — Player Analysis Page

**Status:** [ ] pending

**Intent**
Enable per-player deep-dive with a comparison table, scatter plots, and a radar/stats breakdown.

**Expected Outcomes**
- Player selector (up to 5 players) for side-by-side stat comparison table
- Scatter plot: Goals vs Assists (colour = position, size = minutes_played, hover = player name + team)
- Scatter plot: Shots vs Goals (colour = position, trendline via `px.scatter(..., trendline='ols')`)
- Searchable, sortable full statistics table using `st.dataframe` with column config
- CSV download button for filtered data

**Todo List**
1. Write `render_player_analysis(filtered_df)` function
2. Build player multiselect (default: top 5 by rating) and render comparison `st.dataframe`
3. Build Goals vs Assists scatter with `px.scatter`, hover_data including name and team
4. Build Shots vs Goals scatter with OLS trendline
5. Render full stats table via `st.dataframe(filtered_df, use_container_width=True)`
6. Add `st.download_button` that converts `filtered_df` to CSV bytes via `df.to_csv(index=False).encode('utf-8')`

**Relevant Context**
- `px.scatter` trendline requires `statsmodels` — add to `requirements.txt`
- `st.dataframe` column_config: `st.column_config.NumberColumn` for formatted stat columns
- Download button: `mime='text/csv'`

---

### Sub-Task 5 — Team Analysis Page

**Status:** [ ] pending

**Intent**
Aggregate player statistics to team level and display grouped bar charts and a team league table.

**Expected Outcomes**
- Grouped bar chart: Total Goals and Assists per team (two bars per team)
- Bar chart: Player count per team (to show squad size)
- Team league table: team, total goals, total assists, total players, avg rating — sortable
- All aggregations computed with `groupby('team').agg(...)`

**Todo List**
1. Write `render_team_analysis(filtered_df)` function
2. Compute `team_df = filtered_df.groupby('team').agg(goals=('goals','sum'), assists=('assists','sum'), players=('player_id','nunique'), avg_rating=('rating','mean')).reset_index()`
3. Build grouped bar chart for goals + assists using `px.bar(..., barmode='group')`
4. Build player count bar chart
5. Display sortable team table with `st.dataframe`
6. Add download button for `team_df`

**Relevant Context**
- `pd.DataFrame.groupby` with named aggregation syntax `agg(col=(src_col, func))`
- Plotly grouped bar: pass melted DataFrame or use `go.Bar` traces

---

### Sub-Task 6 — Position Analysis Page

**Status:** [ ] pending

**Intent**
Compare performance metrics across the four positions (GK, DEF, MID, FWD) using aggregated charts and a violin/box plot.

**Expected Outcomes**
- KPI breakdown cards per position (avg goals, avg assists, avg rating)
- Box plot: Rating distribution by position (using `px.box`)
- Bar chart: Average goals per position
- Bar chart: Average tackles and interceptions per position (defensive metrics)
- Radar chart comparing average stats across all four positions (using `go.Scatterpolar`)

**Todo List**
1. Write `render_position_analysis(filtered_df)` function
2. Compute `pos_df = filtered_df.groupby('position').mean(numeric_only=True).reset_index()`
3. Build box plot with `px.box(filtered_df, x='position', y='rating', color='position')`
4. Build average goals and avg tackles bar charts
5. Build radar chart with `go.Scatterpolar` — one trace per position, categories = [goals, assists, passes, tackles, rating]
6. Normalise radar values to 0–1 range per metric before plotting

**Relevant Context**
- `go.Scatterpolar` requires `r` (values) and `theta` (category labels), `fill='toself'`
- Normalise: `(val - min) / (max - min)` per column before radar plot

---

### Sub-Task 7 — `requirements.txt` and `README.md`

**Status:** [ ] pending

**Intent**
Provide all dependency and setup information needed to run or deploy the app.

**Expected Outcomes**
- `requirements.txt` contains exact package list with minimum version pins
- `README.md` covers: project description, features list, local setup steps, deploy to Streamlit Cloud steps, dataset disclaimer, screenshot placeholder

**Todo List**
1. Write `requirements.txt`:
   - `streamlit>=1.32.0`
   - `pandas>=2.0.0`
   - `numpy>=1.26.0`
   - `plotly>=5.20.0`
   - `statsmodels>=0.14.0`
2. Write `README.md` with sections: About, Features, Installation, Running Locally, Deploying to Streamlit Cloud, Data Disclaimer
3. Include `pip install -r requirements.txt` and `streamlit run app.py` commands
4. Add Streamlit Cloud deploy badge/link template

**Relevant Context**
- Streamlit Cloud free tier supports public GitHub repos: `https://share.streamlit.io`
- `statsmodels` is needed for OLS trendlines in `px.scatter`

---

## Architecture Diagram (described in text)

```
app.py
│
├── generate_data()          → writes football_players.csv (once)
├── load_data()              → reads CSV, returns DataFrame (cached)
├── get_sidebar_filters(df)  → returns filtered_df
│
├── render_overview(filtered_df)
├── render_player_analysis(filtered_df)
├── render_team_analysis(filtered_df)
├── render_position_analysis(filtered_df)
│
└── main()
    ├── load_data()
    ├── get_sidebar_filters(df)
    └── route to render_* based on page selection
```

---

## UI Theme Specification

| Element | Value |
|---|---|
| App background | `#0e1117` |
| Sidebar background | `#1a1a2e` |
| Primary accent | `#00ff88` (bright green) |
| Secondary accent | `#1a472a` (dark pitch green) |
| Card background | `#16213e` |
| Text colour | `#ffffff` |
| Chart template | `plotly_dark` |
| Chart bg | `rgba(0,0,0,0)` (transparent) |

---

## Input Validation & Error Handling

| Scenario | Handling |
|---|---|
| CSV missing on startup | `generate_data()` auto-creates it |
| Filters produce empty DataFrame | `st.warning("No players match the selected filters.")` + `st.stop()` |
| Player multiselect has no selection | Default to top 5 by rating |
| Single-position filter on radar | Show `st.info("Select at least 2 positions for radar chart")` |
| Numeric columns with NaN | `df.fillna(0)` after load |
