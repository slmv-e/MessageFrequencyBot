from scheduler import Scheduler
import datetime as dt
import time
import gspread
from data import UsersInfo


class Sheets:
    def __init__(self, users_info: UsersInfo = None):
        self.users_info = users_info
        self.wkh = gspread.service_account(filename="spatial-flag-367222-d4d647987359.json").open("AverageTime").worksheet("Sheet")

    def worker(self):
        time_now = dt.datetime.now(tz=dt.timezone(dt.timedelta(hours=3)))
        self.wkh.update(
            f"R1C{self.wkh.col_count}",
            f"{'0' + str(time_now.day) if len(str(time_now.date())) == 1 else time_now.day}.{'0' + str(time_now.month) if len(str(time_now.month)) == 1 else time_now.month}"
        )
        for user in self.users_info.users:
            if user.messages_difference:
                average_time = int(sum(user.messages_difference) / len(user.messages_difference))
                if user_cell := self.wkh.find(user.full_name):
                    self.wkh.update(f"R{user_cell.row}C{self.wkh.col_count}", average_time)
                else:
                    self.wkh.update(f"R{self.wkh.row_count}C1", user.full_name)
                    self.wkh.update(f"R{self.wkh.row_count}C{self.wkh.col_count}", average_time)
                    self.wkh.add_rows(rows=1)
        self.wkh.add_cols(cols=1)
        self.users_info.users = []

    def start(self):
        schedule = Scheduler(tzinfo=dt.timezone.utc)
        tz_moscow = dt.timezone(dt.timedelta(hours=3))
        schedule.daily(dt.time(hour=23, minute=55, tzinfo=tz_moscow), self.worker)
        while True:
            schedule.exec_jobs()
            time.sleep(1)
