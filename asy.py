import time
from datetime import datetime


class WaitLoopResult:

    def __bool__(self):
        return self.bool

    def __eq__(self, other):
        return other == self.bool

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.bool)

    def __repr__(self):
        return self.bool

    def __str__(self):
        return str(self.__repr__())

    def __init__(self, **kwargs):
        self.bool = kwargs.pop("bool", None)
        self.last_exception = kwargs.pop("exception", None)
        self.result = kwargs.pop("result", None)




def wait_while_not(f_logic, timeout, warning_timeout=None, delay_between_attempts=1.5):
    """
    Внутренний цик выполняется, пока вычисление `f_logic()` трактуется как `False`.
    """

    warning_flag = False
    start_time = datetime.now()
    wl_result = WaitLoopResult()

    while True:
        try:
            result = f_logic()
        except Exception as ex:
            print('Exception')
            wl_result.last_exception = ex
        else:
            if result:
                wl_result.bool = True
                wl_result.result = result
                return wl_result

        elaps_time = (datetime.now() - start_time).total_seconds()

        if warning_timeout and elaps_time > warning_timeout and not warning_flag:
            print("Waiting time exceeded {}".format(warning_timeout))
            warning_flag = True

        if timeout and elaps_time > timeout:
            wl_result.bool = False
            return wl_result

        time.sleep(delay_between_attempts)
def check(det_name, ev_name, timeout=30):
    res = []

    def f(ls=1):
        print(f'they touch me {res}')
        res.append(1)
        if len(res) == 3:
            return 1



    x = wait_while_not(lambda: f(), 20)
    print(x)

def test():
    ev_count = check('neuro','some_event')