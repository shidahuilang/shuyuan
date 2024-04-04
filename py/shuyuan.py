import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import re
import urllib3
import urllib.parse
import shutil
import pytz
import time
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

urls = [
    'https://www.yckceo.com/yuedu/shuyuan/index.html',
    'https://www.yckceo.com/yuedu/shuyuans/index.html',
]

# 定义不同网址对应的时间范围，单位为天
time_ranges = {
    'https://www.yckceo.com/yuedu/shuyuan/index.html': (1, 4),
    'https://www.yckceo.com/yuedu/shuyuans/index.html': (1, 10),
}

def parse_page(url):
    response = requests.get(url, verify=True)
    if response.status_code != 200:
        print(f'Access {url}: response.status_code')
        return []
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
                    days_ago = 1
                elif unit == '小时前':
                    days_ago = 1
                else:
                    days_ago = int(value)

                link_date = today - timedelta(days=days_ago)
                time_range = time_ranges.get(url, (0, float('inf')))
                if time_range[0] <= days_ago <= time_range[1]:
                    json_url = f'https://www.yckceo.com{href.replace("content", "json")}'
                    relevant_links.append((json_url, link_date))
            else:
                # Try to parse the date in the format MM/DD HH:MM
                try:
                    date_format = "%m/%d %H:%M"
                    link_date = datetime.strptime(link_date_str, date_format)
                    link_date = link_date.replace(year=today.year)  # Assume the year is the same as today's year

                    # Check if the link is within the specified time range for the current URL
                    time_range = time_ranges.get(url, (0, float('inf')))
                    if today - link_date.date() <= timedelta(days=time_range[1]):
                        json_url = f'https://www.yckceo.com{href.replace("content", "json")}'
                        relevant_links.append((json_url, link_date.date()))
                except ValueError as e:
                    print(f"Error parsing date for {url}: {e}")

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


        json_url = final_url.replace('.html', '.json')
        response = requests.get(json_url, verify=True) 

        if response.status_code == 200:
            try:
                json_content = response.json()
                id = json_url.split('/')[-1].split('.')[0]


                filename = os.path.basename(urllib.parse.urlparse(json_url).path)

             
                output_dir = 'shuyuan_data' if 'shuyuan' in json_url else 'shuyuans_data'
                output_path = os.path.join(output_base_dir, output_dir, filename)

                os.makedirs(os.path.join(output_base_dir, output_dir), exist_ok=True)

                with open(output_path, 'w') as f:
 
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
   
    directory = directory or os.getcwd()
    full_path = os.path.abspath(os.path.join(root_dir, directory))

    try:

        if os.path.exists(full_path):
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
        else:
            print(f"Directory does not exist: {full_path}")
    except OSError as e:
        print(f"Unable to clean old files in {full_path}: {e}")

def beautify_json_files(directory='', root_dir=''):
 
    directory = directory or os.getcwd()
    full_path = os.path.join(root_dir, directory)

    try:

        if os.path.isfile(full_path):
            beautify_json_file(full_path)
            print(f"成功美化 JSON 文件: {full_path}")
        elif os.path.isdir(full_path):
           
            for filename in os.listdir(full_path):
                if filename.endswith('.json'):
                    file_path = os.path.join(full_path, filename)
                    beautify_json_file(file_path)
                    print(f"成功美化 JSON 文件: {file_path}")

            print(f"成功美化目录中的所有 JSON 文件: {full_path}")
        else:
            print(f"无效路径: {full_path}")
    except OSError as e:
        print(f"无法美化 JSON 文件：{full_path}，错误信息：{e}")

def beautify_json_file(file_path):
    try:
        with open(file_path, 'r') as f:

            json_data = json.load(f)
        with open(file_path, 'w') as f:
 
            json.dump(json_data, f, indent=2, ensure_ascii=False)
        print(f"成功美化文件：{file_path}")
    except Exception as e:
        print(f"美化文件时出错：{file_path}，错误信息：{e}")


def merge_json_files(input_dir='', output_file='merged.json', root_dir=''):

    input_dir = os.path.join(root_dir, input_dir)


    if input_dir and not os.path.exists(input_dir):
        os.makedirs(input_dir)

  
    clean_old_files(directory='shuyuan_data', root_dir=root_dir)
    clean_old_files(directory='shuyuans_data', root_dir=root_dir)

   
    for url, _ in parse_page(urls[0]):
        
        output_dir = 'shuyuan_data' if 'shuyuan' in url else 'shuyuans_data'
        download_json(url, output_base_dir=root_dir)  
        print(f"Processed URL: {url}")  

    for url, _ in parse_page(urls[1]): 
       
        output_dir = 'shuyuan_data' if 'shuyuan' in url else 'shuyuans_data'
        download_json(url, output_base_dir=root_dir)
        print(f"Processed URL: {url}") 

    for dir_name in ['shuyuan_data', 'shuyuans_data']:
        dir_path = os.path.join(root_dir, dir_name)
        if not os.path.exists(dir_path):
            print(f"Folder does not exist: {dir_path}")
            continue

        all_data = []

        for filename in os.listdir(dir_path):
            if filename.endswith('.json'):
                with open(os.path.join(dir_path, filename)) as f:
                    data = json.load(f)
                    all_data.extend(data)


        output_path = os.path.join(root_dir, f"{dir_name}.json")
        with open(output_path, 'w') as f:
            f.write(json.dumps(all_data, indent=2, ensure_ascii=False))
            print(f"合并的数据保存到 {output_path}")


        beautify_json_files(f"{dir_name}.json", root_dir)

def updateDate(readMePath):
    text_list = []
    tz = pytz.timezone('Asia/Shanghai')  # 东八区
    dateNow = datetime.fromtimestamp(int(time.time()), tz).strftime('%Y-%m-%d %H:%M:%S %Z%z')

    with open(readMePath, 'r', encoding="UTF-8") as f:
        for lineTmp in f.readlines():
            if re.search('自动更新时间', lineTmp):
                print('旧的: \t' + lineTmp)
                lineTmp = '**自动更新时间** ' + dateNow + '\n'
                text_list.append(lineTmp)
            else:
                text_list.append(lineTmp)

    with open(readMePath, 'w+', encoding="UTF-8") as f2:
        for text in text_list:
            f2.write(text)
            
def merge_book_json(root_dir=''):
    shuyuan_data_path = os.path.join(root_dir, 'shuyuan_data.json')
    shuyuans_data_path = os.path.join(root_dir, 'shuyuans_data.json')
    book_path = os.path.join(root_dir, 'book.json')

    try:
        with open(shuyuan_data_path, 'r') as shuyuan_file, open(shuyuans_data_path, 'r') as shuyuans_file:
            shuyuan_data = json.load(shuyuan_file)
            shuyuans_data = json.load(shuyuans_file)

            book_data = shuyuan_data + shuyuans_data

            with open(book_path, 'w') as book_file:
                json.dump(book_data, book_file, indent=2, ensure_ascii=False)
                print(f"合并的数据保存到 {book_path}")

    except Exception as e:
        print(f"合并JSON文件时发生错误：{e}")

def main():
    root_dir = os.getcwd()

    # 合并 JSON 文件
    merge_json_files(root_dir=root_dir)

    # 合并 shuyuan_data.json 和 shuyuans_data.json 为 book.json
    merge_book_json(root_dir=root_dir)

    readMePath = "README.md"
    updateDate(readMePath)

if __name__ == "__main__":
    main()
