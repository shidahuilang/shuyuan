import datetime
import time
import pytz as pytz
from tzlocal import get_localzone
local_tz = get_localzone()
tz = pytz.timezone('Asia/Shanghai')  # 东八区
t = datetime.datetime.fromtimestamp(int(time.time()), tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')
print(t)
print(local_tz)