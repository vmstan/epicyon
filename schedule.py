__filename__ = "schedule.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.2.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Calendar"

import os
import time
import datetime
from utils import has_object_dict
from utils import getStatusNumber
from utils import load_json
from utils import is_account_dir
from utils import acct_dir
from outbox import postMessageToOutbox


def _updatePostSchedule(base_dir: str, handle: str, httpd,
                        maxScheduledPosts: int) -> None:
    """Checks if posts are due to be delivered and if so moves them to the outbox
    """
    scheduleIndexFilename = \
        base_dir + '/accounts/' + handle + '/schedule.index'
    if not os.path.isfile(scheduleIndexFilename):
        return

    # get the current time as an int
    curr_time = datetime.datetime.utcnow()
    daysSinceEpoch = (curr_time - datetime.datetime(1970, 1, 1)).days

    scheduleDir = base_dir + '/accounts/' + handle + '/scheduled/'
    indexLines = []
    deleteSchedulePost = False
    nickname = handle.split('@')[0]
    with open(scheduleIndexFilename, 'r') as fp:
        for line in fp:
            if ' ' not in line:
                continue
            dateStr = line.split(' ')[0]
            if 'T' not in dateStr:
                continue
            post_id = line.split(' ', 1)[1].replace('\n', '').replace('\r', '')
            post_filename = scheduleDir + post_id + '.json'
            if deleteSchedulePost:
                # delete extraneous scheduled posts
                if os.path.isfile(post_filename):
                    try:
                        os.remove(post_filename)
                    except OSError:
                        print('EX: _updatePostSchedule unable to delete ' +
                              str(post_filename))
                continue
            # create the new index file
            indexLines.append(line)
            # convert string date to int
            postTime = \
                datetime.datetime.strptime(dateStr, "%Y-%m-%dT%H:%M:%S%z")
            postTime = postTime.replace(tzinfo=None)
            postDaysSinceEpoch = \
                (postTime - datetime.datetime(1970, 1, 1)).days
            if daysSinceEpoch < postDaysSinceEpoch:
                continue
            if daysSinceEpoch == postDaysSinceEpoch:
                if curr_time.time().hour < postTime.time().hour:
                    continue
                if curr_time.time().minute < postTime.time().minute:
                    continue
            if not os.path.isfile(post_filename):
                print('WARN: schedule missing post_filename=' + post_filename)
                indexLines.remove(line)
                continue
            # load post
            post_json_object = load_json(post_filename)
            if not post_json_object:
                print('WARN: schedule json not loaded')
                indexLines.remove(line)
                continue

            # set the published time
            # If this is not recent then http checks on the receiving side
            # will reject it
            statusNumber, published = getStatusNumber()
            if post_json_object.get('published'):
                post_json_object['published'] = published
            if has_object_dict(post_json_object):
                if post_json_object['object'].get('published'):
                    post_json_object['published'] = published

            print('Sending scheduled post ' + post_id)

            if nickname:
                httpd.postToNickname = nickname
            if not postMessageToOutbox(httpd.session,
                                       httpd.translate,
                                       post_json_object, nickname,
                                       httpd, base_dir,
                                       httpd.http_prefix,
                                       httpd.domain,
                                       httpd.domain_full,
                                       httpd.onion_domain,
                                       httpd.i2p_domain,
                                       httpd.port,
                                       httpd.recent_posts_cache,
                                       httpd.followers_threads,
                                       httpd.federation_list,
                                       httpd.send_threads,
                                       httpd.postLog,
                                       httpd.cached_webfingers,
                                       httpd.person_cache,
                                       httpd.allow_deletion,
                                       httpd.proxy_type,
                                       httpd.project_version,
                                       httpd.debug,
                                       httpd.yt_replace_domain,
                                       httpd.twitter_replacement_domain,
                                       httpd.show_published_date_only,
                                       httpd.allow_local_network_access,
                                       httpd.city, httpd.system_language,
                                       httpd.shared_items_federated_domains,
                                       httpd.sharedItemFederationTokens,
                                       httpd.low_bandwidth,
                                       httpd.signing_priv_key_pem,
                                       httpd.peertube_instances,
                                       httpd.theme_name,
                                       httpd.max_like_count,
                                       httpd.max_recent_posts,
                                       httpd.cw_lists,
                                       httpd.lists_enabled,
                                       httpd.content_license_url):
                indexLines.remove(line)
                try:
                    os.remove(post_filename)
                except OSError:
                    print('EX: _updatePostSchedule unable to delete ' +
                          str(post_filename))
                continue

            # move to the outbox
            outboxPostFilename = \
                post_filename.replace('/scheduled/', '/outbox/')
            os.rename(post_filename, outboxPostFilename)

            print('Scheduled post sent ' + post_id)

            indexLines.remove(line)
            if len(indexLines) > maxScheduledPosts:
                deleteSchedulePost = True

    # write the new schedule index file
    scheduleIndexFile = \
        base_dir + '/accounts/' + handle + '/schedule.index'
    with open(scheduleIndexFile, 'w+') as scheduleFile:
        for line in indexLines:
            scheduleFile.write(line)


def runPostSchedule(base_dir: str, httpd, maxScheduledPosts: int):
    """Dispatches scheduled posts
    """
    while True:
        time.sleep(60)
        # for each account
        for subdir, dirs, files in os.walk(base_dir + '/accounts'):
            for account in dirs:
                if '@' not in account:
                    continue
                if not is_account_dir(account):
                    continue
                # scheduled posts index for this account
                scheduleIndexFilename = \
                    base_dir + '/accounts/' + account + '/schedule.index'
                if not os.path.isfile(scheduleIndexFilename):
                    continue
                _updatePostSchedule(base_dir, account,
                                    httpd, maxScheduledPosts)
            break


def runPostScheduleWatchdog(project_version: str, httpd) -> None:
    """This tries to keep the scheduled post thread running even if it dies
    """
    print('Starting scheduled post watchdog')
    postScheduleOriginal = \
        httpd.thrPostSchedule.clone(runPostSchedule)
    httpd.thrPostSchedule.start()
    while True:
        time.sleep(20)
        if httpd.thrPostSchedule.is_alive():
            continue
        httpd.thrPostSchedule.kill()
        httpd.thrPostSchedule = \
            postScheduleOriginal.clone(runPostSchedule)
        httpd.thrPostSchedule.start()
        print('Restarting scheduled posts...')


def removeScheduledPosts(base_dir: str, nickname: str, domain: str) -> None:
    """Removes any scheduled posts
    """
    # remove the index
    scheduleIndexFilename = \
        acct_dir(base_dir, nickname, domain) + '/schedule.index'
    if os.path.isfile(scheduleIndexFilename):
        try:
            os.remove(scheduleIndexFilename)
        except OSError:
            print('EX: removeScheduledPosts unable to delete ' +
                  scheduleIndexFilename)
    # remove the scheduled posts
    scheduledDir = acct_dir(base_dir, nickname, domain) + '/scheduled'
    if not os.path.isdir(scheduledDir):
        return
    for scheduledPostFilename in os.listdir(scheduledDir):
        filePath = os.path.join(scheduledDir, scheduledPostFilename)
        if os.path.isfile(filePath):
            try:
                os.remove(filePath)
            except OSError:
                print('EX: removeScheduledPosts unable to delete ' +
                      filePath)
