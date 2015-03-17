import re
import os
import webbrowser
import os.path
import sys
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email import Encoders

def get_user_dict(section):
    filename = 'dict'+section+'.txt'
    if os.path.isfile(filename):
        print "Read text file " + filename
    else:
        print "No file "+filename
        sys.exit(0)

    my_dict = {}
    with open(filename, 'r') as f:
        for line in f:
            #for word in line.split():
            # print word
            user_info = re.search(r'(\S*)\s*(\S*)', line)
            ''' key is the uscid, value is the last name '''
            my_dict[user_info.group(2)] = user_info.group(1)
    f.close()

##    for key, value in user_dict.items(): # returns the dictionary as a list of value pairs
##        print key, value

    return my_dict



def mail(to, subject, text, attach):
   msg = MIMEMultipart()

   msg['From'] = gmail_user
   msg['To'] = to
   msg['Subject'] = subject

   msg.attach(MIMEText(text))

   part = MIMEBase('application', 'octet-stream')
   part.set_payload(open(attach, 'rb').read())
   Encoders.encode_base64(part)
   part.add_header('Content-Disposition',
           'attachment; filename="%s"' % os.path.basename(attach))
   msg.attach(part)

   mailServer = smtplib.SMTP("smtp.gmail.com", 587)
   mailServer.ehlo()
   mailServer.starttls()
   mailServer.ehlo()
   mailServer.login(gmail_user, gmail_pwd)
   mailServer.sendmail(gmail_user, to, msg.as_string())
   # Should be mailServer.quit(), but that crashes...
   mailServer.close()



gmail_user = "ysong.sc@gmail.com"
gmail_pwd = "W_0i0n0d"

section = raw_input('Enter Section number : ')
lab_num = raw_input('Enter Lab number: ')

dirname = 'section'+section+'/lab'+lab_num
user_group = get_user_dict(section)
email_subject = 'CSCE102 Grade Report Lab' +lab_num


for filename in os.listdir(dirname):
    root, ext = os.path.splitext(filename)
    if ext == '.html':
        ''' find user id , re.match checks for a match at the beginning of the str'''
        u = re.match(r"\w+_", root)
        v = re.match(r"[^_]*", u.group())
        user_id = v.group()
        user_name = user_group[user_id]
        user_email = user_id+'@email.sc.edu'
        html_report = dirname+'/'+filename
        mail(user_email,
           email_subject,
           'Hello Mr./Ms. '+user_name+',\n please find the grade report attached. Let me know if you have any question.\n Yours\n Yang Song',
           html_report)
        print 'email sent to ' + user_email

print 'All emails sent!'
