import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


class DataAnalyzer:
    """
    Responsible for loading, cleaning, and exporting bike-sharing datasets.
    Does NOT work with domain objects (Bike, Trip, User).
    """

    def __init__(self) -> None:
        self.trips: pd.DataFrame | None = None
        self.stations: pd.DataFrame | None = None
        self.maintenance: pd.DataFrame | None = None

        # Loading
    
    def load_data(self) -> None:
        self.trips = pd.read_csv(DATA_DIR / "trips.csv")
        self.stations = pd.read_csv(DATA_DIR / "stations.csv")
        self.maintenance = pd.read_csv(DATA_DIR / "maintenance.csv")

       # Inspection
    
    def inspect(self) -> None:
        for name, df in [
            ("Trips", self.trips),
            ("Stations", self.stations),
            ("Maintenance", self.maintenance),
        ]:
            print(f"\n{name}")
            print(df.info())
            print(df.isnull().sum())

        # Cleaning
    
    def _clean_trips(self) -> None:
        df = self.trips.copy()

        # 1. Remove duplicates
        df = df.drop_duplicates(subset=["trip_id"])

        # 2. Parse datetime columns
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

        # 3. Remove invalid time ranges
        df = df[df["end_time"] > df["start_time"]]

        # 4. Numeric columns — предварительно очистим строки
        df["duration_minutes"] = (
            df["duration_minutes"]
            .astype(str)
            .str.replace(",", ".")
            .str.strip()
        )
        df["distance_km"] = (
            df["distance_km"]
            .astype(str)
            .str.replace(",", ".")
            .str.strip()
        )

        df["duration_minutes"] = pd.to_numeric(df["duration_minutes"], errors="coerce")
        df["distance_km"] = pd.to_numeric(df["distance_km"], errors="coerce")

        # 5. Handle missing values
        df["duration_minutes"] = df["duration_minutes"].fillna(df["duration_minutes"].median())
        df["distance_km"] = df["distance_km"].fillna(df["distance_km"].median())
        df["status"] = df["status"].fillna("completed")

        # 6. Standardize categoricals
        df["status"] = df["status"].str.lower().str.strip()
        df["user_type"] = df["user_type"].str.lower().str.strip()
        df["bike_type"] = df["bike_type"].str.lower().str.strip()

        self.trips = df  
    
    

