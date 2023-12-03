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

            if matches:
                for tv_channel, link in matches:
                    output_file.write(f'{tv_channel},{link} ')
                print(f'Successfully extracted and saved TV links.')
            else:
                print('No TV links found.')

    except Exception as e:
        print(f'Error: {e}')


output_file_path = 'tvlive.txt'

extract_tv_links_from_url('https://raw.githubusercontent.com/qist/tvbox/master/tvlive.txt', output_file_path)
