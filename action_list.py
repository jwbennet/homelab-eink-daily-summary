import logging;
import os;
from configparser import SafeConfigParser
from dateutil import parser
from PIL import ImageDraw, ImageFont
from summary import Task
from textwrap import wrap
from typing import List

logger = logging.getLogger(__name__)

class ActionListConfig(object):

    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.sections()
        found = self.parser.read('config/organizer.cfg')
        if not found:
            raise ValueError('No config file found!')
        self.fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')
    
    @property
    def header_font(self) -> ImageFont:
        font = self.parser.get('action-list', 'header_font')
        font_size = int(self.parser.get('action-list', 'header_font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)

    @property
    def header_icon_font(self) -> ImageFont:
        return ImageFont.truetype(os.path.join(self.fontdir, 'fa5-solid.otf'), 25)

    @property
    def body_font(self) -> ImageFont:
        font = self.parser.get('body', 'font')
        font_size = int(self.parser.get('body', 'font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)

    @property
    def body_icon_font(self) -> ImageFont:
        return ImageFont.truetype(os.path.join(self.fontdir, 'fa5-regular.otf'), 15)

class ActionList(object):

    def __init__(self, tasks: List[Task], box_start: tuple[int, int], box_end: tuple[int, int]):
        self.config = ActionListConfig()
        self.tasks = tasks
        self.box_start = box_start
        self.box_end = box_end

    def draw_header(self, image: ImageDraw) -> int:
        icon = '\uf0ae'
        header_text = 'Action List'
        (x, y) = self.box_start
        (max_x, max_y) = self.box_end
        (icon_w, icon_h) = image.textsize(icon, font = self.config.header_icon_font)
        (text_w, text_h) = image.textsize(header_text, font=self.config.header_font)
        action_list_header_offset = x + int((max_x - x - text_w - icon_w - 10) / 2)
        image.text((action_list_header_offset, y + 2), icon, font=self.config.header_icon_font)
        image.text((action_list_header_offset + icon_w + 10, y), header_text, font=self.config.header_font)
        
        return y + text_h + 10

    def draw_action_list(self, image: ImageDraw, start_y: int) -> None:
        y = start_y
        (x, _) = self.box_start
        (max_x, _) = self.box_end
        for i, task in enumerate(self.tasks):
            icon = '\uf058 ' if task.complete else '\uf111 '
            formatted_summary = wrap(task.summary, width=32)
            (task_bullet_w, _) = image.textsize(icon, font=self.config.body_icon_font)
            for line, summary_line in enumerate(formatted_summary):
                y += 4
                (task_w, task_h) = image.textsize(summary_line, font=self.config.body_font)
                if line == 0:
                    image.text((x + 8, y + 2), icon, font=self.config.body_icon_font)
                image.text((x + task_bullet_w + 8, y), summary_line, font=self.config.body_font)
                if task.complete:
                    image.rectangle([(x + task_bullet_w + 8, y + int(task_h / 2)), (x + task_bullet_w + 8 + task_w, y + int(task_h / 2) + 1)], fill = "#000000")
                y += task_h
            y += 6
            if i < len(self.tasks) - 1:
                image.rectangle([(x, y), (max_x, y)], fill = "#000000")
                y += 1

    def render(self, black_image: ImageDraw, red_image: ImageDraw) -> None:
        logger.info("Rendering")
        body_y = self.draw_header(black_image)
        self.draw_action_list(black_image, body_y)
