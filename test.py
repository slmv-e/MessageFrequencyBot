from sheets_worker import Sheets
from data import UsersInfo, User

sh = Sheets(
    UsersInfo(
        [
            User(
                id=123,
                full_name="123 123",
                last_time=1,
                messages_difference=[1, 2, 3]
            ),
            User(
                id=123,
                full_name="234 123",
                last_time=1,
                messages_difference=[1, 2, 3]
            )
        ]
    )
)

sh.worker()