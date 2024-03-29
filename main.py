#!/usr/bin/env python3

from bs4 import BeautifulSoup
from pathlib import Path
from enum import Enum
import json
import shutil
import subprocess
import argparse
import os
import sys
import time
import kwparser

#class Posting(Enum)
Posting = Enum('Posting', 'jobbank indeed linkedin unknown')

parser = argparse.ArgumentParser()
parser.add_argument('htm')
#parser.add_argument('keywords', help='list of keywords separated by comma. Single bar | is used to separate keywords of same meaning. e.g. skills/certs')
parser.add_argument('keywords', help='list of keywords separated by comma. e.g. skills/certs')
parser.add_argument('-s', '--skip-parsing', help='Skip html posting details parsing, this is usually used when website is not common job board', action='store_true')
nmsce: argparse.Namespace = parser.parse_args()
htm_file: str = nmsce.htm
keywords: str = nmsce.keywords
skip_parsing: bool = nmsce.skip_parsing

kws: list[str] = keywords.split(',')
kws = [the_kw.strip() for the_kw in kws if the_kw.strip()]

txtdesc = htm_file+'.excerpt.txt'
kwlst = htm_file+'.keywords.txt'
if skip_parsing:
 kwparser.kwparse(kws, txtdesc, kwlst)
 sys.exit(0)

ptype: Posting = Posting.unknown

tdir = os.path.dirname(htm_file)
htm = Path(htm_file).read_text()

postingsrc: str = 'internet'

if htm.count('Job Bank') > 3:
 ptype = Posting.jobbank
 postingsrc = 'Job Bank'
if htm.count('indeed.com') > 5:
 if ptype != Posting.unknown:
  raise Exception('site detection failure')
 ptype = Posting.indeed
 postingsrc = 'Indeed.com'
if htm.count('linkedin.com') > 5:
 if ptype != Posting.unknown:
  raise Exception('site detection failure')
 ptype = Posting.linkedin
 postingsrc = 'LinkedIn.com'

title: str
company: str
recruiter: str = 'Recruiter'
result_html: bytes

if ptype == Posting.unknown:
 raise Exception('Not a common job board')
elif ptype == Posting.jobbank:
 soup = BeautifulSoup(htm, 'html.parser')
 #wb_auto_2 = soup.find('div', {'id': 'wb-auto-2'})
 #if wb_auto_2 is None:
 # raise Exception('err')
 #if 'wb-auto-2' != wb_auto_2.get('id'):
 # raise Exception('err')
 #child = wb_auto_2.find()
 jobpostingdetails = soup.find('div',class_='job-posting-details')
 child = jobpostingdetails.find()
 child = child.find()
 wb_cont = child.find()
 #print(wb_cont)
 if 'wb-cont' != wb_cont.get('id'):
  raise Exception('err')
 title = wb_cont.find('span', {'property':'title'}).contents[0].get_text()
 title = title.strip().title()
 if not title:
  raise Exception('title not found')
 #.find('p',recursive=False)
 company = child.find('span',{'property':'hiringOrganization'}).find('span',{'property':'name'}).find().get_text()
 company = company.strip()
 if not company:
  raise Exception('company not found')
 lastel = child.find('div',class_='job-posting-detail-requirements', recursive=False)
 if lastel is None:
  lastel = child.find('div',class_='job-posting-detail-apply', recursive=False)
  if lastel is None:
   raise Exception('err')
  while lastel.next_sibling:
   lastel.next_sibling.extract()
  lastel.extract()
 else:
  while lastel.next_sibling:
   lastel.next_sibling.extract()
 result_html = child.encode_contents()
elif ptype == Posting.indeed:
 soup = BeautifulSoup(htm, 'html.parser')
 vjs_container = soup.find('div', {'id': 'jobsearch-ViewjobPaneWrapper'})
 if vjs_container is None:
  raise Exception('err')
 job_com = vjs_container.find('div',class_='jobsearch-JobComponent')
 infohdr = job_com.find('div',class_='jobsearch-HeaderContainer').find('div',class_='jobsearch-InfoHeaderContainer')
 title = infohdr.find('h2',class_='jobsearch-JobInfoHeader-title').find('span').contents[0].get_text()
 title = title.strip().title()
 if not title:
  raise Exception('title not found')
 company = infohdr.find('div', {'data-company-name':'true'}).get_text()
 company = company.strip()
 if not company:
  raise Exception('company not found')
 job_com.find('div',class_='jobsearch-BodyContainer').find('div',class_='jobsearch-JobMetadataFooter').extract()
 result_html = job_com.encode_contents()
elif ptype == Posting.linkedin:
 soup = BeautifulSoup(htm, 'html.parser')
 #mcont = soup.find('main', {'id':'main'}).find('div',class_='jobs-search__job-details').find('div',class_='jobs-details__main-content')
 mcont = soup.find('main', {'id':'main'}).find('div',class_='jobs-details__main-content')
 jutc = mcont.find('div',class_='jobs-unified-top-card')
 title = jutc.find('h2',class_='job-details-jobs-unified-top-card__job-title').get_text()
 title = title.strip().title()
 if not title:
  raise Exception('title not found')
 company = jutc.find('div',class_='job-details-jobs-unified-top-card__primary-description-container').find('a',class_='app-aware-link').get_text()
 company = company.strip()
 if not company:
  raise Exception('company not found')
 hchi = mcont.find('div',class_='hirer-card__hirer-information')
 if hchi:
  recruiternm = hchi.find('span',class_='jobs-poster__name')
  recruiter = recruiternm.find('strong').get_text()
  if shutil.which('run-external-cmd') and shutil.which('firefox') and shutil.which('xclip'):
   recruiterurl: str = hchi.find('a',class_='app-aware-link').get('href')
   if not recruiterurl.startswith('https://'):
    raise Exception('unexpected url')
   #print(recruiterurl)
   subprocess.run(['run-external-cmd', 'firefox', recruiterurl])
   while True:
    print('Waiting for userscript in browser detect Mr./Ms.')
    time.sleep(1)
    text_from_clip: str = subprocess.check_output(['xclip', '-o', '-selection', 'clipboard']).decode()
    if text_from_clip == 'LINKEDIN_CLIP_HE':
     recruiter = 'Mr. '+recruiter
     break
    elif text_from_clip == 'LINKEDIN_CLIP_SHE':
     recruiter = 'Ms. '+recruiter
     break
    elif text_from_clip == 'LINKEDIN_CLIP_UNKNOWN':
     break
 lastel = mcont.find('div',{'id':'SALARY'}, recursive=False)
 while lastel.next_sibling.name != 'section':
  lastel.next_sibling.extract()
 lsection = lastel.next_sibling
 lastel.extract()
 lsection.insert_before(soup.new_tag('br'))
 lsection.insert_before(soup.new_tag('br'))
 lsection.insert_before(soup.new_tag('br'))
 lsection.insert_before(soup.new_tag('br'))
 lsection = lsection.find('section')
 lastel = lsection.find('div')
 while lastel.next_sibling:
  lastel.next_sibling.extract()
 lastel = lastel.find('p', class_='jobs-company__company-description')
 while lastel.next_sibling:
  lastel.next_sibling.extract()
 if lastel.find(class_='inline-show-more-text__button'):
  raise Exception('Found "show more". It must be clicked beforehand.')
 result_html = mcont.encode_contents()
else:
 raise Exception('Unexpected error.')

fields = htm_file+'.fields.json'
excerpt = htm_file+'.excerpt.html'
Path(fields).write_text(json.dumps({'postingsrc':postingsrc, 'title':title, 'company':company, 'recruiter':recruiter}))
Path(excerpt).write_bytes(result_html)
if shutil.which('libreoffice') is None:
 sys.exit(0)

subprocess.run(['libreoffice', '--headless', '--convert-to', 'txt:Text', excerpt], check=True, cwd=tdir)
kwparser.kwparse(kws, txtdesc, kwlst)
