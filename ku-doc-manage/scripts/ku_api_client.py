#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库开放API Python客户端
基于SKILL.md文档开发
支持：查询文档内容、查询文档列表、创建文档、查询权限等
支持两种认证方式（自动降级）：
1. 个人身份认证（默认，需要 ugate-token）
   - ugate-token: 优先从 ~/.config/uuap/.eac_ugate_token_{username} 读取，认证失败时从 get-ugate-token SKILL 获取
   - username: 从环境变量 SANDBOX_USERNAME 或 BAIDU_CC_USERNAME 获取
2. 数字员工身份认证（使用 AK/SK）
"""

import os
import sys
import yaml
import json
import tempfile
import requests
import subprocess
from pathlib import Path
from typing import Optional, List, Dict, Any


class KuApiClient:
    """知识库开放API客户端"""

    # 定义两种认证方式的URL
    BASE_URL_XIAOLONGXIA = 'https://apigo.baidu-int.com/wiki/so'  # 个人身份认证
    BASE_URL_DIGITAL = 'https://ku.baidu-int.com/wiki/so'  # 数字员工认证


    @staticmethod
    def _load_config() -> Dict[str, Any]:
        """
        从config.yaml文件读取认证配置

        Returns:
            dict: 包含xiaolongxia_auth和digital_auth的字典，如果读取失败返回空字典
        """
        try:
            # 获取config.yaml文件路径（在scripts目录）
            current_dir = Path(__file__).parent
            config_path = current_dir / 'config.yaml'

            if not config_path.exists():
                return {}

            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)

            result = {}

            # 读取个人身份认证配置
            if config and 'xiaolongxia_auth' in config:
                xiaolongxia_auth = config['xiaolongxia_auth']
                result['xiaolongxia_auth'] = {
                    'enabled': xiaolongxia_auth.get('enabled', True)
                }

            # 读取数字员工认证配置
            if config and 'digital_auth' in config:
                digital_auth = config['digital_auth']
                result['digital_auth'] = {
                    'ak': digital_auth.get('ak', ''),
                    'sk': digital_auth.get('sk', '')
                }

            return result
        except Exception as e:
            print(f"⚠️  从config.yaml读取配置失败: {e}")

        return {}

    def __init__(self, base_url: str = None, ak: str = None, sk: str = None,
                 auth_mode: str = "auto"):
        """
        初始化API客户端

        Args:
            base_url: API基础URL，如果不指定则根据auth_mode自动选择
            ak: Access Key，用于数字员工身份认证
            sk: Secret Key，用于数字员工身份认证
            auth_mode: 认证模式，可选值：
                - "auto": 自动降级（默认，依次尝试: 个人身份认证 -> 数字员工）
                - "xiaolongxia": 仅使用个人身份认证
                - "digital": 仅使用数字员工身份认证
        """
        self.auth_mode = auth_mode
        self.current_auth_method = None  # 当前使用的认证方式
        self.tried_auth_methods = []  # 已尝试过的认证方式

        # 从config.yaml读取配置
        self.config = self._load_config()

        # 初始化各种认证凭证
        self.xiaolongxia_token = None
        self.xiaolongxia_token_refreshed = False  # 标记是否已经尝试过刷新 ugate-token
        self.ak = ak
        self.sk = sk

        # 根据认证模式初始化
        if auth_mode == "auto":
            # 自动模式：依次尝试两种认证方式
            self._init_auto_auth()
        elif auth_mode == "xiaolongxia":
            self._init_xiaolongxia_auth()
        elif auth_mode == "digital":
            self._init_digital_auth()
        else:
            raise ValueError(f"不支持的认证模式: {auth_mode}，可选值: auto, xiaolongxia, digital")

        # 设置base_url
        if base_url:
            self.base_url = base_url
        else:
            self.base_url = self._get_base_url_for_current_auth()

    def _get_base_url_for_current_auth(self) -> str:
        """根据当前认证方式获取对应的base_url"""
        if self.current_auth_method == "xiaolongxia":
            return self.BASE_URL_XIAOLONGXIA
        elif self.current_auth_method == "digital":
            return self.BASE_URL_DIGITAL
        # 默认返回个人身份认证URL
        return self.BASE_URL_XIAOLONGXIA

    def _init_auto_auth(self):
        """自动认证模式：依次尝试两种认证方式"""
        # 第一优先级：个人身份认证
        if self._try_init_xiaolongxia_auth():
            return

        # 第二优先级：数字员工认证
        if self._try_init_digital_auth():
            return

        # 如果都失败，使用个人身份认证（让后续请求时再处理错误）
        print("\n" + "=" *  70)
        print("⚠️  所有认证方式初始化都失败，将使用个人身份认证方式（可能需要配置）")
        print("=" *  70)
        self.current_auth_method = "xiaolongxia"

    def _init_xiaolongxia_auth(self):
        """初始化个人身份认证"""
        if not self._try_init_xiaolongxia_auth():
            raise ValueError("个人身份认证初始化失败，请检查config.yaml中的xiaolongxia_auth配置")

    def _init_digital_auth(self):
        """初始化数字员工认证"""
        if not self._try_init_digital_auth():
            raise ValueError("数字员工认证初始化失败，请检查config.yaml中的digital_auth配置")

    def _try_init_xiaolongxia_auth(self) -> bool:
        """尝试初始化个人身份认证，成功返回True"""
        try:
            xiaolongxia_config = self.config.get('xiaolongxia_auth', {})
            if not xiaolongxia_config.get('enabled', True):
                return False

            # 个人身份认证只需要启用即可，用户身份由 get-ugate-token SKILL 自己处理
            self.current_auth_method = "xiaolongxia"
            return True
        except Exception as e:
            print(f"⚠️  个人身份认证初始化失败: {e}", file=sys.stderr)
            return False

    def _try_init_digital_auth(self) -> bool:
        """尝试初始化数字员工认证，成功返回True"""
        try:
            digital_config = self.config.get('digital_auth', {})
            ak = self.ak or digital_config.get('ak', '')
            sk = self.sk or digital_config.get('sk', '')

            if not ak or not sk:
                return False

            self.ak = ak
            self.sk = sk
            self.current_auth_method = "digital"
            return True
        except Exception as e:
            print(f"⚠️  数字员工认证初始化失败: {e}", file=sys.stderr)
            return False

    @staticmethod
    def _get_current_username() -> str:
        """
        获取当前用户名
        优先级：
        1. SANDBOX_USERNAME > BAIDU_CC_USERNAME 环境变量
        2. 如果环境变量未设置，引导用户输入用户名

        Returns:
            str: 用户名
        """
        username = os.environ.get('SANDBOX_USERNAME') or os.environ.get('BAIDU_CC_USERNAME')
        if username.strip():
            return username

        # 如果环境变量未设置，引导用户输入用户名
        print("ℹ️  请输入您的用户名")
        username = input("用户名: ").strip()
        if not username:
            raise ValueError("用户名不能为空")

        # 创建空的 token 文件，方便下次自动识别
        uuap_dir = Path.home() / ".config" / "uuap"
        uuap_dir.mkdir(parents=True, exist_ok=True)
        token_file_path = KuApiClient._get_ugate_token_file_path(username)
        token_file_path.touch()
        print(f"✅ 已创建用户配置文件: {token_file_path}")
        print(f"💡 提示: 您也可以通过设置环境变量 SANDBOX_USERNAME 或 BAIDU_CC_USERNAME 来指定用户名")

        return username

    @staticmethod
    def _get_ugate_token_file_path(username: str) -> Path:
        """
        获取 ugate token 文件路径

        Args:
            username: 用户名

        Returns:
            Path: token 文件路径
        """
        return Path.home() / ".config" / "uuap" / f".eac_ugate_token_{username}"

    @staticmethod
    def _parse_token_content(content: str) -> Optional[str]:
        """
        解析token内容，支持多种格式：
        1. 纯文本token
        2. JSON格式：{"token": "...", "permanent": true/false} 或 {"token": "...", "expires_at": ...}
        3. 多行格式：第一行是过期时间（permanent:...），第二行是token

        Args:
            content: token文件内容或SKILL输出内容

        Returns:
            str: 解析后的token字符串，如果解析失败返回 None
        """
        if not content:
            return None

        content = content.strip()

        # 尝试格式1：JSON格式
        try:
            token_data = json.loads(content)
            if isinstance(token_data, dict) and 'token' in token_data:
                token = token_data['token']

                # 新格式：检查 permanent 字段
                if 'permanent' in token_data:
                    is_permanent = token_data['permanent']
                    if is_permanent:
                        print(f"✅ 解析 token (JSON格式，永久有效)")
                    else:
                        print(f"✅ 解析 token (JSON格式，非永久)")
                    return token

                # 旧格式：检查 expires_at 字段（保持向后兼容）
                if 'expires_at' in token_data:
                    import time
                    expires_at = token_data['expires_at']
                    current_time = int(time.time())
                    if expires_at < current_time:
                        print(f"⚠️  Token 已过期 (expires_at: {expires_at}, current: {current_time})")
                        return None
                    print(f"✅ 解析 token (JSON格式，旧格式)")
                    return token

                # 如果没有 permanent 和 expires_at 字段，直接返回 token
                print(f"✅ 解析 token (JSON格式)")
                return token
        except json.JSONDecodeError:
            pass

        # 尝试格式2：多行格式（第一行是 EXPIRES_AT:...，第二行是token）
        if '\n' in content:
            lines = content.split('\n')
            if len(lines) >= 2:
                first_line = lines[0].strip()
                second_line = lines[1].strip()

                # 检查第一行是否包含 EXPIRES_AT
                if 'EXPIRES_AT:' in first_line.upper():
                    # 第二行是实际的token
                    if second_line:
                        print(f"✅ 解析 token (多行格式，过期时间: {first_line})")
                        return second_line

        # 格式3：纯文本token（单行）
        if content and not content.startswith('{'):
            print(f"✅ 解析 token (纯文本格式)")
            return content

        return None

    @staticmethod
    def _read_local_token(username: str) -> Optional[str]:
        """
        从本地文件读取 token
        支持多种格式：
        1. 旧格式：纯文本token
        2. JSON格式：{"token": "...", "expires_at": ...}
        3. 多行格式：第一行是过期时间（EXPIRES_AT:...），第二行是token

        Args:
            username: 用户名

        Returns:
            str: token 字符串，如果读取失败返回 None
        """
        try:
            token_file = KuApiClient._get_ugate_token_file_path(username)
            if token_file.exists():
                with open(token_file, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if not content:
                        return None

                    token = KuApiClient._parse_token_content(content)
                    if token:
                        print(f"📄 从本地文件读取: {token_file}")
                        return token
        except Exception as e:
            print(f"⚠️  读取本地 token 文件失败: {e}", file=sys.stderr)

        return None

    @staticmethod
    def _write_local_token(username: str, token: str):
        """
        将 token 写入本地文件

        Args:
            username: 用户名
            token: token 字符串
        """
        try:
            token_file = KuApiClient._get_ugate_token_file_path(username)
            token_file.parent.mkdir(parents=True, exist_ok=True)

            with open(token_file, 'w', encoding='utf-8') as f:
                f.write(token)

            print(f"✅ Token 已保存到本地文件: {token_file}")
        except Exception as e:
            print(f"⚠️  写入本地 token 文件失败: {e}", file=sys.stderr)

    def _get_xiaolongxia_token(self, force_refresh: bool = False) -> str:
        """
        获取个人身份token
        新的认证逻辑:
        1. 获取当前用户名（从 SANDBOX_USERNAME 环境变量）
        2. 优先从本地文件 ~/.config/uuap/.eac_ugate_token_{username} 读取 token
        3. 如果本地文件不存在或 force_refresh=True，则调用 get-ugate-token SKILL 获取新 token
        4. 将新获取的 token 保存到本地文件

        Args:
            force_refresh: 是否强制刷新 token（认证失败时使用）

        Returns:
            str: Ugate Token
        """
        # 获取当前用户名
        username = self._get_current_username()

        # 如果不是强制刷新，先尝试从本地文件读取
        if not force_refresh:
            local_token = self._read_local_token(username)
            if local_token:
                return local_token

        # 本地文件不存在或强制刷新，调用 get-ugate-token SKILL 获取新 token
        try:
            if force_refresh:
                print(f"🔄 认证失败，重新调用 get-ugate-token SKILL 获取新 token...")
            else:
                print(f"🔄 本地 token 不存在，调用 get-ugate-token SKILL 获取新 token...")

            # 获取 get-ugate-token 脚本路径
            skill_dir = Path.home() / ".openclaw" / "skills" / "get-ugate-token"
            script_path = skill_dir / "getUgateToken.py"

            if not script_path.exists():
                # 尝试从当前文件的父父父目录（skills目录）的同级目录下查找
                # 当前文件: .../skills/ku-doc-manage/scripts/ku_api_client.py
                # parent.parent.parent = .../skills/
                # 所以在 .../skills/get-ugate-token/ 下查找
                project_skill_dir = Path(__file__).parent.parent.parent / "get-ugate-token"
                script_path = project_skill_dir / "getUgateToken.py"

            if not script_path.exists():
                print("\n" + "=" * 70)
                print("⚠️  未找到 get-ugate-token SKILL")
                print("=" * 70)
                print(f"\n检查路径: {skill_dir}")
                print(f"检查路径: {project_skill_dir}")
                print("\n💡 解决方案：下载并安装 get-ugate-token SKILL")
                print("\n请执行以下步骤：")
                print("1. 下载 Skill 包：")
                print("   wget https://bj.bcebos.com/baidu-cc/skills/16dbe2c9-c2e2-444c-90e0-8ceac0d332a5/get-ugate-token.zip")
                print("\n2. 解压并安装到以下任一目录：")
                print(f"   unzip get-ugate-token.zip -d {Path(__file__).parent.parent.parent}/")
                print("\n正在尝试自动下载安装...")
                print("=" * 70)

                # 尝试自动下载安装
                try:
                    # 下载到临时目录
                    with tempfile.TemporaryDirectory() as tmp_dir:
                        tmp_path = Path(tmp_dir)
                        zip_file = tmp_path / "get-ugate-token.zip"

                        print("📥 正在下载 get-ugate-token SKILL...")
                        download_result = subprocess.run(
                            ["wget", "-O", str(zip_file),
                             "https://bj.bcebos.com/baidu-cc/skills/16dbe2c9-c2e2-444c-90e0-8ceac0d332a5/get-ugate-token.zip"],
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if download_result.returncode != 0:
                            raise RuntimeError(f"下载失败: {download_result.stderr}")

                        print("✅ 下载完成")

                        # 优先尝试解压到项目本地的 skills 目录
                        # 当前文件: .../skills/ku-doc-manage/scripts/ku_api_client.py
                        # parent.parent.parent = .../skills/
                        target_dir = Path(__file__).parent.parent.parent
                        target_dir.mkdir(parents=True, exist_ok=True)

                        print(f"📦 正在解压到 {target_dir}...")
                        unzip_result = subprocess.run(
                            ["unzip", "-o", str(zip_file), "-d", str(target_dir)],
                            capture_output=True,
                            text=True,
                            timeout=10
                        )

                        if unzip_result.returncode != 0:
                            raise RuntimeError(f"解压失败: {unzip_result.stderr}")

                        print("✅ 安装完成")

                        # 重新检查脚本路径
                        script_path = target_dir / "get-ugate-token" / "getUgateToken.py"
                        if not script_path.exists():
                            raise RuntimeError(f"安装后仍然找不到脚本: {script_path}")

                        print(f"✅ 找到脚本: {script_path}\n")
                        print("=" * 70 + "\n")

                except Exception as e:
                    print(f"\n❌ 自动安装失败: {e}")
                    print("\n" + "=" * 70)
                    print("💡 请手动执行以下命令安装：")
                    print("wget https://bj.bcebos.com/baidu-cc/skills/16dbe2c9-c2e2-444c-90e0-8ceac0d332a5/get-ugate-token.zip")
                    print(f"unzip get-ugate-token.zip -d {Path(__file__).parent.parent.parent}/")
                    print("\n安装完成后，请重新运行本命令")
                    print("\n💡 或者使用其他认证方式（数字员工认证）")
                    print("   在 config.yaml 中配置 digital_auth.ak 和 digital_auth.sk")
                    print("=" * 70 + "\n")
                    raise RuntimeError("get-ugate-token SKILL 未安装，请先安装后重试")

            print(f"⏳ 正在等待认证（可能需要1-5分钟，请耐心等待）...\n")

            # 调用 get-ugate-token SKILL，传入当前用户名
            # 增加超时时间到 5 分钟，给用户足够时间在手机端确认
            result = subprocess.run(
                [sys.executable, str(script_path), username],
                capture_output=True,
                text=True,
                timeout=300,  # 5分钟超时
                env=os.environ.copy()
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                print("\n" + "=" * 70)
                print("❌ 获取个人身份token 失败")
                print("=" * 70 + "\n")
                raise RuntimeError(f"获取个人身份token失败: {error_msg}")

            # 解析token（支持多种格式：纯文本、JSON、多行格式）
            output_content = result.stdout.strip()
            print("UUAP 返回最新内容: {}".format(output_content))
            token = self._parse_token_content(output_content)

            if not token:
                raise RuntimeError(f"无法解析个人身份token，原始输出:\n{output_content}\n请检查 get-ugate-token SKILL 是否正常工作")

            # 将新 token 保存到本地文件
            # self._write_local_token(username, token)

            print(f"✅ 成功获取新 token")
            return token

        except subprocess.TimeoutExpired:
            print("\n" + "=" * 70)
            print("⏰ 认证超时（5分钟内未完成）")
            print("=" * 70 + "\n")
            raise RuntimeError("⏰ 认证超时（5分钟内未完成）")
        except Exception as e:
            print(f"⚠️  获取个人身份token失败: {e}", file=sys.stderr)
            raise

    def _get_headers(self) -> Dict[str, str]:
        """
        根据当前认证方式构建请求头

        Returns:
            dict: HTTP请求头
        """
        headers = {
            'Content-Type': 'application/json'
        }

        if self.current_auth_method == "xiaolongxia":
            # 个人身份认证：需要 Ugate-Token
            # Ugate-Token: 从本地文件读取，认证失败时重新获取
            if not self.xiaolongxia_token:
                self.xiaolongxia_token = self._get_xiaolongxia_token()
                # 如果返回 None，说明 get-ugate-token SKILL 不存在，尝试切换认证方式
                if self.xiaolongxia_token is None:
                    if self._try_next_auth_method():
                        # 成功切换到其他认证方式，递归调用以使用新的认证方式
                        return self._get_headers()
                    else:
                        raise RuntimeError("个人身份认证失败（未找到 get-ugate-token SKILL），且无其他可用的认证方式")
            headers['Ugate-Token'] = self.xiaolongxia_token
            headers['access-key'] = "6+uUJkYF+/0dbJ56CEoadQ=="

        elif self.current_auth_method == "digital":
            # 数字员工认证：需要 ak/sk
            headers['ak'] = self.ak
            headers['sk'] = self.sk

        print("headers is: {}".format(headers))
        return headers

    def _try_next_auth_method(self) -> bool:
        """
        尝试切换到下一个认证方式（自动降级）
        返回True表示成功切换，False表示没有更多可尝试的认证方式

        降级顺序：
        1. 个人身份认证（本地文件）
        2. 个人身份认证（强制刷新 token）
        3. 数字员工认证
        """
        # 如果是个人身份认证且还没有尝试过刷新 token，则尝试刷新
        if self.current_auth_method == "xiaolongxia" and not self.xiaolongxia_token_refreshed:
            print("\n" + "=" * 70)
            print("🔄 个人身份认证失败，尝试重新获取 token...")
            print("=" * 70)
            try:
                self.xiaolongxia_token = self._get_xiaolongxia_token(force_refresh=True)
                # 如果返回 None，说明 get-ugate-token SKILL 不存在，标记为已尝试并继续降级
                if self.xiaolongxia_token is None:
                    print("⚠️  get-ugate-token SKILL 不可用，跳过个人身份认证")
                    self.xiaolongxia_token_refreshed = True
                    # 继续执行后续的降级逻辑
                else:
                    self.xiaolongxia_token_refreshed = True
                    print("✅ Token 已刷新，重新尝试请求\n")
                    print("=" * 70 + "\n")
                    return True
            except Exception as e:
                print(f"⚠️  刷新 token 失败: {e}")
                self.xiaolongxia_token_refreshed = True  # 标记已尝试过

        # 记录当前失败的认证方式
        if self.current_auth_method and self.current_auth_method not in self.tried_auth_methods:
            self.tried_auth_methods.append(self.current_auth_method)

        # 如果不是auto模式，不允许降级
        if self.auth_mode != "auto":
            return False

        # 尝试下一个认证方式
        if self.current_auth_method == "xiaolongxia":
            print("\n" + "=" * 70)
            print("🔄 个人身份认证失败，尝试切换到数字员工认证...")
            print("=" * 70)
            if self._try_init_digital_auth():
                self.base_url = self._get_base_url_for_current_auth()
                print(f"✅ 已切换到数字员工认证 (AK: {self.ak[:10]}...)\n")
                print("=" * 70 + "\n")
                return True

        # 所有认证方式都失败
        print("\n" + "=" * 70)
        print("❌ 所有认证方式都已失败，无法继续")
        print("=" * 70)
        self._print_auth_help()
        return False

    def _print_auth_help(self):
        """打印认证配置帮助信息"""
        print("\n💡 认证配置帮助：\n")
        print("1️⃣  个人身份认证（推荐）：")
        print("   - 双token认证：")
        print("     * header: 从本地文件读取，认证失败时重新获取")
        print("       - Token文件位置: ~/.config/uuap/.eac_ugate_token_{username}")
        print("       - username 从环境变量 SANDBOX_USERNAME 或 BAIDU_CC_USERNAME 获取")
        print("2️⃣  数字员工认证：")
        print("   - 在 config.yaml 中配置 digital_auth.ak 和 digital_auth.sk\n")
        print("=" * 70 + "\n")
    
    def _request(self, endpoint: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        发送HTTP请求，支持两层自动认证降级

        Args:
            endpoint: API端点路径
            data: 请求数据

        Returns:
            dict: API响应结果
        """
        max_retries = 2  # 最多尝试2种认证方式
        retry_count = 0

        while retry_count < max_retries:
            url = f"{self.base_url}{endpoint}"
            headers = self._get_headers()

            try:
                response = requests.post(url, headers=headers, json=data, timeout=60)

                # 先尝试解析JSON响应
                try:
                    result = response.json()
                except Exception:
                    # 如果无法解析JSON，按HTTP状态码处理
                    if response.status_code in [401, 403]:
                        print(f"\n⚠️  认证失败 (HTTP {response.status_code})")
                        if self._try_next_auth_method():
                            retry_count += 1
                            continue
                        else:
                            response.raise_for_status()
                    response.raise_for_status()
                    raise

                # 检查响应体中的code字段
                response_code = result.get('code') or result.get('returnCode')

                # 个人身份认证 ugate-token 过期的错误码：500 或 403 (特殊处理，仅对个人身份认证生效)
                # 检查 error_msg 是否包含 "ugateToken invalid"
                if self.current_auth_method == "xiaolongxia":
                    # 支持多种错误消息字段名：error_msg, msg, returnMessage
                    error_msg = result.get('error_msg') or result.get('msg') or result.get('returnMessage', '')

                    # 如果是 500 错误码，或者是 403 且错误消息包含 ugateToken
                    is_ugate_token_error = (
                        response_code == 500 or
                        (response_code == 403 and 'ugateToken invalid' in error_msg)
                    )

                    if is_ugate_token_error:
                        print(f"\n⚠️  个人身份认证 ugate-token 已过期或无效 (code: {response_code}, {error_msg})")

                        if self._try_next_auth_method():
                            retry_count += 1
                            continue
                        else:
                            # 没有更多认证方式可尝试
                            return result

                # 认证失败的错误码：401, 403, 60413
                if response_code in [401, 403, 60413]:
                    error_msg = result.get('msg') or result.get('returnMessage', '')
                    print(f"\n⚠️  {self.current_auth_method}认证失败 (code: {response_code}, {error_msg})")

                    if self._try_next_auth_method():
                        retry_count += 1
                        continue
                    else:
                        # 没有更多认证方式可尝试
                        return result

                # 检查HTTP状态码
                if response.status_code in [401, 403]:
                    print(f"\n⚠️  {self.current_auth_method}认证失败 (HTTP {response.status_code})")
                    if self._try_next_auth_method():
                        retry_count += 1
                        continue
                    else:
                        response.raise_for_status()

                # 如果状态码不是2xx，抛出异常
                response.raise_for_status()

                return result

            except requests.exceptions.RequestException as e:
                # 网络错误或其他异常
                if hasattr(e, 'response') and e.response is not None and e.response.status_code in [401, 403]:
                    print(f"\n⚠️  {self.current_auth_method}认证失败")
                    if self._try_next_auth_method():
                        retry_count += 1
                        continue

                print(f"❌ 请求失败: {e}")
                if hasattr(e, 'response') and e.response is not None:
                    print(f"响应内容: {e.response.text}")
                raise

        # 所有重试都失败
        raise RuntimeError("所有认证方式都已尝试但失败，无法完成请求")
    
    def query_content(self, doc_id: str = None, url: str = None, show_doc_info: bool = True) -> Dict[str, Any]:
        """
        查询文档正文内容
        
        Args:
            doc_id: 文档ID
            url: 文档URL
            show_doc_info: 是否显示文档信息
            
        Returns:
            dict: 文档内容数据
        """
        if not doc_id and not url:
            raise ValueError("docId和url至少提供一个")
        
        data = {
            "showDocInfo": show_doc_info
        }
        if doc_id:
            data["docId"] = doc_id
        if url:
            data["url"] = url
            
        return self._request("/ku/openapi/queryContent", data)
    
    def query_repo(self, 
                   repo_id: str,
                   page_num: int = 1,
                   page_size: int = 10,
                   order_direction: str = "desc",
                   parent_doc_guid: str = None,
                   doc_guids: List[str] = None,
                   urls: List[str] = None,
                   show_doc_creator_info: bool = True,
                   show_doc_publisher_info: bool = True,
                   order_by: str = "publishTime") -> Dict[str, Any]:
        """
        分页查询知识库文档列表
        
        Args:
            repo_id: 知识库ID
            page_num: 页码
            page_size: 每页数量
            order_direction: 排序方向（desc/asc）
            parent_doc_guid: 父文档ID
            doc_guids: 文档ID列表
            urls: URL列表
            show_doc_creator_info: 是否显示创建者信息
            show_doc_publisher_info: 是否显示发布者信息
            order_by: 排序字段
            
        Returns:
            dict: 文档列表数据
        """
        data = {
            "repoId": repo_id,
            "pageNum": page_num,
            "pageSize": page_size,
            "orderDirection": order_direction
        }
        
        if parent_doc_guid is not None:
            data["parentDocGuid"] = parent_doc_guid
        if doc_guids:
            data["docGuids"] = doc_guids
        if urls:
            data["urls"] = urls
        if show_doc_creator_info:
            data["showDocCreatorInfo"] = show_doc_creator_info
        if show_doc_publisher_info:
            data["showDocPublisherInfo"] = show_doc_publisher_info
        if order_by:
            data["orderBy"] = order_by
            
        return self._request("/ku/openapi/queryRepo", data)
    
    def query_permission(self, doc_id: str, usernames: List[str]) -> Dict[str, Any]:
        """
        查询用户对文档的权限
        
        Args:
            doc_id: 文档ID
            usernames: 用户名列表
            
        Returns:
            dict: 权限信息
        """
        data = {
            "docId": doc_id,
            "usernames": usernames
        }
        return self._request("/ku/openapi/queryPermission", data)
    
    def create_doc(self,
                   repository_guid: str,
                   creator_username: str = None,
                   title: str = None,
                   content: str = "",
                   parent_doc_guid: str = None,
                   create_mode: int = 2,
                   template_doc_guid: str = None,
                   process_images: bool = True,
                   base_dir: str = None,
                   md_file_path: str = None) -> Dict[str, Any]:
        """
        创建文档

        Args:
            repository_guid: 知识库ID
            creator_username: 创建者用户名
            title: 文档标题
            content: 文档内容
            parent_doc_guid: 父文档ID
            create_mode: 文档创建模式,1-创建空文档,2-指定文档内容创建,3-指定源文档复制创建,默认为2
            template_doc_guid: 待复制的目标文档ID,当且仅当create_mode=3时必须有值
            process_images: 是否自动处理Markdown中的图片，默认True
            base_dir: 基础目录（用于解析相对路径的本地图片），如Markdown文件所在目录
            md_file_path: Markdown文件路径，直接从文件读取内容。如果提供，将自动设置base_dir为文件所在目录

        Returns:
            dict: 创建结果，当 process_images=True 时，result 中会额外包含：
                  - processedContent: 处理后的Markdown内容（图片URL已替换）
                  - imageUrls: 图片URL映射 {原始URL: 新URL}

        Note:
            图片处理流程（先处理图片，再创建文档）：
            1. 判断 content 是否是 Markdown 且包含本地/外部图片
            2. 使用上传图片并替换URL
            3. 用处理后的 content 创建文档

            图片处理规则：
            - 内部域名图片 (rte.weiyun.baidu.com): 跳过，保留原链接
            - 本地路径图片: 读取文件并上传
            - 外部URL图片: 下载后上传

            md_file_path 优先级高于 content：
            - 如果提供 md_file_path，将从该文件读取内容，base_dir 自动设为文件所在目录
            - 如果未提供 title 且能从文件名推断，将自动使用文件名（不含扩展名）作为标题
        """
        # 如果提供了 md_file_path，从文件读取内容
        if md_file_path:
            file_path = os.path.expanduser(md_file_path)
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"Markdown文件不存在: {file_path}")

            # 读取文件内容
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # 自动设置 base_dir 为文件所在目录
            if base_dir is None:
                base_dir = os.path.dirname(os.path.abspath(file_path))

            # 如果未提供 title，尝试从文件名推断
            if title is None:
                title = os.path.splitext(os.path.basename(file_path))[0]

        # 判断是否需要处理图片
        final_content = content
        processed_content = None  # 声明在外部作用域

        if process_images and create_mode == 2 and content:
            # 获取临时文档ID（从配置读取）
            temp_doc_id_for_use = "BSmo1JO8fRZ_Jz"
            print(f"🔍 图片处理调试: process_images={process_images}, create_mode={create_mode}, temp_doc_id={temp_doc_id_for_use}")
            
            if temp_doc_id_for_use:
                # 先处理图片（使用临时文档ID上传）
                print(f"🔄 开始处理图片，使用临时文档ID: {temp_doc_id_for_use}")
                processed_content = self._process_markdown_images(content, temp_doc_id_for_use, base_dir)
                print(f"📝 图片处理完成，原始长度: {len(content)}, 处理后长度: {len(processed_content)}")
                if processed_content != content:
                    final_content = processed_content
                    print("✅ 图片已处理，内容已更新")
                else:
                    print("⚠️  图片处理后内容未变化")
            else:
                print("⚠️  未找到临时文档ID，跳过图片处理")
        # 如果不需要图片处理，直接使用原始内容
        data = {
            "repositoryGuid": repository_guid,
            "content": final_content,
            "createMode": create_mode
        }

        if creator_username:
            data["creatorUsername"] = creator_username
        if title:
            data["title"] = title
        if parent_doc_guid:
            data["parentDocGuid"] = parent_doc_guid
        if template_doc_guid:
            data["templateDocGuid"] = template_doc_guid

        # 创建文档
        result = self._request("/ku/openapi/createDoc", data)

        # 如果处理了图片，添加处理结果到返回值
        if result.get('returnCode') == 200 and processed_content and processed_content != content:
            result['result']['processedContent'] = processed_content

        return result

    def add_member(self, doc_id: str, usernames: List[str], role_name: str = "DocReader") -> Dict[str, Any]:
        """
        添加文档成员

        Args:
            doc_id: 文档ID
            usernames: 用户名列表（邮箱前缀）
            role_name: 角色名称，默认DocReader。可选值：
                - DocReader: 可读
                - DocMember: 可编辑
                - DocAdmin: 管理员

        Returns:
            dict: 操作结果
        """
        data = {
            "docId": doc_id,
            "usernames": usernames,
            "roleName": role_name
        }
        return self._request("/ku/openapi/addMember", data)

    def update_member(self, doc_id: str, username: str, role_name: str) -> Dict[str, Any]:
        """
        更新文档成员权限

        Args:
            doc_id: 文档ID
            username: 待更新的用户名（邮箱前缀）
            role_name: 新的角色名称：DocReader、DocMember、DocAdmin

        Returns:
            dict: 操作结果
        """
        data = {
            "docId": doc_id,
            "username": username,
            "roleName": role_name
        }
        return self._request("/ku/openapi/updateMember", data)

    def copy_doc(self,
                 doc_id: str,
                 operator_username: str = None,
                 to_repo_guid: str = None,
                 to_parent_guid: str = None,
                 new_title: str = None) -> Dict[str, Any]:
        """
        复制文档

        Args:
            doc_id: 待复制的源文档ID
            operator_username: 操作者用户名
            to_repo_guid: 目标知识库ID，不传则默认为源文档所在库
            to_parent_guid: 目标父目录ID，不传则默认为源文档同级
            new_title: 新文档标题，不传则默认为"源标题的复制"

        Returns:
            dict: 新文档信息，包含docGuid、url、title
        """
        data = {
            "docId": doc_id
        }
        if operator_username:
            data["operatorUsername"] = operator_username
        if to_repo_guid:
            data["toRepoGuid"] = to_repo_guid
        if to_parent_guid:
            data["toParentGuid"] = to_parent_guid
        if new_title:
            data["newTitle"] = new_title
        return self._request("/ku/openapi/copyDoc", data)

    def move_doc(self,
                 doc_id: str,
                 to_repo_guid: str,
                 operator_username: str = None,
                 to_parent_guid: str = None,
                 to_adjacent_doc_guid: str = None,
                 upper: bool = False) -> Dict[str, Any]:
        """
        移动文档

        Args:
            doc_id: 待移动的源文档ID
            to_repo_guid: 目标知识库ID
            operator_username: 操作者用户名
            to_parent_guid: 目标父目录ID，不传则默认为根目录
            to_adjacent_doc_guid: 目标相邻文档ID
            upper: 是否移动到目标上方，默认False

        Returns:
            dict: 移动后的文档信息，包含docGuid、url
        """
        data = {
            "docId": doc_id,
            "toRepoGuid": to_repo_guid
        }
        if operator_username:
            data["operatorUsername"] = operator_username
        if to_parent_guid:
            data["toParentGuid"] = to_parent_guid
        if to_adjacent_doc_guid:
            data["toAdjacentDocGuid"] = to_adjacent_doc_guid
        if upper:
            data["upper"] = upper
        return self._request("/ku/openapi/moveDoc", data)

    def change_scope(self, doc_id: str, scope: int, operator_username: str = None) -> Dict[str, Any]:
        """
        修改文档公开范围

        Args:
            doc_id: 文档ID
            scope: 权限范围：5-公开可读，6-公开可编辑，20-私密
            operator_username: 操作者用户名，不传则使用ak对应的用户名

        Returns:
            dict: 操作结果
        """
        data = {
            "docId": doc_id,
            "scope": scope
        }
        if operator_username:
            data["operatorUsername"] = operator_username
        return self._request("/ku/openapi/changeScope", data)

    def query_comments(self,
                      doc_id: str,
                      query_bottom_comment: bool = True,
                      query_side_comment: bool = True,
                      page_num: int = 1,
                      page_size: int = 10) -> Dict[str, Any]:
        """
        查询文档评论

        Args:
            doc_id: 文档ID
            query_bottom_comment: 是否查询底部评论，默认True
            query_side_comment: 是否查询侧边评论，默认True
            page_num: 页码，默认1
            page_size: 每页数量，默认10

        Returns:
            dict: 评论数据，包含bottomComments、sideComments、total
        """
        data = {
            "docId": doc_id,
            "queryBottomComment": query_bottom_comment,
            "querySideComment": query_side_comment,
            "pageNum": page_num,
            "pageSize": page_size
        }
        return self._request("/ku/openapi/queryComments", data)

    def query_recent_view(self,
                         doc_id: str,
                         begin_time: int = None,
                         end_time: int = None,
                         page_num: int = 1,
                         page_size: int = 10) -> Dict[str, Any]:
        """
        查询文档最近浏览信息

        Args:
            doc_id: 文档ID
            begin_time: 记录起始时间（毫秒级时间戳），不传则默认为当天起始时间
            end_time: 记录结束时间（毫秒级时间戳），不传则默认为当前时间
            page_num: 页码，默认1
            page_size: 每页数量，默认10

        Returns:
            dict: 浏览信息，包含repositoryGuid、docGuid、totalViewers、count、data
        """
        data = {
            "docId": doc_id,
            "pageNum": page_num,
            "pageSize": page_size
        }
        if begin_time is not None:
            data["beginTime"] = begin_time
        if end_time is not None:
            data["endTime"] = end_time
        return self._request("/ku/openapi/queryRecentView", data)

    def query_flowchart(self, doc_guid: str, flowchart_id: str) -> Dict[str, Any]:
        """
        导出流程图数据

        Args:
            doc_guid: 文档ID
            flowchart_id: 流程图ID

        Returns:
            dict: 流程图数据，包含docGuid、flowchartId、content（mxGraph格式的XML）
        """
        data = {
            "docGuid": doc_guid,
            "flowchartId": flowchart_id
        }
        return self._request("/ku/openapi/queryFlowchart", data)

    def query_user_info(self, username: str) -> Dict[str, Any]:
        """
        查询用户个人信息

        查询指定用户的个人信息，包括个人知识库ID等。当需要创建文档但不知道目标知识库ID时，
        可以使用此API获取用户的个人知识库ID。

        Args:
            username: 用户名（邮箱前缀）

        Returns:
            dict: 用户信息数据，包含个人知识库ID

        Example:
            >>> client = KuApiClient()
            >>> result = client.query_user_info(username="zhangsan")
            >>> if result.get('returnCode') == 200:
            >>>     user_info = result['result']['userPersonalRepo']
            >>>     personal_repo_id = user_info['repositoryGuid']
            >>>     print(f"个人知识库ID: {personal_repo_id}")
        """
        data = {
            "username": username
        }
        return self._request("/ku/openapi/queryUserInfo", data)

    def upload_attachment(self, doc_guid: str, file, file_name: str = None) -> Dict[str, Any]:
        """
        上传文档附件

        上传附件到指定的知识库文档，支持各种文件类型（PDF、Word、Excel、图片等）。

        Args:
            doc_guid: 文档ID
            file: 文件路径（字符串）或文件内容（bytes）
                  本期支持文件路径字符串和 bytes 数据
            file_name: 文件名，当 file 为 bytes 时必填

        Returns:
            dict: 上传结果，包含 returnCode、returnMessage 和 result
                  result中包含：
                  - docGuid: 文档ID
                  - attachId: 附件ID
                  - name: 文件名
                  - extension: 文件扩展名
                  - size: 文件大小（字节）

        Example:
            >>> client = KuApiClient()
            >>> # 方式1: 传入文件路径
            >>> result = client.upload_attachment(
            ...     doc_guid="WKoT7ltTnjU1oW",
            ...     file="/path/to/file.pdf"
            ... )
            >>> # 方式2: 传入 bytes 数据
            >>> result = client.upload_attachment(
            ...     doc_guid="WKoT7ltTnjU1oW",
            ...     file=b"file_content_bytes",
            ...     file_name="test.pdf"
            ... )
        """
        import os

        # 处理 bytes 输入
        if isinstance(file, bytes):
            file_content = file
            if not file_name:
                return {
                    "returnCode": 400,
                    "returnMessage": "当 file 为 bytes 类型时，file_name 参数必填",
                    "result": None
                }
        # 处理文件路径输入
        elif isinstance(file, str):
            # 检查文件是否存在
            if not os.path.exists(file):
                return {
                    "returnCode": 400,
                    "returnMessage": f"文件不存在: {file}",
                    "result": None
                }
            # 读取文件内容和文件名
            with open(file, 'rb') as f:
                file_content = f.read()
            file_name = os.path.basename(file)
        else:
            return {
                "returnCode": 400,
                "returnMessage": "file 参数仅支持文件路径字符串或 bytes 类型",
                "result": None
            }

        # 构建multipart/form-data请求
        files_param = {'file': (file_name, file_content)}
        form_data = {'docGuid': doc_guid}

        # 根据当前认证方式选择base_url
        base_url = self._get_base_url_for_current_auth()
        url = f"{base_url}/ku/openapi/uploadAttachment"

        # 获取headers（包含认证信息）
        headers = self._get_headers()

        # 注意：使用multipart/form-data时，不要手动设置Content-Type
        # requests会自动设置正确的Content-Type和boundary
        if 'Content-Type' in headers:
            del headers['Content-Type']

        try:
            response = requests.post(
                url,
                headers=headers,
                data=form_data,
                files=files_param,
                timeout=120  # 上传文件可能需要更长时间
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "returnCode": 500,
                "returnMessage": f"上传附件失败: {str(e)}",
                "result": None
            }
    
    def editor_ku_page(self,
                       doc_guid: str,
                       editor_username: str,
                       operations: List[Dict[str, Any]],
                       publish: bool = True) -> Dict[str, Any]:
        """
        编辑文档正文

        通过编辑操作列表对文档进行增删改操作。

        Args:
            doc_guid: 文档ID
            editor_username: 编辑者用户名（UUAP格式，即邮箱前缀）
            operations: 编辑操作列表，每个操作是一个字典，包含：
                - mode (str): 操作模式
                    - "append": 追加到文档末尾（不需要 blockId 和 position）
                    - "cover": 覆盖全文（不需要 blockId 和 position）
                    - "sibling": 同级插入，在指定 blockId 的上方或下方插入
                    - "delete": 删除指定 blockId 的节点
                - blockId (str): 目标节点ID
                    - sibling/delete 模式时需要
                    - sibling 模式下可不传，表示追加到文档末尾
                    - append/cover 模式下不需要
                - json (list): 编辑器 JSON 元素数组（delete 模式下不需要）
                - position (int): 位置信息（sibling 模式下需要）
                    - -1: 目标节点上方
                    - 1: 目标节点下方
            publish: 是否编辑后同步发布，默认 True

        Returns:
            dict: 操作结果
        """
        data = {
            "docGuid": doc_guid,
            "editorUsername": editor_username,
            "operations": operations,
            "publish": publish
        }
        return self._request("/ku/openapi/editContent", data)

    def _get_temp_doc_id(self) -> str:
        """
        从配置文件获取临时文档ID
        
        Returns:
            str: 临时文档ID，如果未配置则返回空字符串
        """
        try:
            import yaml
            config_path = os.path.join(os.path.dirname(__file__), 'config.yaml')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            temp_doc_id = config.get('image_upload', {}).get('temp_doc_id', '')
            return temp_doc_id
        except Exception as e:
            print(f"⚠️  读取临时文档ID配置失败: {e}")
            return ""

    def _process_markdown_images(self, content: str, doc_id: str, base_dir: str = None) -> str:
        """
        处理Markdown中的图片，自动上传到知识库并替换URL

        Args:
            content: Markdown内容
            doc_id: 文档ID
            base_dir: 基础目录（用于解析相对路径的本地图片），默认为当前工作目录

        Returns:
            str: 处理后的Markdown内容
        """
        import re
        import os
        from urllib.parse import urlparse
        from urllib.request import urlopen

        # 如果 base_dir 为空，默认使用当前工作目录
        if base_dir is None:
            base_dir = os.getcwd()

        # 正则匹配Markdown图片：![alt](url)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'
        
        print(f"🔍 _process_markdown_images: 开始处理图片，文档ID: {doc_id}，基础目录: {base_dir}")
        print(f"🔍 原始内容长度: {len(content)} 字符")

        def process_image(match):
            alt_text = match.group(1)
            original_url = match.group(2).strip()
            print(f"🖼️  处理图片匹配: alt='{alt_text}', url='{original_url}'")

            # 1. 跳过内部域名图片
            if 'rte.weiyun.baidu.com' in original_url:
                print(f"  跳过内部域名图片")
                return match.group(0)

            # 2. 处理本地路径图片
            if original_url.startswith('./') or original_url.startswith('/') or not original_url.startswith('http'):
                # 确定完整路径
                if base_dir and not original_url.startswith('/'):
                    # 相对路径，拼接基础目录
                    full_path = os.path.join(base_dir, original_url)
                else:
                    full_path = original_url
                
                print(f"  本地图片路径解析: '{original_url}' -> '{full_path}'")

                # 检查文件是否存在
                if os.path.exists(full_path):
                    file_name = os.path.basename(full_path)
                    print(f"  文件存在，开始上传: {file_name}")
                    # 直接用文件路径上传
                    result = self.upload_attachment(doc_id, full_path)
                    print(f"  上传结果: {result}")
                else:
                    # 文件不存在，保留原链接
                    print(f"  文件不存在: {full_path}")
                    return match.group(0)

            # 3. 处理外部URL图片
            elif original_url.startswith('http://') or original_url.startswith('https://'):
                try:
                    # 下载图片
                    response = urlopen(original_url, timeout=30)
                    file_content = response.read()

                    # 从URL中提取文件名
                    parsed_url = urlparse(original_url)
                    path = parsed_url.path
                    file_name = os.path.basename(path) or 'image.png'

                    # 上传图片
                    result = self.upload_attachment(doc_id, file_content, file_name)
                except Exception as e:
                    # 下载失败，保留原链接
                    return match.group(0)
            else:
                # 未知格式，保留原链接
                return match.group(0)

            # 检查上传结果
            if result.get('returnCode') == 200 and result.get('result'):
                attach_info = result['result']
                attach_id = attach_info.get('attachId')
                if attach_id:
                    # 构建新的图片URL
                    new_url = f"https://rte.weiyun.baidu.com/wiki/attach/image/api/imageDownloadAddress?attachId={attach_id}&docGuid={doc_id}"
                    print(f"  上传成功! attachId={attach_id}, 新URL: {new_url}")
                    return f'![{alt_text}]({new_url})'
                else:
                    print(f"  上传成功但未返回attachId: {result}")
                    return match.group(0)
            else:
                # 上传失败，保留原链接
                print(f"  上传失败: {result.get('returnMessage', '未知错误')}")
                return match.group(0)

        # 替换所有图片
        return re.sub(image_pattern, process_image, content)


def main():
    """示例用法"""
    # 初始化客户端
    client = KuApiClient()

    print("=" *  60)
    print("知识库开放API Python客户端示例 - 完整14个API")
    print("=" *  60)

    # 示例1: 查询文档内容
    print("\n1. 查询文档内容")
    print("-" * 60)
    try:
        result = client.query_content(doc_id="WKoT7ltTnjU1oW")
        if result.get('returnCode') == 200:
            doc_info = result['result'].get('docInfo', {})
            print(f"✅ 文档标题: {doc_info.get('name')}")
            print(f"✅ 创建者: {doc_info.get('creatorUserInfo', {}).get('nickname')}")
            print(f"✅ 文档URL: {doc_info.get('url')}")
        else:
            print(f"❌ 查询失败: {result.get('returnMessage')}")
    except Exception as e:
        print(f"❌ 错误: {e}")

    # # 示例2: 上传文档附件
    # print("\n2. 上传文档附件")
    # print("-" * 60)
    # try:
    #     # 请将此路径替换为实际存在的文件路径
    #     file_path = "/path/to/your/file.pdf"
    #     result = client.upload_attachment(
    #         doc_guid="WKoT7ltTnjU1oW",
    #         file=file_path
    #     )
    #     if result.get('returnCode') == 200:
    #         attach_info = result['result']
    #         print(f"✅ 附件上传成功！")
    #         print(f"  - 文档ID: {attach_info.get('docGuid')}")
    #         print(f"  - 附件ID: {attach_info.get('attachId')}")
    #         print(f"  - 文件名: {attach_info.get('name')}")
    #         print(f"  - 文件扩展名: {attach_info.get('extension')}")
    #         print(f"  - 文件大小: {attach_info.get('size')} 字节")
    #     else:
    #         print(f"❌ 上传失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例3: 查询知识库文档列表
    # print("\n3. 查询知识库文档列表")
    # print("-" * 60)
    # try:
    #     result = client.query_repo(
    #         repo_id="E3d4LRExEl",
    #         page_num=1,
    #         page_size=5
    #     )
    #     if result.get('returnCode') == 200:
    #         docs = result['result'].get('data', [])
    #         total = result['result'].get('total', 0)
    #         print(f"✅ 共找到 {total} 篇文档，显示前5篇:")
    #         for i, doc in enumerate(docs, 1):
    #             print(f"  {i}. {doc.get('name')} (ID: {doc.get('docGuid')})")
    #     else:
    #         print(f"❌ 查询失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例4: 创建文档
    # print("\n4. 创建文档")
    # print("-" * 60)
    # try:
    #     result = client.create_doc(
    #         repository_guid="E3d4LRExEl",
    #         creator_username="zhangsan",
    #         title="API测试文档",
    #         content="这是一篇通过API创建的测试文档"
    #     )
    #     if result.get('returnCode') == 200:
    #         doc_info = result['result']
    #         print(f"✅ 文档创建成功")
    #         print(f"  - 文档ID: {doc_info.get('docGuid')}")
    #         print(f"  - 文档URL: {doc_info.get('url')}")
    #     else:
    #         print(f"❌ 创建失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例5: 查询用户权限
    # print("\n5. 查询用户权限")
    # print("-" * 60)
    # try:
    #     result = client.query_permission(
    #         doc_id="WKoT7ltTnjU1oW",
    #         usernames=["zhangsan"]
    #     )
    #     if result.get('returnCode') == 200:
    #         permissions = result.get('result', [])
    #         for perm in permissions:
    #             print(f"✅ 用户: {perm.get('username')}")
    #             print(f"  - 可读: {perm.get('canRead')}")
    #             print(f"  - 可写: {perm.get('canUpdate')}")
    #             print(f"  - 角色: {perm.get('roleName')}")
    #     else:
    #         print(f"❌ 查询失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例6: 添加文档成员
    # print("\n6. 添加文档成员")
    # print("-" * 60)
    # try:
    #     result = client.add_member(
    #         doc_id="WKoT7ltTnjU1oW",
    #         usernames=["zhangsan"],
    #         role_name="DocReader"
    #     )
    #     if result.get('returnCode') == 200:
    #         print(f"✅ 成员添加成功")
    #     else:
    #         print(f"❌ 添加失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例7: 更新文档成员权限
    # print("\n7. 更新文档成员权限")
    # print("-" * 60)
    # try:
    #     result = client.update_member(
    #         doc_id="WKoT7ltTnjU1oW",
    #         username="zhangsan",
    #         role_name="DocMember"
    #     )
    #     if result.get('returnCode') == 200:
    #         print(f"✅ 权限更新成功")
    #     else:
    #         print(f"❌ 更新失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例8: 查询文档评论
    # print("\n8. 查询文档评论")
    # print("-" * 60)
    # try:
    #     result = client.query_comments(
    #         doc_id="WKoT7ltTnjU1oW",
    #         page_num=1,
    #         page_size=5
    #     )
    #     if result.get('returnCode') == 200:
    #         total = result['result'].get('total', 0)
    #         print(f"✅ 共有 {total} 条评论")
    #     else:
    #         print(f"❌ 查询失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例9: 查询文档浏览记录
    # print("\n9. 查询文档最近浏览信息")
    # print("-" * 60)
    # try:
    #     result = client.query_recent_view(
    #         doc_id="WKoT7ltTnjU1oW",
    #         page_num=1,
    #         page_size=5
    #     )
    #     if result.get('returnCode') == 200:
    #         view_info = result['result']
    #         print(f"✅ 总浏览人数: {view_info.get('totalViewers')}")
    #         print(f"✅ 浏览记录数: {view_info.get('count')}")
    #     else:
    #         print(f"❌ 查询失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例10: 复制文档
    # print("\n10. 复制文档")
    # print("-" * 60)
    # try:
    #     result = client.copy_doc(
    #         doc_id="WKoT7ltTnjU1oW",
    #         operator_username="zhangsan",
    #         new_title="文档副本"
    #     )
    #     if result.get('returnCode') == 200:
    #         doc_info = result['result']
    #         print(f"✅ 文档复制成功")
    #         print(f"  - 新文档ID: {doc_info.get('docGuid')}")
    #     else:
    #         print(f"❌ 复制失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例11: 修改文档公开范围
    # print("\n11. 修改文档公开范围")
    # print("-" * 60)
    # try:
    #     result = client.change_scope(
    #         doc_id="WKoT7ltTnjU1oW",
    #         scope=5,  # 5-公开可读
    #         operator_username="zhangsan"
    #     )
    #     if result.get('returnCode') == 200:
    #         print(f"✅ 公开范围修改成功")
    #     else:
    #         print(f"❌ 修改失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例12: 导出流程图数据
    # print("\n12. 导出流程图数据")
    # print("-" * 60)
    # try:
    #     result = client.query_flowchart(
    #         doc_guid="WKoT7ltTnjU1oW",
    #         flowchart_id="flowchart_123"
    #     )
    #     if result.get('returnCode') == 200:
    #         print(f"✅ 流程图数据导出成功")
    #     else:
    #         print(f"❌ 导出失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例13: 查询用户个人信息（获取个人知识库ID）
    # print("\n13. 查询用户个人信息")
    # print("-" * 60)
    # try:
    #     result = client.query_user_info(username="zhangsan")
    #     if result.get('returnCode') == 200:
    #         user_info = result['result']['userPersonalRepo']
    #         personal_repo_id = user_info['repositoryGuid']
    #         print(f"✅ 用户个人信息查询成功")
    #         print(f"  - 用户名: {result['result'].get('username')}")
    #         print(f"  - 昵称: {result['result'].get('nickname')}")
    #         print(f"  - 个人知识库ID: {personal_repo_id}")
    #         print(f"  - 个人知识库名: {user_info.get('name')}")
    #     else:
    #         print(f"❌ 查询失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # # 示例14: 编辑文档正文
    # print("\n14. 编辑文档正文")
    # print("-" * 60)
    # try:
    #     # 示例14.1: 追加一段文字到文档末尾
    #     result = client.editor_ku_page(
    #         doc_guid="WKoT7ltTnjU1oW",
    #         editor_username="zhangsan",
    #         operations=[{
    #             "mode": "append",
    #             "withNewCard": True,
    #             "json": [{"type": "paragraph", "children": [{"text": "追加的新内容"}]}]
    #         }]
    #     )
    #     if result.get('returnCode') == 200:
    #         print(f"✅ 文档编辑成功: {result['result'].get('docGuid')}")
    #     else:
    #         print(f"❌ 编辑失败: {result.get('returnMessage')}")
    #
    #     # 示例14.2: 覆盖全文
    #     result = client.editor_ku_page(
    #         doc_guid="WKoT7ltTnjU1oW",
    #         editor_username="zhangsan",
    #         operations=[{
    #             "mode": "cover",
    #             "withNewCard": True,
    #             "json": [
    #                 {
    #                     "type": "heading",
    #                     "level": 1,
    #                     "children": [{"text": "新标题"}]
    #                 },
    #                 {
    #                     "type": "paragraph",
    #                     "children": [{"text": "新文档内容，完全替换原内容"}]
    #                 }
    #             ]
    #         }]
    #     )
    #     if result.get('returnCode') == 200:
    #         print(f"✅ 文档覆盖成功: {result['result'].get('docGuid')}")
    #     else:
    #         print(f"❌ 覆盖失败: {result.get('returnMessage')}")
    #
    #     # 示例14.3: 在指定节点同级插入
    #     result = client.editor_ku_page(
    #         doc_guid="WKoT7ltTnjU1oW",
    #         editor_username="zhangsan",
    #         operations=[{
    #             "mode": "sibling",
    #             "blockId": "block_abc123",  # 目标节点ID，可通过 query_content 获取
    #             "withNewCard": True,
    #             "json": [{"type": "paragraph", "children": [{"text": "插入的内容"}]}]
    #         }]
    #     )
    #     if result.get('returnCode') == 200:
    #         print(f"✅ 节点插入成功: {result['result'].get('docGuid')}")
    #     else:
    #         print(f"❌ 插入失败: {result.get('returnMessage')}")
    # except Exception as e:
    #     print(f"❌ 错误: {e}")

    # print("\n" + "=" *  60)
    # print("示例执行完成 - 展示了14个常用API")
    # print("=" *  60)


if __name__ == '__main__':
    main()