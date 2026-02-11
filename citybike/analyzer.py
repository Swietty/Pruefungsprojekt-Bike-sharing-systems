import pandas as pd
from pathlib import Path
import numpy as np

DATA_DIR = Path(__file__).resolve().parent / "data"

class DataAnalyzer:
    """
    Responsible for loading, cleaning, and exporting bike-sharing datasets.
    """

    def __init__(self, output_dir: str = "output") -> None:
        """Initialize the data analyzer.
        
        Args:
            output_dir: Folder to save reports (default is "output")
        """
        # DATA STORAGE - three tables for three data types
        self.trips: pd.DataFrame | None = None  # Trips table (loaded later)
        self.stations: pd.DataFrame | None = None  # Stations table (loaded later)
        self.maintenance: pd.DataFrame | None = None  # Maintenance table (loaded later)

        # PATH FOR SAVING REPORTS
        self.OUTPUT_DIR = Path(output_dir)  # Reports will be saved here

    # ============================================================
    # DATA LOADING
    # ============================================================

    def load_data(self) -> None:
        """Load all CSV files into memory as DataFrames.
        
        Reads three CSV files from the data/ folder:
        - trips.csv - anonymous trip data
        - stations.csv - station information
        - maintenance.csv - maintenance history
        
        Note:
            After loading, the data is NOT cleaned!
            You need to call _clean_trips() to clean it.
        """
        # Load trips table (the largest table)
        self.trips = pd.read_csv(DATA_DIR / "trips.csv")
        # Load stations table (static data)
        self.stations = pd.read_csv(DATA_DIR / "stations.csv")
        # Load maintenance table
        self.maintenance = pd.read_csv(DATA_DIR / "maintenance.csv")

    # ============================================================
    # DATA CLEANING
    # ============================================================

    def _clean_trips(self) -> None:
        """Clean the trips table from dirty data.       
        """
        # Create a copy so as not to spoil the original
        df = self.trips.copy()
        
        # STEP 1: Remove duplicate rows (duplicate trips)
        df = df.drop_duplicates(subset=["trip_id"])
        
        # STEP 2: Convert strings like "2024-01-01 10:30" to datetime objects
        # errors="coerce" = if can't parse - make NaT (Not a Time)
        df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
        df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")
        
        # STEP 3: Convert numbers stored as strings ("25.5" or "25,5")
        # Logic: convert to string → replace comma with dot → strip spaces → parse as number
        for col in ["duration_minutes", "distance_km"]:
            df[col] = pd.to_numeric(
                df[col].astype(str)  # Convert column to str (in case it's a number)
                       .str.replace(",", ".")  # Replace comma with dot (locale issue)
                       .str.strip(),  # Remove leading/trailing spaces
                errors="coerce",  # If can't parse - make NaN (Not a Number)
            )

        # STEP 4: Fill missing values (NaN) with MEDIAN
        # Median is more robust to outliers than mean
        # Example: if data = [1, 2, 3, 1000], then
        #         mean = 251.5 (wrong!)
        #         median = 2.5 (correct!)
        df["duration_minutes"] = df["duration_minutes"].fillna(df["duration_minutes"].median())
        df["distance_km"] = df["distance_km"].fillna(df["distance_km"].median())
        # Missing statuses - assume the trip is completed
        df["status"] = df["status"].fillna("completed")

        # STEP 5: REMOVE INVALID RECORDS
        # If end is before or equal to start - it's an invalid trip
        # Keep only rows where end_time > start_time
        df = df[df["end_time"] > df["start_time"]]

        # STEP 6: STANDARDIZE CATEGORIES
        # "Completed", "COMPLETED", "completed" should all be the same
        # Convert everything to lowercase and strip spaces
        for col in ["status", "user_type", "bike_type"]:
            df[col] = df[col].str.lower().str.strip()

        # STEP 6.5: FILL EMPTY USER_NAME VALUES
        # Some datasets do not contain the `user_name` column.
        # If the column doesn't exist - create it from `user_id`.
        # If it exists, fill empty rows with "Anonymous_" + user_id
        if "user_name" not in df.columns:
            df["user_name"] = "Anonymous_" + df["user_id"].astype(str)
        else:
            empty_names_mask = df["user_name"].isna() | (df["user_name"].str.strip() == "")
            df.loc[empty_names_mask, "user_name"] = "Anonymous_" + df.loc[empty_names_mask, "user_id"].astype(str)

        # STEP 7: SAVE CLEANED DATA
        self.trips = df

    # ============================================================
    # ANALYSIS METHODS - BUSINESS QUESTIONS
    # ============================================================
    # 
    # These are 14 methods that answer different business questions:
    # - How many trips were there?
    # - What are the peak usage hours?
    # - Which bikes need maintenance?
    # - Who are the most active users?
    # - Etc.
    #
    # ✅ NOTE: The assignment required 10+ analysis methods!
    # You have 16 methods (even more than required!) 🏆
    #

    def total_trips_summary(self) -> dict:
        """QUESTION: How many total trips were there and how many km?
        
        Business meaning:
        - Need to know total business volume
        - What's the average trip duration?
        
        Returns:
            dict with three numbers:
            - total_trips: number of trips
            - total_distance_km: sum of distances of all trips
            - avg_duration_min: average trip duration
        """
        df = self.trips
        return {
            "total_trips": len(df),  # Number of rows = number of trips
            "total_distance_km": round(df["distance_km"].sum(), 2),  # Sum of all distances
            "avg_duration_min": round(df["duration_minutes"].mean(), 2),  # Average time
        }

    def top_start_stations(self, n: int = 10) -> pd.DataFrame:
        """QUESTION: Top N DEPARTURE stations (where do people get bikes from)?
        
        Business meaning:
        - Most popular stations for trip start
        - Need to know where to place more bikes
        - Where to build new stations?
        
        Logic:
        1. Count how many times each station was start_station_id
        2. Take top N
        3. Join station names from self.stations table
        4. Return pretty table with names
        
        Args:
            n: How many top-stations to return (default 10)
        
        Returns:
            DataFrame with three columns: station_id, station_name, trip_count
        """
        # Count how many times each station is used as start station
        counts = self.trips["start_station_id"].value_counts().head(n).reset_index()
        # Rename columns to understand what this is
        counts.columns = ["station_id", "trip_count"]
        # Add station names from self.stations reference table
        # (merge = SQL LEFT JOIN, joins on station_id)
        return counts.merge(self.stations, on="station_id", how="left")[["station_id", "station_name", "trip_count"]]

    def top_end_stations(self, n: int = 10) -> pd.DataFrame:
        """QUESTION: Top N DESTINATION stations (where are bikes returned to)?
        
        Business meaning:
        - Most popular stations for trip end
        - Where do bikes accumulate?
        - Where might there be dock shortages?
        
        Logic: Same as top_start_stations() but for end_station_id
        
        Args:
            n: How many top-stations to return (default 10)
        
        Returns:
            DataFrame with three columns: station_id, station_name, trip_count
        """
        # Count how many times each station is used as final station
        counts = self.trips["end_station_id"].value_counts().head(n).reset_index()
        # Rename columns
        counts.columns = ["station_id", "trip_count"]
        # Add station names
        return counts.merge(self.stations, on="station_id", how="left")[["station_id", "station_name", "trip_count"]]

    def peak_usage_hours(self) -> pd.Series:
        """QUESTION: What hours of the day have peak system load?
        
        Business meaning:
        - When are bikes in shortage? (rush hour)
        - When is demand low? (night time)
        - When do we need technical support?
        - When to schedule maintenance?
        
        Logic:
        1. Extract hour from datetime (10:30 → 10)
        2. Group trips by hour
        3. Count how many trips in each hour
        4. Return the distribution
        
        Returns:
            Series where index is hour (0-23) and values are trip counts
            
        Example:
            peak_usage_hours()
            Output:
            0    5   (5 trips in 00:00-01:00)
            1    3
            8    150  ← peak hours in the morning!
            9    200
            17   180  ← peak hours in the evening!
        """
        # Create a copy to avoid spoiling the original data
        df = self.trips.copy()
        # Extract the hour part (0-23) from datetime
        df["hour"] = df["start_time"].dt.hour
        # Count trips in each hour
        return df.groupby("hour").size()

    def busiest_day_of_week(self) -> pd.Series:
        """QUESTION: Which day of the week is the busiest (Monday, Tuesday, ...)?
        
        Business meaning:
        - Weekends vs weekdays?
        - Which days to do maintenance on stations?
        - Which days to hire more staff?
        
        Logic: Same as peak_usage_hours but for days of the week
        
        Returns:
            Series where index is day of week (Monday, Tuesday, ...)
            and values are trip counts
            Sorting: descending (busiest day first)
        """
        df = self.trips.copy()
        # Get the day of week name ("Monday", "Tuesday", ...)
        df["weekday"] = df["start_time"].dt.day_name()
        # Count and sort in descending order
        return df.groupby("weekday").size().sort_values(ascending=False)

    def avg_distance_by_user_type(self) -> pd.Series:
        """QUESTION: Guests vs Members - who rides farther?
        
        Business meaning:
        - Which user group is more active?
        - Are members needed for long trips?
        - Should we change prices for different groups?
        
        Logic:
        1. Group trips by user type
        2. Calculate average distance in each group
        3. Round to 2 decimal places
        
        Returns:
            Series where index is user_type (casual, member)
            and values are average distance (km)
        """
        # Group by user_type and find average distance_km
        return self.trips.groupby("user_type")["distance_km"].mean().round(2)

    def avg_duration_by_user_type(self) -> pd.Series:
        """QUESTION: Guests vs Members - who rides longer?
        
        Business meaning:
        - Do members keep bikes longer?
        - Do we need a penalty system for long trips?
        
        Logic: Same as avg_distance_by_user_type but for duration_minutes
        
        Returns:
            Series where index is user_type (casual, member)
            and values are average time (minutes)
        """
        return self.trips.groupby("user_type")["duration_minutes"].mean().round(2)

    def monthly_trip_trend(self) -> pd.Series:
        """QUESTION: Trip trend by month (is the business growing?)?
        
        Business meaning:
        - Demand seasonality?
        - Was there growth/decline after marketing campaign?
        - Forecast for next month?
        
        Logic:
        1. Group dates by month (2024-01, 2024-02, ...)
        2. Count trips in each month
        
        Returns:
            Series where index is year-month (Period objects)
            and values are trip counts in that month
        """
        df = self.trips.copy()
        # Convert date to Period (2024-01-15 → 2024-01)
        df["year_month"] = df["start_time"].dt.to_period("M")
        # Count trips by month
        return df.groupby("year_month").size()

    def top_active_users(self, n: int = 15) -> pd.DataFrame:
        """QUESTION: Who are the top N most active users?
        
        Business meaning:
        - VIP users (most loyal)?
        - Friendly discounts/rewards for active users?
        - Who should be brand ambassador?
        
        Logic:
        1. Group trips by user_id
        2. Count trips for each user
        3. Sort (most trips first)
        4. Take top N
        
        Args:
            n: How many top-users (default 15)
        
        Returns:
            DataFrame with two columns: user_id, trip_count
        """
        return (
            self.trips.groupby("user_id")  # Group by user
                     .size()  # Count rows in each group
                     .sort_values(ascending=False)  # Sort (largest first)
                     .head(n)  # Take top N
                     .reset_index(name="trip_count")  # Convert to DataFrame
        )

    def maintenance_cost_by_bike_type(self) -> pd.Series:
        """QUESTION: How much money was spent on maintenance for each bike type?
        
        Business meaning:
        - Which bikes are expensive to maintain?
        - Electric vs classic - which is more profitable?
        - Should we remove a certain type from our fleet?
        
        Logic:
        1. Group maintenance data by bike type
        2. Sum expenses (SUM not average!)
        
        Returns:
            Series where index is bike_type (classic, electric)
            and values are total costs
        """
        # Group maintenance data by bike_type and sum cost
        return self.maintenance.groupby("bike_type")["cost"].sum().round(2)

    def top_routes(self, n: int = 10) -> pd.DataFrame:
        """QUESTION: Top N most popular routes (A→B)?
        
        Business meaning:
        - Are there systematic routes (station A → station B)?
        - Can we optimize bike placement?
        - Which routes need more people for bike redistribution?
        
        Logic:
        1. Group trips by pair (start_station, end_station)
        2. Count trips for each route
        3. Find top N
        
        Args:
            n: How many routes to return (default 10)
        
        Returns:
            DataFrame with three columns: start_station_id, end_station_id, trip_count
        """
        routes = (
            self.trips.groupby(["start_station_id", "end_station_id"])  # Pairs of stations
                     .size()  # Count trips for each pair
                     .sort_values(ascending=False)  # Sort
                     .head(n)  # Take top N
                     .reset_index(name="trip_count")  # To DataFrame
        )
        return routes

    def bike_utilization_rate(self) -> float:
        """QUESTION: What % of time do bikes spend in use on average?
        
        Business meaning:
        - Do 80% of bikes sit idle at a station?
        - Do we need to stimulate demand?
        - Is the fleet too large?
        
        Logic:
        - Bike is being used: time when it is in a trip
        - Available time: time from first to last trip
        - Coefficient = used / available * 100%
        
        Formula:
        1. total_time = sum of all (end_time - start_time)
        2. n_bikes = count of unique bikes
        3. total_possible = n_bikes × (max_date - min_date)
        4. rate = (total_time / total_possible) * 100%
        
        Returns:
            float: utilization percentage (0-100%)
        """
        # Calculate sum of all usage time across all trips (in hours)
        total_time = (self.trips["end_time"] - self.trips["start_time"]).sum().total_seconds() / 3600
        # Count unique bikes
        n_bikes = self.trips["bike_id"].nunique()
        # Calculate potential maximum time (if all bikes worked 24/7)
        # (number of bikes × time period)
        total_possible = n_bikes * (self.trips["end_time"].max() - self.trips["start_time"].min()).total_seconds() / 3600
        # Return percentage
        return round((total_time / total_possible) * 100, 2)

    def trip_completion_rate(self) -> dict:
        """QUESTION: How many trips are completed vs cancelled?
        
        Business meaning:
        - App issues? (many cancellations = bad)
        - Equipment issues? (broken bikes = cancellations)
        - Service quality
        
        Logic:
        1. Count trips with "completed" status
        2. Count trips with "cancelled" status
        3. Calculate percentage
        
        Returns:
            dict with three values:
            - completed: count of completed trips
            - cancelled: count of cancelled trips  
            - completion_rate_%: percentage completed (0-100)
        """
        # Count statuses
        counts = self.trips["status"].value_counts()
        # Safely get values (if no "cancelled" - take 0)
        completed = counts.get("completed", 0)
        cancelled = counts.get("cancelled", 0)
        total = completed + cancelled
        # Return results
        return {
            "completed": completed,
            "cancelled": cancelled,
            "completion_rate_%": round((completed / total) * 100, 2) if total > 0 else 0
        }

    def avg_trips_per_user(self) -> pd.Series:
        """QUESTION: On average, how many trips per user (by types)?
        
        Business meaning:
        - Are members more active?
        - Do guests do 1 trip and leave?
        - Is it worth investing in attracting members?
        
        Logic: Group by user_type and find average number of trips
        
        Returns:
            Series where index is user_type (casual, member)
            and values are average number of trips per user
        """
        return (
            self.trips.groupby("user_type")["user_id"]  # Group
                     .value_counts()  # Count how many trips each user has
                     .groupby(level=0)  # Group back by user_type
                     .mean()  # Average
                     .round(2)  # Round
        )

    def bikes_highest_maintenance(self, n: int = 10) -> pd.DataFrame:
        """QUESTION: Top N bikes that are most frequently in maintenance?
        
        Business meaning:
        - Which bikes are unreliable?
        - Should we replace them?
        - Manufacturing quality issues?
        
        Logic:
        1. Group maintenance records by bike_id
        2. Count how many times each bike was serviced
        3. Take top N
        
        Args:
            n: How many bikes to show (default 10)
        
        Returns:
            DataFrame with two columns: bike_id, maintenance_count
        """
        # Count how many times each bike is in self.maintenance
        counts = self.maintenance["bike_id"].value_counts().head(n).reset_index()
        # Rename columns
        counts.columns = ["bike_id", "maintenance_count"]
        return counts

    def detect_outlier_trips(self, z_thresh: float = 3.0) -> pd.DataFrame:
        """QUESTION: Which trips are abnormal/anomalous?
        
        Business meaning:
        - Fraud? (very long trip without end)
        - Data error? (bike: 1000 km per hour?)
        - Need to check?
        
        Logic (Z-SCORE METHOD FOR OUTLIER DETECTION):
        1. Calculate standard deviation
        2. For each trip calculate its "z-score"
           z = (value - mean) / std_dev
        3. If |z| > threshold (3.0) - it's an outlier/anomaly
        4. Return all anomalous trips
        
        Z-score explanation:
        - z = 0: trip is normal (at average value!)
        - z = 1: trip slightly above average
        - z = 3: trip is 3 standard deviations away!
        - z > 3: this is VERY unusual (only 0.1% of normal data is this far)
        
        Args:
            z_thresh: Threshold (default 3.0, needs > 3 standard deviations)
        
        Returns:
            DataFrame with all anomalous trips
        """
        df = self.trips.copy()
        # Calculate z-score for trip duration
        df["duration_z"] = (df["duration_minutes"] - df["duration_minutes"].mean()) / df["duration_minutes"].std()
        # Calculate z-score for distance
        df["distance_z"] = (df["distance_km"] - df["distance_km"].mean()) / df["distance_km"].std()
        # Find trips where EITHER duration OR distance is anomalous
        outliers = df[(df["duration_z"].abs() > z_thresh) | (df["distance_z"].abs() > z_thresh)]
        return outliers

    # ============================================================
    # REPORT GENERATION
    # ============================================================

    def generate_summary_report(self) -> None:
        """CREATE PRETTY TEXT REPORT with all analysis results.
        
        This is the main method which:
        1. Calls all 14 other analysis methods
        2. Formats results into a pretty text report
        3. Saves to file summary_report.txt
        
        Output format:
        ```
        ============================================================
          CityBike — Analytics Summary Report
        ============================================================
        
        --- Q1: Overall Summary ---
        Total trips        : 12345
        Total distance     : 56789.12 km
        ...
        
        --- Q2: Top 10 Start Stations ---
        station_id  station_name      trip_count
        1           Central Park      1234
        ...
        ```
        
        File is saved to self.OUTPUT_DIR / "summary_report.txt"
        """
        # Create output folder if it doesn't exist
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        # Path where to save the report
        report_path = self.OUTPUT_DIR / "summary_report.txt"

        # REPORT LINES - collect them in a list then write to file
        lines: list[str] = [
            "=" * 60,
            "  CityBike — Analytics Summary Report",
            "=" * 60,
        ]

        # Q1: Overall statistics
        summary = self.total_trips_summary()
        lines += [
            "\n--- Q1: Overall Trip Statistics ---",
            f"Total trips       : {summary['total_trips']}",
            f"Total distance    : {summary['total_distance_km']} km",
            f"Average duration  : {summary['avg_duration_min']} min",
        ]

        # Q2: Top start and end stations
        lines += ["\n--- Q2: Top 10 Start Stations ---", self.top_start_stations().to_string(index=False)]
        lines += ["\n--- Q2: Top 10 End Stations ---", self.top_end_stations().to_string(index=False)]

        # Q3: Peak hours
        lines += ["\n--- Q3: Usage by Hour of Day ---", self.peak_usage_hours().to_string()]

        # Q4: Busiest days of week
        lines += ["\n--- Q4: Busiest Days of Week ---", self.busiest_day_of_week().to_string()]

        # Q5: Distance by user types
        lines += ["\n--- Q5: Average Distance by User Type ---", self.avg_distance_by_user_type().to_string()]

        # Q6: Bike utilization
        lines += [f"\n--- Q6: Bike Utilization Rate --- {self.bike_utilization_rate()} %"]

        # Q7: Trend by month
        lines += ["\n--- Q7: Trip Trend by Month ---", self.monthly_trip_trend().to_string()]

        # Q8: Most active users
        lines += ["\n--- Q8: Top 15 Most Active Users ---", self.top_active_users().to_string(index=False)]

        # Q9: Maintenance costs by bike type
        lines += ["\n--- Q9: Maintenance Costs by Bike Type ---", self.maintenance_cost_by_bike_type().to_string()]

        # Q10: Most popular routes
        lines += ["\n--- Q10: Top 10 Most Popular Routes ---", self.top_routes().to_string(index=False)]

        # Q11: Trip completion rate
        lines += ["\n--- Q11: Trip Completion Rate ---", str(self.trip_completion_rate())]

        # Q12: Average trips per user
        lines += ["\n--- Q12: Average Trips per User by Type ---", self.avg_trips_per_user().to_string()]

        # Q13: Bikes with most maintenance
        lines += ["\n--- Q13: Bikes with Highest Maintenance Frequency ---", self.bikes_highest_maintenance().to_string(index=False)]

        # Q14: Detected anomalous trips
        outliers = self.detect_outlier_trips()
        lines += [f"\n--- Q14: Detected Anomalous Trips --- {len(outliers)} found"]

        # SAVE REPORT to disk
        report_path.write_text("\n".join(lines), encoding="utf-8")
        print(f"[OK] Report saved to {report_path}")
