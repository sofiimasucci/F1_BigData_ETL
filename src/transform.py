# ── transform.py — Fase TRANSFORM del pipeline ETL F1 ──
import pandas as pd
import hashlib
from sklearn.preprocessing import LabelEncoder
from datetime import datetime

def transform_all(results, races, drivers):
    """Aplica T08-T10 y genera el modelo en estrella"""

    # T08 — Detección de outliers IQR (documentar, no eliminar)
    def detectar_outliers(df, col):
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = df[(df[col] < Q1 - 1.5*IQR) | (df[col] > Q3 + 1.5*IQR)]
        return len(outliers)

    for col in ['grid','positionOrder','points','laps']:
        n = detectar_outliers(results, col)
        print(f"[{datetime.now()}] T08 Outliers {col}: {n} detectados — conservados")

    # T09 — Seudonimización SHA-256
    def hash_sha256(valor):
        return hashlib.sha256(str(valor).encode()).hexdigest()

    drivers['dob_hash'] = drivers['dob'].apply(hash_sha256)
    drivers['url_hash'] = drivers['url'].apply(hash_sha256)
    drivers = drivers.drop(columns=['dob', 'url'], errors='ignore')
    print(f"[{datetime.now()}] T09 Seudonimización aplicada ✅")

    # T10 — LabelEncoder nationality
    le = LabelEncoder()
    drivers['nationality_encoded'] = le.fit_transform(drivers['nationality'])
    print(f"[{datetime.now()}] T10 Encoding nationality: {drivers['nationality'].nunique()} valores ✅")

    # Crear DIM_TIEMPO
    dim_tiempo = pd.DataFrame()
    dim_tiempo['fecha'] = pd.to_datetime(races['date'])
    dim_tiempo.insert(0, 'sk_tiempo', range(1, len(dim_tiempo)+1))
    dim_tiempo['anio']       = dim_tiempo['fecha'].dt.year
    dim_tiempo['trimestre']  = dim_tiempo['fecha'].dt.quarter
    dim_tiempo['mes']        = dim_tiempo['fecha'].dt.month
    dim_tiempo['semana']     = dim_tiempo['fecha'].dt.isocalendar().week.astype(int)
    dim_tiempo['dia']        = dim_tiempo['fecha'].dt.day
    dim_tiempo['dia_semana'] = dim_tiempo['fecha'].dt.day_name()
    dim_tiempo['es_festivo'] = False
    dim_tiempo['fecha']      = dim_tiempo['fecha'].dt.strftime('%Y-%m-%d')

    # Crear DIM_RACES
    dim_races = races[['raceId','year','round','circuitId','name','date']].copy()
    dim_races.insert(0, 'sk_race', range(1, len(dim_races)+1))
    dim_races['source_id']       = 'kaggle_races'
    dim_races['load_timestamp']  = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

    # Crear DIM_DRIVERS
    dim_drivers = drivers[['driverId','driverRef','forename','surname',
                            'nationality','nationality_encoded','code','dob_hash']].copy()
    dim_drivers.insert(0, 'sk_driver', range(1, len(dim_drivers)+1))
    dim_drivers['source_id']      = 'kaggle_drivers'
    dim_drivers['load_timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

    # Crear FACT_RESULTS
    fact = results.copy()
    fact = fact.merge(dim_races[['raceId','sk_race']], on='raceId', how='left')
    fact = fact.merge(dim_drivers[['driverId','sk_driver']], on='driverId', how='left')
    dim_t_merge = dim_tiempo[['sk_tiempo','fecha']].merge(
        dim_races[['raceId','date']], left_on='fecha', right_on='date', how='left')
    fact = fact.merge(dim_t_merge[['raceId','sk_tiempo']], on='raceId', how='left')

    fact_final = fact[['resultId','sk_race','sk_driver','sk_tiempo',
                        'constructorId','grid','positionOrder','points',
                        'laps','milliseconds','fastestLapSpeed','statusId']].copy()
    fact_final = fact_final.loc[:, ~fact_final.columns.duplicated()]
    fact_final.insert(0, 'sk_resultado', range(1, len(fact_final)+1))
    fact_final['source_id']      = 'kaggle_results'
    fact_final['load_timestamp'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')

    print(f"[{datetime.now()}] Modelo en estrella generado ✅")
    return dim_tiempo, dim_races, dim_drivers, fact_final

if __name__ == "__main__":
    from extract import extract_kaggle
    from clean import clean_all
    results, races, drivers = extract_kaggle()
    results, races, drivers = clean_all(results, races, drivers)
    dim_tiempo, dim_races, dim_drivers, fact_final = transform_all(results, races, drivers)
    print("Transformación completada ✅")
