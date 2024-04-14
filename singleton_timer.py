import time

'''
NOTE(jpyo0803): this is not thread safe
'''


class SingletonTimer:
    class TimeStampBegin:
        def __init__(self, tag=None, category=None, ticket=None, time_begin=None, exclude=None):
            self.tag = tag
            self.category = category
            self.ticket = ticket
            self.time_begin = time_begin
            self.exclude = exclude

    class TimeStampEnd:
        def __init__(self, ticket=None, time_end=None):
            self.ticket = ticket
            self.time_end = time_end

    class TimeRecord:
        def __init__(self, tag, category, ticket, time_begin, time_end, exclude):
            self.tag = tag
            self.category = category
            self.ticket = ticket
            self.time_begin = time_begin
            self.time_end = time_end
            self.exclude = exclude

    def __new__(cls, allow_overlap=False):
        if not hasattr(cls, "_instance"):
            print(
                f"Singleton timer is created (allow_overlap: {allow_overlap})")
            cls._instance = super().__new__(cls)
            cls._is_measuring = False
            cls._allow_overlap = allow_overlap
            cls._ticker_counter = 0
            cls._measure_counter = 0

            cls._time_begin_list = []
            cls._time_end_list = []
        return cls._instance

    def __init__(self, allow_overlap=False):
        cls = type(self)
        if not hasattr(cls, "_init"):
            cls._init = True

    @classmethod
    def issue_ticket(cls):
        ticket = cls._ticker_counter
        cls._ticker_counter += 1
        return ticket

    @classmethod
    def start(cls, tag: str, category: str = None, exclude=False, ticket: int = None):
        # NOTE(jpyo0803): when overlapped time measures are not allowed, check it is already measuring
        if not cls._allow_overlap:
            assert not cls._is_measuring
            cls._is_measuring = True
        else:
            cls._measure_counter += 1
        ticket_now = ticket if ticket is not None else cls.issue_ticket()

        ts_begin = SingletonTimer.TimeStampBegin()
        ts_begin.tag = tag
        ts_begin.category = category
        ts_begin.exclude = exclude
        ts_begin.ticket = ticket_now
        ts_begin.time_begin = time.time()

        cls._time_begin_list.append(ts_begin)

        return ticket_now

    @classmethod
    def stop(cls, ticket: int):
        time_end = time.time()
        if not cls._allow_overlap:
            assert cls._is_measuring

        ts_end = SingletonTimer.TimeStampEnd()
        ts_end.ticket = ticket
        ts_end.time_end = time_end

        cls._time_end_list.append(ts_end)

        if not cls._allow_overlap:
            cls._is_measuring = False
        else:
            cls._measure_counter -= 1

    @classmethod
    def 


if __name__ == "__main__":
    timer = SingletonTimer()
    timer2 = SingletonTimer()
    # NOTE(jpyo0803): they must be same
    assert timer is timer2


'''
[Reference]
1. https://wikidocs.net/69361
'''
