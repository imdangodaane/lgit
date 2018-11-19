#!/usr/bin/env python3
import os
import argparse
import time
import datetime
import sys


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
    rm_parser.add_argument('rm')


    config_parser = sub_parsers.add_parser('config', help='Get and set \
    repository or global options')
    config_parser.add_argument('config', action='store_true')
    config_parser.add_argument('--author', help='Author help')

    commit_parser = sub_parsers.add_parser('commit', help='Record changes \
    to the directory')
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


def lgit_rm(file_name):
    # Find file if exist and remove file from staging index
    f = open(index_path, 'r')
    content = f.read()
    f.close()
    file_name_list = []
    lines = content.split('\n')
    for line in lines:
        if len(line) > 0:
            file_name_list.append(line.split()[-1])
    if file_name not in file_name_list:
        print("fatal: pathspec '%s' did not match any files" % file_name)
        sys.exit()
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
    print('Remove file completed')


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
    if 'rm' in cmd:
        lgit_rm(file)


if __name__ == '__main__':
    main()
