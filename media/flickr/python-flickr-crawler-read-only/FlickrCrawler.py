'''
Created on Sep 25, 2010

@author: ziliangdotme
'''
import re, urllib2, os, thread, sys
import ThreadingPool


# common utilities
class BasePhotoCrawler(object):
    crawled = set([])
    dirLock = thread.allocate_lock()
    tPool = ThreadingPool.ThreadingPool(24)
        
    @staticmethod
    def fetch(url):
        try: doc = urllib2.urlopen(url).read()
        except Exception: doc = BasePhotoCrawler.fetch(url)
        return doc
        
    @staticmethod
    def getPhotoId(url):
        '''get photo id from a url in the format of /photos/{username}/{id}/'''
        pattern = r'/photos/[^/]+/(\d+)/'
        return re.search(pattern, url).group(1)
    
    @staticmethod    
    def createPath(path):
        subpath = '.';
        BasePhotoCrawler.dirLock.acquire()
        for dir in path.split('/')[:-1]:
            subpath += '/' + dir
            if not os.path.exists(subpath): os.mkdir(subpath)
            if not os.path.isdir(subpath): os.rename(subpath, subpath + '_backup'), os.mkdir(subpath)
        BasePhotoCrawler.dirLock.release()
            
    def downloadImageMT(self, url, path, redownload=True):
        if url in self.crawled and redownload is False: return
        self.crawled.add(url)
        self.tPool.addTask(task=BasePhotoCrawler.downloadImage, args=(), kwargs={'url':url, 'path':path, 'redownload':redownload})

    @staticmethod
    def downloadImage(url, path, redownload):
        '''download image from a image page(not necessarily a .jpg)'''
#        url = kwargs['url']
#        path = kwargs['path']
#        redownload = kwargs['redownload']
        BasePhotoCrawler.createPath(path)
        if os.path.isfile(path) and redownload is False: return
                
        id = BasePhotoCrawler.getPhotoId(url)
        doc = BasePhotoCrawler.fetch(url + 'sizes/')
        pattern = r'<img[^>]+src=\"(http://\w+\.static\.flickr\.com/\w+/{id}\w+\.(jpg|png))[^>]*>'.format(id=id)
        m = re.search(pattern, doc).group(1)
            
        print 'downloading ' + m + ' to ' + path
        img = BasePhotoCrawler.fetch(m)
        open(path, "w+").write(img)
        print 'download complete ' + m
    
    @staticmethod
    def getPhotoLinksFromPage(doc):
        '''get all links to photos within a HTML document'''
        pattern = r'/photos/[^/]+/\d+/'
        return set('http://www.flickr.com' + str for str in re.findall(pattern, doc))
    
    @staticmethod
    def hasNextPage(pageNumber, doc):
        '''Algorithm: check whether there's a <a> tag with src contains 'page' + str(pageNumber + 1) in it'''
        pattern = r'<a[^>]+href=\"[^\"]*page=?{nextPage}[^>]*>'.format(nextPage=pageNumber+1)
        if re.search(pattern, doc) is None: return False
        else: return True
        
    def crawlAPage(self, url, path):
        doc = self.fetch(url)
        for url in self.getPhotoLinksFromPage(doc):
            self.downloadImageMT(url, path.format(id=self.getPhotoId(url)), False)
        return doc
    
    def crawlAllPages(self, url, path):
        for pageNumber in xrange(1, 1024):
            doc = self.crawlAPage(url.format(pageNumber=pageNumber), path)
            if BasePhotoCrawler.hasNextPage(pageNumber, doc) is False: break


# Crawler for page
class UserCrawler(BasePhotoCrawler):

    def  __init__(self, username):
        self.username = username
    
    def getAllSets(self, doc=None):
        '''retrieve all sets in sets page, there might be more than one page, this method did not handle this case.'''
        if doc is None:
            url = r'http://www.flickr.com/photos/{username}/sets/'.format(username=self.username)
            doc = self.fetch(url)
        pattern = r'<a[^>]+href=\"/photos/{username}/sets/(\d+)/[^>]+title=\"(.*?)\"[^>]*>'.format(username=self.username)
        map = {} 
        for match in re.finditer(pattern, doc):
            setId = match.group(1)
            setName = match.group(2)
            map[setId] = setName
            print 'Found set id={setId} name={setName}'.format(setId=setId, setName=setName)
        return map
    
    def crawl(self, crawlSets=True):
        # crawl all sets
        if crawlSets is True:
            map = self.getAllSets()
            for setId, setName in map.iteritems():
                url = r'http://www.flickr.com/photos/{username}/sets/{setId}/page{pageNumber}/'.format(username=self.username, setId=setId, pageNumber='{pageNumber}')
                path = r'User/{username}/{setName}/{id}.jpg'.format(username=self.username, setName=setName, id='{id}')
                self.crawlAllPages(url, path)
                
        # crawl all photos
        url = r'http://www.flickr.com/photos/{username}/page{pageNumber}'.format(username=self.username, pageNumber='{pageNumber}')
        path = r'User/{username}/{id}.jpg'.format(username=self.username, id='{id}')
        self.crawlAllPages(url, path)
        

class TagCrawler(BasePhotoCrawler):
    
    def __init__(self, tag):
        self.tag = tag
            
    def crawl(self):
        url = r'http://www.flickr.com/photos/tags/{tag}/?page={pageNumber}'.format(tag=self.tag, pageNumber='{pageNumber}')
        path = r'Tag/{tag}/{id}.jpg'.format(tag=self.tag, id='{id}')
        self.crawlAllPages(url, path)
            
class SearchResultCrawler():
    
    def __init__(self, keys):
        if type(keys).__name__ is 'str': key = keys
        elif type(keys).__name__ is 'list': key = '+'.join(keys)
        self.key = key
        
    def crawl(self):
        url = r'http://www.flickr.com/search/?q={key}&page={pageNumber}'.format(key=self.key, pageNumber='{pageNumber}')
        path = r'Search/{key}/{id}.jpg'.format(key=self.key.replace('+', ' '), id='{id}')
        self.crawlAllPages(url, path)
    
# main
if __name__ == '__main__':
    ready = False
    if len(sys.argv) >= 2:
        type = sys.argv[1]
    # user    
    if str(type).lower() is 'user':
        if len(sys.argv) >= 3:
            username = sys.argv[2]
            ready = True
            userCrawler = UserCrawler(username)
            userCrawler.crawl(True)
    # tag        
    if str(type).lower() is 'tag':
        if len(sys.argv) >= 3:
            tag = sys.argv[2]
            ready = True
            tagCrawler = TagCrawler(tag)
            tagCrawler.crawl()
    # search        
    if str(type).lower() is 'search':
        if len(sys.argv) >= 3:
            keywords = sys.argv[2:]
            ready = True
            searchResultCrawler = SearchResultCrawler(keywords)
            searchResultCrawler.crawl()

    autoTest = True
    # test
    if not ready and autoTest:
        tagCrawler = TagCrawler('katiewhite')
        tagCrawler.crawl()

    if not autoTest:
        print 'input type of operation'
        cin = sys.stdin