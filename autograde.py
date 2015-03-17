'''
      Author: Yang Song
      Email: song24@email.sc.edu
      Date: Jan 2014
      Version: 2.0 
'''
import os
import webbrowser
import os.path
import sys
import glob
import fnmatch
import shutil, errno
import stat
import time
import json
import urllib
import datetime
import re

''' generate html file using markup.py module '''
try:
    import markup
except:
    print __doc__
    sys.exit( 1 )
    

def obtainTime():
    user_input = raw_input('Type date yyyy/mm/dd hh:mm  ')
    dt = datetime.datetime.strptime(user_input, "%Y/%m/%d %H:%M" )
    return dt

def getDueTime(section, lab_num):
    ''' section and lab_num must be integer '''
    dt = datetime.datetime(2014, 1, 14, 22, 59) 
    ''' end = datetime.datetime(2014, 4, 28, 22, 59) '''
    if section == 6:
        dt += datetime.timedelta(days=1)
    if section == 10:
        dt += datetime.timedelta(days=2)
    if section == 16:
        dt += datetime.timedelta(days=7)
        
    interval = lab_num
    
    ''' special case : lab 1 is always extended '''
    if lab_num == 1:
        due = dt + datetime.timedelta(weeks=2)
    else:
        due = dt + datetime.timedelta(weeks=interval)
    
    return due

def showFileInfo(filename):
        fp = open(filename)
        fileStats = os.fstat(fp.fileno())
        #fileStats = os.stat(filename)

        fileInfo = {
            'Last Modified' : time.ctime(fileStats[stat.ST_MTIME]),
            'Last Accessed' : time.ctime(fileStats[stat.ST_ATIME]),
            'Creation Time' : time.ctime(fileStats[stat.ST_CTIME])
            }
 
        for infoField, infoValue in fileInfo.items():
            print '         --  ' , infoField, ':' , infoValue
         
        fp.close()

def getSubmissionTime(filename):
    print "last modified time : %s" % time.ctime(os.path.getmtime(filename))
    '''print "created: %s" % time.ctime(os.path.getctime(file))'''
   
    return time.ctime(os.path.getmtime(filename))

def isLateSubmission(sub_time, due):
    sub = datetime.datetime.strptime(sub_time,  "%a %b %d %H:%M:%S %Y")
    '''due = datetime.datetime.strptime(due_time,  "%a %b %d %H:%M:%S %Y")
        due = datetime.dateime(2014, 1, 17, 22, 59)
    '''
    if due < sub:
        print '\n late work '
        return True
    
    return False      

        
def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        else: raise

# trim last newline character in a string variable
def getFolderName(a):
        n = len(a)- 1
        c=a[0]
        for i in range(1,n):
                c = c+a[i]
     
        return c

def showLabFiles(rootdir):
        fileIdx = 0;
        #L = [] # a list holds file name
        for file in os.listdir(rootdir):
                if fnmatch.fnmatch(file, '*.html') or fnmatch.fnmatch(file, '*.css'):
                        #L.append(file)
                        fileIdx +=1
                        print "["+str(fileIdx)+"]  ",
                        print file
                        fullname=rootdir+file
                        #getSubmissionTime(fullname)


def labFileList(uscid):
        # call after lab folder validation
        rootdir = getLabFolder(uscid)
        L = []
        for file in os.listdir(rootdir):
                if fnmatch.fnmatch(file, '*.html') or fnmatch.fnmatch(file, '*.css'):
                        L.append(file)
        return L
        

def getFolderPath(uscid):
        return '\\\\fs.cl.sc.edu\\USERS\\'+getFolderName(uscid)+'\\'

#lab folder validation
def isLabFolder(uscid):
        userfolder = getFolderPath(uscid)
        #for item in glob.glob('\\\\fs.cl.sc.edu\\USERS\\*'):
        for item in glob.glob(userfolder):
                #print item
                if os.path.isdir(item+'All_102Submissions\\'):
                        rootdir = item+"All_102Submissions\\"
                        print "_____________________________"
                        print "\nShow files : " + uscid
                        # only show html and css files
                        showLabFiles(rootdir)
                        return True
                        
        return False

# index file validation
def isIndexFile(uscid):
        userfolder = getFolderPath(uscid)
        for item in glob.glob(userfolder):
                if isLabFolder(uscid):
                        if os.path.isfile(item+'All_102Submissions\\All_Index.html'):
                                return True

        return False

def getLabFolder(uscid):
        labfolder = getFolderPath(uscid)+'All_102Submissions\\'
        return labfolder

def getIndexPage(uscid):
        # call this function after index file validation
        indexPage = getFolderPath(uscid)+'All_102Submissions\\All_Index.html'
        return indexPage
        
def getCmd():
        cmd = raw_input('[0] Stop grading\n[1] Grade in order \n[2] Search user to grade\n\
[3] Copy folder to local drive\n[4] Enter score directly\n[5] Show users id\nSelect : ')
        return cmd

def addComments(report):
    #global report
    comments = raw_input('comments (hit ENTER key to finishing adding comments): ')
    report.addcontent('<p> %s </p>' %comments)


def evaluate(num_errors, is_late, report):
        #global report
        score = 100
        ''' errors must be an integer'''
        report.addcontent('<p><b>File Validation Result : </b>  ')
        if num_errors > 0:
            print 'You have ', num_errors, ' syntax errors.'
            report.addcontent(' You have %d syntax errors ...  ' %num_errors)
            if num_errors > 40:
                print ' -40 '
                report.addcontent(' -40 </p>')
                score -= 40
            else:
                print ' -', num_errors
                report.addcontent(' -%d </p>' %num_errors)
                score -= num_errors
        else:
            report.addcontent(' NO syntax errors </p>')

        ''' is_late must be a bool '''
        report.addcontent('<p><b>Late submission ? </b>  ')
        if is_late:
            print 'Late work -15'
            report.addcontent(' YES. Late penalty ... -15 </p>')
            score -= 15
        else:
            report.addcontent(' NO </p>')
        
        ''' 1. check index image '''
        index_image = raw_input('\nMissing index image?(y/n)')
        report.addcontent('<p><b>Missing index image? </b>  ')
        if index_image == 'y':
            '''generate comment here and update score also'''
            print 'Missing index image on All_Index.html -5'
            report.addcontent(' YES ... -5 </p>')
            score -= 5
        else:
            report.addcontent(' NO </p>')

        ''' 2. check html comments in <head> '''
        html_comment = raw_input('\nMissing comment in <head>?(y/n)')
        report.addcontent('<p><b>Missing comment in &lt;head&gt;?</b>  ')
        if html_comment == 'y':
            print 'Missing html comment tag -5'
            report.addcontent(' YES ... -5 </p>')
            score -= 5
        else:
            report.addcontent(' NO</p>')

            
        ''' 3. check indents '''
        source_indent = raw_input('\nMissing indentations?(y/n)')
        report.addcontent('<p><b>Inproper indentations?</b>  ')
        if source_indent == 'y':
            print 'You need indent your source code -5'
            report.addcontent(' YES ... -5</p>')
            score -= 5
        else:
            report.addcontent(' NO </p>')

        ''' 4. check links '''
        hyper_link = raw_input('\nMissing or invalid lab links?(y/n)')
        report.addcontent('<p><b>Missing or invalid lab links?</b>  ')
        if  hyper_link == 'y':
            print 'Invalid/missing link for lab on All_Index page -5'
            report.addcontent(' YES ... -5 </p>')
            score -= 5
        else:
            report.addcontent(' NO </p>')
            
        ''' 5. check references '''
        no_refer = raw_input('\nMissing references?(y/n)')
        report.addcontent('<p><b>Missing references? </b>  ')
        if no_refer == 'y':
            print 'No reference at all -10'
            report.addcontent(' YES ... -10 </p>')
            score -= 10
        else:
            report.addcontent(' NO </p>')
            bad_refer = raw_input('\nInproper reference format?(y/n)')
            report.addcontent('<p><b>Inproper reference format?</b>  ')
            if bad_refer == 'y':
                print 'Inproper reference format -5'
                report.addcontent(' YES ... -5 </p>')
                score -= 5
            else:
                report.addcontent(' NO </p>')

        ''' 6. Sloppy writing '''
        sloppy_writing = raw_input('\nMissing writings?(y/n)')
        report.addcontent('<p><b>Are all requirements not finished or missing writings?</b>  ')
        if  sloppy_writing == 'y': 
            lost_points = raw_input('Enter points deducted :')
            report.addcontent(' YES ... -%s </p>' %lost_points)
            score -= int(lost_points)
            while True:
                need_comments = raw_input('Want to add more comments? (y/n): ')
                if need_comments == 'n':
                    break
                else:
                    addComments(report)
        else:
            report.addcontent(' NO </p>')

        ''' 7. Extra credits '''
        extra_credit = raw_input('\nExtra Credits for creativity?(y/n)')
        report.addcontent('<p><b>Extra Credits for creativity? </b>  ')
        if extra_credit == 'y':
            print 'Extra credits +10'
            report.addcontent(' YES ... + 10 </p>')
            score += 10
        else:
            report.addcontent(' NO </p>')
           
            
        return score
        
def gradeUserFile(uscid, due_time, section, lab_num):
        
        global out_dir
        report = markup.page()
        report.init(title="Grade Report",
        css="http://www.cse.sc.edu/~song24/reportstyle.css",
        header='<h2 id="banner">Grade Report</h2>',
        footer='<h4 id="footer">By Yang Song &nbsp; song24@email.sc.edu </h4>')
        report.addcontent('<h3> Section '+ section +' -- Lab '+lab_num )
        report.addcontent('Due : %s/%s/%s 22:59:00 </h3>' %(due_time.month, due_time.day, due_time.year))

        final_score = 0
        #if isIndexFile(uscid):
        if isLabFolder(uscid):
                response = raw_input('\nOpen Current index page (y)\nOpen NEXT index page (n)\n\
Select file to grade (Enter file index NO)\nReturn to main menu (r)\nEND grading (e): ')
                L = labFileList(uscid)
                if response == "y":
                        #print " ---- Open Index ---- "
                        webbrowser.open_new_tab(getIndexPage(uscid))
                elif response == "n":
                        print " .... Open Next Index ..."
                elif response == "r":
                        return 0
                elif response == "e":
                        print "GoodBye"
                        sys.exit()                        
                else:
                        # open selected files
                        prefix = getLabFolder(uscid)
                        webbrowser.open_new_tab(prefix+L[int(float(response))-1])
                        
                        report.addcontent('<h3> User ID :  %s </h3>' %uscid[0:(uscid.__len__()-1)])

                        sub_time = getSubmissionTime(prefix+L[int(float(response))-1])
                        is_late = isLateSubmission(sub_time, due_time)
                         
                        str_sub_time = ('<p>Last modified time : %s </p>' %sub_time)
                        report.addcontent(str_sub_time)
                        
                        source = prefix
                        dest = 'tmp'
                        ''' clean tmp folder first '''
                        if os.path.exists(dest):                               
                                print 'tmp folder already exist, clean it now'
                                shutil.rmtree('/tmp')        
                        
                        shutil.copytree(source, dest)
                        print 'finished copying user folder to tmp '
                        html_file = dest+'/'+L[int(float(response))-1]
                        
                        report.addcontent('<p> HTML File Errors </p>')
                        html_errors = get_errors(html_file, report)
                        num_errors = html_errors
                        has_css = raw_input('has external css file ?(y/n)')
                        if has_css == 'y':
                            css_index = raw_input('Enter file index NO.')
                            css_file = dest+L[int(float(css_index))-1]
                            report.addcontent('<p> CSS File Errors </p>')
                            css_errors = get_errors(css_file, report)
                            num_errors += css_errors
                            
                        final_score = evaluate(num_errors, is_late, report)                    
                            
                        print 'Final score is :', final_score
                        report.addcontent('<h3> Final Score : %d </h3>' %final_score)
                        
                        if final_score >= 90:
                            report.img(src="http://www.cse.sc.edu/~song24/like.jpg", alt="like")                      


                        # print uscid, uscid.__len__()
                        id_end = uscid.__len__() - 1
                        out_file = (out_dir +'/'+ uscid[0:id_end]+'_%d.html' %final_score)
                        html_report = open(out_file, 'w')
                        html_report.write(report.__str__())
                        html_report.close()
                        print 'Finished generating grade report for ', uscid
                        
                del L[:]
        else:
                print uscid+" has no valid foler"
                userfolder = getFolderPath(uscid)
                webbrowser.open(userfolder)
                return 0
   
        
        return 1

def searchUser(char, ID, due_time, section, lab_num):                      
        potential_users = []
        charIdx = 0
        for allids in ID:
                if char == allids[0][:1]:
                        potential_users.append(allids)
                        charIdx += 1
                        print "["+str(charIdx)+"]  ",
                        print allids
        target_user_idx = raw_input('Enter User Number: ')
        target_idx = int(float(target_user_idx))
        if target_idx > len(potential_users) or target_idx < 1:
                print "Error: Input number out of range !"
        else:
                new_uscid = potential_users[target_idx - 1]
                gradeUserFile(new_uscid, due_time, section, lab_num)                                    
                                                                        
        del potential_users[:]

def showUsers(ID):
        count = 0
        for uscid in ID:
                count += 1
                print "["+str(count)+"] ", 
                print ID[count-1]  



'''
w3c-validator - Validate HTML and CSS files using the WC3 validators

Copyright: Stuart Rackham (c) 2011
License:   MIT
Email:     srackham@gmail.com

Modified:  Yang Song 
Email:     song24@email.sc.edu
'''

html_validator_url = 'http://validator.w3.org/check'
css_validator_url = 'http://jigsaw.w3.org/css-validator/validator'

verbose_option = False

def message(msg):
    print >> sys.stderr, msg

def verbose(msg):
    if verbose_option:
        message(msg)

def validate(filename):
    '''
    Validate file and return JSON result as dictionary.
    'filename' can be a file name or an HTTP URL.
    Return '' if the validator does not return valid JSON.
    Raise OSError if curl command returns an error status.
    '''
    quoted_filename = urllib.quote(filename)
    if filename.startswith('http://'):
        # Submit URI with GET.
        if filename.endswith('.css'):
            cmd =  ('curl -sG -d uri=%s -d output=json -d warning=0 %s'
                    % (quoted_filename, css_validator_url))
        else:
            cmd =  ('curl -sG -d uri=%s -d output=json %s'
                    % (quoted_filename, html_validator_url))
    else:
        # Upload file as multipart/form-data with POST.
        if filename.endswith('.css'):
            cmd =  ('curl -sF "file=@%s;type=text/css" -F output=json -F warning=0 %s'
                    % (quoted_filename, css_validator_url))
        else:
            cmd = ('curl -sF "uploaded_file=@%s;type=text/html"  -F output=json %s'
                   % (quoted_filename, html_validator_url))
    #verbose(cmd)
    status = os.system(cmd)
    f = os.popen(cmd)
    output = f.read()
    if status != 0:
        raise OSError (status, 'failed: %s' % cmd)
    #verbose(output)
    try:
        result = json.loads(output)
    except ValueError:
        result = ' '
    time.sleep(2)   # Be nice and don't hog the free validator service.
    return result

def get_errors(f, report):
    #global report
    report.addcontent('<ol>')
    errors = 0
    warnings = 0
    message('validating: %s ...' % f)
    result = validate(f)
    if f.endswith('.css'):
        errorcount = result['cssvalidation']['result']['errorcount']
        warningcount = result['cssvalidation']['result']['warningcount']
        errors += errorcount
        warnings += warningcount
        if errorcount > 0:
            message('errors: %d' % errorcount)
        if warningcount > 0:
            message('warnings: %d' % warningcount)
    else:
        #print '**************************************\n', result
        for msg in result['messages']:
            
            if 'lastLine' in msg:
                message('%(type)s: line %(lastLine)d: %(message)s' % msg)
                report.addcontent('<li> %(type)s: line %(lastLine)d: %(message)s </li>' %msg)
            else:
                message('%(type)s: %(message)s' % msg)
                report.addcontent('<li> %(type)s: %(message)s </li>' %msg)
            if msg['type'] == 'error':
                errors += 1
            else:
                warnings += 1

    report.addcontent('</ol>')
    print 'Total Syntax Errors: ', errors
    return errors

''' test function     '''
#get_errors('All_Index.html')

if __name__ == "__main__":
    final_score = 0
    section = raw_input('Enter section number:')
    lab_num = raw_input('Enter lab number:')
    out_dir = ('section%s/lab%s' %(section, lab_num))
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
        
    filename = section+'.txt'
    if os.path.isfile(filename):
            print "Read text file " + filename
    else:
            print "No file "+filename
            sys.exit(0)

##    user_dict = {}  
##    with open(filename, 'r') as f:
##        for line in f:
##            #for word in line.split():
##            # print word
##            user_info = re.search(r'(\S*)\s*(\S*)', line)
##            ''' key is the uscid, value is the last name '''
##            user_dict[user_info.group(2)] = user_info.group(1)
##    f.close()   
##    for key, value in user_dict.items():
##        # returns the dictionary as a list of value pairs
##        print key, value

    ID = []
    count = 0     
    fp = open(filename, 'r')  
    while 1:
            uscid = fp.readline()
            #print uscid,
            if not uscid:
                    break
            # do sth.
            else:
                    count += 1
                    ID.append(uscid)
                    print "["+str(count)+"] ", 
                    print ID[count-1]
                  
    fp.close()
    
    due_time =  getDueTime(int(section), int(lab_num))
    print 'Due time of lab'+lab_num+' , section '+section+' : ', due_time
    time_confirm = raw_input('Due time confirm? (y/n)')
    if time_confirm == 'n':
        due_time = obtainTime()
        print 'Due time redefined as', due_time
   
    
    while True:
            
            print "_____________________________"
            print "         Main Menu           "
            print "_____________________________"
            cmd = int(float(getCmd()))
            '''
            0 : stop script
            1 : grade in order
            2 : select user to grade
            3 : copy user folder to disk
            4 : enter score directly
            5 : show user id list 
            ''' 
            if cmd == 0:
                    break
            elif cmd == 1:
                    for uscid in ID:
                        gradeUserFile(uscid, due_time, section, lab_num)
                        #if gradeUserFile(uscid, due_time, section, lab_num) == 0:
                        #    break
                                               
            elif cmd == 2:
                    char = raw_input('Enter only the first letter of USC ID:' )
                    searchUser(char, ID, due_time, section, lab_num)
            elif cmd == 3:
                    drive = raw_input('Enter Target Path: (eg: H:\\newfolder) : ')
                    ans = raw_input('[1] Copy all users\' folders \n[2] Copy single user foler\n Select:')
                    if ans == "1":
                            for uscid in ID:
                                    src = getFolderPath(uscid)
                                    dst = getFolderName(drive)+getFolderName(uscid)+'\\'
                                    print "copy folder of "+uscid
                                    copyanything(src, dst)
                            print "Finish!"
                    elif ans=="2":
                            showUsers(ID)
                            num = raw_input('Enter user\' number :')
                            src_idx = int(float(num))-1
                            src = getFolderPath(ID[src_idx])
                            dst = getFolderName(drive)+getFolderName(ID[src_idx])+'\\'
                            copyanything(src, dst)
                            print "Finish!"
                    else:
                            print "Invalid input. Bye"
                            #break
            elif cmd == 4:
                    num = raw_input('Enter score directly : ')
                    scores.append(num)
            elif cmd == 5:
                    for i in range(0, len(ID)):
                        print '[%d] %s' %((i+1), ID[i])
                       
            else:
                    print "Invalid input. Byebye!"
                    break

    del ID[:]

##    scores_txt = open(out_dir+'/scores.txt', 'w')
##    for item in scores:
##        scores_txt.write("%s\n" % item)
##
##    scores_txt.close()
        
    print "End of Script ... "



