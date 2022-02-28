import logging;
import os;
from configparser import SafeConfigParser
from dateutil import parser
from PIL import ImageDraw, ImageFont
from summary import Meeting
from textwrap import wrap
from typing import List

logger = logging.getLogger(__name__)

class ScheduleConfig(object):

    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.sections()
        found = self.parser.read('config/organizer.cfg')
        if not found:
            raise ValueError('No config file found!')
        self.fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')
    
    @property
    def header_font(self) -> ImageFont:
        font = self.parser.get('schedule', 'header_font')
        font_size = int(self.parser.get('schedule', 'header_font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)
    
    @property
    def header_icon_font(self) -> ImageFont:
        font = self.parser.get('schedule', 'header_font')
        font_size = int(self.parser.get('schedule', 'header_font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, 'fa5-regular.otf'), 25)

    @property
    def body_font(self) -> ImageFont:
        font = self.parser.get('body', 'font')
        font_size = int(self.parser.get('body', 'font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)

class Schedule(object):

    def __init__(self, meetings: List[Meeting], box_start: tuple[int, int], box_end: tuple[int, int]):
        self.config = ScheduleConfig()
        self.meetings = meetings
        self.box_start = box_start
        self.box_end = box_end

    def draw_header(self, image: ImageDraw) -> int:
        icon = '\uf133'
        header_text = 'Schedule'
        (x, y) = self.box_start
        (max_x, max_y) = self.box_end
        (icon_w, icon_h) = image.textsize(icon, font = self.config.header_icon_font)
        (text_w, text_h) = image.textsize(header_text, font=self.config.header_font)
        action_list_header_offset = x + int((max_x - x - text_w - icon_w - 10) / 2)
        image.text((action_list_header_offset, y + 2), icon, font=self.config.header_icon_font)
        image.text((action_list_header_offset + icon_w + 10, y), header_text, font=self.config.header_font)
        
        return y + text_h + 10

    def draw_schedule(self, image: ImageDraw, start_y: int) -> None:
        y = start_y
        (x, _) = self.box_start
        (max_x, max_y) = self.box_end
        for i, meeting in enumerate(self.meetings):
            event_time = parser.parse(meeting.start_time).strftime("%H:%M") + " \u2014 "
            event_text = '\n'.join(wrap(meeting.summary, width=27))
            y += 4
            (event_time_w, event_time_h) = image.textsize(event_time, font=self.config.body_font)
            (event_w, event_h) = image.textsize(event_text, font=self.config.body_font)
            image.text((x + 8, y), event_time, font = self.config.body_font)
            image.text((x + 8 + event_time_w, y), event_text, font = self.config.body_font)
            y += event_h + 6
            if i < len(self.meetings) - 1:
                image.rectangle([(x, y), (max_x, y)], fill = "#000000")
                y += 1

    def render(self, black_image: ImageDraw, red_image: ImageDraw) -> None:
        logger.info("Rendering")
        body_y = self.draw_header(black_image)
        self.draw_schedule(black_image, body_y)
