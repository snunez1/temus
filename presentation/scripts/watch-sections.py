#!/usr/bin/env python3
import time
import subprocess
from pathlib import Path

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog not installed. File watching disabled.")
    print("Install with: pip install watchdog")

if WATCHDOG_AVAILABLE:
    class SectionHandler(FileSystemEventHandler):
        def on_modified(self, event):
            if event.src_path.endswith('.md') or event.src_path.endswith('.html'):
                print(f"Change detected: {event.src_path}")
                subprocess.run([Path(__file__).parent / "concat-sections.py"])

    if __name__ == "__main__":
        observer = Observer()
        observer.schedule(SectionHandler(), path='sections', recursive=True)
        observer.start()
        print("Watching for changes in sections/...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
else:
    print("File watcher not available. Run concat-sections.py manually after changes.")
