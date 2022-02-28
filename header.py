import logging;
import os;
from configparser import SafeConfigParser
from datetime import datetime
from layout import Layout
from PIL import ImageDraw, ImageFont
from power import PowerHelper

logger = logging.getLogger(__name__)

class HeaderConfig(object):

    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.sections()
        found = self.parser.read('config/organizer.cfg')
        if not found:
            raise ValueError('No config file found!')
        self.fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')
    
    @property
    def font(self) -> ImageFont:
        font = self.parser.get('header', 'font')
        font_size = int(self.parser.get('header', 'font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)

    @property
    def icon_font(self) -> ImageFont:
      return ImageFont.truetype(os.path.join(self.fontdir, 'fa5-solid.otf'), 25)

    @property
    def body_font(self) -> ImageFont:
        font = self.parser.get('body', 'font')
        font_size = int(self.parser.get('body', 'font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)

class Header(object):

    def __init__(self, layout: Layout, power_helper: PowerHelper):
        self.config = HeaderConfig()
        self.layout = layout
        self.power_helper = power_helper

    def draw_header_text(self, image: ImageDraw) -> None:
        todays_date = datetime.today().strftime('%A, %B %d')
        (header_w, header_h) = image.textsize(todays_date, font=self.config.font)
        image.text(
            (((self.layout.width - header_w) / 2), 5),
            todays_date,
            font = self.config.font,
            fill = "#ffffff")

    def draw_last_updated(self, image: ImageDraw) -> None:
        current_time = datetime.now().strftime("%H:%M")
        (time_w, time_h) = image.textsize(current_time, font=self.config.body_font)
        (battery_w, battery_h) = image.textsize('\uf243', font=self.config.icon_font)
    
        image.text(((self.layout.width - self.layout.border - time_w - battery_w - 10), 17), current_time, font = self.config.body_font, fill = "#ffffff")

    def draw_battery_state(self, black_image: ImageDraw, red_image: ImageDraw) -> None:
        battery_icon = '\uf244'
        battery_image = black_image
        battery_color = '#FFFFFF'
        battery_level = self.power_helper.get_battery()
        if battery_level == -1:
            battery_icon = '\uf1e6'
        elif battery_level >= 80:
            battery_icon = '\uf240'
        elif battery_level >= 60:
            battery_icon = '\uf241'
        elif battery_level >= 40:
            battery_icon = '\uf242'
        elif battery_level >= 20:
            battery_icon = '\uf243'
        else:
            battery_icon = '\uf244'
            battery_image = red_image
            battery_color = '#000000'
        (battery_w, battery_h) = black_image.textsize('\uf243', font=self.config.icon_font)
        battery_image.text(((self.layout.width - self.layout.border - battery_w), 15), battery_icon, font=self.config.icon_font, fill = battery_color)

    def render(self, black_image: ImageDraw, red_image: ImageDraw) -> None:
        logger.info("Rendering")
        self.draw_header_text(black_image)
        self.draw_last_updated(black_image)
        self.draw_battery_state(black_image, red_image)
