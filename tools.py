import subprocess

tools = []
tools.append(
    {
        "toolSpec": {
            "name": "cat",
            "description": "テキストファイルの中身を出力するツール。返り値にはテキストファイルの中身が入る",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "input_file_path": {
                            "type": "string",
                            "description": "中身を確認したいテキストファイルのパス",
                        }
                    },
                    "required": ["input_file_path"],
                }
            },
        }
    }
)

tools.append(
    {
        "toolSpec": {
            "name": "ls",
            "description": "ディレクトリの中身の一覧を取得するツール。ls -l {dir} した結果の標準出力が返ってくる。",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "input_directory_path": {
                            "type": "string",
                            "description": "確認したいディレクトリのパス。",
                        }
                    },
                    "required": ["input_directory_path"],
                }
            },
        }
    }
)

tools.append(
    {
        "toolSpec": {
            "name": "write",
            "description": "ファイルにテキストを書き込むツール。返り値には書き込んだファイルのパスが格納される。",
            "inputSchema": {
                "json": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "ファイルに書き込みたい内容",
                        },
                        "write_file_path": {
                            "type": "string",
                            "description": "テキストを書き込むファイルパス",
                        },
                        "mode": {
                            "type": "string",
                            'enum' : ['wt', 'at'],
                            "description": "上書きならば wt, 追記なら at を格納",
                        }
                    },
                    "required": ["content", "write_file_path"],
                }
            },
        }
    }
)

tools.append(
    {
        "toolSpec": {
            "name": "rm",
            "description": "ファイルを削除するツール",
            "inputSchema":{
                "json": {
                    "type": "object",
                    "properties": {
                        "remove_file_path": {
                            "type": "string",
                            "description": "削除したいファイル名",
                        },
                    },
                    "required": ["remove_file_path"],
                }
            }
            
        },
    }
)

tools.append(
    {
        "toolSpec": {
            "name": "rm_recursive",
            "description": "ディレクトリを削除するツール",
            "inputSchema":{
                "json": {
                    "type": "object",
                    "properties": {
                        "remove_dir_path": {
                            "type": "string",
                            "description": "削除したいディレクトリ名",
                        },
                    },
                    "required": ["remove_dir_path"],
                }
            }
            
        },
    }
)

tools.append(
    {
        "toolSpec": {
            "name": "complete",
            "description": "全ての処理が完了した際に結果を出力するツール",
            "inputSchema":{
                "json": {
                    "type": "object",
                    "properties": {
                        "content": {
                            "type": "string",
                            "description": "出力したい内容",
                        },
                    },
                    "required": ["content"],
                }
            }
            
        },
    }
)

def get_tools():
    return tools
    
def cat(input_file_path:str) -> str:
    result = subprocess.run(['cat',input_file_path], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    return output

def ls(input_directory_path:str) -> str:
    result = subprocess.run(['ls', '-l', input_directory_path], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    return output

def write(content, write_file_path, mode) -> str:
    with open(write_file_path,mode) as f:
        f.write(content + '\n')
    return write_file_path

def rm(remove_file_path:str) -> str:
    result = subprocess.run(['rm', remove_file_path ], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    return output

def rm_recursive(remove_dir_path:str) -> str:
    result = subprocess.run(['rm', '-rf', remove_dir_path ], stdout=subprocess.PIPE)
    output = result.stdout.decode('utf-8')
    return output

def complete(content:str) -> bool:
    print(content)
    return False