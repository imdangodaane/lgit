import os


def get_all_files(dir_name=None):
    files = []
    list_dir = os.listdir(dir_name)
    # Get all files and sub files in directories
    if bool(list_dir):
        for file in list_dir:
            if dir_name:
                name = os.path.join(dir_name, file)
            else:
                name = file
            if os.path.isdir(name):
                files += get_all_files(name)
            if os.path.isfile(name):
                files.append(name)
    return files

untracked_files = ['a', 'b', 'c', 'd', 'e', 'f']
print('Untracked files:\n  (use "./lgit.py add <file>..." to include in what will\
 be commited)\n')
for file in untracked_files:
    print('\t\033[1;31m%s' % file)
print('\033[0;0m')
