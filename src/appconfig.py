import logging

from pygame import image, font

font.init()  # 初始化字体加载
from os import getenv, path as ospath
from threading import Thread


class Appconfig:
    def __init__(self):
        self.window = {
            "title": "",
            "bg": "white",
            "fps": 60,
        }

        self.message_types = {
            "error": 1,
            "warning": 2,
            "info": 0,
        }

        # 初始化加载图片
        self.message_images = {
            1: image.load(r"resources\image\message_box\error.png"),
            2: image.load(r"resources\image\message_box\warning.png"),
            0: image.load(r"resources\image\message_box\info.png")
        }

        # 初始化提示语
        self.message_tips = {
            1: "错误",
            2: "警告",
            0: "提示"
        }

        appdata = getenv("appdata", None)
        if appdata is not None:
            self.mgr_config_file = ospath.join(appdata, "./Timer/Config/Latest.cfg")
        else:
            self.mgr_config_file = "./Timer/Config/Latest.cfg"

        self.default_config = {
            "subjects": {},
            "shows": [],
            "settings": {
                "text": "期末考试"  # 科目后提示的文本
            },
            "debug": {
                "level": "debug"  # 日志输出等级 (不支持热加载)
            }
        }

        self.mgr_error_interval: float = 10
        self.mgr_remove_error_time = 30
        self.mgr_remove_interval: float = 3

        self.fonts_range = range(500, 0, -10)  # 加载字体字号范围
        self.font_file = r"resources\font\font.ttf"
        # 字体字典 {%字号%: %pygame.font.Font%}
        self.fonts = {}
        self.load_fonts_thread = Thread(target=self.load_fonts, daemon=True)
        self.load_fonts_thread.start()  # 多线程加载

    def load_fonts(self):
        for size in self.fonts_range:
            try:
                self.fonts[size] = font.Font(self.font_file, size)
            except Exception as e:
                print(e)
        self.fonts[1] = font.Font(self.font_file, 1)

    @staticmethod
    def get_loglevel(string: str, default=None):
        """
        获取日志级别 by string
        :param string: 级别 (大小写不敏感)
        :param default: 默认返回值
        :return: logging 级别 / None
        """
        string = string.upper()  # 转大写
        return {  # 获取到返回, 获取失败返回None
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRIT": logging.CRITICAL,
            "CRITICAL": logging.CRITICAL
        }.get(string, default)


class Model:
    """
    配置文件内容
    """

    def __init__(self, appconfig_obj: Appconfig):
        self.__appconfig = appconfig_obj
        self.__config_dict = self.__appconfig.default_config.copy()
        self.__subjects = {}
        self.error = None

    @property
    def config_dict(self):
        self.__appconfig.default_config.copy().update(self.__config_dict)  # 添加没有项
        return self.__config_dict

    @config_dict.setter
    def config_dict(self, value: dict):
        if type(value) == dict:  # 如果value合法
            self.__config_dict.update(value)  # 更新字典

    @property
    def subjects(self):
        return self.__subjects

    @subjects.setter
    def subjects(self, value: dict):
        self.__subjects = value.copy()
