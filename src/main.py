# 第三方包
from threading import Thread
from time import sleep
from json import dumps, loads
from flask import Flask, request

# 本地包
from staticTools import is_num
from mgr import Mgr
from init import appconfig, config

app = Flask(__name__, template_folder="./resources/templates", )


@app.route("/")
def index():
    result = {
        "code": 200,
        "msg": "ok",
        "result": ""
    }
    return dumps(result, ensure_ascii=False)


@app.route("/api/get_config/")
def get_config():
    mgr.read_file()
    result = {
        "code": 200,
        "msg": "ok",
        "result": config.config_dict
    }
    return dumps(result, ensure_ascii=False)


@app.route("/api/get_key/")
def get_key():
    key = request.values.get("key")
    default = request.values.get("default")
    if default is None:
        default = ""
    mgr.read_file()
    if key is not None:
        result = {
            "code": 200,
            "msg": "ok",
            "result": mgr.get_config(key, default)
        }
    else:
        result = {
            "code": 400,
            "msg": "argument 'key' not found",
            "result": ""
        }
    return dumps(result, ensure_ascii=False)


@app.route("/api/get_event/")
def get_event():
    mgr.read_file()
    result = {
        "code": 200,
        "msg": "ok",
        "result": mgr.get_event()
    }
    return dumps(result, ensure_ascii=False)


@app.route("/api/set_config/")
def set_config():
    value = request.values.get("value")
    if value is not None:
        try:
            value = loads(value)
        except Exception as e:
            result = {
                "code": 400,
                "msg": "error: {}".format(repr(e)),
                "result": ""
            }
            return dumps(result, ensure_ascii=False)
    else:
        result = {
            "code": 400,
            "msg": "argument 'value' not found",
            "result": ""
        }
        return dumps(result, ensure_ascii=False)
    config.config_dict = value
    mgr.write_file()
    mgr.read_file()
    result = {
        "code": 200,
        "msg": "ok",
        "result": ""
    }
    return dumps(result, ensure_ascii=False)


@app.errorhandler(404)  # 404 界面
def error_404(err_info):
    result = {
        "code": 400,
        "msg": "page not found: 404",
        "result": ""
    }
    return dumps(result, ensure_ascii=False)


def reload_config():
    while True:
        mgr.read_file()
        sleep(0.1)


if __name__ == "__main__":
    mgr = Mgr(appconfig, config)
    reload_thread = Thread(target=reload_config, daemon=True)
    reload_thread.start()

    port = mgr.get_config("debug.port")
    if port is not None and is_num(port, _type="int"):
        app.run(host=appconfig.website.get("host", "0.0.0.0"), port=port, debug=appconfig.website.get("debug", False))
    else:
        app.run(host=appconfig.website.get("host", "0.0.0.0"), port=appconfig.website.get("default-port", None),
                debug=appconfig.website.get("debug", False))
