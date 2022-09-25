import time

class StopWatch:
    def __init__(self):
        self._start_time = None
        self._duration = None

    def start(self, duration):
        self._duration = duration
        self._start_time = time.perf_counter()

    def has_elapsed(self):
        if((self._start_time == None) or (self._duration == None)):
            return False;

        elapsed_time = time.perf_counter() - self._start_time
        return elapsed_time >= self._duration

    def time_left(self):
        if((self._start_time == None) or (self._duration == None)):
            return 0

        elapsed_time = time.perf_counter() - self._start_time        
        return (self._duration - elapsed_time)
