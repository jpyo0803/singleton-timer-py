import time
from collections import OrderedDict
from enum import Enum

'''
NOTE(jpyo0803): this is not thread safe
'''


class SingletonTimer:
    class TimerSource(Enum):
        Time = 0,
        PerfCounter = 1,
        PerfCounterNs = 2,

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
            self.max_time = 0.0
            self.min_time = 1e18

    def __new__(cls, allow_overlap=False):
        if not hasattr(cls, "_instance"):
            print(
                f"Singleton timer is created (allow_overlap: {allow_overlap})")
            cls._instance = super().__new__(cls)

            cls.__allow_overlap = allow_overlap
            cls.set_time_source(SingletonTimer.TimerSource.PerfCounterNs)
            cls.reset()
        return cls._instance

    def __init__(self, allow_overlap=False):
        cls = type(self)
        if not hasattr(cls, "__init"):
            cls.__init = True

    @classmethod
    def __issue_ticket(cls):
        ticket = cls.__ticket_counter
        cls.__ticket_counter += 1
        return ticket

    @classmethod
    def start(cls, tag: str, category: str, exclude=False, ticket: int = None):
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
        cls.__time_begin_list[-1].time_begin = cls.__get_time_stamp()

        return ticket_now

    @classmethod
    def end(cls, ticket: int):
        if cls.__disable:
            return
        # NOTE(jpyo0803): Generate stop timestamp as soon as possible

        time_end = cls.__get_time_stamp()
        if not cls.__allow_overlap:
            assert cls.__is_measuring

        ts_end = SingletonTimer.TimeStampEnd()
        ts_end.ticket = ticket
        ts_end.time_end = time_end

        cls.__time_end_list.append(ts_end)

        if not cls.__allow_overlap:
            cls.__is_measuring = False
        else:
            cls.__overlap_counter -= 1

    @classmethod
    def __construct_time_record(cls):
        assert len(cls.__time_begin_list) == len(
            cls.__time_end_list), "sizes of time begin/end list do not match"

        const_begin_time = cls.__get_time_stamp()
        proc_num = len(cls.__time_begin_list)
        # if no elements in time list, no work to do
        if len(cls.__time_begin_list) == 0:
            return

        time_end_od = OrderedDict()  # For fast search
        for e in cls.__time_end_list:
            time_end_od[e.ticket] = e

        # clear time end list
        cls.__time_end_list.clear()

        for x in cls.__time_begin_list:
            if not x.ticket in time_end_od:
                assert False, f'Not found tag = {x.tag}, ticket = {x.ticket}'
            y = time_end_od[x.ticket]

            tr = SingletonTimer.TimeRecord(tag=x.tag, category=x.category, ticket=x.ticket,
                                           time_begin=x.time_begin, time_end=y.time_end, exclude=x.exclude)

            # increasing order is always preserved
            cls.__time_record_list.append(tr)

            # if not tr.exclude:
            #     if not tr.category in cls.__cumul_time_record_od:
            #         cls.__cumul_time_record_od[tr.category] = SingletonTimer.CumulTimeRecord(
            #         )

            #     ctr = cls.__cumul_time_record_od[tr.category]

            #     dt = tr.time_end - tr.time_begin
            #     ctr.category = tr.category
            #     ctr.cumul_time += dt
            #     ctr.sum_count += 1
            #     ctr.max_time = max(ctr.max_time, dt)
            #     ctr.min_time = min(ctr.min_time, dt)

        # clear time begin list
        cls.__time_begin_list.clear()

        const_end_time = cls.__get_time_stamp()
        print(
            f'Construction time record took {const_end_time - const_begin_time : 0.6f} s to process # {proc_num} elements')

    @classmethod
    def display_log(cls):
        cls.__construct_time_record()

        # This will simply print out all the time records
        print("\n[Display Log]")
        for tr in cls.__time_record_list:
            if not tr.exclude:
                print(f'Tag: {tr.tag}, Category: {tr.category}, Ticket: {tr.ticket}, Begin: {tr.time_begin - cls.__reset_time : 0.6f} s, End: {tr.time_end - cls.__reset_time : 0.6f} s, dt: {tr.time_end - tr.time_begin : 0.6f} s')
        print("\n")

    @classmethod
    def display_summary(cls, outlier_percent=0.10):
        assert outlier_percent >= 0 and outlier_percent <= 0.5, "outlier_percent must be in [0, 0.5]"

        cls.__construct_time_record()

        dt_arr_by_category = OrderedDict()
        for tr in cls.__time_record_list:
            if not tr.exclude:
                if not tr.category in dt_arr_by_category:
                    dt_arr_by_category[tr.category] = []
                dt_arr_by_category[tr.category].append(
                    tr.time_end - tr.time_begin)

        for k, v in dt_arr_by_category.items():
            v.sort()
            n = len(v)
            dt_arr_by_category[k] = v[int(
                n * outlier_percent):int(n * (1 - outlier_percent))]

        for k, v in dt_arr_by_category.items():
            if not k in cls.__cumul_time_record_od:
                cls.__cumul_time_record_od[k] = SingletonTimer.CumulTimeRecord(
                )

            ctr = cls.__cumul_time_record_od[k]

            ctr.category = k
            ctr.sum_count = len(v)
            ctr.min_time = min(v)
            ctr.max_time = max(v)
            ctr.cumul_time = sum(v)

        # NOTE(jpyo0803): exclude 'excluded' measures
        avg_serial_latency = 0
        serial_latency = 0

        for k, v in cls.__cumul_time_record_od.items():
            serial_latency += v.cumul_time
            avg_serial_latency += v.cumul_time / v.sum_count

        if cls.__allow_overlap:
            unoverlapped_latency = 0

            x_s = x_e = -1
            for tr in cls.__time_record_list:
                y_s = tr.time_begin
                y_e = tr.time_end
                dt = y_e - y_s

                if y_s < x_e:
                    unoverlapped_latency += max(0, y_e - x_e)
                    x_e = max(x_e, y_e)
                else:
                    unoverlapped_latency += dt
                    x_s = y_s
                    x_e = y_e
            unoverlapped_percent = unoverlapped_latency / serial_latency
            overlapped_percent = 1 - unoverlapped_percent

        raw_data = dict()
        print("\n[Display Summary]")
        if cls.__allow_overlap:
            print(
                f'Avg. total Latency: {avg_serial_latency * unoverlapped_percent : 0.6f} s, Avg. hidden latency: {overlapped_percent * 100: 0.2f} %')
        else:
            print(f'Avg. total Latency: {avg_serial_latency : 0.6f} s')

        total_cumul_time = 0
        for k, v in cls.__cumul_time_record_od.items():
            total_cumul_time += v.cumul_time

        for k, v in cls.__cumul_time_record_od.items():
            avg_time = v.cumul_time / v.sum_count
            # self.cumul_time = 0.0
            # self.sum_count = 0
            # self.max_time = 0.0
            # self.min_time = 1e18
            raw_data[k] = (v.sum_count, v.min_time,
                           v.max_time, avg_time, v.cumul_time)
            print(f'Category: {k}, # Samples = {v.sum_count}, Min latency: {v.min_time : 0.6f} s, Max latency: {v.max_time : 0.6f} s, Avg latency: {avg_time : 0.6f} s, ({avg_time / (avg_serial_latency * unoverlapped_percent if cls.__allow_overlap else avg_serial_latency) * 100 : 0.2f} % ), Cumulative latency: { v.cumul_time : 0.6f} s ({v.cumul_time / total_cumul_time * 100 : 0.2f} %)')

        print("\n")

        return raw_data

    @ classmethod
    def disable(cls):
        cls.__disable = True

    @ classmethod
    def enable(cls):
        cls.__disable = False

    @ classmethod
    def get_allow_overlap(cls):
        return cls.__allow_overlap

    @ classmethod
    def get_overlap_counter(cls):
        return cls.__overlap_counter

    @ classmethod
    def reset(cls):
        cls.__is_measuring = False
        cls.__ticket_counter = 0
        cls.__overlap_counter = 0

        cls.__time_begin_list = []
        cls.__time_end_list = []

        cls.__disable = False

        cls.__time_record_list = []
        cls.__cumul_time_record_od = OrderedDict()
        cls.__reset_time = cls.__get_time_stamp()
        print(f'Singleton timer is reset at {cls.__reset_time : 0.6f} s')

    @ classmethod
    def __get_time_stamp(cls):
        if cls.__timer_source == SingletonTimer.TimerSource.Time:
            return time.time()
        elif cls.__timer_source == SingletonTimer.TimerSource.PerfCounter:
            return time.perf_counter()
        elif cls.__timer_source == SingletonTimer.TimerSource.PerfCounterNs:
            return time.perf_counter_ns() / 1e9
        else:
            assert False, "Invalid timer source"

    @ classmethod
    def set_time_source(cls, type: TimerSource):
        if type == SingletonTimer.TimerSource.Time:
            print(f'Set timer source: Time')
        elif type == SingletonTimer.TimerSource.PerfCounter:
            print(f'Set timer source: PerfCounter')
        elif type == SingletonTimer.TimerSource.PerfCounterNs:
            print(f'Set timer source: PerfCounterNs')

        cls.__timer_source = type


if __name__ == "__main__":
    timer = SingletonTimer()
    timer2 = SingletonTimer()
    # NOTE(jpyo0803): they must be same
    assert timer is timer2


'''
[Reference]
1. https://wikidocs.net/69361
'''
