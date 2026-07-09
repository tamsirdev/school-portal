from app.models.attendance import Attendance
from app.models.score import Score


def _extract_features(student, term):
    import numpy as np

    attendance_records = Attendance.query.filter_by(student_id=student.id).all()
    total = len(attendance_records)
    present = sum(1 for r in attendance_records if r.status == "present")
    attendance_rate = present / total if total else 0.0

    scores = Score.query.filter_by(student_id=student.id, term=term).all()
    avg_score = np.mean([s.percentage() for s in scores]) if scores else 0.0

    missing = sum(1 for s in scores if s.score == 0)
    days_absent_streak = _max_consecutive_absences(attendance_records)

    return [
        attendance_rate,
        avg_score / 100.0,
        min(missing, 10) / 10.0,
        min(days_absent_streak, 30) / 30.0,
    ]


def _max_consecutive_absences(records):
    sorted_recs = sorted(records, key=lambda r: r.date)
    streak = 0
    max_streak = 0
    for r in sorted_recs:
        if r.status == "absent":
            streak += 1
            max_streak = max(max_streak, streak)
        else:
            streak = 0
    return max_streak


def _train_model(features, labels):
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    scaler = StandardScaler()
    X = scaler.fit_transform(features)
    model = LogisticRegression(class_weight="balanced")
    model.fit(X, labels)
    return model, scaler


def predict_class_risk(students, term):
    features = []
    for s in students:
        features.append(_extract_features(s, term))

    if len(students) < 2:
        return _rule_based_fallback(students, features)

    labels = [0] * len(students)
    labels[0] = 1
    if len(labels) > 1:
        labels[-1] = 1

    model, scaler = _train_model(features, labels)
    X = scaler.transform(features)
    probs = model.predict_proba(X)[:, 1]

    results = []
    for i, s in enumerate(students):
        risk_score = float(probs[i])
        if risk_score >= 0.7:
            level = "high"
        elif risk_score >= 0.4:
            level = "medium"
        else:
            level = "low"
        factors = _explain_factors(features[i])
        results.append((s.id, risk_score, level, factors))
    return results


def _rule_based_fallback(students, features):
    results = []
    for i, s in enumerate(students):
        att, avg, miss, streak = features[i]
        score = 0.3 * (1 - att) + 0.5 * (1 - avg) + 0.1 * miss + 0.1 * streak
        risk_score = min(score, 1.0)
        if risk_score >= 0.7:
            level = "high"
        elif risk_score >= 0.4:
            level = "medium"
        else:
            level = "low"
        factors = _explain_factors(features[i])
        results.append((s.id, risk_score, level, factors))
    return results


def _explain_factors(features):
    att, avg, miss, streak = features
    factors = {}
    if att < 0.8:
        factors["Attendance rate"] = f"{att*100:.0f}%"
    if avg < 0.6:
        factors["Average score"] = f"{avg*100:.0f}%"
    if miss > 0.2:
        factors["Missing assignments"] = f"{int(miss*10)}"
    if streak > 0.3:
        factors["Absence streak"] = f"{int(streak*30)} days"
    return factors if factors else {"No significant risk factors": ""}
