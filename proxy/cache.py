# -*- coding:utf-8 -*-
import os
import time
import requests


class Cache(object):

    def __init__(self, url):
        self.url = url
        self.name = url[:50].replace('/', '%')

        self.__check_exist_cache_dir()

    def is_cache_exist(self):
        '''
        检测缓存是否存在
        '''
        if os.path.exists('./cache/' + self.name):
            return self.check_cache()

        else:
            with open('./cache/' + self.name, 'w') as f:
                return False

    def check_cache(self):
        '''
        向远程发送请求检查缓存是否可用
        '''
        file_time = os.stat('./cache/' + self.name).st_mtime
        # 将文件最终修改时间转化为GMT格式的时间
        headers = {'If-Modified-Since': time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(file_time))}
        if requests.get(self.url, headers=headers).status_code == 304:
            return True
        else:
            with open('./cache/' + self.name, 'w') as f:
                return False

    def update_cache(self, data):
        '''
        进行缓存
        '''
        with open('./cache/' + self.name, 'a') as f:
            f.write(data)

    def __check_exist_cache_dir(self):
        '''
        创建缓存目录
        '''
        if not os.path.exists('./cache'):
            os.mkdir('./cache')

if __name__ == '__main__':
    pass
