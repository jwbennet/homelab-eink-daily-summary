import logging
from configparser import SafeConfigParser
from dataclasses import dataclass
from PIL import ImageDraw

logger = logging.getLogger(__name__)

class LayoutConfig(object):

    def __init__(self):
        self.parser = SafeConfigParser()
        self.parser.sections()
        found = self.parser.read('config/organizer.cfg')
        if not found:
            raise ValueError('No config file found!')
    
    @property
    def column_height(self) -> int:
        return int(self.parser.get('layout', 'column.height'))    
    
    @property
    def column_width(self) -> int:
        return int(self.parser.get('layout', 'column.width'))

    @property
    def divider_width(self) -> int:
        return int(self.parser.get('layout', 'divider.width'))

    @property
    def header_height(self) -> int:
        return int(self.parser.get('header', 'height'))

    @property
    def side_border_width(self) -> int:
        return int(self.parser.get('layout', 'side_border.width'))
    
class Layout(object):

    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.config = LayoutConfig()

    @property
    def width(self) -> int:
        return self.screen_width

    @property
    def height(self) -> int:
        return self.screen_height
    
    @property
    def border(self) -> int:
        return self.config.side_border_width

    @property
    def left_column_offset(self) -> int:
        return self.config.side_border_width

    @property
    def left_column_start(self) -> tuple[int, int]:
        return (self.left_column_offset + 5, self.config.header_height + 10)

    @property
    def left_column_end(self) -> tuple[int, int]:
        return (self.left_column_offset + self.config.column_width - 10, self.config.header_height + self.config.column_height - 10)

    @property
    def right_column_offset(self) -> int:
        return self.left_column_offset + self.config.column_width + self.config.divider_width
      
    @property
    def right_column_start(self) -> tuple[int, int]:
        return (self.right_column_offset + 5, self.config.header_height + 10)

    @property
    def right_column_end(self) -> tuple[int, int]:
        return (self.right_column_offset + self.config.column_width - 5, self.config.header_height + self.config.column_height - 10)

    @property
    def footer_start(self) -> tuple[int, int]:
        return (self.config.side_border_width, self.config.header_height + self.config.column_height + self.config.side_border_width + 5)

    @property
    def footer_end(self) -> tuple[int, int]:
        return (self.width - self.config.side_border_width, self.height - self.config.side_border_width)

    def draw_header(self, image: ImageDraw) -> None:
        image.rectangle([
                0,
                0,
                self.screen_width,
                self.config.header_height
            ], fill = "#000000")

    def draw_left_border(self, image: ImageDraw) -> None:
        image.rectangle([
                0,
                self.config.header_height,
                self.config.side_border_width,
                self.config.header_height + self.config.column_height
            ], fill = "#000000")

    def draw_center_divider(self, image: ImageDraw) -> None:
        image.rectangle([
                self.right_column_offset - self.config.divider_width,
                self.config.header_height,
                self.right_column_offset,
                self.config.column_height + self.config.header_height
            ], fill = "#000000")
    
    def draw_right_border(self, image: ImageDraw) -> None:
        image.rectangle([
                self.screen_width - self.config.side_border_width,
                self.config.header_height,
                self.screen_width,
                self.config.header_height + self.config.column_height 
            ], fill = "#000000")

    def draw_footer(self, image: ImageDraw) -> None:
        image.rectangle([
                0,
                self.config.column_height + self.config.header_height,
                self.screen_width,
                self.screen_height
            ], fill = "#000000")
  
    def render(self, image: ImageDraw) -> None:
        logger.info("Rendering")
        self.draw_header(image)
        self.draw_left_border(image)
        self.draw_center_divider(image)
        self.draw_right_border(image)
        self.draw_footer(image)
