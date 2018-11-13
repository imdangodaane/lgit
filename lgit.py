#!/usr/bin/env python3
import os
import argparse
import hashlib


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

    ls_files_parser = sub_parsers.add_parser('ls_files', help='Show \
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


def check_status():
    pass


def add_a_file(file_name):
    file_path = os.path.realpath(file_name)
    try:
        fd = os.open(file_name, os.O_RDONLY)
    except PermissionError:
        print('error: open("%s"): Permission denied' % file_name)
        print('error: unable to index file test')
        print('fatal: adding files failed')
    except FileNotFoundError:
        print("fatal: pathspec '%s' did not match any files" % file_name)
    file_content = os.read(fd, os.stat(file_name).st_size)
    file_sha1 = hashlib.sha1(file_content).hexdigest()



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
