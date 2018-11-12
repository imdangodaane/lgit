#!/usr/bin/env python3
import os


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
    lgit = os.path.realpath('.lgit')
    dir_paths = [
                 os.path.join(lgit, 'objects'),
                 os.path.join(lgit, 'commits'),
                 os.path.join(lgit, 'snapshots')
    ]
    file_paths = [
                  os.path.join(lgit, 'index'),
                  os.path.join(lgit, 'config')
    ]
    # Make .lgit directory
    os.mkdir(lgit)
    # Make dirs of .lgit directory
    for dir in dir_paths:
        os.mkdir(dir)
    # Make files of .lgit directory
    for file in file_paths:
        os.mknod(file, mode=0o644)
    # Write LOGNAME (current user) into config
    fd = os.open(os.path.join(lgit, 'config'), os.O_WRONLY)
    log_name = 'LOGNAME=' + os.environ['LOGNAME']
    os.write(fd, log_name.encode())
    os.close(fd)
    # Print initialized success
    print('Initialized empty Git repository in %s' % lgit)


def main():
    check_and_init()


if __name__ == '__main__':
    main()
