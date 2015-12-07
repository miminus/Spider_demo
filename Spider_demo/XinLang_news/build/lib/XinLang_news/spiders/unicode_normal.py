#coding=utf-8
import re
def tranun(s):
	l=len(s)
	ss=''
	i=0
	while i<l:
		if s[i]=='\\' and s[i+1]=='u':
			ss=ss+unichr(int(s[i+2:i+6],16))
			i=i+6
		else:
			ss=ss+s[i]
			i=i+1
	return ss
def tran(s):
	l=len(s)
	ss=''
	i=0
	while i<l:
		if s[i]=='\\':
			i=i+1
		else:
			ss=ss+s[i]
			i=i+1
	return ss

def main(path):
	Path='C:\\Users\\MINUS\\Desktop\\all_catch\\'+path
	f=open(Path,'rb')
	a=f.read()
	b=tranun(a)
	c=tran(b)
	pattern=re.compile(r'rnt{0,25}|t{3,25}',re.S)
	d=re.sub(pattern,'',c)
	f.close()
	f=open(Path,'wb')
	f.write(d)
	f.close()
def main_get(content):
	content=tranun(content)
	content=tran(content)
	content=content.replace('>n','>')
	#pattern=re.compile(r'rnt{0,25}|t{2,25}',re.S)
	content=content.replace('&lt;','<')
	content=content.replace('&gt;','>')
	#content=re.sub(pattern,'',content)
	return content
