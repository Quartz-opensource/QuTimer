import logging

from pygame import image
from os import getenv, path as ospath


class Appconfig:
    def __init__(self):
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

    def __init__(self):
        self.config_dict = {}
