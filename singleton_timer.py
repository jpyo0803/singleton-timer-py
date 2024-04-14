import time
from collections import OrderedDict

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

    class CumulTimeRecord:
        def __init__(self):
            self.category = None  # key
            self.cumul_time = 0.0
            self.sum_count = 0

    def __new__(cls, allow_overlap=False):
        if not hasattr(cls, "_instance"):
            print(
                f"Singleton timer is created (allow_overlap: {allow_overlap})")
            cls._instance = super().__new__(cls)
            cls.__allow_overlap = allow_overlap
            cls.__is_measuring = False
            cls.__ticker_counter = 0
            cls.__overlap_counter = 0

            cls.__time_begin_list = []
            cls.__time_end_list = []

            cls.__disable = False

            cls.__time_record_list = []
            cls.__cumul_time_record_od = OrderedDict()
        return cls._instance

    def __init__(self, allow_overlap=False):
        cls = type(self)
        if not hasattr(cls, "__init"):
            cls.__init = True

    @classmethod
    def __issue_ticket(cls):
        ticket = cls.__ticker_counter
        cls.__ticker_counter += 1
        return ticket

    @classmethod
    def start(cls, tag: str, category: str = None, exclude=False, ticket: int = None):
        if cls.__disable:
            return

        # NOTE(jpyo0803): when overlapped time measures are not allowed, check it is already measuring
        if not cls.__allow_overlap:
            assert not cls.__is_measuring, "Overlapped time measures are not allowed"
            cls.__is_measuring = True
        else:
            cls.__overlap_counter += 1
        ticket_now = ticket if ticket is not None else cls.__issue_ticket()

        ts_begin = SingletonTimer.TimeStampBegin()
        ts_begin.tag = tag
        ts_begin.category = category
        ts_begin.exclude = exclude
        ts_begin.ticket = ticket_now

        cls.__time_begin_list.append(ts_begin)

        # NOTE(jpyo0803): Generate star timestamp as late as possible
        cls.__time_begin_list[-1].time_begin = time.time()

        return ticket_now

    @classmethod
    def end(cls, ticket: int):
        if cls.__disable:
            return
        # NOTE(jpyo0803): Generate stop timestamp as soon as possible

        time_end = time.time()
        if not cls.__allow_overlap:
            assert cls.__is_measuring

        ts_end = SingletonTimer.TimeStampEnd()
        ts_end.ticket = ticket
        ts_end.time_end = time_end

        cls.__time_end_list.append(ts_end)

        if not cls.__allow_overlap:
            cls.__is_measuring = False
        else:
            cls.__measure_counter -= 1

    @classmethod
    def __construct_time_record_tree(cls):
        assert len(cls.__time_begin_list) == len(
            cls.__time_end_list), "sizes of time begin/end list do not match"

        # if no elements in time list, no work to do
        if len(cls.__time_begin_list) == 0:
            return

        time_end_od = OrderedDict()  # For fast search
        for e in cls.__time_end_list:
            time_end_od[e.ticket] = e

        # clear time end list
        cls.__time_end_list.clear()

        for x in cls.__time_begin_list:
            try:
                y = time_end_od[x.ticket]
            except:
                assert False, f'Not found tag = {x.tag}, ticket = {x.ticket}'

            tr = SingletonTimer.TimeRecord(tag=x.tag, category=x.category, ticket=x.ticket, time_begin=x.time_begin, time_end=y.time_end, exclude=x.exclude)

            # increasing order is always preserved
            cls.__time_record_list.append(tr)

        # clear time begin list
        cls.__time_begin_list.clear()

    @classmethod
    def display_log(cls):
        cls.__construct_time_record_tree()

        # This will simply print out all the time records
        for tr in cls.__time_record_list:
            if not tr.exclude:
                print(f'Tag: {tr.tag}, Category: {tr.category}, Ticket: {tr.ticket}, Begin: {tr.time_begin : 0.6f} s, End: {tr.time_end : 0.6f} s, dt: {tr.time_end - tr.time_begin : 0.6f}')

    @classmethod
    def display_summary(cls):
        cls.__construct_time_record_tree()

    @classmethod
    def disable(cls):
        cls.__disable = True

    @classmethod
    def enable(cls):
        cls.__disable = False


if __name__ == "__main__":
    timer = SingletonTimer()
    timer2 = SingletonTimer()
    # NOTE(jpyo0803): they must be same
    assert timer is timer2


'''
[Reference]
1. https://wikidocs.net/69361
'''
