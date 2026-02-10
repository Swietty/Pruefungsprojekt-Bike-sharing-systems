import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"


class DataAnalyzer:
    """
    Responsible for loading, cleaning, and exporting bike-sharing datasets.
    """

    def __init__(self, output_dir: str = "output") -> None:
        self.trips: pd.DataFrame | None = None
        self.stations: pd.DataFrame | None = None
        self.maintenance: pd.DataFrame | None = None

        self.OUTPUT_DIR = Path(output_dir)  

    # ---------------------------
    # Loading
    # ---------------------------
    def load_data(self) -> None:
        self.trips = pd.read_csv(DATA_DIR / "trips.csv")
        self.stations = pd.read_csv(DATA_DIR / "stations.csv")
        self.maintenance = pd.read_csv(DATA_DIR / "maintenance.csv")

    # ---------------------------
    # Inspection
    # ---------------------------
    def inspect(self) -> None:
        for name, df in [
            ("Trips", self.trips),
            ("Stations", self.stations),
            ("Maintenance", self.maintenance),
        ]:
            print(f"\n{name}")
            print(df.info())
            print(df.isnull().sum())

    # ---------------------------
    # Cleaning
    # ---------------------------
    def _clean_trips(self) -> None:
        df = self.trips.copy()

        df = df.drop_duplicates(subset=["trip_id"])
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
        df = df[df["end_time"] > df["start_time"]]

        # Numeric columns
        for col in ["duration_minutes", "distance_km"]:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ".").str.strip(),
                errors="coerce",
            )

        df["duration_minutes"] = df["duration_minutes"].fillna(df["duration_minutes"].median())
        df["distance_km"] = df["distance_km"].fillna(df["distance_km"].median())
        df["status"] = df["status"].fillna("completed")

        # Standardize categoricals
        for col in ["status", "user_type", "bike_type"]:
            df[col] = df[col].str.lower().str.strip()

        self.trips = df

    # ---------------------------
    # Analytics — Business Questions
    # ---------------------------
    def total_trips_summary(self) -> dict:
        df = self.trips
        return {
            "total_trips": len(df),
            "total_distance_km": round(df["distance_km"].sum(), 2),
            "avg_duration_min": round(df["duration_minutes"].mean(), 2),
        }

    def top_start_stations(self, n: int = 10) -> pd.DataFrame:
        counts = self.trips["start_station_id"].value_counts().head(n).reset_index()
        counts.columns = ["station_id", "trip_count"]
        return counts.merge(self.stations, on="station_id", how="left")[["station_id", "station_name", "trip_count"]]

    def peak_usage_hours(self) -> pd.Series:
        df = self.trips.copy()
        df["hour"] = df["start_time"].dt.hour
        return df.groupby("hour").size()

    def busiest_day_of_week(self) -> pd.Series:
        df = self.trips.copy()
        df["weekday"] = df["start_time"].dt.day_name()
        return df.groupby("weekday").size().sort_values(ascending=False)

    def avg_distance_by_user_type(self) -> pd.Series:
        return self.trips.groupby("user_type")["distance_km"].mean().round(2)

    def avg_duration_by_user_type(self) -> pd.Series:
        return self.trips.groupby("user_type")["duration_minutes"].mean().round(2)

    def monthly_trip_trend(self) -> pd.Series:
        df = self.trips.copy()
        df["year_month"] = df["start_time"].dt.to_period("M")
        return df.groupby("year_month").size()

    def top_active_users(self, n: int = 15) -> pd.DataFrame:
        return (
            self.trips.groupby("user_id").size().sort_values(ascending=False).head(n)
            .reset_index(name="trip_count")
        )

    def maintenance_cost_by_bike_type(self) -> pd.Series:
        return self.maintenance.groupby("bike_type")["cost"].sum().round(2)

    def top_routes(self, n: int = 10) -> pd.DataFrame:
        routes = (
            self.trips.groupby(["start_station_id", "end_station_id"])
            .size().sort_values(ascending=False).head(n)
            .reset_index(name="trip_count")
        )
        return routes

    # ---------------------------
    # Reporting
    # ---------------------------
    def generate_summary_report(self) -> None:
        """Write a summary text report to OUTPUT_DIR / summary_report.txt"""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        report_path = self.OUTPUT_DIR / "summary_report.txt"

        lines: list[str] = [
            "=" * 60,
            "  CityBike — Analytics Summary Report",
            "=" * 60,
        ]

        # --- Q1 Overall Summary ---
        summary = self.total_trips_summary()
        lines += [
            "\n--- Overall Summary ---",
            f"Total trips        : {summary['total_trips']}",
            f"Total distance     : {summary['total_distance_km']} km",
            f"Average duration   : {summary['avg_duration_min']} min",
        ]

        # --- Q2 Top 10 Start Stations ---
        lines += ["\n--- Top 10 Start Stations ---", self.top_start_stations().to_string(index=False)]

        # --- Q3 Peak Usage Hours ---
        lines += ["\n--- Peak Usage Hours ---", self.peak_usage_hours().to_string()]

        # --- Q4 Busiest Days of Week ---
        lines += ["\n--- Busiest Days of Week ---", self.busiest_day_of_week().to_string()]

        # --- Q5 Avg Distance by User Type ---
        lines += ["\n--- Avg Distance by User Type ---", self.avg_distance_by_user_type().to_string()]

        # --- Q6 Avg Duration by User Type ---
        lines += ["\n--- Avg Duration by User Type ---", self.avg_duration_by_user_type().to_string()]

        # --- Q7 Monthly Trip Trend ---
        lines += ["\n--- Monthly Trip Trend ---", self.monthly_trip_trend().to_string()]

        # --- Q8 Top Active Users ---
        lines += ["\n--- Top 15 Active Users ---", self.top_active_users().to_string(index=False)]

        # --- Q9 Maintenance Cost by Bike Type ---
        lines += ["\n--- Maintenance Cost by Bike Type ---", self.maintenance_cost_by_bike_type().to_string()]

        # --- Q10 Top Routes ---
        lines += ["\n--- Top 10 Most Common Routes ---", self.top_routes().to_string(index=False)]

        # Write to file
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Report saved to {report_path}")

