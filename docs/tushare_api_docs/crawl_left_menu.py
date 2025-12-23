#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TuShare API 文档左侧菜单链接爬取脚本
"""
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup


def fetch_html(url: str) -> str:
    """获取网页HTML源码"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"获取网页失败: {e}")
        sys.exit(1)


def extract_left_menu_links(html: str, base_url: str) -> list[str]:
    """从HTML中提取左侧菜单链接"""
    soup = BeautifulSoup(html, 'html.parser')
    
    # 尝试多种方式查找左侧菜单
    menu_elements = []
    
    # 1. 查找包含sidebar关键词的元素
    menu_elements.extend(soup.find_all(class_=re.compile(r'sidebar', re.I)))
    
    # 2. 查找nav元素
    menu_elements.extend(soup.find_all('nav'))
    
    # 3. 查找aside元素
    menu_elements.extend(soup.find_all('aside'))
    
    # 4. 如果以上都没找到，就查找所有包含menu关键词的元素
    if not menu_elements:
        menu_elements.extend(soup.find_all(class_=re.compile(r'menu', re.I)))
    
    links = []
    
    # 从找到的元素中提取所有链接
    for element in menu_elements:
        for a_tag in element.find_all('a', href=True):
            href = a_tag['href'].strip()
            if href:
                links.append(href)
    
    # 如果还是没有找到，尝试查找页面中所有的链接
    if not links:
        print("未找到明确的左侧菜单，尝试提取页面中所有链接...")
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            if href:
                links.append(href)
    
    return links


def clean_urls(urls: list[str], base_url: str) -> list[str]:
    """清理和规范化URL列表"""
    cleaned_urls = []
    
    for url in urls:
        # 跳过无效协议
        if url.startswith(('javascript:', '#', 'mailto:', 'tel:')):
            continue
        
        # 转换为绝对URL
        absolute_url = urljoin(base_url, url)
        
        # 验证URL格式
        parsed = urlparse(absolute_url)
        if parsed.scheme in ('http', 'https') and parsed.netloc:
            cleaned_urls.append(absolute_url)
    
    # 去重并保持顺序
    seen = set()
    unique_urls = []
    for url in cleaned_urls:
        if url not in seen:
            seen.add(url)
            unique_urls.append(url)
    
    return unique_urls


def save_content(content: str, file_path: Path, encoding: str = 'utf-8') -> None:
    """保存内容到文件"""
    try:
        file_path.write_text(content, encoding=encoding)
        print(f"已保存: {file_path}")
    except Exception as e:
        print(f"保存文件失败: {e}")
        sys.exit(1)


def main():
    """主函数"""
    # 获取当前脚本所在目录
    current_dir = Path(__file__).parent.resolve()
    
    # 目标URL
    target_url = "https://tushare.pro/document/2"
    
    print(f"正在获取网页: {target_url}")
    html_content = fetch_html(target_url)
    
    # 保存原始HTML
    raw_html_path = current_dir / "raw.html"
    save_content(html_content, raw_html_path)
    print(f"原始HTML已保存，大小: {len(html_content)} 字符")
    
    print("正在解析左侧菜单链接...")
    menu_links = extract_left_menu_links(html_content, target_url)
    print(f"找到 {len(menu_links)} 个原始链接")
    
    print("正在清理和规范化URL...")
    clean_links = clean_urls(menu_links, target_url)
    print(f"清理后得到 {len(clean_links)} 个有效链接")
    
    # 保存URL列表
    urls_file_path = current_dir / "left_menu_urls.txt"
    urls_content = "\n".join(clean_links)
    save_content(urls_content, urls_file_path)
    
    print(f"\n任务完成!")
    print(f"原始HTML保存为: {raw_html_path}")
    print(f"URL列表保存为: {urls_file_path}")
    print(f"共提取 {len(clean_links)} 个有效链接")
    
    # 显示前10个链接作为示例
    if clean_links:
        print("\n前10个链接示例:")
        for i, link in enumerate(clean_links[:10], 1):
            print(f"{i}. {link}")


if __name__ == "__main__":
    main()