"""
easyMoney - Cross-selling campaign simulator (Task 4)

Reads the lightweight tables exported by 04_tarea4_impacto_economico.ipynb (data/app/)
and lets the business simulate a campaign: product, channel, segments and model cutoff.
All the calculation logic is the same as in the notebook; here it is only combined and displayed.

Run from the repository root:  streamlit run app/simulador.py
"""

from pathlib import Path

import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

# ── Paths ────────────────────────────────────────────────────────────────
RUTA_APP = Path(__file__).resolve().parent.parent / "data" / "app"

# Same rule as section 6 of notebook 04 to propose the role of each segment.
# Segment names are NOT hard-coded: they come from the data (they change if K-Means is retrained).
FACTOR_NUCLEO = 2.0    # "Everyone": conversion >= 2 x base rate and at least MIN_COMPRAS purchases
FACTOR_EXCLUIR = 0.5   # "Exclude": conversion < 0.5 x base rate
MIN_COMPRAS = 30

# Option labels in the sidebar
TODOS, TOP_MODELO, EXCLUIR = "Everyone", "Model top X%", "Exclude"

# English display names for the Task 3 segments (the data keeps the original Spanish names).
# Any segment not listed here is shown with its original name.
NOMBRES_EN = {
    "Particulares con nómina": "Individuals with salary account",
    "Universitarios con nómina": "Students with salary account",
    "Particulares con tarjeta": "Individuals with debit card",
    "Particulares básicos": "Basic individuals",
    "TOP ahorradores": "Top savers",
    "Universitarios recién llegados": "New student customers",
    "Universitarios inactivos": "Inactive students",
    "Sin producto": "No products",
    "Sin grupo": "No segment",
}


def nombre_en(g):
    return NOMBRES_EN.get(g, g)


# ── Data (read only once thanks to the cache) ────────────────────────────
@st.cache_data
def cargar(producto):
    val = pd.read_csv(RUTA_APP / f"validacion_grupo_{producto}.csv")
    val["nombre_grupo"] = val["nombre_grupo"].fillna("Sin grupo")
    sc = pd.read_csv(RUTA_APP / f"scoring_grupo_{producto}.csv")
    sc = sc.rename(columns={f"probabilidad_{producto}": "probabilidad"})
    sc["nombre_grupo"] = sc["nombre_grupo"].fillna("Sin grupo")
    margenes = pd.read_csv(RUTA_APP / f"margenes_{producto}.csv")["net_margin"].values
    return val, sc, margenes


def papel_por_defecto(val):
    """Proposes Everyone / Model top / Exclude for each segment based on its actual validation conversion."""
    tasa = val["compra_real"].mean()
    pg = val.groupby("nombre_grupo")["compra_real"].agg(["mean", "sum"]).sort_values("mean", ascending=False)
    defecto = {}
    for g, fila in pg.iterrows():
        if g == "Sin grupo" or fila["mean"] < FACTOR_EXCLUIR * tasa:
            defecto[g] = EXCLUIR
        elif fila["mean"] >= FACTOR_NUCLEO * tasa and fila["sum"] >= MIN_COMPRAS:
            defecto[g] = TODOS
        else:
            defecto[g] = TOP_MODELO
    return defecto


# ── Logic (identical to notebook 04) ─────────────────────────────────────
def aplicar_regla(df, nucleo, excluir, top_pct_resto):
    """Full core + model top X% in the remaining non-excluded segments."""
    umbral = df["probabilidad"].quantile(1 - top_pct_resto / 100) if top_pct_resto > 0 else np.inf
    en_nucleo = df["nombre_grupo"].isin(nucleo)
    en_resto = ~df["nombre_grupo"].isin(list(nucleo) + list(excluir)) & (df["probabilidad"] >= umbral)
    return df[en_nucleo | en_resto]


def evaluar(val, sc, margen_medio, nucleo, excluir, top_resto, coste_contacto, coste_fijo):
    """Measures the rule on validation and applies it to the scoring. Returns the deterministic result."""
    v = aplicar_regla(val, nucleo, excluir, top_resto)
    s = aplicar_regla(sc, nucleo, excluir, top_resto)
    conv = v["compra_real"].mean() if len(v) else 0.0
    contactos = len(s)
    ventas = contactos * conv
    coste = contactos * coste_contacto + coste_fijo
    return {
        "contactos": contactos, "conversion": conv, "ventas": ventas,
        "ingreso": ventas * margen_medio, "coste": coste, "beneficio": ventas * margen_medio - coste,
        "compras_val": int(v["compra_real"].sum()), "no_compras_val": int(len(v) - v["compra_real"].sum()),
        "seleccion": s,
    }


def monte_carlo(res, margenes, coste_contacto, coste_fijo, n_sim, semilla=42):
    """Beta for conversion, Binomial for sales, actual margins sampled."""
    rng = np.random.default_rng(semilla)
    contactos = res["contactos"]
    coste = contactos * coste_contacto + coste_fijo
    out = np.empty(n_sim)
    for i in range(n_sim):
        conv = rng.beta(res["compras_val"] + 1, res["no_compras_val"] + 1)
        ventas = rng.binomial(contactos, conv)
        out[i] = rng.choice(margenes, size=ventas).sum() - coste
    return out


def eur(x):
    return f"€{x:,.0f}" if x >= 0 else f"-€{-x:,.0f}"


# ── Interface ────────────────────────────────────────────────────────────
LOGO = Path(__file__).resolve().parent / "assets" / "logo.png"
st.set_page_config(page_title="easyMoney · Campaign simulator", page_icon=str(LOGO), layout="wide")
c_logo, c_titulo = st.columns([1, 5], vertical_alignment="center")
c_logo.image(str(LOGO), use_container_width=True)
c_titulo.title("Cross-selling campaign simulator")
st.caption("Combines the propensity model (Task 2) and the segmentation (Task 3) to estimate the economic outcome of a campaign.")

OPCIONES = [TODOS, TOP_MODELO, EXCLUIR]

with st.sidebar:
    st.header("Campaign")
    producto = st.selectbox("Product", ["pension_plan", "em_acount"])
    coste_contacto = st.select_slider(
        "Channel / cost per contact (€)", options=[0.1, 0.5, 1, 2, 5, 10, 30, 60], value=0.5,
        help="Push/email ≈ €0.10 · email + management ≈ €0.50 · letter ≈ €2 · phone call ≈ €5 · visit ≈ €30",
    )
    coste_fijo = st.number_input("Fixed cost (€)", 0, 100000, 10000, step=1000)

    val, sc, margenes = cargar(producto)
    DEFECTO = papel_por_defecto(val)
    # Campaign segments (May) that do not appear in validation: "Model top" by default
    for g in sc["nombre_grupo"].unique():
        DEFECTO.setdefault(g, EXCLUIR if g == "Sin grupo" else TOP_MODELO)

    st.header("Segments (Task 3)")
    st.caption("For each segment: contact everyone, only the model's top scores, or exclude it. "
               "The initial proposal comes from each segment's actual validation conversion (same rule as notebook 04).")
    decision = {}
    for g in DEFECTO:
        decision[g] = st.selectbox(nombre_en(g), OPCIONES, index=OPCIONES.index(DEFECTO[g]), key=f"dec_{producto}_{g}")
    top_resto = st.slider("In 'Model top X%' segments, contact the top X%", 0, 50, 20, step=5)

    st.header("Simulation")
    n_sim = st.select_slider("Monte Carlo simulations", options=[1000, 5000, 10000], value=5000)

nucleo = [g for g, d in decision.items() if d == TODOS]
excluir = [g for g, d in decision.items() if d == EXCLUIR]

margen_medio = margenes.mean()

res = evaluar(val, sc, margen_medio, nucleo, excluir, top_resto, coste_contacto, coste_fijo)
sim = monte_carlo(res, margenes, coste_contacto, coste_fijo, n_sim)
p5, p50, p95 = np.percentile(sim, [5, 50, 95])

# ── KPI cards ────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
c1.metric("Customers contacted", f"{res['contactos']:,}",
          f"{res['contactos'] / len(sc) * 100:.0f}% of eligible")
c2.metric("Expected sales", f"{res['ventas']:,.0f}",
          f"{res['conversion'] * 100:.2f}% conversion")
c3.metric("Campaign cost", eur(res["coste"]))
c4.metric("Net profit", f"€{res['beneficio'] / 1e6:.2f}M",
          f"90%: €{p5 / 1e6:.2f}M – €{p95 / 1e6:.2f}M", delta_color="off")

st.markdown(
    f"A **{producto}** sale brings in **{eur(margen_medio)}** on average. "
    f"Under these assumptions, each contact generates **{eur(res['beneficio'] / max(res['contactos'], 1))}** of profit. "
    f"Probability that the campaign loses money: **{(sim < 0).mean() * 100:.1f}%**."
)

# ── Profit curve by cutoff in the remaining segments ─────────────────────
col_a, col_b = st.columns([3, 2])

with col_a:
    st.subheader("Where to stop?")
    cortes = list(range(0, 51, 5))
    curva = pd.DataFrame([
        {"top_resto": c, **{k: v for k, v in evaluar(val, sc, margen_medio, nucleo, excluir, c, coste_contacto, coste_fijo).items() if k != "seleccion"}}
        for c in cortes
    ])
    curva["beneficio_M"] = curva["beneficio"] / 1e6
    base = alt.Chart(curva).encode(
        x=alt.X("contactos:Q", title="Customers contacted", axis=alt.Axis(format=",.0f")),
        y=alt.Y("beneficio_M:Q", title="Net profit (€M)", scale=alt.Scale(zero=False)),
        tooltip=[alt.Tooltip("top_resto:Q", title="Top % of the rest"),
                 alt.Tooltip("contactos:Q", title="Contacts", format=",.0f"),
                 alt.Tooltip("ventas:Q", title="Sales", format=",.0f"),
                 alt.Tooltip("beneficio_M:Q", title="Profit (€M)", format=".2f")],
    )
    linea = base.mark_line(color="#9A9A94", point=alt.OverlayMarkDef(color="#9A9A94", size=40))
    actual = alt.Chart(pd.DataFrame({"contactos": [res["contactos"]], "beneficio_M": [res["beneficio"] / 1e6]})).mark_point(
        size=220, filled=True, color="#7CC242").encode(x="contactos:Q", y="beneficio_M:Q")
    st.altair_chart((linea + actual).properties(height=320), use_container_width=True)
    st.caption("Each point adds another 5% of the model in the remaining segments. The green dot is the current configuration. When the curve flattens, each additional contact adds very little.")

with col_b:
    st.subheader("Who we contact")
    comp = (res["seleccion"]["nombre_grupo"].value_counts().rename("contactos").to_frame())
    conv_grupo = (aplicar_regla(val, nucleo, excluir, top_resto)
                  .groupby("nombre_grupo")["compra_real"].mean() * 100).round(2)
    comp["conversión %"] = conv_grupo.reindex(comp.index).fillna(0)
    comp["ventas esp."] = (comp["contactos"] * comp["conversión %"] / 100).round(0).astype(int)
    comp.index = [nombre_en(g) for g in comp.index]
    comp.index.name = "Segment"
    st.dataframe(
        comp, use_container_width=True, height=min(40 + 35 * len(comp), 400),
        column_config={
            "contactos": st.column_config.NumberColumn("Contacts", format="%d"),
            "conversión %": st.column_config.NumberColumn("Conversion", format="%.2f %%"),
            "ventas esp.": st.column_config.NumberColumn("Sales", format="%d"),
        },
    )

# ── Monte Carlo distribution ─────────────────────────────────────────────
st.subheader("Confidence interval")
hist_df = pd.DataFrame({"beneficio_M": sim / 1e6})
hist = alt.Chart(hist_df).mark_bar(color="#7CC242", opacity=0.75).encode(
    x=alt.X("beneficio_M:Q", bin=alt.Bin(maxbins=60), title="Net profit (€M)"),
    y=alt.Y("count():Q", title="Simulations"),
)
lineas = alt.Chart(pd.DataFrame({"x": [p5 / 1e6, p95 / 1e6]})).mark_rule(strokeDash=[4, 4], color="#1F1F1F").encode(x="x:Q")
st.altair_chart((hist + lineas).properties(height=220), use_container_width=True)
st.caption(
    f"{n_sim:,} simulations. Conservative scenario (p5) {eur(p5)} · base (p50) {eur(p50)} · optimistic (p95) {eur(p95)}. "
    "Conversion is sampled from a Beta fitted to the May 2019 validation; margin, from actual sales."
)

with st.expander("Assumptions and limitations"):
    st.markdown(
        """
- Conversion is measured in the validation month (May 2019) and assumed to hold for the campaign (June 2019).
- Results cover **one month**. They are not annualised: later waves yield less.
- These are sales the model **identifies**, not necessarily attributable to the campaign. Measuring incrementality requires a pilot with a control group.
- Cost per contact and fixed cost are business assumptions; they can be changed in the sidebar.
        """
    )