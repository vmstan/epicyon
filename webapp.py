__filename__ = "webapp.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.1.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@freedombone.net"
__status__ = "Production"

import os
from shutil import copyfile
from utils import getNicknameFromActor
from utils import getDomainFromActor
from utils import loadJson
from shares import getValidSharedItemID
from webapp_utils import getAltPath
from webapp_utils import htmlHeaderWithExternalStyle
from webapp_utils import htmlFooter


def htmlFollowingList(cssCache: {}, baseDir: str,
                      followingFilename: str) -> str:
    """Returns a list of handles being followed
    """
    with open(followingFilename, 'r') as followingFile:
        msg = followingFile.read()
        followingList = msg.split('\n')
        followingList.sort()
        if followingList:
            cssFilename = baseDir + '/epicyon-profile.css'
            if os.path.isfile(baseDir + '/epicyon.css'):
                cssFilename = baseDir + '/epicyon.css'

            followingListHtml = htmlHeaderWithExternalStyle(cssFilename)
            for followingAddress in followingList:
                if followingAddress:
                    followingListHtml += \
                        '<h3>@' + followingAddress + '</h3>'
            followingListHtml += htmlFooter()
            msg = followingListHtml
        return msg
    return ''


def htmlHashtagBlocked(cssCache: {}, baseDir: str, translate: {}) -> str:
    """Show the screen for a blocked hashtag
    """
    blockedHashtagForm = ''
    cssFilename = baseDir + '/epicyon-suspended.css'
    if os.path.isfile(baseDir + '/suspended.css'):
        cssFilename = baseDir + '/suspended.css'

    blockedHashtagForm = htmlHeaderWithExternalStyle(cssFilename)
    blockedHashtagForm += '<div><center>\n'
    blockedHashtagForm += \
        '  <p class="screentitle">' + \
        translate['Hashtag Blocked'] + '</p>\n'
    blockedHashtagForm += \
        '  <p>See <a href="/terms">' + \
        translate['Terms of Service'] + '</a></p>\n'
    blockedHashtagForm += '</center></div>\n'
    blockedHashtagForm += htmlFooter()
    return blockedHashtagForm


def htmlRemoveSharedItem(cssCache: {}, translate: {}, baseDir: str,
                         actor: str, shareName: str,
                         callingDomain: str) -> str:
    """Shows a screen asking to confirm the removal of a shared item
    """
    itemID = getValidSharedItemID(shareName)
    nickname = getNicknameFromActor(actor)
    domain, port = getDomainFromActor(actor)
    domainFull = domain
    if port:
        if port != 80 and port != 443:
            domainFull = domain + ':' + str(port)
    sharesFile = baseDir + '/accounts/' + \
        nickname + '@' + domain + '/shares.json'
    if not os.path.isfile(sharesFile):
        print('ERROR: no shares file ' + sharesFile)
        return None
    sharesJson = loadJson(sharesFile)
    if not sharesJson:
        print('ERROR: unable to load shares.json')
        return None
    if not sharesJson.get(itemID):
        print('ERROR: share named "' + itemID + '" is not in ' + sharesFile)
        return None
    sharedItemDisplayName = sharesJson[itemID]['displayName']
    sharedItemImageUrl = None
    if sharesJson[itemID].get('imageUrl'):
        sharedItemImageUrl = sharesJson[itemID]['imageUrl']

    if os.path.isfile(baseDir + '/img/shares-background.png'):
        if not os.path.isfile(baseDir + '/accounts/shares-background.png'):
            copyfile(baseDir + '/img/shares-background.png',
                     baseDir + '/accounts/shares-background.png')

    cssFilename = baseDir + '/epicyon-follow.css'
    if os.path.isfile(baseDir + '/follow.css'):
        cssFilename = baseDir + '/follow.css'

    sharesStr = htmlHeaderWithExternalStyle(cssFilename)
    sharesStr += '<div class="follow">\n'
    sharesStr += '  <div class="followAvatar">\n'
    sharesStr += '  <center>\n'
    if sharedItemImageUrl:
        sharesStr += '  <img loading="lazy" src="' + \
            sharedItemImageUrl + '"/>\n'
    sharesStr += \
        '  <p class="followText">' + translate['Remove'] + \
        ' ' + sharedItemDisplayName + ' ?</p>\n'
    postActor = getAltPath(actor, domainFull, callingDomain)
    sharesStr += '  <form method="POST" action="' + postActor + '/rmshare">\n'
    sharesStr += \
        '    <input type="hidden" name="actor" value="' + actor + '">\n'
    sharesStr += '    <input type="hidden" name="shareName" value="' + \
        shareName + '">\n'
    sharesStr += \
        '    <button type="submit" class="button" name="submitYes">' + \
        translate['Yes'] + '</button>\n'
    sharesStr += \
        '    <a href="' + actor + '/inbox' + '"><button class="button">' + \
        translate['No'] + '</button></a>\n'
    sharesStr += '  </form>\n'
    sharesStr += '  </center>\n'
    sharesStr += '  </div>\n'
    sharesStr += '</div>\n'
    sharesStr += htmlFooter()
    return sharesStr


def htmlFollowConfirm(cssCache: {}, translate: {}, baseDir: str,
                      originPathStr: str,
                      followActor: str,
                      followProfileUrl: str) -> str:
    """Asks to confirm a follow
    """
    followDomain, port = getDomainFromActor(followActor)

    if os.path.isfile(baseDir + '/accounts/follow-background-custom.jpg'):
        if not os.path.isfile(baseDir + '/accounts/follow-background.jpg'):
            copyfile(baseDir + '/accounts/follow-background-custom.jpg',
                     baseDir + '/accounts/follow-background.jpg')

    cssFilename = baseDir + '/epicyon-follow.css'
    if os.path.isfile(baseDir + '/follow.css'):
        cssFilename = baseDir + '/follow.css'

    followStr = htmlHeaderWithExternalStyle(cssFilename)
    followStr += '<div class="follow">\n'
    followStr += '  <div class="followAvatar">\n'
    followStr += '  <center>\n'
    followStr += '  <a href="' + followActor + '">\n'
    followStr += '  <img loading="lazy" src="' + followProfileUrl + '"/></a>\n'
    followStr += \
        '  <p class="followText">' + translate['Follow'] + ' ' + \
        getNicknameFromActor(followActor) + '@' + followDomain + ' ?</p>\n'
    followStr += '  <form method="POST" action="' + \
        originPathStr + '/followconfirm">\n'
    followStr += '    <input type="hidden" name="actor" value="' + \
        followActor + '">\n'
    followStr += \
        '    <button type="submit" class="button" name="submitYes">' + \
        translate['Yes'] + '</button>\n'
    followStr += \
        '    <a href="' + originPathStr + '"><button class="button">' + \
        translate['No'] + '</button></a>\n'
    followStr += '  </form>\n'
    followStr += '</center>\n'
    followStr += '</div>\n'
    followStr += '</div>\n'
    followStr += htmlFooter()
    return followStr


def htmlUnfollowConfirm(cssCache: {}, translate: {}, baseDir: str,
                        originPathStr: str,
                        followActor: str,
                        followProfileUrl: str) -> str:
    """Asks to confirm unfollowing an actor
    """
    followDomain, port = getDomainFromActor(followActor)

    if os.path.isfile(baseDir + '/accounts/follow-background-custom.jpg'):
        if not os.path.isfile(baseDir + '/accounts/follow-background.jpg'):
            copyfile(baseDir + '/accounts/follow-background-custom.jpg',
                     baseDir + '/accounts/follow-background.jpg')

    cssFilename = baseDir + '/epicyon-follow.css'
    if os.path.isfile(baseDir + '/follow.css'):
        cssFilename = baseDir + '/follow.css'

    followStr = htmlHeaderWithExternalStyle(cssFilename)
    followStr += '<div class="follow">\n'
    followStr += '  <div class="followAvatar">\n'
    followStr += '  <center>\n'
    followStr += '  <a href="' + followActor + '">\n'
    followStr += '  <img loading="lazy" src="' + followProfileUrl + '"/></a>\n'
    followStr += \
        '  <p class="followText">' + translate['Stop following'] + \
        ' ' + getNicknameFromActor(followActor) + \
        '@' + followDomain + ' ?</p>\n'
    followStr += '  <form method="POST" action="' + \
        originPathStr + '/unfollowconfirm">\n'
    followStr += '    <input type="hidden" name="actor" value="' + \
        followActor + '">\n'
    followStr += \
        '    <button type="submit" class="button" name="submitYes">' + \
        translate['Yes'] + '</button>\n'
    followStr += \
        '    <a href="' + originPathStr + '"><button class="button">' + \
        translate['No'] + '</button></a>\n'
    followStr += '  </form>\n'
    followStr += '</center>\n'
    followStr += '</div>\n'
    followStr += '</div>\n'
    followStr += htmlFooter()
    return followStr


def htmlUnblockConfirm(cssCache: {}, translate: {}, baseDir: str,
                       originPathStr: str,
                       blockActor: str,
                       blockProfileUrl: str) -> str:
    """Asks to confirm unblocking an actor
    """
    blockDomain, port = getDomainFromActor(blockActor)

    if os.path.isfile(baseDir + '/img/block-background.png'):
        if not os.path.isfile(baseDir + '/accounts/block-background.png'):
            copyfile(baseDir + '/img/block-background.png',
                     baseDir + '/accounts/block-background.png')

    cssFilename = baseDir + '/epicyon-follow.css'
    if os.path.isfile(baseDir + '/follow.css'):
        cssFilename = baseDir + '/follow.css'

    blockStr = htmlHeaderWithExternalStyle(cssFilename)
    blockStr += '<div class="block">\n'
    blockStr += '  <div class="blockAvatar">\n'
    blockStr += '  <center>\n'
    blockStr += '  <a href="' + blockActor + '">\n'
    blockStr += '  <img loading="lazy" src="' + blockProfileUrl + '"/></a>\n'
    blockStr += \
        '  <p class="blockText">' + translate['Stop blocking'] + ' ' + \
        getNicknameFromActor(blockActor) + '@' + blockDomain + ' ?</p>\n'
    blockStr += '  <form method="POST" action="' + \
        originPathStr + '/unblockconfirm">\n'
    blockStr += '    <input type="hidden" name="actor" value="' + \
        blockActor + '">\n'
    blockStr += \
        '    <button type="submit" class="button" name="submitYes">' + \
        translate['Yes'] + '</button>\n'
    blockStr += \
        '    <a href="' + originPathStr + '"><button class="button">' + \
        translate['No'] + '</button></a>\n'
    blockStr += '  </form>\n'
    blockStr += '</center>\n'
    blockStr += '</div>\n'
    blockStr += '</div>\n'
    blockStr += htmlFooter()
    return blockStr
