import logging;
import os;
from configparser import SafeConfigParser
from dateutil import parser
from functools import reduce
from PIL import Image, ImageDraw, ImageFont
from summary import Weather
from textwrap import wrap
from typing import List

logger = logging.getLogger(__name__)

class FooterConfig(object):

    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.sections()
        found = self.parser.read('config/organizer.cfg')
        if not found:
            raise ValueError('No config file found!')
        self.fontdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'font')
    
    @property
    def header_font(self) -> ImageFont:
        font = self.parser.get('footer', 'header_font')
        font_size = int(self.parser.get('footer', 'header_font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)
    
    @property
    def body_font(self) -> ImageFont:
        font = self.parser.get('body', 'font')
        font_size = int(self.parser.get('body', 'font_size'))
        return ImageFont.truetype(os.path.join(self.fontdir, f'{font}.ttf'), font_size)

    @property
    def weather_icon_font(self) -> ImageFont:
        return ImageFont.truetype(os.path.join(self.fontdir, 'fa5-solid.otf'), 15)

class Footer(object):

    def __init__(self, weather: List[Weather], box_start: tuple[int, int], box_end: tuple[int, int]):
        self.config = FooterConfig()
        self.weather = weather
        self.box_start = box_start
        self.box_end = box_end

    def draw_weather(self, weather: Weather, black_image: Image, red_image: ImageDraw) -> Image:
        icon = ""
        if weather.condition == 1000: # Sunny
            icon = "\uf185"
        elif weather.condition == 1003: # Partly cloudy
            icon = "\uf6c4"
        elif weather.condition in [ 1006, 1009 ]: # Cloudy, Overcast
            icon = "\uf0c2"
        elif weather.condition in [ 1030, 1135, 1147 ]: # Mist, Fog, Freezing fog
            icon = "\uf75f"
        elif weather.condition in [ 1063, 1150, 1153, 1180, 1183, 1186, 1189, 1240 ]: # Patchy rain possible, Patchy light drizzle, Light drizzle, Patchy light rain, Light rain, Moderate rain at times, Moderate rain, Light rain shower
            icon = "\uf73d"
        elif weather.condition in [ 1192, 1195, 1243, 1246,  ]: # Heavy rain at times, Heavy rain, Moderate or heavy rain shower, Torrential rain shower
            icon = "\uf740"
        elif weather.condition in [ 1066, 1114, 1117, 1210, 1213, 1216, 1219, 1222, 1225, 1255, 1258 ]: # Patchy snow possible, Blowing snow, Blizzard, Patchy light snow, Light snow, Patchy moderate snow, Moderate snow, Patchy heavy snow, Heavy snow, Light snow showers, Moderate or heavy snow showers
            icon = "\uf2dc"
        elif weather.condition in [ 1069, 1072, 1087, 1168, 1171, 1198, 1201, 1204, 1207, 1237, 1249, 1252, 1261, 1264 ]: # Patchy sleet possible, Patchy freezing drizzle possible, Freezing drizzle, Heavy freezing drizzle, Light freezing rain, Moderate or heavy freezing rain, Light sleet,  Moderate or heavy sleet, Ice pellets, Light sleet showers, Moderate or heavy sleet showers, Light showers of ice pellets, Moderate or heavy showers of ice pellets
            icon = "\uf7ad"
        elif weather.condition in [ 1087, 1273, 1276, 1279, 1282 ] : # Thundery outbreaks possible, Patchy light rain with thunder, Moderate or heavy rain with thunder, Patchy light snow with thunder, Moderate or heavy snow with thunder
            icon = "\uf0e7"

        time = parser.parse(weather.time).strftime("%H:%M")
        temperature = f" | {weather.temperature}\u00B0 | "
        precipitation_icon = "\uf043"
        precipitation = f"{weather.precipitation}%"
        (time_w, time_h) = black_image.textsize(time, font=self.config.header_font)
        (icon_w, icon_h) = black_image.textsize(icon, font = self.config.weather_icon_font)
        (temp_w, temp_h) = black_image.textsize(temperature, font=self.config.body_font)
        (precip_icon_w, precip_icon_h) = black_image.textsize(precipitation_icon, font = self.config.weather_icon_font)
        (precip_w, precip_h) = black_image.textsize(precipitation, font=self.config.body_font)

        image_width = (icon_w + temp_w + precip_icon_w + 4 + precip_w)
        image_height = (time_h + 5 + max(icon_h, temp_h, precip_icon_h, precip_h) + 2)
        image = Image.new('1', (image_width, image_height), 0)
        draw_image = ImageDraw.Draw(image)
        x = 0
        y = 0
        time_offset = int((image_width - time_w) / 2)
        draw_image.text((time_offset, y), time, font=self.config.header_font, fill="#ffffff")
        y += time_h + 5
        draw_image.text((x, y + 2), icon, font=self.config.weather_icon_font, fill="#ffffff")
        x += icon_w
        draw_image.text((x, y), temperature, font=self.config.body_font, fill="#ffffff")
        x += temp_w
        draw_image.text((x, y + 2), precipitation_icon, font=self.config.weather_icon_font, fill="#ffffff")
        x += precip_icon_w + 4
        draw_image.text((x, y), precipitation, font=self.config.body_font, fill="#ffffff")

        return image

    def draw_weather_forecast(self, black_image: Image, red_image: ImageDraw) -> None:
        weather_images = list(map(lambda weather: self.draw_weather(weather, black_image, red_image), self.weather))
        weather_forecast_w = reduce(lambda acc, weather: acc + weather.width, weather_images, 0) + (len(self.weather) - 1) * 41
        (_, y) = self.box_start
        (max_x, max_y) = self.box_end
        x = int((max_x - weather_forecast_w) / 2)
        draw_image = ImageDraw.Draw(black_image)
        for i, image in enumerate(weather_images):
            if i != 0:
                x += image.width + 20
                draw_image.rectangle([x, y, x, max_y], fill="#FFFFFF")
                x += 21
            black_image.paste(image, (x, y))
        
    def render(self, black_image: Image, red_image: ImageDraw) -> None:
        logger.info("Rendering")
        self.draw_weather_forecast(black_image, red_image)
