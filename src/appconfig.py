from pygame import image

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
