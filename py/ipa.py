import json
import requests

def download_remote_file(remote_url, local_path):
    response = requests.get(remote_url)
    if response.status_code == 200:
        with open(local_path, 'wb') as local_file:
            local_file.write(response.content)

def merge_libraries(library1, library2):
    apps1 = library1.get('apps', [])
    apps2 = library2.get('apps', [])
    merged_apps = apps1 + apps2
    merged_library = library1.copy()
    merged_library['apps'] = merged_apps
    return merged_library

def main():
    # 更改本地路径
    new_test_path = 'ipa/test.json'
    new_local_path = 'ipa/apps.json'
    #remote_url = 'https://raw.githubusercontent.com/swaggyP36000/TrollStore-IPAs/main/apps.json'
    
    # Download remote file
    #download_remote_file(remote_url, new_local_path)

    # Continue with your existing merge logic
    try:
        with open(new_test_path, 'r', encoding='utf-8') as test_file:
            test_content = json.load(test_file)
            if 'apps' not in test_content:
                test_content['apps'] = []
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {new_test_path}: {e}")
        test_content = {'apps': []}

    try:
        with open(new_local_path, 'r', encoding='utf-8') as file2:
            library2 = json.load(file2)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading {new_local_path}: {e}")
        library2 = {'apps': []}

    merged_library = merge_libraries(test_content, library2)

    with open('ipa.json', 'w', encoding='utf-8') as merged_file:
        json.dump(merged_library, merged_file, ensure_ascii=False, indent=4)

    print('Merged library successfully.')
    print(f'Contents of merged_library: {merged_library}')

if __name__ == "__main__":
    main()
