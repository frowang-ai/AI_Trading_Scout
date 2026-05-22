#!/usr/bin/env python3
"""
HTML清洗脚本（Agent专用版）：将Tushare API文档清洗为Coding Agent友好的格式
输出：精简的JSON索引 + 精简的Markdown文档（不含数据样例）

目标：保留接口名称、层级路径、描述、输入参数、输出参数、调用示例
"""

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup
from typing import Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 路径配置
current_dir = Path(__file__).parent.resolve()
raw_docs_dir = current_dir / "raw_tushare_api_docs"
output_dir = current_dir / "agent_api_docs"
output_dir.mkdir(exist_ok=True)


def extract_sidebar_category(soup) -> dict:
    """
    从侧边栏提取当前页面的分类路径
    返回: {"path": "股票数据/行情数据/历史日线", "doc_id": "27"}
    """
    sidebar = soup.find('nav', class_='sidebar')
    if not sidebar:
        return {"path": "", "parent_ids": []}
    
    # 查找当前激活的菜单项
    active_item = sidebar.find('li', class_=lambda x: x and 'active' in x)
    if not active_item:
        active_item = sidebar.find('li', class_='jstree-clicked')
    
    if not active_item:
        return {"path": "", "parent_ids": []}
    
    # 向上遍历获取完整路径
    path_parts = []
    parent_ids = []
    current = active_item
    
    while current:
        link = current.find('a', recursive=False)
        if link:
            text = link.get_text().strip()
            href = link.get('href', '')
            if text and text not in path_parts:
                path_parts.insert(0, text)
                # 提取 doc_id
                match = re.search(r'doc_id=(\d+)', href)
                if match:
                    parent_ids.insert(0, match.group(1))
        
        # 向上查找父级 li
        parent = current.find_parent('li')
        if parent and parent != current:
            current = parent
        else:
            break
    
    return {
        "path": "/".join(path_parts[:-1]) if len(path_parts) > 1 else "",  # 不包含自身
        "parent_ids": parent_ids[:-1] if len(parent_ids) > 1 else []
    }


def extract_api_info(soup, content_text: str) -> dict:
    """提取API基本信息：接口名称、描述、积分要求"""
    info = {
        "api_name": "",
        "title": "",
        "description": "",
        "points": 0,
        "update_time": "",
        "limit": ""
    }
    
    # 从内容区提取标题
    content_div = soup.find('div', class_='content')
    if content_div:
        h2 = content_div.find('h2')
        if h2:
            info["title"] = h2.get_text().strip()
    
    # 提取接口名称 - 多种模式匹配
    patterns = [
        r'接口[：:]\s*(\w+)',           # 接口：daily
        r'接口名称[：:]\s*(\w+)',        # 接口名称：pro_bar
        r'pro\.(\w+)\s*\(',             # pro.daily(
        r'ts\.pro_api\(\).*?\.(\w+)\s*\(',  # ts.pro_api()...daily(
    ]
    
    for pattern in patterns:
        match = re.search(pattern, content_text)
        if match:
            api_name = match.group(1)
            # 清理api_name中的后缀（如"描述"、"权限"等）
            api_name = re.sub(r'(描述|权限|接口|说明)$', '', api_name)
            info["api_name"] = api_name
            break
    
    # 提取描述
    desc_patterns = [
        r'描述[：:]\s*([^\n]+)',
        r'数据说明[：:]\s*([^\n]+)',
    ]
    for pattern in desc_patterns:
        match = re.search(pattern, content_text)
        if match:
            info["description"] = match.group(1).strip()
            break
    
    # 提取积分要求
    points_patterns = [
        r'(\d+)\s*积分',
        r'积分[：:]\s*(\d+)',
    ]
    for pattern in points_patterns:
        match = re.search(pattern, content_text)
        if match:
            info["points"] = int(match.group(1))
            break
    
    # 提取更新时间
    time_match = re.search(r'更新时间[：:]\s*([^\n]+)', content_text)
    if time_match:
        info["update_time"] = time_match.group(1).strip()
    
    # 提取限量说明
    limit_match = re.search(r'限量[：:]\s*([^\n]+)', content_text)
    if limit_match:
        info["limit"] = limit_match.group(1).strip()
    
    return info


def extract_table_as_list(table) -> list:
    """将HTML表格提取为字典列表"""
    if not table:
        return []
    
    rows = table.find_all('tr')
    if len(rows) < 2:
        return []
    
    # 提取表头
    headers = []
    header_row = rows[0]
    for th in header_row.find_all(['th', 'td']):
        headers.append(th.get_text().strip())
    
    if not headers:
        return []
    
    # 提取数据行
    result = []
    for row in rows[1:]:
        cells = row.find_all(['td', 'th'])
        if len(cells) >= len(headers):
            row_data = {}
            for i, header in enumerate(headers):
                row_data[header] = cells[i].get_text().strip()
            result.append(row_data)
    
    return result


def extract_parameters(soup) -> dict:
    """提取输入参数和输出参数"""
    params = {
        "inputs": [],
        "outputs": []
    }
    
    content_div = soup.find('div', class_='content')
    if not content_div:
        return params
    
    # 查找所有表格及其前面的标题
    tables = content_div.find_all('table')
    
    for table in tables:
        # 查找表格前面的标题文本
        prev_element = table.find_previous(['p', 'h3', 'h4', 'strong'])
        if prev_element:
            prev_text = prev_element.get_text().strip()
            
            table_data = extract_table_as_list(table)
            
            if '输入参数' in prev_text or '输入' in prev_text:
                params["inputs"] = table_data
            elif '输出参数' in prev_text or '输出' in prev_text:
                params["outputs"] = table_data
    
    return params


def extract_code_examples(soup) -> list:
    """提取代码示例（不含数据样例）"""
    examples = []
    content_div = soup.find('div', class_='content')
    if not content_div:
        return examples
    
    # 查找所有 pre 和 code 块
    code_blocks = content_div.find_all(['pre', 'code'])
    
    for block in code_blocks:
        code_text = block.get_text().strip()
        
        # 过滤掉数据样例（通常包含大量数字和表格数据）
        # 只保留包含函数调用的代码
        if not code_text:
            continue
            
        # 跳过数据样例特征
        if any([
            code_text.count('\n') > 15,  # 太多行的通常是数据样例
            re.search(r'\d{8}\s+\d+\.\d+\s+\d+\.\d+', code_text),  # 日期+数字格式
            'trade_date' in code_text and code_text.count('SZ') > 3,  # 多行股票数据
            code_text.startswith('0 ') or code_text.startswith('1 '),  # DataFrame输出
        ]):
            continue
        
        # 保留包含API调用的代码
        if any([
            'pro.' in code_text,
            'ts.pro_' in code_text,
            'pro_api' in code_text,
            '= pro.' in code_text,
        ]):
            # 清理代码
            code_text = code_text.strip()
            if code_text and code_text not in examples:
                examples.append(code_text)
    
    return examples


def generate_compact_markdown(api_info: dict, category: dict, params: dict, examples: list) -> str:
    """生成精简的Markdown文档"""
    lines = []
    
    # 标题和路径
    title = api_info.get("title") or api_info.get("api_name") or "未知接口"
    lines.append(f"# {title}")
    lines.append("")
    
    if category.get("path"):
        lines.append(f"**路径**: {category['path']}")
    
    if api_info.get("api_name"):
        lines.append(f"**接口**: `{api_info['api_name']}`")
    
    if api_info.get("points"):
        lines.append(f"**积分**: {api_info['points']}")
    
    if api_info.get("description"):
        lines.append(f"**描述**: {api_info['description']}")
    
    if api_info.get("limit"):
        lines.append(f"**限量**: {api_info['limit']}")
    
    lines.append("")
    
    # 输入参数
    if params.get("inputs"):
        lines.append("## 输入参数")
        lines.append("")
        lines.append("| 名称 | 类型 | 必选 | 描述 |")
        lines.append("|------|------|------|------|")
        for p in params["inputs"]:
            name = p.get("名称", p.get("name", ""))
            ptype = p.get("类型", p.get("type", ""))
            required = p.get("必选", p.get("required", ""))
            desc = p.get("描述", p.get("desc", ""))
            lines.append(f"| {name} | {ptype} | {required} | {desc} |")
        lines.append("")
    
    # 输出参数
    if params.get("outputs"):
        lines.append("## 输出参数")
        lines.append("")
        # 检测输出表格的列数
        sample_output = params["outputs"][0] if params["outputs"] else {}
        if "默认显示" in sample_output:
            lines.append("| 名称 | 类型 | 默认显示 | 描述 |")
            lines.append("|------|------|----------|------|")
            for p in params["outputs"]:
                name = p.get("名称", "")
                ptype = p.get("类型", "")
                default = p.get("默认显示", "")
                desc = p.get("描述", "")
                lines.append(f"| {name} | {ptype} | {default} | {desc} |")
        else:
            lines.append("| 名称 | 类型 | 描述 |")
            lines.append("|------|------|------|")
            for p in params["outputs"]:
                name = p.get("名称", "")
                ptype = p.get("类型", "")
                desc = p.get("描述", "")
                lines.append(f"| {name} | {ptype} | {desc} |")
        lines.append("")
    
    # 代码示例
    if examples:
        lines.append("## 调用示例")
        lines.append("")
        for example in examples[:3]:  # 最多3个示例
            lines.append("```python")
            lines.append(example)
            lines.append("```")
            lines.append("")
    
    return "\n".join(lines)


def process_html_file(html_file_path: Path) -> Optional[dict]:
    """处理单个HTML文件"""
    try:
        with open(html_file_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        content_text = soup.get_text()
        
        doc_id = html_file_path.stem
        
        # 提取各类信息
        category = extract_sidebar_category(soup)
        api_info = extract_api_info(soup, content_text)
        params = extract_parameters(soup)
        examples = extract_code_examples(soup)
        
        # 生成精简的Markdown
        markdown_content = generate_compact_markdown(api_info, category, params, examples)
        
        # 保存Markdown文件
        md_file_path = output_dir / f"{doc_id}.md"
        with open(md_file_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # 构建索引记录
        index_record = {
            "doc_id": doc_id,
            "api_name": api_info.get("api_name", ""),
            "title": api_info.get("title", ""),
            "category": category.get("path", ""),
            "description": api_info.get("description", ""),
            "points": api_info.get("points", 0),
            "limit": api_info.get("limit", ""),
            "inputs": [
                {
                    "name": p.get("名称", ""),
                    "type": p.get("类型", ""),
                    "required": p.get("必选", "") == "Y",
                    "desc": p.get("描述", "")
                }
                for p in params.get("inputs", [])
            ],
            "outputs": [p.get("名称", "") for p in params.get("outputs", [])],
            "example": examples[0] if examples else "",
            "url": f"https://tushare.pro/document/2?doc_id={doc_id}",
            "md_path": f"agent_api_docs/{doc_id}.md"
        }
        
        return index_record
        
    except Exception as e:
        logger.error(f"处理文件 {html_file_path} 时出错: {str(e)}")
        return None


def build_category_tree(index_data: list) -> dict:
    """构建分类树结构"""
    tree = {}
    
    for item in index_data:
        category = item.get("category", "")
        if not category:
            category = "其他"
        
        parts = category.split("/")
        current = tree
        
        for part in parts:
            if part not in current:
                current[part] = {"_apis": [], "_children": {}}
            current = current[part]["_children"]
        
        # 添加到最终分类
        if parts:
            # 回溯到正确的位置添加API
            current = tree
            for part in parts[:-1]:
                current = current[part]["_children"]
            if parts[-1] in current:
                current[parts[-1]]["_apis"].append(item["api_name"] or item["doc_id"])
    
    return tree


def main():
    """主函数"""
    logger.info("开始处理HTML文件（Agent专用版）...")
    
    html_files = list(raw_docs_dir.glob("*.html"))
    total_files = len(html_files)
    logger.info(f"找到 {total_files} 个HTML文件")
    
    success_count = 0
    fail_count = 0
    index_data = []
    
    for i, html_file in enumerate(html_files, 1):
        result = process_html_file(html_file)
        
        if result:
            # 只添加有效的API记录（必须有api_name或有输入/输出参数）
            # 排除纯分类页面（如"沪深股票"、"基金数据"等首页）
            is_valid_api = (
                result.get("api_name") and 
                (result.get("inputs") or result.get("outputs") or result.get("example"))
            )
            if is_valid_api:
                index_data.append(result)
            success_count += 1
        else:
            fail_count += 1
        
        if i % 50 == 0:
            logger.info(f"处理进度: {i}/{total_files}")
    
    # 按分类排序
    index_data.sort(key=lambda x: (x.get("category", ""), x.get("api_name", "")))
    
    # 生成主索引文件
    output_index = {
        "meta": {
            "version": "2.0",
            "generated": "2025-11-30",
            "total_apis": len(index_data),
            "description": "Tushare API索引 - Coding Agent专用"
        },
        "apis": index_data
    }
    
    index_file_path = output_dir / "api_index.json"
    with open(index_file_path, 'w', encoding='utf-8') as f:
        json.dump(output_index, f, ensure_ascii=False, indent=2)
    
    # 生成按分类组织的快速查找表
    category_index = {}
    for item in index_data:
        cat = item.get("category", "其他")
        if cat not in category_index:
            category_index[cat] = []
        category_index[cat].append({
            "api_name": item.get("api_name", ""),
            "title": item.get("title", ""),
            "doc_id": item.get("doc_id", "")
        })
    
    category_file_path = output_dir / "category_index.json"
    with open(category_file_path, 'w', encoding='utf-8') as f:
        json.dump(category_index, f, ensure_ascii=False, indent=2)
    
    # 生成API名称快速查找表
    api_lookup = {
        item.get("api_name"): item.get("doc_id")
        for item in index_data
        if item.get("api_name")
    }
    
    lookup_file_path = output_dir / "api_lookup.json"
    with open(lookup_file_path, 'w', encoding='utf-8') as f:
        json.dump(api_lookup, f, ensure_ascii=False, indent=2)
    
    # 输出统计
    logger.info(f"处理完成！")
    logger.info(f"成功: {success_count}, 失败: {fail_count}")
    logger.info(f"有效API记录: {len(index_data)}")
    logger.info(f"输出目录: {output_dir}")
    
    print(f"\n=== 处理结果 ===")
    print(f"成功处理: {success_count} 个文件")
    print(f"有效API: {len(index_data)} 个")
    print(f"输出文件:")
    print(f"  - {index_file_path}")
    print(f"  - {category_file_path}")
    print(f"  - {lookup_file_path}")
    print(f"  - {len(list(output_dir.glob('*.md')))} 个Markdown文件")
    
    # 显示示例记录
    if index_data:
        print(f"\n示例记录:")
        sample = next((x for x in index_data if x.get("api_name") == "daily"), index_data[0])
        print(json.dumps(sample, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
