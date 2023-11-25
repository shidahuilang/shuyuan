import os
import json
import time
import logging
from urllib3 import disable_warnings
from requests import get
from concurrent.futures import ThreadPoolExecutor

# 禁用 SSL 警告
disable_warnings()

class BookSourceChecker:
    def __init__(self, path, output_path):
        self.input_path = path
        self.output_path = output_path
        self.type = self.recog_type(self.input_path)
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

        # 输出 Telegram Bot Token 和 Chat ID 信息
        logging.info(f"TELEGRAM_BOT_TOKEN: {self.telegram_bot_token}")
        logging.info(f"TELEGRAM_CHAT_ID: {self.telegram_chat_id}")

    def recog_type(self, path: str):
        if path.startswith('http'):
            return 'url'
        elif os.path.exists(path):
            return os.path.splitext(path)[1]
        else:
            return None

    def read_input_file(self):
        if self.type == 'url':
            return get(url=self.input_path, verify=False).json()
        elif os.path.isfile(self.input_path):
            with open(self.input_path, mode='r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    else:
                        logging.error("Invalid JSON format. The JSON file should contain a list of dictionaries.")
                        return []
                except json.decoder.JSONDecodeError:
                    logging.error("Error decoding JSON file. Please check the file format.")
                    return []
        elif os.path.isdir(self.input_path):
            sources = []
            for filename in os.listdir(self.input_path):
                filepath = os.path.join(self.input_path, filename)
                if os.path.isfile(filepath) and filename.lower().endswith('.json'):
                    with open(filepath, mode='r', encoding='utf-8') as f:
                        try:
                            data = json.load(f)
                            if isinstance(data, list):
                                sources.extend(data)
                            else:
                                logging.warning(f"Invalid JSON format in file: {filepath}. Skipping.")
                        except json.decoder.JSONDecodeError:
                            logging.warning(f"Error decoding JSON file: {filepath}. Skipping.")
            return sources
        else:
            return []

    def check(self, abook, timeout=3):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
        }

        try:
            status = get(url=abook.get('bookSourceUrl'), verify=False, headers=headers, timeout=timeout).status_code

            if status == 200:
                return {'book': abook, 'status': True}
            else:
                return {'book': abook, 'status': False}
        except Exception as e:
            return {'book': abook, 'status': False}

    def check_books(self, workers=16):
        pool = ThreadPoolExecutor(workers)
        books = self.read_input_file()
        
        if not books:
            logging.error('Invalid input type or path. Please provide a valid URL or file path.')
            return {'good': [], 'error': []}

        ans = list(pool.map(self.check, books))
        good = []
        error = []

        # 代表当前检测了多少书源
        count = 0
        # 代表书源总数
        count_all = len(books)
        print('-' * 16)
        print('检验进度：')
        for i in ans:
            if i.get('status'):
                good.append(i.get('book'))
            else:
                error.append(i.get('book'))
            # 设计进度条
            count += 1
            per = count / count_all
            p = '#' * int(per * 100 / 5)
            print(f'\r[{p}]', end='')
            print(f' \b{per:.2%}', end='')

        return {'good': good, 'error': error}

    def dedup(self, books: list):
        # 不重复书源的下标
        flag = []
        # 不重复书源的链接
        ans = []
        # 所有书源的链接
        urls = [i.get('bookSourceUrl') for i in books]

        for i in range(len(urls)):
            if urls[i] not in ans:
                ans.append(urls[i])
                flag.append(i)

        return [books[i] for i in flag]

    def write_output_files(self, good_sources, error_sources):
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)

        with open(os.path.join(self.output_path, 'good.json'), 'w', encoding='utf-8') as f:
            json.dump(good_sources, f, ensure_ascii=False, indent=4, sort_keys=False)

        with open(os.path.join(self.output_path, 'error.json'), 'w', encoding='utf-8') as f:
            json.dump(error_sources, f, ensure_ascii=False, indent=4, sort_keys=False)

    def print_validation_summary(self, total_sources, good_sources, error_sources):
        logging.info(f"\n{'-' * 16}\n"
                     "成果报表\n"
                     f"书源总数：{total_sources}\n"
                     f"有效书源数：{good_sources}\n"
                     f"无效书源数：{error_sources}\n"
                     f"重复书源数：{(total_sources - good_sources - error_sources) if error_sources > 0 else '未选择去重'}\n")

    def send_telegram_notification(self, message):
        url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
        data = {
            'chat_id': self.telegram_chat_id,
            'text': message
        }

        logging.info(f"Sending Telegram notification. Message: {message}")

        response = get(url, params=data)
        logging.info(f"Telegram notification response: {response.text}")

        if response.status_code != 200:
            logging.warning(f"Telegram notification failed. Status code: {response.status_code}")

    def append_to_readme(self, content, total_sources, good_sources, error_sources):
        readme_path = 'README.md'

        # 读取 README.md 文件的内容
        with open(readme_path, 'r', encoding='utf-8') as f:
            readme_content = f.read()

        # 根据需要插入的位置，将内容插入到读取的内容中
        start_marker = '<!-- 更新位置开始 -->'
        end_marker = '<!-- 更新位置结束 -->'

        start_index = readme_content.find(start_marker)
        end_index = readme_content.find(end_marker)

        if start_index != -1 and end_index != -1:
            # 构建要插入的内容
            content_to_append = (
                f"\n| 阅读源总数 | 有效书源数 | 无效书源数 | 重复书源数 |\n"
                f"|------------|------------|------------|--------------|\n"
                f"| <span style=\"color:green;\">{total_sources}</span> | <span style=\"color:blue;\">{len(good_sources)}</span> | <span style=\"color:red;\">{len(error_sources)}</span> | <span style=\"color:orange;\">{(total_sources - len(good_sources) - len(error_sources)) if len(error_sources) > 0 else '未检测'}</span> |\n"
            )

            # 更新新内容到 README.md 文件中
            updated_content = (
                readme_content[:start_index + len(start_marker)]
                + content_to_append
                + readme_content[end_index:]
            )

            # 将新的内容写回到 README.md 文件中
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
        else:
            logging.warning("README.md 中没有找到更新位置的标记。请确保在 README.md 文件中包含 <!-- 更新位置开始 --> 和 <!-- 更新位置结束 -->。")


def main():
    input_path = 'xiaoyan/shuru'
    output_path = 'xiaoyan/shuchu'

    books_checker = BookSourceChecker(input_path, output_path)
    results = books_checker.check_books()

    # 处理结果
    good_sources = results['good']
    error_sources = results['error']
    total_sources = len(good_sources) + len(error_sources)

    # 将结果写入输出文件
    books_checker.write_output_files(good_sources, error_sources)

    # 打印检验总结
    books_checker.print_validation_summary(total_sources, len(good_sources), len(error_sources))

    # 写入环境文件
    with open("env.txt", "w") as f:
        f.write(f"阅读源总数：{total_sources}\n")
        f.write(f"有效书源数：{len(good_sources)}\n")
        f.write(f"无效书源数：{len(error_sources)}\n")
        f.write(f"重复书源数：{(total_sources - len(good_sources) - len(error_sources)) if len(error_sources) > 0 else '未检测'}\n")

    # 将 env.txt 文件的内容追加到 README.md 文件的指定位置
    with open("env.txt", "r") as f:
        env_content = f.read()
    books_checker.append_to_readme(env_content, total_sources, good_sources, error_sources)

    # 发送Telegram通知
    message = f"成果报表\n阅读源总数：{total_sources}\n有效书源数：{len(good_sources)}\n无效书源数：{len(error_sources)}\n重复书源数：{(total_sources - len(good_sources) - len(error_sources)) if len(error_sources) > 0 else '未选择去重'}\n"

    # 发送Telegram通知
    books_checker.send_telegram_notification(message)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
