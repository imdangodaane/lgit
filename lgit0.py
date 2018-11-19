#!/usr/bin/env python3
import os
import sys
import argparse
import hashlib
import datetime


def get_cmd():
    # Create command argument for handling
    parser = argparse.ArgumentParser(prog='lgit')
    sub_parsers = parser.add_subparsers(help='sub-command help')

    init_parser = sub_parsers.add_parser('init', help='Create an empty lgit \
    directory or reinitialize an existing one')
    init_parser.add_argument('init', action='store_true')

    add_parser = sub_parsers.add_parser('add', help='Add file content to \
    the index')
    add_parser.add_argument('add', nargs='+', action='store')

    rm_parser = sub_parsers.add_parser('rm', help='Remove files from the \
    index')
    rm_parser.add_argument('rm')

    config_parser = sub_parsers.add_parser('config', help='Get and set \
    repository or global options')
    config_parser.add_argument('config', action='store_true')
    config_parser.add_argument('--author', help='Author help')

    commit_parser = sub_parsers.add_parser('commit', help='Record changes \
    to the directory')
    commit_parser.add_argument('commit', action='store_true')
    commit_parser.add_argument('-m', help='message help')

    status_parser = sub_parsers.add_parser('status', help='Show the working \
    tree status')
    status_parser.add_argument('status', action='store_true')

    ls_files_parser = sub_parsers.add_parser('ls-files', help='Show \
    information about files in the index and the working tree')
    ls_files_parser.add_argument('ls_files', action='store_true')

    log_parser = sub_parsers.add_parser('log', help='Show commit logs')
    log_parser.add_argument('log', action='store_true')

    args = parser.parse_args()

    if 'init' in args:
        return 'init', None
    if 'add' in args:
        return 'add', args.add
    if 'rm' in args:
        return 'rm', args.rm
    if 'config' in args:
        return 'config', args.author
    if 'commit' in args:
        return 'commit', args.m
    if 'status' in args:
        return 'status', None
    if 'ls_files' in args:
        return 'ls_files', None
    if 'log' in args:
        return 'log', None
    if len(vars(args)) < 1:
        print('fatal: no command was added, add -h to know more')
        sys.exit()


def lgit_get(file, cmd):
    # Open and get content from the file
    try:
        fd = os.open(file, os.O_RDONLY)
        file_content = os.read(fd, os.stat(file).st_size)
        os.close(fd)
    except PermissionError:
        print('error: open("%s"): Permission denied' % file)
        print('error: unable to index file test')
        print('fatal: adding files failed')
        sys.exit()
    except FileNotFoundError:
        print("fatal: pathspec '%s' did not match any files" % file)
        sys.exit()
    if cmd == 'content_byte':
        return file_content
    elif cmd == 'content_str':
        return file_content.decode()
    elif cmd == 'sha1':
        return hashlib.sha1(file_content).hexdigest()
    elif cmd == 'tracked_files':
        tracked_files = []
        lines = file_content.decode().split('\n')
        for line in lines:
            if len(line) > 0:
                tracked_files.append(line.split()[-1])
        return tracked_files
    elif cmd == 'timestamp':
        dt = datetime.datetime.fromtimestamp(os.stat(file).st_mtime)
        return dt.strftime('%Y%m%d%H%M%S')
    else:
        print('Please add command to lgit_get')
        sys.exit()


def get_all_files(dir_name=None):
    files = []
    # Get all files and sub files in directories
    list_dir = os.listdir(dir_name)
    if '.git' in list_dir:
        list_dir.remove('.git')
    if '.lgit' in list_dir:
        list_dir.remove('.lgit')
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


def find_file_line(file_name, content):
    for line in content.split('\n'):
        if len(line) > 0 and file_name == line.split()[-1]:
            return content.find(line)


def update_index():
    '''
    This function update new SHA1 of file to index if there's change in file
    and handle error of file if it was deleted or modified
    Return two fields of files:
    - Deleted files
    - Modified files
    '''
    modified_files = []
    deleted_files = []
    content = lgit_get(index_path, 'content_str')
    all_files = get_all_files()
    # Handle error if index is an empty file
    if len(content) == 0 and len(all_files) == 0:
        print('On branch master\n\nInitial commit\n\nnothing to commit \
(create/copy files and use ""./lgit.py add" to track)')
        sys.exit()
    # Else:
    lines = content.split('\n')
    for line in lines:
        if len(line) == 0:
            continue
        line_index = content.find(line)
        tracked_file = line.split()[-1]
        try:
            fd = os.open(tracked_file, os.O_RDONLY)
            os.close(fd)
            file_mtime = lgit_get(tracked_file, 'timestamp')
            file_sha1 = lgit_get(tracked_file, 'sha1')
            if file_sha1 != line.split()[2]:
                modified_files.append(tracked_file)
            fd = os.open(index_path, os.O_WRONLY)
            os.lseek(fd, line_index, 0)
            os.write(fd, file_mtime.encode())
            os.lseek(fd, line_index + delta_1st_sha1, 0)
            os.write(fd, file_sha1.encode())
            os.close(fd)
        except FileNotFoundError:
            deleted_files.append(tracked_file)
        except PermissionError:
            modified_files.append(tracked_file)
    return modified_files, deleted_files


def lgit_status():
    '''
    This function include multiple action to show the status of lgit
    - Update index if file was be modified
    - Show status of untrack files, to be commited and not stage for commit
    files
    '''
    new_files = []
    modified_files, deleted_files = update_index()

    to_be_commit = []
    not_staged = []
    untracked_files = []

    all_files = get_all_files()
    tracked_files = lgit_get(index_path, 'tracked_files')

    for file in all_files:
        if file not in tracked_files:
            untracked_files.append(file)

    content = lgit_get(index_path, 'content_str')
    lines = content.split('\n')
    for line in lines:
        time = line[:14]
        first_sha1 = line[15:55]
        second_sha1 = line[56:96]
        third_sha1 = line[97:137]
        file_name = line.split()[-1]
        # Find group of file
        if third_sha1 == ' ' * 40:
            new_files.append(file_name)
        if second_sha1 != third_sha1:
            to_be_commit.append(file_name)
            modified_files.append(file_name)
        if first_sha1 != second_sha1:
            not_staged.append(file_name)
    # Print HEAD
    print('On branch master')
    if len(os.listdir(commits_path)) == 0:
        print('\nNo commits yet\n')
    # Print change to be commited files
    if to_be_commit:
        print('Changes to be committed:\n  (use "./lgit.py reset HEAD ..." \
to unstage)\n')
        for file in to_be_commit:
            if file in new_files:
                print('\033[0;32m\tnew file:   %s' % file)
            elif file in modified_files:
                print('\033[0;32m\tmodified:   %s' % file)
            elif file in deleted_files:
                print('\033[0;31m\tdeleted:   %s' % file)
        print('\033[0m')
    # Print not staged for commit files
    if not_staged:
        print('Changes not staged for commit:\n  (use "./lgit.py add ..." \
to update what will be commited)\n  (use "./lgit.py checkout -- ..." \
to discard changes in working directory)\n')
        for file in not_staged:
            # if file in new_files:
            #     print('\tnew file:   %s' % file)
            if file in deleted_files:
                print('\033[0;31m\tdeleted:   %s' % file)
            elif file in modified_files:
                print('\033[0;31m\tmodified:   %s' % file)
        print('\033[0m')
    # Print untracked files
    if untracked_files:
        print('Untracked files:\n  (use "./lgit.py add <file>..." to include \
in what will be commited)\n')
        for file in untracked_files:
            print('\033[0;31m\t%s' % file)
        print('\033[0m')
    # If there're no not stage files, print no changes...
    if not not_staged:
        print('no changes added to commit (use ".lgit.py add and/or "\
.lgit.py commit -a")')


def lgit_add(file_name):
    # Get file content
    file_content = lgit_get(file_name, 'content_byte')
    # Get readable timestamp of file
    time = lgit_get(file_name, 'timestamp')
    file_sha1 = lgit_get(file_name, 'sha1')
    init_info = (time + ' ' + file_sha1 + ' ' + file_sha1 + ' ' + ' ' * 40 +
                 ' ' + file_name + '\n')
    index = None
    # Create directory contain file to store by SHA1 hash
    try:
        os.mkdir(os.path.join(objects_path, file_sha1[:2]))
    except FileExistsError:
        pass
    try:
        os.mknod(os.path.join(objects_path, file_sha1[:2], file_sha1[2:]))
    except FileExistsError:
        pass
    # Write content to the file stored in lgit database
    fd = os.open(os.path.join(objects_path, file_sha1[:2], file_sha1[2:]),
                 os.O_WRONLY)
    os.write(fd, file_content)
    os.close(fd)
    # Write file information to index file
    # If file was not stage in index, write a new information for file,
    # if there're file informations in index, find index of informations
    # and write new set of those
    f = open(index_path, 'r+')
    content = f.read()
    if len(content) == 0:
        f.write(init_info)
    else:
        for line in content.split('\n'):
            if len(line) > 0 and file_name == line.split()[-1]:
                index = content.find(line)
                break
        if index == -1 or index is None:
            f.write(init_info)
        else:
            fd = os.open(index_path, os.O_RDWR)
            os.lseek(fd, index + delta_timestamp, 0)
            os.write(fd, time.encode())
            os.lseek(fd, index + delta_1st_sha1, 0)
            os.write(fd, file_sha1.encode())
            os.lseek(fd, index + delta_2nd_sha1, 0)
            os.write(fd, file_sha1.encode())
            os.close(fd)
    f.close()


def commit_update_index():
    '''
    This function update index (update the third sha1 to index file)
    '''
    content = lgit_get(index_path, 'content_str')
    lines = content.split('\n')
    fd = os.open(index_path, os.O_WRONLY)
    for line in lines:
        if len(line) > 0:
            line_index = content.find(line)
            second_sha1 = line.split()[2]
            os.lseek(fd, line_index + delta_3rd_sha1, 0)
            os.write(fd, second_sha1.encode())
    os.close(fd)


def lgit_commit(message):
    timestamp = datetime.datetime.today().strftime('%Y%m%d%H%M%S.%f')
    f = open(config_path, 'r')
    author_name = f.read().split('=')[1]
    f.close()
    commit_update_index()
    commit_name = os.path.join(commits_path, timestamp)
    snap_name = os.path.join(snapshots_path, timestamp)
    os.mknod(commit_name, mode=0o644)
    os.mknod(snap_name, mode=0o644)
    f = open(commit_name, 'r+')
    f.write(author_name + '\n' + timestamp[:14] + '\n\n' + message + '\n\n')
    f.close()
    content = lgit_get(index_path, 'content_str')
    lines = content.split('\n')
    f = open(snap_name, 'r+')
    for line in lines:
        if len(line) > 0:
            f.write(line[delta_3rd_sha1:] + '\n')
    f.close()


def lgit_log():
    temp = os.listdir(commits_path)
    if len(temp) == 0:
        print("fatal: your current branch 'master' does not have any \
commits yet")
        sys.exit()
    for name in temp:
        commit_name = os.path.join(commits_path, name)
        f = open(commit_name, 'r')
        content = f.read()
        f.close()
        author_name = content.split('\n')[0]
        tim = content.split('\n')[1]
        commit_message = content.split('\n')[3]
        date = datetime.datetime.strptime(tim, '%Y%m%d%H%M%S')
        date = date.strftime('%a %b %d %H:%M:%S %Y')
        print('commit', name)
        print('Author:', author_name)
        print('Date:', date)
        print('\n\t%s\n\n' % commit_message)


def lgit_rm(file_name):
    # Find file if exist and remove file from staging index
    content = lgit_get(index_path, 'content')
    tracked_files = lgit_get(index_path, 'tracked_files')
    if file_name not in tracked_files:
        print("fatal: pathspec '%s' did not match any files" % file_name)
        sys.exit()
    lines = content.split('\n')
    for i in range(len(lines)):
        if len(lines[i]) > 0:
            if file_name == lines[i].split()[-1]:
                lines.remove(lines[i])
                # Remove file from current working directory
                if os.path.exists(file_name):
                    os.remove(file_name)
                break
    # Write new info to index
    f = open(index_path, 'w')
    for line in lines:
        if len(line) > 0:
            f.write(line + '\n')
    f.close()


def lgit_config(name):
    f = open(config_path, 'w')
    f.write('LOGNAME=' + name)
    f.close()


def lgit_ls_files():
    files = lgit_get(index_path, 'tracked_files')
    for file in files:
        print(file)


def re_init():
    print('Reinitialized existing lgit repository in %s'
          % os.path.realpath('.lgit'))


def check_and_init():
    if os.path.exists('.lgit'):
        if os.path.isfile('.lgit'):
            print('fatal: Invalid gitfile format: %s'
                  % os.path.realpath('.lgit'))
            sys.exit()
        if os.path.isdir('.lgit'):
            re_init()
    else:
        lgit_init()


def lgit_init():
    '''
    Initialize .lgit directory contains all directories and files needed for
    lgit command. Directories and files include:
    - Directories:
        + objects
        + commits
        + snapshots
    - Files:
        + index
        + config (contain name of the author (environment variable: LOGNAME))
    '''
    dirs = [
            '.lgit',
            '.lgit/objects',
            '.lgit/commits',
            '.lgit/snapshots'
    ]
    files = [
             '.lgit/index',
             '.lgit/config'
    ]
    for dir in dirs:
        os.mkdir(dir)
    for file in files:
        os.mknode(file)
        if file == '.lgit/config':
            fd = os.open(file, os.O_WRONLY)
            os.write(fd, ('LOGNAME=' + os.environ['LOGNAME']).encode())
            os.close(fd)
    print('Initialized empty lgit repository in %s' \
    % os.path.realpath('.lgit'))


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


def main():
    global lgit_path, objects_path, commits_path, snapshots_path, \
           index_path, config_path, delta_timestamp, delta_1st_sha1, \
           delta_2nd_sha1, delta_3rd_sha1

    lgit_path = find_lgit_dir()
    objects_path = os.path.join(lgit_path, 'objects')
    commits_path = os.path.join(lgit_path, 'commits')
    snapshots_path = os.path.join(lgit_path, 'snapshots')
    index_path = os.path.join(lgit_path, 'index')
    config_path = os.path.join(lgit_path, 'config')

    delta_timestamp = 0
    delta_1st_sha1 = 15
    delta_2nd_sha1 = 56
    delta_3rd_sha1 = 97

    cmd, file = get_cmd()
    if 'init' in cmd:
        check_and_init()
    if 'status' in cmd:
        lgit_status()
    if 'commit' in cmd:
        lgit_commit(file)
    if 'add' in cmd:
        lgit_add(file)
    if 'rm' in cmd:
        lgit_rm(file)
    if 'config' in cmd:
        lgit_config(file)
    if 'ls_files' in cmd:
        lgit_ls_files()
    if 'log' in cmd:
        lgit_log()


if __name__ == '__main__':
    main()
