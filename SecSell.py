# -*- coding:utf-8 -*-
 
import urllib.request
import requests
import re
import time
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.header import Header
from email.utils import parseaddr, formataddr
from email.mime.base import MIMEBase

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))

class autoreply:
    def __init__(self):
        self.baseurl1 = "https://api-v2.cc98.org/Board/80/topic?from=" #0&size=20"
        self.baseurl2 = "https://api-v2.cc98.org/Topic/" #4754388/post?from=0&size=10"
        self.baseurl3 = "http://www.cc98.org/topic/"
        self.needs = []
        self.exclu = []
        self.needid = {}
        self.needpage = {}
        self.neednames = {}
        self.needtitle = {}
        self.idcontain = {}
        self.ids = []
        self.msg_from='664019449@qq.com'     #发送方邮箱
        self.passwd= 'ppegojettgowbbea'  #'ppegojettgowbbea'       #填入发送方邮箱的授权码
        self.msg_to='1317890542@qq.com'      #收件人邮箱
        self.subject = ""
        self.mailcont = ""
        self.neednum = 0
        self.findflag = False
        self.SendPic = False
        self.msg = MIMEMultipart('alternative')
        self.loginHeaders =  {
            'Host':'www.cc98.org',
            'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0',
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding':'gzip, deflate',
            'Cookie':'aspsky=username=etwll&usercookies=3&userid=530690&useranony=&userhidden=2&password=a5a0d846600cfaac; BoardList=BoardID=Show; autoplay=True; owaenabled=True; ASPSESSIONIDACQTQBDT=GOELLJLBMPFKGCBJMJHPNLAP; upNum=0',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection' : 'keep-Alive',
            'Upgrade-Insecure-Requests':'1'
        }

        
    def main(self,page=1):
        self.readtxt()
        while True:
            self.getids(page)
            self.chkconts()
            if self.findflag:
                self.sendemail()
                self.idwrite()
                self.findflag = False
                self.reinit()
            print('====================log: Wait!====================')
            time.sleep(50)

    def reinit(self):
        self.needid = {}
        self.needpage = {}
        self.needtitle = {}
        self.idcontain = {}
        self.ids = []
        self.subject = ""
        self.mailcont = ""
        self.neednum = 0
        self.findflag = False
        self.msg = MIMEMultipart('alternative')
        for need in self.needs:
            self.needid[need] = []
            self.needpage[need] = []
            self.needtitle[need] = []


    def idwrite(self):
        for x in self.idcontain:
            self.exclu.append(x)

        if len(self.exclu) >= 20:
            self.exclu = self.exclu[-20:]

        file3 = open("exclude.txt",'w')
        for xx in self.exclu:
            file3.write(xx+'\n')
        file3.close

    def getids(self,pages):
        self.ids = []
        self.titles = []
        for i in range(pages):
            urls = self.baseurl1+str(i*20)+'&size=20'
            topics = self.myweb(urls)
            jh = json.loads(topics)
            for jh2 in jh:
                self.ids.append(jh2['id'])
                self.titles.append(jh2['title'])
        print('====================log: Get CC98 Pages OK!====================')

    def chkconts(self):
        print('====================log: Checking for my needs!====================')
        for sid in self.ids:
            # print('====================log: Checking sid %s!===================='%str(sid))
            if(str(sid) not in self.exclu):
                myurl = self.baseurl2 + str(sid) + "/post?from=0&size=10"
                pcont = self.myweb(myurl)
                for allnames in self.neednames:
                    for myneed in self.neednames[allnames]:
                        # print('====================log: Checking MyNeeds %s, Topic id %s!===================='%(myneed,str(sid)))
                        if(pcont.find(myneed)!=-1):
                            self.needid[allnames].append(str(sid))
                            jh = json.loads(pcont)
                            self.needpage[allnames].append(jh[0]['content'])
                            self.needtitle[allnames].append(jh[0]['title'])
                            self.findflag = True
                            print('====================log: MyNeeds %s Found!===================='%myneed)
        print('====================log: Checking Ended!====================')



    def myweb(self,inurl):
        IFlg = 0
        content = ''
        while IFlg < 5:
            try:
                request = urllib.request.Request(inurl)
                response = urllib.request.urlopen(request,timeout=40)
                content = response.read().decode('utf-8')
                return content
            except:
                print('====================log:My web service go wrong %d times!===================='%IFlg)
                IFlg = IFlg + 1
                pass
        return content

    def readtxt(self):
        file1 = open("need.txt",encoding='utf-8')
        for line in file1:
            words = re.split('[ ;,]',line)
            self.needs.append(words[0].strip())
            for xx in words:
                if xx.strip() != '':
                    if words[0].strip() not in self.neednames:
                        self.neednames[words[0].strip()]=[words[0].strip()]
                    else:
                        self.neednames[words[0].strip()].append(xx.strip())
                
        file1.close
        file2 = open("exclude.txt",encoding='utf-8')
        for line in file2:
            self.exclu.append(line.strip('\n'))
        file2.close
        for need in self.needs:
            self.needid[need] = []
            self.needpage[need] = []
            self.needtitle[need] = []
        print('====================log: Read Inputs OK!====================')

    def sendemail(self):
        print('====================log: Preparing Emails!====================')
        finds = ""
        for x in self.needid:
            if len(self.needid[x]):
                finds = finds + x + ","
        self.subject ="碧莲！碧莲！CC98上出现了"+finds.strip(',')+"!"
        self.editcont()
        msgText = MIMEText(self.mailcont,"html",'utf-8')
        self.msg.attach(msgText)
        self.msg['Subject'] = Header(self.subject,'utf-8').encode()
        self.msg['From'] = _format_addr('玉泉吴彦祖<%s>'%self.msg_from)
        self.msg['To'] = _format_addr('胜利商店王美丽<%s>'%self.msg_to)
        print('====================log: Emails Prepared!====================')
        # print(self.mailcont)
        Iflags = 0
        while Iflags < 5:
            try:
                print('====================log: Emails Sending!====================')
                s = smtplib.SMTP_SSL("smtp.qq.com",465)#("smtp.126.com",465)
                s.login(self.msg_from,self.passwd)
                s.sendmail(self.msg_from, self.msg_to, self.msg.as_string())
                print('====================log: Emails Sent!====================')
                s.quit()
                return 1
            except:
                Iflags = Iflags + 1
                print('====================log: Send Failed: %d try!===================='%Iflags)
                time.sleep(600)
        print("Something wrong!")
        return 1
        

    def editcont(self):
        for x in self.needid:
            needlen = len(self.needid[x])
            if needlen:
                self.neednum = self.neednum + 1
                self.mailcont = self.mailcont + self.oneneedcont(x,self.neednum,needlen)

    def oneneedcont(self,nname,num,nlen):
        ctitle = '<div style="text-align: center;"><b><font size="5">'+str(num)+'. '+nname+'</font></b></div>'
        for i in range(nlen):
            sbti = '<div style="text-align: center;"><span style="color: rgb(255, 0, 0); font-weight: bold;"><font size="3">'
            sbti = sbti + '('+str(num)+'.'+str(i+1)+') '+ '<< '+self.needtitle[nname][i]+' >> </font></span></div>'
            sbti = sbti + '<div style="text-align: center;"><span style="color: rgb(255, 0, 0); font-weight: bold;"> \
                        <font size="3"> 链接: '+self.baseurl3+str(self.needid[nname][i])+'</font></span></div>'
            ctitle = ctitle + sbti + self.formatcont(nname,i,num)+'<p> </p>'
        return ctitle


    def formatcont(self,nname,ii,num):
        incont = self.needpage[nname][ii]
        iid = str(self.needid[nname][ii])
        if iid not in self.idcontain:
            self.idcontain[iid] = str(num)+'.'+ str(ii+1)
            ctsplit = incont.split('\n')
            retcont = ''
            for cont in ctsplit:
                if(cont.find('[img]')!=-1 and self.SendPic):
                    retcont = retcont + self.parsefig(cont,iid)
                else:
                    retcont = retcont + '<div>' + cont + '</div>'
        else:
            retcont = '<div> 参见：'+self.idcontain[iid]+'。</div>' 
        return retcont

    def parsefig(self,labels,iid):
        aa = labels.split('[img]')[-1]
        iurl = aa.split('[/img]')[0]
        picname = iurl.split('/')[-1]
        imname =str(iid)+'_'+ str(picname.split('.')[0])
        self.getfig(iurl,imname)
        imcont = '<div><img src="cid:'+imname+'" modifysize="30%" scalingmode="zoom" style="width: 360px;"></div>'
        # print(imcont)
        return imcont


    def getfig(self,ffurl,imname):
        print('====================log: Downloading pics!====================')
        # picsize = int(requests.head(furl).headers.get('content-length'))
        try:
            # print(ffurl)
            request = urllib.request.Request(ffurl)
            response = urllib.request.urlopen(request,timeout=1000)
            # for i in range(100):
            #   c = response.read()
            #   if(len(c)==picsize):
            #       pass
            #   else:
            #       time.sleep(0.1)
            picts = response.read()
            msgImage = MIMEImage(picts)
            msgImage.add_header('Content-ID', imname)
            msgImage.add_header('Content-Disposition', 'attachment')
            msgImage.add_header('X-Attachment-Id', '0')
            self.msg.attach(msgImage)
        except:
            pass

instance = autoreply()
instance.main()
