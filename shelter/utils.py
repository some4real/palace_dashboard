from datetime import datetime, time

def get_current_shift():
    now = datetime.now().time()
    if time(7, 0) <= now < time(15, 0):
        return "Morning (7AM - 3PM)"
    elif time(15, 0) <= now < time(23, 0):
        return "Evening (3PM - 11PM)"
    else:
        return "Overnight (11PM - 7AM)"
