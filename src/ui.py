# 第三方包
import pygame
import logging

from types import FunctionType
from typing import Union

from time import time

# 本地包
from init import appconfig

# 初始化
pygame.init()


class MessageBox:
    def __init__(self, text: str, font_obj: pygame.font.Font, screen: pygame.Surface, height: int = None,
                 color=(0, 0, 0), bg_color=None, use_anti_aliasing: bool = True,
                 message_type: str = "info", sep: str = "\n", title_icon_size: tuple = (70, 70),
                 title_font_obj: pygame.font.Font = None,
                 click_exit: Union[bool, FunctionType] = False):
        """
        初始化

        :param text: 显示的文本 [str]
        :param font_obj: pygame Font 对象 [pygame.font.Font]
        :param screen: 屏幕 [pygame.Surface]
        :param height: 显示的右下角高度值 [int]
        :param color: 字体颜色
        :param bg_color: 字体背景颜色 ("默认无“)
        :param use_anti_aliasing: 是否启用抗锯齿 (默认True)
        :param message_type: 消息类型 (影响显示, 默认info) ["error", "info", "warning"]
        :param sep: 换行符 (默认"\n")
        :param title_icon_size: 标题栏图标大小
        :param title_font_obj: 标题栏font_object
        :param click_exit: 是否再点击时退出 (若为Func则在点击时调用) [bool | Func]
        """
        message_types_dict = appconfig.message_types
        self.__message_type = message_types_dict.get(message_type.lower(), None)
        if self.__message_type is None:
            print(f"Warning: message_type: \"{message_type}\" not define, use the \"info\".")
            self.__message_type = message_types_dict.get("info")

        self.height = height if height is not None else screen.get_height()
        self.screen = screen

        self.__click_exit = click_exit
        self.__text = text
        self.__font_config = [color, use_anti_aliasing, bg_color]
        self.__sep = sep
        self.__font_obj = font_obj
        self.__title_font_obj = title_font_obj if title_font_obj is not None else font_obj

        self.__font_max_pos = None
        self.__message_surface = None
        self.__check_box = [0, 0, 0, 0]

        self.__config = {
            "title-size": title_icon_size,
        }

    def init(self):
        lines = self.__text.split(self.__sep)

        # 加上title高度
        total_height = round(self.__font_obj.get_height() * 0.8) * len(lines) + self.__config.get("title-size",
                                                                                                  0)[1] + 15
        total_width = self.screen.get_width()
        self.__message_surface = pygame.Surface((total_width, total_height)).convert_alpha()  # 创建surface并设置使用透明通道
        self.__message_surface.fill((0, 0, 0, 0))  # 设置全部透明
        self.__message_surface.blit(pygame.transform.scale(appconfig.message_images.get(self.__message_type),
                                                           self.__config.get("title-size")), (0, 0))  # 创建title icon
        title_font_surface = self.__title_font_obj.render(appconfig.message_tips.get(self.__message_type),
                                                          *self.__font_config)  # title 文本surface
        self.__message_surface.blit(title_font_surface, (self.__config.get("title-size")[0] + 3,
                                                         -round(title_font_surface.get_height() * 0.17)))  # 画
        # 加上title高度
        font_pos = [self.__config.get("title-size")[0] + 3,
                    -round(self.__font_obj.get_height() * 0.17) + self.__config.get("title-size", (0, 0))[1] + 10]
        self.__font_max_pos = [-1, -1]
        for string in lines:
            font_surface = self.__font_obj.render(string, *self.__font_config)
            self.__message_surface.blit(font_surface, font_pos)
            font_pos[1] += round(font_surface.get_height() * 0.8)
            if font_pos[0] > self.__font_max_pos[0] or font_pos[1] > self.__font_max_pos[1]:
                self.__font_max_pos = font_pos

        pygame.image.save(self.__message_surface, "test-{}.png".format(time()))

    def __enter(self):
        """
        入场动画
        :return: None
        """


if __name__ == "__main__":
    screen = pygame.display.set_mode((1000, 1000))
    font = pygame.font.SysFont("microsoft Yahei", 70)
    test = MessageBox("error test", font, screen, message_type="error")
    test.init()
    test = MessageBox("warning test", font, screen, message_type="warning")
    test.init()
    test = MessageBox("info test", font, screen, message_type="info")
    test.init()
