"""
iCafe API Client - 卡片操作助手

提供 iCafe 平台卡片相关的 API 接口封装。
"""

import os
import re
import requests
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

# 尝试导入 markdown 库，如果不存在则使用简单的转换函数
try:
    import markdown
    HAS_MARKDOWN = True
except ImportError:
    HAS_MARKDOWN = False


def _has_formatting(text: str) -> bool:
    """检测文本是否包含格式标记（Markdown 或 HTML）

    Args:
        text: 待检测的文本

    Returns:
        True 表示包含格式标记，False 表示纯文本
    """
    if not text:
        return False

    # 检测 HTML 标签
    html_pattern = r'<(a|b|strong|em|p|ul|ol|li|h1|h2|h3|h4|h5|h6|br|hr|div|span|blockquote|code|pre|table|tr|td|th)\b'
    if re.search(html_pattern, text, re.IGNORECASE):
        return True

    # 检测 Markdown 格式标记
    markdown_patterns = [
        r'\*\*.+?\*\*',      # 加粗 **text**
        r'\*.+?\*',          # 斜体 *text*
        r'__.+?__',          # 加粗 __text__
        r'_.+?_',            # 斜体 _text_
        r'#{1,6}\s.+',      # 标题 # text
        r'\[.+\]\(.+\)',     # 链接 [text](url)
        r'!\[.+\]\(.+\)',    # 图片
        r'^\s*[-*+]\s+',     # 无序列表 - item 或 * item
        r'^\s*\d+\.\s+',     # 有序列表 1. item
        r'^\s*>\s+',         # 引用 > text
        r'`[^`]+`',          # 行内代码 `code`
        r'^```',             # 代码块 ```code```
        r'^---+$',           # 分隔线
        r'\^\s+.+',          # 上标 ^text
        r'~~.+?~~',          # 删除线 ~~text~~
    ]

    for pattern in markdown_patterns:
        if re.search(pattern, text, re.MULTILINE):
            return True

    return False


def _format_to_html(text: str) -> str:
    """将格式化文本转换为 HTML

    如果文本包含 HTML 标签，直接返回。
    如果包含 Markdown 格式，转换为 HTML。
    如果是纯文本，直接返回。

    Args:
        text: 待格式化的文本

    Returns:
        转换后的 HTML 文本
    """
    if not text:
        return text

    # 如果已经包含 HTML 标签，直接返回
    html_pattern = r'<(a|b|strong|em|p|ul|ol|li|h1|h2|h3|h4|h5|h6|br|hr|div|span|blockquote|code|pre|table|tr|td|th)\b'
    if re.search(html_pattern, text, re.IGNORECASE):
        return text

    # 如果包含 Markdown 格式，转换为 HTML
    if _has_formatting(text):
        if HAS_MARKDOWN:
            # 使用 markdown 库转换
            return markdown.markdown(text, extensions=['extra', 'nl2br'])
        else:
            # 简单的 Markdown 转 HTML
            return _simple_markdown_to_html(text)

    # 纯文本，原样返回
    return text


def _simple_markdown_to_html(text: str) -> str:
    """简单的 Markdown 转 HTML（当没有 markdown 库时使用）

    Args:
        text: Markdown 文本

    Returns:
        HTML 文本
    """
    if not text:
        return text

    result = text

    # 处理代码块
    result = re.sub(r'```(\w*)\n(.*?)\n```', r'<pre><code>\2</code></pre>', result, flags=re.DOTALL)

    # 处理行内代码
    result = re.sub(r'`([^`]+)`', r'<code>\1</code>', result)

    # 处理加粗
    result = re.sub(r'\*\*([^*]+)\*\*', r'<strong>\1</strong>', result)
    result = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', result)

    # 处理斜体
    result = re.sub(r'\*([^*]+)\*', r'<em>\1</em>', result)
    result = re.sub(r'_([^_]+)_', r'<em>\1</em>', result)

    # 处理删除线
    result = re.sub(r'~~([^~]+)~~', r'<del>\1</del>', result)

    # 处理链接
    result = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', result)

    # 处理标题
    for i in range(6, 0, -1):
        result = re.sub(rf'^{"#" * i}\s+(.+)$', rf'<h{i}>\1</h{i}>', result, flags=re.MULTILINE)

    # 处理引用
    result = re.sub(r'^>\s+(.+)$', r'<blockquote>\1</blockquote>', result, flags=re.MULTILINE)

    # 处理无序列表
    result = re.sub(r'^\s*[-*+]\s+(.+)$', r'<li>\1</li>', result, flags=re.MULTILINE)
    result = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', result)

    # 处理有序列表
    result = re.sub(r'^\s*\d+\.\s+(.+)$', r'<li>\1</li>', result, flags=re.MULTILINE)
    result = re.sub(r'(<li>.*?</li>\n?)+', r'<ol>\g<0></ol>', result)

    # 处理分隔线
    result = re.sub(r'^-{3,}$', '<hr>', result, flags=re.MULTILINE)

    # 处理换行
    result = re.sub(r'\n', '<br>', result)

    return result


@dataclass
class ICafeConfig:
    """iCafe API 配置"""
    base_url: str = "http://10.11.152.208:8701/api/process/icafe"
    username: Optional[str] = None
    password: Optional[str] = None
    timeout: int = 30

    @staticmethod
    def _get_auth_token() -> Optional[str]:
        """获取认证 token

        优先从环境变量 COMATE_AUTH_TOKEN 读取，
        如果没有则从 ~/.comate/login 文件读取

        Returns:
            认证 token 字符串，如果都未找到则返回 None
        """
        # 优先从环境变量读取
        token = os.environ.get("COMATE_AUTH_TOKEN")
        if token:
            return token

        # 从登录文件读取
        login_file = Path.home() / ".comate" / "login"
        if login_file.exists():
            try:
                content = login_file.read_text().strip()
                # 文件格式：纯 token（单行）
                if content:
                    return content
            except Exception:
                pass

        return None


class ICafeClient:
    """iCafe API 客户端"""

    def __init__(self, config: Optional[ICafeConfig] = None):
        self.config = config or ICafeConfig()
        self.session = requests.Session()

        # 设置默认 headers
        self.session.headers.update({
            "Content-Type": "application/json"
        })

        # 添加认证 token header
        auth_token = self.config._get_auth_token()
        if auth_token:
            self.session.headers["x-ac-Authorization"] = auth_token

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """通用请求方法

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE)
            endpoint: API 端点
            **kwargs: 其他请求参数

        Returns:
            响应数据字典

        Raises:
            requests.RequestException: 请求失败时抛出
        """
        url = f"{self.config.base_url}{endpoint}"
        # 添加 User-Agent
        headers = kwargs.get('headers', {})
        headers['User-Agent'] = 'iAPI/1.0.0 (http://iapi.baidu-int.com)'
        kwargs['headers'] = headers

        response = self.session.request(
            method,
            url,
            timeout=self.config.timeout,
            **kwargs
        )
        response.raise_for_status()
        return response.json()

    @staticmethod
    def generate_card_url(space_id: str, sequence: int) -> str:
        """生成 iCafe 卡片链接

        Args:
            space_id: 空间 ID，如 "joytest"
            sequence: 卡片序列号（不是数据库 ID）

        Returns:
            卡片链接，格式：https://console.cloud.baidu-int.com/devops/icafe/issue/{space_id}-{sequence}/show

        Example:
            >>> ICafeClient.generate_card_url("joytest", 2023)
            'https://console.cloud.baidu-int.com/devops/icafe/issue/joytest-2023/show'
        """
        return f"https://console.cloud.baidu-int.com/devops/icafe/issue/{space_id}-{sequence}/show"

    @staticmethod
    def generate_card_url_from_card(space_id: str, card: Dict[str, Any]) -> str:
        """从卡片数据生成 iCafe 卡片链接

        Args:
            space_id: 空间 ID，如 "joytest"
            card: 卡片数据字典（通常从 query_cards 或 get_card_by_id 返回）

        Returns:
            卡片链接

        Example:
            >>> result = client.query_cards("joytest", "创建人 = shijiazheng", max_records=1)
            >>> if result.get('cards'):
            ...     url = ICafeClient.generate_card_url_from_card("joytest", result['cards'][0])
        """
        sequence = card.get('sequence')
        if sequence is None:
            raise ValueError("卡片数据中缺少 sequence 字段")
        return ICafeClient.generate_card_url(space_id, sequence)

    # ========================================
    # 1. 根据空间ID和卡片序列号获取单张卡片信息
    # ========================================
    def get_card_by_id(self, space_id: str, sequence: str,
                       show_associations: bool = True,
                       show_children: bool = True,
                       show_okr: bool = True,
                       show_accumulate: bool = True) -> Dict[str, Any]:
        """根据空间 ID 和卡片序列号获取单张卡片信息

        Args:
            space_id: 空间 ID
            sequence: 卡片序列号（如 1856，即 URL 中的卡片编号）
            show_associations: 是否显示关联信息
            show_children: 是否显示子卡片
            show_okr: 是否显示 OKR 信息
            show_accumulate: 是否显示累计信息

        Returns:
            卡片信息字典，包含：id, sequence, title, description, status, assignee, created_at, updated_at 等

        Raises:
            ValueError: 当 space_id 或 sequence 为空时
            requests.RequestException: 请求失败时
        """
        if not space_id or not sequence:
            raise ValueError("space_id 和 sequence 不能为空")

        params = {}
        if show_associations:
            params['showAssociations'] = 'true'
        if show_children:
            params['showChildren'] = 'true'
        if show_okr:
            params['showOkr'] = 'true'
        if show_accumulate:
            params['showAccumulate'] = 'true'

        return self._request(
            "GET",
            f"/api/spaces/{space_id}/cards/{sequence}",
            params=params
        )

    # ========================================
    # 2. 创建卡片
    # ========================================
    def create_card(self, title: str, description: str, space_id: str,
                    card_type: Optional[str] = None,
                    assignee_id: Optional[str] = None,
                    status: Optional[str] = None,
                    priority: Optional[str] = None,
                    comment: Optional[str] = None,
                    **kwargs) -> Dict[str, Any]:
        """创建卡片

        Args:
            title: 卡片标题
            description: 卡片描述，支持 Markdown 或 HTML 格式
            space_id: 所属空间 ID
            card_type: 卡片类型，如 "Story", "Bug", "Task" 等，可选
            assignee_id: 负责人 ID，可选
            status: 流程状态，如 "新建"、"待开发" 等，可选
            priority: 优先级，如 "P1-High", "P2-Medium" 等，可选
            comment: 初始评论，可选
            **kwargs: 其他自定义字段（会放入 fields 中）

        Returns:
            新创建的卡片信息，包含：id, title, description, status, created_at 等

        Raises:
            ValueError: 当 title、description 或 space_id 为空时
            requests.RequestException: 请求失败时

        Note:
            description 参数支持以下格式：
            - 纯文本：直接传递
            - Markdown：自动转换为 HTML（支持加粗、斜体、链接、列表、标题等）
            - HTML：直接传递
        """
        if not title or not description or not space_id:
            raise ValueError("title、description 和 space_id 不能为空")

        # 构建 issue 对象
        issue = {
            'title': title,
            # 自动格式化 description 为 HTML
            'detail': _format_to_html(description)
        }

        if card_type:
            issue['type'] = card_type

        # parent 字段需要放在 issue 根级别
        parent = kwargs.pop('parent', None)
        if parent:
            issue['parent'] = parent

        # 构建自定义字段
        fields = {}
        if assignee_id:
            fields['负责人'] = assignee_id
        if status:
            fields['流程状态'] = status
        if priority:
            fields['优先级'] = priority

        # 添加其他自定义字段到 fields
        for key, value in kwargs.items():
            fields[key] = value

        if fields:
            issue['fields'] = fields
        if comment:
            issue['comment'] = comment

        data = {
            'issues': [issue]
        }

        url = f"{self.config.base_url}/api/v2/space/{space_id}/issue/new"
        headers = {
            'User-Agent': 'iAPI/1.0.0 (http://iapi.baidu-int.com)',
            'Content-Type': 'application/json'
        }

        response = self.session.post(url, json=data, headers=headers, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    # ========================================
    # 3. 创建卡片评论
    # ========================================
    def create_card_comment(self, space_id: str, sequence: str, content: str) -> Dict[str, Any]:
        """创建卡片评论

        Args:
            space_id: 空间 ID
            sequence: 卡片序列号（如 1856，即 URL 中的卡片编号）
            content: 评论内容

        Returns:
            新创建的评论信息，包含：id, content, author, created_at 等

        Raises:
            ValueError: 当 space_id、sequence 或 content 为空时
            requests.RequestException: 请求失败时
        """
        if not space_id or not sequence or not content:
            raise ValueError("space_id、sequence 和 content 不能为空")

        data = {
            'commentMsg': content
        }
        return self._request(
            "POST",
            f"/api/v2/space/{space_id}/issue/{sequence}/comment",
            json=data
        )

    # ========================================
    # 4. 查询最近访问的空间列表
    # ========================================
    def get_latest_spaces(self, current_user: Optional[str] = None) -> List[Dict[str, Any]]:
        """查询最近访问的空间列表

        Args:
            current_user: 当前用户名，默认使用配置的用户名

        Returns:
            最近访问的空间列表，每个空间包含：id, name, prefix_code, access_time 等

        Raises:
            requests.RequestException: 请求失败时
        """
        url = f"{self.config.base_url}/api/v2/space/latest"
        params = {}
        if current_user:
            params['currentUser'] = current_user
        headers = {
            'User-Agent': 'iAPI/1.0.0 (http://iapi.baidu-int.com)'
        }

        response = self.session.get(url, params=params, headers=headers, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    # ========================================
    # 5. 获取空间内所有计划
    # ========================================
    def get_space_plans(self, space_id: str) -> List[Dict[str, Any]]:
        """获取空间内所有计划

        Args:
            space_id: 空间 ID

        Returns:
            计划列表，每个计划包含：id, name, start_date, end_date, status, cards 等

        Raises:
            ValueError: 当 space_id 为空时
            requests.RequestException: 请求失败时
        """
        if not space_id:
            raise ValueError("space_id 不能为空")

        url = f"{self.config.base_url}/api/v2/space/{space_id}/plans"
        params = {}
        headers = {
            'User-Agent': 'iAPI/1.0.0 (http://iapi.baidu-int.com)'
        }

        response = self.session.get(url, params=params, headers=headers, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    # ========================================
    # 6. 查询满足条件的卡片
    # ========================================
    def query_cards(self, space_id: str, iql: str,
                  page: Optional[int] = None,
                  show_detail: bool = False,
                  show_associations: bool = False,
                  is_desc: bool = False,
                  order: Optional[str] = None,
                  show_children: bool = False,
                  max_records: Optional[int] = None,
                  show_okr: bool = False,
                  show_accumulate: bool = False) -> Dict[str, Any]:
        """查询满足条件的卡片

        Args:
            space_id: 空间 ID
            iql: IQL 查询表达式，如 "类型 = Bug AND 负责人 = currentUser"
            page: 页码，可选
            show_detail: 是否显示详情，默认 False
            show_associations: 是否显示关联信息，默认 False
            is_desc: 是否降序排列，默认 False
            order: 排序字段，可选
            show_children: 是否显示子卡片，默认 False
            max_records: 最大返回记录数，可选
            show_okr: 是否显示 OKR 信息，默认 False
            show_accumulate: 是否显示累计信息，默认 False

        Returns:
            查询结果，包含卡片列表、分页信息等

        Raises:
            ValueError: 当 space_id 或 iql 为空时
            requests.RequestException: 请求失败时

        IQL 表达式示例：
            - "类型 = Bug"
            - "负责人 = currentUser"
            - "状态 = 新建"
            - "类型 = Bug AND 负责人 = currentUser"
            - "创建时间 > 2025-01-01"

        Note:
            返回的卡片包含以下字段：
            - id: 数据库唯一 ID
            - sequence: 卡片序列号（用于 URL 拼接）
            - title: 卡片标题
            - type: 卡片类型 {'localId': ..., 'name': ...}
            - status: 流程状态
            - createdTime: 创建时间
            - lastModifiedTime: 最后修改时间
            - createdUser: 创建人 {'username': ..., 'name': ..., ...}
            - lastModifiedUser: 最后修改人
            - responsiblePeople: 负责人列表 [{'username': ..., 'name': ..., ...}]
            - properties: 自定义字段列表
        """
        if not space_id or not iql:
            raise ValueError("space_id 和 iql 不能为空")

        params = {'iql': iql}
        if page is not None:
            params['page'] = page
        if show_detail:
            params['showDetail'] = 'true'
        if show_associations:
            params['showAssociations'] = 'true'
        if is_desc:
            params['isDesc'] = 'true'
        if order:
            params['order'] = order
        if show_children:
            params['showChildren'] = 'true'
        if max_records:
            params['maxRecords'] = max_records
        if show_okr:
            params['showOkr'] = 'true'
        if show_accumulate:
            params['showAccumulate'] = 'true'

        url = f"{self.config.base_url}/api/spaces/{space_id}/cards"
        headers = {
            'User-Agent': 'iAPI/1.0.0 (http://iapi.baidu-int.com)'
        }

        response = self.session.get(url, params=params, headers=headers, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    # ========================================
    # 7. 修改卡片内容
    # ========================================
    def update_card(self, space_id: str, sequence: str,
                    title: Optional[str] = None,
                    description: Optional[str] = None,
                    assignee_id: Optional[str] = None,
                    status: Optional[str] = None,
                    priority: Optional[str] = None,
                    labels: Optional[List[str]] = None,
                    due_date: Optional[str] = None,
                    comment: Optional[str] = None,
                    **kwargs) -> Dict[str, Any]:
        """修改卡片内容

        Args:
            space_id: 空间 ID
            sequence: 卡片序列号（如 1856，即 URL 中的卡片编号）
            title: 新标题，可选
            description: 新描述/内容，支持 Markdown 或 HTML 格式，可选
            assignee_id: 新负责人 ID，可以是单个用户名或逗号分隔的多个用户名，可选
            status: 新流程状态，可选
            priority: 新优先级，可选
            labels: 新标签列表，可选
            due_date: 新截止日期，可选
            comment: 更新评论，可选
            **kwargs: 其他可修改字段，格式为 {字段名: 字段值}，可选

        Returns:
            更新后的卡片信息

        Raises:
            ValueError: 当 space_id 或 sequence 为空时
            requests.RequestException: 请求失败时

        Note:
            description 参数支持以下格式：
            - 纯文本：直接传递
            - Markdown：自动转换为 HTML（支持加粗、斜体、链接、列表、标题等）
            - HTML：直接传递
        """
        if not space_id or not sequence:
            raise ValueError("space_id 和 sequence 不能为空")

        # 构建 fields 参数（字段名=字段值 格式）
        fields_list = []
        if title:
            fields_list.append(f'标题={title}')
        if description:
            # 自动格式化 description 为 HTML，处理换行符
            formatted_description = _format_to_html(description)
            # 对 form data 进行 URL 编码处理，保持 HTML 结构
            fields_list.append(f'内容={formatted_description}')
        if assignee_id:
            fields_list.append(f'负责人={assignee_id}')
        if status:
            fields_list.append(f'流程状态={status}')
        if priority:
            fields_list.append(f'优先级={priority}')
        if due_date:
            fields_list.append(f'截止日期={due_date}')
        # 添加其他自定义字段
        for key, value in kwargs.items():
            if value:
                fields_list.append(f'{key}={value}')

        # 构建 URL 和 form data（确保所有参数在 body 中）
        url = f"{self.config.base_url}/api/spaces/{space_id}/cards/{sequence}"

        # 构建 form data，所有字段都放在 body 中
        data = {'isCheckStatus': False}
        if fields_list:
            data['fields'] = ','.join(fields_list)
        if comment:
            data['comment'] = comment
        if labels:
            data['labels'] = ','.join(labels)

        headers = {
            'User-Agent': 'iAPI/1.0.0 (http://iapi.baidu-int.com)',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # 添加认证 token
        auth_token = self.config._get_auth_token()
        if auth_token:
            headers['x-ac-Authorization'] = auth_token

        # 直接使用 requests.post 确保 data 在 body 中（不使用 session）
        response = requests.post(url, data=data, headers=headers, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()

    # ========================================
    # 8. 查询卡片研发数据链信息
    # ========================================
    def get_card_dev_info(self, space_id: str, sequence: str) -> Dict[str, Any]:
        """查询卡片研发数据链信息

        Args:
            space_id: 空间 ID，如 "mapcio-qatools"
            sequence: 卡片序列号（如 1368，即 URL 中的卡片编号）

        Returns:
            研发数据链信息字典，包含：
            - codeReview: 代码评审信息
            - testCase: 测试用例信息
            - build: 构建信息
            - testRecord: 测试记录信息
            - 等其他研发数据链相关信息

        Raises:
            ValueError: 当 space_id 或 sequence 为空时
            requests.RequestException: 请求失败时
        """
        if not space_id or not sequence:
            raise ValueError("space_id 和 sequence 不能为空")

        url = f"{self.config.base_url}/api/v2/space/{space_id}/issue/{sequence}/devInfo"
        headers = {
            'User-Agent': 'iAPI/1.0.0 (http://iapi.baidu-int.com)'
        }

        # 添加认证 token
        auth_token = self.config._get_auth_token()
        if auth_token:
            headers['x-ac-Authorization'] = auth_token

        response = self.session.get(url, headers=headers, timeout=self.config.timeout)
        response.raise_for_status()
        return response.json()


# ========================================
# 使用示例
# ========================================
if __name__ == "__main__":
    # 方式一：使用默认配置（使用环境变量或登录文件的认证 token）
    client = ICafeClient()

    # 方式二：自定义配置
    # config = ICafeConfig(
    #     base_url="http://10.11.152.208:8701/api/process/icafe",
    #     timeout=30
    # )
    # client = ICafeClient(config)

    # 示例：获取卡片信息
    # card = client.get_card_by_id("joytest", "628")
    # print(card)

    # 示例：更新卡片
    # result = client.update_card("joytest", "628", title="更新后的标题")
    # print(result)
