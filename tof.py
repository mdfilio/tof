#!/usr/bin/python2

# Copyright 2015 Michael Filio.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import subprocess
from time import sleep


# hack for backwards compatibility for pre 2.7 python
# http://stackoverflow.com/questions/4814970/subprocess-check-output-doesnt-seem-to-exist-python-2-6-5
if "check_output" not in dir( subprocess ): # duck punch it in!
    def f(*popenargs, **kwargs):
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise subprocess.CalledProcessError(retcode, cmd)
        return output
    subprocess.check_output = f


#lsof headers
#COMMAND     PID   TID   USER   FD      TYPE             DEVICE  SIZE/OFF      NODE NAME

"""

Bash format

lsof -w -X | \
awk '{ if (NF == 10){ \
           if ($5 ~ "^[0123456789].*$|txt" && $6 == "REG"){ \
                                             print $8 " " $10 \
                                           } \
                    }else if(NF == 9){ \
                             if ($4 ~ "^[0123456789].*$|txt" && $5 == "REG"){ \
                                 print $7 " " $9 \
                             } \
                          } \
                    }'| \
sort -u -k1rn
"""


#humansize borrowed from  
#http://stackoverflow.com/questions/14996453/python-libraries-to-calculate-human-readable-filesize-from-bytes


suffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
def humansize(nbytes):	
    if nbytes == 0: return '0 B'
    i = 0
    while nbytes >= 1024 and i < len(suffixes)-1:
        nbytes /= 1024.
        i += 1
    f = ('%.2f' % nbytes).rstrip('0').rstrip('.')
    return '%7s %s' % (f, suffixes[i])
####### END OF humansize #########


def getlsof():
	direct_output = subprocess.check_output(
	              'lsof -w -X | \
	               awk \'{ if (NF == 10){ \
	                  if ($5 ~ "^[0123456789].*$|txt" && $6 == "REG"){ \
	                      print $8 " " $10 }}else if(NF == 9){ \
	                         if ($4 ~ "^[0123456789].*$|txt" && $5 =="REG"){ \
	                             print $7 " " $9 \
	                         } \
	                      } \
	                  }\'| \
	               sort -u -k1rn',
	               shell=True)

	lines = direct_output.split('\n')
	files = list()

	for line in lines:
		filename = line.split()
		files.append(filename)		
	return files
####### END OF getlsof #########


def topTenFiles():
	print "Top 10 active open files by size: \n"

	ct = 0
	for filename in files:
		if ct < 10:		
			print "%15s %s" % ( humansize(int(filename[0])), filename[1])
			ct += 1
	print '\n'
####### END OF topTenFiles #########			

files = getlsof()

dFiles = {}

for filename in files:
	if len(filename) == 2:
		dFiles[filename[1]] = filename[0]

sleep(30)
files = getlsof()


for filename in files:
	if len(filename) == 2:
		#print filename[1]
		#print dFiles[filename[1]]
		if filename[1] in dFiles:			
			dFiles[filename[1]] = int(filename[0]) - int(dFiles[filename[1]])


deltaFiles = list()

for key, value in dFiles.iteritems():
	temp = [key, int(value)]
	deltaFiles.append(temp)


filteredFiles = filter(lambda x: int(x[1]) > 0, deltaFiles)


topTenFiles()

print "Open growing files (after 30 second interval): \n"

if len(filteredFiles) > 0:
	for filename in filteredFiles:
		if len(filename) > 0:
			print "file size increased %15s %s" % (humansize(int(filename[1])), filename[0])
