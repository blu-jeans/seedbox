#!/usr/bin/python
# -*- coding: utf-8 -*- 
# Before using, install the dependence using the following command
# python -m pip install chardet
import os,re,sys,time,datetime
import subprocess,shlex
import math,random
import unicodedata
import chardet

reload(sys)
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')
#sys.stdin=open('in.txt','r')


def execute(cmd):
    # os.system(cmd)
    output = subprocess.check_output(cmd, shell=True)
    # output = unicodedata.normalize('NFC', output.decode('utf-8'))
    # print(output)
    # write_log(output)
    return output


whoami = execute('whoami').strip()
session_path = '/home/%s/rtorrent/.session'%whoami
download_path = '/home/%s/rtorrent/download'%whoami #Essential
print('session_path: %s'%session_path)
print('download_path: %s'%download_path)

os.chdir(session_path)

execute('mkdir -p %s'%os.path.join(session_path,'log'))
log = open("%s"%os.path.join(session_path,'log','log.txt'), 'a')



torrent_id = ''
name = ''


def write_log(s, log=log):
    print(log)
    timestamp = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
    log.write('%s '%timestamp)
    log.write('%s: '%torrent_id)
    log.write(s + '\n')
    log.flush()
    pass

def getidname():
    global torrent_id,name
    print("sys.argv len: %d"%len(sys.argv))
    write_log("sys.argv: {}".format(sys.argv))
    for i in range(len(sys.argv)):
        print('%d: %s'%(i, sys.argv[i]))
    name = sys.argv[1]
    torrent_id = sys.argv[2]
    the_encoding = chardet.detect(name)['encoding']
    write_log(the_encoding)
    write_log(torrent_id)
    write_log(name)
    print('Torrent name: %s'%name)
    return torrent_id,name


# def get_info():
#     # cmd = 'lstor -qo info.name,__hash__ *.torrent'
#     # lstor -qo info.name *.torrent
#     # print(cmd)
#     try:
#         write_log('get_info... execute: lstor -qo info.name *.torrent')
#         # execute('lstor -qo info.name,__hash__ *.torrent').strip().split('\n')
#         names = execute('lstor -qo info.name *.torrent').strip().split('\n')
#         write_log('finish')
#         write_log('get_info... execute: lstor -qo __hash__ *.torrent')
#         hashs = execute('lstor -qo __hash__ *.torrent').strip().split('\n')
#         write_log('finish')
#     except Exception as e:
#         write_log(e.text)
#         write_log('Error, exit.')
#         return
#         raise e
    
#     # sources = execute('lstor -qo info.source *.torrent').strip().split('\n')
#     torrents_info = zip(names, hashs)
#     write_log('Success')
#     return torrents_info


def get_info():
    ret = []
    files = execute("ls -1 | grep -E '\.torrent$'").strip().split('\n')
    for file in files:
        name = execute("/usr/bin/transmission-show %s | grep -E ^Name:"%file).strip()[6:]
        # hx = execute("/usr/bin/transmission-show 042B8D42A5079F5E2D3BB5004B63EA0174162AC2.torrent | grep -E Hash:").strip().split()[1]
        hx = file.strip().split('.')[0]
        ret.append((name,hx))
    return ret


def add_recovery(torrent_id, torrent_folder):
    write_log('%s add_recovery...'%torrent_id)
    path = os.path.join(download_path, torrent_folder)
    cmd = '/home/tobox/bin/chtor %s.torrent --hashed=\'%s\''%(torrent_id, path)
    print(cmd)
    r = execute(cmd)
    write_log(r)
    write_log('Success')
    pass

def getidbyname(name, torrents_info):
    write_log('getidbyname... %s'%name)
    ret = []
    for nm,hx in torrents_info:
        if name == nm:
            ret.append(hx)
    return ret

def save_torrent(torrent_id):
    write_log('%s save_torrent...'%torrent_id)
    cmd = 'cp %s.torrent %s.torrent.bk'%(torrent_id,torrent_id)
    r = execute(cmd).strip()
    write_log('Success')
    print(r)

def del_task(torrent_id):
    write_log('%s del_task...'%torrent_id)
    cmd = '/home/tobox/bin/rtxmlrpc d.erase %s'%torrent_id
    r = execute(cmd).strip()
    write_log('Success')
    print(r)

def re_add_start(torrent_id):
    write_log('%s re_add_start...'%torrent_id)
    cmd1 = 'mv %s.torrent.bk %s.torrent'%(torrent_id,torrent_id)
    torrent_path = os.path.join(session_path, '%s.torrent'%torrent_id)
    cmd2 = 'cp %s /home/tobox2/rtorrent/watch'%torrent_path 
    write_log(execute(cmd1))
    write_log(execute(cmd2))
    write_log('Success')


def check_statue(torrent_id):
    write_log('check status for %s...'%torrent_id)
    cmd = '/home/tobox/bin/rtxmlrpc d.connection_current %s'%torrent_id
    ret = execute(cmd).strip()
    write_log('finished, %s'%ret)
    return ret

# def triger(hashid):
#     # The torrent just finished exists from trigger lsit.
#     tracker = ''
#     for _,hx,source in torrents_info:
#         if hx == hashid:
#             tracker = source
#             break
#     if not all( tracker not in i for i in trigger_list ):
#         return True
#     return False


def main():
    write_log('Running start...')
    write_log('Current path: %s'%os.path.abspath('.'))
    finid, name = getidname()
    torrents_info = get_info()
    write_log('Found %d torrents in your session.'%len(torrents_info))

    if (name, finid.upper()) not in torrents_info:
        write_log('Not find this torrent. Added forcibly.')
        torrents_info.append((name, finid.upper()))
    else:
        write_log('Already found this torrent in session.')
    # write_log(str(torrents_info))

    # if not triger(finid):
    #     write_log('The torrent finished %s %s is not from trigger list'%(finid, name))
    #     return

    l = getidbyname(name, torrents_info)
    write_log(str(l))
    if len(l) <= 1:
        write_log('No other same name torrent. Exit. (%d)'%len(l))
        # check_statue(l[0][1])
        return
    else:
        write_log('Found %d same name torrent. '%len(l))
        hash_status = [(i,check_statue(i)) for i in l]
        write_log('hash status: {}'.format(hash_status))
        if 'seed' not in [j for i,j in hash_status]:
            print('All torrents in leetch status, exit.')
            return
        for hx,status in hash_status:
            if 'seed' not in status:
                write_log('Start torrent %s'%hx)
                add_recovery(hx, name)
                save_torrent(hx)
#                del_task(hx)
                re_add_start(hx)

    write_log('Running finished.')
    pass

if __name__ == '__main__':
    main()
    pass
    