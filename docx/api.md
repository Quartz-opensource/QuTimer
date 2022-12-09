# api内容
* 请求方式: get + 传参
* 返回示例:
```
result = {
        "code": 200,  // 返回码, int, 正常为 200
        "msg": "ok", // 错误信息(正常为"ok") 
        "result": "" // 您的返回值 (默认为""空字符串)
    }
```


## `/`
* 获取运行状态, 正常为
```
result = {
        "code": 200,
        "msg": "ok",
        "result": "{你请求的内容}"
    }
```

## `api/get_config`
* 返回配置文件所有内容
* 参数: 无
* 返回: 配置文件(json格式)

## `/api/get_key`
* 获取配置文件指定键
* 参数: `key`, `default`:
    * `key`: str, 样式`{键}.{子键}/[{value index}].{子键}/[{value index}]`
    * 示例: `/api/get_config?key=debug.port //  获取debug键的port子键`
    * `default`: str, 当未找到时返回此值, 默认为""空字符串
* 返回: 指定键的值, 任何json支持的格式

## `/api/get_event`
* 获取当前事件
* 参数: 无
* 返回: 当前事件字符串, str

## `/api/set_config`
* 设置并写入文件
* 参数: `value`: 
    * `value`: json格式字符串, 要写入的config, 注意子项会被直接覆盖而非增加
* 返回: 无
