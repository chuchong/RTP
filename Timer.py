import time
import threading
class Timer():
    def singleShot(self, func, mscs, *args, **kwargs):
        time.sleep(mscs / 1000)
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
