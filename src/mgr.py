# 第三方包
import logging
from time import time, mktime, strptime, strftime
from threading import Thread
from typing import Optional

# 本地包
from appconfig import Appconfig, Model
from staticTools import write_json, read_json

# 初始化
logger = logging.getLogger("mgr")


class Mgr:
    def __init__(self, appconfig_obj: Appconfig, config_obj: Model):
        self.__update_thread: Optional[Thread] = None
        self.__appconfig = appconfig_obj
        self.__config = config_obj

        self.__error_dict = {}
        self.__latest_del_time = time()
        self.__shift_error = (0, {})
        self.__subjects_list = [
            [],
            []
        ]

    def __del_error_dict_thread(self):
        t = Thread(target=self.__del_error_dict, daemon=True)
        t.start()
        return t

    def __del_error_dict(self):
        for k, v in self.__error_dict.copy().items():
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
        if self.__update_thread is None or not self.__update_thread.is_alive():
            self.__update_thread = Thread(target=self.__shift_subjects_call, daemon=True)  # 更新时间戳字典
            self.__update_thread.start()
        if self.__shift_error[0] != 0 and abs(time() - self.__error_dict.get("shift_error", 0)) > \
                self.__appconfig.mgr_error_interval:
            self.__dict_to_log(self.__shift_error[1], tips="转化为时间戳")
            self.__error_dict["shift_error"] = time()

    def __shift_subjects_call(self):
        self.__shift_error = self.__shift_subjects()

    def __shift_subjects(self) -> tuple[int, any]:
        """
        将时间转为时间戳subjects
        :return: tuple[int, any]
        return_code: 0 -> 正常, -1 -> 未找到, -2 -> 运行时错误, -3 -> 列表更新错误;
        """
        errors = {}
        e_code = 0
        subjects = self.__config.config_dict.get("subjects", None)

        if subjects is None:
            return -1, RuntimeError("Subjects not found")
        else:
            for k, v in list(subjects.items()):
                k: str
                v: list
                if type(v) == list and len(v) == 2:
                    try:
                        start_timestamp = int(mktime(strptime(v[0], "%Y-%m-%d %H:%M:%S")))
                        end_timestamp = int(mktime(strptime(v[1], "%Y-%m-%d %H:%M:%S")))
                        self.__config.subjects[k] = [start_timestamp, end_timestamp]
                        if k not in self.__subjects_list[0] and v not in self.__subjects_list[1]:
                            self.__subjects_list[0].append(k)
                            self.__subjects_list[1].append([start_timestamp, end_timestamp])
                        else:
                            try:
                                index = self.__subjects_list[0].index(k)
                                self.__subjects_list[0][index] = k
                                self.__subjects_list[1][index] = [start_timestamp, end_timestamp]
                            except Exception as e:
                                e_code = -3
                                errors[k] = (RuntimeError("Subject \"{}\" update error: {}"
                                                          .format(k, repr(e).replace("'", '"'))), e)
                    except Exception as e:
                        e_code = -2
                        errors[k] = (RuntimeError("Subject \"{}\" start time or end time error: {}"
                                                  .format(k, repr(e).replace("'", '"'))), e)
                else:
                    del subjects[k]  # 不符合预期的直接删掉
                    e_code = -2
                    errors[k] = (RuntimeError("Subject \"{}\" (\"{}\") not expected".format(k, v)), None)

        self.__config.subjects = subjects.copy()
        return e_code, errors

    @staticmethod
    def __dict_to_log(target_dict: dict, tips: str = ""):
        def tmp():
            for k, v in list(target_dict.items()):
                try:
                    logger.error("{}(\"{}\")错误:".format(tips, k), exc_info=v[0])
                except Exception as e:
                    pass

        t = Thread(target=tmp, daemon=True)
        t.start()
        return t

    def __get_tips_string(self) -> str:
        return self.__config.config_dict.get(
            "settings",
            self.__appconfig.default_config["settings"]
        ).get(
            "text", self.__appconfig.default_config["settings"]["text"]
        )

    def get_event(self) -> str:
        now = time()
        for subject_name, (start, end) in zip(*self.__subjects_list):
            if start <= now <= end + 60.5:
                show_times = self.__config.config_dict.get("shows", self.__appconfig.default_config["shows"])
                for show_time in show_times:
                    remaining_time = end - now
                    # print(remaining_time, show_time)
                    if "all" in show_times:  # 如果 "all" 在 show_times, 则优先显示所有
                        show_time = "all"
                    if show_time == -1:
                        if 0 >= remaining_time >= -60.5:
                            tips_string = self.__get_tips_string()
                            return "{}{}结束".format(subject_name, tips_string)
                    elif show_time == "all" or (type(show_time) == float and show_time >= remaining_time and
                                                abs(show_time - remaining_time) <= 60.5):
                        tips_string = self.__get_tips_string()
                        if remaining_time < 0:
                            return "{}{}结束".format(subject_name, tips_string)
                        elif show_time != 0:
                            return "距离{}{}结束还有{}分钟" \
                                .format(subject_name, tips_string, format(round(remaining_time / 60, 1), ".1f"))
                        else:
                            return "{}{}开始".format(subject_name, tips_string)
        return ""
