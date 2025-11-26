from datetime import datetime

def generate_request_number(city, count):
    now = datetime.now()
    city_code = city[:3].upper()
    fy_code = f"{now.year % 100}/{(now.year + 1) % 100}"
    return f"{city_code}-{count:03}-{fy_code}"
