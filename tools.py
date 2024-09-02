import os
import shutil
import fnmatch
import requests

tools = []
tools.append(
    {
        'toolSpec': {
            'name': 'cat',
            # テキストファイルの中身を出力するツール。返り値にはテキストファイルの中身が入る。
            # エラーが発生した場合は Error: という文言から始まる言葉が返る。
            'description': '''A tool to output the contents of a text file. 
The return value contains the contents of the text file. 
If an error occurs, the output will start with "Error:"''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'input_file_path': {
                            'type': 'string',
                            # 中身を確認したいテキストファイルのパス
                            'description': 'The file path of the text file you want to check the contents of',
                        }
                    },
                    'required': ['input_file_path'],
                }
            },
        }
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'ls',
            # ディレクトリの中身とファイルサイズの一覧を取得するツール。出力形式は {file size} {file name}
            # エラーが発生した場合は Error: という文言から始まる言葉が返る。
            'description': '''Tool to get a list of files and their sizes in a directory. Output format is {file size} {file name}.
If an error occurs, the output will start with "Error:"''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'input_directory_path': {
                            'type': 'string',
                            # ファイル一覧を確認したいディレクトリのパス
                            'description': 'The path of the directory whose file list you want to check',
                        },
                    },
                    'required': ['input_directory_path'],
                }
            },
        }
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'find',
            # 指定ディレクトリ以下のファイルパス一覧を表示するツール
            # 引数にファイル名を与えると、指定したファイル名のファイルだけを表示することもできる。
            # 引数のファイル名はワイルドカードを与えることもでき、*.txt なども可能で、マッチしたファイルのみを出力できる。
            # エラーが発生した場合は Error: という文言から始まる言葉が返る。
            'description': '''A tool to display a list of file paths under a specified directory.
If you provide a file name as an argument, it can also display only the files with the specified file name.
The file name argument can also use wildcards, such as *.txt, and only the matching files will be output.
If an error occurs, the output will start with "Error:"''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'input_directory_path': {
                            'type': 'string',
                            'description': 'The path of the directory you would like to confirm',
                        },
                        'match_file_name': {
                            'type': 'string',
                            # 表示させたいファイル名がわかっている場合の絞り込み文字列。
                            # ワイルドカードも使える。例として、HelloWorld.java や *.txt がなどが入る。
                            'description': '''The filtering string when the file name to be displayed is known. 
Wildcards can also be used. Examples include HelloWorld.java or *.txt.''',
                        },
                    },
                    'required': ['input_directory_path'],
                }
            },
        }
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'mkdir_p',
            # ディレクトリを再帰的に作成するツール
            # 引数に作成したいディレクトリ名を受け付ける。
            # 返り値はディレクトリ作成に成功した場合は"Already exists a directory."を返し、既にディレクトリがあった場合は "Directory created successfully" を返し、エラーが発生した場合は "Error:"から始まる文字列を返す。
            'description': '''A tool to recursively create directories
Accept the directory name to be created as an argument.
The return value is "Already exists a directory." if the directory creation is successful, "Directory created successfully" if the directory already existed, and a string starting with "Error:" if an error occurred.''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'directory_name': {
                            'type': 'string',
                            # ファイルに書き込みたい内容
                            'description': 'directory name to be created',
                        },
                    },
                    'required': ['directory_name'],
                }
            },
        }
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'write',
            # ファイルにテキストを書き込むツール。
            # 返り値は"File written successfully."
            # エラーが発生した場合は Error: という文言から始まる言葉が返る。
            'description': '''A tool to write text to a file.
The return value is "File written successfully".
If an error occurs, the output will start with "Error:"''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'content': {
                            'type': 'string',
                            # ファイルに書き込みたい内容
                            'description': 'Content to be written to the file',
                        },
                        'write_file_path': {
                            'type': 'string',
                            # テキストを書き込むファイルパス
                            'description': 'File path to write text',
                        },
                        'mode': {
                            'type': 'string',
                            'enum': ['wt', 'at'],
                            # 上書きならば wt, 追記なら at を格納
                            'description': 'If overwriting, store as "wt", if appending, store as "at".',
                        },
                    },
                    'required': ['content', 'write_file_path', 'mode'],
                }
            },
        }
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'rm',
            # ファイルを削除するツール
            # エラーが発生した場合は Error: という文言から始まる言葉が返る。
            # もし、成功したら "Successfully removed: {normalized_path}" という文言が返る
            'description': '''File deletion tool
If an error occurs, the output will start with "Error:"
If successful, the message "Successfully removed: {normalized_path}" will be returned.''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'remove_file_path': {
                            'type': 'string',
                            # 削除したいファイル名
                            'description': 'File path to be deleted',
                        },
                    },
                    'required': ['remove_file_path'],
                }
            },
        },
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'rm_recursive',
            # ディレクトリを削除するツール
            # エラーが発生した場合は Error: という文言から始まる言葉が返る。
            # もし、成功したら "Successfully removed directory and its contents {normalized_path}" という文言が返る
            'description': '''Tool to delete a directory
If an error occurs, the output will start with "Error:"
If successful, the message "Successfully removed directory and its contents {normalized_path}" will be returned.''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'remove_dir_path': {
                            'type': 'string',
                            # 削除したいディレクトリ名
                            'description': 'Directory name to be deleted',
                        },
                    },
                    'required': ['remove_dir_path'],
                }
            },
        },
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'get_url_body',
            # URL を与えたら URL にアクセスしコンテンツの body を返すツール。
            # エラーが発生した場合は Error: という文言から始まる言葉が返る。
            'description': '''A tool that takes a URL and accesses the content's body.
If an error occurs, the output will start with "Error:"''',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'url': {
                            'type': 'string',
                            # コンテンツを取得したい URL
                            'description': 'The URL from which you would like to retrieve content',
                        },
                    },
                    'required': ['url'],
                }
            },
        },
    }
)

tools.append(
    {
        'toolSpec': {
            'name': 'complete',
            # 全ての処理が完了したことを知らせるツール
            'description': 'A tool to notify when all processing is complete',
            'inputSchema': {
                'json': {
                    'type': 'object',
                    'properties': {
                        'content': {
                            'type': 'string',
                            # 処理完了のメッセージ
                            'description': 'A message for processing complete',
                        },
                    },
                    'required': ['content'],
                }
            },
        },
    }
)


def get_tools():
    return tools


def cat(input_file_path: str) -> str:
    try:
        if not os.path.exists(input_file_path):
            return f'Error: not found {input_file_path}'
        if not os.access(input_file_path, os.R_OK):
            return f'Error: not have read permission for {input_file_path}'
        with open(input_file_path, 'rt') as f:
            return f.read()
    except Exception as e:
        return f'Error: {e}'


def ls(input_directory_path: str) -> str:
    normalized_path = os.path.normpath(input_directory_path)
    if not os.path.exists(normalized_path) or not os.path.isdir(normalized_path):
        return 'Error: Invalid directory path'
    try:
        files = os.listdir(normalized_path)
        output = []
        for file in files:
            file_path = os.path.join(normalized_path, file)
            stats = os.stat(file_path)
            size = stats.st_size
            output.append(f'{size} {file}')
        return '\n'.join(output)
    except Exception as e:
        return f'Error: {str(e)}'


def find(input_directory_path, match_file_name=None):
    matched_files = []
    try:
        if not os.path.isdir(input_directory_path):
            return (
                f"Error: The specified directory was not found {input_directory_path}"
            )
        for root, _dirnames, filenames in os.walk(input_directory_path):
            try:
                if match_file_name:
                    for filename_pattern in (
                        [match_file_name]
                        if isinstance(match_file_name, str)
                        else match_file_name
                    ):
                        for match in fnmatch.filter(filenames, filename_pattern):
                            matched_files.append(os.path.join(root, match))
                else:
                    matched_files.extend(os.path.join(root, name) for name in filenames)
            except PermissionError:
                print(f'Warning: I do not have access permission to {root}. Skipping.')
    except PermissionError:
        return f'Error: I do not have access permission to {input_directory_path}.'
    except Exception as e:
        return f'Error: {e}'
    if not matched_files:
        return 'Error: No matching files were found.'
    return '\n'.join(matched_files)


def write(content, write_file_path, mode) -> str:
    try:
        with open(write_file_path, mode) as f:
            f.write(content + '\n')
        return 'File written successfully.'
    except Exception as e:
        return f'Error: An unexpected error occurred: {str(e)}'


def mkdir_p(directory):
    try:
        if os.path.exists(directory):
            return 'Already exists a directory.'
        os.makedirs(directory, exist_ok=True)
        return 'Directory created successfully'
    except Exception as e:
        # エラーが発生した場合
        return f'Error: {str(e)}'


def rm(remove_file_path: str) -> str:
    try:
        normalized_path = os.path.normpath(remove_file_path)
        if not os.path.exists(normalized_path):
            return f'Error: File or directory does not exist: {normalized_path}'
        if os.path.isfile(normalized_path):
            os.remove(normalized_path)
        elif os.path.isdir(normalized_path):
            shutil.rmtree(normalized_path)
        return f'Successfully removed: {normalized_path}'
    except Exception as e:
        return f'Error: {str(e)}'


def rm_recursive(remove_dir_path: str) -> str:
    try:
        normalized_path = os.path.abspath(os.path.normpath(remove_dir_path))
        if not os.path.exists(normalized_path):
            return f'Error: Directory does not exist {normalized_path}'
        if not os.path.isdir(normalized_path):
            return f'Error: Not a directory {normalized_path}'
        important_dirs = ['/', '/etc', '/bin', '/sbin', '/var', '/usr', '/home']
        if normalized_path in important_dirs:
            return f'Error: Cannot remove important system directory {normalized_path}'
        shutil.rmtree(normalized_path)
        return f'Successfully removed directory and its contents {normalized_path}'
    except Exception as e:
        return f'Error: {str(e)}'


def get_url_body(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.text
        else:
            return f'Error: Received status code {response.status_code}'
    except requests.RequestException as e:
        return f'Error: {str(e)}'


def complete(content: str) -> bool:
    print(content)
    return False
