import numpy as np
import pandas as pd
from sqlalchemy import func, extract
from app import db
from app.models import LecturerSubject

def get_lecturer_forecast(years_ahead=3):
    """
    Forecast the number of part-time lecturers needed using Linear Regression.
    Based on subject loads and teaching hours.
    """

    # ---- Step 1: Collect historical data ----
    results = (
        db.session.query(
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
        .group_by(extract('year', LecturerSubject.start_date))
        .order_by(extract('year', LecturerSubject.start_date))
        .all()
    )

    # Convert to DataFrame
    df = pd.DataFrame(results, columns=["year", "lecturers_needed", "total_subjects", "total_hours"])
    if df.empty:
        return {"error": "No lecturer subject data found"}

    # ---- Step 2: Prepare features and target ----
    X = df[["total_subjects", "total_hours"]].values
    y = df["lecturers_needed"].values

    # Add intercept column
    X_b = np.c_[np.ones((X.shape[0], 1)), X]

    # Normal Equation: (XᵀX)^(-1) Xᵀy
    theta = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

    # ---- Step 3: Forecast for future years ----
    last_subjects = df["total_subjects"].iloc[-1]
    last_hours = df["total_hours"].iloc[-1]

    # Assume +5% growth per year
    future_subjects = [last_subjects * (1.05 ** i) for i in range(1, years_ahead + 1)]
    future_hours = [last_hours * (1.05 ** i) for i in range(1, years_ahead + 1)]
    future_years = [int(df["year"].iloc[-1]) + i for i in range(1, years_ahead + 1)]

    future_X = np.c_[np.ones((len(future_years), 1)), np.column_stack([future_subjects, future_hours])]
    preds = future_X.dot(theta)

    # ---- Step 4: Return structured results ----
    forecast = {
        "history": df.to_dict(orient="records"),
        "forecast": [
            {"year": year, "lecturers_needed": round(float(p), 2)}
            for year, p in zip(future_years, preds)
        ]
    }

    return forecast
