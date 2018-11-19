import os
import sys


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
    print(len(file_content))
    if cmd == 'content':
        return file_content
    elif cmd == 'sha1':
        return hashlib.sha1(file_content).hexdigest()
    elif cmd == 'tracked files':
        tracked_files = []
        lines = file_content.decode().split('\n')
        for line in lines:
            if len(line) > 0:
                tracked_files.append(line.split()[-1])
        return tracked_files
    else:
        print('Please add command to lgit_get')
        sys.exit()


# a = []
# for value in lgit_get('../lgit/.lgit/index', 'tracked files'):
#     a.append(value)
# # a = list(lgit_get('test.py', 'content'))
# print('type: ', type(a))
# print('content:\n' + str(a))
