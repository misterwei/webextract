from urllib import request
from urllib import parse
from pathlib import Path
import re
import queue
import download

url_root = "https://doc.rust-lang.org/"
url_start = ""

file_path = "E:/rust"

class Extract:
    def __init__(self,root,start):
        self.root = root
        self.start = start
        self.thisurl = root
        self.urls = []
        self.queue = queue.Queue()
        url = parse.urljoin(self.root,self.start)
        self.queue.put(url)
        self.download_task = download.Download(file_path)
        self.download_task.start_down()
        
    #1
    def start_task(self):
        while self.queue.qsize() > 0:
            url = self.queue.get()
            print("queue size %d" % self.queue.qsize())
            #yes = input("start %s ? y/n \n" % url)
            #while len(str(yes).strip()) <= 0:
            #    yes = input("start url? y/n \n")
            #
            #if str(yes).lower()[0] != "y":
            #    break
            try:
                self.read(url)
            except Exception as e:
                print("extract read error")
                print(e)
        print("extract end!")
        pass
    #2
    def read(self,url):
        self.thisurl = url
        r = request.Request(url)
        response = request.urlopen(r)
        #print("headers : %s" % str(response.getheaders()) )
        contentType = response.getheader("Content-Type")
        contentEncoding = response.getheader("Content-Encoding")
        print("%s ContentType:%s,ContentEncoding:%s" % (url,contentType,contentEncoding))
        responselate = response.read().decode("utf-8")
        responselate = self.extract(responselate)
        url_path = parse.urlsplit(url).path
        
        # split filepath and file
        f_path = (file_path + url_path).rpartition("/")[0]
        print("file path : " + f_path)
        fpath = Path(f_path )
        if not fpath.exists():
            fpath.mkdir(parents=True)
        if url_path.endswith("/"):
            url_path = url_path + "index"
        if contentType.startswith("text/"):
            f = open(file_path  + url_path,"w",encoding = "utf-8")
        else:
            f = open(file_path  + url_path,"wb")
        f.write(responselate)
        f.close()
        
    #3
    def extract(self,bodysrc):
        body = bodysrc
        #匹配body
        def match_body(url,replace_tag):
            nonlocal body
            result,replace_url = self.check_url(url)
            if replace_url is not None and replace_url.strip() != "":
                new_tag = replace_tag.replace(url,replace_url)
                print("replace url %s to %s" % (url,replace_url))
                body = body.replace(replace_tag,new_tag)
                return True
            return False
        #a tag
        ataglist = re.findall("<a.*?</a>",body,re.DOTALL)
        atags = set(ataglist)
        for atag in atags:
            #print(atag)
            match = re.search("href=[\"\'](.+?)[\"\']",atag)
            if match:
                url = match.groups()[0]
                if match_body(url,atag):
                    #print(body)
                    pass
        #link tag
        links = re.findall("<link.*?/>",body,re.DOTALL)
        links2 = re.findall("<link.*?</link>",body,re.DOTALL)
        for link in links2:
            links.append(link)
        for link in links:
            match = re.search("href=[\"\'](.+?)[\"\']",link)
            if match:
                url = match.groups()[0]
                match_body(url,link)
        #script tag
        scripts = re.findall("<script.*?/>",body,re.DOTALL)
        scripts2 = re.findall("<script.*?</script>",body,re.DOTALL)
        for script in scripts2:
            scripts.append(script)
        for script in scripts:
            match = re.search("src=[\"\'](.+?)[\"\']",script)
            if match:
                url = match.groups()[0]
                match_body(url,script)
                
        return body
    
    #4
    def check_url(self,src_url):
        if src_url.endswith("#"):
            return (False,None)
        second_result = None
        old_src_url = src_url
        start_with = src_url.startswith("http://") or src_url.startswith("https://")
        if not start_with:
            src_url = parse.urljoin(self.thisurl,src_url)
        sp = parse.urlsplit(src_url)
        if start_with:
            second_result = sp.path
        
        url = sp.scheme + "://" + sp.netloc + sp.path
        if not url.startswith(self.root) :
            #print("not starts with root %s" % url)
            return (False,None)
        if src_url.endswith("#"):
            return (False,None)
        if src_url.endswith("/"):
            if second_result is None:
                second_result = old_src_url + "index"
            else:
                second_result = second_result + "index"
        
        if self.contains(url):
            return (False,second_result)

        if src_url.endswith(".js") or src_url.endswith(".css") or src_url.endswith(".jpg") or src_url.endswith(".gif"):
            self.download(src_url)
            return (True,second_result)
        
        
        self.queue.put(src_url)
        return (True,second_result)
    
    #5
    def download(self,url):
        #print("download url: %s" % url)
        self.download_task.put(url)
        pass
    # contains url and append url
    def contains(self,url):
        cons = url in self.urls
        if not cons:
            self.urls.append(url)
        return cons

if __name__ == "__main__":
    extract = Extract(url_root,url_start)
    extract.start_task()
    
    
    
    
