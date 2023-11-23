import os
import json

def format_json_files(input_folder, output_folder):
    # 确保输出文件夹存在
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # 遍历输入文件夹中的所有文件
    for filename in os.listdir(input_folder):
        if filename.endswith(".json"):
            input_file = os.path.join(input_folder, filename)
            output_file = os.path.join(output_folder, filename)

            with open(input_file, 'r') as file:
                json_data = file.read()

            parsed_json = json.loads(json_data)
            formatted_json = json.dumps(parsed_json, indent=4)

            with open(output_file, 'w') as file:
                file.write(formatted_json)

            print("已成功美化并保存文件：", output_file)

# 设置输入文件夹名字和输出文件夹名字
input_folder_name = "json/input"
output_folder_name = "json/output"

# 获取当前脚本所在的目录
script_directory = os.path.dirname(os.path.abspath(__file__))

# 构建输入和输出文件夹的完整路径
input_folder = os.path.join(script_directory, input_folder_name)
output_folder = os.path.join(script_directory, output_folder_name)

# 调用函数美化JSON文件
format_json_files(input_folder, output_folder)
