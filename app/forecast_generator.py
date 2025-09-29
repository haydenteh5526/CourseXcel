from app import db
from app.models import ClaimApproval, Lecturer, LecturerClaim, LecturerSubject, RequisitionApproval
import numpy as np
import pandas as pd
from sqlalchemy import func, extract

def get_lecturer_forecast(years_ahead=3):
    """
    Forecast the number of part-time lecturers needed per department using Linear Regression.
    Includes validation using the last available year as test data.
    Applies a business rule: each lecturer can handle max 4 subjects.
    """

    # ---- Step 1: Collect historical data per department ----
    results = (
        db.session.query(
            Lecturer.department_id.label("department_id"),
            extract('year', LecturerSubject.start_date).label('year'),
            func.count(func.distinct(LecturerSubject.lecturer_id)).label('lecturers_needed'),
            func.count(LecturerSubject.subject_id).label('total_subjects'),
            (
                func.sum(LecturerSubject.total_lecture_hours) +
                func.sum(LecturerSubject.total_tutorial_hours) +
                func.sum(LecturerSubject.total_practical_hours) +
                func.sum(LecturerSubject.total_blended_hours)
            ).label('total_hours')
        )
        .join(Lecturer, Lecturer.lecturer_id == LecturerSubject.lecturer_id)
        .join(RequisitionApproval, LecturerSubject.requisition_id == RequisitionApproval.approval_id)
        .group_by(Lecturer.department_id, extract('year', LecturerSubject.start_date))
        .order_by(Lecturer.department_id, extract('year', LecturerSubject.start_date))
        .all()
    )

    if not results:
        return {"error": "No lecturer subject data found"}

    # ---- Step 2: Convert to DataFrame ----
    df = pd.DataFrame(results, columns=["department_id", "year", "lecturers_needed", "total_subjects", "total_hours"])
    df = df.astype({
        "department_id": int,
        "year": int,
        "lecturers_needed": float,
        "total_subjects": float,
        "total_hours": float
    })

    forecasts = {}
    # ---- Step 3: Process per department ----
    for dept_id, group in df.groupby("department_id"):
        group = group.sort_values("year")
        X = group[["total_subjects", "total_hours"]].values
        y = group["lecturers_needed"].values

        if len(group) < 2:
            forecasts[dept_id] = {
                "history": group.to_dict(orient="records"),
                "forecast": [],
                "metrics": {"R2": None, "RMSE": None, "MSE": None, "note": "Not enough data"}
            }
            continue

        # ---- Split into training (all but last year) and test (last year) ----
        X_train, y_train = X[:-1], y[:-1]
        X_test, y_test = X[-1:], y[-1:]

        # Add intercept
        X_b = np.c_[np.ones((X_train.shape[0], 1)), X_train]
        theta = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y_train)

        # ---- Validation on test set ----
        X_test_b = np.c_[np.ones((X_test.shape[0], 1)), X_test]
        y_pred = X_test_b.dot(theta)

        mse = float(np.mean((y_test - y_pred) ** 2))
        rmse = float(np.sqrt(mse))
        ss_tot = float(np.sum((y_test - np.mean(y_train)) ** 2))
        ss_res = float(np.sum((y_test - y_pred) ** 2))
        r2 = 1 - ss_res / ss_tot if ss_tot > 0 else None

        # ---- Forecast future years ----
        last_subjects = group["total_subjects"].iloc[-1]
        last_hours = group["total_hours"].iloc[-1]
        last_year = int(group["year"].iloc[-1])

        # Assume +5% growth per year
        future_subjects = [last_subjects * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_hours = [last_hours * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_years = [last_year + i for i in range(1, years_ahead + 1)]

        future_X = np.c_[np.ones((len(future_years), 1)), np.column_stack([future_subjects, future_hours])]
        preds = future_X.dot(theta)

        # ---- Apply business rule: max 4 subjects per lecturer ----
        adjusted_preds = []
        for subj, pred in zip(future_subjects, preds):
            min_needed = int(np.ceil(subj / 4))  # at least enough lecturers so no one has >4 subjects
            adjusted_preds.append(max(int(round(pred)), min_needed))

        forecasts[dept_id] = {
            "history": group.to_dict(orient="records"),
            "forecast": [
                {"year": year, "lecturers_needed": val}
                for year, val in zip(future_years, adjusted_preds)
            ],
            "metrics": {"R2": r2, "RMSE": rmse, "MSE": mse}
        }

    return forecasts

def get_budget_forecast(years_ahead=3):
    """
    Forecast future budget allocation per department using a lightweight ARIMA(1,1,1).
    Includes validation using the last available year as test data.
    """

    # ---- Step 1: Aggregate yearly total claims per department ----
    results = (
        db.session.query(
            Lecturer.department_id.label("department_id"),
            extract('year', LecturerClaim.date).label('year'),
            func.sum(LecturerClaim.total_cost).label("total_claims")
        )
        .join(Lecturer, Lecturer.lecturer_id == LecturerClaim.lecturer_id)
        .join(ClaimApproval, LecturerClaim.claim_id == ClaimApproval.approval_id)
        # .filter(ClaimApproval.status == "Completed")  # only completed
        .group_by(Lecturer.department_id, extract('year', LecturerClaim.date))
        .order_by(Lecturer.department_id, extract('year', LecturerClaim.date))
        .all()
    )

    if not results:
        return {"error": "No claim data found"}

    # ---- Step 2: Convert to DataFrame ----
    df = pd.DataFrame(results, columns=["department_id", "year", "total_claims"])
    df = df.astype({"department_id": int, "year": int, "total_claims": float})

    forecasts = {}

    # ---- Step 3: Forecast per department ----
    for dept_id, group in df.groupby("department_id"):
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
