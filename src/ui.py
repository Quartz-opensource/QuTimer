# 第三方包
import pygame
import logging

from types import FunctionType
from typing import Union
from threading import Thread

from time import sleep

# 本地包
from init import appconfig

# 初始化
pygame.init()


class MessageBox:
    def __init__(self, text: str, font_obj: pygame.font.Font, screen: pygame.Surface,
                 height: int = None, width: int = None,
                 color=(0, 0, 0), bg_color=None, use_anti_aliasing: bool = True,
                 message_type: str = "info", sep: str = "\n", title_icon_size: tuple = None,
                 title_font_obj: pygame.font.Font = None, move_lens: Union[int, float] = 3, move_sleep: float = 0.03,
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
        :param move_lens: 动画移动最小像素
        :param move_sleep: 动画移动暂停时间
        :param click_exit: 是否再点击时退出 (若为Func则在点击时调用, 返回值为True(或者任意python中bool为True)的值退出) [bool | Func]
        """

        message_types_dict = appconfig.message_types
        self.__message_type = message_types_dict.get(message_type.lower(), None)
        if self.__message_type is None:
            print(f"Warning: message_type: \"{message_type}\" not define, use the \"info\".")
            self.__message_type = message_types_dict.get("info")

        self.height = height
        self.width = width if width is not None else 0
        self.screen = screen

        self.__click_exit = click_exit
        self.__text = text
        self.__font_config = [color, use_anti_aliasing, bg_color]
        self.__sep = sep
        self.__font_obj = font_obj
        self.__title_font_obj = title_font_obj if title_font_obj is not None else font_obj
        self.__move_lens = move_lens
        self.__move_sleep = move_sleep

        self.__running = True
        self.__font_max_pos = None
        self.__message_surface = None
        self.__rect: pygame.rect.Rect = pygame.rect.Rect([0, 0, 0, 0])
        self.__clicked = False
        self.__done = False

        self.__config = {
            "title-size": title_icon_size if title_icon_size is not None else (
                round(self.__title_font_obj.get_height() * 0.77),
                round(self.__title_font_obj.get_height() * 0.77)
            ),
        }

        init_thread = Thread(target=self.__init, daemon=False)
        init_thread.start()

    @property
    def rect(self) -> pygame.rect.Rect:
        return self.__rect

    @property
    def check_box(self) -> pygame.rect.Rect:
        return self.__rect

    @property
    def clicked(self):
        return self.__clicked

    def __init(self):
        if not self.__done:
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
            self.__font_max_pos = [title_font_surface.get_width() + self.__config.get("title-size")[0] + 10,
                                   title_font_surface.get_height() + self.__config.get("title-size")[1]]  # 默认假设title栏最长
            for string in lines:
                font_surface = self.__font_obj.render(string, *self.__font_config)
                self.__message_surface.blit(font_surface, font_pos)
                font_pos[1] += round(font_surface.get_height() * 0.8)
                if font_pos[0] + font_surface.get_width() > self.__font_max_pos[0]:  # 比较长度
                    self.__font_max_pos = [font_pos[0] + font_surface.get_width() + 10, font_pos[1] + 10]

    def enter(self):
        if not self.__done:
            t = Thread(target=self.__enter, daemon=True)
            t.start()
            return t
        return False

    def __enter(self, move: int = None):
        """
        入场动画
        :return: None
        """
        if move is None:
            move = self.__move_lens

        self.__message_surface: pygame.Surface

        x = self.screen.get_width()
        self.__running = False
        sleep(self.__move_sleep + 0.01)
        self.__running = True
        pos = (0, 0)
        while self.__running:
            if self.height is None:
                height = self.screen.get_height()
            else:
                height = self.height
            target_x = self.screen.get_width() - self.__font_max_pos[0] + self.width  # 左上角x坐标
            target_y = height - self.__font_max_pos[1] - 10  # 左上角y坐标
            if target_y < 3:
                target_y = 3

            if self.__done:
                self.__rect = pygame.rect.Rect([0, 0, 0, 0])
                break
            if x == 0:
                x = 1
            if x > target_x and abs(target_x - x) >= move:
                x -= round(move * (1.1 - abs(target_x / x)) + 1)
            elif 0 < abs(target_x - x) < move:
                x -= abs(target_x - x) // 3
            if abs(target_x - x) <= 5:
                self.__running = False
            pos = x, target_y
            if self.__done:
                self.__rect = pygame.rect.Rect([0, 0, 0, 0])
                break
            else:
                self.__rect = pygame.rect.Rect([*pos, *self.__font_max_pos])  # 点击域 (x, y, width, height)
                self.screen.blit(self.__message_surface, pos)
            if self.__move_sleep > 0 and not self.__done:
                sleep(self.__move_sleep)

        self.__rect = pygame.rect.Rect([*pos, *self.__font_max_pos])  # 点击域 (x, y, width, height)

    def exit(self):
        if not self.__done:
            t = Thread(target=self.__exit, daemon=True)
            t.start()
            return t
        return False

    def __exit(self, move: int = None):
        """
        出场动画
        :return: None
        """
        if move is None:
            move = self.__move_lens

        self.__message_surface: pygame.Surface

        x = self.__rect[0]  # 获取当前x位置
        self.__running = False
        sleep(self.__move_sleep + 0.01)
        self.__running = True
        pos = self.__rect[:2]  # 当前位置
        while self.__running:
            if self.height is None:
                height = self.screen.get_height()
            else:
                height = self.height
            target_x = self.screen.get_width() + self.__font_max_pos[0] + self.width  # 左上角x坐标
            target_y = height - self.__font_max_pos[1] - 10  # 左上角y坐标
            if target_y < 3:
                target_y = 3

            if self.__done:
                self.__rect = pygame.rect.Rect([0, 0, 0, 0])
                break
            if x == 0:
                x = 1
            if x < target_x and abs(target_x - x) >= move:
                x += round(move * abs(x / target_x) + 1)
            elif 0 < abs(target_x - x) < move:
                x += abs(target_x - x) // 3
            if abs(x - target_x) <= 5:
                self.__running = False
            pos = x, target_y
            if self.__done:
                self.__rect = pygame.rect.Rect([0, 0, 0, 0])
                break
            else:
                self.__rect = pygame.rect.Rect([*pos, *self.__font_max_pos])  # 点击域 (x, y, width, height)
                self.screen.blit(self.__message_surface, pos)
            if self.__move_sleep > 0 and not self.__done:
                sleep(self.__move_sleep)

        # self.__rect = pygame.rect.Rect([*pos, *self.__font_max_pos])  # 点击域 (x, y, width, height)
        self.__done = True
        self.__rect = pygame.rect.Rect([0, 0, 0, 0])  # 重置rect

    def show(self, sec: float):
        if sec < 0:
            sec = 0

        def func(sec):
            self.__enter()
            sleep(sec)
            self.__exit()

        if not self.__done:
            t = Thread(target=func, args=(sec,), daemon=True)
            t.start()
            return t
        return False

    def update(self, mouse_events: list[pygame.event]):
        if self.__done:
            self.__rect = pygame.rect.Rect([0, 0, 0, 0])
            return False
        for e in mouse_events:
            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:  # 左键鼠标按下
                if self.__rect.colliderect(pygame.rect.Rect([*e.pos, 1, 1])):  # 把鼠标看成 1x1 的矩形并检测碰撞
                    self.__clicked = True
                else:
                    self.__clicked = False
            if e.type == pygame.MOUSEBUTTONUP and e.button == 1:  # 左键鼠标弹起
                if self.__clicked is True:
                    if type(self.__click_exit) == FunctionType:
                        try:
                            result = self.__click_exit()
                            if result:
                                self.__done = True
                                self.__rect = pygame.rect.Rect([0, 0, 0, 0])
                        except Exception as e:
                            print("WARNING: click_exit func error: {}".format(e))
                    else:
                        if self.__click_exit:
                            self.__done = True
                            self.__rect = pygame.rect.Rect([0, 0, 0, 0])
                self.__clicked = False

        if not self.__done:
            self.screen.blit(self.__message_surface, self.__rect)  # 重画
        else:
            self.__rect = pygame.rect.Rect([0, 0, 0, 0])


class Ui:
    def mainloop(self):
        pass


if __name__ == "__main__":
    pass
