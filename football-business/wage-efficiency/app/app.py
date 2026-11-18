from pathlib import Path

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

DATA = Path(__file__).parent / "data"

LEAGUE_NAMES = {
    "premier": "Premier League",
    "laliga": "LaLiga",
    "seriea": "Serie A",
    "bundesliga": "Bundesliga",
    "ligue1": "Ligue 1",
}

# diverging pair: blue = got results cheaply, red = overpaid, gray = as expected
BLUE, RED, GRAY = "#2a78d6", "#e34948", "#b8b7b0"
SERIES_1, SERIES_2 = "#2a78d6", "#eb6834"
INK, INK_2 = "#0b0b0b", "#52514e"

st.set_page_config(page_title="Wage efficiency in European football", page_icon="⚽", layout="wide")


@st.cache_data
def load():
    res = pd.read_csv(DATA / "efficiency_results.csv")
    fits = pd.read_csv(DATA / "model_fits.csv")
    res["league_name"] = res.league.map(LEAGUE_NAMES)
    res["season_short"] = res.season.str[2:4] + "/" + res.season.str[-2:]
    res["wages_m"] = res.annual_wages_eur / 1e6
    res["wasted_m"] = res.wasted_eur / 1e6
    res["club_season"] = res.team + " " + res.season_short
    return res, fits


def base_layout(fig, height=480, **kw):
    fig.update_layout(
        height=height, margin=dict(l=10, r=10, t=30, b=10),
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, size=13), hoverlabel=dict(bgcolor="white", font_color=INK),
        **kw,
    )
    fig.update_xaxes(showgrid=False, linecolor="#d9d8d3", tickfont=dict(color=INK_2))
    fig.update_yaxes(gridcolor="#ecebe7", zeroline=False, tickfont=dict(color=INK_2))
    return fig


def money(v):
    return f"€{v:,.0f}m"


res, fits = load()

# ---------- header ----------
st.title("Who overpays for results in European football?")
st.caption(
    "Big 5 leagues · 2021/22–2025/26 · one regression per league-season: "
    "points per game ~ log(wage bill). Wages: Capology via FBref (estimates for most clubs)."
)

career = (res.groupby(["league_name", "team"])
          .agg(seasons=("season", "nunique"), wages_m=("wages_m", "sum"),
               pts=("pts_above_expected", "sum"), wasted_m=("wasted_m", "sum"))
          .reset_index())
worst = career.loc[career.wasted_m.idxmax()]
best = career.loc[career.pts.idxmax()]

k1, k2, k3, k4 = st.columns(4)
k1.metric("Club-seasons analysed", f"{len(res)}")
k2.metric("Points explained by wages", f"{fits.r2.mean():.0%}", help="Mean R² across the 25 league-season models")
k3.metric("Biggest overspend (5 seasons)", worst.team, f"+{money(worst.wasted_m)} wasted", delta_color="inverse")
k4.metric("Best value (5 seasons)", best.team, f"+{best.pts:.0f} pts above expected")

# ---------- filters ----------
f1, f2 = st.columns([3, 2])
leagues = f1.multiselect("Leagues", list(LEAGUE_NAMES.values()), default=list(LEAGUE_NAMES.values()))
seasons = sorted(res.season.unique())
season_sel = f2.select_slider("Seasons", options=seasons, value=(seasons[0], seasons[-1]),
                              format_func=lambda s: s[2:4] + "/" + s[-2:])
mask = res.league_name.isin(leagues) & res.season.between(*season_sel)
view = res[mask]

if view.empty:
    st.info("Pick at least one league.")
    st.stop()

tab_rank, tab_scatter, tab_club, tab_method = st.tabs(
    ["Ranking", "Wages vs points", "Club profile", "Method & limits"])

# ---------- ranking ----------
with tab_rank:
    level = st.radio("Level", ["Club (sum over selected seasons)", "Single season"], horizontal=True)
    if level.startswith("Club"):
        t = (view.groupby(["league_name", "team"])
             .agg(seasons=("season", "nunique"), wages_m=("wages_m", "sum"),
                  pts_above_expected=("pts_above_expected", "sum"), wasted_m=("wasted_m", "sum"))
             .reset_index())
        t["label"] = t.team
    else:
        t = view[["league_name", "team", "season_short", "position", "wages_m", "ppg", "expected",
                  "pts_above_expected", "wasted_m", "quadrant"]].copy()
        t["label"] = t.team + " " + t.season_short

    c1, c2 = st.columns(2)
    n = 10
    over = t.nlargest(n, "wasted_m").sort_values("wasted_m")
    fig = go.Figure(go.Bar(
        x=over.wasted_m, y=over.label, orientation="h", marker_color=RED,
        hovertemplate="%{y}<br>Overpaid: €%{x:,.0f}m<extra></extra>"))
    base_layout(fig, height=420, title=dict(text="Overpaid most (€m above what results justified)", font=dict(size=15)))
    fig.update_xaxes(title_text="€m")
    c1.plotly_chart(fig, width="stretch")

    top = t.nlargest(n, "pts_above_expected").sort_values("pts_above_expected")
    fig = go.Figure(go.Bar(
        x=top.pts_above_expected, y=top.label, orientation="h", marker_color=BLUE,
        hovertemplate="%{y}<br>+%{x:.1f} points above expected<extra></extra>"))
    base_layout(fig, height=420, title=dict(text="Best value (points above expected)", font=dict(size=15)))
    fig.update_xaxes(title_text="points")
    c2.plotly_chart(fig, width="stretch")

    st.caption("Overpayment is shown in €; over-performance in points, because the model's 'saving' for a title "
               "winner grows exponentially and would dominate any € chart.")

    table = t.drop(columns="label").sort_values("pts_above_expected", ascending=False)
    st.dataframe(
        table.rename(columns={"league_name": "League", "team": "Club", "seasons": "Seasons",
                              "season_short": "Season", "position": "Pos", "wages_m": "Wages €m",
                              "ppg": "PPG", "expected": "Expected PPG",
                              "pts_above_expected": "Pts vs expected", "wasted_m": "Overpaid €m",
                              "quadrant": "Quadrant"}),
        hide_index=True, width="stretch",
        column_config={c: st.column_config.NumberColumn(format="%.1f")
                       for c in ["Wages €m", "Pts vs expected", "Overpaid €m"]}
        | {c: st.column_config.NumberColumn(format="%.2f") for c in ["PPG", "Expected PPG"]},
    )

# ---------- scatter ----------
with tab_scatter:
    s1, s2 = st.columns(2)
    lg = s1.selectbox("League", leagues, key="sc_league")
    ss = s2.selectbox("Season", [s for s in seasons if season_sel[0] <= s <= season_sel[1]][::-1],
                      format_func=lambda s: s[2:4] + "/" + s[-2:], key="sc_season")
    lg_code = {v: k for k, v in LEAGUE_NAMES.items()}[lg]
    g = res[(res.league == lg_code) & (res.season == ss)]
    f = fits[(fits.league == lg_code) & (fits.season == ss)].iloc[0]

    lim = max(abs(g.residual).max(), 0.01)
    fig = go.Figure()
    xs = np.linspace(g.annual_wages_eur.min(), g.annual_wages_eur.max(), 200)
    fig.add_trace(go.Scatter(x=xs / 1e6, y=f.a + f.b * np.log(xs), mode="lines", name="Expected PPG",
                             line=dict(color=INK_2, width=2, dash="dash"), hoverinfo="skip"))
    fig.add_trace(go.Scatter(
        x=g.wages_m, y=g.ppg, mode="markers+text", text=g.team, textposition="top center",
        textfont=dict(size=11, color=INK_2), name="Clubs",
        marker=dict(size=13, color=g.residual, cmin=-lim, cmax=lim,
                    colorscale=[[0, RED], [0.5, GRAY], [1, BLUE]],
                    line=dict(color="white", width=2),
                    colorbar=dict(title="PPG vs<br>expected", thickness=12)),
        customdata=np.stack([g.position, g.expected, g.pts_above_expected, g.wasted_m], axis=1),
        hovertemplate=("<b>%{text}</b><br>Wages: €%{x:,.0f}m<br>PPG: %{y:.2f} (expected %{customdata[1]:.2f})"
                       "<br>Points vs expected: %{customdata[2]:+.1f}<br>Overpaid: €%{customdata[3]:+,.0f}m"
                       "<br>Final position: %{customdata[0]:.0f}<extra></extra>")))
    base_layout(fig, height=600, showlegend=False,
                title=dict(text=f"{lg} {ss[2:4]}/{ss[-2:]} — wages explain {f.r2:.0%} of points", font=dict(size=15)))
    fig.update_xaxes(type="log", title_text="Annual wage bill (€m, log scale)")
    fig.update_yaxes(title_text="Points per game")
    st.plotly_chart(fig, width="stretch")
    st.caption("Above the dashed line = more points than the wage bill predicts (blue); below = overpaid (red).")

# ---------- club profile ----------
with tab_club:
    clubs = sorted(view.team.unique())
    default = clubs.index("Sevilla") if "Sevilla" in clubs else 0
    club = st.selectbox("Club", clubs, index=default)
    c = res[res.team == club].sort_values("season")

    m1, m2, m3 = st.columns(3)
    m1.metric("Seasons in the data", c.season.nunique())
    m2.metric("Points vs expected (total)", f"{c.pts_above_expected.sum():+.0f}")
    m3.metric("Overpaid (total)", f"€{c.wasted_m.clip(lower=0).sum():,.0f}m",
              help="Sum of seasons where the club paid more than its results justified")

    p1, p2 = st.columns(2)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=c.season_short, y=c.ppg, name="Actual PPG", mode="lines+markers",
                             line=dict(color=SERIES_1, width=2), marker=dict(size=9)))
    fig.add_trace(go.Scatter(x=c.season_short, y=c.expected, name="Expected PPG (from wages)",
                             mode="lines+markers", line=dict(color=SERIES_2, width=2, dash="dash"),
                             marker=dict(size=9)))
    base_layout(fig, height=380, hovermode="x unified",
                title=dict(text="Points per game: actual vs expected", font=dict(size=15)),
                legend=dict(orientation="h", y=-0.15))
    p1.plotly_chart(fig, width="stretch")

    fig = go.Figure(go.Bar(
        x=c.season_short, y=c.wasted_m, marker_color=np.where(c.wasted_m > 0, RED, BLUE),
        hovertemplate="%{x}<br>%{y:+,.0f} €m<extra></extra>"))
    base_layout(fig, height=380, title=dict(text="Overpaid (+) / got results cheaply (−), €m", font=dict(size=15)))
    p2.plotly_chart(fig, width="stretch")

    st.dataframe(
        c[["season_short", "league_name", "position", "wages_m", "ppg", "expected", "pts_above_expected",
           "wasted_m", "pct_estimated", "quadrant"]]
        .rename(columns={"season_short": "Season", "league_name": "League", "position": "Pos",
                         "wages_m": "Wages €m", "ppg": "PPG", "expected": "Expected PPG",
                         "pts_above_expected": "Pts vs expected", "wasted_m": "Overpaid €m",
                         "pct_estimated": "% wages estimated", "quadrant": "Quadrant"}).round(2),
        hide_index=True, width="stretch")

# ---------- method ----------
with tab_method:
    st.markdown("""
**Question.** Given what a club pays its squad, how many points should it get — and how much money is it wasting?

**Model.** For each league and season: `PPG = a + b · log(wage bill)`. Fitting per league-season avoids comparing
nominal euros across leagues (Premier League money) and years (wage inflation).

**Metrics.**
- *Points vs expected* = (actual PPG − expected PPG) × games played.
- *Overpaid €* = wage bill − the wage bill the model needs for the points actually won.
- *Quadrants* = wage bill above/below the league median × performance above/below expected.

**Robustness.** Rankings were re-run with squad market value instead of wages and with goal difference or final
position instead of PPG. The share of wages that Capology estimates is uncorrelated with over/under-performance.

**Limits.**
- Wages are estimates for most clubs outside the elite.
- League games only: European and cup workload is not modelled.
- Wages measure squad cost, not the transfer fees behind it.
- Association, not causation: a big residual can be good management, luck, or an underpriced squad.

**Data.** Results: football-data.co.uk · Wages: Capology via FBref · Squad value: Transfermarkt (dcaribou dataset).
""")
    st.dataframe(fits.assign(league=fits.league.map(LEAGUE_NAMES)).round(3), hide_index=True, width="stretch")
