import json
import os.path
import requests
from concurrent.futures import ThreadPoolExecutor
from urllib3 import disable_warnings

disable_warnings()

class BookChecker:
    def __init__(self, file):
        self.file = file
        self.type = self.recognize_type(self.file)

        # 初始化 Telegram 属性，默认为 None，并尝试从环境变量中获取值
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')

    def recognize_type(self, file: str):
        if file.startswith('http'):
            return 'url'
        elif os.path.exists(file):
            return os.path.splitext(file)[1]
        else:
            return None

    def json_to_books(self):
        if self.type == 'url':
            return requests.get(url=self.file, verify=False).json()
        else:
            with open(self.file, mode='r', encoding='utf-8') as f:
                return json.loads(f.read())

    def check(self, abook, timeout=3):
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36 Edg/114.0.1823.58'
        }

        try:
            status = requests.get(url=abook.get('bookSourceUrl'), verify=False, headers=headers, timeout=timeout).status_code

            if status == 200:
                return {'book': abook, 'status': True}
            else:
                return {'book': abook, 'status': False, 'reason': 'Cannot open URL'}
        except Exception as e:
            return {'book': abook, 'status': False, 'reason': str(e)}

    def check_books(self, workers=16):
        pool = ThreadPoolExecutor(workers)
        books = self.json_to_books()
        ans = list(pool.map(self.check, books))
        good = []
        error = []

        # 不重复书源的下标
        unique_indices = []
        # 所有书源的链接
        urls = [i.get('bookSourceUrl') for i in books]

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

            # 获取重复书源的下标
            if urls.count(i['book']['bookSourceUrl']) > 1:
                unique_indices.append(urls.index(i['book']['bookSourceUrl']))

        unique_indices = list(set(unique_indices))  # 去重

        return {'good': good, 'error': error, 'unique_indices': unique_indices}

    def dedup(self, books: list, unique_indices: list):
        # 不重复书源的下标
        flag = [i for i in range(len(books)) if i not in unique_indices]
        return [books[i] for i in flag]

    def notify_telegram(self, total, good, error, unique):
        if not self.telegram_bot_token or not self.telegram_chat_id:
            print("Telegram Bot的token或chat_id未设置，无法发送通知。")
            return

        url = f'https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage'
        message = f"书源总数：{total}\n有效书源数：{good}\n无效书源数：{error}\n重复书源数：{unique}"

        params = {
            'chat_id': self.telegram_chat_id,
            'text': message
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            print("\nTelegram通知已发送成功！")
        except requests.exceptions.RequestException as e:
            print(f"\nTelegram通知发送失败：{str(e)}")

    def update_readme(self, total, good, error, unique):
        # 读取 README.md 文件的内容
        with open('README.md', 'r', encoding='utf-8') as f:
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
                f"| <span style=\"color:green;\">{total}</span> | <span style=\"color:blue;\">{good}</span> | <span style=\"color:red;\">{error}</span> | <span style=\"color:orange;\">{unique}</span> |\n"
            )

            # 更新新内容到 README.md 文件中
            updated_content = (
                readme_content[:start_index + len(start_marker)]
                + content_to_append
                + readme_content[end_index:]
            )

            # 将新的内容写回到 README.md 文件中
            with open('README.md', 'w', encoding='utf-8') as f:
                f.write(updated_content)
        else:
            print("README.md 中没有找到更新位置的标记。请确保在 README.md 文件中包含 <!-- 更新位置开始 --> 和 <!-- 更新位置结束 -->。")

if __name__ == "__main__":
    # 修改文件路径为你的实际路径
    file_path = "book.json"
    checker = BookChecker(file_path)

    result = checker.check_books()

    # 输出到文件
    good_books = checker.dedup(result['good'], result['unique_indices'])
    error_books = result['error']

    with open('good.json', 'w', encoding='utf-8') as good_file:
        json.dump(good_books, good_file, ensure_ascii=False, indent=2)

    with open('error.json', 'w', encoding='utf-8') as error_file:
        json.dump(error_books, error_file, ensure_ascii=False, indent=2)

    # 发送 Telegram 通知
    checker.notify_telegram(total=len(result['good']) + len(result['error']),
                            good=len(result['good']),
                            error=len(result['error']),
                            unique=len(result['unique_indices']))

    # 更新 README.md 文件
    checker.update_readme(total=len(result['good']) + len(result['error']),
                          good=len(result['good']),
                          error=len(result['error']),
                          unique=len(result['unique_indices']))
