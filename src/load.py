# ── load.py — Fase LOAD del pipeline ETL F1 ──
import sqlite3
import pandas as pd
from datetime import datetime

def load_to_sqlite(dim_tiempo, dim_races, dim_drivers, fact_final, db_path="f1_warehouse_final.db"):
    """Carga el modelo en estrella en SQLite"""

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Crear tablas con DDL explícito
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DIM_TIEMPO (
        sk_tiempo   INTEGER PRIMARY KEY,
        fecha       TEXT,
        anio        INTEGER,
        trimestre   INTEGER,
        mes         INTEGER,
        semana      INTEGER,
        dia         INTEGER,
        dia_semana  TEXT,
        es_festivo  INTEGER
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DIM_RACES (
        sk_race        INTEGER PRIMARY KEY,
        raceId         INTEGER NOT NULL,
        year           INTEGER,
        round          INTEGER,
        circuitId      INTEGER,
        name           TEXT,
        date           TEXT,
        source_id      TEXT,
        load_timestamp TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS DIM_DRIVERS (
        sk_driver           INTEGER PRIMARY KEY,
        driverId            INTEGER NOT NULL,
        driverRef           TEXT,
        forename            TEXT,
        surname             TEXT,
        nationality         TEXT,
        nationality_encoded INTEGER,
        code                TEXT,
        dob_hash            TEXT,
        source_id           TEXT,
        load_timestamp      TEXT
    )""")

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS FACT_RESULTS (
        sk_resultado    INTEGER PRIMARY KEY,
        resultId        INTEGER,
        sk_race         INTEGER,
        sk_driver       INTEGER,
        sk_tiempo       INTEGER,
        constructorId   INTEGER,
        grid            INTEGER,
        positionOrder   INTEGER,
        points          REAL,
        laps            INTEGER,
        milliseconds    INTEGER,
        fastestLapSpeed REAL,
        statusId        INTEGER,
        source_id       TEXT,
        load_timestamp  TEXT,
        FOREIGN KEY (sk_race)    REFERENCES DIM_RACES(sk_race),
        FOREIGN KEY (sk_driver)  REFERENCES DIM_DRIVERS(sk_driver),
        FOREIGN KEY (sk_tiempo)  REFERENCES DIM_TIEMPO(sk_tiempo)
    )""")

    conn.commit()
    print(f"[{datetime.now()}] Esquema DDL creado ✅")

    # Cargar dimensiones primero, luego fact
    dim_tiempo.to_sql("DIM_TIEMPO",   conn, if_exists="replace", index=False)
    dim_races.to_sql("DIM_RACES",     conn, if_exists="replace", index=False)
    dim_drivers.to_sql("DIM_DRIVERS", conn, if_exists="replace", index=False)
    fact_final.to_sql("FACT_RESULTS", conn, if_exists="replace", index=False)
    print(f"[{datetime.now()}] Datos cargados ✅")

    # Crear índices
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sk_race   ON FACT_RESULTS(sk_race)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sk_driver ON FACT_RESULTS(sk_driver)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_sk_tiempo ON FACT_RESULTS(sk_tiempo)")
    conn.commit()
    print(f"[{datetime.now()}] Índices creados ✅")

    # Verificación COUNT(*)
    print(f"\n=== VERIFICACIÓN DE CARGA ===")
    for tabla in ["DIM_TIEMPO", "DIM_RACES", "DIM_DRIVERS", "FACT_RESULTS"]:
        count = pd.read_sql(f"SELECT COUNT(*) as n FROM {tabla}", conn)['n'][0]
        print(f"{tabla:<20} → {count:>6} filas ✅")

    conn.close()
    return db_path

if __name__ == "__main__":
    from extract import extract_kaggle
    from clean import clean_all
    from transform import transform_all
    results, races, drivers = extract_kaggle()
    results, races, drivers = clean_all(results, races, drivers)
    dim_tiempo, dim_races, dim_drivers, fact_final = transform_all(results, races, drivers)
    load_to_sqlite(dim_tiempo, dim_races, dim_drivers, fact_final)
    print("Carga completada ✅")
