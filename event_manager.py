from typing import Callable
import threading
from queue import Queue

class Event:
    def __init__(self, name: str):
        self.name = name
        self._handlers = []

    def __iadd__(self, handler: Callable):
        self._handlers.append(handler)
        return self

    def __isub__(self, handler: Callable):
        self._handlers.remove(handler)
        return self

    def invoke(self, *args, **kwargs):
        for handler in self._handlers:
            handler(*args, **kwargs)

class AppEventManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        if not self._initialized:
            self.events = {}
            self.event_queue = Queue()
            self._running = False
            self._thread = None
            self._initialized = True
            
            # Initialize common events
            self.button_clicked = self.create_event("button_clicked")
            self.data_received = self.create_event("data_received")
            
            # Start processing
            self.start_processing()

    def create_event(self, event_name: str) -> Event:
        if event_name not in self.events:
            self.events[event_name] = Event(event_name)
        return self.events[event_name]

    def start_processing(self):
        if not self._running:
            self._running = True
            self._thread = threading.Thread(target=self._process_events)
            self._thread.daemon = True
            self._thread.start()

    def stop_processing(self):
        self._running = False
        if self._thread:
            self._thread.join()

    def _process_events(self):
        while self._running:
            try:
                event_name, data = self.event_queue.get(timeout=1)
                if event_name in self.events:
                    self.events[event_name].invoke(data)
                self.event_queue.task_done()
            except Exception as e:
                print(e)
                continue

    def trigger_event(self, event_name: str, data: dict):
        self.event_queue.put((event_name, data))

