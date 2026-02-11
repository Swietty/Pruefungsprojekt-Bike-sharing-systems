import matplotlib.pyplot as plt # type: ignore
import pandas as pd
import seaborn as sns   # type: ignore
from pathlib import Path


FIGURES_DIR = Path(__file__).resolve().parent / "output" / "figures"

def _save_figure(fig: plt.Figure, filename: str) -> None:
    """Save a Matplotlib figure to the figures directory."""
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    filepath = FIGURES_DIR / filename
    fig.savefig(filepath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved: {filepath}")

# ---------------------------------------------------------------------------
# Bar chart — trips per station
# ---------------------------------------------------------------------------
def plot_trips_per_station(trips: pd.DataFrame, stations: pd.DataFrame) -> None:
    counts = (
        trips["start_station_id"]
        .value_counts()
        .head(10)
        .rename_axis("station_id")
        .reset_index(name="trip_count")
    )
    merged = counts.merge(stations[["station_id", "station_name"]], on="station_id", how="left")
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(merged["station_name"], merged["trip_count"], color="steelblue")
    ax.set_xlabel("Number of Trips")
    ax.set_ylabel("Station")
    ax.set_title("Top 10 Start Stations by Trip Count")
    ax.invert_yaxis()
    _save_figure(fig, "trips_per_station.png")

# ---------------------------------------------------------------------------
# Line chart — monthly trip trend
# ---------------------------------------------------------------------------
def plot_monthly_trend(trips: pd.DataFrame) -> None:
    df = trips.copy()
    df["year_month"] = df["start_time"].dt.to_period("M")
    monthly_counts = df.groupby("year_month").size()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(monthly_counts.index.astype(str), monthly_counts.values, marker='o', color='darkorange')
    ax.set_xlabel("Month")
    ax.set_ylabel("Number of Trips")
    ax.set_title("Monthly Trip Trend")
    ax.tick_params(axis='x', rotation=45)
    _save_figure(fig, "monthly_trend.png")

# ---------------------------------------------------------------------------
# Histogram — trip duration distribution
# ---------------------------------------------------------------------------
def plot_duration_histogram(trips: pd.DataFrame) -> None:
    durations = trips["duration_minutes"].dropna()
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.hist(durations, bins=30, color="green", edgecolor="black", alpha=0.7)
    ax.set_xlabel("Duration (minutes)")
    ax.set_ylabel("Number of Trips")
    ax.set_title("Distribution of Trip Durations")
    _save_figure(fig, "duration_histogram.png")

# ---------------------------------------------------------------------------
# Box plot — duration by user type
# ---------------------------------------------------------------------------
def plot_duration_by_user_type(trips: pd.DataFrame) -> None:
    """Box plot comparing trip durations across user types."""
    """Box plot comparing trip durations across user types.

    TODO:
        - Group data by user_type
        - Create side-by-side box plots
        - Add title, axis labels
        - Save as 'duration_by_user_type.png'
    """
    df = trips[["user_type", "duration_minutes"]].dropna()
    
    fig, ax = plt.subplots(figsize=(8, 5))
    
    sns.boxplot(
    x="user_type",
    y="duration_minutes",
    data=df,
    palette="Set2",
    hue="user_type", 
    legend=False    )  
    
    ax.set_xlabel("User Type", fontsize=12)
    ax.set_ylabel("Duration (minutes)", fontsize=12)
    ax.set_title("Trip Duration by User Type", fontsize=14)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    
    _save_figure(fig, "duration_by_user_type.png")

