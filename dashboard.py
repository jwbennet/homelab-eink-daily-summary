import logging;
from action_list import ActionList
from footer import Footer
from header import Header
from layout import Layout
from PIL import Image, ImageDraw
from power import PowerHelper
from schedule import Schedule
from summary import Summary

logger = logging.getLogger(__name__)

class Dashboard(object):

    def __init__(self, summary: Summary, width: int, height: int, power_helper: PowerHelper):
        self.blackimg = Image.new('1', (width, height), 255)
        self.draw_blackimg = ImageDraw.Draw(self.blackimg)
        self.redimg = Image.new('1', (width, height), 255)
        self.draw_redimg = ImageDraw.Draw(self.redimg)
        self._layout = Layout(width, height)
        self.header = Header(self.layout, power_helper)
        self.schedule = Schedule(summary.schedule, self.layout.left_column_start, self.layout.left_column_end)
        self.action_list = ActionList(summary.tasks, self.layout.right_column_start, self.layout.right_column_end)
        self.footer = Footer(summary.weather, self.layout.footer_start, self.layout.footer_end)

    @property
    def black(self) -> ImageDraw:
        return self.draw_blackimg
    
    @property
    def red(self) -> ImageDraw:
        return self.draw_redimg

    @property
    def layout(self) -> Layout:
        return self._layout

    def render(self) -> tuple[Image, Image]:
        self.layout.render(self.black)
        self.header.render(self.black, self.red)
        self.schedule.render(self.black, self.red)
        self.action_list.render(self.black, self.red)
        self.footer.render(self.blackimg, self.red)
        return (self.blackimg, self.redimg)
