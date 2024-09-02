import boto3
import sys
from tools import *
import tools
from time import sleep
from prompt import get_system_prompt


def initialize_bedrock_client():
    return boto3.client('bedrock-runtime', region_name='us-west-2')


def get_model_id():
    return 'us.anthropic.claude-3-5-sonnet-20240620-v1:0'


def create_initial_message(repository_path):
    return [{"role": "user", "content": [{"text": repository_path}]}]


def converse_with_model(brt, model_id, messages, usecase):
    return brt.converse(
        system=[{'text': get_system_prompt(usecase)}],
        modelId=model_id,
        messages=messages,
        toolConfig={"tools": get_tools()},
        inferenceConfig={"maxTokens": 4096, 'temperature': 0},
    )


def retry_converse_with_model(
    brt, model_id, messages, usecase, max_retries=10, sleep_time=7
):
    for attempt in range(max_retries):
        try:
            response = converse_with_model(brt, model_id, messages, usecase)
            return response
        except Exception as e:
            if attempt < max_retries - 1:
                print(
                    f"エラーが発生しました: {e}. {sleep_time}秒後にリトライします。(試行 {attempt + 1}/{max_retries})"
                )
                sleep(sleep_time)
            else:
                print(f"最大リトライ回数に達しました。エラー: {e}")
                raise


def list_tools():
    module_attributes = set(dir(tools))
    imported_functions = [
        attr for attr in module_attributes if callable(getattr(tools, attr))
    ]
    return imported_functions


def process_tool_use(assistant_content, tools: list):
    tool_name = assistant_content['toolUse']['name']
    args = assistant_content['toolUse']['input']
    if tool_name not in tools:
        raise ValueError(f"Unknown tool: {tool_name}")
    tool_function = globals()[tool_name]

    if tool_name != 'complete':
        tool_result = tool_function(**args)
        print(tool_result)
        return {
            "toolResult": {
                "toolUseId": assistant_content['toolUse']['toolUseId'],
                "content": [{"text": tool_result}],
            }
        }, True
    else:
        return None, tool_function(**args)


def main():
    usecase = sys.argv[1]
    repository_path = sys.argv[2]
    print('work directory の初期化')
    print(rm_recursive('./work'))
    print(mkdir_p('./work'))
    print('work directory の初期化完了')
    brt = initialize_bedrock_client()
    model_id = get_model_id()
    messages = create_initial_message(repository_path)
    tools = list_tools()
    is_loop = True
    while is_loop:
        try:
            response = retry_converse_with_model(brt, model_id, messages, usecase)
        except Exception as e:
            print(f"会話に失敗しました: {e}")
        output = response["output"]
        print(output['message'])
        messages.append(output['message'])

        user_content = []
        for assistant_content in output['message']['content']:
            if 'toolUse' in assistant_content:
                tool_result, is_loop = process_tool_use(assistant_content, tools)
                if tool_result:
                    user_content.append(tool_result)
            else:
                print('loop done')
                is_loop = False
                print(messages[-1])

        if user_content:
            messages.append(
                {
                    'role': 'user',
                    "content": user_content,
                }
            )
            print(messages[-1])

        print(f"Is loop continuing: {is_loop}")


if __name__ == "__main__":
    main()
