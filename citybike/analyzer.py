import pandas as pd
from pathlib import Path
import numpy as np

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
    # Cleaning
    # ---------------------------
    def _clean_trips(self) -> None:
        df = self.trips.copy()
        df = df.drop_duplicates(subset=["trip_id"])
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
        df = df[df["end_time"] > df["start_time"]]

        for col in ["duration_minutes", "distance_km"]:
            df[col] = pd.to_numeric(
                df[col].astype(str).str.replace(",", ".").str.strip(),
                errors="coerce",
            )

        df["duration_minutes"] = df["duration_minutes"].fillna(df["duration_minutes"].median())
        df["distance_km"] = df["distance_km"].fillna(df["distance_km"].median())
        df["status"] = df["status"].fillna("completed")

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

    def top_end_stations(self, n: int = 10) -> pd.DataFrame:
        counts = self.trips["end_station_id"].value_counts().head(n).reset_index()
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

    def bike_utilization_rate(self) -> float:
        total_time = (self.trips["end_time"] - self.trips["start_time"]).sum().total_seconds() / 3600
        n_bikes = self.trips["bike_id"].nunique()
        total_possible = n_bikes * (self.trips["end_time"].max() - self.trips["start_time"].min()).total_seconds() / 3600
        return round((total_time / total_possible) * 100, 2)

    def trip_completion_rate(self) -> dict:
        counts = self.trips["status"].value_counts()
        completed = counts.get("completed", 0)
        cancelled = counts.get("cancelled", 0)
        total = completed + cancelled
        return {
            "completed": completed,
            "cancelled": cancelled,
            "completion_rate_%": round((completed / total) * 100, 2) if total > 0 else 0
        }

    def avg_trips_per_user(self) -> pd.Series:
        return self.trips.groupby("user_type")["user_id"].value_counts().groupby(level=0).mean().round(2)

    def bikes_highest_maintenance(self, n: int = 10) -> pd.DataFrame:
        counts = self.maintenance["bike_id"].value_counts().head(n).reset_index()
        counts.columns = ["bike_id", "maintenance_count"]
        return counts

    def detect_outlier_trips(self, z_thresh: float = 3.0) -> pd.DataFrame:
        df = self.trips.copy()
        df["duration_z"] = (df["duration_minutes"] - df["duration_minutes"].mean()) / df["duration_minutes"].std()
        df["distance_z"] = (df["distance_km"] - df["distance_km"].mean()) / df["distance_km"].std()
        outliers = df[(df["duration_z"].abs() > z_thresh) | (df["distance_z"].abs() > z_thresh)]
        return outliers

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

        # Q1 Overall Summary
        summary = self.total_trips_summary()
        lines += [
            "\n--- Q1: Overall Summary ---",
            f"Total trips        : {summary['total_trips']}",
            f"Total distance     : {summary['total_distance_km']} km",
            f"Average duration   : {summary['avg_duration_min']} min",
        ]

        # Q2 Top Start/End Stations
        lines += ["\n--- Q2: Top 10 Start Stations ---", self.top_start_stations().to_string(index=False)]
        lines += ["\n--- Q2: Top 10 End Stations ---", self.top_end_stations().to_string(index=False)]

        # Q3 Peak Usage Hours
        lines += ["\n--- Q3: Peak Usage Hours ---", self.peak_usage_hours().to_string()]

        # Q4 Busiest Days of Week
        lines += ["\n--- Q4: Busiest Days of Week ---", self.busiest_day_of_week().to_string()]

        # Q5 Avg Distance by User Type
        lines += ["\n--- Q5: Avg Distance by User Type ---", self.avg_distance_by_user_type().to_string()]

        # Q6 Bike Utilization Rate
        lines += [f"\n--- Q6: Bike Utilization Rate --- {self.bike_utilization_rate()} %"]

        # Q7 Monthly Trip Trend
        lines += ["\n--- Q7: Monthly Trip Trend ---", self.monthly_trip_trend().to_string()]

        # Q8 Top Active Users
        lines += ["\n--- Q8: Top 15 Active Users ---", self.top_active_users().to_string(index=False)]

        # Q9 Maintenance Cost by Bike Type
        lines += ["\n--- Q9: Maintenance Cost by Bike Type ---", self.maintenance_cost_by_bike_type().to_string()]

        # Q10 Top Routes
        lines += ["\n--- Q10: Top 10 Most Common Routes ---", self.top_routes().to_string(index=False)]

        # Q11 Trip Completion Rate
        lines += ["\n--- Q11: Trip Completion Rate ---", str(self.trip_completion_rate())]

        # Q12 Avg Trips per User
        lines += ["\n--- Q12: Avg Trips per User by User Type ---", self.avg_trips_per_user().to_string()]

        # Q13 Bikes with Highest Maintenance Frequency
        lines += ["\n--- Q13: Bikes with Highest Maintenance Frequency ---", self.bikes_highest_maintenance().to_string(index=False)]

        # Q14 Outlier Trips
        outliers = self.detect_outlier_trips()
        lines += [f"\n--- Q14: Number of Outlier Trips --- {len(outliers)}"]

        # Write to file
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"Report saved to {report_path}")
