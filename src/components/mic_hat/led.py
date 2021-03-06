
from src.components.mic_hat import apa102
import time
import threading, logging
try:
    import queue as Queue
except ImportError:
    import Queue as Queue


class Pixels:
    PIXELS_N = 3

    def __init__(self):
        self.basis = [0] * 3 * self.PIXELS_N
        self.basis[0] = 1
        self.basis[4] = 1
        self.basis[8] = 2

        self.colors = [0] * 3 * self.PIXELS_N
        self.dev = apa102.APA102(num_led=self.PIXELS_N)

        self.next = threading.Event()
        self.queue = Queue.Queue()
        self.thread = threading.Thread(target=self._run)
        self.thread.daemon = True
        self.thread.start()
        self._logger = logging.getLogger()

    def wakeup(self, direction=0):
        def f():
            self._wakeup(direction)

        self.next.set()
        self.queue.put(f)
        self._logger.info('mic hat led wakeup')

    def listen(self):
        self.next.set()
        self.queue.put(self._listen)
        self._logger.info('mic hat led listen')

    def think(self):
        self.next.set()
        self.queue.put(self._think)
        self._logger.info('mic hat led think')

    def speak(self):
        self.next.set()
        self.queue.put(self._speak)
        self._logger.info('mic hat led speak')

    def off(self):
        self.next.set()
        self.queue.put(self._off)
        self._logger.info('mic hat led off')

    def _run(self):
        while True:
            func = self.queue.get()
            func()

    def _wakeup(self, direction=0):
        for i in range(1, 100):
            colors = [i * v for v in self.basis]
            self.write(colors)
            time.sleep(0.02)
            if self.next.is_set():
                break

        self.colors = colors

    def _listen(self):
        for i in range(1, 25):
            colors = [i * v for v in self.basis]
            self.write(colors)
            time.sleep(0.5)
            if self.next.is_set():
                break

        self.colors = colors

    def _think(self):
        colors = self.colors

        self.next.clear()
        while not self.next.is_set():
            colors = colors[3:] + colors[:3]
            self.write(colors)
            time.sleep(0.2)

        t = 0.05
        for i in range(0, 5):
            colors = colors[3:] + colors[:3]
            self.write([(v * (4 - i) / 4) for v in colors])
            time.sleep(t)
            t /= 2
            if self.next.is_set():
                break

        # time.sleep(0.5)

        self.colors = colors

    def _speak(self):
        colors = self.colors

        self.next.clear()
        while not self.next.is_set():
            for i in range(5, 25):
                self.write([(v * i / 24) for v in colors])
                time.sleep(0.02)

            time.sleep(0.3)

            for i in range(24, 4, -1):
                self.write([(v * i / 24) for v in colors])
                time.sleep(0.02)

            time.sleep(0.3)

        self._off()

    def _off(self):
        self.write([0] * 3 * self.PIXELS_N)

    def write(self, colors):
        for i in range(self.PIXELS_N):
            self.dev.set_pixel(i, int(colors[3*i]), int(colors[3*i + 1]), int(colors[3*i + 2]))

        self.dev.show()


pixels = Pixels()


if __name__ == '__main__':
    while True:

        try:
            pixels.wakeup()
            time.sleep(3)
            pixels.think()
            time.sleep(3)
            pixels.speak()
            time.sleep(3)
            pixels.off()
            time.sleep(3)
        except KeyboardInterrupt:
            break


    pixels.off()
    time.sleep(1)