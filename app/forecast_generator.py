import numpy as np
import pandas as pd
from sqlalchemy import func, extract
from app import db
from app.models import LecturerSubject, Lecturer

def get_lecturer_forecast(years_ahead=3):
    """
    Forecast the number of part-time lecturers needed per department using Linear Regression.
    Based on subject loads and teaching hours.
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

    # ---- Step 3: Forecast per department ----
    forecasts = {}
    for dept_id, group in df.groupby("department_id"):
        X = group[["total_subjects", "total_hours"]].values
        y = group["lecturers_needed"].values

        # Add intercept
        X_b = np.c_[np.ones((X.shape[0], 1)), X]
        theta = np.linalg.pinv(X_b.T.dot(X_b)).dot(X_b.T).dot(y)

        # Get last values
        last_subjects = group["total_subjects"].iloc[-1]
        last_hours = group["total_hours"].iloc[-1]
        last_year = int(group["year"].iloc[-1])

        # Assume +5% growth per year
        future_subjects = [last_subjects * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_hours = [last_hours * (1.05 ** i) for i in range(1, years_ahead + 1)]
        future_years = [last_year + i for i in range(1, years_ahead + 1)]

        future_X = np.c_[np.ones((len(future_years), 1)), np.column_stack([future_subjects, future_hours])]
        preds = future_X.dot(theta)

        # Store forecast
        forecasts[dept_id] = {
            "history": group.to_dict(orient="records"),
            "forecast": [
                {"year": year, "lecturers_needed": int(round(p))}
                for year, p in zip(future_years, preds)
            ]
        }

    return forecasts
