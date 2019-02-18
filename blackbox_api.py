#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# let's detach bots from platforms
#
# usage: python3 blackbox_api.py post whatToPost --mastodon

#TODO: change "if verbose: print(...)" for logging.info(...)

__author__ = "@jartigag"
__version__ = "0.1"

import argparse
import json
from tweepy import OAuthHandler, API
import secrets
from datetime import datetime
import urllib.request

try:
    auth = OAuthHandler(secrets.twitter_consumer_key, secrets.twitter_consumer_secret)
    auth.set_access_token(secrets.twitter_access_token, secrets.twitter_access_token_secret)
    twitter_api = API(auth)
except Exception as e:
    pass

def post(content,twitter=False,mastodon=False,telegram=False,reply_options=[],verbose=False):
    """post some content on any platform

    args:
        content (str): what to post
        twitter (bool): if True, post it on Twitter
        mastodon (bool): if True, post it on Mastodon
        telegram (bool): if True, post it (either on a chat or a channel) on Telegram
        reply_options (list): if not empty, include predefined reply options to the post (for Telegram)
        verbose (bool): if True, print post info

    returns:
        the post object as a JSON. if error, post=False
    """
    global secrets
    post = True
    if twitter:
        try:
            post = twitter_api.update_status(content)
            tweet_url = '{}/{}/status/{}'.format(post.source_url,post.user.screen_name,post.id)
            if verbose: print('%s - \033[1mtweeted "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
                (post.created_at.strftime('%Y-%m-%d %H:%M:%S'),post.text,tweet_url))
            post = json.loads(post)
        except Exception as e:
            post = False
            if verbose: print("\n[\033[91m!\033[0m] twitter error: %s" % e)
    if mastodon:
        try:
            header = {'Authorization': 'Bearer {}'.format(secrets.masto_access_token)}
            data = urllib.parse.urlencode({'status': content}).encode('utf8')
            req = urllib.request.Request('https://botsin.space/api/v1/statuses', data, header)
            resp = urllib.request.urlopen(req)
            post = json.loads(resp.read().decode('utf8'))
            if verbose: print('%s - \033[1mtooted "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
                (post['created_at'],post['content'],post['uri']))
        except Exception as e:
            post = False
            if verbose: print("\n[\033[91m!\033[0m] mastodon error: %s" % e)
    if telegram:
        if reply_options:
            reply_markup = '&reply_markup={"keyboard":['+','.join(map('["{0}"]'.format, reply_options))+']}'
        else:
            reply_markup = ''
        try:
            req = "https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}{}".format(\
                    secrets.telegram_token, secrets.telegram_chat_id, content, reply_markup)
            resp = urllib.request.urlopen(req)
            post = json.loads(resp.read().decode('utf8'))
            if verbose: print('%s - \033[1msent by telegram "\033[0m%s\033[1m" (in \033[0m%s\033[1m)\033[0m' %
                (datetime.now().strftime('%Y-%m-%d %H:%M:%S'),content,secrets.telegram_chat_id))
        except Exception as e:
            post = False
            if verbose: print("\n[\033[91m!\033[0m] telegram error: %s" % e)
    return post

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description="let's detach from platforms, v%s by %s" % (__version__,__author__),
        usage="%(prog)s post 'content of the post' [--mastodon --telegram --twitter] [-v]")
    parser.add_argument('action',choices=['post'],
        help='what to do')
    parser.add_argument('content',
        help="action's text/content")
    parser.add_argument('-m','--mastodon',action='store_true',
        help='where: mastodon')
    parser.add_argument('-tg','--telegram',action='store_true',
        help='where: telegram')
    parser.add_argument('-tw','--twitter',action='store_true',
        help='where: twitter')
    parser.add_argument('-r','--reply_options',nargs='+',
            help="list of replies to be chosen")
    parser.add_argument('-v','--verbose',action='store_true',
        help='to print or not to print')
    args = parser.parse_args()

    if args.action=='post':
        post(args.content,args.twitter,args.mastodon,args.telegram,args.reply_options,args.verbose)
