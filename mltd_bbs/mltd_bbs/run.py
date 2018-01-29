# -*- coding: utf-8 -*-


from scrapy import cmdline
from mltd_bbs.settings import JOB_KEEP


if JOB_KEEP["ON"] == True:
    job_keep = " -s JOBDIR=" + JOB_KEEP["DIR"]
else:
    job_keep = ""


exec_words = "scrapy crawl bbs2ch_spider" + job_keep
cmdline.execute(exec_words.split())
