"""
Configurable options
"""
from django.conf import settings

SSHR_MAX_CARRY_OVER = 10
SSHR_DAY_LEAVE_VALUES = {
    1: 1,  # Monday
    2: 1,  # Tuesday
    3: 1,  # Wednesday
    4: 1,  # Thursday
    5: 1,  # Friday
    6: 0,  # Saturday
    7: 0,  # Sunday
}
SSHR_ALLOW_OVERSUBSCRIBE = True  # allow taking more leave days one has
SSHR_DEFAULT_TIME = 7  # default time of the day for leave
SSHR_FREE_DAYS = [
    {"day": 1, "month": 1},  # New year
    {"day": 1, "month": 5},  # labour day
    {"day": 1, "month": 6},  # Madaraka day
    {"day": 20, "month": 10},  # Mashujaa day
    {"day": 12, "month": 12},  # Jamhuri day
    {"day": 25, "month": 12},  # Christmas
    {"day": 26, "month": 12},  # Boxing day
]  # these are days that are not counted when getting taken leave days
# admins
SSHR_ADMIN_USER_GROUP_NAME = "Human Resource"
# emails
SSHR_ADMIN_NAME = "HR"
SSHR_ADMIN_EMAILS = [settings.DEFAULT_FROM_EMAIL]
SSHR_ADMIN_LEAVE_EMAILS = SSHR_ADMIN_EMAILS
SSHR_ADMIN_OVERTIME_EMAILS = SSHR_ADMIN_EMAILS
# SSHR_LEAVE_PROCESSED_EMAIL_TXT - text of processed leave email
# SSHR_LEAVE_PROCESSED_EMAIL_SUBJ - subject of processed leave email
# SSHR_LEAVE_APPLICATION_EMAIL_TXT - text of leave application email
# SSHR_LEAVE_APPLICATION_EMAIL_SUBJ - subject of leave application email
# SSHR_OVERTIME_PROCESSED_EMAIL_TXT - text of processed overtime email
# SSHR_OVERTIME_PROCESSED_EMAIL_SUBJ - subject of processed overtime email
# SSHR_OVERTIME_APPLICATION_EMAIL_TXT - text of overtime application email
# SSHR_OVERTIME_APPLICATION_EMAIL_SUBJ - subject of overtime application email
