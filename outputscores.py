import re
import os
import webbrowser
import os.path
import sys

def get_userid_score(dirname):
    ''' dictionary key is user id, value is lab score '''
    mydict ={}
    for filename in os.listdir(dirname):
        root, ext = os.path.splitext(filename)
        if ext == '.html':
            ''' find user id , re.match checks for a match at the beginning of the str'''
            #u = re.match(r"\w+_", root)
            #v = re.match(r"[^_]*", u.group())
            v = re.match(r'[a-zA-Z0-9]+', root)
            #print v.group()
            key = v.group().rstrip('\n') #remove \n at end of line if there is any
            ''' find the score after _ '''
            m =  re.search(r"_\d+", root)
            n = re.search(r"\d+", m.group())
            #print n.group()
            value = n.group().rstrip('\n')
            mydict[key] = value    

    return mydict


def get_id_array(filename):
    if os.path.isfile(filename):
        print "Read text file " + filename
    else:
        print "No file "+filename
        sys.exit(0)
        
    fp = open(filename, "r" )
    id_array = []
    for line in fp:
        id_array.append( line.rstrip('\n') )
        fp.close()

    return id_array

section = raw_input('Enter Section number : ')
lab_num = raw_input('Enter Lab number: ')

dirname = 'section'+section+'/lab'+lab_num
dict_uid_score = get_userid_score(dirname)
'''
for key,value in dict_uid_score.items():
        print(key, ":", value)
'''
filename = section+'.txt'
array_uid = get_id_array(filename)
array_score = []

for each_id in array_uid:
    if dict_uid_score.get(each_id):
        array_score.append(dict_uid_score[each_id])
    else:
        array_score.append(0)

for each_score in array_score:
    print each_score
    



    
