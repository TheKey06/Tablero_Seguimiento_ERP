import base64
from pathlib import Path
import pandas as pd

MESES = ["", "ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]

def logo_data_uri(path: Path) -> str:
    mime = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
            ".svg": "image/svg+xml", ".webp": "image/webp"}[path.suffix.lower()]
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

def h(s: str) -> str:
    """Compacta el HTML para que Markdown no lo interprete como bloque de código."""
    return "".join(line.strip() for line in s.strip().splitlines())


def fdate(ts, year: bool = False) -> str:
        
    if pd.isna(ts):
        return "—"
    return f"{ts.day:02d} {MESES[ts.month]}" + (f" {ts.year}" if year else "")


def cop(v: float) -> str:
    return "$" + f"{v:,.0f}".replace(",", ".")


def pct1(x: float) -> str:
    return f"{x * 100:.1f}%".replace(".", ",")


def num2(x) -> str:
    return "—" if x is None else f"{x:.2f}".replace(".", ",")


def sem_color(p: float) -> str:
    """Semáforo para indicadores en % (0-100)."""
    return "var(--tertiary)" if p >= 80 else "var(--warn)" if p >= 60 else "var(--error)"


def bucket(r) -> str:
    if r.estado == "Completado":
        return "Completado"
    if r.cumplimiento == "Con retraso" or r.dias_retraso > 0:
        return "Con retraso"
    return "En progreso" if r.estado == "En progreso" else "Pendiente"

