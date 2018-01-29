# -*- coding: utf-8 -*-

from scrapy import cmdline
from settings import JOB_KEEP


if JOB_KEEP["ON"] == True:
    job_keep = " -s JOBDIR=" + JOB_KEEP["DIR"]
else:
    job_keep = ""


exec_words = "scrapy crawl mypage_spider" + job_keep
cmdline.execute(exec_words.split())
