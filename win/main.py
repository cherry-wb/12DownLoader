# coding=gbk
import os, urllib, urllib2, urlparse, HTMLParser
#���ع���
        #���´�����ԣ�http://www.cnpythoner.com/post/pythonurldown.html
def url2name(url):
    return os.path.basename(urlparse.urlsplit(url)[2])

def reporthook(count,block_size,total_size):
    print '\x0D','�����أ�'+'%d MB' % int(count*block_size/(1024.0*1024.0)),#'%02.1f%%' % (100*count*block_size/total_size),
      
def download(url, destDir = None, localFileName = None):
    localName = url2name(url)
    req = urllib2.Request(url)
    r = urllib2.urlopen(req)
    if r.info().has_key('Content-Disposition'):
        # If the response has Content-Disposition, we take file name from it
        localName = r.info()['Content-Disposition'].split('filename=')[1]
        if localName[0] == '"' or localName[0] == "'":
            localName = localName[1:-1]
    elif r.url != url:
        # if we were redirected, the real file name we take from the final URL
        localName = url2name(r.url)
    localName = urllib2.unquote(localName)
    if localFileName:
        # we can force to save the file as specified name
        localName = localFileName
    elif destDir:
        localName = destDir + localName
    urllib.urlretrieve(r.url,localName.decode('utf-8').encode('gbk'),reporthook)
    print ''
    
class My12Parser(HTMLParser.HTMLParser):
    def __init__(self):
        self.downloadList = []
        self.nameList = []
        HTMLParser.HTMLParser.__init__(self)
        
    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            isDownloadLink = False
            for name,value in attrs:
                if name == 'class' and value == 'download_link':
                    isDownloadLink = True
                    break
            if isDownloadLink:
                for name,value in attrs:
                    if name == 'href':
                        self.downloadList.append(str(value))
                    if name == 'title':
                        self.nameList.append(str(value))
                        
    def get_downloadlist(self):
        return self.downloadList

    def get_namelist(self):
        return self.nameList
#End

#��������
def search(key):
    '���ݴ���Ĳ���key��12club�Ͻ�������'
    url12 = r'http://12club.nankai.edu.cn'
    urlreq = urllib.urlopen(url12)
    sc = urlreq.read()
    sc = sc[sc.find('authenticity_token')+5:]
    sc = sc[sc.find('authenticity_token'):]
    sc = sc[sc.find(r'value="'):]
    sc = sc[sc.find(r'"')+1:]
    token = sc[:sc.find(r'"')]
    params = {
        'utf8':'?',
        'authenticity_token':token,
        'keyword':key
        }
    params = urllib.urlencode(params)
    r = urllib.urlopen(url12+r'/search', params)
    sc = r.read()
    return sc

class SearchParser(HTMLParser.HTMLParser):
    '���������parser'
    def __init__(self):
        self.linkList = []
        self.nameList = []
        self.isTag = False
        self.tags = []
        self.taglist = []
        HTMLParser.HTMLParser.__init__(self)

    def handle_starttag(self, tag, attrs):
        if tag == 'a' :
            names = [name for name, value in attrs]
            values = [value for name, value in attrs]
            if 'href' in names and 'class' not in names and r'/programs/' in values[names.index('href')]:
                self.linkList.append(values[names.index('href')])
                self.nameList.append(values[names.index('title')])
        elif tag == 'div' and [('class', 'tag_list')] == attrs:
            self.isTag = True
            
    def handle_data(self,data):
        if self.isTag and data.strip():
            self.tags.append(data)
            
    def handle_endtag(self,tag):
        if tag == 'div' and self.isTag:
            self.isTag = False
            self.taglist.append(self.tags)
            self.tags = []

    def get_linklist(self):
        return self.linkList

    def get_namelist(self):
        return self.nameList
    
    def get_taglist(self):
        return self.taglist

def showSearchResult(codes):
    '��ʾ��������������û�ѡ����Ҫ�����ؽ��'
    parser = SearchParser()
    parser.feed(codes)
    links = parser.get_linklist()
    names = parser.get_namelist()
    tags = parser.get_taglist()
    parser.close()
    if names:
        i = 0
        print '�������������ʾ:'
        for name in names:
            i += 1
            print i,'. ',name
            print '��ǩ��',','.join(tags[i-1][1:]), '\n'
        i = int(raw_input('������ѡ��������һ��(�������Ӧ���):'))
        return links[i-1]
    else:
        print 'û�����������,��������������ؼ���!'
#��������End

if __name__ == '__main__':
    addr = 'http://12club.nankai.edu.cn'
    print '��ӭ����12���������������ʾ���������������أ�����������ʾ�����߸Ų�����'
    
    while True:
        choose = raw_input('�����������¹��ܣ�\n1.����������ĳ��������ȫ��\n2.���ݶ���id���ظö�������ȫ��\n��������ѡ��Ĺ��ܣ�')
        if choose == '1':
            while True:
                key = raw_input('�����������ѯ�Ĺؼ��ʣ�')
                searchResult = search(key.decode('gbk').encode('utf-8'))
                searchResult = searchResult.decode('utf-8').encode('gbk')
                url = showSearchResult(searchResult)
                if url:
                    break
            break
        elif choose == '2':
            cartoonid = raw_input("�������صĶ�����ID(�ڶ�Ӧҳ��ĵ�ַ��������ң�Ϊ�������֣�ע�������ˣ����������д�Ŷ~)��")
            url = addr+'/programs/'+cartoonid
            break
        else:
            print r'������д��������������ɣ�'

    while True:
        yesorno = raw_input("Ҫ�Ѷ������ص���ǰ�ļ�����ô�����ص���ǰ�ļ�������y���س������ص������ļ���������n���س���")
        if yesorno == 'y':
            dest_dir = None
            break
        elif yesorno == 'n':
            while True:
                dest_dir = raw_input("��������Ѷ������ص�����(���ļ�����·������Ŀ¼�����ڣ����½�)��")
                if not os.path.isdir(dest_dir):
                    try:
                        print '��ʾ��Ŀ¼�����ڣ��������½�...',
                        os.makedirs(dest_dir)
                        print '�½��ɹ���'
                        break
                    except:
                        print '�����½���ʱ�����˴����п�����Ϊ������Ŀ¼�����⣬��������ɣ�',
                        continue
                else:
                    break
            break
        else:
            print r"��λ��ʿ����������y��n����Ҫ����ʲô�������ŵ��˼���������~����������������again��",

    sourcecode = urllib2.urlopen(url).read()
    parser = My12Parser()
    parser.feed(sourcecode)
    downlist = parser.get_downloadlist()
    namelist = parser.get_namelist()
    i=1
    for downlink in downlist:
        print '��ʼ����' , namelist[i-1].decode('utf-8').encode('gbk') , '�����Եȣ��벻Ҫ�˳����򣬷����������صĶ�������Ч��������ɽ���ʾ......'
        if dest_dir:
            download('http://12club.nankai.edu.cn'+downlink,dest_dir)
        else:
            download('http://12club.nankai.edu.cn'+downlink)
        print namelist[i-1].decode('utf-8').encode('gbk'), '������ϣ�'
        i += 1
    raw_input('������ɣ��밴�»س��رճ���')