from typing import Literal, Any, Optional
from dataclasses import dataclass, field

@dataclass
class MessageSegment:    

    # TODO: 仅考虑了简单的信息发送，不包含以下消息：
    # 【难以获取接口权限】
    # 发送群名片：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot#发送群名片
    # 发送图片：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot#发送图片
    # 此外，at 用户也难以获取用户 id：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot#9eb9367
    # 【需要设计新类型】
    # 发送消息卡片：https://open.feishu.cn/document/client-docs/bot-v3/add-custom-bot#发送消息卡片

    tag: Literal["text", "a", "at", "img", "delimiter"]
    '''消息段类型'''

    data: dict[str, Any] = field(default_factory=dict)
    '''消息段必要信息'''

    extra: dict[str, Any] = field(default_factory=dict)
    '''消息段非必要信息，将不会影响 export 结果'''

    @staticmethod
    def text(text: str, un_escape: Optional[bool] = None) -> 'MessageSegment':
        if un_escape is not None:
            return MessageSegment(
                "text",
                {
                    "text": text,
                    "un_escape": un_escape
                }
            )
        return MessageSegment(
            "text",
            {"text": text}
        )

    @staticmethod
    def a(text: str, href: str) -> 'MessageSegment':
        return MessageSegment(
            "a",
            {"text": text, "href": href}
        )

    @staticmethod
    def at(user_id: str, user_name: Optional[str] = None) -> 'MessageSegment':
        '''
        at 消息段。
        在 at 全员时，user_id 应为 all.
        '''
        if user_name is not None:
            return MessageSegment(
                "at",
                {
                    "user_id": user_id,
                    "user_name": user_name
                }
            )
        return MessageSegment(
            "at",
            {"user_id": user_id}
        )
    
    @staticmethod
    def img(image_key: str) -> 'MessageSegment':
        return MessageSegment(
            "img",
            {"image_key": image_key}
        )

    @staticmethod
    def delimiter():
        '''
        分段符。
        仅用于分段。
        在 post 模式下表现为额外的换行符，在 text 模式下表现为空字符串，拼接后可能产生换行。
        '''
        return MessageSegment("delimiter")
    
    def post_export(self) -> dict[str, Any]:
        if self.tag == "delimiter":
            return MessageSegment.text("").post_export()
        res = self.data.copy()
        res.update({"tag": self.tag})
        return res

@dataclass
class Message:

    mss: list[MessageSegment] = field(default_factory=list)

    type: Literal["text", "post"] = "post"

    language: Literal["zh_cn", "en_us"] = "zh_cn"

    title: Optional[str] = None

    def export(self, type: Optional[Literal["text", "post"]] = None) -> dict[str, Any]:
        if type is None:
            type = self.type
        if type == "text":
            ms_texts = []
            for ms in self.mss:
                if ms.tag == "text":
                    ms_texts.append(ms.data.get("text", ""))
                elif ms.tag == "a":
                    ms_texts.append(f"【{ms.data.get('text')}】{ms.data.get('href')}")
                elif ms.tag == "at":
                    if ms.data.get("user_id") == "all":
                        ms_texts.append(f"<at user_id=\"{ms.data.get('user_id')}\">{ms.data.get('user_name', '所有人')}</at>")
                    else:
                        ms_texts.append(f"<at user_id=\"{ms.data.get('user_id')}\">{ms.data.get('user_name', '用户')}</at>")
            return {
                "msg_type": "text",
                "content": {
                    "text": "\n".join(ms_texts)
                }
            }
        elif type == "post":
            if self.title is not None:
                title_info = {"title": self.title}
            else:
                title_info = {}
            content = []
            index = 0
            for i in range(len(self.mss)):
                if self.mss[i].tag == "delimiter":
                    content.append([ms.post_export() for ms in self.mss[index:i]])
                    index = i+1
                elif i == len(self.mss)-1:
                    content.append([ms.post_export() for ms in self.mss[index:i+1]])
            return {
                "msg_type": "post",
                "content": {
                    "post": {
                        self.language: {
                            **title_info,
                            "content": content
                        }
                    }
                }
            }