"""
Tablero ERP — Módulo de Facturación (Streamlit)
Estructura tomada de frame.html: barra lateral (iniciativa, objetivos, navegación, usuario),
barra superior, métricas de cabecera, barra de macroprogreso, filtros secuenciales y tarjetas
de actividades. Todos los números salen de data/dataset_facturacion_erp.csv.

Ejecutar:  streamlit run app.py
"""
from __future__ import annotations
from hooks import * # Importar todas las funciones del archivo hooks.py para tener el codigo mas limpio
import io
from datetime import date
from html import escape
from pathlib import Path
from textwrap import shorten

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Vanguard — Facturación ERP", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

# ───────────────────────────── Configuración ─────────────────────────────
BASE = Path(__file__).parent
DATA_PATHS = [BASE / "data" / "dataset_facturacion_erp.csv", BASE / "dataset_facturacion_erp.csv"]
LOGO = logo_data_uri(BASE / "images" / "logo.png")
USER_NAME, USER_ROLE = "Keyner Rivas", "Gestor ERP"
INITIATIVE = "Módulo de Facturación ERP- Grupo Éxito"
INITIATIVE_TEXT = "Control de facturación electrónica, cumplimiento DIAN e integración tecnológica."
NAV = ["Inicio", "Proyectos y Flujos", "Riesgos y Alertas", "Reportes Ejecutivos", "Configuración"]
RISK_ORDER = ["Alto", "Medio", "Bajo"]
ALL = "Todos"
REQUIRED = ["ID", "obj", "nombre_obj", "actividad", "entregable", "modulo", "responsable", "estado", "avance%",
            "inicio_plan", "fin_plan", "fin_presupuesto", "costo_plan.", "costo_ejec.", "%_ejec_financiera",
            "ddesviacion", "valor_ganado", "riesgo_asociado", "nombre_riesgo", "Nivel_riesgo", "cumplimiento",
            "Dias_retraso", "alerta"]
BUCKETS = ["Completado", "En progreso", "Con retraso", "Pendiente"]
BUCKET_COL = {"Completado": "var(--tertiary)", "En progreso": "var(--secondary)",
              "Con retraso": "var(--error)", "Pendiente": "#475569"}
BUCKET_HEX = {"Completado": "#34d399", "En progreso": "#38bdf8", "Con retraso": "#f87171", "Pendiente": "#475569"}
CUMPL_CLS = {"Entregada a tiempo": "ok", "Entregada con retraso": "warn", "Con retraso": "err",
             "En proceso": "sec", "Pendiente": "mut"}
ALERT = {"OK": ("ok", "Sin alerta"), "Sobrecosto": ("warn", "Sobrecosto"),
         "Retraso": ("err", "Retraso"), "Revisar": ("sec", "Revisar")}


# ───────────────────────────── Estilos ─────────────────────────────
CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');
:root{--surface:#0b1326;--dim:#080e1c;--lowest:#060b17;--low:#111827;--cont:#151e33;--high:#1e2942;--highest:#283454;
--on:#f1f5f9;--variant:#94a3b8;--outline:#64748b;--ovar:#334155;--primary:#818cf8;--pcont:#4f46e5;
--secondary:#38bdf8;--tertiary:#34d399;--error:#f87171;--warn:#fbbf24;}
html,body,.stApp,[data-testid="stAppViewContainer"]{background:var(--surface)!important;color:var(--on);font-family:'Inter',sans-serif;}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],#MainMenu,footer{display:none!important;}
[data-testid="stSidebarCollapseButton"],[data-testid="collapsedControl"],[data-testid="stSidebarCollapsedControl"]{display:none!important;}
section[data-testid="stSidebar"]{min-width:320px!important;max-width:320px!important;width:320px!important;background:rgba(8,14,28,.95)!important;border-right:1px solid rgba(51,65,85,.35);}
section[data-testid="stSidebar"] > div{width:320px!important;}
[data-testid="stSidebarUserContent"],[data-testid="stSidebarContent"]>div:first-child{padding-top:1.2rem!important;}
section[data-testid="stSidebar"] .block-container,[data-testid="stSidebarUserContent"]{padding-left:1.4rem!important;padding-right:1.4rem!important;}
.block-container{max-width:1080px!important;margin:0 auto;padding:5.8rem 2.2rem 4rem!important;}
.mono{font-family:'JetBrains Mono',monospace;}
.ms{font-family:'Material Symbols Outlined';font-weight:normal;font-style:normal;line-height:1;letter-spacing:normal;text-transform:none;display:inline-block;white-space:nowrap;font-feature-settings:'liga';vertical-align:middle;}
.lbl{font-size:10px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--outline);}
/* Barra superior */
.vg-top{position:fixed;top:0;left:320px;right:0;height:64px;z-index:999;background:rgba(11,19,38,.78);backdrop-filter:blur(10px);
border-bottom:1px solid rgba(51,65,85,.25);display:flex;align-items:center;justify-content:space-between;padding:0 2.5rem;}
.vg-top h2{font-size:14px;font-weight:600;letter-spacing:.02em;margin:0;padding:0;color:var(--on);}
.vg-row{display:flex;align-items:center;gap:12px;}
.pill{font-size:11px;color:var(--outline);border:1px solid rgba(51,65,85,.5);padding:2px 8px;border-radius:6px;}
.sync{display:flex;align-items:center;gap:8px;font-size:12px;color:var(--outline);border:1px solid rgba(51,65,85,.5);padding:6px 12px;border-radius:8px;}
.dot{display:inline-block;width:8px;height:8px;border-radius:50%;}
@media(max-width:1000px){.vg-top{left:0;}}
/* Barra lateral */
.sb-brand{display:flex;align-items:center;gap:12px;margin-bottom:22px;}
.sb-brand img{height:32px;width:32px;border-radius:8px;object-fit:contain;}
.sb-brand b{display:block;font-size:16px;font-weight:600;letter-spacing:-.01em;}
.sb-brand span{display:block;font-size:11px;font-weight:500;letter-spacing:.06em;text-transform:uppercase;color:var(--variant);}
.sb-card{background:rgba(17,24,39,.7);border:1px solid rgba(51,65,85,.4);border-radius:12px;padding:18px;margin-bottom:22px;}
.sb-card .t{font-size:15px;font-weight:600;margin:10px 0 6px;}
.sb-card p{font-size:12px;color:var(--outline);line-height:1.55;margin:0;}
.sb-prog{margin-top:14px;padding-top:12px;border-top:1px solid rgba(51,65,85,.4);}
.sb-obj{border:1px solid rgba(51,65,85,.3);border-radius:8px;padding:10px;margin-bottom:9px;}
.sb-profile{display:flex;align-items:center;gap:10px;margin-top:26px;padding-top:16px;border-top:1px solid rgba(51,65,85,.25);}
.sb-av{width:28px;height:28px;border-radius:50%;background:rgba(129,140,248,.2);color:var(--primary);font-size:12px;font-weight:600;display:flex;align-items:center;justify-content:center;}
.between{display:flex;align-items:center;justify-content:space-between;gap:8px;}
.track{width:100%;background:var(--cont);border-radius:99px;overflow:hidden;display:flex;border:1px solid rgba(51,65,85,.3);}
.fill{height:100%;border-radius:99px;}
/* Navegación (st.radio) */
section[data-testid="stSidebar"] div[role="radiogroup"]{gap:4px;}
section[data-testid="stSidebar"] div[role="radiogroup"]>label{width:100%;padding:8px 12px!important;border-radius:8px;border:1px solid transparent;cursor:pointer;margin:0!important;}
section[data-testid="stSidebar"] div[role="radiogroup"]>label>div:first-child{display:none!important;}
section[data-testid="stSidebar"] div[role="radiogroup"]>label p{font-size:12px!important;font-weight:500;color:var(--variant);margin:0;}
section[data-testid="stSidebar"] div[role="radiogroup"]>label p::before{font-family:'Material Symbols Outlined';font-size:18px;vertical-align:middle;margin-right:10px;color:var(--outline);font-weight:normal;}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:nth-of-type(1) p::before{content:'home';}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:nth-of-type(2) p::before{content:'folder_open';}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:nth-of-type(3) p::before{content:'warning';}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:nth-of-type(4) p::before{content:'bar_chart';}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:nth-of-type(5) p::before{content:'settings';}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:hover{background:var(--low);}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked){background:rgba(129,140,248,.10);border-color:rgba(129,140,248,.25);}
section[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked) p,
section[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked) p::before{color:var(--primary);}
/* Cabecera */
.vg-head{display:flex;flex-wrap:wrap;align-items:flex-end;justify-content:space-between;gap:24px;padding-bottom:22px;border-bottom:1px solid rgba(51,65,85,.3);margin-bottom:26px;}
.vg-head h1{font-size:26px;font-weight:700;letter-spacing:-.02em;margin:2px 0 4px;padding:0;line-height:1.2;}
.vg-head p{font-size:12px;color:var(--outline);margin:0;}
.vg-met{display:flex;gap:14px;flex-wrap:wrap;}
.met{border:1px solid rgba(51,65,85,.4);background:rgba(21,30,51,.5);border-radius:10px;padding:12px 14px;min-width:132px;}
.met .v{font-size:22px;font-weight:700;margin:4px 0 2px;}
.met .s{font-size:10px;color:var(--outline);}
.vg-sec{border:1px solid rgba(51,65,85,.35);border-radius:12px;padding:18px 20px;margin-bottom:26px;background:rgba(21,30,51,.35);}
.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:11px;color:var(--outline);}
.legend span{display:flex;align-items:center;gap:5px;}
/* Filtros */
div[data-testid="stSelectbox"] label p{font-size:10px!important;font-weight:600!important;letter-spacing:.08em;text-transform:uppercase;color:var(--outline)!important;}
div[data-baseweb="select"]>div{background:var(--low)!important;border:1px solid rgba(51,65,85,.5)!important;border-radius:8px!important;min-height:38px;font-size:12px;}
.stButton>button,.stDownloadButton>button{background:transparent;border:1px solid rgba(51,65,85,.6);color:var(--variant);font-size:12px;border-radius:8px;padding:.25rem .8rem;}
.stButton>button:hover,.stDownloadButton>button:hover{border-color:var(--outline);color:var(--on);background:var(--low);}
/* Tarjetas de actividad */
.vg-act{border:1px solid rgba(51,65,85,.4);background:rgba(17,24,39,.55);border-radius:12px;padding:18px 20px;margin-bottom:14px;transition:background .2s;}
.vg-act:hover{background:var(--low);}
.vg-act-top{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin-bottom:12px;}
.vg-act-id{display:flex;align-items:center;gap:12px;}
.vg-num{width:32px;height:32px;border-radius:50%;border:1px solid rgba(100,116,139,.5);color:var(--outline);font-size:11px;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;justify-content:center;flex:none;}
.vg-act-name{font-size:13px;font-weight:600;color:var(--on);line-height:1.35;}
.vg-act-sub{font-size:11px;color:var(--outline);margin-top:2px;}
.vg-act-right{display:flex;align-items:center;gap:12px;}
.vg-pct{font-size:15px;font-weight:700;font-family:'JetBrains Mono',monospace;}
.vg-track{height:8px;width:100%;background:var(--cont);border-radius:99px;overflow:hidden;border:1px solid rgba(51,65,85,.3);}
.vg-fill{height:100%;border-radius:99px;}
.vg-chips{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0;}
.tag{display:inline-block;padding:2px 9px;border-radius:6px;font-size:11px;font-weight:600;border:1px solid transparent;}
.tag.err{background:rgba(248,113,113,.12);color:var(--error);border-color:rgba(248,113,113,.25);}
.tag.warn{background:rgba(251,191,36,.12);color:var(--warn);border-color:rgba(251,191,36,.25);}
.tag.ok{background:rgba(52,211,153,.12);color:var(--tertiary);border-color:rgba(52,211,153,.25);}
.tag.sec{background:rgba(56,189,248,.12);color:var(--secondary);border-color:rgba(56,189,248,.25);}
.tag.mut{background:rgba(100,116,139,.12);color:var(--variant);border-color:rgba(100,116,139,.3);}
.vg-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;}
@media(max-width:900px){.vg-grid{grid-template-columns:1fr;}}
.vg-cell{background:rgba(8,14,28,.55);border-radius:8px;padding:10px 12px;font-size:11px;color:var(--outline);}
.vg-cell b{display:block;color:var(--on);font-weight:500;font-size:12px;margin:3px 0;}
.vg-cell em{font-style:normal;}
.vg-empty{border:1px dashed rgba(51,65,85,.6);border-radius:12px;padding:40px;text-align:center;color:var(--outline);}
.vg-title{font-size:18px;font-weight:600;margin:0 0 4px;}
.vg-sub{font-size:12px;color:var(--outline);margin-bottom:18px;}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

# ───────────────────────────── Datos ─────────────────────────────
def default_bytes() -> bytes:
    for p in DATA_PATHS:
        if p.exists():
            return p.read_bytes()
    st.error("No se encontró data/dataset_facturacion_erp.csv. Cárgalo en Configuración o colócalo en esa ruta.")
    st.stop()


@st.cache_data(show_spinner=False)
def load_data(raw: bytes) -> pd.DataFrame:
    df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig")
    df.columns = [c.strip() for c in df.columns]
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError("Faltan columnas: " + ", ".join(missing))
    df = df.rename(columns={"avance%": "avance", "costo_plan.": "costo_plan", "costo_ejec.": "costo_ejec",
                            "%_ejec_financiera": "ejec_fin", "ddesviacion": "desviacion",
                            "Nivel_riesgo": "nivel_riesgo", "Dias_retraso": "dias_retraso"})
    for c in ("inicio_plan", "fin_plan", "fin_presupuesto"):
        df[c] = pd.to_datetime(df[c], errors="coerce")
    for c in ("avance", "costo_plan", "costo_ejec", "ejec_fin", "desviacion", "valor_ganado", "dias_retraso"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df = df.reset_index(drop=True)
    df["n"] = df.index + 1
    df["bucket"] = df.apply(bucket, axis=1)
    return df


def infer_cutoff(df: pd.DataFrame) -> pd.Timestamp:
    """Fecha de corte = fin_plan + días de retraso de las actividades retrasadas (viernes de seguimiento)."""
    late = df[df.dias_retraso > 0]
    if not late.empty:
        return (late.fin_plan + pd.to_timedelta(late.dias_retraso, unit="D")).mode().iloc[0]
    return pd.Timestamp(date.today())


def kpis(d: pd.DataFrame, corte: pd.Timestamp) -> dict:
    bac, ev, ac = d.costo_plan.sum(), d.valor_ganado.sum(), d.costo_ejec.sum()
    pv = d.loc[d.fin_plan <= corte, "costo_plan"].sum()
    cpi = ev / ac if ac else None
    spi = ev / pv if pv else None
    return dict(bac=bac, ev=ev, ac=ac, pv=pv, prog=ev / bac if bac else 0, planned=pv / bac if bac else 0,
                cpi=cpi, spi=spi, eac=bac / cpi if cpi else None)


ss = st.session_state
try:
    raw = ss.get("csv_bytes") or default_bytes()
    df = load_data(raw)
except Exception as exc:  # CSV subido inválido → vuelve al original
    st.warning(f"No se pudo leer el dataset cargado ({exc}). Se usa el original.")
    ss.pop("csv_bytes", None)
    df = load_data(default_bytes())
if df.empty:
    st.error("El dataset no contiene actividades.")
    st.stop()

CORTE = infer_cutoff(df)
G = kpis(df, CORTE)
n_alerts = int((df.alerta != "OK").sum())
n_ok_sched = int((~df.cumplimiento.isin(["Con retraso", "Entregada con retraso"])).sum())
dian = df[df.nombre_obj.str.contains("DIAN", case=False, na=False)]
dian_prog = (dian.valor_ganado.sum() / dian.costo_plan.sum() * 100) if len(dian) and dian.costo_plan.sum() else None
worst = min([v for v in (G["cpi"], G["spi"]) if v is not None], default=1)
STATUS = ("En riesgo", "err") if worst < 0.8 else ("En atención", "warn") if worst < 0.95 else ("En control", "ok")

# ───────────────────────────── Barra lateral ─────────────────────────────
OBJECTIVES = [
    ("Avance del módulo", G["prog"] * 100, "Valor ganado / presupuesto total (BAC)"),
    ("Cumplimiento de cronograma", n_ok_sched / len(df) * 100, "Actividades sin retraso / total de actividades"),
    ("Eficiencia de costos", min(G["cpi"], 1) * 100 if G["cpi"] else 100, "CPI = valor ganado / costo ejecutado (tope 100 %)"),
    ("Cumplimiento normativo DIAN", dian_prog, "Avance ponderado de las actividades del objetivo de facturación y cumplimiento DIAN"),
]
obj_html = ""
for name, val, tip in OBJECTIVES:
    if val is None:
        obj_html += f'<div class="sb-obj" title="{escape(tip)}"><div class="between lbl" style="text-transform:none;font-size:12px;font-weight:400"><span>{name}</span><span>--</span></div></div>'
        continue
    obj_html += (f'<div class="sb-obj" title="{escape(tip)}"><div class="between" style="font-size:12px;color:var(--outline);margin-bottom:7px">'
                 f'<span>{name}</span><span class="mono" style="color:{sem_color(val)}">{val:.1f}%</span></div>'
                 f'<div class="track" style="height:4px"><div class="fill" style="width:{min(val, 100):.1f}%;background:{sem_color(val)}"></div></div></div>')

with st.sidebar:
    st.markdown(h(f"""
    <div class="sb-brand"><img alt="Logo" src="{LOGO}"><div><b>Vanguard</b><span>Inteligencia de Proyectos</span></div></div>
    <div class="sb-card">
      <div class="between"><span class="lbl">Iniciativa Estratégica</span><span class="tag {STATUS[1]}">{STATUS[0]}</span></div>
      <div class="t">{INITIATIVE}</div>
      <p>{INITIATIVE_TEXT}</p>
      <div class="sb-prog">
        <div class="between" style="font-size:12px;color:var(--outline);margin-bottom:7px"><span>Progreso Global</span><span class="mono">{pct1(G['prog'])}</span></div>
        <div class="track" style="height:6px"><div class="fill" style="width:{G['prog']*100:.1f}%;background:var(--primary)"></div></div>
      </div>
    </div>
    <div class="between" style="margin-bottom:12px"><span class="lbl" style="font-size:11px">Objetivos Clave</span><span style="font-size:11px;color:var(--outline)">{len(OBJECTIVES)} indicadores</span></div>
    {obj_html}
    <div class="lbl" style="margin:22px 0 8px 2px;font-size:11px">Navegación</div>
    """), unsafe_allow_html=True)
    view = st.radio("Navegación", NAV, key="view", label_visibility="collapsed",
                    format_func=lambda x: f"{x}  ·  {n_alerts}" if x == "Riesgos y Alertas" else x)
    initials = "".join(w[0] for w in USER_NAME.split()[:2]).upper()
    st.markdown(h(f"""<div class="sb-profile"><div class="sb-av">{initials}</div>
    <div><div style="font-size:12px;font-weight:500">{USER_NAME}</div><div style="font-size:10px;color:var(--outline)">{USER_ROLE}</div></div></div>"""),
                unsafe_allow_html=True)

# ───────────────────────────── Barra superior ─────────────────────────────
crumb = "Inicio / Vista Facturación" if view == "Inicio" else f"Inicio / {view}"
st.markdown(h(f"""<div class="vg-top"><div class="vg-row"><span class="ms" style="color:var(--outline);font-size:20px">grid_view</span>
<h2>{crumb}</h2><span class="pill">Corte: {fdate(CORTE, True)}</span></div>
<div class="vg-row"><div class="sync"><span class="dot" style="background:var(--tertiary)"></span><span>Sincronizado</span></div></div></div>"""),
            unsafe_allow_html=True)


# ───────────────────────────── Componentes de vista ─────────────────────────────
def metric(label: str, value: str, sub: str, vcolor: str = "var(--on)", subcolor: str = "var(--outline)") -> str:
    return (f'<div class="met"><span class="lbl" style="text-transform:none;font-size:11px;font-weight:500">{label}</span>'
            f'<div class="v" style="color:{vcolor}">{value}</div><span class="s" style="color:{subcolor}">{sub}</span></div>')


def activity_card(r) -> str:
    risk_cls = {"Alto": "err", "Medio": "warn", "Bajo": "ok"}.get(r.nivel_riesgo, "mut")
    bcol = BUCKET_COL[r.bucket]
    p = max(0.0, min(1.0, r.avance))
    cump_txt = r.cumplimiento + (f" · {int(r.dias_retraso)} d" if r.dias_retraso > 0 else "")
    a_cls, a_txt = ALERT.get(r.alerta, ("mut", r.alerta))
    real = fdate(r.fin_presupuesto, True) if pd.notna(r.fin_presupuesto) else "en curso"
    pace = r.costo_ejec / r.costo_plan if r.costo_plan else 0
    return h(f"""
    <div class="vg-act">
      <div class="vg-act-top">
        <div class="vg-act-id"><div class="vg-num">{r.n}</div>
          <div><div class="vg-act-name">{escape(r.actividad)}</div>
          <div class="vg-act-sub">{escape(r.responsable)} · {escape(r.modulo)} · <span class="mono">{escape(r.ID)}</span></div></div></div>
        <div class="vg-act-right"><span class="tag {risk_cls}">Riesgo {escape(r.nivel_riesgo)}</span>
          <span class="vg-pct" style="color:{bcol}">{p*100:.0f}%</span></div>
      </div>
      <div class="vg-track"><div class="vg-fill" style="width:{p*100:.1f}%;background:{bcol}"></div></div>
      <div class="vg-chips"><span class="tag mut">{escape(r.estado)}</span>
        <span class="tag {CUMPL_CLS.get(r.cumplimiento, 'mut')}">{escape(cump_txt)}</span>
        <span class="tag {a_cls}">{a_txt}</span></div>
      <div class="vg-grid">
        <div class="vg-cell"><span class="lbl">Cronograma</span><b>{fdate(r.inicio_plan)} → {fdate(r.fin_plan, True)}</b><em>Entrega real: {real}</em></div>
        <div class="vg-cell"><span class="lbl">Presupuesto</span><b>{cop(r.costo_ejec)} / {cop(r.costo_plan)}</b><em>Ejecución {pct1(pace)} · avance {p*100:.0f}%</em></div>
        <div class="vg-cell"><span class="lbl">Riesgo {escape(r.riesgo_asociado)}</span><b>{escape(shorten(r.nombre_riesgo, 70, placeholder='…'))}</b><em>{escape(r.entregable)}</em></div>
      </div>
    </div>""")


def plot_layout(height: int = 320) -> dict:
    return dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8", size=11),
                margin=dict(l=0, r=0, t=10, b=0), height=height, legend=dict(orientation="h", y=1.14))


# ═════════════════════════════ VISTA: INICIO ═════════════════════════════
if view == "Inicio":
    # Estado de filtros (se valida antes de dibujar los widgets)
    for k in ("f_obj", "f_risk", "f_person"):
        ss.setdefault(k, ALL)

    def _reset():
        ss.f_obj = ss.f_risk = ss.f_person = ALL

    def _obj_changed():
        ss.f_risk = ss.f_person = ALL

    def _risk_changed():
        ss.f_person = ALL

    if ss.f_obj != ALL and ss.f_obj not in set(df.obj):
        ss.f_obj = ALL
    d1 = df if ss.f_obj == ALL else df[df.obj == ss.f_obj]
    risk_opts = [ALL] + [r for r in RISK_ORDER if r in set(d1.nivel_riesgo)] + \
                sorted(set(d1.nivel_riesgo) - set(RISK_ORDER))
    if ss.f_risk not in risk_opts:
        ss.f_risk = ALL
    d2 = d1 if ss.f_risk == ALL else d1[d1.nivel_riesgo == ss.f_risk]
    person_opts = [ALL] + sorted(d2.responsable.unique())
    if ss.f_person not in person_opts:
        ss.f_person = ALL
    f = d2 if ss.f_person == ALL else d2[d2.responsable == ss.f_person]
    K = kpis(f, CORTE) if len(f) else kpis(df.iloc[0:0], CORTE)
    filtered = len(f) != len(df)

    # 1) Cabecera + métricas
    delta = (K["prog"] - K["planned"]) * 100
    dcol = "var(--tertiary)" if delta >= 0 else "var(--warn)" if delta > -10 else "var(--error)"
    alerts_f = int((f.alerta != "OK").sum())
    st.markdown(h(f"""
    <section class="vg-head">
      <div><div class="lbl mono" style="font-size:11px">Visualización de Control</div>
        <h1>Tablero de Facturación ERP - Grupo Éxito</h1>
        <p>Seguimiento de actividades, entregables y riesgos del módulo de facturación · valores a la fecha de corte {fdate(CORTE, True)}.</p></div>
      <div class="vg-met">
        {metric("Avance ponderado", pct1(K['prog']), f"{delta:+.1f} pts vs plan".replace('.', ','), subcolor=dcol)}
        {metric("Actividades", str(len(f)), "En la selección" if filtered else "Total activo")}
        {metric("Alertas", str(alerts_f), "Requieren acción", vcolor="var(--error)" if alerts_f else "var(--tertiary)")}
      </div>
    </section>"""), unsafe_allow_html=True)

    # 2) Barra de macroprogreso
    counts = f.bucket.value_counts() if len(f) else pd.Series(dtype=int)
    tot = max(len(f), 1)
    segs = "".join(f'<div style="height:100%;width:{counts.get(b, 0) / tot * 100:.2f}%;background:{BUCKET_COL[b]}" title="{b}: {counts.get(b, 0)}"></div>'
                   for b in BUCKETS if counts.get(b, 0))
    legend = "".join(f'<span><span class="dot" style="background:{BUCKET_COL[b]}"></span>{b} ({int(counts.get(b, 0))})</span>' for b in BUCKETS)
    st.markdown(h(f"""
    <section class="vg-sec">
      <div class="between" style="margin-bottom:12px;flex-wrap:wrap"><span style="font-size:12px;font-weight:500;color:var(--outline)">Estado General de Entregables</span>
      <div class="legend">{legend}</div></div>
      <div class="track" style="height:10px">{segs}</div>
    </section>"""), unsafe_allow_html=True)

    # 3) Filtros secuenciales
    hc, rc, dc = st.columns([5, 1.3, 1.5])
    hc.markdown(h('<div class="vg-row" style="padding-top:6px"><span class="ms" style="color:var(--outline);font-size:18px">filter_alt</span>'
                  '<span class="lbl" style="font-size:12px">Filtros Secuenciales</span></div>'), unsafe_allow_html=True)
    rc.button("↺ Restablecer", on_click=_reset, use_container_width=True)
    dc.download_button("⬇ Exportar CSV", f.to_csv(index=False).encode("utf-8"), "facturacion_filtrado.csv", "text/csv",
                       use_container_width=True)
    c1, c2, c3 = st.columns(3)
    names = df.drop_duplicates("obj").set_index("obj").nombre_obj.to_dict()
    c1.selectbox("Paso 1: Objetivo", [ALL] + sorted(df.obj.unique()), key="f_obj", on_change=_obj_changed,
                 format_func=lambda x: x if x == ALL else f"{x} · {shorten(names[x], 34, placeholder='…')}")
    c2.selectbox("Paso 2: Riesgo", risk_opts, key="f_risk", on_change=_risk_changed)
    c3.selectbox("Paso 3: Responsable", person_opts, key="f_person")
    st.markdown(f'<div style="font-size:11px;color:var(--outline);margin:6px 0 16px">{len(f)} de {len(df)} actividades · cada paso reduce las opciones del siguiente</div>',
                unsafe_allow_html=True)

    # 4) Tarjetas de actividades
    if f.empty:
        st.markdown('<div class="vg-empty"><div class="ms" style="font-size:36px">filter_alt_off</div><div style="margin-top:8px">Ninguna actividad coincide con los filtros.</div></div>',
                    unsafe_allow_html=True)
    else:
        st.markdown("".join(activity_card(r) for r in f.itertuples()), unsafe_allow_html=True)

# ═════════════════════════════ VISTA: PROYECTOS Y FLUJOS ═════════════════════════════
elif view == "Proyectos y Flujos":
    st.markdown('<div class="vg-title">Proyectos y Flujos</div><div class="vg-sub">Cronograma planificado por actividad, con la fecha de corte y el avance real.</div>',
                unsafe_allow_html=True)
    g = df.sort_values("inicio_plan", ascending=False)
    fig = go.Figure()
    for b in BUCKETS:
        gg = g[g.bucket == b]
        if gg.empty:
            continue
        dur = (gg.fin_plan - gg.inicio_plan + pd.Timedelta(days=1)).dt.total_seconds() * 1000
        fig.add_bar(y=gg.apply(lambda r: f"#{r.n} {r.ID}", axis=1), base=gg.inicio_plan, x=dur, orientation="h",
                    name=b, marker_color=BUCKET_HEX[b], opacity=0.85,
                    customdata=gg[["actividad", "responsable", "avance"]].values,
                    hovertemplate="%{customdata[0]}<br>%{customdata[1]} · avance %{customdata[2]:.0%}<extra></extra>")
    fig.add_shape(type="line", x0=CORTE.to_pydatetime(), x1=CORTE.to_pydatetime(), y0=0, y1=1, xref="x", yref="paper",
                  line=dict(color="#fbbf24", dash="dash", width=2))
    fig.add_annotation(x=CORTE.to_pydatetime(), y=1.0, yref="paper", text="Corte", showarrow=False, yshift=10,
                       font=dict(color="#fbbf24", size=11))
    fig.update_layout(barmode="overlay", xaxis=dict(type="date", gridcolor="#1e2942"), yaxis=dict(automargin=True),
                      **plot_layout(340))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    show = df[["n", "ID", "actividad", "modulo", "responsable", "estado", "avance", "inicio_plan", "fin_plan",
               "cumplimiento", "dias_retraso"]].copy()
    show["avance"] = (show.avance * 100).round(0).astype(int).astype(str) + "%"
    for c in ("inicio_plan", "fin_plan"):
        show[c] = show[c].dt.strftime("%Y-%m-%d")
    st.dataframe(show.rename(columns={"n": "#", "dias_retraso": "días retraso"}), hide_index=True, width="stretch")

# ═════════════════════════════ VISTA: RIESGOS Y ALERTAS ═════════════════════════════
elif view == "Riesgos y Alertas":
    st.markdown(f'<div class="vg-title">Riesgos y Alertas</div><div class="vg-sub">{n_alerts} de {len(df)} actividades con alerta activa.</div>',
                unsafe_allow_html=True)
    al = df[df.alerta != "OK"].sort_values(["dias_retraso", "desviacion"], ascending=False)
    if al.empty:
        st.markdown('<div class="vg-empty">Sin alertas activas.</div>', unsafe_allow_html=True)
    else:
        st.markdown("".join(activity_card(r) for r in al.itertuples()), unsafe_allow_html=True)
    st.markdown('<div class="lbl" style="margin:22px 0 8px;font-size:11px">Registro de riesgos asociados</div>', unsafe_allow_html=True)
    rk = (df.groupby(["riesgo_asociado", "nombre_riesgo", "nivel_riesgo"])
            .agg(actividades=("ID", lambda s: ", ".join(s)), avance_prom=("avance", "mean")).reset_index())
    rk["avance_prom"] = (rk.avance_prom * 100).round(0).astype(int).astype(str) + "%"
    st.dataframe(rk.rename(columns={"riesgo_asociado": "riesgo", "nombre_riesgo": "descripción",
                                    "nivel_riesgo": "nivel", "avance_prom": "avance prom."}),
                 hide_index=True, width="stretch")

# ═════════════════════════════ VISTA: REPORTES EJECUTIVOS ═════════════════════════════
elif view == "Reportes Ejecutivos":
    st.markdown(f'<div class="vg-title">Reportes Ejecutivos</div><div class="vg-sub">Indicadores de valor ganado a la fecha de corte {fdate(CORTE, True)}.</div>',
                unsafe_allow_html=True)
    cpi_c = "var(--tertiary)" if (G["cpi"] or 0) >= 1 else "var(--error)"
    spi_c = "var(--tertiary)" if (G["spi"] or 0) >= 1 else "var(--error)"
    vac = G["bac"] - G["eac"] if G["eac"] else None
    st.markdown('<div class="vg-met" style="margin-bottom:22px">' + "".join([
        metric("Presupuesto (BAC)", cop(G["bac"]), "Costo planificado total"),
        metric("Valor planificado (PV)", cop(G["pv"]), "Planeado al corte"),
        metric("Valor ganado (EV)", cop(G["ev"]), "Avance × costo plan"),
        metric("Costo real (AC)", cop(G["ac"]), "Ejecutado al corte"),
        metric("CPI", num2(G["cpi"]), "EV / AC", vcolor=cpi_c),
        metric("SPI", num2(G["spi"]), "EV / PV", vcolor=spi_c),
        metric("EAC", cop(G["eac"]) if G["eac"] else "—", "Estimado al terminar"),
        metric("VAC", cop(vac) if vac is not None else "—", "BAC − EAC", vcolor="var(--error)" if (vac or 0) < 0 else "var(--tertiary)"),
    ]) + "</div>", unsafe_allow_html=True)
    byo = df.groupby(["obj", "nombre_obj"]).agg(actividades=("ID", "count"), plan=("costo_plan", "sum"),
                                               ejecutado=("costo_ejec", "sum"), ganado=("valor_ganado", "sum")).reset_index()
    fig = go.Figure()
    fig.add_bar(x=byo.obj, y=byo.plan, name="Planificado", marker_color="#64748b")
    fig.add_bar(x=byo.obj, y=byo.ejecutado, name="Real (AC)", marker_color="#38bdf8")
    fig.add_bar(x=byo.obj, y=byo.ganado, name="Ganado (EV)", marker_color="#34d399")
    fig.update_layout(barmode="group", yaxis=dict(gridcolor="#1e2942", tickformat=".2s"), **plot_layout(300))
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    tab = byo.copy()
    tab["avance ponderado"] = (tab.ganado / tab.plan * 100).round(1).astype(str) + "%"
    for c in ("plan", "ejecutado", "ganado"):
        tab[c] = tab[c].map(cop)
    st.dataframe(tab.rename(columns={"nombre_obj": "objetivo"}), hide_index=True, width="stretch")
    st.download_button("⬇ Descargar dataset completo (CSV)", df.drop(columns=["n", "bucket"]).to_csv(index=False).encode("utf-8"),
                       "dataset_facturacion_erp.csv", "text/csv")

# ═════════════════════════════ VISTA: CONFIGURACIÓN ═════════════════════════════
else:
    st.markdown('<div class="vg-title">Configuración</div><div class="vg-sub">Origen de datos y definición de los indicadores.</div>', unsafe_allow_html=True)
    origin = "archivo cargado en esta sesión" if ss.get("csv_bytes") else "data/dataset_facturacion_erp.csv"
    st.markdown(h(f"""<div class="vg-sec"><div class="lbl">Dataset activo</div>
    <div style="font-size:13px;margin:6px 0">{origin} · {len(df)} actividades · {df.obj.nunique()} objetivos · BAC {cop(G['bac'])}</div>
    <div style="font-size:12px;color:var(--outline)">Fecha de corte (deducida de fin_plan + Dias_retraso): <b style="color:var(--on)">{fdate(CORTE, True)}</b></div></div>"""),
                unsafe_allow_html=True)
    up = st.file_uploader("Reemplazar dataset (CSV con las 23 columnas del Alcance)", type="csv")
    if up is not None and up.getvalue() != ss.get("csv_bytes"):
        try:
            load_data(up.getvalue())
            ss["csv_bytes"] = up.getvalue()
            st.rerun()
        except Exception as exc:
            st.error(f"Archivo no válido: {exc}")
    if ss.get("csv_bytes") and st.button("Volver al dataset original"):
        ss.pop("csv_bytes", None)
        st.rerun()
    st.markdown(h("""<div class="vg-sec"><div class="lbl" style="margin-bottom:8px">Definición de indicadores</div>
    <div style="font-size:12px;color:var(--variant);line-height:1.8">
    <b>Avance del módulo</b>: valor ganado (avance × costo plan) / presupuesto total.<br>
    <b>Variación vs plan</b>: avance del módulo − valor planificado / presupuesto (actividades con fin_plan ≤ corte).<br>
    <b>Cumplimiento de cronograma</b>: actividades sin retraso (ni vigente ni en la entrega) / total.<br>
    <b>Eficiencia de costos</b>: CPI = valor ganado / costo ejecutado, con tope de 100 %.<br>
    <b>Cumplimiento normativo DIAN</b>: avance ponderado de las actividades del objetivo de facturación y cumplimiento DIAN.<br>
    <b>Semáforo</b>: verde ≥ 80 %, ámbar 60–80 %, rojo &lt; 60 %. Estado del módulo: en riesgo si CPI o SPI &lt; 0,80; en atención si &lt; 0,95.<br>
    <b>Alertas</b>: actividades con alerta distinta de OK.</div></div>"""), unsafe_allow_html=True)