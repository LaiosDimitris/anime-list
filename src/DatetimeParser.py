import datetime
import pytz

class DatetimeParser:

    def __init__(self) -> None:
        pass

    def getTimeLeftForBroadcast(self, broadcast: str):
        print(f'Raw broadcast: {broadcast}')
        return self.__getBroadcastRemainingTime(broadcast)

    def __getDateOfNextBroadcast(self, dayOfBroadcast: str, time: str):
        days = {'Monday': 0, 'Tuesday': 1, 'Wednesday': 2, 'Thursday': 3, 'Friday': 4, 'Saturday': 5, 'Sunday': 6}
        today = datetime.datetime.now()
        dateOfBroadcast = today
        while dateOfBroadcast.weekday() != days[dayOfBroadcast]:
            dateOfBroadcast += datetime.timedelta(1)
        hourOfBroadcast = int(time.split(':')[0])
        minuteOfBroadcast = int(time.split(':')[1])
        return dateOfBroadcast.replace(hour=hourOfBroadcast, minute=minuteOfBroadcast)

    def __getDateOfNextBroadcastInJpTimezone(self, date: datetime.datetime):
        return date.replace(tzinfo=pytz.timezone('Asia/Tokyo'))

    def __getTimeLeftForBroadcast(self, nextBroadcast: datetime.datetime):
        return str(nextBroadcast - datetime.datetime.now(tz=pytz.timezone('Europe/Athens')))[:-10]

    def __getTimeLeftInReadableFormat(self, timeLeft: str):
        if len(timeLeft.split(', ')) == 1:
            if timeLeft.split(':')[0] == '0':
                return f"{timeLeft.split(':')[1]}m"
            else:
                return f"{timeLeft.split(':')[0]}h {timeLeft.split(':')[1]}m"
        else:
            return f"{timeLeft.split(', ')[0][0]}d {timeLeft.split(', ')[1].split(':')[0]}h {timeLeft.split(', ')[1].split(':')[1]}m"

    def __getBroadcastRemainingTime(self, broadcast: str):
        dayOfBroadcast = broadcast.split()[0][:-1]
        timeOfBroadcast = broadcast.split()[2]
        dateOfNextBroadcast = self.__getDateOfNextBroadcast(dayOfBroadcast, timeOfBroadcast)
        dateOfNextBroadcastInJpTimezone = self.__getDateOfNextBroadcastInJpTimezone(dateOfNextBroadcast)
        timeLeft = self.__getTimeLeftForBroadcast(dateOfNextBroadcastInJpTimezone)
        return self.__getTimeLeftInReadableFormat(timeLeft)

