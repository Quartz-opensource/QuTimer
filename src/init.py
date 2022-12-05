# 第三方包
from os import path as ospath
import logging

# 本地包
from appconfig import Appconfig, Model
from staticTools import create_file, read_json, write_json

appconfig = Appconfig()
config = Model(appconfig)


def init_logging(loglevel):
    logging.basicConfig(level=loglevel,
                        filename="latest.log",
                        datefmt="%Y-%m-%d %H:%M:%S",
                        format="[%(asctime)s] [%(levelname)s] Pid: %(process)d "
                               "Thread: %(thread)d ThreadName: %(threadName)s"
                               " In %(filename)s, Line %(lineno)s:\n\t%(message)s ",
                        encoding="UTF-8"
                        )


if not ospath.exists(appconfig.mgr_config_file) or ospath.isdir(appconfig.mgr_config_file):  # 文件不存在或文件是文件夹
    create_file(appconfig.mgr_config_file, cover_file=True, def_info="")  # 创建配置文件
    return_code, err_info = write_json(appconfig.mgr_config_file, appconfig.default_config)
    if return_code != 0:
        log_level = appconfig.get_loglevel(appconfig.default_config["debug"]["level"])
        init_logging(log_level)
        logger = logging.getLogger("init")
        logger.error("写入配置文件发生错误:", exc_info=err_info)
else:
    return_code, json_info = read_json(appconfig.mgr_config_file)
    if return_code != 0:  # 读取失败
        log_level = appconfig.get_loglevel(appconfig.default_config["debug"]["level"])
        init_logging(log_level)
        logger = logging.getLogger("init")
        logger.error("读取配置文件错误(已更改为默认内容): {}".format(str(json_info)))
        return_code, err_info = write_json(appconfig.mgr_config_file, appconfig.default_config)
        if return_code != 0:
            logger.error("写入配置文件发生错误(已更改为默认内容):", exc_info=err_info)
    else:  # 读取成功
        json_info: dict
        config.config_dict = json_info
        log_level = appconfig.get_loglevel(
            json_info.get("debug", {}).get("level", appconfig.default_config["debug"]["level"]), logging.INFO)
        init_logging(log_level)
        logger = logging.getLogger("init")
        logger.debug("配置文件\"({})\"读取成功".format(appconfig.mgr_config_file))
