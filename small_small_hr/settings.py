"""
Configurable options
"""
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
