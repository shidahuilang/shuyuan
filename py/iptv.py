import re
import requests

def extract_tv_links_from_url(url, output_file_path):
    try:
        response = requests.get(url)
        response.raise_for_status()

        text = response.text

        with open(output_file_path, 'w', encoding='utf-8') as output_file:
            pattern_ipv6 = re.compile(r'\[.*?\]')
            text = re.sub(pattern_ipv6, '', text)

            pattern = re.compile(r'([^,]+(?:CCTV|卫视|香港|澳门|台湾|凤凰)[^\n,]*[^,]*),(https://[^\s]+)')
            matches = re.findall(pattern, text)

            channel_types_written = set()
            if matches:
                for tv_channel, link in matches:
                    if not should_exclude_channel(tv_channel):
                        header = get_channel_type_header(tv_channel)
                        if header and header not in channel_types_written:
                            output_file.write(f'{header},#genre#\n')
                            channel_types_written.add(header)
                        output_file.write(f'{tv_channel},{link}\n')
                print(f'Successfully extracted and saved TV links.')
            else:
                print('No TV links found.')

    except Exception as e:
        print(f'Error: {e}')

def should_exclude_channel(channel_name):
    # 判断是否要排除特定类型的频道，可以根据需要进行修改
    excluded_keywords = ['台湾女歌手龙飘飘珍藏版HD', '湖南-凤凰古城', '香港佛陀']
    for keyword in excluded_keywords:
        if keyword in channel_name:
            return True
    return False

def get_channel_type_header(channel_name):
    if 'CCTV' in channel_name:
        return '央视频道'
    elif '卫视' in channel_name:
        return '卫视频道'
    elif '香港' in channel_name or '澳门' in channel_name or '凤凰' in channel_name:
        return '港澳频道'
    else:
        return ''


output_file_path = 'iptv.txt'

extract_tv_links_from_url('https://raw.githubusercontent.com/qist/tvbox/master/tvlive.txt', output_file_path)

with open(output_file_path, 'r', encoding='utf-8') as file:
    content = file.read()

content = re.sub(r'#genre#(\s+#genre#)+', '#genre#', content)
content = re.sub(r'\n\s*\n', '\n', content)

with open(output_file_path, 'w', encoding='utf-8') as file:
    file.write(content)
