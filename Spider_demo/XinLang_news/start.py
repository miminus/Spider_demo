import os,subprocess,time

os.chdir('D:\Work_space\Java\Spider_demo\XinLang_news')
print os.getcwd()
thread = subprocess.Popen(['python','Run.py'])
time.sleep(60)
thread.kill()