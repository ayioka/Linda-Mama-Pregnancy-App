# pregnancy/utils.py

from datetime import datetime

def calculate_pregnancy_progress(start_date):
    """
    Calculate pregnancy progress (weeks and days) from the start date.
    """
    if not start_date:
        return {"weeks": 0, "days": 0}

    today = datetime.today().date()
    delta = today - start_date
    weeks = delta.days // 7
    days = delta.days % 7

    return {"weeks": weeks, "days": days}
