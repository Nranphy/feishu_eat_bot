from typing import Literal, Union, Optional
import hashlib
from loguru import logger
import base64
import httpx
import hmac
import time

from message import Message, MessageSegment

class Bot:

    webhook_url: str

    secret: Optional[str] = None

    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url
        logger.info("实例化 Bot 成功！")

    def send(
            self,
            msg: Union[Message, MessageSegment, list[MessageSegment]],
            type: Optional[Literal["text", "post"]] = None
        ):
        if not isinstance(msg, Message):
            if isinstance(msg, list):
                msg = Message(msg)
            elif isinstance(msg, MessageSegment):
                msg = Message([msg])
        post_content = msg.export(type)
        logger.debug("Bot 发送消息中...")
        try:
            response = httpx.post(
                self.webhook_url,
                headers = {
                    "Content-Type": "application/json"
                },
                json = post_content
            )
            logger.info(f"Bot 发送消息请求成功，请求状态：{response.status_code}")
            resp_info:dict = response.json()
            if resp_info.get("code") == 0:
                logger.success(f"消息发送成功~！！返回代码为 {resp_info.get('code')}，返回信息为 {resp_info.get('msg')}")
            else:
                logger.error(f"Bot 发送消息失败，错误代码为 {resp_info.get('code')}，错误信息为 {resp_info.get('msg')}")
        except Exception as e:
            logger.error(f"Bot 发送消息请求出错，错误信息：{e}")

    def gen_sign(self):
        timestamp = time.time()
        string_to_sign = '{}\n{}'.format(timestamp, self.secret)
        hmac_code = hmac.new(string_to_sign.encode("utf-8"), digestmod=hashlib.sha256).digest()
        sign = base64.b64encode(hmac_code).decode('utf-8')
        return sign