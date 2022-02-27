from src.app import app
import logging
if __name__ == "__main__":
  log = logging.getLogger('werkzeug')
  log.setLevel(logging.ERROR)
  app.run()