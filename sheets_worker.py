from scheduler import Scheduler
import datetime as dt
import time
import gspread
from data import UsersInfo


class Sheets:
    def __init__(self, users_info: UsersInfo = None):
        self.users_info = users_info
        self.sh = gspread.service_account(filename="spatial-flag-367222-d4d647987359.json").open("AverageTime")

    def worker(self):
        wkh = self.sh.worksheet("Sheet")
        time_now = dt.datetime.now(tz=dt.timezone(dt.timedelta(hours=3)))
        wkh.add_cols(cols=1)
        wkh.update(
            f"R1C{wkh.col_count}",
            f"{'0' + str(time_now.day) if len(str(time_now.date())) == 1 else time_now.day}.{'0' + str(time_now.month) if len(str(time_now.month)) == 1 else time_now.month}"
        )
        for user in self.users_info.users:
            if user.messages_difference:
                average_time = int(sum(user.messages_difference) / len(user.messages_difference))
                if user_cell := wkh.find(user.full_name):
                    wkh.update(f"R{user_cell.row}C{wkh.col_count}", average_time)
                else:
                    wkh.add_rows(rows=1)
                    wkh.update(f"R{wkh.row_count}C1", user.full_name)
                    wkh.update(f"R{wkh.row_count}C{wkh.col_count}", average_time)
        self.users_info.users = []

    def start(self):
        schedule = Scheduler(tzinfo=dt.timezone.utc)
        tz_moscow = dt.timezone(dt.timedelta(hours=3))
        schedule.daily(dt.time(hour=23, minute=55, tzinfo=tz_moscow), self.worker)
        while True:
            schedule.exec_jobs()
            time.sleep(1)
