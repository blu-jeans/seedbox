#!/usr/bin/python
# -*- coding: utf-8 -*- 
# Before using, install use the following command
# python -m pip install chardet
import os,re,sys,time,datetime
import subprocess,shlex
import math,random
import unicodedata
import chardet

reload(sys)
clear = lambda: os.system('cls' if os.name=='nt' else 'clear')
#sys.stdin=open('in.txt','r')

local_server = "127.0.0.1:58846"
path = "/root/autoseed"
log = open("/root/autoseed/log2.txt", 'a')
#trigger_list = ['landof.tv']
#loop_interval = 60 # detect every 60 seconds


torrent_id = ''
name = ''

def write_log(s, log=log):
    timestamp = datetime.datetime.today().strftime('%Y%m%d_%H%M%S')
    log.write('%s '%timestamp)
    log.write('%s: '%torrent_id)
    log.write(s + '\n')
    log.flush()
    pass

def getidname():
    global torrent_id,name
    write_log("sys.argv len: %d"%len(sys.argv))
    write_log("sys.argv: {}".format(sys.argv))
    # for i in range(len(sys.argv)):
    #     print('%d: %s'%(i, sys.argv[i]))
    torrent_id = sys.argv[1]
    name = sys.argv[2]
    the_encoding = chardet.detect(name)['encoding']
    print(the_encoding)
    write_log(the_encoding)
    write_log(torrent_id)
    write_log(name)
    write_log(path)
    print('Torrent name: %s'%name)
    return torrent_id,name

def execute(cmd):
    # os.system(cmd)
    output = subprocess.check_output(cmd, shell=True)
    # output = unicodedata.normalize('NFC', output.decode('utf-8'))
    # print(output)
    # write_log(output)
    return output

def info():
    write_log('Fetching info...')
    cmd = '/usr/bin/deluge-console "connect %s ; info"'%local_server
    print(cmd)
    l = execute(cmd)
    return l

def resume(torrent_id):
    cmd = '/usr/bin/deluge-console "connect %s ; resume %s"'%(local_server, torrent_id)
    print(cmd)
    execute(cmd)
    pass

def pause(torrent_id):
    cmd = '/usr/bin/deluge-console "connect %s ; pause %s"'%(local_server, torrent_id)
    print(cmd)
    execute(cmd)
    pass

def recheck(torrent_id):
    cmd = '/usr/bin/deluge-console "connect %s ; recheck %s"'%(local_server, torrent_id)
    print(cmd)
    execute(cmd)
    pass

def getflagfromflag(flag1, flag2, s):
    lft = s.find(flag1)
    lft = s.find(flag2, lft)
    rt = s.find('\n', lft)
    ret = s[lft:rt].strip()
    return ret

def check_statue(torrent_id, s):
    if torrent_id not in s:
        return ''
    statue = getflagfromflag(torrent_id, 'State', s)
    return statue

def getidbyname(name, s):
    if s.find(name) == -1:
        return []
    lft = s.find(name)
    lft = s.find('ID:', lft) + 4
    rt = s.find('\n', lft)
    id = s[lft:rt].strip()
    return [id] + getidbyname(name, s[rt:])
    pass


def triger(hashid, s):
    write_log('Trigger test...')
    if s.find(hashid) == -1:
        write_log('This torrent_id does not exit in deluge.')
        return False
    lft = s.find(hashid)
    lft = s.find('Tracker', lft)
    rt = s.find('\n', lft)
    tracker = s[lft:rt]
    write_log('trigger_list: {}'.format(trigger_list))
    write_log('%s' % tracker)
    if not all( i not in tracker for i in trigger_list ):
        return True
    return False

def check_seeding(l, s):
    ret = []
    for i in l:
        if 'Seeding' in check_statue(i,s):
            ret.append(i)
    return ret


def main():
    write_log('Running start...')
    os.chdir(path)
    finid, name = getidname()
    s = info()
#   if not triger(finid, s):
#        write_log('The torrent is not in the trigger list. Exit.')
#       return

    l = getidbyname(name, s)
    seeding_list = check_seeding(l, s)
    if len(seeding_list) == 0:
        write_log('No same name torrent seeding. Exit.')
        return
    else:
        write_log('Found %d same name torrents. %d Seeding. '%(len(l), len(seeding_list)) )
        for i in l:
            if 'Paused' in check_statue(i, s):
                write_log('Start torrent %s'%i)
                recheck(i)
                resume(i)

    # num = 0
    # while len(l)<=1:
    #     l = getidbyname(name, s)
    #     if len(l) <= 1:
    #         num += 1
    #         write_log('loop for the %dst time'%num)
    #         time.sleep(loop_interval)
    #     else:
    #         break
    # print(l)
    # for i in l:
    #     recheck(i)
    #     resume(i)
    write_log('Running finished.')
    pass

if __name__ == '__main__':
    main()
    
