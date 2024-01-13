from datetime import datetime, timedelta
from loguru import logger
from pathlib import Path
from typing import Any
import httpx


data_path = Path("../data")

def get_china_time() -> str:
    return (datetime.utcnow() + timedelta(hours=8)).strftime('%H:%M:%S')

def get_china_date() -> str:
    return (datetime.utcnow() + timedelta(hours=8)).strftime('%Y-%m-%d')

def get_today_info() -> dict[str, Any]:
    china_date = get_china_date()
    query_url = f"http://tool.bitefu.net/jiari/?d={china_date}&info=1"
    logger.debug(f"正在获取本日({china_date})信息...")
    try:
        resp_info = httpx.get(query_url).json()
    except Exception as e:
        logger.error(f"请求节假日接口时出错，错误信息：{e}")
        raise
    if resp_info.get("status") != 1:
        logger.error(f"请求节假日接口异常，返回内容：{resp_info}")
        raise ValueError()
    return resp_info