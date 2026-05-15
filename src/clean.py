# ── clean.py — Fase CLEAN del pipeline ETL F1 ──
import pandas as pd
import numpy as np
import unicodedata
from datetime import datetime

def clean_all(results, races, drivers):
    """Aplica T01-T08 a los 3 DataFrames"""

    # T01 — Eliminar duplicados
    results = results.drop_duplicates()
    races   = races.drop_duplicates()
    drivers = drivers.drop_duplicates()
    print(f"[{datetime.now()}] T01 Duplicados eliminados ✅")

    # T02 — Reemplazar \N por NaN y tratar nulos
    results = results.replace("\\N", np.nan)
    races   = races.replace("\\N", np.nan)
    drivers = drivers.replace("\\N", np.nan)

    results['position']        = results['position'].fillna("N/A")
    results['time']            = results['time'].fillna("N/A")
    results['milliseconds']    = results['milliseconds'].fillna(0)
    results['fastestLap']      = results['fastestLap'].fillna("N/A")
    results['rank']            = results['rank'].fillna("N/A")
    results['fastestLapTime']  = results['fastestLapTime'].fillna("N/A")
    results['fastestLapSpeed'] = results['fastestLapSpeed'].fillna(0)
    results['number']          = results['number'].fillna("N/A")

    for col in ['time','fp1_date','fp1_time','fp2_date','fp2_time',
                'fp3_date','fp3_time','quali_date','quali_time',
                'sprint_date','sprint_time']:
        races[col] = races[col].fillna("N/A")

    drivers['number'] = drivers['number'].fillna("N/A")
    drivers['code']   = drivers['code'].fillna("N/A")
    print(f"[{datetime.now()}] T02 Nulos tratados ✅")

    # T03 — Eliminar blancos
    for df in [results, races, drivers]:
        for col in df.select_dtypes(include='object').columns:
            df[col] = df[col].astype(str).str.strip()
    print(f"[{datetime.now()}] T03 Blancos eliminados ✅")

    # T04 — Corrección de tipos
    results['milliseconds']    = pd.to_numeric(results['milliseconds'], errors='coerce').fillna(0)
    results['fastestLapSpeed'] = pd.to_numeric(results['fastestLapSpeed'], errors='coerce').fillna(0)
    races['date']   = pd.to_datetime(races['date'], errors='coerce')
    drivers['dob']  = pd.to_datetime(drivers['dob'], errors='coerce')
    print(f"[{datetime.now()}] T04 Tipos corregidos ✅")

    # T05 — Normalización de fechas ISO-8601
    races['date']   = races['date'].dt.strftime('%Y-%m-%d')
    drivers['dob']  = drivers['dob'].dt.strftime('%Y-%m-%d')
    print(f"[{datetime.now()}] T05 Fechas normalizadas ✅")

    # T06 — Normalización de texto
    def normalizar(texto):
        if isinstance(texto, str):
            texto = texto.lower().strip()
            texto = unicodedata.normalize('NFKD', texto)
            texto = texto.encode('ascii', 'ignore').decode('ascii')
        return texto

    drivers['nationality'] = drivers['nationality'].apply(normalizar)
    drivers['forename']    = drivers['forename'].apply(normalizar)
    drivers['surname']     = drivers['surname'].apply(normalizar)
    races['name']          = races['name'].apply(normalizar)
    print(f"[{datetime.now()}] T06 Texto normalizado ✅")

    # T07 — Validación de rangos
    assert results['grid'].min() >= 0, "Error: grid negativo"
    assert results['points'].min() >= 0, "Error: points negativo"
    print(f"[{datetime.now()}] T07 Rangos validados ✅")

    return results, races, drivers

if __name__ == "__main__":
    from extract import extract_kaggle
    results, races, drivers = extract_kaggle()
    results, races, drivers = clean_all(results, races, drivers)
    print("Limpieza completada ✅")
