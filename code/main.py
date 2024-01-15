from loguru import logger
import schedule
import random
import time
import json

from message import Message, MessageSegment
from bot import Bot
from utils import (
    data_path,
    get_china_time,
    get_today_info
)


webhook_url = ""

bot = Bot(
    webhook_url
)

# bot.send(
#     Message([
#         MessageSegment.text("*测试*"),
#         MessageSegment.delimiter(),
#         MessageSegment.text("第二**段**文本"),
#         MessageSegment.delimiter(),
#         ], title="这是一个测试", type="text")
# )


@schedule.repeat(schedule.every().day.at("11:20"), time_segment = "中午")
@schedule.repeat(schedule.every().day.at("18:30"), time_segment = "晚上")
def eat_remind(time_segment: str = ""):
    try:
        resp_info = get_today_info()
    except Exception as e:
        return
    if resp_info.get("type") != 0:
        logger.debug("本日不是工作日，已忽略任务...")
        return
    with open(data_path / "what2eat.json", "r", encoding="utf-8-sig") as f:
        dish_info = json.load(f).get("data")
    dish_choose: list[dict] = random.choices(dish_info, k = 5)
    dish_text = "\n".join(
        [f"{i+1}. 【{dish.get('type')}】{dish.get('name')}\n地点：{dish.get('place')} | 价格：{dish.get('price')}\n" \
         for i, dish in enumerate(dish_choose)]
    )
    bot.send(
        Message(
                [
                    MessageSegment.text(
                        f"已经是{time_segment}{get_china_time()}了，\n"
                        "要准备吃饭了吗~\n"
                        "\n"
                        "如果不知道吃什么，那么现在推荐的菜品有——\n"
                        # "1. 【堂食】迷宫饭 家的\n水煮大蝎子走路菇火锅！！  (￥0)\n"
                        # "2. 【堂食】迷宫饭 家的\n食人植物水果塔  (￥0)\n"
                        # "3. 【堂食】迷宫饭 家的\n炸什锦曼德拉草与大蝙蝠天妇罗  (￥0)\n"
                        # "4. 【堂食】迷宫饭 家的\n会动的铠甲全餐  (￥0)\n"
                        # "5. 【堂食】迷宫饭 家的\n祈求消灾解厄！除灵雪酪  (￥0)\n"
                        f"{dish_text}"
                        "\n"
                        f"那么，今天{time_segment}也要好好干饭哦~！！"
                    )
                ],
            title = f"{time_segment}的干饭提醒~"
        )
    )

@schedule.repeat(schedule.every().day.at("09:30"))
def start_remind():
    try:
        resp_info = get_today_info()
    except Exception as e:
        return
    if resp_info.get("type") != 0:
        logger.debug("本日不是工作日，已忽略任务...")
        return
    bot.send(
        Message(
                [
                    MessageSegment.at("all"),
                    MessageSegment.delimiter(),
                    MessageSegment.text(
                        f"现在是{get_china_time()}，\n"
                        f"要准备开始今天的工作了！！\n"
                        "\n"
                        "去工位前要记得打卡哦~"
                    )
                ],
            title = "上班打卡提醒~"
        )
    )

@schedule.repeat(schedule.every().day.at("18:55"))
def end_remind():
    try:
        resp_info = get_today_info()
    except Exception as e:
        return
    if resp_info.get("type") != 0:
        logger.debug("本日不是工作日，已忽略任务...")
        return
    bot.send(
        Message(
                [
                    MessageSegment.at("all"),
                    MessageSegment.delimiter(),
                    MessageSegment.text(
                        f"已经是{get_china_time()}了，\n"
                        "工作不要忘了时间√\n"
                        "\n"
                        "下班要记得打卡哦~"
                    )
                ],
            title = "临下班打卡提醒~"
        )
    )

while True:
    schedule.run_pending()
    time.sleep(10)