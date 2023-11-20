import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime, timedelta
import re

def parse_page():
    url = 'https://www.yckceo.com/yuedu/shuyuans/index.html'
    response = requests.get(url, verify=False)
    soup = BeautifulSoup(response.text, 'html.parser')

    relevant_links = []
    today = datetime.today().date()

    for div in soup.find_all('div', class_='layui-col-xs12 layui-col-sm6 layui-col-md4'):
        link = div.find('a', href=True)
        date_element = div.find('p', class_='m-right')

        if link and date_element:
            href = link['href']
            link_date_str = date_element.text.strip()

            # Use regex to extract the number of days or hours
            match = re.search(r'(\d+)(天前|小时前)', link_date_str)
            if match:
                value, unit = match.group(1, 2)
                if unit == '小时前':
                    # For hours, consider them as 1 day
                    days_ago = 1
                else:
                    days_ago = int(value)

                link_date = today - timedelta(days=days_ago)

                print(f"Link: {href}, Date String: {link_date_str}, Calculated Date: {link_date}")

                # Check if the link is within the specified time range
                if 1 <= days_ago <= 3:  # Include links from 1 to 3 days ago
                    json_url = f'https://www.yckceo.com{href.replace("content", "json")}'
                    relevant_links.append((json_url, link_date))

    return relevant_links

def get_redirected_url(url):
    session = requests.Session()
    response = session.get(url, verify=False, allow_redirects=False)
    final_url = next(session.resolve_redirects(response, response.request), None)
    return final_url.url if final_url else None

def download_json(url, output_dir='3.0'):
    # Check if the output directory exists, create it if not
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get the redirected URL
    final_url = get_redirected_url(url)
    
    if final_url:
        print(f"Real URL: {final_url}")

        # Download the JSON content from the final URL
        response = requests.get(final_url)

        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            try:
                json_content = response.json()
                id = final_url.split('/')[-1].split('.')[0]

                # Use the provided date if available, otherwise use today
                link_date = None
                for _, date in parse_page():
                    if _ == url:
                        link_date = date
                        break

                if link_date is None:
                    link_date = datetime.today().date()

                output_path = os.path.join(output_dir, f'{id}.json')

                with open(output_path, 'w') as f:
                    json.dump(json_content, f, indent=2, ensure_ascii=False)
                print(f"Downloaded {id}.json to {output_dir}")
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON for {final_url}: {e}")
                print(f"Response Content: {response.text}")
        else:
            print(f"Error downloading {final_url}: Status code {response.status_code}")
            print(f"Response Content: {response.text}")
    else:
        print(f"Error getting redirected URL for {url}")

def merge_json_files(input_dir='3.0', output_file='merged.json'):
    all_data = []

    # Check if the merged.json file already exists
    if os.path.exists(output_file):
        with open(output_file) as f:
            all_data = json.load(f)

    for filename in os.listdir(input_dir):
        if filename.endswith('.json'):
            with open(os.path.join(input_dir, filename)) as f:
                data = json.load(f)
                all_data.extend(data)
            # Delete the processed JSON file
            os.remove(os.path.join(input_dir, filename))

    with open(output_file, 'w') as f:
        # Write JSON content with the outermost square brackets
        f.write(json.dumps(all_data, indent=2, ensure_ascii=False))

def main():
    urls = parse_page()
    for url, _ in urls:
        download_json(url)

    merge_json_files()

if __name__ == "__main__":
    main()
