#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-prd-split 使用数据收集工具
"""

import json
import ssl
import subprocess
from datetime import datetime
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError


# API 配置
API_URL = "https://wf-test.dev.weiyun.baidu.com/pioneer/card/devops/log/storage"

# 默认参数
DEFAULTS = {
    "bizId": "智能拆卡助手",
    "robot": "12345",
    "robot_name": "智能拆卡助手",
    "groupId": "0",
    "action": "ai-prd-split",
    "eventId": "ai-prd-split",
    "result": "",
    "source": "comate",
    "query": "",
}


def get_trigger_name() -> str:
    """自动获取触发人用户名"""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True, text=True, timeout=3
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass
    return ""


def log(card_ids: str = "", trigger_name: str = "") -> dict:
    """
    发送使用日志

    Args:
        card_ids: 创建的卡片ID，多个用逗号分隔（如 "joytest-5181,joytest-5182"）
        trigger_name: 触发用户姓名

    Returns:
        响应结果
    """
    body = {
        **DEFAULTS,
        "cardId": card_ids,
        "triggerName": trigger_name,
        "triggerTime": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "result": str(len([c for c in card_ids.split(",") if c.strip()])) if card_ids else "0",
    }

    req = Request(
        API_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urlopen(req, timeout=10, context=ctx) as resp:
            return {"success": True, "status": resp.status}
    except HTTPError as e:
        return {"success": False, "error": f"HTTP {e.code}"}
    except URLError as e:
        return {"success": False, "error": str(e.reason)}


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="ai-prd-split 使用数据收集")
    parser.add_argument("--card-ids", default="", help="卡片ID，多个用逗号分隔")
    parser.add_argument("--trigger-name", default="", help="触发用户姓名")

    args = parser.parse_args()
    trigger = args.trigger_name or get_trigger_name()
    result = log(card_ids=args.card_ids, trigger_name=trigger)
    print(json.dumps(result, ensure_ascii=False))
