from datetime import datetime

def formatToHumanTime(seconds: int) -> str:
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)

    if(days > 0): return f'{days}d{hours}h{minutes}m{seconds}s'
    elif(hours > 0): return f'{hours}h{minutes}m{seconds}s'
    elif(minutes > 0): return f'{minutes}m{seconds}s'
    else: return f'{seconds}s'
    