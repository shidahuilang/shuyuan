import os
import json

def format_and_convert_unicode(input_folder, output_folder, replace_original=False):
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

            # 将JSON字符串解析为Python对象
            parsed_json = json.loads(json_data)

            # 使用json.dumps将Python对象转换为格式化的JSON字符串，同时处理Unicode转义字符
            formatted_json = json.dumps(parsed_json, indent=4, ensure_ascii=False)

            # 写入到输出文件夹
            with open(output_file, 'w', encoding='utf-8') as file:
                file.write(formatted_json)

            print("已成功转换Unicode并美化保存文件：", output_file)

            # 替换原始文件（如果指定了替换原始文件的选项）
            if replace_original:
                os.remove(input_file)
                os.rename(output_file, input_file)
                print("已替换原始文件：", input_file)

# 设置输入文件夹名字和输出文件夹名字
input_folder_name = "json/input"
output_folder_name = "json/output"

# 获取当前脚本所在的目录
script_directory = os.path.dirname(os.path.abspath(__file__))

# 构建输入和输出文件夹的完整路径
input_folder = os.path.join(script_directory, input_folder_name)
output_folder = os.path.join(script_directory, output_folder_name)

# 调用函数转换Unicode并美化JSON文件
format_and_convert_unicode(input_folder, output_folder, replace_original=True)
