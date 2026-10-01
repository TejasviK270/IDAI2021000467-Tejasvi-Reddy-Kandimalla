import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ------------------------------------------------------------------
# Page setup
# ------------------------------------------------------------------
st.set_page_config(
    page_title="Player Injuries & Team Performance Dashboard",
    page_icon="⚽",
    layout="wide",
)

DATA_FILE = "cleaned_player_injuries.csv"
MONTH_ORDER = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]


# ------------------------------------------------------------------
# Data loading (cached so the file is only read once)
# ------------------------------------------------------------------
@st.cache_data
def load_data(path):
    data = pd.read_csv(path, parse_dates=["injury_start", "injury_end"])
    return data


try:
    df = load_data(DATA_FILE)
except FileNotFoundError:
    st.error(f"Could not find '{DATA_FILE}'. Make sure it is in the same folder as app.py in your GitHub repository.")
    st.stop()


# ------------------------------------------------------------------
# Title
# ------------------------------------------------------------------
st.title("⚽ Player Injuries & Team Performance Dashboard")
st.markdown(
    "Built for **FootLens Analytics** to help technical directors and sports managers understand "
    "how player injuries affect team results, and how players perform after they recover.  \n"
    "**Performance drop index** = team's average goal difference *before* the injury minus its average "
    "goal difference *during* the player's absence. A **positive** value means the team did worse without the player."
)

# ------------------------------------------------------------------
# Sidebar filters
# ------------------------------------------------------------------
st.sidebar.header("Filters")

teams = sorted(df["team"].dropna().unique())
seasons = sorted(df["season"].dropna().unique())
injury_types = sorted(df["injury_type"].dropna().unique())

sel_teams = st.sidebar.multiselect("Club", teams, default=teams)
sel_seasons = st.sidebar.multiselect("Season", seasons, default=seasons)
sel_injuries = st.sidebar.multiselect("Injury type", injury_types, default=injury_types)

age_min, age_max = int(df["age"].min()), int(df["age"].max())
if age_min == age_max:
    sel_age = (age_min, age_max)
else:
    sel_age = st.sidebar.slider("Player age", age_min, age_max, (age_min, age_max))

filtered = df[
    df["team"].isin(sel_teams)
    & df["season"].isin(sel_seasons)
    & df["injury_type"].isin(sel_injuries)
    & df["age"].between(sel_age[0], sel_age[1])
]

if filtered.empty:
    st.warning("No data matches the selected filters. Please widen your selection in the sidebar.")
    st.stop()

st.sidebar.download_button(
    "Download filtered data (CSV)",
    filtered.to_csv(index=False).encode("utf-8"),
    file_name="filtered_player_injuries.csv",
    mime="text/csv",
)

# ------------------------------------------------------------------
# KPI row
# ------------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Injury cases", f"{len(filtered):,}")
c2.metric("Players injured", f"{filtered['player_name'].nunique():,}")
c3.metric("Avg. days out", f"{filtered['injury_duration_days'].mean():.0f}")
c4.metric("Avg. team drop index", f"{filtered['performance_drop_index'].mean():.2f}")
c5.metric("Avg. rating change", f"{filtered['rating_change'].mean():+.2f}")

st.divider()

# ------------------------------------------------------------------
# Visual 1: Bar chart - top 10 injuries with highest team performance drop
# ------------------------------------------------------------------
st.subheader("1. Top 10 injuries with the highest team performance drop")

min_cases = st.slider("Minimum number of cases per injury type", 1, 10, 1,
                      help="Hide rare injuries so one unusual case does not dominate the chart.")

injury_impact = (
    filtered.groupby("injury_type")
    .agg(avg_drop_index=("performance_drop_index", "mean"),
         cases=("player_name", "count"),
         avg_days_out=("injury_duration_days", "mean"))
    .reset_index()
)
injury_impact = injury_impact[injury_impact["cases"] >= min_cases]
top_injuries = injury_impact.sort_values("avg_drop_index", ascending=False).head(10)

if top_injuries.empty:
    st.info("No injury types meet the minimum number of cases. Lower the slider above.")
else:
    fig1 = px.bar(
        top_injuries.sort_values("avg_drop_index"),
        x="avg_drop_index", y="injury_type", orientation="h",
        color="avg_drop_index", color_continuous_scale="Reds",
        hover_data={"cases": True, "avg_days_out": ":.0f", "avg_drop_index": ":.2f"},
        labels={"avg_drop_index": "Avg. performance drop index", "injury_type": "Injury"},
    )
    fig1.update_layout(coloraxis_showscale=False, height=450)
    st.plotly_chart(fig1, width="stretch")

st.divider()

# ------------------------------------------------------------------
# Visual 2: Line chart - player performance timeline (before vs after injury)
# ------------------------------------------------------------------
st.subheader("2. Player performance timeline (before and after injury)")

players = sorted(filtered["player_name"].unique())
sel_player = st.selectbox("Choose a player", players)
player_cases = filtered[filtered["player_name"] == sel_player].sort_values("injury_start")

case_labels = [
    f"{row.injury_type} ({row.injury_start:%d %b %Y} to {row.injury_end:%d %b %Y})"
    for row in player_cases.itertuples()
]
sel_case = st.selectbox("Choose an injury case", case_labels)
case = player_cases.iloc[case_labels.index(sel_case)]

timeline_cols = [
    ("Before M1", "before_m1_rating"), ("Before M2", "before_m2_rating"), ("Before M3", "before_m3_rating"),
    ("After M1", "after_m1_rating"), ("After M2", "after_m2_rating"), ("After M3", "after_m3_rating"),
]
timeline = pd.DataFrame({
    "Match": [label for label, col in timeline_cols if col in case.index],
    "Rating": [case[col] for label, col in timeline_cols if col in case.index],
    "Phase": ["Before injury" if label.startswith("Before") else "After injury"
              for label, col in timeline_cols if col in case.index],
})

fig2 = px.line(timeline, x="Match", y="Rating", color="Phase", markers=True,
               color_discrete_map={"Before injury": "#1f77b4", "After injury": "#2ca02c"})
fig2.update_traces(connectgaps=False)
fig2.add_hline(y=case["avg_rating_before"], line_dash="dot", line_color="#1f77b4",
               annotation_text=f"Avg before: {case['avg_rating_before']:.2f}")
fig2.add_hline(y=case["avg_rating_after"], line_dash="dot", line_color="#2ca02c",
               annotation_text=f"Avg after: {case['avg_rating_after']:.2f}",
               annotation_position="bottom right")
fig2.update_layout(height=420, yaxis_title="Match rating")
st.plotly_chart(fig2, width="stretch")
st.caption("Gaps in the line mean no rating was recorded for that match. "
           f"Rating change after recovery: {case['rating_change']:+.2f}")

st.divider()

# ------------------------------------------------------------------
# Visual 3: Heatmap - injury frequency across months and clubs
# ------------------------------------------------------------------
st.subheader("3. Injury frequency across months and clubs")

heat = pd.pivot_table(
    filtered, index="team", columns="injury_month_name",
    values="player_name", aggfunc="count", fill_value=0,
)
heat = heat.reindex(columns=[m for m in MONTH_ORDER if m in heat.columns])

fig3 = px.imshow(
    heat, text_auto=True, aspect="auto", color_continuous_scale="YlOrRd",
    labels={"x": "Month of injury", "y": "Club", "color": "Injuries"},
)
fig3.update_layout(height=max(400, 28 * len(heat) + 150))
st.plotly_chart(fig3, width="stretch")

st.divider()

# ------------------------------------------------------------------
# Visual 4: Scatter plot - player age vs performance drop index
# ------------------------------------------------------------------
st.subheader("4. Player age vs. team performance drop index")

fig4 = px.scatter(
    filtered, x="age", y="performance_drop_index",
    color="position", size="injury_duration_days", size_max=22,
    hover_data=["player_name", "team", "injury_type", "injury_duration_days"],
    labels={"age": "Player age", "performance_drop_index": "Performance drop index",
            "injury_duration_days": "Days out"},
)
fig4.add_hline(y=0, line_dash="dash", line_color="grey")
fig4.update_layout(height=480)
st.plotly_chart(fig4, width="stretch")
st.caption("Bubble size shows how many days the player was out. Points above the dashed line mean the team did worse without the player.")

st.divider()

# ------------------------------------------------------------------
# Visual 5: Leaderboard table - comeback players ranked by rating improvement
# ------------------------------------------------------------------
st.subheader("5. Comeback leaderboard: players ranked by rating improvement")

top_n = st.slider("Number of players to show", 5, 50, 15)

leaderboard = (
    filtered.groupby("player_name")
    .agg(team=("team", "last"),
         injuries=("injury_type", "count"),
         avg_rating_before=("avg_rating_before", "mean"),
         avg_rating_after=("avg_rating_after", "mean"),
         rating_improvement=("rating_change", "mean"))
    .round(2)
    .sort_values("rating_improvement", ascending=False)
    .head(top_n)
    .reset_index()
)
leaderboard.insert(0, "rank", range(1, len(leaderboard) + 1))

st.dataframe(
    leaderboard,
    width="stretch",
    hide_index=True,
    column_config={
        "rank": "Rank",
        "player_name": "Player",
        "team": "Club",
        "injuries": "Injuries",
        "avg_rating_before": st.column_config.NumberColumn("Avg rating before", format="%.2f"),
        "avg_rating_after": st.column_config.NumberColumn("Avg rating after", format="%.2f"),
        "rating_improvement": st.column_config.ProgressColumn(
            "Rating improvement",
            format="%+.2f",
            min_value=float(leaderboard["rating_improvement"].min()),
            max_value=float(max(leaderboard["rating_improvement"].max(), 0.01)),
        ),
    },
)

st.divider()
st.caption("Data source: FootLens player injuries and team performance dataset. "
           "Dashboard built with Streamlit, pandas and Plotly.")
