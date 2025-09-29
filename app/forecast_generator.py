import csv, os
import numpy as np
import pandas as pd

def append_to_csv(file_name, fieldnames, row):
    # Base path: same folder where your templates are stored
    folder_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files")
    os.makedirs(folder_path, exist_ok=True)

    file_path = os.path.join(folder_path, file_name)
    file_exists = os.path.isfile(file_path)

    with open(file_path, mode="a", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

def get_lecturer_forecast(years_ahead=3):
    """
    Forecast the number of part-time lecturers needed per department using Linear Regression.
    Reads from lecturer_subject_history.csv instead of DB.
    Applies a business rule: each lecturer can handle max 4 subjects per teaching period (start_date–end_date).
    """

    # Build absolute path to files directory
    csv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files", "lecturer_subject_history.csv")

    # ---- Step 1: Load CSV ----
    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return {"error": f"CSV file not found at {csv_path}"}

    # Ensure correct dtypes
    df = df.astype({
        "lecturer_id": int,
        "department_id": int,
        "subject_id": int,
        "total_lecture_hours": float,
        "total_tutorial_hours": float,
        "total_practical_hours": float,
        "total_blended_hours": float,
        "total_cost": float,
    })

    # Extract year from start_date
    df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year

    # ---- Step 2: Aggregate per department-year, considering teaching periods ----
    # Compute total_hours row-wise first
    df["total_hours"] = (
        df["total_lecture_hours"] +
        df["total_tutorial_hours"] +
        df["total_practical_hours"] +
        df["total_blended_hours"]
    )

    period_group = (
        df.groupby(["department_id", "year", "start_date", "end_date"])
        .agg(
            total_subjects=("subject_id", "count"),
            total_hours=("total_hours", "sum")
        )
        .reset_index()
    )

    # For each teaching period, apply the 4-subjects rule:
    period_group["lecturers_needed"] = np.ceil(period_group["total_subjects"] / 4).astype(int)

    # Subjects per lecturer in this semester
    period_group["subjects_per_lecturer"] = np.ceil(
        period_group["total_subjects"] / period_group["lecturers_needed"]
    ).astype(int)

    # ---- Step 3: Collapse to department-year totals ----
    grouped = (
        period_group.groupby(["department_id", "year"])
        .agg(
            lecturers_needed=("lecturers_needed", "max"),   # headcount per year
            total_subjects=("total_subjects", "sum"),
            total_hours=("total_hours", "sum"),
            max_subjects_per_sem=("subjects_per_lecturer", "max")
        )
        .reset_index()
    )

    if grouped.empty:
        return {"error": "No lecturer subject history data found"}

    forecasts = {}
    # ---- Step 4: Forecast per department ----
    for dept_id, group in grouped.groupby("department_id"):
        group = group.sort_values("year")

        # Keep only last N years of history, where N = years_ahead
        if len(group) > years_ahead:
            group = group.tail(years_ahead)

        X = group[["total_subjects", "total_hours"]].values
        y = group["lecturers_needed"].values

        if len(group) < 2:
            # Add max_subjects_per_lecturer even in this case
            group = group.assign(
                max_subjects_per_lecturer=np.ceil(group["total_subjects"] / group["lecturers_needed"])
            )
            forecasts[dept_id] = {
                "history": group.to_dict(orient="records"),
                "forecast": [],
                "metrics": {"R2": None, "RMSE": None, "MSE": None, "note": "Not enough data"}
            }
            continue

        # Training = all but last year, Test = last year
        X_train, y_train = X[:-1], y[:-1]
        X_test, y_test = X[-1:], y[-1:]

        # Fit Linear Regression (Normal Equation)
        X_b = np.c_[np.ones((X_train.shape[0], 1)), X_train]
        theta = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y_train)

        # Validation
        X_test_b = np.c_[np.ones((X_test.shape[0], 1)), X_test]
        y_pred = X_test_b.dot(theta)

        mse = float(np.mean((y_test - y_pred) ** 2))
        rmse = float(np.sqrt(mse))
        ss_tot = float(np.sum((y_test - np.mean(y_train)) ** 2))
        ss_res = float(np.sum((y_test - y_pred) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None

        # Forecast future years (+5% subjects & hours per year)
        last_subjects = group["total_subjects"].iloc[-1]
        last_hours = group["total_hours"].iloc[-1]
        last_year = int(group["year"].iloc[-1])

        future_subjects = [last_subjects * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_hours = [last_hours * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_years = [last_year + i for i in range(1, years_ahead + 1)]

        future_X = np.c_[np.ones((len(future_years), 1)), np.column_stack([future_subjects, future_hours])]
        preds = future_X.dot(theta)

        # Apply rule: max 4 subjects per lecturer
        adjusted_preds = []
        for subj, pred in zip(future_subjects, preds):
            min_needed = int(np.ceil(subj / 4))
            adjusted_preds.append(max(int(round(pred)), min_needed))

        forecasts[dept_id] = {
            "history": group.to_dict(orient="records"),
            "forecast": [
                {
                    "year": year,
                    "lecturers_needed": val,
                    "total_subjects": subj,
                    "total_hours": hrs
                }
                for year, val, subj, hrs in zip(future_years, adjusted_preds, future_subjects, future_hours)
            ],
            "metrics": {"R2": r2, "RMSE": rmse, "MSE": mse}
        }

    return forecasts

def get_budget_forecast(years_ahead=3):
    """
    Forecast future budget allocation per department using a lightweight ARIMA(1,1,1).
    Reads from lecturer_claim_history.csv instead of querying DB.
    Includes validation using the last available year as test data.
    """

    # Build absolute path to files directory
    csv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files", "lecturer_claim_history.csv")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return {"error": f"CSV file not found at {csv_path}"}

    # Ensure correct dtypes
    df = df.astype({
        "department_id": int,
        "lecturer_id": int,
        "claim_id": int,
        "subject_id": float,  # can have NULL
        "total_cost": float
    })
    df["year"] = pd.to_datetime(df["date"]).dt.year

    # ---- Step 1: Aggregate yearly total claims per department ----
    agg = (
        df.groupby(["department_id", "year"])["total_cost"]
        .sum()
        .reset_index()
        .rename(columns={"total_cost": "total_claims"})
    )

    if agg.empty:
        return {"error": "No claim data found in CSV"}

    forecasts = {}

    # ---- Step 2: Forecast per department ----
    for dept_id, group in agg.groupby("department_id"):
        values = group["total_claims"].values
        years = group["year"].values

        if len(values) < 3:  # not enough history
            forecasts[dept_id] = {
                "history": group.to_dict(orient="records"),
                "forecast": [],
                "metrics": {"R2": None, "RMSE": None, "MSE": None, "note": "Not enough data"}
            }
            continue

        # ---- Train/test split ----
        train_values = values[:-1]
        test_value = values[-1]
        test_year = int(years[-1])

        # Differencing (d=1)
        diff = np.diff(train_values)

        # ARIMA(1,1,1)-like coefficients
        phi = 0.5
        theta = 0.5

        last_val = train_values[-1]
        last_diff = diff[-1]
        last_err = 0

        # Forecast next year (the test year)
        diff_forecast = phi * last_diff + theta * last_err
        forecast_val = last_val + diff_forecast

        # ---- Validation metrics ----
        y_true = np.array([test_value])
        y_pred = np.array([forecast_val])

        mse = float(np.mean((y_true - y_pred) ** 2))
        rmse = float(np.sqrt(mse))
        ss_tot = float(np.sum((y_true - np.mean(train_values)) ** 2))
        ss_res = float(np.sum((y_true - y_pred) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None

        # ---- Multi-year forecast ----
        preds = []
        future_years = [test_year + i for i in range(1, years_ahead + 1)]

        last_val = forecast_val
        last_diff = diff_forecast
        last_err = 0

        for _ in range(years_ahead):
            diff_forecast = phi * last_diff + theta * last_err
            forecast_val = last_val + diff_forecast
            preds.append(forecast_val)

            last_err = diff_forecast - last_diff
            last_diff = diff_forecast
            last_val = forecast_val

        # ---- Save result ----
        forecasts[dept_id] = {
            "history": group.to_dict(orient="records"),
            "forecast": [
                {"year": year, "budget_forecast": round(float(p), 2)}
                for year, p in zip(future_years, preds)
            ],
            "metrics": {"R2": r2, "RMSE": rmse, "MSE": mse}
        }

    return forecasts
