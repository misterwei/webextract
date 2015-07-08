import threading
import queue
from urllib import request
from urllib import parse
from pathlib import Path

def download_task(obj):
    print("download task started")
    obj.download()
    pass

class Download:
    def __init__(self,basepath):
        self.queue = queue.Queue()
        self.basepath = basepath
        self.running = True
        pass
    def put(self,url):
        self.queue.put(url)
    def start_down(self):
        self.thread = threading.Thread(target=download_task,args=(self,))
        self.thread.start()
        pass
    def stop_down(self):
        self.running = False
    #download task
    def download(self):
        while self.running:
            url = ""
            try:
                url = self.queue.get(10)
            except:
                continue
            
            print("download " + url)
            path = self.basepath + parse.urlsplit(url).path
            fpath = path.rpartition("/")[0]
            fpath = Path(fpath)
            if not fpath.exists():
                fpath.mkdir(parents=True)
            try:
                r = request.Request(url)
                response = request.urlopen(r)
                bys = response.read()
                print("read bytes size: %d ,will write to %s" % (len(bys),path))
                f = open(path,"wb")
                f.write(bys)
                f.close()
            except:
                print("file write failed")
                
if __name__ == "__main__":
    down = Download("E:/pythondoc")
    down.put("https://docs.python.org/3/_static/jquery.js")
    down.start_down()
    input()
