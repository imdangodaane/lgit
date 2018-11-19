#!/usr/bin/env python3
import os
import argparse
import time
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


def commit_update_index():
    f = open(index_path, 'r+')
    content = f.read()
    f.close()
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
    author_name = os.environ["LOGNAME"]
    commit_update_index()
    commit_name = os.path.join(commits_path, timestamp)
    snap_name = os.path.join(snapshots_path, timestamp)
    os.mknod(commit_name, mode=0o644)
    os.mknod(snap_name, mode=0o644)
    f = open(commit_name, 'r+')
    f.write(author_name + '\n' + timestamp[:14] + '\n\n' + message + '\n\n')
    f.close()
    f = open(index_path, 'r+')
    content = f.read()
    f.close()
    lines = content.split('\n')
    f = open(snap_name, 'r+')
    for line in lines:
        if len(line) > 0:
            info = line[delta_3rd_sha1:]
            f.write(info + '\n')
    f.close()



def main():
    global lgit_path, objects_path, commits_path, snapshots_path, \
           index_path, config_path, delta_timestamp, delta_1st_sha1, \
           delta_2nd_sha1, delta_3rd_sha1

    lgit_path = os.path.realpath('.lgit')
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


if __name__ == '__main__':
    main()
