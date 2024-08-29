import boto3
import sys
from tools import *
from time import sleep

def initialize_bedrock_client():
    return boto3.client('bedrock-runtime',region_name='us-west-2')

def get_model_id():
    return 'us.anthropic.claude-3-5-sonnet-20240620-v1:0'

def create_initial_message(repository_path):
    return [
        {
            "role": "user",
            "content": [{"text": repository_path}]
        }
    ]

def get_system_prompt():
    return '''あなたはコード解析が得意な AI です。
リポジトリのパスを与えるので、リポジトリから plantuml 形式で class 図を ./class.puml というファイル名で作成してください。
ただしクラス図には必ず class 名、property, method を含めてください。また見つけたコードはすべて読んでください。
また、各作業をする前に人間の入力を元にした AI の思考過程を必ず ./thinking.txt に日本語で残してください。
write ツールの at モードで思考を追記でき、AI 自身が cat ツールで読み直すことができます。
AI からの出力に会話は不要で与えたツールだけを使って作業してください。
'''

def converse_with_model(brt, model_id, messages):
    return brt.converse(
        system=[{'text': get_system_prompt()}],
        modelId=model_id,
        messages=messages,
        toolConfig={"tools": get_tools()},
        inferenceConfig={
            "maxTokens": 4096,
            'temperature': 0
        },
    )

def retry_converse_with_model(brt, model_id, messages, max_retries=5, sleep_time=5):
    for attempt in range(max_retries):
        try:
            response = converse_with_model(brt, model_id, messages)
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                print(f"エラーが発生しました: {e}. {sleep_time}秒後にリトライします。(試行 {attempt + 1}/{max_retries})")
                sleep(sleep_time)
            else:
                print(f"最大リトライ回数に達しました。エラー: {e}")
                raise

def process_tool_use(assistant_content):
    tool_name = assistant_content['toolUse']['name']
    args = assistant_content['toolUse']['input']
    
    if tool_name != 'complete':
        tool_result = eval(tool_name)(**args)
        print(tool_result)
        return {
            "toolResult": {
                "toolUseId": assistant_content['toolUse']['toolUseId'],
                "content": [{"text": tool_result}],
            }
        }, True
    else:
        return None, eval(tool_name)(**args)

def main():
    repository_path = sys.argv[1]
    brt = initialize_bedrock_client()
    model_id = get_model_id()
    messages = create_initial_message(repository_path)
    
    is_loop = True
    while is_loop:
        try:
            response = retry_converse_with_model(brt, model_id, messages)
        except Exception as e:
            print(f"会話に失敗しました: {e}")
        
        output = response["output"]
        print(output['message'])
        messages.append(output['message'])
        
        user_content = []
        for assistant_content in output['message']['content']:
            if 'toolUse' in assistant_content:
                tool_result, is_loop = process_tool_use(assistant_content)
                if tool_result:
                    user_content.append(tool_result)
            else:
                print('loop done')
                is_loop = False
                print(messages[-1])
        
        if user_content:
            messages.append({
                'role': 'user',
                "content": user_content,
            })
            print(messages[-1])
        
        print(f"Is loop continuing: {is_loop}")

if __name__ == "__main__":
    main()