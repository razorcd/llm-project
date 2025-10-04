# courier age in years heper method
from datetime import datetime
import time
DAYS_IN_YEAR = 365.2425
SECONDS_IN_YEAR = 60 * 60 * 24 * DAYS_IN_YEAR

def get_age_by_birthdate(birthdate):    
    birth_seconds = datetime.strptime(birthdate, "%Y-%m-%d").timestamp()
    current_seconds = time.time()
    age_in_seconds = current_seconds - birth_seconds
    return int(age_in_seconds / SECONDS_IN_YEAR)