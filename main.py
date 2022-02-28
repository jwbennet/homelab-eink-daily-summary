import logging
import os
import sys
libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'lib')
if os.path.exists(libdir):
    sys.path.append(libdir)

from dashboard import Dashboard
from datetime import datetime, timedelta, tzinfo
from google.cloud import storage
from power import PowerHelper
from summary import Summary
from waveshare_epd import epd7in5b_V2

logging.basicConfig(filename="calendar.log", filemode="a", format="%(asctime)s %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    logger.info("Begin processing personal organizer")
    
    last_rendered = datetime.now().astimezone() - timedelta(weeks=52)
    try:
        with open('last_rendered.txt', 'r') as last_rendered_file:
            data = last_rendered_file.readline().replace("\n", "")
            last_rendered = datetime.fromisoformat(data).astimezone()
    except IOError:
        logger.info("Last rendered file did not exist")
    

    storage_client = storage.Client("dashboard-api-279503")
    bucket = storage_client.get_bucket("inpulsetech-calendar")
    payload = bucket.get_blob("current.json")
    last_updated = payload.updated
    logger.info(f"Calendar was last updated at {last_rendered.isoformat()} and payload was last updated at {last_updated.isoformat()}")
    render = True
    if last_updated < last_rendered:
        logger.info("Payload has not been updated since last render")
        render = False

    power_helper = PowerHelper()
    if render:
        epd = epd7in5b_V2.EPD()
        summary = Summary.from_json(payload.download_as_string())
        (black_image, red_image) = Dashboard(summary, epd.width, epd.height, power_helper).render()

        logger.info("Init screen")
        epd.init()
        # epd.Clear()
        logger.info("Begin painting")
        epd.display(epd.getbuffer(black_image), epd.getbuffer(red_image))
        logger.info("End painting")
        logger.info("Set display to sleep")
        epd.sleep()

        # Store last time the screen was rendered
        with open("last_rendered.txt", "w") as last_rendered_file:
            last_rendered_file.write(datetime.now().astimezone().isoformat());

    logger.info("Set next wake time")
    now = datetime.now().replace(minute=55, second=0, microsecond=0)
    next_run = now + timedelta(hours=2)
    if now.weekday() >= 5: # It is a weekend, so update less often
        next_run = now + timedelta(hours=4)
    if next_run.hour < 8 or next_run.hour >= 19:
        next_run = now.replace(hour=7) + timedelta(days=1)
    power_helper.set_next_boot_datetime(next_run)

    power_level = power_helper.get_battery()
    if power_level >= 0:
        logger.info(f"Battery power at {power_level} after updating calendar")
        logger.info("Shutting down")
        os.system("sudo shutdown -h now")
    else:
        logger.info("On dedicated power so not shutting down")
    
except IOError as e:
    logger.error(e)
    
except KeyboardInterrupt:    
    logger.info("ctrl + c:")
    epd7in5b_V2.epdconfig.module_exit()
    exit()
