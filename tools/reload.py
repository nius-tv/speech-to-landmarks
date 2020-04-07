import subprocess
import time

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


def run():
	global p1
	if p1:
		p1.kill()
	# --mocha: adds _nice_ symbols to test results
	# -s: displays print statement outputs
	# -v: show full diff
	p1 = subprocess.Popen(['bash', '-c', 'pytest -s -vv --mocha'])

	print('running')


class Handler(FileSystemEventHandler):

	@staticmethod
	def on_any_event(e):
		for name in ['__pycache__', '.git']:
			if name in e.src_path:
				return
		print('reloading code:', e.event_type, e.src_path)
		run()


if __name__ == '__main__':
	p1 = None
	observer = Observer()
	observer.schedule(Handler(), '.', recursive=True)
	observer.start()
	# Run for first time
	run()
	# Prevent app from exiting
	while True:
		time.sleep(1)
