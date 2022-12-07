# 第三方包
import logging
import pygame
import sys
from threading import Thread
from time import sleep

# 本地包
from init import appconfig, config
from mgr import Mgr
from ui import Ui

# 初始化
logger = logging.getLogger("main")
pygame.init()

ui = Ui(appconfig)
mgr = Mgr(appconfig, config)
Thread(name="pygame-Ui", target=ui.mainloop, daemon=True).start()
quit_events = []
while True:
    if len(quit_events) > 0:
        ui.stop = True
        sys.exit(0)
    # print(config.config_dict, mgr.__dict__)
    mgr.read_file()
    # print(config.config_dict)
    ui.font_text = mgr.get_event()
    # pygame.display.update()
    quit_events = pygame.event.get(pygame.QUIT)
    sleep(0.1)
