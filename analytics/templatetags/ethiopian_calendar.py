from django import template
from ethiopian_date import EthiopianDateConverter
import datetime

register = template.Library()

@register.filter(name='to_ethiopian')
def to_ethiopian(value):
    if not value:
        return ""
    
    if isinstance(value, datetime.datetime):
        date_obj = value.date()
    elif isinstance(value, datetime.date):
        date_obj = value
    else:
        return value
    
    try:
        eth_date = EthiopianDateConverter.to_ethiopian(date_obj.year, date_obj.month, date_obj.day)
        # Format: DD/MM/YYYY
        return f"{eth_date.day}/{eth_date.month}/{eth_date.year}"
    except Exception:
        return value

@register.filter(name='to_ethiopian_full')
def to_ethiopian_full(value):
    if not value:
        return ""
    
    if isinstance(value, datetime.datetime):
        date_obj = value.date()
    elif isinstance(value, datetime.date):
        date_obj = value
    else:
        return value
        
    months = [
        "መስከረም", "ጥቅምት", "ህዳር", "ታህሳስ", "ጥር", "የካቲት",
        "መጋቢት", "ሚያዝያ", "ግንቦት", "ሰኔ", "ሐምሌ", "ነሐሴ", "ጳጉሜ"
    ]
    
    try:
        eth_date = EthiopianDateConverter.to_ethiopian(date_obj.year, date_obj.month, date_obj.day)
        month_name = months[eth_date.month-1]
        return f"{month_name} {eth_date.day}, {eth_date.year}"
    except Exception:
        return value
