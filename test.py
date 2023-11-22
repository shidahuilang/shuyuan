import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import re
import urllib3
import urllib.parse
import shutil

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urls = [
    'https://www.yckceo.com/yuedu/shuyuan/index.html',
    'https://www.yckceo.com/yuedu/shuyuans/index.html',
]

def parse_page(url):
    response = requests.get(url, verify=True)
    soup = BeautifulSoup(response.text, 'html.parser')

    relevant_links = []
    today = datetime.today().date()

    for div in soup.find_all('div', class_='layui-col-xs12 layui-col-sm6 layui-col-md4'):
        link = div.find('a', href=True)
        date_element = div.find('p', class_='m-right')

        if link and date_element:
            href = link['href']
            link_date_str = date_element.text.strip()

            match = re.search(r'(\d+)(天前|小时前|分钟前)', link_date_str)
            if match:
                value, unit = match.group(1, 2)
                if unit == '分钟前':
                    # For minutes, consider them as 1 day
                    days_ago = 1
                elif unit == '小时前':
                    # For hours, consider them as 1 day
                    days_ago = 1
                else:
                    days_ago = int(value)

                link_date = today - timedelta(days=days_ago)

                print(f"Link: {href}, Date String: {link_date_str}, Calculated Date: {link_date}")

                # Check if the link is within the specified time range
                if 1 <= days_ago <= 2:  # Include links from 1 to 3 days ago
                    json_url = f'https://www.yckceo.com{href.replace("content", "json")}'
                    relevant_links.append((json_url, link_date))

    return relevant_links


def get_redirected_url(url):
    session = requests.Session()
    response = session.get(url, allow_redirects=False)

    try:
        if response.status_code == 302:
            # Handling the case where the URL ends with .html and is redirected
            final_url = response.headers['Location']
            return final_url
        elif response.status_code == 200:
            # Handling the case where the URL directly returns content (not a redirection)
            return url
        else:
            print(f"Unexpected status code {response.status_code} for {url}")
            return None
    except KeyError:
        print(f"Error getting redirected URL for {url}")
        return None


def download_json(url, output_base_dir=''):
    final_url = get_redirected_url(url)

    if final_url:
        print(f"Real URL: {final_url}")

        # 下载 JSON 内容
        json_url = final_url.replace('.html', '.json')  # 将.html替换为.json
        response = requests.get(json_url, verify=True)  # 使用正确的 JSON URL 进行请求

        if response.status_code == 200:
            try:
                json_content = response.json()
                id = json_url.split('/')[-1].split('.')[0]

                # 获取文件名
                filename = os.path.basename(urllib.parse.urlparse(json_url).path)

                # 根据链接中的关键词选择文件夹
                output_dir = 'shuyuan_data' if 'shuyuan' in json_url else 'shuyuans_data'
                output_path = os.path.join(output_base_dir, output_dir, filename)

                os.makedirs(os.path.join(output_base_dir, output_dir), exist_ok=True)

                with open(output_path, 'w') as f:
                    # 设置 indent 参数为 2，表示每一层缩进两个空格
                    json.dump(json_content, f, indent=2, ensure_ascii=False)
                print(f"Downloaded {filename} to {output_base_dir}/{output_dir}")

                # Now you can use the original URL for further processing
                print(f"Download URL: {url}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for {json_url}: {e}")
                print(f"Response Content: {response.text}")
        else:
            print(f"Error downloading {json_url}: Status code {response.status_code}")
            print(f"Response Content: {response.text}")
    else:
        print(f"Error getting redirected URL for {url}")


def clean_old_files(directory='', root_dir=''):
    # 如果没有传递目录参数，使用当前工作目录
    directory = directory or os.getcwd()
    full_path = os.path.join(root_dir, directory)  # 使用绝对路径

    try:
        # 删除文件夹中的所有文件
        for filename in os.listdir(full_path):
            file_path = os.path.join(full_path, filename)
            try:
                if os.path.isfile(file_path):
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                    print(f"Deleted directory: {file_path}")
            except Exception as e:
                print(f"Error deleting {file_path}: {e}")

        print(f"Successfully cleaned old files in {full_path}")
    except OSError as e:
        print(f"Unable to clean old files in {full_path}: {e}")


def beautify_json_files(directory='', root_dir=''):
    # 如果没有传递目录参数，使用当前工作目录
    directory = directory or os.getcwd()
    full_path = os.path.join(root_dir, directory)  # 使用绝对路径

    try:
        # 遍历所有文件夹中的所有 JSON 文件，将其转换为美化格式
        for filename in os.listdir(full_path):
            if filename.endswith('.json'):
                file_path = os.path.join(full_path, filename)
                try:
                    with open(file_path, 'r') as f:
                        # 读取 JSON 数据
                        json_data = json.load(f)
                    with open(file_path, 'w') as f:
                        # 将 JSON 数据以美化格式写回文件
                        json.dump(json_data, f, indent=2, ensure_ascii=False)
                    print(f"Beautified file: {file_path}")
                except Exception as e:
                    print(f"Error beautifying {file_path}: {e}")

        print(f"Successfully beautified JSON files in {full_path}")
    except OSError as e:
        print(f"Unable to beautify JSON files in {full_path}: {e}")


def merge_json_files(input_dir='', output_file='merged.json', root_dir=''):
    # 使用绝对路径
    input_dir = os.path.join(root_dir, input_dir)

    # 如果目录不存在，创建它
    if input_dir and not os.path.exists(input_dir):
        os.makedirs(input_dir)

    # 调用 clean_old_files 清除旧文件
    clean_old_files(directory='shuyuan_data', root_dir=root_dir)
    clean_old_files(directory='shuyuans_data', root_dir=root_dir)

    # 遍历所有文件夹，将每个 JSON 文件转换为美化格式
    for url, _ in parse_page(urls[0]):
        # 根据不同的 url 选择不同的输出文件夹
        output_dir = 'shuyuan_data' if 'shuyuan' in url else 'shuyuans_data'
        download_json(url, output_base_dir=root_dir)  # 使用 root_dir，确保使用正确的根目录
        beautify_json_files(output_dir, root_dir)  # 添加此行以确保每个链接下载后都美化 JSON 文件
        print(f"Processed URL: {url}")  # 添加此行以确保每个链接都被处理

    for url, _ in parse_page(urls[1]):  # 添加对第二个 URL 的处理
        # 根据不同的 url 选择不同的输出文件夹
        output_dir = 'shuyuan_data' if 'shuyuan' in url else 'shuyuans_data'
        download_json(url, output_base_dir=root_dir)  # 使用 root_dir，确保使用正确的根目录
        beautify_json_files(output_dir, root_dir)  # 添加此行以确保每个链接下载后都美化 JSON 文件
        print(f"Processed URL: {url}")  # 添加此行以确保每个链接都被处理

    # ...


def main():
    # 存储根目录
    root_dir = os.getcwd()

    # 合并 JSON 文件
    merge_json_files(root_dir=root_dir)

if __name__ == "__main__":
    main()
