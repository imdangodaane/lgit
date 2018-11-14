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
    add_parser.add_argument('add')

    rm_parser = sub_parsers.add_parser('rm', help='Remove files from the \
    index')
    rm_parser.add_argument('rm', action='store_true')

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
        return 'config', None
    if 'commit' in args:
        return 'commit', None
    if 'status' in args:
        return 'status', None
    if 'ls_files' in args:
        return 'ls_files', None
    if 'log' in args:
        return 'log', None
    if len(vars(args)) < 1:
        print('fatal: no command was added, add -h to know more')
        sys.exit()


def check_status():
    pass


def add_a_file(file_name):
    # Open and get content from the file
    try:
        fd = os.open(file_name, os.O_RDONLY)
    except PermissionError:
        print('error: open("%s"): Permission denied' % file_name)
        print('error: unable to index file test')
        print('fatal: adding files failed')
        sys.exit()
    except FileNotFoundError:
        print("fatal: pathspec '%s' did not match any files" % file_name)
        sys.exit()
    file_content = os.read(fd, os.stat(file_name).st_size)
    os.close(fd)
    # Get SHA1 hash from the file (before add)
    file_sha1 = hashlib.sha1(file_content).hexdigest()
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
    fd = os.open(os.path.join(objects_path, file_sha1[:2], file_sha1[2:]), \
    os.O_WRONLY)
    os.write(fd, file_content)
    os.close(fd)
    # Write file information to index
    # Get timestamp of file
    timestamp = os.stat(file_name).st_mtime
    time = str(datetime.datetime.fromtimestamp(timestamp))[:19]
    for i in time:
        if not i.isnumeric():
            time = time.replace(i, '')
    # If file was not stage in index, write a new information for file
    # If there're file informations in index, find index of timestamp,
    # first SHA1, second SHA1,... and write new set of those
    with open(index_path, 'r+') as f:
        content = f.read()
        index = None
        init_info = str(time + ' ' + file_sha1 + ' ' + file_sha1 + ' ' + \
        ' ' * 40 + ' ' + file_name + '\n')
        if len(content) == 0:
            f.write(init_info)
        else:
            lines = content.split('\n')
            for line in lines:
                if len(line) == 0:
                    continue
                if file_name == line.split()[-1]:
                    index = content.find(line)
                    break
            if index:
                fd = os.open(index_path, os.O_RDWR)
                os.lseek(fd, index, 0)
                os.write(fd, time.encode())
                os.lseek(fd, index + 15, 0)
                os.write(fd, file_sha1.encode())
                os.lseek(fd, index + 56, 0)
                os.write(fd, file_sha1.encode())
                os.close(fd)
            else:
                f.write(init_info)


def staging_index(file_name):
    pass


def check_and_commit():
    print("I'm comming here!")


def re_init():
    print('Reinitialized existing Git repository in %s'
          % os.path.realpath('.lgit'))
def check_and_init():
    if os.path.exists('.lgit'):
        if os.path.isdir('.lgit'):
            re_init()
        elif os.path.isfile('.lgit'):
            print('fatal: Invalid gitfile format: %s'
                  % os.path.realpath('.lgit'))
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
    # Make .lgit directory
    os.mkdir(lgit_path)
    # Make dirs of .lgit directory
    os.mkdir(objects_path)
    os.mkdir(commits_path)
    os.mkdir(snapshots_path)
    # Make files of .lgit directory
    os.mknod(index_path, mode=0o644)
    os.mknod(config_path, mode=0o644)
    # Write LOGNAME (current user) into config
    fd = os.open(os.path.join(lgit_path, 'config'), os.O_WRONLY)
    log_name = 'LOGNAME=' + os.environ['LOGNAME']
    os.write(fd, log_name.encode())
    os.close(fd)
    # Print initialized success
    print('Initialized empty Git repository in %s' % lgit_path)


def main():
    global lgit_path, objects_path, commits_path, snapshots_path, \
           index_path, config_path

    lgit_path = os.path.realpath('.lgit')
    objects_path = os.path.join(lgit_path, 'objects')
    commits_path = os.path.join(lgit_path, 'commits')
    snapshots_path = os.path.join(lgit_path, 'snapshots')
    index_path = os.path.join(lgit_path, 'index')
    config_path = os.path.join(lgit_path, 'config')

    cmd, file = get_cmd()
    if 'init' in cmd:
        check_and_init()
    if 'status' in cmd:
        check_status()
    if 'commit' in cmd:
        check_and_commit()
    if 'add' in cmd:
        add_a_file(file)


if __name__ == '__main__':
    main()
