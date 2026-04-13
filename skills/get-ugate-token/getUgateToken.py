#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
获取并缓存 ugate token（多用户版本，永久有效）
"""

import os
import sys
import json
import re
from pathlib import Path

# 配置常量
CACHE_DIR = Path.home() / ".config" / "uuap"

# 强制刷新的关键词
FORCE_REFRESH_KEYWORDS = [
    "重新生成ugate",
    "刷新ugate",
    "重新生成 ugate",
    "刷新 ugate",
    "强制刷新",
    "重新获取",
    "重新生成token",
    "刷新token",
    "重新生成 token",
    "刷新 token",
    "强制刷新token",
    "忽略缓存",
]


def get_cache_file(username):
    """根据用户名获取对应的缓存文件路径"""
    return CACHE_DIR / f".eac_ugate_token_{username}"


def should_force_refresh(user_message):
    """检查用户消息是否包含强制刷新的关键词"""
    if not user_message:
        return False

    user_message_lower = user_message.lower()
    return any(keyword in user_message_lower for keyword in FORCE_REFRESH_KEYWORDS)


def extract_manual_token(user_message):
    """
    从用户消息中提取手动输入的 token
    支持格式：ugate token: xxxx 或 ugate token：xxxx（中文冒号）
    
    Returns:
        str: 提取到的 token，如果格式不匹配则返回 None
    """
    if not user_message:
        return None

    # 支持中英文冒号，支持大小写
    pattern = r'ugate\s+token\s*[:：]\s*(\S.+)'
    match = re.search(pattern, user_message, re.IGNORECASE)
    
    if match:
        return match.group(1).strip()
    
    return None


def get_cached_token(username):
    """
    从缓存读取 token
    
    如果缓存文件中存在 expires_at 字段，则认为 token 无效，返回 None
    """
    cache_file = get_cache_file(username)

    if not cache_file.exists():
        return None

    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)

        # 如果存在 expires_at 字段，认为 token 无效
        if 'expires_at' in data:
            return None

        token = data.get('token')
        if not token:
            return None

        return token
    except (json.JSONDecodeError, KeyError):
        pass

    return None


def save_token_to_cache(token, username):
    """
    将 token 保存到缓存（永久有效）
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = get_cache_file(username)

    with open(cache_file, 'w') as f:
        cache_data = {
            'token': token,
            'permanent': True,  # 所有 token 都是永久有效
        }
        json.dump(cache_data, f)


def main():
    """主函数"""
    # 从命令行参数获取用户名
    if len(sys.argv) < 2:
        print("请输入您的邮箱前缀（例如：chenshouqin）", file=sys.stderr)
        sys.exit(1)

    username = sys.argv[1]

    # 获取用户消息（用于判断是否强制刷新或手动输入 token）
    user_message = os.environ.get('USER_MESSAGE', '')

    # 1. 检查用户是否手动输入了 token（格式：ugate token: xxxx）
    manual_token = extract_manual_token(user_message)
    if manual_token:
        # 保存到缓存（永久有效）
        save_token_to_cache(manual_token, username)
        print(f"TOKEN_SAVED:Token 已保存", file=sys.stderr)
        print(manual_token)
        return

    # 2. 检查是否需要强制刷新
    force_refresh = should_force_refresh(user_message)

    # 3. 尝试从缓存获取（除非强制刷新）
    if not force_refresh:
        cached_token = get_cached_token(username)
        if cached_token:
            print(cached_token)
            return

    # 4. 缓存不存在或强制刷新，提示用户手动获取 token
    print(f"NEED_MANUAL_TOKEN:请点击 https://uuap.baidu.com/agent/token 获取token，然后复制内容发送给我", file=sys.stderr)
    sys.exit(2)


if __name__ == "__main__":
    main()
