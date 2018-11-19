import os
def find_lgit_dir():
    path = os.getcwd()
    dirs = os.listdir(path)
    while '.lgit' not in dirs:
        path = os.path.dirname(os.getcwd())
        os.chdir(path)
        dirs = os.listdir()
        if path == '/home' and '.lgit' not in dirs:
            return None
    return path
print(find_lgit_dir())
