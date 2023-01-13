from datetime import datetime
import logging

# Import logger
log = logging.getLogger()


def get_current(format="%Y-%m-%d__%H-%M-%S"):
    log.info("Start timestamp module")
    current_timestamp = str(datetime.now().strftime(format))
    log.info("Finished timestamp module")
    return current_timestamp

