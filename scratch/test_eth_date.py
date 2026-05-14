from ethiopian_date import EthiopianDateConverter
import datetime

today = datetime.date.today()
print(f"Gregorian: {today}")

eth_date = EthiopianDateConverter.to_ethiopian(today.year, today.month, today.day)
print(f"Ethiopian: {eth_date}")

months = [
    "መስከረም", "ጥቅምት", "ህዳር", "ታህሳስ", "ጥር", "የካቲት",
    "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"
]
month_name = months[eth_date[1]-1]
print(f"Formatted: {month_name} {eth_date[2]}, {eth_date[0]}")
