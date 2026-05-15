# ── tracker.py — Tracking del pipeline ETL F1 ──
import json
import os
from datetime import datetime

TRACKING_FILE = "logs/pipeline_tracking.json"

def init_tracking():
    """Inicializa el archivo de tracking"""
    tracking = {
        "pipeline": "F1 BigData ETL",
        "inicio": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fases": {}
    }
    os.makedirs("logs", exist_ok=True)
    with open(TRACKING_FILE, "w") as f:
        json.dump(tracking, f, indent=2)
    print(f"[{datetime.now()}] Tracking inicializado ✅")
    return tracking

def log_fase(fase, fuente, registros_entrada, registros_salida, descartados, motivo):
    """Registra una fase del pipeline en el archivo de tracking"""
    try:
        with open(TRACKING_FILE, "r") as f:
            tracking = json.load(f)
    except:
        tracking = init_tracking()

    if fase not in tracking["fases"]:
        tracking["fases"][fase] = []

    tracking["fases"][fase].append({
        "fuente": fuente,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "registros_entrada": registros_entrada,
        "registros_salida": registros_salida,
        "descartados": descartados,
        "motivo": motivo
    })

    with open(TRACKING_FILE, "w") as f:
        json.dump(tracking, f, indent=2)

    print(f"[{datetime.now()}] LOG {fase} — {fuente}: {registros_entrada}→{registros_salida} ({descartados} descartados)")

def resumen_tracking():
    """Muestra el resumen del tracking"""
    with open(TRACKING_FILE, "r") as f:
        tracking = json.load(f)
    print("\n=== RESUMEN TRACKING PIPELINE ===")
    print(f"Pipeline: {tracking['pipeline']}")
    print(f"Inicio:   {tracking['inicio']}")
    for fase, registros in tracking["fases"].items():
        for r in registros:
            print(f"{fase:<15} {r['fuente']:<20} {r['registros_entrada']:>8} → {r['registros_salida']:>8} ({r['descartados']} descartados) — {r['motivo']}")

if __name__ == "__main__":
    init_tracking()
    log_fase("EXTRACT", "results.csv", 26759, 26759, 0, "Sin errores")
    log_fase("EXTRACT", "races.csv",   1125,  1125,  0, "Sin errores")
    log_fase("EXTRACT", "drivers.csv", 861,   861,   0, "Sin errores")
    log_fase("T01",     "todas",       28765, 28765, 0, "Sin duplicados")
    log_fase("T02",     "todas",       28765, 28765, 0, "Nulos imputados")
    log_fase("T08",     "results",     26759, 26759, 0, "Outliers conservados")
    resumen_tracking()
    print("\nTracking completado ✅")
