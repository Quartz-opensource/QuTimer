# 第三方包
import logging
from time import time
from threading import Thread

# 本地包
from init import appconfig, config
from appconfig import Appconfig, Model
from staticTools import write_json, read_json

# 初始化
logger = logging.getLogger("mgr")


class Mgr:
    def __init__(self, appconfig_obj: Appconfig, config_obj: Model):
        self.__appconfig = appconfig_obj
        self.__config = config_obj

        self.__error_dict = {}
        self.__latest_del_time = time()

    def __del_error_dict_thread(self):
        t = Thread(target=self.__del_error_dict, daemon=True)
        t.start()
        return t

    def __del_error_dict(self):
        for k, v in self.__error_dict.items():
            if abs(time() - v) >= self.__appconfig.mgr_remove_error_time:  # 大于移除时间
                self.__error_dict.pop(k)  # 删除

    def write_file(self):
        return_code, error = write_json(self.__appconfig.mgr_config_file, self.__config.config_dict)
        if return_code != 0:
            logger.error("读取文件错误:", exc_info=error)
            self.__config.error = error

    def read_file(self):
        return_code, info = read_json(self.__appconfig.mgr_config_file)
        if return_code != 0:
            type_info = type(info)
            if type_info not in self.__error_dict.keys():
                logger.error("热加载文件错误:", exc_info=info)
                self.__error_dict[type_info] = time()
            elif abs(time() - self.__error_dict.get(type_info, 0)) > self.__appconfig.mgr_error_interval:
                logger.error("热加载文件错误(错误输出间隔{}s):".format(self.__appconfig.mgr_error_interval),
                             exc_info=info)
                self.__error_dict[type_info] = time()
            self.__config.error = info
        else:
            self.__config.config_dict = info.copy()
        if abs(time() - self.__latest_del_time) > self.__appconfig.mgr_remove_interval:
            self.__del_error_dict_thread()


if __name__ == '__main__':
    test = Mgr(appconfig, config)
    # while True:
    test.read_file()
    print(config.config_dict)
