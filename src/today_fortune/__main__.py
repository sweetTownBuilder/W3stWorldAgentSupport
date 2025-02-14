import hashlib
import time
import json
import requests
from typing import Dict, Any


def main(appid: str, app_security: str, star: str, date: str = None) -> Dict[str, Any]:
    """
    查询星座信息的优化版本

    :param appid: 应用程序ID
    :param app_security: 应用安全密钥
    :param star: 包含星座信息的JSON字符串（需含astrologicalSign字段）
    :param date: 查询日期（可选，格式YYYY-MM-DD）
    :return: 包含API响应或错误信息的字典
    """
    star_data = json.loads(star)
    astrological_sign = star_data["astrologicalSign"]

    # 构造请求数据
    timestamp = int(time.time() * 1000)
    sign_str = f"{appid}&{timestamp}&{app_security}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()

    payload = {
        "appid": appid,
        "timestamp": timestamp,
        "sign": sign,
        "star": astrological_sign,
        "date": date or ""  # 处理空日期参数
    }

    # 带超时设置的API请求
    response = requests.post(
        "https://api.shumaidata.com/v10/constellation/query",
        data=payload,
        timeout=10  # 设置10秒超时
    )
    response.raise_for_status()  # 检查HTTP错误状态码

    return {
        "result": response.text
    }


# 示例调用
if __name__ == "__main__":
    # 示例参数（需要替换为真实值）
    sample_star = json.dumps({
        "astrologicalSign": "shizi"
    })

    result = main(
        appid="",
        app_security="",
        star=sample_star,
        date=""
    )

    print(result)