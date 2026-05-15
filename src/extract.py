# ── extract.py — Fase EXTRACT del pipeline ETL F1 ──
import pandas as pd
import requests
from datetime import datetime

BASE_RAW = "https://raw.githubusercontent.com/sofiimasucci/F1_BigData_ETL/refs/heads/main/data/raw/"

def extract_kaggle():
    """Extrae los 3 CSV de Kaggle desde GitHub"""
    results = pd.read_csv(BASE_RAW + "results.csv")
    races   = pd.read_csv(BASE_RAW + "races.csv")
    drivers = pd.read_csv(BASE_RAW + "drivers.csv")
    print(f"[{datetime.now()}] EXTRACT Kaggle — results: {results.shape}, races: {races.shape}, drivers: {drivers.shape}")
    return results, races, drivers

def extract_openf1():
    """Extrae datos de pilotos desde la API OpenF1"""
    url = "https://api.openf1.org/v1/drivers?session_key=9158"
    response = requests.get(url)
    openf1 = pd.DataFrame(response.json())
    print(f"[{datetime.now()}] EXTRACT OpenF1 API — registros: {openf1.shape[0]}")
    return openf1

if __name__ == "__main__":
    results, races, drivers = extract_kaggle()
    openf1 = extract_openf1()
    print("Extracción completada ✅")
