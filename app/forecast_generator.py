import csv, os, numpy as np, pandas as pd

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

def get_lecturer_forecast(years_ahead=3, history_years=3):
    """
    Forecast the number of part-time lecturers needed per department using Linear Regression.
    - Uses all available history for training
    - Only last `history_years` years shown in "history"
    - actual_lecturers = unique count of lecturer_id per department-year (real headcount)
    - Rule (max 4 subjects per lecturer per semester) still applied for forecast
    """

    csv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files", "lecturer_subject_history.csv")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return {"error": f"CSV file not found at {csv_path}"}

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

    df["year"] = pd.to_datetime(df["start_date"], errors="coerce").dt.year

    # ---- Step 1: Calculate total hours ----
    df["total_hours"] = (
        df["total_lecture_hours"] +
        df["total_tutorial_hours"] +
        df["total_practical_hours"] +
        df["total_blended_hours"]
    )

    # ---- Step 2: Aggregate per department-year ----
    grouped = (
        df.groupby(["department_id", "year"])
        .agg(
            actual_lecturers=("lecturer_id", "nunique"),   # real headcount
            total_subjects=("subject_id", "count"),
            total_hours=("total_hours", "sum")
        )
        .reset_index()
    )

    if grouped.empty:
        return {"error": "No lecturer subject history data found"}

    forecasts = {}

    # ---- Step 3: Forecast per department ----
    for dept_id, full_group in grouped.groupby("department_id"):
        full_group = full_group.sort_values("year")

        X = full_group[["total_subjects", "total_hours"]].values
        y = full_group["actual_lecturers"].values   # use real headcount for training

        # History limited for chart display
        display_group = full_group.tail(history_years)

        if len(full_group) < 2:
            forecasts[dept_id] = {
                "history": display_group.to_dict(orient="records"),
                "forecast": [],
                "metrics": {"R2": None, "RMSE": None, "MSE": None, "note": "Not enough data"}
            }
            continue

        # Training = all but last year, Test = last year
        X_train, y_train = X[:-1], y[:-1]
        X_test, y_test = X[-1:], y[-1:]

        # Linear regression (Normal Equation)
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

        # ---- Step 4: Forecast future years (+5% growth in subjects & hours) ----
        last_subjects = full_group["total_subjects"].iloc[-1]
        last_hours = full_group["total_hours"].iloc[-1]
        last_year = int(full_group["year"].iloc[-1])

        future_subjects = [last_subjects * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_hours = [last_hours * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_years = [last_year + i for i in range(1, years_ahead + 1)]

        future_X = np.c_[np.ones((len(future_years), 1)), np.column_stack([future_subjects, future_hours])]
        preds = future_X.dot(theta)

        # Apply 4-subject rule for forecast
        adjusted_preds = []
        for subj, pred in zip(future_subjects, preds):
            min_needed = int(np.ceil(subj / 4))
            adjusted_preds.append(max(int(round(pred)), min_needed))

        forecasts[dept_id] = {
            "history": display_group.to_dict(orient="records"),
            "forecast": [
                {
                    "year": year,
                    "lecturers_needed": val,  # forecasted count
                    "total_subjects": subj,
                    "total_hours": hrs
                }
                for year, val, subj, hrs in zip(future_years, adjusted_preds, future_subjects, future_hours)
            ],
            "metrics": {"R2": r2, "RMSE": rmse, "MSE": mse}
        }

    return forecasts

def get_budget_forecast(years_ahead=3, history_years=3):
    """
    Forecast future budget allocation per department using Linear Regression.
    - Uses all available history for training
    - Only last `history_years` shown in "history"
    - Falls back to moving average if regression fails
    - Forecasts are clamped at >= 0
    """

    csv_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "files", "lecturer_claim_history.csv")

    try:
        df = pd.read_csv(csv_path)
    except FileNotFoundError:
        return {"error": f"CSV file not found at {csv_path}"}

    df = df.astype({"department_id": int, "total_cost": float})
    df["year"] = pd.to_datetime(df["date"], errors="coerce").dt.year

    # ---- Step 1: Aggregate yearly total claims per department ----
    agg = (
        df.groupby(["department_id", "year"])["total_cost"]
        .sum()
        .reset_index()
        .rename(columns={"total_cost": "actual_costs"})
    )

    if agg.empty:
        return {"error": "No claim data found in CSV"}

    forecasts = {}

    # ---- Step 2: Forecast per department ----
    for dept_id, group in agg.groupby("department_id"):
        group = group.sort_values("year")
        all_years = group["year"].values
        all_values = group["actual_costs"].values

        # Show only last N years in history
        display_group = group.tail(history_years)

        if len(all_values) < 2:
            forecasts[dept_id] = {
                "history": display_group.to_dict(orient="records"),
                "forecast": [],
                "metrics": {"R2": None, "RMSE": None, "MSE": None, "note": "Not enough data"}
            }
            continue

        # ---- Training = all but last year, Test = last year ----
        X = all_years.reshape(-1, 1)
        y = all_values
        X_train, y_train = X[:-1], y[:-1]
        X_test, y_test = X[-1:], y[-1:]

        try:
            # Fit linear regression (Normal Equation)
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

            # ---- Multi-year forecast ----
            last_year = int(all_years[-1])
            future_years = [last_year + i for i in range(1, years_ahead + 1)]
            future_X = np.c_[np.ones((len(future_years), 1)), np.array(future_years).reshape(-1, 1)]
            preds = future_X.dot(theta)

            # Clamp negatives
            preds = [max(0, float(p)) for p in preds]

        except Exception as e:
            # Fall back to moving average if regression fails
            avg_val = np.mean(all_values[-min(3, len(all_values)):])
            last_year = int(all_years[-1])
            future_years = [last_year + i for i in range(1, years_ahead + 1)]
            preds = [avg_val for _ in future_years]
            mse, rmse, r2 = None, None, None

        # ---- Save result ----
        forecasts[dept_id] = {
            "history": display_group.to_dict(orient="records"),
            "forecast": [
                {"year": year, "budget_forecast": round(float(p), 2)}
                for year, p in zip(future_years, preds)
            ],
            "metrics": {"R2": r2, "RMSE": rmse, "MSE": mse}
        }

    return forecasts
