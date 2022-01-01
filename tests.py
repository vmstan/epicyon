__filename__ = "tests.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.2.0"
__maintainer__ = "Bob Mottram"
__email__ = "bob@libreserver.org"
__status__ = "Production"
__module_group__ = "Testing"

import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import load_pem_public_key
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.asymmetric import utils as hazutils
import time
import os
import shutil
import json
import datetime
from shutil import copyfile
from random import randint
from time import gmtime, strftime
from pprint import pprint
from httpsig import get_digest_algorithm_from_headers
from httpsig import get_digest_prefix
from httpsig import create_signed_header
from httpsig import sign_post_headers
from httpsig import sign_post_headers_new
from httpsig import verify_post_headers
from httpsig import message_content_digest
from cache import store_person_in_cache
from cache import get_person_from_cache
from threads import thread_with_trace
from daemon import run_daemon
from session import create_session
from session import get_json
from posts import get_actor_from_in_reply_to
from posts import regenerate_index_for_box
from posts import remove_post_interactions
from posts import get_mentioned_people
from posts import valid_content_warning
from posts import delete_all_posts
from posts import create_public_post
from posts import send_post
from posts import no_of_followers_on_domain
from posts import group_followers_by_domain
from posts import archive_posts_for_person
from posts import send_post_via_server
from posts import seconds_between_published
from follow import clear_follows
from follow import clear_followers
from follow import send_follow_requestViaServer
from follow import send_unfollow_request_via_server
from siteactive import site_is_active
from utils import convert_to_snake_case
from utils import get_sha_256
from utils import dangerous_svg
from utils import can_reply_to
from utils import is_group_account
from utils import get_actor_languages_list
from utils import get_category_types
from utils import get_supported_languages
from utils import set_config_param
from utils import is_group_actor
from utils import date_string_to_seconds
from utils import date_seconds_to_string
from utils import valid_password
from utils import user_agent_domain
from utils import camel_case_split
from utils import decoded_host
from utils import get_full_domain
from utils import valid_nickname
from utils import first_paragraph_from_string
from utils import remove_id_ending
from utils import update_recent_posts_cache
from utils import follow_person
from utils import get_nickname_from_actor
from utils import get_domain_from_actor
from utils import copytree
from utils import load_json
from utils import save_json
from utils import get_status_number
from utils import get_followers_of_person
from utils import remove_html
from utils import dangerous_markup
from utils import acct_dir
from pgp import extract_pgp_public_key
from pgp import pgp_public_key_upload
from utils import contains_pgp_public_key
from follow import add_follower_of_person
from follow import unfollow_account
from follow import unfollower_of_account
from follow import send_follow_request
from person import create_person
from person import create_group
from person import set_display_nickname
from person import set_bio
# from person import generate_rsa_key
from skills import set_skill_level
from skills import actor_skill_value
from skills import set_skills_from_dict
from skills import actor_has_skill
from roles import set_rolesFromList
from roles import set_role
from roles import actor_has_role
from auth import constant_time_string_check
from auth import create_basic_auth_header
from auth import authorize_basic
from auth import store_basic_credentials
from like import like_post
from like import send_like_via_server
from reaction import reaction_post
from reaction import send_reaction_via_server
from reaction import valid_emoji_content
from announce import announce_public
from announce import send_announce_via_server
from city import parse_nogo_string
from city import spoof_geolocation
from city import point_in_nogo
from media import get_image_dimensions
from media import get_media_path
from media import get_attachment_media_type
from delete import send_delete_via_server
from inbox import json_post_allows_comments
from inbox import valid_inbox
from inbox import valid_inbox_filenames
from categories import guess_hashtag_category
from content import words_similarity
from content import get_price_from_string
from content import limit_repeated_words
from content import switch_words
from content import extract_text_fields_in_post
from content import valid_hash_tag
from content import html_replace_email_quote
from content import html_replace_quote_marks
from content import dangerous_css
from content import add_web_links
from content import replace_emoji_from_tags
from content import add_html_tags
from content import remove_long_words
from content import replace_content_duplicates
from content import remove_text_formatting
from content import remove_html_tag
from theme import update_default_themes_list
from theme import set_cs_sparam
from theme import scan_themes_for_scripts
from linked_data_sig import generate_json_signature
from linked_data_sig import verify_json_signature
from newsdaemon import hashtag_rule_tree
from newsdaemon import hashtag_rule_resolve
from newswire import get_newswire_tags
from newswire import parse_feed_date
from newswire import limit_word_lengths
from mastoapiv1 import get_masto_api_v1id_from_nickname
from mastoapiv1 import get_nickname_from_masto_api_v1id
from webapp_post import prepare_html_post_nickname
from speaker import speaker_replace_links
from markdown import markdown_to_html
from languages import set_actor_languages
from languages import get_actor_languages
from languages import get_links_from_content
from languages import add_links_to_content
from languages import libretranslate
from languages import libretranslate_languages
from shares import authorize_shared_items
from shares import generate_shared_item_federation_tokens
from shares import create_shared_item_federation_token
from shares import update_shared_item_federation_token
from shares import merge_shared_item_tokens
from shares import send_share_via_server
from shares import get_shared_items_catalog_via_server
from blocking import load_cw_lists
from blocking import add_cw_from_lists

testServerGroupRunning = False
testServerAliceRunning = False
testServerBobRunning = False
testServerEveRunning = False
thrGroup = None
thrAlice = None
thrBob = None
thrEve = None


def _test_http_signed_get(base_dir: str):
    print('testHttpSignedGET')
    http_prefix = 'https'
    debug = True

    boxpath = "/users/Actor"
    host = "epicyon.libreserver.org"
    content_length = "0"
    user_agent = "http.rb/4.4.1 (Mastodon/3.4.1; +https://octodon.social/)"
    dateStr = 'Wed, 01 Sep 2021 16:11:10 GMT'
    accept_encoding = 'gzip'
    accept = \
        'application/activity+json, application/ld+json'
    signature = \
        'keyId="https://octodon.social/actor#main-key",' + \
        'algorithm="rsa-sha256",' + \
        'headers="(request-target) host date accept",' + \
        'signature="Fe53PS9A2OSP4x+W/svhA' + \
        'jUKHBvnAR73Ez+H32au7DQklLk08Lvm8al' + \
        'LS7pCor28yfyx+DfZADgq6G1mLLRZo0OOn' + \
        'PFSog7DhdcygLhBUMS0KlT5KVGwUS0tw' + \
        'jdiHv4OC83RiCr/ZySBgOv65YLHYmGCi5B' + \
        'IqSZJRkqi8+SLmLGESlNOEzKu+jIxOBY' + \
        'mEEdIpNrDeE5YrFKpfTC3vS2GnxGOo5J/4' + \
        'lB2h+dlUpso+sv5rDz1d1FsqRWK8waV7' + \
        '4HUfLV+qbgYRceOTyZIi50vVqLvt9CTQes' + \
        'KZHG3GrrPfaBuvoUbR4MCM3BUvpB7EzL' + \
        '9F17Y+Ea9mo8zjqzZm8HaZQ=="'
    publicKeyPem = \
        '-----BEGIN PUBLIC KEY-----\n' + \
        'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMII' + \
        'BCgKCAQEA1XT+ov/i4LDYuaXCwh4r\n' + \
        '2rVfWtnz68wnFx3knwymwtRoAc/SFGzp9ye' + \
        '5ogG1uPcbe7MeirZHhaBICynPlL32\n' + \
        's9OYootI7MsQWn+vu7azxiXO7qcTPByvGcl' + \
        '0vpLhtT/ApmlMintkRTVXdzBdJVM0\n' + \
        'UsmYKg6U+IHNL+a1gURHGXep2Ih0BJMh4Aa' + \
        'DbaID6jtpJZvbIkYgJ4IJucOe+A3T\n' + \
        'YPMwkBA84ew+hso+vKQfTunyDInuPQbEzrA' + \
        'zMJXEHS7IpBhdS4/cEox86BoDJ/q0\n' + \
        'KOEOUpUDniFYWb9k1+9B387OviRDLIcLxNZ' + \
        'nf+bNq8d+CwEXY2xGsToBle/q74d8\n' + \
        'BwIDAQAB\n' + \
        '-----END PUBLIC KEY-----\n'
    headers = {
        "user-agent": user_agent,
        "content-length": content_length,
        "host": host,
        "date": dateStr,
        "accept": accept,
        "accept-encoding": accept_encoding,
        "signature": signature
    }
    GETmethod = True
    messageBodyDigest = None
    messageBodyJsonStr = ''
    noRecencyCheck = True
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, GETmethod, messageBodyDigest,
                               messageBodyJsonStr, debug, noRecencyCheck)
    # Change a single character and the signature should fail
    headers['date'] = headers['date'].replace(':10', ':11')
    assert not verify_post_headers(http_prefix, publicKeyPem, headers,
                                   boxpath, GETmethod, messageBodyDigest,
                                   messageBodyJsonStr, debug, noRecencyCheck)

    path = base_dir + '/.testHttpsigGET'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)

    nickname = 'testactor'
    hostDomain = 'someother.instance'
    domain = 'argumentative.social'
    http_prefix = 'https'
    port = 443
    withDigest = False
    password = 'SuperSecretPassword'
    noRecencyCheck = True
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(path, nickname, domain, port, http_prefix,
                      False, False, password)
    assert privateKeyPem
    assert publicKeyPem
    messageBodyJsonStr = ''

    headersDomain = get_full_domain(hostDomain, port)

    dateStr = 'Tue, 14 Sep 2021 16:19:00 GMT'
    boxpath = '/inbox'
    accept = 'application/json'
#    accept = 'application/activity+json'
    headers = {
        'user-agent': 'Epicyon/1.2.0; +https://' + domain + '/',
        'host': headersDomain,
        'date': dateStr,
        'accept': accept,
        'content-length': 0
    }
    signatureHeader = create_signed_header(dateStr,
                                           privateKeyPem, nickname,
                                           domain, port,
                                           hostDomain, port,
                                           boxpath, http_prefix, False,
                                           None, accept)

    headers['signature'] = signatureHeader['signature']
    GETmethod = not withDigest
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, GETmethod, None,
                               messageBodyJsonStr, debug, noRecencyCheck)
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)


def _test_sign_and_verify() -> None:
    print('testSignAndVerify')
    publicKeyPem = \
        '-----BEGIN RSA PUBLIC KEY-----\n' + \
        'MIIBCgKCAQEAhAKYdtoeoy8zcAcR874L8' + \
        'cnZxKzAGwd7v36APp7Pv6Q2jdsPBRrw\n' + \
        'WEBnez6d0UDKDwGbc6nxfEXAy5mbhgajz' + \
        'rw3MOEt8uA5txSKobBpKDeBLOsdJKFq\n' + \
        'MGmXCQvEG7YemcxDTRPxAleIAgYYRjTSd' + \
        '/QBwVW9OwNFhekro3RtlinV0a75jfZg\n' + \
        'kne/YiktSvLG34lw2zqXBDTC5NHROUqGT' + \
        'lML4PlNZS5Ri2U4aCNx2rUPRcKIlE0P\n' + \
        'uKxI4T+HIaFpv8+rdV6eUgOrB2xeI1dSF' + \
        'Fn/nnv5OoZJEIB+VmuKn3DCUcCZSFlQ\n' + \
        'PSXSfBDiUGhwOw76WuSSsf1D4b/vLoJ10wIDAQAB\n' + \
        '-----END RSA PUBLIC KEY-----\n'

    privateKeyPem = \
        '-----BEGIN RSA PRIVATE KEY-----\n' + \
        'MIIEqAIBAAKCAQEAhAKYdtoeoy8zcAcR8' + \
        '74L8cnZxKzAGwd7v36APp7Pv6Q2jdsP\n' + \
        'BRrwWEBnez6d0UDKDwGbc6nxfEXAy5mbh' + \
        'gajzrw3MOEt8uA5txSKobBpKDeBLOsd\n' + \
        'JKFqMGmXCQvEG7YemcxDTRPxAleIAgYYR' + \
        'jTSd/QBwVW9OwNFhekro3RtlinV0a75\n' + \
        'jfZgkne/YiktSvLG34lw2zqXBDTC5NHRO' + \
        'UqGTlML4PlNZS5Ri2U4aCNx2rUPRcKI\n' + \
        'lE0PuKxI4T+HIaFpv8+rdV6eUgOrB2xeI' + \
        '1dSFFn/nnv5OoZJEIB+VmuKn3DCUcCZ\n' + \
        'SFlQPSXSfBDiUGhwOw76WuSSsf1D4b/vL' + \
        'oJ10wIDAQABAoIBAG/JZuSWdoVHbi56\n' + \
        'vjgCgkjg3lkO1KrO3nrdm6nrgA9P9qaPj' + \
        'xuKoWaKO1cBQlE1pSWp/cKncYgD5WxE\n' + \
        'CpAnRUXG2pG4zdkzCYzAh1i+c34L6oZoH' + \
        'sirK6oNcEnHveydfzJL5934egm6p8DW\n' + \
        '+m1RQ70yUt4uRc0YSor+q1LGJvGQHReF0' + \
        'WmJBZHrhz5e63Pq7lE0gIwuBqL8SMaA\n' + \
        'yRXtK+JGxZpImTq+NHvEWWCu09SCq0r83' + \
        '8ceQI55SvzmTkwqtC+8AT2zFviMZkKR\n' + \
        'Qo6SPsrqItxZWRty2izawTF0Bf5S2VAx7' + \
        'O+6t3wBsQ1sLptoSgX3QblELY5asI0J\n' + \
        'YFz7LJECgYkAsqeUJmqXE3LP8tYoIjMIA' + \
        'KiTm9o6psPlc8CrLI9CH0UbuaA2JCOM\n' + \
        'cCNq8SyYbTqgnWlB9ZfcAm/cFpA8tYci9' + \
        'm5vYK8HNxQr+8FS3Qo8N9RJ8d0U5Csw\n' + \
        'DzMYfRghAfUGwmlWj5hp1pQzAuhwbOXFt' + \
        'xKHVsMPhz1IBtF9Y8jvgqgYHLbmyiu1\n' + \
        'mwJ5AL0pYF0G7x81prlARURwHo0Yf52kE' + \
        'w1dxpx+JXER7hQRWQki5/NsUEtv+8RT\n' + \
        'qn2m6qte5DXLyn83b1qRscSdnCCwKtKWU' + \
        'ug5q2ZbwVOCJCtmRwmnP131lWRYfj67\n' + \
        'B/xJ1ZA6X3GEf4sNReNAtaucPEelgR2ns' + \
        'N0gKQKBiGoqHWbK1qYvBxX2X3kbPDkv\n' + \
        '9C+celgZd2PW7aGYLCHq7nPbmfDV0yHcW' + \
        'jOhXZ8jRMjmANVR/eLQ2EfsRLdW69bn\n' + \
        'f3ZD7JS1fwGnO3exGmHO3HZG+6AvberKY' + \
        'VYNHahNFEw5TsAcQWDLRpkGybBcxqZo\n' + \
        '81YCqlqidwfeO5YtlO7etx1xLyqa2NsCe' + \
        'G9A86UjG+aeNnXEIDk1PDK+EuiThIUa\n' + \
        '/2IxKzJKWl1BKr2d4xAfR0ZnEYuRrbeDQ' + \
        'YgTImOlfW6/GuYIxKYgEKCFHFqJATAG\n' + \
        'IxHrq1PDOiSwXd2GmVVYyEmhZnbcp8Cxa' + \
        'EMQoevxAta0ssMK3w6UsDtvUvYvF22m\n' + \
        'qQKBiD5GwESzsFPy3Ga0MvZpn3D6EJQLg' + \
        'snrtUPZx+z2Ep2x0xc5orneB5fGyF1P\n' + \
        'WtP+fG5Q6Dpdz3LRfm+KwBCWFKQjg7uTx' + \
        'cjerhBWEYPmEMKYwTJF5PBG9/ddvHLQ\n' + \
        'EQeNC8fHGg4UXU8mhHnSBt3EA10qQJfRD' + \
        's15M38eG2cYwB1PZpDHScDnDA0=\n' + \
        '-----END RSA PRIVATE KEY-----'

    # sign
    signedHeaderText = \
        '(request-target): get /actor\n' + \
        'host: octodon.social\n' + \
        'date: Tue, 14 Sep 2021 16:19:00 GMT\n' + \
        'accept: application/json'
    headerDigest = get_sha_256(signedHeaderText.encode('ascii'))
    key = load_pem_private_key(privateKeyPem.encode('utf-8'),
                               None, backend=default_backend())
    rawSignature = key.sign(headerDigest,
                            padding.PKCS1v15(),
                            hazutils.Prehashed(hashes.SHA256()))
    signature1 = base64.b64encode(rawSignature).decode('ascii')

    # verify
    paddingStr = padding.PKCS1v15()
    alg = hazutils.Prehashed(hashes.SHA256())
    pubkey = load_pem_public_key(publicKeyPem.encode('utf-8'),
                                 backend=default_backend())
    signature2 = base64.b64decode(signature1)
    pubkey.verify(signature2, headerDigest, paddingStr, alg)


def _test_http_sig_new(algorithm: str, digestAlgorithm: str):
    print('testHttpSigNew')
    http_prefix = 'https'
    port = 443
    debug = True
    messageBodyJson = {"hello": "world"}
    messageBodyJsonStr = json.dumps(messageBodyJson)
    nickname = 'foo'
    pathStr = "/" + nickname + "?param=value&pet=dog HTTP/1.1"
    domain = 'example.com'
    dateStr = 'Tue, 20 Apr 2021 02:07:55 GMT'
    digestPrefix = get_digest_prefix(digestAlgorithm)
    digestStr = digestPrefix + '=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE='
    bodyDigest = message_content_digest(messageBodyJsonStr, digestAlgorithm)
    assert bodyDigest in digestStr
    contentLength = 18
    content_type = 'application/activity+json'
    publicKeyPem = \
        '-----BEGIN RSA PUBLIC KEY-----\n' + \
        'MIIBCgKCAQEAhAKYdtoeoy8zcAcR874L8' + \
        'cnZxKzAGwd7v36APp7Pv6Q2jdsPBRrw\n' + \
        'WEBnez6d0UDKDwGbc6nxfEXAy5mbhgajz' + \
        'rw3MOEt8uA5txSKobBpKDeBLOsdJKFq\n' + \
        'MGmXCQvEG7YemcxDTRPxAleIAgYYRjTSd' + \
        '/QBwVW9OwNFhekro3RtlinV0a75jfZg\n' + \
        'kne/YiktSvLG34lw2zqXBDTC5NHROUqGT' + \
        'lML4PlNZS5Ri2U4aCNx2rUPRcKIlE0P\n' + \
        'uKxI4T+HIaFpv8+rdV6eUgOrB2xeI1dSF' + \
        'Fn/nnv5OoZJEIB+VmuKn3DCUcCZSFlQ\n' + \
        'PSXSfBDiUGhwOw76WuSSsf1D4b/vLoJ10wIDAQAB\n' + \
        '-----END RSA PUBLIC KEY-----\n'

    privateKeyPem = \
        '-----BEGIN RSA PRIVATE KEY-----\n' + \
        'MIIEqAIBAAKCAQEAhAKYdtoeoy8zcAcR8' + \
        '74L8cnZxKzAGwd7v36APp7Pv6Q2jdsP\n' + \
        'BRrwWEBnez6d0UDKDwGbc6nxfEXAy5mbh' + \
        'gajzrw3MOEt8uA5txSKobBpKDeBLOsd\n' + \
        'JKFqMGmXCQvEG7YemcxDTRPxAleIAgYYR' + \
        'jTSd/QBwVW9OwNFhekro3RtlinV0a75\n' + \
        'jfZgkne/YiktSvLG34lw2zqXBDTC5NHRO' + \
        'UqGTlML4PlNZS5Ri2U4aCNx2rUPRcKI\n' + \
        'lE0PuKxI4T+HIaFpv8+rdV6eUgOrB2xeI' + \
        '1dSFFn/nnv5OoZJEIB+VmuKn3DCUcCZ\n' + \
        'SFlQPSXSfBDiUGhwOw76WuSSsf1D4b/vL' + \
        'oJ10wIDAQABAoIBAG/JZuSWdoVHbi56\n' + \
        'vjgCgkjg3lkO1KrO3nrdm6nrgA9P9qaPj' + \
        'xuKoWaKO1cBQlE1pSWp/cKncYgD5WxE\n' + \
        'CpAnRUXG2pG4zdkzCYzAh1i+c34L6oZoH' + \
        'sirK6oNcEnHveydfzJL5934egm6p8DW\n' + \
        '+m1RQ70yUt4uRc0YSor+q1LGJvGQHReF0' + \
        'WmJBZHrhz5e63Pq7lE0gIwuBqL8SMaA\n' + \
        'yRXtK+JGxZpImTq+NHvEWWCu09SCq0r83' + \
        '8ceQI55SvzmTkwqtC+8AT2zFviMZkKR\n' + \
        'Qo6SPsrqItxZWRty2izawTF0Bf5S2VAx7' + \
        'O+6t3wBsQ1sLptoSgX3QblELY5asI0J\n' + \
        'YFz7LJECgYkAsqeUJmqXE3LP8tYoIjMIA' + \
        'KiTm9o6psPlc8CrLI9CH0UbuaA2JCOM\n' + \
        'cCNq8SyYbTqgnWlB9ZfcAm/cFpA8tYci9' + \
        'm5vYK8HNxQr+8FS3Qo8N9RJ8d0U5Csw\n' + \
        'DzMYfRghAfUGwmlWj5hp1pQzAuhwbOXFt' + \
        'xKHVsMPhz1IBtF9Y8jvgqgYHLbmyiu1\n' + \
        'mwJ5AL0pYF0G7x81prlARURwHo0Yf52kE' + \
        'w1dxpx+JXER7hQRWQki5/NsUEtv+8RT\n' + \
        'qn2m6qte5DXLyn83b1qRscSdnCCwKtKWU' + \
        'ug5q2ZbwVOCJCtmRwmnP131lWRYfj67\n' + \
        'B/xJ1ZA6X3GEf4sNReNAtaucPEelgR2ns' + \
        'N0gKQKBiGoqHWbK1qYvBxX2X3kbPDkv\n' + \
        '9C+celgZd2PW7aGYLCHq7nPbmfDV0yHcW' + \
        'jOhXZ8jRMjmANVR/eLQ2EfsRLdW69bn\n' + \
        'f3ZD7JS1fwGnO3exGmHO3HZG+6AvberKY' + \
        'VYNHahNFEw5TsAcQWDLRpkGybBcxqZo\n' + \
        '81YCqlqidwfeO5YtlO7etx1xLyqa2NsCe' + \
        'G9A86UjG+aeNnXEIDk1PDK+EuiThIUa\n' + \
        '/2IxKzJKWl1BKr2d4xAfR0ZnEYuRrbeDQ' + \
        'YgTImOlfW6/GuYIxKYgEKCFHFqJATAG\n' + \
        'IxHrq1PDOiSwXd2GmVVYyEmhZnbcp8Cxa' + \
        'EMQoevxAta0ssMK3w6UsDtvUvYvF22m\n' + \
        'qQKBiD5GwESzsFPy3Ga0MvZpn3D6EJQLg' + \
        'snrtUPZx+z2Ep2x0xc5orneB5fGyF1P\n' + \
        'WtP+fG5Q6Dpdz3LRfm+KwBCWFKQjg7uTx' + \
        'cjerhBWEYPmEMKYwTJF5PBG9/ddvHLQ\n' + \
        'EQeNC8fHGg4UXU8mhHnSBt3EA10qQJfRD' + \
        's15M38eG2cYwB1PZpDHScDnDA0=\n' + \
        '-----END RSA PRIVATE KEY-----'
    headers = {
        "host": domain,
        "date": dateStr,
        "digest": f'{digestPrefix}={bodyDigest}',
        "content-type": content_type,
        "content-length": str(contentLength)
    }
    signatureIndexHeader, signatureHeader = \
        sign_post_headers_new(dateStr, privateKeyPem, nickname,
                              domain, port,
                              domain, port,
                              pathStr, http_prefix, messageBodyJsonStr,
                              algorithm, digestAlgorithm, debug)
    print('signatureIndexHeader1: ' + str(signatureIndexHeader))
    print('signatureHeader1: ' + str(signatureHeader))
    sigInput = "keyId=\"https://example.com/users/foo#main-key\"; " + \
        "alg=hs2019; created=1618884475; " + \
        "sig1=(@request-target, @created, host, date, digest, " + \
        "content-type, content-length)"
    assert signatureIndexHeader == sigInput
    sig = "sig1=:NXAQ7AtDMR2iwhmH1qCwiZw5PVTjOw5+5kSu0Tsx/3gqz0D" + \
        "py7OQbWqFHrNB7MmS4TukX/vDyQOFdElY5yxnEhbgRwKACq0AP4QH9H" + \
        "CiRyCE8UXDdAkY4VUd6jrWjRHKRoqQN7I+Q5tb2Fu5cDfifw/PQc86Z" + \
        "NmMhPrg3OjUJ9Q2Gj29NhgJ+4el1ECg0cAy4yG1M9AQ3KvQooQFvlg1" + \
        "vp0H2xfbJQjv8FsR/lKiRdaVHqGR2CKrvxvPRPaOsFANp2wzEtiMk3O" + \
        "TrBTYU+Zb53mIspfEeLxsNtcGmBDmQKZ9Pud8f99XGJrP+uDd3zKtnr" + \
        "f3fUnRRqy37yhB7WVwkg==:"
    assert signatureHeader == sig

    debug = True
    headers['path'] = pathStr
    headers['signature'] = sig
    headers['signature-input'] = sigInput
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               pathStr, False, None,
                               messageBodyJsonStr, debug, True)

    # make a deliberate mistake
    debug = False
    headers['signature'] = headers['signature'].replace('V', 'B')
    assert not verify_post_headers(http_prefix, publicKeyPem, headers,
                                   pathStr, False, None,
                                   messageBodyJsonStr, debug, True)


def _test_httpsig_base(withDigest: bool, base_dir: str):
    print('testHttpsig(' + str(withDigest) + ')')

    path = base_dir + '/.testHttpsigBase'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)

    algorithm = 'rsa-sha256'
    digestAlgorithm = 'rsa-sha256'
    content_type = 'application/activity+json'
    nickname = 'socrates'
    hostDomain = 'someother.instance'
    domain = 'argumentative.social'
    http_prefix = 'https'
    port = 5576
    password = 'SuperSecretPassword'
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(path, nickname, domain, port, http_prefix,
                      False, False, password)
    assert privateKeyPem
    if withDigest:
        messageBodyJson = {
            "a key": "a value",
            "another key": "A string",
            "yet another key": "Another string"
        }
        messageBodyJsonStr = json.dumps(messageBodyJson)
    else:
        messageBodyJsonStr = ''

    headersDomain = get_full_domain(hostDomain, port)

    dateStr = strftime("%a, %d %b %Y %H:%M:%S %Z", gmtime())
    boxpath = '/inbox'
    if not withDigest:
        headers = {
            'host': headersDomain,
            'date': dateStr,
            'accept': content_type
        }
        signatureHeader = \
            sign_post_headers(dateStr, privateKeyPem, nickname,
                              domain, port,
                              hostDomain, port,
                              boxpath, http_prefix, None, content_type,
                              algorithm, None)
    else:
        digestPrefix = get_digest_prefix(digestAlgorithm)
        bodyDigest = \
            message_content_digest(messageBodyJsonStr, digestAlgorithm)
        contentLength = len(messageBodyJsonStr)
        headers = {
            'host': headersDomain,
            'date': dateStr,
            'digest': f'{digestPrefix}={bodyDigest}',
            'content-type': content_type,
            'content-length': str(contentLength)
        }
        assert get_digest_algorithm_from_headers(headers) == digestAlgorithm
        signatureHeader = \
            sign_post_headers(dateStr, privateKeyPem, nickname,
                              domain, port,
                              hostDomain, port,
                              boxpath, http_prefix, messageBodyJsonStr,
                              content_type, algorithm, digestAlgorithm)

    headers['signature'] = signatureHeader
    GETmethod = not withDigest
    debug = True
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, GETmethod, None,
                               messageBodyJsonStr, debug)
    if withDigest:
        # everything correct except for content-length
        headers['content-length'] = str(contentLength + 2)
        assert verify_post_headers(http_prefix, publicKeyPem, headers,
                                   boxpath, GETmethod, None,
                                   messageBodyJsonStr, False) is False
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               '/parambulator' + boxpath, GETmethod, None,
                               messageBodyJsonStr, False) is False
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, not GETmethod, None,
                               messageBodyJsonStr, False) is False
    if not withDigest:
        # fake domain
        headers = {
            'host': 'bogon.domain',
            'date': dateStr,
            'content-type': content_type
        }
    else:
        # correct domain but fake message
        messageBodyJsonStr = \
            '{"a key": "a value", "another key": "Fake GNUs", ' + \
            '"yet another key": "More Fake GNUs"}'
        contentLength = len(messageBodyJsonStr)
        digestPrefix = get_digest_prefix(digestAlgorithm)
        bodyDigest = \
            message_content_digest(messageBodyJsonStr, digestAlgorithm)
        headers = {
            'host': domain,
            'date': dateStr,
            'digest': f'{digestPrefix}={bodyDigest}',
            'content-type': content_type,
            'content-length': str(contentLength)
        }
        assert get_digest_algorithm_from_headers(headers) == digestAlgorithm
    headers['signature'] = signatureHeader
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, not GETmethod, None,
                               messageBodyJsonStr, False) is False

    os.chdir(base_dir)
    shutil.rmtree(path, ignore_errors=False, onerror=None)


def _test_httpsig(base_dir: str):
    _test_httpsig_base(True, base_dir)
    _test_httpsig_base(False, base_dir)


def _test_cache():
    print('testCache')
    personUrl = "cat@cardboard.box"
    personJson = {
        "id": 123456,
        "test": "This is a test"
    }
    person_cache = {}
    store_person_in_cache(None, personUrl, personJson, person_cache, True)
    result = get_person_from_cache(None, personUrl, person_cache, True)
    assert result['id'] == 123456
    assert result['test'] == 'This is a test'


def _test_threads_function(param: str):
    for i in range(10000):
        time.sleep(2)


def _test_threads():
    print('testThreads')
    thr = \
        thread_with_trace(target=_test_threads_function,
                          args=('test',),
                          daemon=True)
    thr.start()
    assert thr.is_alive() is True
    time.sleep(1)
    thr.kill()
    thr.join()
    assert thr.is_alive() is False


def create_server_alice(path: str, domain: str, port: int,
                        bobAddress: str, federation_list: [],
                        hasFollows: bool, hasPosts: bool,
                        send_threads: []):
    print('Creating test server: Alice on port ' + str(port))
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)
    shared_items_federated_domains = []
    system_language = 'en'
    nickname = 'alice'
    http_prefix = 'http'
    proxy_type = None
    password = 'alicepass'
    max_replies = 64
    domain_max_posts_per_day = 1000
    account_max_posts_per_day = 1000
    allow_deletion = True
    low_bandwidth = True
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(path, nickname, domain, port, http_prefix, True,
                      False, password)
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    assert set_skill_level(path, nickname, domain, 'hacking', 90)
    assert set_role(path, nickname, domain, 'guru')
    if hasFollows:
        follow_person(path, nickname, domain, 'bob', bobAddress,
                      federation_list, False, False)
        add_follower_of_person(path, nickname, domain, 'bob', bobAddress,
                               federation_list, False, False)
    if hasPosts:
        testFollowersOnly = False
        testSaveToFile = True
        client_to_server = False
        testCommentsEnabled = True
        testAttachImageFilename = None
        testMediaType = None
        testImageDescription = None
        testCity = 'London, England'
        testInReplyTo = None
        testInReplyToAtomUri = None
        testSubject = None
        testSchedulePost = False
        testEventDate = None
        testEventTime = None
        testLocation = None
        testIsArticle = False
        conversationId = None
        content_license_url = 'https://creativecommons.org/licenses/by/4.0'
        create_public_post(path, nickname, domain, port, http_prefix,
                           "No wise fish would go anywhere without a porpoise",
                           testFollowersOnly,
                           testSaveToFile,
                           client_to_server,
                           testCommentsEnabled,
                           testAttachImageFilename,
                           testMediaType,
                           testImageDescription, testCity,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "Curiouser and curiouser!",
                           testFollowersOnly,
                           testSaveToFile,
                           client_to_server,
                           testCommentsEnabled,
                           testAttachImageFilename,
                           testMediaType,
                           testImageDescription, testCity,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "In the gardens of memory, in the palace " +
                           "of dreams, that is where you and I shall meet",
                           testFollowersOnly,
                           testSaveToFile,
                           client_to_server,
                           testCommentsEnabled,
                           testAttachImageFilename,
                           testMediaType,
                           testImageDescription, testCity,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
        regenerate_index_for_box(path, nickname, domain, 'outbox')
    global testServerAliceRunning
    testServerAliceRunning = True
    max_mentions = 10
    max_emoji = 10
    onion_domain = None
    i2p_domain = None
    allow_local_network_access = True
    max_newswire_posts = 20
    dormant_months = 3
    send_threads_timeout_mins = 30
    max_followers = 10
    verify_all_signatures = True
    broch_mode = False
    show_node_info_accounts = True
    show_node_info_version = True
    city = 'London, England'
    log_login_failures = False
    user_agents_blocked = []
    max_like_count = 10
    default_reply_interval_hrs = 9999999999
    lists_enabled = ''
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    print('Server running: Alice')
    run_daemon(content_license_url,
               lists_enabled, default_reply_interval_hrs,
               low_bandwidth, max_like_count,
               shared_items_federated_domains,
               user_agents_blocked,
               log_login_failures, city,
               show_node_info_accounts,
               show_node_info_version,
               broch_mode,
               verify_all_signatures,
               send_threads_timeout_mins,
               dormant_months, max_newswire_posts,
               allow_local_network_access,
               2048, False, True, False, False, True, max_followers,
               0, 100, 1024, 5, False,
               0, False, 1, False, False, False,
               5, True, True, 'en', __version__,
               "instance_id", False, path, domain,
               onion_domain, i2p_domain, None, None, port, port,
               http_prefix, federation_list, max_mentions, max_emoji, False,
               proxy_type, max_replies,
               domain_max_posts_per_day, account_max_posts_per_day,
               allow_deletion, True, True, False, send_threads,
               False)


def create_server_bob(path: str, domain: str, port: int,
                      aliceAddress: str, federation_list: [],
                      hasFollows: bool, hasPosts: bool,
                      send_threads: []):
    print('Creating test server: Bob on port ' + str(port))
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)
    shared_items_federated_domains = []
    system_language = 'en'
    nickname = 'bob'
    http_prefix = 'http'
    proxy_type = None
    client_to_server = False
    password = 'bobpass'
    max_replies = 64
    domain_max_posts_per_day = 1000
    account_max_posts_per_day = 1000
    allow_deletion = True
    low_bandwidth = True
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(path, nickname, domain, port, http_prefix, True,
                      False, password)
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    if hasFollows and aliceAddress:
        follow_person(path, nickname, domain,
                      'alice', aliceAddress, federation_list, False, False)
        add_follower_of_person(path, nickname, domain,
                               'alice', aliceAddress, federation_list,
                               False, False)
    if hasPosts:
        testFollowersOnly = False
        testSaveToFile = True
        testCommentsEnabled = True
        testAttachImageFilename = None
        testImageDescription = None
        testMediaType = None
        testCity = 'London, England'
        testInReplyTo = None
        testInReplyToAtomUri = None
        testSubject = None
        testSchedulePost = False
        testEventDate = None
        testEventTime = None
        testLocation = None
        testIsArticle = False
        conversationId = None
        content_license_url = 'https://creativecommons.org/licenses/by/4.0'
        create_public_post(path, nickname, domain, port, http_prefix,
                           "It's your life, live it your way.",
                           testFollowersOnly,
                           testSaveToFile,
                           client_to_server,
                           testCommentsEnabled,
                           testAttachImageFilename,
                           testMediaType,
                           testImageDescription, testCity,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "One of the things I've realised is that " +
                           "I am very simple",
                           testFollowersOnly,
                           testSaveToFile,
                           client_to_server,
                           testCommentsEnabled,
                           testAttachImageFilename,
                           testMediaType,
                           testImageDescription, testCity,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "Quantum physics is a bit of a passion of mine",
                           testFollowersOnly,
                           testSaveToFile,
                           client_to_server,
                           testCommentsEnabled,
                           testAttachImageFilename,
                           testMediaType,
                           testImageDescription, testCity,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
        regenerate_index_for_box(path, nickname, domain, 'outbox')
    global testServerBobRunning
    testServerBobRunning = True
    max_mentions = 10
    max_emoji = 10
    onion_domain = None
    i2p_domain = None
    allow_local_network_access = True
    max_newswire_posts = 20
    dormant_months = 3
    send_threads_timeout_mins = 30
    max_followers = 10
    verify_all_signatures = True
    broch_mode = False
    show_node_info_accounts = True
    show_node_info_version = True
    city = 'London, England'
    log_login_failures = False
    user_agents_blocked = []
    max_like_count = 10
    default_reply_interval_hrs = 9999999999
    lists_enabled = ''
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    print('Server running: Bob')
    run_daemon(content_license_url,
               lists_enabled, default_reply_interval_hrs,
               low_bandwidth, max_like_count,
               shared_items_federated_domains,
               user_agents_blocked,
               log_login_failures, city,
               show_node_info_accounts,
               show_node_info_version,
               broch_mode,
               verify_all_signatures,
               send_threads_timeout_mins,
               dormant_months, max_newswire_posts,
               allow_local_network_access,
               2048, False, True, False, False, True, max_followers,
               0, 100, 1024, 5, False, 0,
               False, 1, False, False, False,
               5, True, True, 'en', __version__,
               "instance_id", False, path, domain,
               onion_domain, i2p_domain, None, None, port, port,
               http_prefix, federation_list, max_mentions, max_emoji, False,
               proxy_type, max_replies,
               domain_max_posts_per_day, account_max_posts_per_day,
               allow_deletion, True, True, False, send_threads,
               False)


def create_server_eve(path: str, domain: str, port: int, federation_list: [],
                      hasFollows: bool, hasPosts: bool,
                      send_threads: []):
    print('Creating test server: Eve on port ' + str(port))
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)
    shared_items_federated_domains = []
    nickname = 'eve'
    http_prefix = 'http'
    proxy_type = None
    password = 'evepass'
    max_replies = 64
    allow_deletion = True
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(path, nickname, domain, port, http_prefix, True,
                      False, password)
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    global testServerEveRunning
    testServerEveRunning = True
    max_mentions = 10
    max_emoji = 10
    onion_domain = None
    i2p_domain = None
    allow_local_network_access = True
    max_newswire_posts = 20
    dormant_months = 3
    send_threads_timeout_mins = 30
    max_followers = 10
    verify_all_signatures = True
    broch_mode = False
    show_node_info_accounts = True
    show_node_info_version = True
    city = 'London, England'
    log_login_failures = False
    user_agents_blocked = []
    max_like_count = 10
    low_bandwidth = True
    default_reply_interval_hrs = 9999999999
    lists_enabled = ''
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    print('Server running: Eve')
    run_daemon(content_license_url,
               lists_enabled, default_reply_interval_hrs,
               low_bandwidth, max_like_count,
               shared_items_federated_domains,
               user_agents_blocked,
               log_login_failures, city,
               show_node_info_accounts,
               show_node_info_version,
               broch_mode,
               verify_all_signatures,
               send_threads_timeout_mins,
               dormant_months, max_newswire_posts,
               allow_local_network_access,
               2048, False, True, False, False, True, max_followers,
               0, 100, 1024, 5, False, 0,
               False, 1, False, False, False,
               5, True, True, 'en', __version__,
               "instance_id", False, path, domain,
               onion_domain, i2p_domain, None, None, port, port,
               http_prefix, federation_list, max_mentions, max_emoji, False,
               proxy_type, max_replies, allow_deletion, True, True, False,
               send_threads, False)


def create_server_group(path: str, domain: str, port: int,
                        federation_list: [],
                        hasFollows: bool, hasPosts: bool,
                        send_threads: []):
    print('Creating test server: Group on port ' + str(port))
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)
    shared_items_federated_domains = []
    # system_language = 'en'
    nickname = 'testgroup'
    http_prefix = 'http'
    proxy_type = None
    password = 'testgrouppass'
    max_replies = 64
    domain_max_posts_per_day = 1000
    account_max_posts_per_day = 1000
    allow_deletion = True
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_group(path, nickname, domain, port, http_prefix, True,
                     password)
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    global testServerGroupRunning
    testServerGroupRunning = True
    max_mentions = 10
    max_emoji = 10
    onion_domain = None
    i2p_domain = None
    allow_local_network_access = True
    max_newswire_posts = 20
    dormant_months = 3
    send_threads_timeout_mins = 30
    max_followers = 10
    verify_all_signatures = True
    broch_mode = False
    show_node_info_accounts = True
    show_node_info_version = True
    city = 'London, England'
    log_login_failures = False
    user_agents_blocked = []
    max_like_count = 10
    low_bandwidth = True
    default_reply_interval_hrs = 9999999999
    lists_enabled = ''
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    print('Server running: Group')
    run_daemon(content_license_url,
               lists_enabled, default_reply_interval_hrs,
               low_bandwidth, max_like_count,
               shared_items_federated_domains,
               user_agents_blocked,
               log_login_failures, city,
               show_node_info_accounts,
               show_node_info_version,
               broch_mode,
               verify_all_signatures,
               send_threads_timeout_mins,
               dormant_months, max_newswire_posts,
               allow_local_network_access,
               2048, False, True, False, False, True, max_followers,
               0, 100, 1024, 5, False,
               0, False, 1, False, False, False,
               5, True, True, 'en', __version__,
               "instance_id", False, path, domain,
               onion_domain, i2p_domain, None, None, port, port,
               http_prefix, federation_list, max_mentions, max_emoji, False,
               proxy_type, max_replies,
               domain_max_posts_per_day, account_max_posts_per_day,
               allow_deletion, True, True, False, send_threads,
               False)


def test_post_message_between_servers(base_dir: str) -> None:
    print('Testing sending message from one server to the inbox of another')

    global testServerAliceRunning
    global testServerBobRunning
    testServerAliceRunning = False
    testServerBobRunning = False

    system_language = 'en'
    http_prefix = 'http'
    proxy_type = None
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    aliceDir = base_dir + '/.tests/alice'
    aliceDomain = '127.0.0.50'
    alicePort = 61935
    aliceAddress = aliceDomain + ':' + str(alicePort)

    bobDir = base_dir + '/.tests/bob'
    bobDomain = '127.0.0.100'
    bobPort = 61936
    federation_list = [bobDomain, aliceDomain]
    aliceSendThreads = []
    bobSendThreads = []
    bobAddress = bobDomain + ':' + str(bobPort)

    global thrAlice
    if thrAlice:
        while thrAlice.is_alive():
            thrAlice.stop()
            time.sleep(1)
        thrAlice.kill()

    thrAlice = \
        thread_with_trace(target=create_server_alice,
                          args=(aliceDir, aliceDomain, alicePort, bobAddress,
                                federation_list, False, False,
                                aliceSendThreads),
                          daemon=True)

    global thrBob
    if thrBob:
        while thrBob.is_alive():
            thrBob.stop()
            time.sleep(1)
        thrBob.kill()

    thrBob = \
        thread_with_trace(target=create_server_bob,
                          args=(bobDir, bobDomain, bobPort, aliceAddress,
                                federation_list, False, False,
                                bobSendThreads),
                          daemon=True)

    thrAlice.start()
    thrBob.start()
    assert thrAlice.is_alive() is True
    assert thrBob.is_alive() is True

    # wait for both servers to be running
    while not (testServerAliceRunning and testServerBobRunning):
        time.sleep(1)

    time.sleep(1)

    print('\n\n*******************************************************')
    print('Alice sends to Bob')
    os.chdir(aliceDir)
    sessionAlice = create_session(proxy_type)
    inReplyTo = None
    inReplyToAtomUri = None
    subject = None
    alicePostLog = []
    followersOnly = False
    saveToFile = True
    client_to_server = False
    ccUrl = None
    alicePersonCache = {}
    aliceCachedWebfingers = {}
    aliceSharedItemsFederatedDomains = []
    aliceSharedItemFederationTokens = {}
    attachedImageFilename = base_dir + '/img/logo.png'
    testImageWidth, testImageHeight = \
        get_image_dimensions(attachedImageFilename)
    assert testImageWidth
    assert testImageHeight
    mediaType = get_attachment_media_type(attachedImageFilename)
    attachedImageDescription = 'Logo'
    isArticle = False
    city = 'London, England'
    # nothing in Alice's outbox
    outboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/outbox'
    assert len([name for name in os.listdir(outboxPath)
                if os.path.isfile(os.path.join(outboxPath, name))]) == 0
    low_bandwidth = False
    signing_priv_key_pem = None
    sendResult = \
        send_post(signing_priv_key_pem, __version__,
                  sessionAlice, aliceDir, 'alice', aliceDomain, alicePort,
                  'bob', bobDomain, bobPort, ccUrl, http_prefix,
                  'Why is a mouse when it spins? ' +
                  'यह एक परीक्षण है #sillyquestion',
                  followersOnly,
                  saveToFile, client_to_server, True,
                  attachedImageFilename, mediaType,
                  attachedImageDescription, city, federation_list,
                  aliceSendThreads, alicePostLog, aliceCachedWebfingers,
                  alicePersonCache, isArticle, system_language,
                  aliceSharedItemsFederatedDomains,
                  aliceSharedItemFederationTokens, low_bandwidth,
                  content_license_url,
                  inReplyTo, inReplyToAtomUri, subject)
    print('sendResult: ' + str(sendResult))

    queuePath = bobDir + '/accounts/bob@' + bobDomain + '/queue'
    inboxPath = bobDir + '/accounts/bob@' + bobDomain + '/inbox'
    mPath = get_media_path()
    mediaPath = aliceDir + '/' + mPath
    for i in range(30):
        if os.path.isdir(inboxPath):
            if len([name for name in os.listdir(inboxPath)
                    if os.path.isfile(os.path.join(inboxPath, name))]) > 0:
                if len([name for name in os.listdir(outboxPath)
                        if os.path.isfile(os.path.join(outboxPath,
                                                       name))]) == 1:
                    if len([name for name in os.listdir(mediaPath)
                            if os.path.isfile(os.path.join(mediaPath,
                                                           name))]) > 0:
                        if len([name for name in os.listdir(queuePath)
                                if os.path.isfile(os.path.join(queuePath,
                                                               name))]) == 0:
                            break
        time.sleep(1)

    # check that a news account exists
    newsActorDir = aliceDir + '/accounts/news@' + aliceDomain
    print("newsActorDir: " + newsActorDir)
    assert os.path.isdir(newsActorDir)
    newsActorFile = newsActorDir + '.json'
    assert os.path.isfile(newsActorFile)
    newsActorJson = load_json(newsActorFile)
    assert newsActorJson
    assert newsActorJson.get("id")
    # check the id of the news actor
    print('News actor Id: ' + newsActorJson["id"])
    assert (newsActorJson["id"] ==
            http_prefix + '://' + aliceAddress + '/users/news')

    # Image attachment created
    assert len([name for name in os.listdir(mediaPath)
                if os.path.isfile(os.path.join(mediaPath, name))]) > 0
    # inbox item created
    assert len([name for name in os.listdir(inboxPath)
                if os.path.isfile(os.path.join(inboxPath, name))]) == 1
    # queue item removed
    testval = len([name for name in os.listdir(queuePath)
                   if os.path.isfile(os.path.join(queuePath, name))])
    print('queuePath: ' + queuePath + ' '+str(testval))
    assert testval == 0
    assert valid_inbox(bobDir, 'bob', bobDomain)
    assert valid_inbox_filenames(bobDir, 'bob', bobDomain,
                                 aliceDomain, alicePort)
    print('Check that message received from Alice contains the expected text')
    for name in os.listdir(inboxPath):
        filename = os.path.join(inboxPath, name)
        assert os.path.isfile(filename)
        receivedJson = load_json(filename, 0)
        if receivedJson:
            pprint(receivedJson['object']['content'])
        assert receivedJson
        assert 'Why is a mouse when it spins?' in \
            receivedJson['object']['content']
        assert 'Why is a mouse when it spins?' in \
            receivedJson['object']['contentMap'][system_language]
        assert 'यह एक परीक्षण है' in receivedJson['object']['content']
        print('Check that message received from Alice contains an attachment')
        assert receivedJson['object']['attachment']
        assert len(receivedJson['object']['attachment']) == 1
        attached = receivedJson['object']['attachment'][0]
        pprint(attached)
        assert attached.get('type')
        assert attached.get('url')
        assert attached['mediaType'] == 'image/png'
        if '/system/media_attachments/files/' not in attached['url']:
            print(attached['url'])
        assert '/system/media_attachments/files/' in attached['url']
        assert attached['url'].endswith('.png')
        assert attached.get('width')
        assert attached.get('height')
        assert attached['width'] > 0
        assert attached['height'] > 0

    print('\n\n*******************************************************')
    print("Bob likes Alice's post")

    aliceDomainStr = aliceDomain + ':' + str(alicePort)
    add_follower_of_person(bobDir, 'bob', bobDomain, 'alice',
                           aliceDomainStr, federation_list, False, False)
    bobDomainStr = bobDomain + ':' + str(bobPort)
    follow_person(aliceDir, 'alice', aliceDomain, 'bob',
                  bobDomainStr, federation_list, False, False)

    sessionBob = create_session(proxy_type)
    bobPostLog = []
    bobPersonCache = {}
    bobCachedWebfingers = {}
    statusNumber = None
    outboxPostFilename = None
    outboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/outbox'
    for name in os.listdir(outboxPath):
        if '#statuses#' in name:
            statusNumber = \
                int(name.split('#statuses#')[1].replace('.json', ''))
            outboxPostFilename = outboxPath + '/' + name
    assert statusNumber > 0
    assert outboxPostFilename
    assert like_post({}, sessionBob, bobDir, federation_list,
                     'bob', bobDomain, bobPort, http_prefix,
                     'alice', aliceDomain, alicePort, [],
                     statusNumber, False, bobSendThreads, bobPostLog,
                     bobPersonCache, bobCachedWebfingers,
                     True, __version__, signing_priv_key_pem)

    for i in range(20):
        if 'likes' in open(outboxPostFilename).read():
            break
        time.sleep(1)

    alicePostJson = load_json(outboxPostFilename, 0)
    if alicePostJson:
        pprint(alicePostJson)

    assert 'likes' in open(outboxPostFilename).read()

    print('\n\n*******************************************************')
    print("Bob reacts to Alice's post")

    assert reaction_post({}, sessionBob, bobDir, federation_list,
                         'bob', bobDomain, bobPort, http_prefix,
                         'alice', aliceDomain, alicePort, [],
                         statusNumber, '😀',
                         False, bobSendThreads, bobPostLog,
                         bobPersonCache, bobCachedWebfingers,
                         True, __version__, signing_priv_key_pem)

    for i in range(20):
        if 'reactions' in open(outboxPostFilename).read():
            break
        time.sleep(1)

    alicePostJson = load_json(outboxPostFilename, 0)
    if alicePostJson:
        pprint(alicePostJson)

    assert 'reactions' in open(outboxPostFilename).read()

    print('\n\n*******************************************************')
    print("Bob repeats Alice's post")
    objectUrl = \
        http_prefix + '://' + aliceDomain + ':' + str(alicePort) + \
        '/users/alice/statuses/' + str(statusNumber)
    inboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/inbox'
    outboxPath = bobDir + '/accounts/bob@' + bobDomain + '/outbox'
    outboxBeforeAnnounceCount = \
        len([name for name in os.listdir(outboxPath)
             if os.path.isfile(os.path.join(outboxPath, name))])
    beforeAnnounceCount = \
        len([name for name in os.listdir(inboxPath)
             if os.path.isfile(os.path.join(inboxPath, name))])
    print('inbox items before announce: ' + str(beforeAnnounceCount))
    print('outbox items before announce: ' + str(outboxBeforeAnnounceCount))
    assert outboxBeforeAnnounceCount == 0
    assert beforeAnnounceCount == 0
    announce_public(sessionBob, bobDir, federation_list,
                    'bob', bobDomain, bobPort, http_prefix,
                    objectUrl,
                    False, bobSendThreads, bobPostLog,
                    bobPersonCache, bobCachedWebfingers,
                    True, __version__, signing_priv_key_pem)
    announceMessageArrived = False
    outboxMessageArrived = False
    for i in range(10):
        time.sleep(1)
        if not os.path.isdir(inboxPath):
            continue
        if len([name for name in os.listdir(outboxPath)
                if os.path.isfile(os.path.join(outboxPath, name))]) > 0:
            outboxMessageArrived = True
            print('Announce created by Bob')
        if len([name for name in os.listdir(inboxPath)
                if os.path.isfile(os.path.join(inboxPath, name))]) > 0:
            announceMessageArrived = True
            print('Announce message sent to Alice!')
        if announceMessageArrived and outboxMessageArrived:
            break
    afterAnnounceCount = \
        len([name for name in os.listdir(inboxPath)
             if os.path.isfile(os.path.join(inboxPath, name))])
    outboxAfterAnnounceCount = \
        len([name for name in os.listdir(outboxPath)
             if os.path.isfile(os.path.join(outboxPath, name))])
    print('inbox items after announce: ' + str(afterAnnounceCount))
    print('outbox items after announce: ' + str(outboxAfterAnnounceCount))
    assert afterAnnounceCount == beforeAnnounceCount+1
    assert outboxAfterAnnounceCount == outboxBeforeAnnounceCount + 1
    # stop the servers
    thrAlice.kill()
    thrAlice.join()
    assert thrAlice.is_alive() is False

    thrBob.kill()
    thrBob.join()
    assert thrBob.is_alive() is False

    os.chdir(base_dir)
    shutil.rmtree(aliceDir, ignore_errors=False, onerror=None)
    shutil.rmtree(bobDir, ignore_errors=False, onerror=None)


def test_follow_between_servers(base_dir: str) -> None:
    print('Testing sending a follow request from one server to another')

    global testServerAliceRunning
    global testServerBobRunning
    testServerAliceRunning = False
    testServerBobRunning = False

    system_language = 'en'
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    aliceDir = base_dir + '/.tests/alice'
    aliceDomain = '127.0.0.47'
    alicePort = 61935
    aliceSendThreads = []
    aliceAddress = aliceDomain + ':' + str(alicePort)

    bobDir = base_dir + '/.tests/bob'
    bobDomain = '127.0.0.79'
    bobPort = 61936
    bobSendThreads = []
    bobAddress = bobDomain + ':' + str(bobPort)

    global thrAlice
    if thrAlice:
        while thrAlice.is_alive():
            thrAlice.stop()
            time.sleep(1)
        thrAlice.kill()

    thrAlice = \
        thread_with_trace(target=create_server_alice,
                          args=(aliceDir, aliceDomain, alicePort, bobAddress,
                                federation_list, False, False,
                                aliceSendThreads),
                          daemon=True)

    global thrBob
    if thrBob:
        while thrBob.is_alive():
            thrBob.stop()
            time.sleep(1)
        thrBob.kill()

    thrBob = \
        thread_with_trace(target=create_server_bob,
                          args=(bobDir, bobDomain, bobPort, aliceAddress,
                                federation_list, False, False,
                                bobSendThreads),
                          daemon=True)

    thrAlice.start()
    thrBob.start()
    assert thrAlice.is_alive() is True
    assert thrBob.is_alive() is True

    # wait for all servers to be running
    ctr = 0
    while not (testServerAliceRunning and testServerBobRunning):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(testServerAliceRunning))
    print('Bob online: ' + str(testServerBobRunning))
    assert ctr <= 60
    time.sleep(1)

    # In the beginning all was calm and there were no follows

    print('*********************************************************')
    print('Alice sends a follow request to Bob')
    os.chdir(aliceDir)
    sessionAlice = create_session(proxy_type)
    inReplyTo = None
    inReplyToAtomUri = None
    subject = None
    alicePostLog = []
    followersOnly = False
    saveToFile = True
    client_to_server = False
    ccUrl = None
    alicePersonCache = {}
    aliceCachedWebfingers = {}
    alicePostLog = []
    bobActor = http_prefix + '://' + bobAddress + '/users/bob'
    signing_priv_key_pem = None
    sendResult = \
        send_follow_request(sessionAlice, aliceDir,
                            'alice', aliceDomain, alicePort, http_prefix,
                            'bob', bobDomain, bobActor,
                            bobPort, http_prefix,
                            client_to_server, federation_list,
                            aliceSendThreads, alicePostLog,
                            aliceCachedWebfingers, alicePersonCache,
                            True, __version__, signing_priv_key_pem)
    print('sendResult: ' + str(sendResult))

    for t in range(16):
        if os.path.isfile(bobDir + '/accounts/bob@' +
                          bobDomain + '/followers.txt'):
            if os.path.isfile(aliceDir + '/accounts/alice@' +
                              aliceDomain + '/following.txt'):
                if os.path.isfile(aliceDir + '/accounts/alice@' +
                                  aliceDomain + '/followingCalendar.txt'):
                    break
        time.sleep(1)

    assert valid_inbox(bobDir, 'bob', bobDomain)
    assert valid_inbox_filenames(bobDir, 'bob', bobDomain,
                                 aliceDomain, alicePort)
    assert 'alice@' + aliceDomain in open(bobDir + '/accounts/bob@' +
                                          bobDomain + '/followers.txt').read()
    assert 'bob@' + bobDomain in open(aliceDir + '/accounts/alice@' +
                                      aliceDomain + '/following.txt').read()
    assert 'bob@' + bobDomain in open(aliceDir + '/accounts/alice@' +
                                      aliceDomain +
                                      '/followingCalendar.txt').read()
    assert not is_group_actor(aliceDir, bobActor, alicePersonCache)
    assert not is_group_account(aliceDir, 'alice', aliceDomain)

    print('\n\n*********************************************************')
    print('Alice sends a message to Bob')
    alicePostLog = []
    alicePersonCache = {}
    aliceCachedWebfingers = {}
    aliceSharedItemsFederatedDomains = []
    aliceSharedItemFederationTokens = {}
    alicePostLog = []
    isArticle = False
    city = 'London, England'
    low_bandwidth = False
    signing_priv_key_pem = None
    sendResult = \
        send_post(signing_priv_key_pem, __version__,
                  sessionAlice, aliceDir, 'alice', aliceDomain, alicePort,
                  'bob', bobDomain, bobPort, ccUrl,
                  http_prefix, 'Alice message', followersOnly, saveToFile,
                  client_to_server, True,
                  None, None, None, city, federation_list,
                  aliceSendThreads, alicePostLog, aliceCachedWebfingers,
                  alicePersonCache, isArticle, system_language,
                  aliceSharedItemsFederatedDomains,
                  aliceSharedItemFederationTokens, low_bandwidth,
                  content_license_url,
                  inReplyTo, inReplyToAtomUri, subject)
    print('sendResult: ' + str(sendResult))

    queuePath = bobDir + '/accounts/bob@' + bobDomain + '/queue'
    inboxPath = bobDir + '/accounts/bob@' + bobDomain + '/inbox'
    aliceMessageArrived = False
    for i in range(20):
        time.sleep(1)
        if os.path.isdir(inboxPath):
            if len([name for name in os.listdir(inboxPath)
                    if os.path.isfile(os.path.join(inboxPath, name))]) > 0:
                aliceMessageArrived = True
                print('Alice message sent to Bob!')
                break

    assert aliceMessageArrived is True
    print('Message from Alice to Bob succeeded')

    # stop the servers
    thrAlice.kill()
    thrAlice.join()
    assert thrAlice.is_alive() is False

    thrBob.kill()
    thrBob.join()
    assert thrBob.is_alive() is False

    # queue item removed
    time.sleep(4)
    assert len([name for name in os.listdir(queuePath)
                if os.path.isfile(os.path.join(queuePath, name))]) == 0

    os.chdir(base_dir)
    shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)


def test_shared_items_federation(base_dir: str) -> None:
    print('Testing federation of shared items between Alice and Bob')

    global testServerAliceRunning
    global testServerBobRunning
    testServerAliceRunning = False
    testServerBobRunning = False

    system_language = 'en'
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    aliceDir = base_dir + '/.tests/alice'
    aliceDomain = '127.0.0.74'
    alicePort = 61917
    aliceSendThreads = []
    aliceAddress = aliceDomain + ':' + str(alicePort)

    bobDir = base_dir + '/.tests/bob'
    bobDomain = '127.0.0.81'
    bobPort = 61983
    bobSendThreads = []
    bobAddress = bobDomain + ':' + str(bobPort)
    bobPassword = 'bobpass'
    bobCachedWebfingers = {}
    bobPersonCache = {}

    global thrAlice
    if thrAlice:
        while thrAlice.is_alive():
            thrAlice.stop()
            time.sleep(1)
        thrAlice.kill()

    thrAlice = \
        thread_with_trace(target=create_server_alice,
                          args=(aliceDir, aliceDomain, alicePort, bobAddress,
                                federation_list, False, False,
                                aliceSendThreads),
                          daemon=True)

    global thrBob
    if thrBob:
        while thrBob.is_alive():
            thrBob.stop()
            time.sleep(1)
        thrBob.kill()

    thrBob = \
        thread_with_trace(target=create_server_bob,
                          args=(bobDir, bobDomain, bobPort, aliceAddress,
                                federation_list, False, False,
                                bobSendThreads),
                          daemon=True)

    thrAlice.start()
    thrBob.start()
    assert thrAlice.is_alive() is True
    assert thrBob.is_alive() is True

    # wait for all servers to be running
    ctr = 0
    while not (testServerAliceRunning and testServerBobRunning):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(testServerAliceRunning))
    print('Bob online: ' + str(testServerBobRunning))
    assert ctr <= 60
    time.sleep(1)

    signing_priv_key_pem = None
    sessionClient = create_session(proxy_type)

    # Get Bob's instance actor
    print('\n\n*********************************************************')
    print("Test Bob's instance actor")
    profileStr = 'https://www.w3.org/ns/activitystreams'
    testHeaders = {
        'host': bobAddress,
        'Accept': 'application/ld+json; profile="' + profileStr + '"'
    }
    bobInstanceActorJson = \
        get_json(signing_priv_key_pem, sessionClient,
                 'http://' + bobAddress + '/@actor', testHeaders, {}, True,
                 __version__, 'http', 'somedomain.or.other', 10, True)
    assert bobInstanceActorJson
    pprint(bobInstanceActorJson)
    assert bobInstanceActorJson['name'] == 'ACTOR'

    # In the beginning all was calm and there were no follows

    print('\n\n*********************************************************')
    print("Alice and Bob agree to share items catalogs")
    assert os.path.isdir(aliceDir)
    assert os.path.isdir(bobDir)
    set_config_param(aliceDir, 'sharedItemsFederatedDomains', bobAddress)
    set_config_param(bobDir, 'sharedItemsFederatedDomains', aliceAddress)

    print('*********************************************************')
    print('Alice sends a follow request to Bob')
    os.chdir(aliceDir)
    sessionAlice = create_session(proxy_type)
    inReplyTo = None
    inReplyToAtomUri = None
    subject = None
    alicePostLog = []
    followersOnly = False
    saveToFile = True
    client_to_server = False
    ccUrl = None
    alicePersonCache = {}
    aliceCachedWebfingers = {}
    alicePostLog = []
    bobActor = http_prefix + '://' + bobAddress + '/users/bob'
    sendResult = \
        send_follow_request(sessionAlice, aliceDir,
                            'alice', aliceDomain, alicePort, http_prefix,
                            'bob', bobDomain, bobActor,
                            bobPort, http_prefix,
                            client_to_server, federation_list,
                            aliceSendThreads, alicePostLog,
                            aliceCachedWebfingers, alicePersonCache,
                            True, __version__, signing_priv_key_pem)
    print('sendResult: ' + str(sendResult))

    for t in range(16):
        if os.path.isfile(bobDir + '/accounts/bob@' +
                          bobDomain + '/followers.txt'):
            if os.path.isfile(aliceDir + '/accounts/alice@' +
                              aliceDomain + '/following.txt'):
                if os.path.isfile(aliceDir + '/accounts/alice@' +
                                  aliceDomain + '/followingCalendar.txt'):
                    break
        time.sleep(1)

    assert valid_inbox(bobDir, 'bob', bobDomain)
    assert valid_inbox_filenames(bobDir, 'bob', bobDomain,
                                 aliceDomain, alicePort)
    assert 'alice@' + aliceDomain in open(bobDir + '/accounts/bob@' +
                                          bobDomain + '/followers.txt').read()
    assert 'bob@' + bobDomain in open(aliceDir + '/accounts/alice@' +
                                      aliceDomain + '/following.txt').read()
    assert 'bob@' + bobDomain in open(aliceDir + '/accounts/alice@' +
                                      aliceDomain +
                                      '/followingCalendar.txt').read()
    assert not is_group_actor(aliceDir, bobActor, alicePersonCache)
    assert not is_group_account(bobDir, 'bob', bobDomain)

    print('\n\n*********************************************************')
    print('Bob publishes some shared items')
    if os.path.isdir(bobDir + '/ontology'):
        shutil.rmtree(bobDir + '/ontology', ignore_errors=False, onerror=None)
    os.mkdir(bobDir + '/ontology')
    copyfile(base_dir + '/img/logo.png', bobDir + '/logo.png')
    copyfile(base_dir + '/ontology/foodTypes.json',
             bobDir + '/ontology/foodTypes.json')
    copyfile(base_dir + '/ontology/toolTypes.json',
             bobDir + '/ontology/toolTypes.json')
    copyfile(base_dir + '/ontology/clothesTypes.json',
             bobDir + '/ontology/clothesTypes.json')
    copyfile(base_dir + '/ontology/medicalTypes.json',
             bobDir + '/ontology/medicalTypes.json')
    copyfile(base_dir + '/ontology/accommodationTypes.json',
             bobDir + '/ontology/accommodationTypes.json')
    assert os.path.isfile(bobDir + '/logo.png')
    assert os.path.isfile(bobDir + '/ontology/foodTypes.json')
    assert os.path.isfile(bobDir + '/ontology/toolTypes.json')
    assert os.path.isfile(bobDir + '/ontology/clothesTypes.json')
    assert os.path.isfile(bobDir + '/ontology/medicalTypes.json')
    assert os.path.isfile(bobDir + '/ontology/accommodationTypes.json')
    sharedItemName = 'cheddar'
    sharedItemDescription = 'Some cheese'
    sharedItemImageFilename = 'logo.png'
    sharedItemQty = 1
    sharedItemType = 'Cheese'
    sharedItemCategory = 'Food'
    sharedItemLocation = "Bob's location"
    sharedItemDuration = "10 days"
    sharedItemPrice = "1.30"
    sharedItemCurrency = "EUR"
    signing_priv_key_pem = None
    sessionBob = create_session(proxy_type)
    shareJson = \
        send_share_via_server(bobDir, sessionBob,
                              'bob', bobPassword,
                              bobDomain, bobPort,
                              http_prefix, sharedItemName,
                              sharedItemDescription, sharedItemImageFilename,
                              sharedItemQty, sharedItemType,
                              sharedItemCategory,
                              sharedItemLocation, sharedItemDuration,
                              bobCachedWebfingers, bobPersonCache,
                              True, __version__,
                              sharedItemPrice, sharedItemCurrency,
                              signing_priv_key_pem)
    assert shareJson
    assert isinstance(shareJson, dict)
    sharedItemName = 'Epicyon T-shirt'
    sharedItemDescription = 'A fashionable item'
    sharedItemImageFilename = 'logo.png'
    sharedItemQty = 1
    sharedItemType = 'T-Shirt'
    sharedItemCategory = 'Clothes'
    sharedItemLocation = "Bob's location"
    sharedItemDuration = "5 days"
    sharedItemPrice = "0"
    sharedItemCurrency = "EUR"
    shareJson = \
        send_share_via_server(bobDir, sessionBob,
                              'bob', bobPassword,
                              bobDomain, bobPort,
                              http_prefix, sharedItemName,
                              sharedItemDescription, sharedItemImageFilename,
                              sharedItemQty, sharedItemType,
                              sharedItemCategory,
                              sharedItemLocation, sharedItemDuration,
                              bobCachedWebfingers, bobPersonCache,
                              True, __version__,
                              sharedItemPrice, sharedItemCurrency,
                              signing_priv_key_pem)
    assert shareJson
    assert isinstance(shareJson, dict)
    sharedItemName = 'Soldering iron'
    sharedItemDescription = 'A soldering iron'
    sharedItemImageFilename = 'logo.png'
    sharedItemQty = 1
    sharedItemType = 'Soldering iron'
    sharedItemCategory = 'Tools'
    sharedItemLocation = "Bob's location"
    sharedItemDuration = "9 days"
    sharedItemPrice = "10.00"
    sharedItemCurrency = "EUR"
    shareJson = \
        send_share_via_server(bobDir, sessionBob,
                              'bob', bobPassword,
                              bobDomain, bobPort,
                              http_prefix, sharedItemName,
                              sharedItemDescription, sharedItemImageFilename,
                              sharedItemQty, sharedItemType,
                              sharedItemCategory,
                              sharedItemLocation, sharedItemDuration,
                              bobCachedWebfingers, bobPersonCache,
                              True, __version__,
                              sharedItemPrice, sharedItemCurrency,
                              signing_priv_key_pem)
    assert shareJson
    assert isinstance(shareJson, dict)

    time.sleep(2)
    print('\n\n*********************************************************')
    print('Bob has a shares.json file containing the uploaded items')

    sharesFilename = bobDir + '/accounts/bob@' + bobDomain + '/shares.json'
    assert os.path.isfile(sharesFilename)
    sharesJson = load_json(sharesFilename)
    assert sharesJson
    pprint(sharesJson)
    assert len(sharesJson.items()) == 3
    for itemID, item in sharesJson.items():
        if not item.get('dfcId'):
            pprint(item)
            print(itemID + ' does not have dfcId field')
        assert item.get('dfcId')

    print('\n\n*********************************************************')
    print('Bob can read the shared items catalog on his own instance')
    signing_priv_key_pem = None
    catalogJson = \
        get_shared_items_catalog_via_server(bobDir, sessionBob,
                                            'bob', bobPassword,
                                            bobDomain, bobPort,
                                            http_prefix, True,
                                            signing_priv_key_pem)
    assert catalogJson
    pprint(catalogJson)
    assert 'DFC:supplies' in catalogJson
    assert len(catalogJson.get('DFC:supplies')) == 3

    print('\n\n*********************************************************')
    print('Alice sends a message to Bob')
    aliceTokensFilename = \
        aliceDir + '/accounts/sharedItemsFederationTokens.json'
    assert os.path.isfile(aliceTokensFilename)
    aliceSharedItemFederationTokens = load_json(aliceTokensFilename)
    assert aliceSharedItemFederationTokens
    print('Alice shared item federation tokens:')
    pprint(aliceSharedItemFederationTokens)
    assert len(aliceSharedItemFederationTokens.items()) > 0
    for hostStr, token in aliceSharedItemFederationTokens.items():
        assert ':' in hostStr
    alicePostLog = []
    alicePersonCache = {}
    aliceCachedWebfingers = {}
    aliceSharedItemsFederatedDomains = [bobAddress]
    alicePostLog = []
    isArticle = False
    city = 'London, England'
    low_bandwidth = False
    signing_priv_key_pem = None
    sendResult = \
        send_post(signing_priv_key_pem, __version__,
                  sessionAlice, aliceDir, 'alice', aliceDomain, alicePort,
                  'bob', bobDomain, bobPort, ccUrl,
                  http_prefix, 'Alice message', followersOnly, saveToFile,
                  client_to_server, True,
                  None, None, None, city, federation_list,
                  aliceSendThreads, alicePostLog, aliceCachedWebfingers,
                  alicePersonCache, isArticle, system_language,
                  aliceSharedItemsFederatedDomains,
                  aliceSharedItemFederationTokens, low_bandwidth,
                  content_license_url, True,
                  inReplyTo, inReplyToAtomUri, subject)
    print('sendResult: ' + str(sendResult))

    queuePath = bobDir + '/accounts/bob@' + bobDomain + '/queue'
    inboxPath = bobDir + '/accounts/bob@' + bobDomain + '/inbox'
    aliceMessageArrived = False
    for i in range(20):
        time.sleep(1)
        if os.path.isdir(inboxPath):
            if len([name for name in os.listdir(inboxPath)
                    if os.path.isfile(os.path.join(inboxPath, name))]) > 0:
                aliceMessageArrived = True
                print('Alice message sent to Bob!')
                break

    assert aliceMessageArrived is True
    print('Message from Alice to Bob succeeded')

    print('\n\n*********************************************************')
    print('Check that Alice received the shared items authorization')
    print('token from Bob')
    aliceTokensFilename = \
        aliceDir + '/accounts/sharedItemsFederationTokens.json'
    bobTokensFilename = \
        bobDir + '/accounts/sharedItemsFederationTokens.json'
    assert os.path.isfile(aliceTokensFilename)
    assert os.path.isfile(bobTokensFilename)
    aliceTokens = load_json(aliceTokensFilename)
    assert aliceTokens
    for hostStr, token in aliceTokens.items():
        assert ':' in hostStr
    assert aliceTokens.get(aliceAddress)
    print('Alice tokens')
    pprint(aliceTokens)
    bobTokens = load_json(bobTokensFilename)
    assert bobTokens
    for hostStr, token in bobTokens.items():
        assert ':' in hostStr
    assert bobTokens.get(bobAddress)
    print("Check that Bob now has Alice's token")
    assert bobTokens.get(aliceAddress)
    print('Bob tokens')
    pprint(bobTokens)

    print('\n\n*********************************************************')
    print('Alice can read the federated shared items catalog of Bob')
    headers = {
        'Origin': aliceAddress,
        'Authorization': bobTokens[bobAddress],
        'host': bobAddress,
        'Accept': 'application/json'
    }
    url = http_prefix + '://' + bobAddress + '/catalog'
    signing_priv_key_pem = None
    catalogJson = get_json(signing_priv_key_pem, sessionAlice, url, headers,
                           None, True)
    assert catalogJson
    pprint(catalogJson)
    assert 'DFC:supplies' in catalogJson
    assert len(catalogJson.get('DFC:supplies')) == 3

    # queue item removed
    ctr = 0
    while len([name for name in os.listdir(queuePath)
               if os.path.isfile(os.path.join(queuePath, name))]) > 0:
        ctr += 1
        if ctr > 10:
            break
        time.sleep(1)

#    assert len([name for name in os.listdir(queuePath)
#                if os.path.isfile(os.path.join(queuePath, name))]) == 0

    # stop the servers
    thrAlice.kill()
    thrAlice.join()
    assert thrAlice.is_alive() is False

    thrBob.kill()
    thrBob.join()
    assert thrBob.is_alive() is False

    os.chdir(base_dir)
    shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    print('Testing federation of shared items between ' +
          'Alice and Bob is complete')


def test_group_follow(base_dir: str) -> None:
    print('Testing following of a group')

    global testServerAliceRunning
    global testServerBobRunning
    global testServerGroupRunning
    system_language = 'en'
    testServerAliceRunning = False
    testServerBobRunning = False
    testServerGroupRunning = False

    # system_language = 'en'
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    aliceDir = base_dir + '/.tests/alice'
    aliceDomain = '127.0.0.57'
    alicePort = 61927
    aliceSendThreads = []
    aliceAddress = aliceDomain + ':' + str(alicePort)

    bobDir = base_dir + '/.tests/bob'
    bobDomain = '127.0.0.59'
    bobPort = 61814
    bobSendThreads = []
    # bobAddress = bobDomain + ':' + str(bobPort)

    testgroupDir = base_dir + '/.tests/testgroup'
    testgroupDomain = '127.0.0.63'
    testgroupPort = 61925
    testgroupSendThreads = []
    testgroupAddress = testgroupDomain + ':' + str(testgroupPort)

    global thrAlice
    if thrAlice:
        while thrAlice.is_alive():
            thrAlice.stop()
            time.sleep(1)
        thrAlice.kill()

    thrAlice = \
        thread_with_trace(target=create_server_alice,
                          args=(aliceDir, aliceDomain, alicePort,
                                testgroupAddress,
                                federation_list, False, True,
                                aliceSendThreads),
                          daemon=True)

    global thrBob
    if thrBob:
        while thrBob.is_alive():
            thrBob.stop()
            time.sleep(1)
        thrBob.kill()

    thrBob = \
        thread_with_trace(target=create_server_bob,
                          args=(bobDir, bobDomain, bobPort, None,
                                federation_list, False, False,
                                bobSendThreads),
                          daemon=True)

    global thrGroup
    if thrGroup:
        while thrGroup.is_alive():
            thrGroup.stop()
            time.sleep(1)
        thrGroup.kill()

    thrGroup = \
        thread_with_trace(target=create_server_group,
                          args=(testgroupDir, testgroupDomain, testgroupPort,
                                federation_list, False, False,
                                testgroupSendThreads),
                          daemon=True)

    thrAlice.start()
    thrBob.start()
    thrGroup.start()
    assert thrAlice.is_alive() is True
    assert thrBob.is_alive() is True
    assert thrGroup.is_alive() is True

    # wait for all servers to be running
    ctr = 0
    while not (testServerAliceRunning and
               testServerBobRunning and
               testServerGroupRunning):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(testServerAliceRunning))
    print('Bob online: ' + str(testServerBobRunning))
    print('Test Group online: ' + str(testServerGroupRunning))
    assert ctr <= 60
    time.sleep(1)

    print('*********************************************************')
    print('Alice has some outbox posts')
    aliceOutbox = 'http://' + aliceAddress + '/users/alice/outbox'
    session = create_session(None)
    profileStr = 'https://www.w3.org/ns/activitystreams'
    asHeader = {
        'Accept': 'application/ld+json; profile="' + profileStr + '"'
    }
    signing_priv_key_pem = None
    outboxJson = get_json(signing_priv_key_pem, session, aliceOutbox, asHeader,
                          None, True, __version__, 'http', None)
    assert outboxJson
    pprint(outboxJson)
    assert outboxJson['type'] == 'OrderedCollection'
    assert 'first' in outboxJson
    firstPage = outboxJson['first']
    assert 'totalItems' in outboxJson
    print('Alice outbox totalItems: ' + str(outboxJson['totalItems']))
    assert outboxJson['totalItems'] == 3

    outboxJson = get_json(signing_priv_key_pem, session, firstPage, asHeader,
                          None, True, __version__, 'http', None)
    assert outboxJson
    pprint(outboxJson)
    assert 'orderedItems' in outboxJson
    assert outboxJson['type'] == 'OrderedCollectionPage'
    print('Alice outbox orderedItems: ' +
          str(len(outboxJson['orderedItems'])))
    assert len(outboxJson['orderedItems']) == 3

    queuePath = \
        testgroupDir + '/accounts/testgroup@' + testgroupDomain + '/queue'

    # In the beginning the test group had no followers

    print('*********************************************************')
    print('Alice sends a follow request to the test group')
    os.chdir(aliceDir)
    sessionAlice = create_session(proxy_type)
    inReplyTo = None
    inReplyToAtomUri = None
    subject = None
    alicePostLog = []
    followersOnly = False
    saveToFile = True
    client_to_server = False
    ccUrl = None
    alicePersonCache = {}
    aliceCachedWebfingers = {}
    alicePostLog = []
    # aliceActor = http_prefix + '://' + aliceAddress + '/users/alice'
    testgroupActor = \
        http_prefix + '://' + testgroupAddress + '/users/testgroup'
    signing_priv_key_pem = None
    sendResult = \
        send_follow_request(sessionAlice, aliceDir,
                            'alice', aliceDomain, alicePort, http_prefix,
                            'testgroup', testgroupDomain, testgroupActor,
                            testgroupPort, http_prefix,
                            client_to_server, federation_list,
                            aliceSendThreads, alicePostLog,
                            aliceCachedWebfingers, alicePersonCache,
                            True, __version__, signing_priv_key_pem)
    print('sendResult: ' + str(sendResult))

    aliceFollowingFilename = \
        aliceDir + '/accounts/alice@' + aliceDomain + '/following.txt'
    aliceFollowingCalendarFilename = \
        aliceDir + '/accounts/alice@' + aliceDomain + \
        '/followingCalendar.txt'
    testgroupFollowersFilename = \
        testgroupDir + '/accounts/testgroup@' + testgroupDomain + \
        '/followers.txt'

    for t in range(16):
        if os.path.isfile(testgroupFollowersFilename):
            if os.path.isfile(aliceFollowingFilename):
                if os.path.isfile(aliceFollowingCalendarFilename):
                    break
        time.sleep(1)

    assert valid_inbox(testgroupDir, 'testgroup', testgroupDomain)
    assert valid_inbox_filenames(testgroupDir, 'testgroup', testgroupDomain,
                                 aliceDomain, alicePort)
    assert 'alice@' + aliceDomain in open(testgroupFollowersFilename).read()
    assert '!alice@' + aliceDomain not in \
        open(testgroupFollowersFilename).read()

    testgroupWebfingerFilename = \
        testgroupDir + '/wfendpoints/testgroup@' + \
        testgroupDomain + ':' + str(testgroupPort) + '.json'
    assert os.path.isfile(testgroupWebfingerFilename)
    assert 'acct:testgroup@' in open(testgroupWebfingerFilename).read()
    print('acct: exists within the webfinger endpoint for testgroup')

    testgroupHandle = 'testgroup@' + testgroupDomain
    followingStr = ''
    with open(aliceFollowingFilename, 'r') as fp:
        followingStr = fp.read()
        print('Alice following.txt:\n\n' + followingStr)
    if '!testgroup' not in followingStr:
        print('Alice following.txt does not contain !testgroup@' +
              testgroupDomain + ':' + str(testgroupPort))
    assert is_group_actor(aliceDir, testgroupActor, alicePersonCache)
    assert not is_group_account(aliceDir, 'alice', aliceDomain)
    assert is_group_account(testgroupDir, 'testgroup', testgroupDomain)
    assert '!testgroup' in followingStr
    assert testgroupHandle in open(aliceFollowingFilename).read()
    assert testgroupHandle in open(aliceFollowingCalendarFilename).read()
    print('\n\n*********************************************************')
    print('Alice follows the test group')

    print('*********************************************************')
    print('Bob sends a follow request to the test group')
    os.chdir(bobDir)
    sessionBob = create_session(proxy_type)
    inReplyTo = None
    inReplyToAtomUri = None
    subject = None
    bobPostLog = []
    followersOnly = False
    saveToFile = True
    client_to_server = False
    ccUrl = None
    bobPersonCache = {}
    bobCachedWebfingers = {}
    bobPostLog = []
    # bobActor = http_prefix + '://' + bobAddress + '/users/bob'
    testgroupActor = \
        http_prefix + '://' + testgroupAddress + '/users/testgroup'
    signing_priv_key_pem = None
    sendResult = \
        send_follow_request(sessionBob, bobDir,
                            'bob', bobDomain, bobPort, http_prefix,
                            'testgroup', testgroupDomain, testgroupActor,
                            testgroupPort, http_prefix,
                            client_to_server, federation_list,
                            bobSendThreads, bobPostLog,
                            bobCachedWebfingers, bobPersonCache,
                            True, __version__, signing_priv_key_pem)
    print('sendResult: ' + str(sendResult))

    bobFollowingFilename = \
        bobDir + '/accounts/bob@' + bobDomain + '/following.txt'
    bobFollowingCalendarFilename = \
        bobDir + '/accounts/bob@' + bobDomain + \
        '/followingCalendar.txt'
    testgroupFollowersFilename = \
        testgroupDir + '/accounts/testgroup@' + testgroupDomain + \
        '/followers.txt'

    for t in range(16):
        if os.path.isfile(testgroupFollowersFilename):
            if os.path.isfile(bobFollowingFilename):
                if os.path.isfile(bobFollowingCalendarFilename):
                    break
        time.sleep(1)

    assert valid_inbox(testgroupDir, 'testgroup', testgroupDomain)
    assert valid_inbox_filenames(testgroupDir, 'testgroup', testgroupDomain,
                                 bobDomain, bobPort)
    assert 'bob@' + bobDomain in open(testgroupFollowersFilename).read()
    assert '!bob@' + bobDomain not in open(testgroupFollowersFilename).read()

    testgroupWebfingerFilename = \
        testgroupDir + '/wfendpoints/testgroup@' + \
        testgroupDomain + ':' + str(testgroupPort) + '.json'
    assert os.path.isfile(testgroupWebfingerFilename)
    assert 'acct:testgroup@' in open(testgroupWebfingerFilename).read()
    print('acct: exists within the webfinger endpoint for testgroup')

    testgroupHandle = 'testgroup@' + testgroupDomain
    followingStr = ''
    with open(bobFollowingFilename, 'r') as fp:
        followingStr = fp.read()
        print('Bob following.txt:\n\n' + followingStr)
    if '!testgroup' not in followingStr:
        print('Bob following.txt does not contain !testgroup@' +
              testgroupDomain + ':' + str(testgroupPort))
    assert is_group_actor(bobDir, testgroupActor, bobPersonCache)
    assert '!testgroup' in followingStr
    assert testgroupHandle in open(bobFollowingFilename).read()
    assert testgroupHandle in open(bobFollowingCalendarFilename).read()
    print('Bob follows the test group')

    print('\n\n*********************************************************')
    print('Alice posts to the test group')
    inboxPathBob = \
        bobDir + '/accounts/bob@' + bobDomain + '/inbox'
    startPostsBob = \
        len([name for name in os.listdir(inboxPathBob)
             if os.path.isfile(os.path.join(inboxPathBob, name))])
    assert startPostsBob == 0
    alicePostLog = []
    alicePersonCache = {}
    aliceCachedWebfingers = {}
    aliceSharedItemsFederatedDomains = []
    aliceSharedItemFederationTokens = {}
    alicePostLog = []
    isArticle = False
    city = 'London, England'
    low_bandwidth = False
    signing_priv_key_pem = None

    queuePath = \
        testgroupDir + '/accounts/testgroup@' + testgroupDomain + '/queue'
    inboxPath = \
        testgroupDir + '/accounts/testgroup@' + testgroupDomain + '/inbox'
    outboxPath = \
        testgroupDir + '/accounts/testgroup@' + testgroupDomain + '/outbox'
    aliceMessageArrived = False
    startPostsInbox = \
        len([name for name in os.listdir(inboxPath)
             if os.path.isfile(os.path.join(inboxPath, name))])
    startPostsOutbox = \
        len([name for name in os.listdir(outboxPath)
             if os.path.isfile(os.path.join(outboxPath, name))])

    sendResult = \
        send_post(signing_priv_key_pem, __version__,
                  sessionAlice, aliceDir, 'alice', aliceDomain, alicePort,
                  'testgroup', testgroupDomain, testgroupPort, ccUrl,
                  http_prefix, "Alice group message", followersOnly,
                  saveToFile, client_to_server, True,
                  None, None, None, city, federation_list,
                  aliceSendThreads, alicePostLog, aliceCachedWebfingers,
                  alicePersonCache, isArticle, system_language,
                  aliceSharedItemsFederatedDomains,
                  aliceSharedItemFederationTokens, low_bandwidth,
                  content_license_url,
                  inReplyTo, inReplyToAtomUri, subject)
    print('sendResult: ' + str(sendResult))

    for i in range(20):
        time.sleep(1)
        if os.path.isdir(inboxPath):
            currPostsInbox = \
                len([name for name in os.listdir(inboxPath)
                     if os.path.isfile(os.path.join(inboxPath, name))])
            currPostsOutbox = \
                len([name for name in os.listdir(outboxPath)
                     if os.path.isfile(os.path.join(outboxPath, name))])
            if currPostsInbox > startPostsInbox and \
               currPostsOutbox > startPostsOutbox:
                aliceMessageArrived = True
                print('Alice post sent to test group!')
                break

    assert aliceMessageArrived is True
    print('\n\n*********************************************************')
    print('Post from Alice to test group succeeded')

    print('\n\n*********************************************************')
    print('Check that post was relayed from test group to bob')

    bobMessageArrived = False
    for i in range(20):
        time.sleep(1)
        if os.path.isdir(inboxPathBob):
            currPostsBob = \
                len([name for name in os.listdir(inboxPathBob)
                     if os.path.isfile(os.path.join(inboxPathBob, name))])
            if currPostsBob > startPostsBob:
                bobMessageArrived = True
                print('Bob received relayed group post!')
                break

    assert bobMessageArrived is True

    # check that the received post has an id from the group,
    # not from the original sender (alice)
    groupIdChecked = False
    for name in os.listdir(inboxPathBob):
        filename = os.path.join(inboxPathBob, name)
        if os.path.isfile(filename):
            receivedJson = load_json(filename)
            assert receivedJson
            print('Received group post ' + receivedJson['id'])
            assert '/testgroup/statuses/' in receivedJson['id']
            groupIdChecked = True
            break
    assert groupIdChecked

    # stop the servers
    thrAlice.kill()
    thrAlice.join()
    assert thrAlice.is_alive() is False

    thrBob.kill()
    thrBob.join()
    assert thrBob.is_alive() is False

    thrGroup.kill()
    thrGroup.join()
    assert thrGroup.is_alive() is False

    # queue item removed
    time.sleep(4)
    assert len([name for name in os.listdir(queuePath)
                if os.path.isfile(os.path.join(queuePath, name))]) == 0

    os.chdir(base_dir)
    shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    print('Testing following of a group is complete')


def _test_followers_of_person(base_dir: str) -> None:
    print('testFollowersOfPerson')
    currDir = base_dir
    nickname = 'mxpop'
    domain = 'diva.domain'
    password = 'birb'
    port = 80
    http_prefix = 'https'
    federation_list = []
    base_dir = currDir + '/.tests_followersofperson'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)
    create_person(base_dir, nickname, domain, port,
                  http_prefix, True, False, password)
    create_person(base_dir, 'maxboardroom', domain, port,
                  http_prefix, True, False, password)
    create_person(base_dir, 'ultrapancake', domain, port,
                  http_prefix, True, False, password)
    create_person(base_dir, 'drokk', domain, port,
                  http_prefix, True, False, password)
    create_person(base_dir, 'sausagedog', domain, port,
                  http_prefix, True, False, password)

    clear_follows(base_dir, nickname, domain)
    follow_person(base_dir, nickname, domain, 'maxboardroom', domain,
                  federation_list, False, False)
    follow_person(base_dir, 'drokk', domain, 'ultrapancake', domain,
                  federation_list, False, False)
    # deliberate duplication
    follow_person(base_dir, 'drokk', domain, 'ultrapancake', domain,
                  federation_list, False, False)
    follow_person(base_dir, 'sausagedog', domain, 'ultrapancake', domain,
                  federation_list, False, False)
    follow_person(base_dir, nickname, domain, 'ultrapancake', domain,
                  federation_list, False, False)
    follow_person(base_dir, nickname, domain, 'someother', 'randodomain.net',
                  federation_list, False, False)

    followList = get_followers_of_person(base_dir, 'ultrapancake', domain)
    assert len(followList) == 3
    assert 'mxpop@' + domain in followList
    assert 'drokk@' + domain in followList
    assert 'sausagedog@' + domain in followList
    os.chdir(currDir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_followers_on_domain(base_dir: str) -> None:
    print('testNoOfFollowersOnDomain')
    currDir = base_dir
    nickname = 'mxpop'
    domain = 'diva.domain'
    otherdomain = 'soup.dragon'
    password = 'birb'
    port = 80
    http_prefix = 'https'
    federation_list = []
    base_dir = currDir + '/.tests_nooffollowersOndomain'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)
    create_person(base_dir, nickname, domain, port, http_prefix, True,
                  False, password)
    create_person(base_dir, 'maxboardroom', otherdomain, port,
                  http_prefix, True, False, password)
    create_person(base_dir, 'ultrapancake', otherdomain, port,
                  http_prefix, True, False, password)
    create_person(base_dir, 'drokk', otherdomain, port,
                  http_prefix, True, False, password)
    create_person(base_dir, 'sausagedog', otherdomain, port,
                  http_prefix, True, False, password)

    follow_person(base_dir, 'drokk', otherdomain, nickname, domain,
                  federation_list, False, False)
    follow_person(base_dir, 'sausagedog', otherdomain, nickname, domain,
                  federation_list, False, False)
    follow_person(base_dir, 'maxboardroom', otherdomain, nickname, domain,
                  federation_list, False, False)

    add_follower_of_person(base_dir, nickname, domain,
                           'cucumber', 'sandwiches.party',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'captainsensible', 'damned.zone',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'pilchard', 'zombies.attack',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain, 'drokk', otherdomain,
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'sausagedog', otherdomain,
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'maxboardroom', otherdomain,
                           federation_list, False, False)

    followersOnOtherDomain = \
        no_of_followers_on_domain(base_dir,
                                  nickname + '@' + domain, otherdomain)
    assert followersOnOtherDomain == 3

    unfollower_of_account(base_dir, nickname, domain, 'sausagedog',
                          otherdomain, False, False)
    followersOnOtherDomain = \
        no_of_followers_on_domain(base_dir,
                                  nickname + '@' + domain, otherdomain)
    assert followersOnOtherDomain == 2

    os.chdir(currDir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_group_followers(base_dir: str) -> None:
    print('test_group_followers')

    currDir = base_dir
    nickname = 'test735'
    domain = 'mydomain.com'
    password = 'somepass'
    port = 80
    http_prefix = 'https'
    federation_list = []
    base_dir = currDir + '/.tests_testgroupfollowers'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)
    create_person(base_dir, nickname, domain, port, http_prefix, True,
                  False, password)

    clear_followers(base_dir, nickname, domain)
    add_follower_of_person(base_dir, nickname, domain, 'badger', 'wild.domain',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'squirrel', 'wild.domain',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain, 'rodent', 'wild.domain',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'utterly', 'clutterly.domain',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain, 'zonked', 'zzz.domain',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain, 'nap', 'zzz.domain',
                           federation_list, False, False)

    grouped = group_followers_by_domain(base_dir, nickname, domain)
    assert len(grouped.items()) == 3
    assert grouped.get('zzz.domain')
    assert grouped.get('clutterly.domain')
    assert grouped.get('wild.domain')
    assert len(grouped['zzz.domain']) == 2
    assert len(grouped['wild.domain']) == 3
    assert len(grouped['clutterly.domain']) == 1

    os.chdir(currDir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_follows(base_dir: str) -> None:
    print('testFollows')
    currDir = base_dir
    nickname = 'test529'
    domain = 'testdomain.com'
    password = 'mypass'
    port = 80
    http_prefix = 'https'
    federation_list = ['wild.com', 'mesh.com']
    base_dir = currDir + '/.tests_testfollows'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)
    create_person(base_dir, nickname, domain, port, http_prefix, True,
                  False, password)

    clear_follows(base_dir, nickname, domain)
    follow_person(base_dir, nickname, domain, 'badger', 'wild.com',
                  federation_list, False, False)
    follow_person(base_dir, nickname, domain, 'squirrel', 'secret.com',
                  federation_list, False, False)
    follow_person(base_dir, nickname, domain, 'rodent', 'drainpipe.com',
                  federation_list, False, False)
    follow_person(base_dir, nickname, domain, 'batman', 'mesh.com',
                  federation_list, False, False)
    follow_person(base_dir, nickname, domain, 'giraffe', 'trees.com',
                  federation_list, False, False)

    accountDir = acct_dir(base_dir, nickname, domain)
    f = open(accountDir + '/following.txt', 'r')
    domainFound = False
    for followingDomain in f:
        testDomain = followingDomain.split('@')[1]
        testDomain = testDomain.replace('\n', '').replace('\r', '')
        if testDomain == 'mesh.com':
            domainFound = True
        if testDomain not in federation_list:
            print(testDomain)
            assert(False)

    assert(domainFound)
    unfollow_account(base_dir, nickname, domain, 'batman', 'mesh.com',
                     True, False)

    domainFound = False
    for followingDomain in f:
        testDomain = followingDomain.split('@')[1]
        testDomain = testDomain.replace('\n', '').replace('\r', '')
        if testDomain == 'mesh.com':
            domainFound = True
    assert(domainFound is False)

    clear_followers(base_dir, nickname, domain)
    add_follower_of_person(base_dir, nickname, domain, 'badger', 'wild.com',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'squirrel', 'secret.com',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain,
                           'rodent', 'drainpipe.com',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain, 'batman', 'mesh.com',
                           federation_list, False, False)
    add_follower_of_person(base_dir, nickname, domain, 'giraffe', 'trees.com',
                           federation_list, False, False)

    accountDir = acct_dir(base_dir, nickname, domain)
    f = open(accountDir + '/followers.txt', 'r')
    for followerDomain in f:
        testDomain = followerDomain.split('@')[1]
        testDomain = testDomain.replace('\n', '').replace('\r', '')
        if testDomain not in federation_list:
            print(testDomain)
            assert(False)

    os.chdir(currDir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_create_person_account(base_dir: str):
    print('testCreatePerson')
    system_language = 'en'
    currDir = base_dir
    nickname = 'test382'
    domain = 'badgerdomain.com'
    password = 'mypass'
    port = 80
    http_prefix = 'https'
    client_to_server = False
    base_dir = currDir + '/.tests_createperson'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)

    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(base_dir, nickname, domain, port,
                      http_prefix, True, False, password)
    assert os.path.isfile(base_dir + '/accounts/passwords')
    delete_all_posts(base_dir, nickname, domain, 'inbox')
    delete_all_posts(base_dir, nickname, domain, 'outbox')
    set_display_nickname(base_dir, nickname, domain, 'badger')
    set_bio(base_dir, nickname, domain, 'Randomly roaming in your backyard')
    archive_posts_for_person(nickname, domain, base_dir, 'inbox', None, {}, 4)
    archive_posts_for_person(nickname, domain, base_dir, 'outbox', None, {}, 4)
    testInReplyTo = None
    testInReplyToAtomUri = None
    testSubject = None
    testSchedulePost = False
    testEventDate = None
    testEventTime = None
    testLocation = None
    testIsArticle = False
    content = "G'day world!"
    followersOnly = False
    saveToFile = True
    commentsEnabled = True
    attachImageFilename = None
    mediaType = None
    conversationId = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    create_public_post(base_dir, nickname, domain, port, http_prefix,
                       content, followersOnly, saveToFile, client_to_server,
                       commentsEnabled, attachImageFilename, mediaType,
                       'Not suitable for Vogons', 'London, England',
                       testInReplyTo, testInReplyToAtomUri,
                       testSubject, testSchedulePost,
                       testEventDate, testEventTime, testLocation,
                       testIsArticle, system_language, conversationId,
                       low_bandwidth, content_license_url)

    os.chdir(currDir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def show_test_boxes(name: str, inboxPath: str, outboxPath: str) -> None:
    inboxPosts = \
        len([name for name in os.listdir(inboxPath)
             if os.path.isfile(os.path.join(inboxPath, name))])
    outboxPosts = \
        len([name for name in os.listdir(outboxPath)
             if os.path.isfile(os.path.join(outboxPath, name))])
    print('EVENT: ' + name +
          ' inbox has ' + str(inboxPosts) + ' posts and ' +
          str(outboxPosts) + ' outbox posts')


def _test_authentication(base_dir: str) -> None:
    print('testAuthentication')
    currDir = base_dir
    nickname = 'test8743'
    password = 'SuperSecretPassword12345'

    base_dir = currDir + '/.tests_authentication'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)

    assert store_basic_credentials(base_dir, 'othernick', 'otherpass')
    assert store_basic_credentials(base_dir, 'bad:nick', 'otherpass') is False
    assert store_basic_credentials(base_dir, 'badnick', 'otherpa:ss') is False
    assert store_basic_credentials(base_dir, nickname, password)

    authHeader = create_basic_auth_header(nickname, password)
    assert authorize_basic(base_dir, '/users/' + nickname + '/inbox',
                           authHeader, False)
    assert authorize_basic(base_dir, '/users/' + nickname,
                           authHeader, False) is False
    assert authorize_basic(base_dir, '/users/othernick/inbox',
                           authHeader, False) is False

    authHeader = create_basic_auth_header(nickname, password + '1')
    assert authorize_basic(base_dir, '/users/' + nickname + '/inbox',
                           authHeader, False) is False

    password = 'someOtherPassword'
    assert store_basic_credentials(base_dir, nickname, password)

    authHeader = create_basic_auth_header(nickname, password)
    assert authorize_basic(base_dir, '/users/' + nickname + '/inbox',
                           authHeader, False)

    os.chdir(currDir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def test_client_to_server(base_dir: str):
    print('EVENT: Testing sending a post via c2s')

    global testServerAliceRunning
    global testServerBobRunning
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    testServerAliceRunning = False
    testServerBobRunning = False

    system_language = 'en'
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    low_bandwidth = False

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    aliceDir = base_dir + '/.tests/alice'
    aliceDomain = '127.0.0.42'
    alicePort = 61935
    aliceSendThreads = []
    aliceAddress = aliceDomain + ':' + str(alicePort)

    bobDir = base_dir + '/.tests/bob'
    bobDomain = '127.0.0.64'
    bobPort = 61936
    bobSendThreads = []
    bobAddress = bobDomain + ':' + str(bobPort)

    global thrAlice
    if thrAlice:
        while thrAlice.is_alive():
            thrAlice.stop()
            time.sleep(1)
        thrAlice.kill()

    thrAlice = \
        thread_with_trace(target=create_server_alice,
                          args=(aliceDir, aliceDomain, alicePort, bobAddress,
                                federation_list, False, False,
                                aliceSendThreads),
                          daemon=True)

    global thrBob
    if thrBob:
        while thrBob.is_alive():
            thrBob.stop()
            time.sleep(1)
        thrBob.kill()

    thrBob = \
        thread_with_trace(target=create_server_bob,
                          args=(bobDir, bobDomain, bobPort, aliceAddress,
                                federation_list, False, False,
                                bobSendThreads),
                          daemon=True)

    thrAlice.start()
    thrBob.start()
    assert thrAlice.is_alive() is True
    assert thrBob.is_alive() is True

    # wait for both servers to be running
    ctr = 0
    while not (testServerAliceRunning and testServerBobRunning):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(testServerAliceRunning))
    print('Bob online: ' + str(testServerBobRunning))

    time.sleep(1)

    print('\n\n*******************************************************')
    print('EVENT: Alice sends to Bob via c2s')

    sessionAlice = create_session(proxy_type)
    followersOnly = False
    attachedImageFilename = base_dir + '/img/logo.png'
    mediaType = get_attachment_media_type(attachedImageFilename)
    attachedImageDescription = 'Logo'
    city = 'London, England'
    isArticle = False
    cached_webfingers = {}
    person_cache = {}
    password = 'alicepass'
    conversationId = None

    aliceInboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/inbox'
    aliceOutboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/outbox'
    bobInboxPath = bobDir + '/accounts/bob@' + bobDomain + '/inbox'
    bobOutboxPath = bobDir + '/accounts/bob@' + bobDomain + '/outbox'

    outboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/outbox'
    inboxPath = bobDir + '/accounts/bob@' + bobDomain + '/inbox'
    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    assert len([name for name in os.listdir(aliceInboxPath)
                if os.path.isfile(os.path.join(aliceInboxPath, name))]) == 0
    assert len([name for name in os.listdir(aliceOutboxPath)
                if os.path.isfile(os.path.join(aliceOutboxPath, name))]) == 0
    assert len([name for name in os.listdir(bobInboxPath)
                if os.path.isfile(os.path.join(bobInboxPath, name))]) == 0
    assert len([name for name in os.listdir(bobOutboxPath)
                if os.path.isfile(os.path.join(bobOutboxPath, name))]) == 0
    print('EVENT: all inboxes and outboxes are empty')
    signing_priv_key_pem = None
    sendResult = \
        send_post_via_server(signing_priv_key_pem, __version__,
                             aliceDir, sessionAlice, 'alice', password,
                             aliceDomain, alicePort,
                             'bob', bobDomain, bobPort, None,
                             http_prefix, 'Sent from my ActivityPub client',
                             followersOnly, True,
                             attachedImageFilename, mediaType,
                             attachedImageDescription, city,
                             cached_webfingers, person_cache, isArticle,
                             system_language, low_bandwidth,
                             content_license_url,
                             True, None, None,
                             conversationId, None)
    print('sendResult: ' + str(sendResult))

    for i in range(30):
        if os.path.isdir(outboxPath):
            if len([name for name in os.listdir(outboxPath)
                    if os.path.isfile(os.path.join(outboxPath, name))]) == 1:
                break
        time.sleep(1)

    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    assert len([name for name in os.listdir(aliceInboxPath)
                if os.path.isfile(os.path.join(aliceInboxPath, name))]) == 0
    assert len([name for name in os.listdir(aliceOutboxPath)
                if os.path.isfile(os.path.join(aliceOutboxPath, name))]) == 1
    print(">>> c2s post arrived in Alice's outbox\n\n\n")

    for i in range(30):
        if os.path.isdir(inboxPath):
            if len([name for name in os.listdir(bobInboxPath)
                    if os.path.isfile(os.path.join(bobInboxPath, name))]) == 1:
                break
        time.sleep(1)

    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    assert len([name for name in os.listdir(bobInboxPath)
                if os.path.isfile(os.path.join(bobInboxPath, name))]) == 1
    assert len([name for name in os.listdir(bobOutboxPath)
                if os.path.isfile(os.path.join(bobOutboxPath, name))]) == 0

    print(">>> s2s post arrived in Bob's inbox")
    print("c2s send success\n\n\n")

    print('\n\nEVENT: Getting message id for the post')
    statusNumber = 0
    outboxPostFilename = None
    outboxPostId = None
    for name in os.listdir(outboxPath):
        if '#statuses#' in name:
            statusNumber = name.split('#statuses#')[1].replace('.json', '')
            statusNumber = int(statusNumber.replace('#activity', ''))
            outboxPostFilename = outboxPath + '/' + name
            post_json_object = load_json(outboxPostFilename, 0)
            if post_json_object:
                outboxPostId = remove_id_ending(post_json_object['id'])
    assert outboxPostId
    print('message id obtained: ' + outboxPostId)
    assert valid_inbox(bobDir, 'bob', bobDomain)
    assert valid_inbox_filenames(bobDir, 'bob', bobDomain,
                                 aliceDomain, alicePort)

    print('\n\nAlice follows Bob')
    signing_priv_key_pem = None
    send_follow_requestViaServer(aliceDir, sessionAlice,
                                 'alice', password,
                                 aliceDomain, alicePort,
                                 'bob', bobDomain, bobPort,
                                 http_prefix,
                                 cached_webfingers, person_cache,
                                 True, __version__, signing_priv_key_pem)
    alicePetnamesFilename = aliceDir + '/accounts/' + \
        'alice@' + aliceDomain + '/petnames.txt'
    aliceFollowingFilename = \
        aliceDir + '/accounts/alice@' + aliceDomain + '/following.txt'
    bobFollowersFilename = \
        bobDir + '/accounts/bob@' + bobDomain + '/followers.txt'
    for t in range(10):
        if os.path.isfile(bobFollowersFilename):
            if 'alice@' + aliceDomain + ':' + str(alicePort) in \
               open(bobFollowersFilename).read():
                if os.path.isfile(aliceFollowingFilename) and \
                   os.path.isfile(alicePetnamesFilename):
                    if 'bob@' + bobDomain + ':' + str(bobPort) in \
                       open(aliceFollowingFilename).read():
                        break
        time.sleep(1)

    assert os.path.isfile(bobFollowersFilename)
    assert os.path.isfile(aliceFollowingFilename)
    assert os.path.isfile(alicePetnamesFilename)
    assert 'bob bob@' + bobDomain in \
        open(alicePetnamesFilename).read()
    print('alice@' + aliceDomain + ':' + str(alicePort) + ' in ' +
          bobFollowersFilename)
    assert 'alice@' + aliceDomain + ':' + str(alicePort) in \
        open(bobFollowersFilename).read()
    print('bob@' + bobDomain + ':' + str(bobPort) + ' in ' +
          aliceFollowingFilename)
    assert 'bob@' + bobDomain + ':' + str(bobPort) in \
        open(aliceFollowingFilename).read()
    assert valid_inbox(bobDir, 'bob', bobDomain)
    assert valid_inbox_filenames(bobDir, 'bob', bobDomain,
                                 aliceDomain, alicePort)

    print('\n\nEVENT: Bob follows Alice')
    send_follow_requestViaServer(aliceDir, sessionAlice,
                                 'bob', 'bobpass',
                                 bobDomain, bobPort,
                                 'alice', aliceDomain, alicePort,
                                 http_prefix,
                                 cached_webfingers, person_cache,
                                 True, __version__, signing_priv_key_pem)
    for t in range(10):
        if os.path.isfile(aliceDir + '/accounts/alice@' + aliceDomain +
                          '/followers.txt'):
            if 'bob@' + bobDomain + ':' + str(bobPort) in \
               open(aliceDir + '/accounts/alice@' + aliceDomain +
                    '/followers.txt').read():
                if os.path.isfile(bobDir + '/accounts/bob@' + bobDomain +
                                  '/following.txt'):
                    aliceHandleStr = \
                        'alice@' + aliceDomain + ':' + str(alicePort)
                    if aliceHandleStr in \
                       open(bobDir + '/accounts/bob@' + bobDomain +
                            '/following.txt').read():
                        if os.path.isfile(bobDir + '/accounts/bob@' +
                                          bobDomain +
                                          '/followingCalendar.txt'):
                            if aliceHandleStr in \
                               open(bobDir + '/accounts/bob@' + bobDomain +
                                    '/followingCalendar.txt').read():
                                break
        time.sleep(1)

    assert os.path.isfile(aliceDir + '/accounts/alice@' + aliceDomain +
                          '/followers.txt')
    assert os.path.isfile(bobDir + '/accounts/bob@' + bobDomain +
                          '/following.txt')
    assert 'bob@' + bobDomain + ':' + str(bobPort) in \
        open(aliceDir + '/accounts/alice@' + aliceDomain +
             '/followers.txt').read()
    assert 'alice@' + aliceDomain + ':' + str(alicePort) in \
        open(bobDir + '/accounts/bob@' + bobDomain + '/following.txt').read()

    sessionBob = create_session(proxy_type)
    password = 'bobpass'
    outboxPath = bobDir + '/accounts/bob@' + bobDomain + '/outbox'
    inboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/inbox'
    print(str(len([name for name in os.listdir(bobOutboxPath)
                   if os.path.isfile(os.path.join(bobOutboxPath, name))])))
    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    assert len([name for name in os.listdir(bobOutboxPath)
                if os.path.isfile(os.path.join(bobOutboxPath, name))]) == 1
    print(str(len([name for name in os.listdir(aliceInboxPath)
                   if os.path.isfile(os.path.join(aliceInboxPath, name))])))
    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    assert len([name for name in os.listdir(aliceInboxPath)
                if os.path.isfile(os.path.join(aliceInboxPath, name))]) == 0
    print('\n\nEVENT: Bob likes the post')
    send_like_via_server(bobDir, sessionBob,
                         'bob', 'bobpass',
                         bobDomain, bobPort,
                         http_prefix, outboxPostId,
                         cached_webfingers, person_cache,
                         True, __version__, signing_priv_key_pem)
    for i in range(20):
        if os.path.isdir(outboxPath) and os.path.isdir(inboxPath):
            if len([name for name in os.listdir(outboxPath)
                    if os.path.isfile(os.path.join(outboxPath, name))]) == 2:
                test = len([name for name in os.listdir(inboxPath)
                            if os.path.isfile(os.path.join(inboxPath, name))])
                if test == 1:
                    break
        time.sleep(1)
    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    bobOutboxPathCtr = \
        len([name for name in os.listdir(bobOutboxPath)
             if os.path.isfile(os.path.join(bobOutboxPath, name))])
    print('bobOutboxPathCtr: ' + str(bobOutboxPathCtr))
    assert bobOutboxPathCtr == 2
    aliceInboxPathCtr = \
        len([name for name in os.listdir(aliceInboxPath)
             if os.path.isfile(os.path.join(aliceInboxPath, name))])
    print('aliceInboxPathCtr: ' + str(aliceInboxPathCtr))
    assert aliceInboxPathCtr == 0
    print('EVENT: Post liked')

    print('\n\nEVENT: Bob reacts to the post')
    send_reaction_via_server(bobDir, sessionBob,
                             'bob', 'bobpass',
                             bobDomain, bobPort,
                             http_prefix, outboxPostId, '😃',
                             cached_webfingers, person_cache,
                             True, __version__, signing_priv_key_pem)
    for i in range(20):
        if os.path.isdir(outboxPath) and os.path.isdir(inboxPath):
            if len([name for name in os.listdir(outboxPath)
                    if os.path.isfile(os.path.join(outboxPath, name))]) == 3:
                test = len([name for name in os.listdir(inboxPath)
                            if os.path.isfile(os.path.join(inboxPath, name))])
                if test == 1:
                    break
        time.sleep(1)
    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    bobOutboxPathCtr = \
        len([name for name in os.listdir(bobOutboxPath)
             if os.path.isfile(os.path.join(bobOutboxPath, name))])
    print('bobOutboxPathCtr: ' + str(bobOutboxPathCtr))
    assert bobOutboxPathCtr == 3
    aliceInboxPathCtr = \
        len([name for name in os.listdir(aliceInboxPath)
             if os.path.isfile(os.path.join(aliceInboxPath, name))])
    print('aliceInboxPathCtr: ' + str(aliceInboxPathCtr))
    assert aliceInboxPathCtr == 0
    print('EVENT: Post reacted to')

    print(str(len([name for name in os.listdir(outboxPath)
                   if os.path.isfile(os.path.join(outboxPath, name))])))
    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    outboxPathCtr = \
        len([name for name in os.listdir(outboxPath)
             if os.path.isfile(os.path.join(outboxPath, name))])
    print('outboxPathCtr: ' + str(outboxPathCtr))
    assert outboxPathCtr == 3
    inboxPathCtr = \
        len([name for name in os.listdir(inboxPath)
             if os.path.isfile(os.path.join(inboxPath, name))])
    print('inboxPathCtr: ' + str(inboxPathCtr))
    assert inboxPathCtr == 0
    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    print('\n\nEVENT: Bob repeats the post')
    signing_priv_key_pem = None
    send_announce_via_server(bobDir, sessionBob, 'bob', password,
                             bobDomain, bobPort,
                             http_prefix, outboxPostId,
                             cached_webfingers,
                             person_cache, True, __version__,
                             signing_priv_key_pem)
    for i in range(20):
        if os.path.isdir(outboxPath) and os.path.isdir(inboxPath):
            if len([name for name in os.listdir(outboxPath)
                    if os.path.isfile(os.path.join(outboxPath, name))]) == 4:
                if len([name for name in os.listdir(inboxPath)
                        if os.path.isfile(os.path.join(inboxPath,
                                                       name))]) == 2:
                    break
        time.sleep(1)

    show_test_boxes('alice', aliceInboxPath, aliceOutboxPath)
    show_test_boxes('bob', bobInboxPath, bobOutboxPath)
    bobOutboxPathCtr = \
        len([name for name in os.listdir(bobOutboxPath)
             if os.path.isfile(os.path.join(bobOutboxPath, name))])
    print('bobOutboxPathCtr: ' + str(bobOutboxPathCtr))
    assert bobOutboxPathCtr == 5
    aliceInboxPathCtr = \
        len([name for name in os.listdir(aliceInboxPath)
             if os.path.isfile(os.path.join(aliceInboxPath, name))])
    print('aliceInboxPathCtr: ' + str(aliceInboxPathCtr))
    assert aliceInboxPathCtr == 1
    print('EVENT: Post repeated')

    inboxPath = bobDir + '/accounts/bob@' + bobDomain + '/inbox'
    outboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/outbox'
    postsBefore = \
        len([name for name in os.listdir(inboxPath)
             if os.path.isfile(os.path.join(inboxPath, name))])
    print('\n\nEVENT: Alice deletes her post: ' + outboxPostId + ' ' +
          str(postsBefore))
    password = 'alicepass'
    send_delete_via_server(aliceDir, sessionAlice, 'alice', password,
                           aliceDomain, alicePort,
                           http_prefix, outboxPostId,
                           cached_webfingers, person_cache,
                           True, __version__, signing_priv_key_pem)
    for i in range(30):
        if os.path.isdir(inboxPath):
            test = len([name for name in os.listdir(inboxPath)
                        if os.path.isfile(os.path.join(inboxPath, name))])
            if test == postsBefore-1:
                break
        time.sleep(1)

    test = len([name for name in os.listdir(inboxPath)
                if os.path.isfile(os.path.join(inboxPath, name))])
    assert test == postsBefore - 1
    print(">>> post deleted from Alice's outbox and Bob's inbox")
    assert valid_inbox(bobDir, 'bob', bobDomain)
    assert valid_inbox_filenames(bobDir, 'bob', bobDomain,
                                 aliceDomain, alicePort)

    print('\n\nEVENT: Alice unfollows Bob')
    password = 'alicepass'
    send_unfollow_request_via_server(base_dir, sessionAlice,
                                     'alice', password,
                                     aliceDomain, alicePort,
                                     'bob', bobDomain, bobPort,
                                     http_prefix,
                                     cached_webfingers, person_cache,
                                     True, __version__, signing_priv_key_pem)
    for t in range(10):
        if 'alice@' + aliceDomain + ':' + str(alicePort) not in \
           open(bobFollowersFilename).read():
            if 'bob@' + bobDomain + ':' + str(bobPort) not in \
               open(aliceFollowingFilename).read():
                break
        time.sleep(1)

    assert os.path.isfile(bobFollowersFilename)
    assert os.path.isfile(aliceFollowingFilename)
    assert 'alice@' + aliceDomain + ':' + str(alicePort) \
        not in open(bobFollowersFilename).read()
    assert 'bob@' + bobDomain + ':' + str(bobPort) \
        not in open(aliceFollowingFilename).read()
    assert valid_inbox(bobDir, 'bob', bobDomain)
    assert valid_inbox_filenames(bobDir, 'bob', bobDomain,
                                 aliceDomain, alicePort)
    assert valid_inbox(aliceDir, 'alice', aliceDomain)
    assert valid_inbox_filenames(aliceDir, 'alice', aliceDomain,
                                 bobDomain, bobPort)

    # stop the servers
    thrAlice.kill()
    thrAlice.join()
    assert thrAlice.is_alive() is False

    thrBob.kill()
    thrBob.join()
    assert thrBob.is_alive() is False

    os.chdir(base_dir)
    # shutil.rmtree(aliceDir, ignore_errors=False, onerror=None)
    # shutil.rmtree(bobDir, ignore_errors=False, onerror=None)


def _test_actor_parsing():
    print('testActorParsing')
    actor = 'https://mydomain:72/users/mynick'
    domain, port = get_domain_from_actor(actor)
    assert domain == 'mydomain'
    assert port == 72
    nickname = get_nickname_from_actor(actor)
    assert nickname == 'mynick'

    actor = 'https://element/accounts/badger'
    domain, port = get_domain_from_actor(actor)
    assert domain == 'element'
    nickname = get_nickname_from_actor(actor)
    assert nickname == 'badger'

    actor = 'egg@chicken.com'
    domain, port = get_domain_from_actor(actor)
    assert domain == 'chicken.com'
    nickname = get_nickname_from_actor(actor)
    assert nickname == 'egg'

    actor = '@waffle@cardboard'
    domain, port = get_domain_from_actor(actor)
    assert domain == 'cardboard'
    nickname = get_nickname_from_actor(actor)
    assert nickname == 'waffle'

    actor = 'https://astral/channel/sky'
    domain, port = get_domain_from_actor(actor)
    assert domain == 'astral'
    nickname = get_nickname_from_actor(actor)
    assert nickname == 'sky'

    actor = 'https://randomain/users/rando'
    domain, port = get_domain_from_actor(actor)
    assert domain == 'randomain'
    nickname = get_nickname_from_actor(actor)
    assert nickname == 'rando'

    actor = 'https://otherdomain:49/@othernick'
    domain, port = get_domain_from_actor(actor)
    assert domain == 'otherdomain'
    assert port == 49
    nickname = get_nickname_from_actor(actor)
    assert nickname == 'othernick'


def _test_web_links():
    print('testWebLinks')

    exampleText = \
        "<p>Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        " <a href=\"https://domain.ugh/tags/turbot\" class=\"mention " + \
        "hashtag\" rel=\"tag\">#<span>turbot</span></a> <a href=\"" + \
        "https://domain.ugh/tags/haddock\" class=\"mention hashtag\"" + \
        " rel=\"tag\">#<span>haddock</span></a></p>"
    resultText = remove_long_words(exampleText, 40, [])
    assert resultText == "<p>Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        " <a href=\"https://domain.ugh/tags/turbot\" class=\"mention " + \
        "hashtag\" rel=\"tag\">#<span>turbot</span></a> " + \
        "<a href=\"https://domain.ugh/tags/haddock\" " + \
        "class=\"mention hashtag\" rel=\"tag\">#<span>haddock</span></a></p>"

    exampleText = \
        '<p><span class=\"h-card\"><a href=\"https://something/@orother' + \
        '\" class=\"u-url mention\">@<span>foo</span></a></span> Some ' + \
        'random text.</p><p>AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA</p>'
    resultText = remove_long_words(exampleText, 40, [])
    assert resultText == \
        '<p><span class="h-card"><a href="https://something/@orother"' + \
        ' class="u-url mention">@<span>foo</span></a></span> ' + \
        'Some random text.</p>'

    exampleText = \
        'This post has a web links https://somesite.net\n\nAnd some other text'
    linkedText = add_web_links(exampleText)
    assert \
        '<a href="https://somesite.net" rel="nofollow noopener noreferrer"' + \
        ' target="_blank"><span class="invisible">https://' + \
        '</span><span class="ellipsis">somesite.net</span></a' in linkedText

    exampleText = \
        'This post has a very long web link\n\nhttp://' + \
        'cbwebewuvfuftdiudbqd33dddbbyuef23fyug3bfhcyu2fct2' + \
        'cuyqbcbucuwvckiwyfgewfvqejbchevbhwevuevwbqebqekve' + \
        'qvuvjfkf.onion\n\nAnd some other text'
    linkedText = add_web_links(exampleText)
    assert 'ellipsis' in linkedText

    exampleText = \
        '<p>1. HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAH' + \
        'AHAHAHHAHAHAHAHAHAHAHAHAHAHAHAHHAHAHAHAHAHAHAHAH</p>'
    resultText = remove_long_words(exampleText, 40, [])
    assert resultText == '<p>1. HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHA</p>'

    exampleText = \
        '<p>Tox address is 88AB9DED6F9FBEF43E105FB72060A2D89F9B93C74' + \
        '4E8C45AB3C5E42C361C837155AFCFD9D448 </p>'
    resultText = remove_long_words(exampleText, 40, [])
    assert resultText == exampleText

    exampleText = \
        'some.incredibly.long.and.annoying.word.which.should.be.removed: ' + \
        'The remaining text'
    resultText = remove_long_words(exampleText, 40, [])
    assert resultText == \
        'some.incredibly.long.and.annoying.word.w\n' + \
        'hich.should.be.removed: The remaining text'

    exampleText = \
        '<p>Tox address is 88AB9DED6F9FBEF43E105FB72060A2D89F9B93C74' + \
        '4E8C45AB3C5E42C361C837155AFCFD9D448</p>'
    resultText = remove_long_words(exampleText, 40, [])
    assert resultText == \
        '<p>Tox address is 88AB9DED6F9FBEF43E105FB72060A2D89F9B93C7\n' + \
        '44E8C45AB3C5E42C361C837155AFCFD9D448</p>'

    exampleText = \
        '<p>ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCA' + \
        'BCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB' + \
        'CABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC' + \
        'ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCA' + \
        'BCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB' + \
        'CABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC' + \
        'ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCA' + \
        'BCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB' + \
        'CABCABCABCABCABCABCABCABC</p>'
    resultText = remove_long_words(exampleText, 40, [])
    assert resultText == r'<p>ABCABCABCABCABCABCABCABCABCABCABCABCABCA<\p>'

    exampleText = \
        '"the nucleus of mutual-support institutions, habits, and customs ' + \
        'remains alive with the millions; it keeps them together; and ' + \
        'they prefer to cling to their customs, beliefs, and traditions ' + \
        'rather than to accept the teachings of a war of each ' + \
        'against all"\n\n--Peter Kropotkin'
    testFnStr = add_web_links(exampleText)
    resultText = remove_long_words(testFnStr, 40, [])
    assert resultText == exampleText
    assert 'ellipsis' not in resultText

    exampleText = \
        '<p>ｆｉｌｅｐｏｐｏｕｔ＝' + \
        'ＴｅｍｐｌａｔｅＡｔｔａｃｈｍｅｎｔＲｉｃｈＰｏｐｏｕｔ<<\\p>'
    resultText = replace_content_duplicates(exampleText)
    assert resultText == \
        '<p>ｆｉｌｅｐｏｐｏｕｔ＝' + \
        'ＴｅｍｐｌａｔｅＡｔｔａｃｈｍｅｎｔＲｉｃｈＰｏｐｏｕｔ'

    exampleText = \
        '<p>Test1 test2 #YetAnotherExcessivelyLongwindedAndBoringHashtag</p>'
    testFnStr = add_web_links(exampleText)
    resultText = remove_long_words(testFnStr, 40, [])
    assert(resultText ==
           '<p>Test1 test2 '
           '#YetAnotherExcessivelyLongwindedAndBorin\ngHashtag</p>')

    exampleText = \
        "<p>Don't remove a p2p link " + \
        "rad:git:hwd1yrerc3mcgn8ga9rho3dqi4w33nep7kxmqezss4topyfgmexihp" + \
        "33xcw</p>"
    testFnStr = add_web_links(exampleText)
    resultText = remove_long_words(testFnStr, 40, [])
    assert resultText == exampleText


def _test_addemoji(base_dir: str):
    print('testAddEmoji')
    content = "Emoji :lemon: :strawberry: :banana:"
    http_prefix = 'http'
    nickname = 'testuser'
    domain = 'testdomain.net'
    port = 3682
    recipients = []
    hashtags = {}
    base_dirOriginal = base_dir
    path = base_dir + '/.tests'
    if not os.path.isdir(path):
        os.mkdir(path)
    path = base_dir + '/.tests/emoji'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    base_dir = path
    path = base_dir + '/emoji'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    copytree(base_dirOriginal + '/emoji', base_dir + '/emoji')
    os.chdir(base_dir)
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(base_dir, nickname, domain, port,
                      http_prefix, True, False, 'password')
    contentModified = \
        add_html_tags(base_dir, http_prefix,
                      nickname, domain, content,
                      recipients, hashtags, True)
    assert ':lemon:' in contentModified
    assert contentModified.startswith('<p>')
    assert contentModified.endswith('</p>')
    tags = []
    for tagName, tag in hashtags.items():
        tags.append(tag)
    content = contentModified
    contentModified = \
        replace_emoji_from_tags(None, base_dir, content, tags, 'content', True)
    # print('contentModified: ' + contentModified)
    assert contentModified == '<p>Emoji 🍋 🍓 🍌</p>'

    os.chdir(base_dirOriginal)
    shutil.rmtree(base_dirOriginal + '/.tests',
                  ignore_errors=False, onerror=None)


def _test_get_status_number():
    print('testGetStatusNumber')
    prevStatusNumber = None
    for i in range(1, 20):
        statusNumber, published = get_status_number()
        if prevStatusNumber:
            assert len(statusNumber) == 18
            assert int(statusNumber) > prevStatusNumber
        prevStatusNumber = int(statusNumber)


def _test_json_string() -> None:
    print('testJsonString')
    filename = '.epicyon_tests_test_json_string.json'
    messageStr = "Crème brûlée यह एक परीक्षण ह"
    testJson = {
        "content": messageStr
    }
    assert save_json(testJson, filename)
    receivedJson = load_json(filename, 0)
    assert receivedJson
    assert receivedJson['content'] == messageStr
    encodedStr = json.dumps(testJson, ensure_ascii=False)
    assert messageStr in encodedStr
    try:
        os.remove(filename)
    except OSError:
        pass


def _test_save_load_json():
    print('testSaveLoadJson')
    testJson = {
        "param1": 3,
        "param2": '"Crème brûlée यह एक परीक्षण ह"'
    }
    testFilename = '.epicyon_tests_test_save_load_json.json'
    if os.path.isfile(testFilename):
        try:
            os.remove(testFilename)
        except OSError:
            pass
    assert save_json(testJson, testFilename)
    assert os.path.isfile(testFilename)
    testLoadJson = load_json(testFilename)
    assert(testLoadJson)
    assert testLoadJson.get('param1')
    assert testLoadJson.get('param2')
    assert testLoadJson['param1'] == 3
    assert testLoadJson['param2'] == '"Crème brûlée यह एक परीक्षण ह"'
    try:
        os.remove(testFilename)
    except OSError:
        pass


def _test_theme():
    print('testTheme')
    css = 'somestring --background-value: 24px; --foreground-value: 24px;'
    result = set_cs_sparam(css, 'background-value', '32px')
    assert result == \
        'somestring --background-value: 32px; --foreground-value: 24px;'
    css = \
        'somestring --background-value: 24px; --foreground-value: 24px; ' + \
        '--background-value: 24px;'
    result = set_cs_sparam(css, 'background-value', '32px')
    assert result == \
        'somestring --background-value: 32px; --foreground-value: 24px; ' + \
        '--background-value: 32px;'
    css = '--background-value: 24px; --foreground-value: 24px;'
    result = set_cs_sparam(css, 'background-value', '32px')
    assert result == '--background-value: 32px; --foreground-value: 24px;'


def _test_recent_posts_cache():
    print('testRecentPostsCache')
    recent_posts_cache = {}
    max_recent_posts = 3
    htmlStr = '<html></html>'
    for i in range(5):
        post_json_object = {
            "id": "https://somesite.whatever/users/someuser/statuses/" + str(i)
        }
        update_recent_posts_cache(recent_posts_cache, max_recent_posts,
                                  post_json_object, htmlStr)
    assert len(recent_posts_cache['index']) == max_recent_posts
    assert len(recent_posts_cache['json'].items()) == max_recent_posts
    assert len(recent_posts_cache['html'].items()) == max_recent_posts


def _test_remove_txt_formatting():
    print('testRemoveTextFormatting')
    testStr = '<p>Text without formatting</p>'
    resultStr = remove_text_formatting(testStr)
    assert(resultStr == testStr)
    testStr = '<p>Text <i>with</i> <h3>formatting</h3></p>'
    resultStr = remove_text_formatting(testStr)
    assert(resultStr == '<p>Text with formatting</p>')


def _test_jsonld():
    print("testJsonld")

    jldDocument = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "actor": "https://somesite.net/users/gerbil",
        "description": "My json document",
        "numberField": 83582,
        "object": {
            "content": "valid content"
        }
    }
    # privateKeyPem, publicKeyPem = generate_rsa_key()
    privateKeyPem = '-----BEGIN RSA PRIVATE KEY-----\n' \
        'MIIEowIBAAKCAQEAod9iHfIn4ugY/2byFrFjUprrFLkkH5bCrjiBq2/MdHFg99IQ\n' \
        '7li2x2mg5fkBMhU5SJIxlN8kiZMFq7JUXSA97Yo4puhVubqTSHihIh6Xn2mTjTgs\n' \
        'zNo9SBbmN3YiyBPTcr0rF4jGWZAduJ8u6i7Eky2QH+UBKyUNRZrcfoVq+7grHUIA\n' \
        '45pE7vAfEEWtgRiw32Nwlx55N3hayHax0y8gMdKEF/vfYKRLcM7rZgEASMtlCpgy\n' \
        'fsyHwFCDzl/BP8AhP9u3dM+SEundeAvF58AiXx1pKvBpxqttDNAsKWCRQ06/WI/W\n' \
        '2Rwihl9yCjobqRoFsZ/cTEi6FG9AbDAds5YjTwIDAQABAoIBAERL3rbpy8Bl0t43\n' \
        'jh7a+yAIMvVMZBxb3InrV3KAug/LInGNFQ2rKnsaawN8uu9pmwCuhfLc7yqIeJUH\n' \
        'qaadCuPlNJ/fWQQC309tbfbaV3iv78xejjBkSATZfIqb8nLeQpGflMXaNG3na1LQ\n' \
        '/tdZoiDC0ZNTaNnOSTo765oKKqhHUTQkwkGChrwG3Js5jekV4zpPMLhUafXk6ksd\n' \
        '8XLlZdCF3RUnuguXAg2xP/duxMYmTCx3eeGPkXBPQl0pahu8/6OtBoYvBrqNdQcx\n' \
        'jnEtYX9PCqDY3hAXW9GWsxNfu02DKhWigFHFNRUQtMI++438+QIfzXPslE2bTQIt\n' \
        '0OXUlwECgYEAxTKUZ7lwIBb5XKPJq53RQmX66M3ArxI1RzFSKm1+/CmxvYiN0c+5\n' \
        '2Aq62WEIauX6hoZ7yQb4zhdeNRzinLR7rsmBvIcP12FidXG37q9v3Vu70KmHniJE\n' \
        'TPbt5lHQ0bNACFxkar4Ab/JZN4CkMRgJdlcZ5boYNmcGOYCvw9izuM8CgYEA0iQ1\n' \
        'khIFZ6fCiXwVRGvEHmqSnkBmBHz8MY8fczv2Z4Gzfq3Tlh9VxpigK2F2pFt7keWc\n' \
        '53HerYFHFpf5otDhEyRwA1LyIcwbj5HopumxsB2WG+/M2as45lLfWa6KO73OtPpU\n' \
        'wGZYW+i/otdk9eFphceYtw19mxI+3lYoeI8EjYECgYBxOtTKJkmCs45lqkp/d3QT\n' \
        '2zjSempcXGkpQuG6KPtUUaCUgxdj1RISQj792OCbeQh8PDZRvOYaeIKInthkQKIQ\n' \
        'P/Z1yVvIQUvmwfBqZmQmR6k1bFLJ80UiqFr7+BiegH2RD3Q9cnIP1aly3DPrWLD+\n' \
        'OY9OQKfsfQWu+PxzyTeRMwKBgD8Zjlh5PtQ8RKcB8mTkMzSq7bHFRpzsZtH+1wPE\n' \
        'Kp40DRDp41H9wMTsiZPdJUH/EmDh4LaCs8nHuu/m3JfuPtd/pn7pBjntzwzSVFji\n' \
        'bW+jwrJK1Gk8B87pbZXBWlLMEOi5Dn/je37Fqd2c7f0DHauFHq9AxsmsteIPXwGs\n' \
        'eEKBAoGBAIzJX/5yFp3ObkPracIfOJ/U/HF1UdP6Y8qmOJBZOg5s9Y+JAdY76raK\n' \
        '0SbZPsOpuFUdTiRkSI3w/p1IuM5dPxgCGH9MHqjqogU5QwXr3vLF+a/PFhINkn1x\n' \
        'lozRZjDcF1y6xHfExotPC973UZnKEviq9/FqOsovZpvSQkzAYSZF\n' \
        '-----END RSA PRIVATE KEY-----'
    publicKeyPem = '-----BEGIN PUBLIC KEY-----\n' \
        'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAod9iHfIn4ugY/2byFrFj\n' \
        'UprrFLkkH5bCrjiBq2/MdHFg99IQ7li2x2mg5fkBMhU5SJIxlN8kiZMFq7JUXSA9\n' \
        '7Yo4puhVubqTSHihIh6Xn2mTjTgszNo9SBbmN3YiyBPTcr0rF4jGWZAduJ8u6i7E\n' \
        'ky2QH+UBKyUNRZrcfoVq+7grHUIA45pE7vAfEEWtgRiw32Nwlx55N3hayHax0y8g\n' \
        'MdKEF/vfYKRLcM7rZgEASMtlCpgyfsyHwFCDzl/BP8AhP9u3dM+SEundeAvF58Ai\n' \
        'Xx1pKvBpxqttDNAsKWCRQ06/WI/W2Rwihl9yCjobqRoFsZ/cTEi6FG9AbDAds5Yj\n' \
        'TwIDAQAB\n' \
        '-----END PUBLIC KEY-----'

    signedDocument = jldDocument.copy()
    generate_json_signature(signedDocument, privateKeyPem)
    assert(signedDocument)
    assert(signedDocument.get('signature'))
    assert(signedDocument['signature'].get('signatureValue'))
    assert(signedDocument['signature'].get('type'))
    assert(len(signedDocument['signature']['signatureValue']) > 50)
    # print(str(signedDocument['signature']))
    assert(signedDocument['signature']['type'] == 'RsaSignature2017')
    assert(verify_json_signature(signedDocument, publicKeyPem))

    # alter the signed document
    signedDocument['object']['content'] = 'forged content'
    assert(not verify_json_signature(signedDocument, publicKeyPem))

    jldDocument2 = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "actor": "https://somesite.net/users/gerbil",
        "description": "Another json document",
        "numberField": 13353,
        "object": {
            "content": "More content"
        }
    }
    signedDocument2 = jldDocument2.copy()
    generate_json_signature(signedDocument2, privateKeyPem)
    assert(signedDocument2)
    assert(signedDocument2.get('signature'))
    assert(signedDocument2['signature'].get('signatureValue'))
    # changed signature on different document
    if signedDocument['signature']['signatureValue'] == \
       signedDocument2['signature']['signatureValue']:
        print('json signature has not changed for different documents')
    assert '.' not in str(signedDocument['signature']['signatureValue'])
    assert len(str(signedDocument['signature']['signatureValue'])) > 340
    assert(signedDocument['signature']['signatureValue'] !=
           signedDocument2['signature']['signatureValue'])


def _test_site_active():
    print('testSiteIsActive')
    timeout = 10
    assert(site_is_active('https://archive.org', timeout))
    assert(site_is_active('https://mastodon.social', timeout))
    assert(not site_is_active('https://notarealwebsite.a.b.c', timeout))


def _test_strip_html():
    print('testRemoveHtml')
    testStr = 'This string has no html.'
    assert(remove_html(testStr) == testStr)
    testStr = 'This string <a href="1234.567">has html</a>.'
    assert(remove_html(testStr) == 'This string has html.')
    testStr = '<label>This string has.</label><label>Two labels.</label>'
    assert(remove_html(testStr) == 'This string has. Two labels.')
    testStr = '<p>This string has.</p><p>Two paragraphs.</p>'
    assert(remove_html(testStr) == 'This string has.\n\nTwo paragraphs.')
    testStr = 'This string has.<br>A new line.'
    assert(remove_html(testStr) == 'This string has.\nA new line.')
    testStr = '<p>This string contains a url http://somesite.or.other</p>'
    assert(remove_html(testStr) ==
           'This string contains a url http://somesite.or.other')


def _test_danger_css(base_dir: str) -> None:
    print('testDangerousCSS')
    for subdir, dirs, files in os.walk(base_dir):
        for f in files:
            if not f.endswith('.css'):
                continue
            assert not dangerous_css(base_dir + '/' + f, False)
        break


def _test_danger_svg(base_dir: str) -> None:
    print('testDangerousSVG')
    svgContent = \
        '  <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">' + \
        '  <circle cx="5" cy="5" r="4" />' + \
        '</svg>'
    assert not dangerous_svg(svgContent, False)
    svgContent = \
        '  <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">' + \
        '  <script>' + \
        '  // <![CDATA[' + \
        "  window.addEventListener('DOMContentLoaded', () => {" + \
        '    function attackScript () {' + \
        '      return `#${OWO}`' + \
        '    }' + \
        '' + \
        "    document.querySelector('circle')." + \
        "addEventListener('click', (e) => {" + \
        '      e.target.style.fill = attackScript()' + \
        '    })' + \
        '  })' + \
        '  // ]]>' + \
        '  </script>' + \
        '' + \
        '  <circle cx="5" cy="5" r="4" />' + \
        '</svg>'
    assert dangerous_svg(svgContent, False)

    assert not scan_themes_for_scripts(base_dir)


def _test_danger_markup():
    print('testDangerousMarkup')
    allow_local_network_access = False
    content = '<p>This is a valid message</p>'
    assert(not dangerous_markup(content, allow_local_network_access))

    content = 'This is a valid message without markup'
    assert(not dangerous_markup(content, allow_local_network_access))

    content = '<p>This is a valid-looking message. But wait... ' + \
        '<script>document.getElementById("concentrated")' + \
        '.innerHTML = "evil";</script></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This is a valid-looking message. But wait... ' + \
        '&lt;script&gt;document.getElementById("concentrated")' + \
        '.innerHTML = "evil";&lt;/script&gt;</p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This html contains more than you expected... ' + \
        '<script language="javascript">document.getElementById("abc")' + \
        '.innerHTML = "def";</script></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This is a valid-looking message. But wait... ' + \
        '<script src="https://evilsite/payload.js" /></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This message embeds an evil frame.' + \
        '<iframe src="somesite"></iframe></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This message tries to obfuscate an evil frame.' + \
        '<  iframe     src = "somesite"></    iframe  ></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This message is not necessarily evil, but annoying.' + \
        '<hr><br><br><br><br><br><br><br><hr><hr></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This message contans a ' + \
        '<a href="https://validsite/index.html">valid link.</a></p>'
    assert(not dangerous_markup(content, allow_local_network_access))

    content = '<p>This message contans a ' + \
        '<a href="https://validsite/iframe.html">' + \
        'valid link having invalid but harmless name.</a></p>'
    assert(not dangerous_markup(content, allow_local_network_access))

    content = '<p>This message which <a href="127.0.0.1:8736">' + \
        'tries to access the local network</a></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>This message which <a href="http://192.168.5.10:7235">' + \
        'tries to access the local network</a></p>'
    assert(dangerous_markup(content, allow_local_network_access))

    content = '<p>127.0.0.1 This message which does not access ' + \
        'the local network</a></p>'
    assert(not dangerous_markup(content, allow_local_network_access))


def _run_html_replace_quote_marks():
    print('html_replace_quote_marks')
    testStr = 'The "cat" "sat" on the mat'
    result = html_replace_quote_marks(testStr)
    assert result == 'The “cat” “sat” on the mat'

    testStr = 'The cat sat on the mat'
    result = html_replace_quote_marks(testStr)
    assert result == 'The cat sat on the mat'

    testStr = '"hello"'
    result = html_replace_quote_marks(testStr)
    assert result == '“hello”'

    testStr = '"hello" <a href="somesite.html">&quot;test&quot; html</a>'
    result = html_replace_quote_marks(testStr)
    assert result == '“hello” <a href="somesite.html">“test” html</a>'


def _test_json_post_allows_comment():
    print('testJsonPostAllowsComments')
    post_json_object = {
        "id": "123"
    }
    assert json_post_allows_comments(post_json_object)
    post_json_object = {
        "id": "123",
        "commentsEnabled": False
    }
    assert not json_post_allows_comments(post_json_object)
    post_json_object = {
        "id": "123",
        "rejectReplies": False
    }
    assert json_post_allows_comments(post_json_object)
    post_json_object = {
        "id": "123",
        "rejectReplies": True
    }
    assert not json_post_allows_comments(post_json_object)
    post_json_object = {
        "id": "123",
        "commentsEnabled": True
    }
    assert json_post_allows_comments(post_json_object)
    post_json_object = {
        "id": "123",
        "object": {
            "commentsEnabled": True
        }
    }
    assert json_post_allows_comments(post_json_object)
    post_json_object = {
        "id": "123",
        "object": {
            "commentsEnabled": False
        }
    }
    assert not json_post_allows_comments(post_json_object)


def _test_remove_id_ending():
    print('testRemoveIdEnding')
    testStr = 'https://activitypub.somedomain.net'
    resultStr = remove_id_ending(testStr)
    assert resultStr == 'https://activitypub.somedomain.net'

    testStr = \
        'https://activitypub.somedomain.net/users/foo/' + \
        'statuses/34544814814/activity'
    resultStr = remove_id_ending(testStr)
    assert resultStr == \
        'https://activitypub.somedomain.net/users/foo/statuses/34544814814'

    testStr = \
        'https://undo.somedomain.net/users/foo/statuses/34544814814/undo'
    resultStr = remove_id_ending(testStr)
    assert resultStr == \
        'https://undo.somedomain.net/users/foo/statuses/34544814814'

    testStr = \
        'https://event.somedomain.net/users/foo/statuses/34544814814/event'
    resultStr = remove_id_ending(testStr)
    assert resultStr == \
        'https://event.somedomain.net/users/foo/statuses/34544814814'


def _test_valid_content_warning():
    print('testValidContentWarning')
    resultStr = valid_content_warning('Valid content warning')
    assert resultStr == 'Valid content warning'

    resultStr = valid_content_warning('Invalid #content warning')
    assert resultStr == 'Invalid content warning'

    resultStr = \
        valid_content_warning('Invalid <a href="somesite">content warning</a>')
    assert resultStr == 'Invalid content warning'


def _test_translations(base_dir: str) -> None:
    print('testTranslations')
    languagesStr = get_supported_languages(base_dir)
    assert languagesStr

    # load all translations into a dict
    langDict = {}
    for lang in languagesStr:
        langJson = load_json('translations/' + lang + '.json')
        if not langJson:
            print('Missing language file ' +
                  'translations/' + lang + '.json')
        assert langJson
        langDict[lang] = langJson

    # load english translations
    translationsJson = load_json('translations/en.json')
    # test each english string exists in the other language files
    for englishStr, translatedStr in translationsJson.items():
        for lang in languagesStr:
            langJson = langDict[lang]
            if not langJson.get(englishStr):
                print(englishStr + ' is missing from ' + lang + '.json')
            assert langJson.get(englishStr)


def _test_constant_time_string():
    print('testConstantTimeStringCheck')
    assert constant_time_string_check('testing', 'testing')
    assert not constant_time_string_check('testing', '1234')
    assert not constant_time_string_check('testing', '1234567')

    itterations = 256

    start = time.time()
    test_str = 'nnjfbefefbsnjsdnvbcueftqfeuqfbqefnjeniwufgy'
    for timingTest in range(itterations):
        constant_time_string_check(test_str, test_str)
    end = time.time()
    avTime1 = ((end - start) * 1000000 / itterations)

    # change a single character and observe timing difference
    start = time.time()
    for timingTest in range(itterations):
        constant_time_string_check(test_str, test_str)
    end = time.time()
    avTime2 = ((end - start) * 1000000 / itterations)
    time_diffMicroseconds = abs(avTime2 - avTime1)
    # time difference should be less than 10uS
    assert int(time_diffMicroseconds) < 10

    # change multiple characters and observe timing difference
    start = time.time()
    test_str2 = 'ano1befffbsn7sd3vbluef6qseuqfpqeznjgni9bfgi'
    for timingTest in range(itterations):
        constant_time_string_check(test_str, test_str2)
    end = time.time()
    avTime2 = ((end - start) * 1000000 / itterations)
    time_diffMicroseconds = abs(avTime2 - avTime1)
    # time difference should be less than 10uS
    assert int(time_diffMicroseconds) < 10


def _test_replace_email_quote():
    print('testReplaceEmailQuote')
    testStr = '<p>This content has no quote.</p>'
    assert html_replace_email_quote(testStr) == testStr

    testStr = '<p>This content has no quote.</p>' + \
        '<p>With multiple</p><p>lines</p>'
    assert html_replace_email_quote(testStr) == testStr

    testStr = '<p>&quot;This is a quoted paragraph.&quot;</p>'
    assert html_replace_email_quote(testStr) == \
        '<p><blockquote>This is a quoted paragraph.</blockquote></p>'

    testStr = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somewebsite/@nickname\" " + \
        "class=\"u-url mention\">@<span>nickname</span></a></span> " + \
        "<br />&gt; This is a quote</p><p>Some other text.</p>"
    expectedStr = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somewebsite/@nickname\" " + \
        "class=\"u-url mention\">@<span>nickname</span></a></span> " + \
        "<br /><blockquote>This is a quote</blockquote></p>" + \
        "<p>Some other text.</p>"
    resultStr = html_replace_email_quote(testStr)
    if resultStr != expectedStr:
        print('Result: ' + str(resultStr))
        print('Expect: ' + expectedStr)
    assert resultStr == expectedStr

    testStr = "<p>Some text:</p><p>&gt; first line-&gt;second line</p>" + \
        "<p>Some question?</p>"
    expectedStr = "<p>Some text:</p><p><blockquote>first line-<br>" + \
        "second line</blockquote></p><p>Some question?</p>"
    resultStr = html_replace_email_quote(testStr)
    if resultStr != expectedStr:
        print('Result: ' + str(resultStr))
        print('Expect: ' + expectedStr)
    assert resultStr == expectedStr

    testStr = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somedomain/@somenick\" " + \
        "class=\"u-url mention\">@<span>somenick</span>" + \
        "</a></span> </p><p>&gt; Text1.<br />&gt; <br />" + \
        "&gt; Text2<br />&gt; <br />&gt; Text3<br />" + \
        "&gt;<br />&gt; Text4<br />&gt; <br />&gt; " + \
        "Text5<br />&gt; <br />&gt; Text6</p><p>Text7</p>"
    expectedStr = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somedomain/@somenick\" " + \
        "class=\"u-url mention\">@<span>somenick</span></a>" + \
        "</span> </p><p><blockquote> Text1.<br /><br />" + \
        "Text2<br /><br />Text3<br />&gt;<br />Text4<br />" + \
        "<br />Text5<br /><br />Text6</blockquote></p><p>Text7</p>"
    resultStr = html_replace_email_quote(testStr)
    if resultStr != expectedStr:
        print('Result: ' + str(resultStr))
        print('Expect: ' + expectedStr)
    assert resultStr == expectedStr


def _test_strip_html_tag():
    print('testRemoveHtmlTag')
    testStr = "<p><img width=\"864\" height=\"486\" " + \
        "src=\"https://somesiteorother.com/image.jpg\"></p>"
    resultStr = remove_html_tag(testStr, 'width')
    assert resultStr == "<p><img height=\"486\" " + \
        "src=\"https://somesiteorother.com/image.jpg\"></p>"


def _test_hashtag_rules():
    print('testHashtagRuleTree')
    operators = ('not', 'and', 'or', 'xor', 'from', 'contains')

    url = 'testsite.com'
    moderated = True
    conditionsStr = \
        'contains "Cat" or contains "Corvid" or ' + \
        'contains "Dormouse" or contains "Buzzard"'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == str(['or', ['contains', ['"Cat"']],
                             ['contains', ['"Corvid"']],
                             ['contains', ['"Dormouse"']],
                             ['contains', ['"Buzzard"']]])

    content = 'This is a test'
    moderated = True
    conditionsStr = '#foo or #bar'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == str(['or', ['#foo'], ['#bar']])
    assert str(tagsInConditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    content = 'This is a test'
    url = 'https://testsite.com/something'
    moderated = True
    conditionsStr = '#foo and from "testsite.com"'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == str(['and', ['#foo'], ['from', ['"testsite.com"']]])
    assert str(tagsInConditions) == str(['#foo'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content,
                                    'othersite.net')

    content = 'This is a test'
    moderated = True
    conditionsStr = 'contains "is a" and #foo or #bar'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == \
        str(['and', ['contains', ['"is a"']],
             ['or', ['#foo'], ['#bar']]])
    assert str(tagsInConditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    moderated = False
    conditionsStr = 'not moderated and #foo or #bar'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == \
        str(['not', ['and', ['moderated'], ['or', ['#foo'], ['#bar']]]])
    assert str(tagsInConditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    moderated = True
    conditionsStr = 'moderated and #foo or #bar'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == \
        str(['and', ['moderated'], ['or', ['#foo'], ['#bar']]])
    assert str(tagsInConditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditionsStr = 'x'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert tree is None
    assert tagsInConditions == []
    hashtags = ['#foo']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditionsStr = '#x'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == str(['#x'])
    assert str(tagsInConditions) == str(['#x'])
    hashtags = ['#x']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#y', '#z']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditionsStr = 'not #b'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == str(['not', ['#b']])
    assert str(tagsInConditions) == str(['#b'])
    hashtags = ['#y', '#z']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#a', '#b', '#c']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditionsStr = '#foo or #bar and #a'
    tagsInConditions = []
    tree = hashtag_rule_tree(operators, conditionsStr,
                             tagsInConditions, moderated)
    assert str(tree) == str(['and', ['or', ['#foo'], ['#bar']], ['#a']])
    assert str(tagsInConditions) == str(['#foo', '#bar', '#a'])
    hashtags = ['#foo', '#bar', '#a']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#bar', '#a']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#foo', '#a']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#x', '#a']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)


def _test_newswire_tags():
    print('testNewswireTags')
    rssDescription = '<img src="https://somesite/someimage.jpg" ' + \
        'class="misc-stuff" alt="#ExcitingHashtag" ' + \
        'srcset="https://somesite/someimage.jpg" ' + \
        'sizes="(max-width: 864px) 100vw, 864px" />' + \
        'Compelling description with #ExcitingHashtag, which is ' + \
        'being posted in #BoringForum'
    tags = get_newswire_tags(rssDescription, 10)
    assert len(tags) == 2
    assert '#BoringForum' in tags
    assert '#ExcitingHashtag' in tags


def _test_first_paragraph_from_string():
    print('testFirstParagraphFromString')
    testStr = \
        '<p><a href="https://somesite.com/somepath">This is a test</a></p>' + \
        '<p>This is another paragraph</p>'
    resultStr = first_paragraph_from_string(testStr)
    if resultStr != 'This is a test':
        print(resultStr)
    assert resultStr == 'This is a test'

    testStr = 'Testing without html'
    resultStr = first_paragraph_from_string(testStr)
    assert resultStr == testStr


def _test_parse_feed_date():
    print('testParseFeedDate')

    pubDate = "2020-12-14T00:08:06+00:00"
    publishedDate = parse_feed_date(pubDate)
    assert publishedDate == "2020-12-14 00:08:06+00:00"

    pubDate = "Tue, 08 Dec 2020 06:24:38 -0600"
    publishedDate = parse_feed_date(pubDate)
    assert publishedDate == "2020-12-08 12:24:38+00:00"

    pubDate = "2020-08-27T16:12:34+00:00"
    publishedDate = parse_feed_date(pubDate)
    assert publishedDate == "2020-08-27 16:12:34+00:00"

    pubDate = "Sun, 22 Nov 2020 19:51:33 +0100"
    publishedDate = parse_feed_date(pubDate)
    assert publishedDate == "2020-11-22 18:51:33+00:00"


def _test_valid_nick():
    print('testValidNickname')
    domain = 'somedomain.net'

    nickname = 'myvalidnick'
    assert valid_nickname(domain, nickname)

    nickname = 'my.invalid.nick'
    assert not valid_nickname(domain, nickname)

    nickname = 'myinvalidnick?'
    assert not valid_nickname(domain, nickname)

    nickname = 'my invalid nick?'
    assert not valid_nickname(domain, nickname)


def _test_guess_tag_category() -> None:
    print('testGuessHashtagCategory')
    hashtagCategories = {
        "foo": ["swan", "goose"],
        "bar": ["cats", "mouse"]
    }
    guess = guess_hashtag_category("unspecifiedgoose", hashtagCategories)
    assert guess == "foo"

    guess = guess_hashtag_category("mastocats", hashtagCategories)
    assert guess == "bar"


def _test_mentioned_people(base_dir: str) -> None:
    print('testGetMentionedPeople')
    content = "@dragon@cave.site @bat@cave.site This is a test."
    actors = get_mentioned_people(base_dir, 'https',
                                  content,
                                  'mydomain', False)
    assert actors
    assert len(actors) == 2
    assert actors[0] == "https://cave.site/users/dragon"
    assert actors[1] == "https://cave.site/users/bat"


def _test_reply_to_public_post(base_dir: str) -> None:
    system_language = 'en'
    nickname = 'test7492362'
    domain = 'other.site'
    port = 443
    http_prefix = 'https'
    post_id = \
        http_prefix + '://rat.site/users/ninjarodent/statuses/63746173435'
    content = "@ninjarodent@rat.site This is a test."
    followersOnly = False
    saveToFile = False
    client_to_server = False
    commentsEnabled = True
    attachImageFilename = None
    mediaType = None
    imageDescription = 'Some description'
    city = 'London, England'
    testInReplyTo = post_id
    testInReplyToAtomUri = None
    testSubject = None
    testSchedulePost = False
    testEventDate = None
    testEventTime = None
    testLocation = None
    testIsArticle = False
    conversationId = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    reply = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content, followersOnly, saveToFile,
                           client_to_server, commentsEnabled,
                           attachImageFilename, mediaType,
                           imageDescription, city, testInReplyTo,
                           testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
    # print(str(reply))
    assert reply['object']['content'] == \
        '<p><span class=\"h-card\">' + \
        '<a href=\"https://rat.site/@ninjarodent\" ' + \
        'class=\"u-url mention\">@<span>ninjarodent</span>' + \
        '</a></span> This is a test.</p>'
    reply['object']['contentMap'][system_language] = reply['object']['content']
    assert reply['object']['tag'][0]['type'] == 'Mention'
    assert reply['object']['tag'][0]['name'] == '@ninjarodent@rat.site'
    assert reply['object']['tag'][0]['href'] == 'https://rat.site/@ninjarodent'
    assert len(reply['object']['to']) == 1
    assert reply['object']['to'][0].endswith('#Public')
    assert len(reply['object']['cc']) >= 1
    assert reply['object']['cc'][0].endswith(nickname + '/followers')
    assert len(reply['object']['tag']) == 1
    if len(reply['object']['cc']) != 2:
        print('reply["object"]["cc"]: ' + str(reply['object']['cc']))
    assert len(reply['object']['cc']) == 2
    assert reply['object']['cc'][1] == \
        http_prefix + '://rat.site/users/ninjarodent'

    assert len(reply['to']) == 1
    assert reply['to'][0].endswith('#Public')
    assert len(reply['cc']) >= 1
    assert reply['cc'][0].endswith(nickname + '/followers')
    if len(reply['cc']) != 2:
        print('reply["cc"]: ' + str(reply['cc']))
    assert len(reply['cc']) == 2
    assert reply['cc'][1] == http_prefix + '://rat.site/users/ninjarodent'


def _get_function_call_args(name: str, lines: [], startLineCtr: int) -> []:
    """Returns the arguments of a function call given lines
    of source code and a starting line number
    """
    argsStr = lines[startLineCtr].split(name + '(')[1]
    if ')' in argsStr:
        argsStr = argsStr.split(')')[0].replace(' ', '').split(',')
        return argsStr
    for lineCtr in range(startLineCtr + 1, len(lines)):
        if ')' not in lines[lineCtr]:
            argsStr += lines[lineCtr]
            continue
        else:
            argsStr += lines[lineCtr].split(')')[0]
            break
    return argsStr.replace('\n', '').replace(' ', '').split(',')


def get_function_calls(name: str, lines: [], startLineCtr: int,
                       functionProperties: {}) -> []:
    """Returns the functions called by the given one,
    Starting with the given source code at the given line
    """
    callsFunctions = []
    functionContentStr = ''
    for lineCtr in range(startLineCtr + 1, len(lines)):
        lineStr = lines[lineCtr].strip()
        if lineStr.startswith('def '):
            break
        if lineStr.startswith('class '):
            break
        functionContentStr += lines[lineCtr]
    for funcName, properties in functionProperties.items():
        if funcName + '(' in functionContentStr:
            callsFunctions.append(funcName)
    return callsFunctions


def _function_args_match(callArgs: [], funcArgs: []):
    """Do the function artuments match the function call arguments
    """
    if len(callArgs) == len(funcArgs):
        return True

    # count non-optional arguments
    callArgsCtr = 0
    for a in callArgs:
        if a == 'self':
            continue
        if '=' not in a or a.startswith("'"):
            callArgsCtr += 1

    funcArgsCtr = 0
    for a in funcArgs:
        if a == 'self':
            continue
        if '=' not in a or a.startswith("'"):
            funcArgsCtr += 1

    return callArgsCtr >= funcArgsCtr


def _module_in_groups(modName: str, includeGroups: [], modGroups: {}) -> bool:
    """Is the given module within the included groups list?
    """
    for groupName in includeGroups:
        if modName in modGroups[groupName]:
            return True
    return False


def _diagram_groups(includeGroups: [],
                    excludeExtraModules: [],
                    modules: {}, modGroups: {},
                    maxModuleCalls: int) -> None:
    """Draws a dot diagram containing only the given module groups
    """
    callGraphStr = 'digraph EpicyonGroups {\n\n'
    callGraphStr += '  graph [fontsize=10 fontname="Verdana" compound=true];\n'
    callGraphStr += '  node [fontsize=10 fontname="Verdana"];\n\n'
    excludeModulesFromDiagram = [
        'setup', 'tests', '__init__', 'pyjsonld'
    ]
    excludeModulesFromDiagram += excludeExtraModules
    # colors of modules nodes
    for modName, modProperties in modules.items():
        if modName in excludeModulesFromDiagram:
            continue
        if not _module_in_groups(modName, includeGroups, modGroups):
            continue
        if not modProperties.get('calls'):
            callGraphStr += '  "' + modName + \
                '" [fillcolor=yellow style=filled];\n'
            continue
        if len(modProperties['calls']) <= int(maxModuleCalls / 8):
            callGraphStr += '  "' + modName + \
                '" [fillcolor=green style=filled];\n'
        elif len(modProperties['calls']) < int(maxModuleCalls / 4):
            callGraphStr += '  "' + modName + \
                '" [fillcolor=orange style=filled];\n'
        else:
            callGraphStr += '  "' + modName + \
                '" [fillcolor=red style=filled];\n'
    callGraphStr += '\n'
    # connections between modules
    for modName, modProperties in modules.items():
        if modName in excludeModulesFromDiagram:
            continue
        if not _module_in_groups(modName, includeGroups, modGroups):
            continue
        if not modProperties.get('calls'):
            continue
        for modCall in modProperties['calls']:
            if modCall in excludeModulesFromDiagram:
                continue
            if not _module_in_groups(modCall, includeGroups, modGroups):
                continue
            callGraphStr += '  "' + modName + '" -> "' + modCall + '";\n'
    # module groups/clusters
    clusterCtr = 1
    for groupName, groupModules in modGroups.items():
        if groupName not in includeGroups:
            continue
        callGraphStr += '\n'
        callGraphStr += \
            '  subgraph cluster_' + str(clusterCtr) + ' {\n'
        callGraphStr += '    node [style=filled];\n'
        for modName in groupModules:
            if modName not in excludeModulesFromDiagram:
                callGraphStr += '    ' + modName + ';\n'
        callGraphStr += '    label = "' + groupName + '";\n'
        callGraphStr += '    color = blue;\n'
        callGraphStr += '  }\n'
        clusterCtr += 1
    callGraphStr += '\n}\n'
    filename = 'epicyon_groups'
    for groupName in includeGroups:
        filename += '_' + groupName.replace(' ', '-')
    filename += '.dot'
    with open(filename, 'w+') as fp:
        fp.write(callGraphStr)
        print('Graph saved to ' + filename)
        print('Plot using: ' +
              'sfdp -x -Goverlap=false -Goverlap_scaling=2 ' +
              '-Gsep=+100 -Tx11 epicyon_modules.dot')


def _test_post_variable_names():
    print('testPostVariableNames')

    for subdir, dirs, files in os.walk('.'):
        for source_file in files:
            if not source_file.endswith('.py'):
                continue
            if source_file.startswith('.#'):
                continue
            if source_file.startswith('flycheck_'):
                continue
            source_str = ''
            with open(source_file, 'r') as file_source:
                source_str = file_source.read()
            if not source_str:
                continue
            if ' name="' not in source_str:
                continue
            names_list = source_str.split(' name="')
            for index in range(1, len(names_list)):
                if '"' not in names_list[index]:
                    continue
                name_var = names_list[index].split('"')[0]
                if not name_var:
                    continue
                if ' ' in name_var:
                    continue
                if '_' in name_var:
                    print(name_var + ' is not camel case POST variable in ' +
                          source_file)
                    assert False
        break


def _test_config_param_names():
    print('testConfigParamNames')

    fnames = ('get_config_param', 'set_config_param')
    for subdir, dirs, files in os.walk('.'):
        for source_file in files:
            if not source_file.endswith('.py'):
                continue
            if source_file.startswith('.#'):
                continue
            if source_file.startswith('flycheck_'):
                continue
            source_str = ''
            with open(source_file, 'r') as file_source:
                source_str = file_source.read()
            if not source_str:
                continue
            for fname in fnames:
                if fname + '(' not in source_str:
                    continue
                names_list = source_str.split(fname + '(')
                for index in range(1, len(names_list)):
                    param_var_name = None
                    if '"' in names_list[index]:
                        param_var_name = names_list[index].split('"')[1]
                    elif "'" in names_list[index]:
                        param_var_name = names_list[index].split("'")[1]
                    if not param_var_name:
                        continue
                    if ' ' in param_var_name:
                        continue
                    if '.' in param_var_name:
                        continue
                    if '/' in param_var_name:
                        continue
                    if '__' in param_var_name:
                        continue
                    if 'POST' in param_var_name:
                        continue
                    if param_var_name.isdigit():
                        continue
                    if '_' in param_var_name:
                        print(fname + ' in ' + source_file +
                              ' should have camel case variable ' +
                              param_var_name)
                        assert False
        break


def _test_source_contains_no_tabs():
    print('testSourceContainsNoTabs')

    for subdir, dirs, files in os.walk('.'):
        for source_file in files:
            if not source_file.endswith('.py'):
                continue
            if source_file.startswith('.#'):
                continue
            if source_file.startswith('flycheck_'):
                continue
            source_str = ''
            with open(source_file, 'r') as file_source:
                source_str = file_source.read()
            if not source_str:
                continue
            if '\t' in source_str:
                print(source_file + ' contains tabs')
                assert False
        break


def _test_checkbox_names():
    print('testCheckboxNames')

    fnames = ['edit_text_field', 'edit_check_box', 'edit_text_area']
    for subdir, dirs, files in os.walk('.'):
        for source_file in files:
            if not source_file.endswith('.py'):
                continue
            if source_file.startswith('.#'):
                continue
            if source_file.startswith('flycheck_'):
                continue
            source_str = ''
            with open(source_file, 'r') as file_source:
                source_str = file_source.read()
            if not source_str:
                continue
            for fname in fnames:
                if fname + '(' not in source_str:
                    continue
                names_list = source_str.split(fname + '(')
                for index in range(1, len(names_list)):
                    if ')' not in names_list[index]:
                        continue
                    allparams = names_list[index].split(')')[0]
                    if ',' not in allparams:
                        continue
                    allparams_list = allparams.split(',')
                    if len(allparams_list) < 2:
                        continue
                    param_var_name = allparams_list[1].strip()
                    param_var_name = param_var_name.replace('"', '')
                    param_var_name = param_var_name.replace("'", '')
                    if ' ' in param_var_name:
                        continue
                    if '/' in param_var_name:
                        continue
                    if '_' in param_var_name:
                        print(fname + ' in ' + source_file +
                              ' should have camel case variable ' +
                              param_var_name)
                        assert False
        break


def _test_post_field_names():
    print('testPOSTfieldNames')

    fnames = ['fields.get']
    source_file = 'daemon.py'
    source_str = ''
    with open(source_file, 'r') as file_source:
        source_str = file_source.read()
    if not source_str:
        return
    for fname in fnames:
        if fname + '(' not in source_str:
            continue
        names_list = source_str.split(fname + '(')
        for index in range(1, len(names_list)):
            if ')' not in names_list[index]:
                continue
            param_var_name = names_list[index].split(')')[0].strip()
            orig_param_var_name = fname + '(' + param_var_name + ')'
            param_var_name = param_var_name.replace('"', '')
            param_var_name = param_var_name.replace("'", '')
            if ' ' in param_var_name:
                continue
            if '/' in param_var_name:
                continue
            if '_' in param_var_name:
                print(orig_param_var_name + ' in ' + source_file +
                      ' should be camel case')
                assert False

    if ' fields[' in source_str:
        names_list = source_str.split(' fields[')
        for index in range(1, len(names_list)):
            if ']' not in names_list[index]:
                continue
            param_var_name = names_list[index].split(']')[0].strip()
            if '"' not in param_var_name and \
               "'" not in param_var_name:
                continue
            orig_param_var_name = 'fields[' + param_var_name + ']'
            param_var_name = param_var_name.replace('"', '')
            param_var_name = param_var_name.replace("'", '')
            if '_' in param_var_name:
                print(orig_param_var_name + ' in ' + source_file +
                      ' should be camel case')
                assert False


def _test_functions():
    print('testFunctions')
    function = {}
    functionProperties = {}
    modules = {}
    modGroups = {}
    methodLOC = []

    for subdir, dirs, files in os.walk('.'):
        for sourceFile in files:
            if not sourceFile.endswith('.py'):
                continue
            if sourceFile.startswith('.#'):
                continue
            if sourceFile.startswith('flycheck_'):
                continue
            modName = sourceFile.replace('.py', '')
            modules[modName] = {
                'functions': []
            }
            sourceStr = ''
            with open(sourceFile, 'r') as f:
                sourceStr = f.read()
                modules[modName]['source'] = sourceStr
            with open(sourceFile, 'r') as f:
                lines = f.readlines()
                modules[modName]['lines'] = lines
                lineCount = 0
                prevLine = 'start'
                methodName = ''
                for line in lines:
                    if '__module_group__' in line:
                        if '=' in line:
                            groupName = line.split('=')[1].strip()
                            groupName = groupName.replace('"', '')
                            groupName = groupName.replace("'", '')
                            modules[modName]['group'] = groupName
                            if not modGroups.get(groupName):
                                modGroups[groupName] = [modName]
                            else:
                                if modName not in modGroups[groupName]:
                                    modGroups[groupName].append(modName)
                    if not line.strip().startswith('def '):
                        if lineCount > 0:
                            lineCount += 1
                        # add LOC count for this function
                        if len(prevLine.strip()) == 0 and \
                           len(line.strip()) == 0 and \
                           lineCount > 2:
                            lineCount -= 2
                            if lineCount > 80:
                                locStr = str(lineCount) + ';' + methodName
                                if lineCount < 1000:
                                    locStr = '0' + locStr
                                if lineCount < 100:
                                    locStr = '0' + locStr
                                if lineCount < 10:
                                    locStr = '0' + locStr
                                if locStr not in methodLOC:
                                    methodLOC.append(locStr)
                                    lineCount = 0
                        prevLine = line
                        continue
                    prevLine = line
                    lineCount = 1
                    methodName = line.split('def ', 1)[1].split('(')[0]
                    methodArgs = \
                        sourceStr.split('def ' + methodName + '(')[1]
                    methodArgs = methodArgs.split(')')[0]
                    methodArgs = methodArgs.replace(' ', '').split(',')
                    if function.get(modName):
                        function[modName].append(methodName)
                    else:
                        function[modName] = [methodName]
                    if methodName not in modules[modName]['functions']:
                        modules[modName]['functions'].append(methodName)
                    functionProperties[methodName] = {
                        "args": methodArgs,
                        "module": modName,
                        "calledInModule": []
                    }
                # LOC count for the last function
                if lineCount > 2:
                    lineCount -= 2
                    if lineCount > 80:
                        locStr = str(lineCount) + ';' + methodName
                        if lineCount < 1000:
                            locStr = '0' + locStr
                        if lineCount < 100:
                            locStr = '0' + locStr
                        if lineCount < 10:
                            locStr = '0' + locStr
                        if locStr not in methodLOC:
                            methodLOC.append(locStr)
        break

    print('LOC counts:')
    methodLOC.sort()
    for locStr in methodLOC:
        print(locStr.split(';')[0] + ' ' + locStr.split(';')[1])

    excludeFuncArgs = [
        'pyjsonld'
    ]
    excludeFuncs = [
        'link',
        'set',
        'get'
    ]

    bad_function_names = []
    for name, properties in functionProperties.items():
        if '_' not in name:
            if name.lower() != name:
                bad_function_names.append(name)
        else:
            if name.startswith('_'):
                name2 = name[1:]
                if '_' not in name2:
                    if name2.lower() != name2:
                        bad_function_names.append(name)
    if bad_function_names:
        bad_function_names2 = \
            sorted(bad_function_names, key=len, reverse=True)
        function_names_str = ''
        function_names_sh = ''
        ctr = 0
        for name in bad_function_names2:
            if ctr > 0:
                function_names_str += '\n' + name
            else:
                function_names_str = name
            snake_case_name = convert_to_snake_case(name)
            function_names_sh += \
                'sed -i "s|' + name + '|' + snake_case_name + '|g" *.py\n'
            ctr += 1
        print(function_names_str + '\n')
        with open('scripts/bad_function_names.sh', 'w+') as fn_file:
            fn_file.write(function_names_sh)
        assert False

    # which modules is each function used within?
    for modName, modProperties in modules.items():
        print('Module: ' + modName + ' ✓')
        for name, properties in functionProperties.items():
            lineCtr = 0
            for line in modules[modName]['lines']:
                lineStr = line.strip()
                if lineStr.startswith('def '):
                    lineCtr += 1
                    continue
                if lineStr.startswith('class '):
                    lineCtr += 1
                    continue
                if name + '(' in line:
                    modList = \
                        functionProperties[name]['calledInModule']
                    if modName not in modList:
                        modList.append(modName)
                    if modName in excludeFuncArgs:
                        lineCtr += 1
                        continue
                    if name in excludeFuncs:
                        lineCtr += 1
                        continue
                    callArgs = \
                        _get_function_call_args(name,
                                                modules[modName]['lines'],
                                                lineCtr)
                    funcArgs = functionProperties[name]['args']
                    if not _function_args_match(callArgs, funcArgs):
                        print('Call to function ' + name +
                              ' does not match its arguments')
                        print('def args: ' +
                              str(len(functionProperties[name]['args'])) +
                              '\n' + str(functionProperties[name]['args']))
                        print('Call args: ' + str(len(callArgs)) + '\n' +
                              str(callArgs))
                        print('module ' + modName + ' line ' + str(lineCtr))
                        assert False
                lineCtr += 1

    # don't check these functions, because they are procedurally called
    exclusions = [
        'do_GET',
        'do_POST',
        'do_HEAD',
        '__run',
        '_send_to_named_addresses',
        'globaltrace',
        'localtrace',
        'kill',
        'clone',
        'unregister_rdf_parser',
        'set_document_loader',
        'has_property',
        'has_value',
        'add_value',
        'get_values',
        'remove_property',
        'remove_value',
        'normalize',
        'get_document_loader',
        'run_inbox_queue_watchdog',
        'run_inbox_queue',
        'run_post_schedule',
        'run_post_schedule_watchdog',
        'str2bool',
        'run_newswire_daemon',
        'run_newswire_watchdog',
        'run_federated_shares_watchdog',
        'run_federated_shares_daemon',
        'fitness_thread',
        'thread_send_post',
        'send_to_followers',
        'expire_cache',
        'get_mutuals_of_person',
        'run_posts_queue',
        'run_shares_expire',
        'run_posts_watchdog',
        'run_shares_expire_watchdog',
        'get_this_weeks_events',
        'get_availability',
        '_test_threads_function',
        'create_server_group',
        'create_server_alice',
        'create_server_bob',
        'create_server_eve',
        'e2e_eremove_device',
        'setOrganizationScheme',
        'fill_headers',
        '_nothing'
    ]
    excludeImports = [
        'link',
        'start'
    ]
    excludeLocal = [
        'pyjsonld',
        'daemon',
        'tests'
    ]
    excludeMods = [
        'pyjsonld'
    ]
    # check that functions are called somewhere
    for name, properties in functionProperties.items():
        if name.startswith('__'):
            if name.endswith('__'):
                continue
        if name in exclusions:
            continue
        if properties['module'] in excludeMods:
            continue
        isLocalFunction = False
        if not properties['calledInModule']:
            print('function ' + name +
                  ' in module ' + properties['module'] +
                  ' is not called anywhere')
        assert properties['calledInModule']

        if len(properties['calledInModule']) == 1:
            modName = properties['calledInModule'][0]
            if modName not in excludeLocal and \
               modName == properties['module']:
                isLocalFunction = True
                if not name.startswith('_'):
                    print('Local function ' + name +
                          ' in ' + modName + '.py does not begin with _')
                    assert False

        if name not in excludeImports:
            for modName in properties['calledInModule']:
                if modName == properties['module']:
                    continue
                importStr = 'from ' + properties['module'] + ' import ' + name
                if importStr not in modules[modName]['source']:
                    print(importStr + ' not found in ' + modName + '.py')
                    assert False

        if not isLocalFunction:
            if name.startswith('_'):
                excludePublic = [
                    'pyjsonld',
                    'daemon',
                    'tests'
                ]
                modName = properties['module']
                if modName not in excludePublic:
                    print('Public function ' + name + ' in ' +
                          modName + '.py begins with _')
                    assert False
        print('Function: ' + name + ' ✓')

    print('Constructing function call graph')
    moduleColors = (
        'red', 'green', 'yellow', 'orange', 'purple', 'cyan',
        'darkgoldenrod3', 'darkolivegreen1', 'darkorange1',
        'darkorchid1', 'darkseagreen', 'darkslategray4',
        'deeppink1', 'deepskyblue1', 'dimgrey', 'gold1',
        'goldenrod', 'burlywood2', 'bisque1', 'brown1',
        'chartreuse2', 'cornsilk', 'darksalmon'
    )
    maxModuleCalls = 1
    maxFunctionCalls = 1
    colorCtr = 0
    for modName, modProperties in modules.items():
        lineCtr = 0
        modules[modName]['color'] = moduleColors[colorCtr]
        colorCtr += 1
        if colorCtr >= len(moduleColors):
            colorCtr = 0
        for line in modules[modName]['lines']:
            if line.strip().startswith('def '):
                name = line.split('def ')[1].split('(')[0]
                callsList = \
                    get_function_calls(name, modules[modName]['lines'],
                                       lineCtr, functionProperties)
                functionProperties[name]['calls'] = callsList.copy()
                if len(callsList) > maxFunctionCalls:
                    maxFunctionCalls = len(callsList)
                # keep track of which module calls which other module
                for fn in callsList:
                    modCall = functionProperties[fn]['module']
                    if modCall != modName:
                        if modules[modName].get('calls'):
                            if modCall not in modules[modName]['calls']:
                                modules[modName]['calls'].append(modCall)
                                if len(modules[modName]['calls']) > \
                                   maxModuleCalls:
                                    maxModuleCalls = \
                                        len(modules[modName]['calls'])
                        else:
                            modules[modName]['calls'] = [modCall]
            lineCtr += 1

    _diagram_groups(['Commandline Interface', 'ActivityPub'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Commandline Interface', 'Core'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Timeline', 'Core'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Web Interface', 'Core'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Web Interface Columns', 'Core'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Core'], [],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['ActivityPub'], [],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['ActivityPub', 'Core'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['ActivityPub', 'Security'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Core', 'Security'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Timeline', 'Security'], ['utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Web Interface', 'Accessibility'],
                    ['utils', 'webapp_utils'],
                    modules, modGroups, maxModuleCalls)
    _diagram_groups(['Core', 'Accessibility'], ['utils'],
                    modules, modGroups, maxModuleCalls)


def _test_links_within_post(base_dir: str) -> None:
    system_language = 'en'
    nickname = 'test27636'
    domain = 'rando.site'
    port = 443
    http_prefix = 'https'
    content = 'This is a test post with links.\n\n' + \
        'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v4/\n\nhttps://libreserver.org'
    followersOnly = False
    saveToFile = False
    client_to_server = False
    commentsEnabled = True
    attachImageFilename = None
    mediaType = None
    imageDescription = None
    city = 'London, England'
    testInReplyTo = None
    testInReplyToAtomUri = None
    testSubject = None
    testSchedulePost = False
    testEventDate = None
    testEventTime = None
    testLocation = None
    testIsArticle = False
    conversationId = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    post_json_object = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content, followersOnly, saveToFile,
                           client_to_server, commentsEnabled,
                           attachImageFilename, mediaType,
                           imageDescription, city,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)

    assert post_json_object['object']['content'] == \
        '<p>This is a test post with links.<br><br>' + \
        '<a href="ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v4/" ' + \
        'rel="nofollow noopener noreferrer" target="_blank">' + \
        '<span class="invisible">ftp://</span>' + \
        '<span class="ellipsis">' + \
        'ftp.ncdc.noaa.gov/pub/data/ghcn/v4/</span>' + \
        '</a><br><br><a href="https://libreserver.org" ' + \
        'rel="nofollow noopener noreferrer" target="_blank">' + \
        '<span class="invisible">https://</span>' + \
        '<span class="ellipsis">libreserver.org</span></a></p>'
    assert post_json_object['object']['content'] == \
        post_json_object['object']['contentMap'][system_language]

    content = "<p>Some text</p><p>Other text</p><p>More text</p>" + \
        "<pre><code>Errno::EOHNOES (No such file or rodent @ " + \
        "ik_right - /tmp/blah.png)<br></code></pre><p>" + \
        "(<a href=\"https://welllookeyhere.maam/error.txt\" " + \
        "rel=\"nofollow noopener noreferrer\" target=\"_blank\">" + \
        "wuh</a>)</p><p>Oh yeah like for sure</p>" + \
        "<p>Ground sloth tin opener</p>" + \
        "<p><a href=\"https://whocodedthis.huh/tags/" + \
        "taggedthing\" class=\"mention hashtag\" rel=\"tag\" " + \
        "target=\"_blank\">#<span>taggedthing</span></a></p>"
    post_json_object = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content,
                           False, False,
                           False, True,
                           None, None,
                           False, None,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
    assert post_json_object['object']['content'] == content
    assert post_json_object['object']['contentMap'][system_language] == content


def _test_mastoapi():
    print('testMastoApi')
    nickname = 'ThisIsATestNickname'
    mastoId = get_masto_api_v1id_from_nickname(nickname)
    assert(mastoId)
    nickname2 = get_nickname_from_masto_api_v1id(mastoId)
    if nickname2 != nickname:
        print(nickname + ' != ' + nickname2)
    assert nickname2 == nickname


def _test_domain_handling():
    print('testDomainHandling')
    testDomain = 'localhost'
    assert decoded_host(testDomain) == testDomain
    testDomain = '127.0.0.1:60'
    assert decoded_host(testDomain) == testDomain
    testDomain = '192.168.5.153'
    assert decoded_host(testDomain) == testDomain
    testDomain = 'xn--espaa-rta.icom.museum'
    assert decoded_host(testDomain) == "españa.icom.museum"


def _test_prepare_html_post_nick():
    print('testPrepareHtmlPostNickname')
    postHtml = '<a class="imageAnchor" href="/users/bob?replyfollowers='
    postHtml += '<a class="imageAnchor" href="/users/bob?repeatprivate='
    result = prepare_html_post_nickname('alice', postHtml)
    assert result == postHtml.replace('/bob?', '/alice?')

    postHtml = '<a class="imageAnchor" href="/users/bob?replyfollowers='
    postHtml += '<a class="imageAnchor" href="/users/bob;repeatprivate='
    expectedHtml = '<a class="imageAnchor" href="/users/alice?replyfollowers='
    expectedHtml += '<a class="imageAnchor" href="/users/bob;repeatprivate='
    result = prepare_html_post_nickname('alice', postHtml)
    assert result == expectedHtml


def _test_valid_hash_tag():
    print('testValidHashTag')
    assert valid_hash_tag('ThisIsValid')
    assert valid_hash_tag('ThisIsValid12345')
    assert valid_hash_tag('ThisIsVälid')
    assert valid_hash_tag('यहमान्यहै')
    assert not valid_hash_tag('ThisIsNotValid!')
    assert not valid_hash_tag('#ThisIsAlsoNotValid')
    assert not valid_hash_tag('#यहमान्यहै')
    assert not valid_hash_tag('ThisIsAlso&NotValid')
    assert not valid_hash_tag('ThisIsAlsoNotValid"')
    assert not valid_hash_tag('This Is Also Not Valid"')
    assert not valid_hash_tag('This=IsAlsoNotValid"')


def _test_markdown_to_html():
    print('testMarkdownToHtml')
    markdown = 'This is just plain text'
    assert markdown_to_html(markdown) == markdown

    markdown = 'This is a quotation:\n' + \
        '> Some quote or other'
    assert markdown_to_html(markdown) == 'This is a quotation:<br>' + \
        '<blockquote><i>Some quote or other</i></blockquote>'

    markdown = 'This is a multi-line quotation:\n' + \
        '> The first line\n' + \
        '> The second line'
    assert markdown_to_html(markdown) == \
        'This is a multi-line quotation:<br>' + \
        '<blockquote><i>The first line The second line</i></blockquote>'

    markdown = 'This is **bold**'
    assert markdown_to_html(markdown) == 'This is <b>bold</b>'

    markdown = 'This is *italic*'
    assert markdown_to_html(markdown) == 'This is <i>italic</i>'

    markdown = 'This is _underlined_'
    assert markdown_to_html(markdown) == 'This is <ul>underlined</ul>'

    markdown = 'This is **just** plain text'
    assert markdown_to_html(markdown) == 'This is <b>just</b> plain text'

    markdown = '# Title1\n### Title3\n## Title2\n'
    assert markdown_to_html(markdown) == \
        '<h1>Title1</h1><h3>Title3</h3><h2>Title2</h2>'

    markdown = \
        'This is [a link](https://something.somewhere) to something.\n' + \
        'And [something else](https://cat.pic).\n' + \
        'Or ![pounce](/cat.jpg).'
    assert markdown_to_html(markdown) == \
        'This is <a href="https://something.somewhere" ' + \
        'target="_blank" rel="nofollow noopener noreferrer">' + \
        'a link</a> to something.<br>' + \
        'And <a href="https://cat.pic" ' + \
        'target="_blank" rel="nofollow noopener noreferrer">' + \
        'something else</a>.<br>' + \
        'Or <img class="markdownImage" src="/cat.jpg" alt="pounce" />.'


def _test_extract_text_fields_from_post():
    print('testExtractTextFieldsInPOST')
    boundary = '-----------------------------116202748023898664511855843036'
    formData = '-----------------------------116202748023898664511855' + \
        '843036\r\nContent-Disposition: form-data; name="submitPost"' + \
        '\r\n\r\nSubmit\r\n-----------------------------116202748023' + \
        '898664511855843036\r\nContent-Disposition: form-data; name=' + \
        '"subject"\r\n\r\n\r\n-----------------------------116202748' + \
        '023898664511855843036\r\nContent-Disposition: form-data; na' + \
        'me="message"\r\n\r\nThis is a ; test\r\n-------------------' + \
        '----------116202748023898664511855843036\r\nContent-Disposi' + \
        'tion: form-data; name="commentsEnabled"\r\n\r\non\r\n------' + \
        '-----------------------116202748023898664511855843036\r\nCo' + \
        'ntent-Disposition: form-data; name="eventDate"\r\n\r\n\r\n' + \
        '-----------------------------116202748023898664511855843036' + \
        '\r\nContent-Disposition: form-data; name="eventTime"\r\n\r' + \
        '\n\r\n-----------------------------116202748023898664511855' + \
        '843036\r\nContent-Disposition: form-data; name="location"' + \
        '\r\n\r\n\r\n-----------------------------116202748023898664' + \
        '511855843036\r\nContent-Disposition: form-data; name=' + \
        '"imageDescription"\r\n\r\n\r\n-----------------------------' + \
        '116202748023898664511855843036\r\nContent-Disposition: ' + \
        'form-data; name="attachpic"; filename=""\r\nContent-Type: ' + \
        'application/octet-stream\r\n\r\n\r\n----------------------' + \
        '-------116202748023898664511855843036--\r\n'
    debug = False
    fields = extract_text_fields_in_post(None, boundary, debug, formData)
    assert fields['submitPost'] == 'Submit'
    assert fields['subject'] == ''
    assert fields['commentsEnabled'] == 'on'
    assert fields['eventDate'] == ''
    assert fields['eventTime'] == ''
    assert fields['location'] == ''
    assert fields['imageDescription'] == ''
    assert fields['message'] == 'This is a ; test'


def _test_speaker_replace_link():
    print('testSpeakerReplaceLinks')
    text = 'The Tor Project: For Snowflake volunteers: If you use ' + \
        'Firefox, Brave, or Chrome, our Snowflake extension turns ' + \
        'your browser into a proxy that connects Tor users in ' + \
        'censored regions to the Tor network. Note: you should ' + \
        'not run more than one snowflake in the same ' + \
        'network.https://support.torproject.org/censorship/' + \
        'how-to-help-running-snowflake/'
    detectedLinks = []
    result = speaker_replace_links(text, {'Linked': 'Web link'}, detectedLinks)
    assert len(detectedLinks) == 1
    assert detectedLinks[0] == \
        'https://support.torproject.org/censorship/' + \
        'how-to-help-running-snowflake/'
    assert 'Web link support.torproject.org' in result


def _test_camel_case_split():
    print('testCamelCaseSplit')
    testStr = 'ThisIsCamelCase'
    assert camel_case_split(testStr) == 'This Is Camel Case'

    testStr = 'Notcamelcase test'
    assert camel_case_split(testStr) == 'Notcamelcase test'


def _test_emoji_images():
    print('testEmojiImages')
    emojiFilename = 'emoji/default_emoji.json'
    assert os.path.isfile(emojiFilename)
    emojiJson = load_json(emojiFilename)
    assert emojiJson
    for emojiName, emojiImage in emojiJson.items():
        emojiImageFilename = 'emoji/' + emojiImage + '.png'
        if not os.path.isfile(emojiImageFilename):
            print('Missing emoji image ' + emojiName + ' ' +
                  emojiImage + '.png')
        assert os.path.isfile(emojiImageFilename)


def _test_extract_pgp_public_key():
    print('testExtractPGPPublicKey')
    pubKey = \
        '-----BEGIN PGP PUBLIC KEY BLOCK-----\n\n' + \
        'mDMEWZBueBYJKwYBBAHaRw8BAQdAKx1t6wL0RTuU6/' + \
        'IBjngMbVJJ3Wg/3UW73/PV\n' + \
        'I47xKTS0IUJvYiBNb3R0cmFtIDxib2JAZnJlZWRvb' + \
        'WJvbmUubmV0PoiQBBMWCAA4\n' + \
        'FiEEmruCwAq/OfgmgEh9zCU2GR+nwz8FAlmQbngCG' + \
        'wMFCwkIBwMFFQoJCAsFFgID\n' + \
        'AQACHgECF4AACgkQzCU2GR+nwz/9sAD/YgsHnVszH' + \
        'Nz1zlVc5EgY1ByDupiJpHj0\n' + \
        'XsLYk3AbNRgBALn45RqgD4eWHpmOriH09H5Rc5V9i' + \
        'N4+OiGUn2AzJ6oHuDgEWZBu\n' + \
        'eBIKKwYBBAGXVQEFAQEHQPRBG2ZQJce475S3e0Dxe' + \
        'b0Fz5WdEu2q3GYLo4QG+4Ry\n' + \
        'AwEIB4h4BBgWCAAgFiEEmruCwAq/OfgmgEh9zCU2G' + \
        'R+nwz8FAlmQbngCGwwACgkQ\n' + \
        'zCU2GR+nwz+OswD+JOoyBku9FzuWoVoOevU2HH+bP' + \
        'OMDgY2OLnST9ZSyHkMBAMcK\n' + \
        'fnaZ2Wi050483Sj2RmQRpb99Dod7rVZTDtCqXk0J\n' + \
        '=gv5G\n' + \
        '-----END PGP PUBLIC KEY BLOCK-----'
    testStr = "Some introduction\n\n" + pubKey + "\n\nSome message."
    assert contains_pgp_public_key(testStr)
    assert not contains_pgp_public_key('String without a pgp key')
    result = extract_pgp_public_key(testStr)
    assert result
    assert result == pubKey


def test_update_actor(base_dir: str):
    print('Testing update of actor properties')

    global testServerAliceRunning
    testServerAliceRunning = False

    http_prefix = 'http'
    proxy_type = None
    federation_list = []

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests',
                      ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the server
    aliceDir = base_dir + '/.tests/alice'
    aliceDomain = '127.0.0.11'
    alicePort = 61792
    aliceSendThreads = []
    bobAddress = '127.0.0.84:6384'

    global thrAlice
    if thrAlice:
        while thrAlice.is_alive():
            thrAlice.stop()
            time.sleep(1)
        thrAlice.kill()

    thrAlice = \
        thread_with_trace(target=create_server_alice,
                          args=(aliceDir, aliceDomain, alicePort, bobAddress,
                                federation_list, False, False,
                                aliceSendThreads),
                          daemon=True)

    thrAlice.start()
    assert thrAlice.is_alive() is True

    # wait for server to be running
    ctr = 0
    while not testServerAliceRunning:
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(testServerAliceRunning))

    print('\n\n*******************************************************')
    print('Alice updates her PGP key')

    sessionAlice = create_session(proxy_type)
    cached_webfingers = {}
    person_cache = {}
    password = 'alicepass'
    outboxPath = aliceDir + '/accounts/alice@' + aliceDomain + '/outbox'
    actorFilename = aliceDir + '/accounts/' + 'alice@' + aliceDomain + '.json'
    assert os.path.isfile(actorFilename)
    assert len([name for name in os.listdir(outboxPath)
                if os.path.isfile(os.path.join(outboxPath, name))]) == 0
    pubKey = \
        '-----BEGIN PGP PUBLIC KEY BLOCK-----\n\n' + \
        'mDMEWZBueBYJKwYBBAHaRw8BAQdAKx1t6wL0RTuU6/' + \
        'IBjngMbVJJ3Wg/3UW73/PV\n' + \
        'I47xKTS0IUJvYiBNb3R0cmFtIDxib2JAZnJlZWRvb' + \
        'WJvbmUubmV0PoiQBBMWCAA4\n' + \
        'FiEEmruCwAq/OfgmgEh9zCU2GR+nwz8FAlmQbngCG' + \
        'wMFCwkIBwMFFQoJCAsFFgID\n' + \
        'AQACHgECF4AACgkQzCU2GR+nwz/9sAD/YgsHnVszH' + \
        'Nz1zlVc5EgY1ByDupiJpHj0\n' + \
        'XsLYk3AbNRgBALn45RqgD4eWHpmOriH09H5Rc5V9i' + \
        'N4+OiGUn2AzJ6oHuDgEWZBu\n' + \
        'eBIKKwYBBAGXVQEFAQEHQPRBG2ZQJce475S3e0Dxe' + \
        'b0Fz5WdEu2q3GYLo4QG+4Ry\n' + \
        'AwEIB4h4BBgWCAAgFiEEmruCwAq/OfgmgEh9zCU2G' + \
        'R+nwz8FAlmQbngCGwwACgkQ\n' + \
        'zCU2GR+nwz+OswD+JOoyBku9FzuWoVoOevU2HH+bP' + \
        'OMDgY2OLnST9ZSyHkMBAMcK\n' + \
        'fnaZ2Wi050483Sj2RmQRpb99Dod7rVZTDtCqXk0J\n' + \
        '=gv5G\n' + \
        '-----END PGP PUBLIC KEY BLOCK-----'
    signing_priv_key_pem = None
    actorUpdate = \
        pgp_public_key_upload(aliceDir, sessionAlice,
                              'alice', password,
                              aliceDomain, alicePort,
                              http_prefix,
                              cached_webfingers, person_cache,
                              True, pubKey, signing_priv_key_pem)
    print('actor update result: ' + str(actorUpdate))
    assert actorUpdate

    # load alice actor
    print('Loading actor: ' + actorFilename)
    actor_json = load_json(actorFilename)
    assert actor_json
    if len(actor_json['attachment']) == 0:
        print("actor_json['attachment'] has no contents")
    assert len(actor_json['attachment']) > 0
    propertyFound = False
    for property_value in actor_json['attachment']:
        if property_value['name'] == 'PGP':
            print('PGP property set within attachment')
            assert pubKey in property_value['value']
            propertyFound = True
    assert propertyFound

    # stop the server
    thrAlice.kill()
    thrAlice.join()
    assert thrAlice.is_alive() is False

    os.chdir(base_dir)
    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)


def _test_remove_interactions() -> None:
    print('testRemovePostInteractions')
    post_json_object = {
        "type": "Create",
        "object": {
            "to": ["#Public"],
            "likes": {
                "items": ["a", "b", "c"]
            },
            "replies": {
                "replyStuff": ["a", "b", "c"]
            },
            "shares": {
                "sharesStuff": ["a", "b", "c"]
            },
            "bookmarks": {
                "bookmarksStuff": ["a", "b", "c"]
            },
            "ignores": {
                "ignoresStuff": ["a", "b", "c"]
            }
        }
    }
    remove_post_interactions(post_json_object, True)
    assert post_json_object['object']['likes']['items'] == []
    assert post_json_object['object']['replies'] == {}
    assert post_json_object['object']['shares'] == {}
    assert post_json_object['object']['bookmarks'] == {}
    assert post_json_object['object']['ignores'] == {}
    post_json_object['object']['to'] = ["some private address"]
    assert not remove_post_interactions(post_json_object, False)


def _test_spoofed_geolocation() -> None:
    print('testSpoofGeolocation')
    nogoLine = \
        'NEW YORK, USA: 73.951W,40.879,  73.974W,40.83,  ' + \
        '74.029W,40.756,  74.038W,40.713,  74.056W,40.713,  ' + \
        '74.127W,40.647,  74.038W,40.629,  73.995W,40.667,  ' + \
        '74.014W,40.676,  73.994W,40.702,  73.967W,40.699,  ' + \
        '73.958W,40.729,  73.956W,40.745,  73.918W,40.781,  ' + \
        '73.937W,40.793,  73.946W,40.782,  73.977W,40.738,  ' + \
        '73.98W,40.713,  74.012W,40.705,  74.006W,40.752,  ' + \
        '73.955W,40.824'
    polygon = parse_nogo_string(nogoLine)
    assert len(polygon) > 0
    assert polygon[0][1] == -73.951
    assert polygon[0][0] == 40.879
    citiesList = [
        'NEW YORK, USA:40.7127281:W74.0060152:784',
        'LOS ANGELES, USA:34.0536909:W118.242766:1214',
        'SAN FRANCISCO, USA:37.74594738515095:W122.44299445520019:121',
        'HOUSTON, USA:29.6072:W95.1586:1553',
        'MANCHESTER, ENGLAND:53.4794892:W2.2451148:1276',
        'BERLIN, GERMANY:52.5170365:13.3888599:891',
        'ANKARA, TURKEY:39.93:32.85:24521',
        'LONDON, ENGLAND:51.5073219:W0.1276474:1738',
        'SEATTLE, USA:47.59840153253106:W122.31143714060059:217'
    ]
    testSquare = [
        [[0.03, 0.01], [0.02, 10], [10.01, 10.02], [10.03, 0.02]]
    ]
    assert point_in_nogo(testSquare, 5, 5)
    assert point_in_nogo(testSquare, 2, 3)
    assert not point_in_nogo(testSquare, 20, 5)
    assert not point_in_nogo(testSquare, 11, 6)
    assert not point_in_nogo(testSquare, 5, -5)
    assert not point_in_nogo(testSquare, 5, 11)
    assert not point_in_nogo(testSquare, -5, -5)
    assert not point_in_nogo(testSquare, -5, 5)
    nogoList = []
    curr_time = datetime.datetime.utcnow()
    decoySeed = 7634681
    cityRadius = 0.1
    coords = spoof_geolocation('', 'los angeles', curr_time,
                               decoySeed, citiesList, nogoList)
    assert coords[0] >= 34.0536909 - cityRadius
    assert coords[0] <= 34.0536909 + cityRadius
    assert coords[1] >= 118.242766 - cityRadius
    assert coords[1] <= 118.242766 + cityRadius
    assert coords[2] == 'N'
    assert coords[3] == 'W'
    assert len(coords[4]) > 4
    assert len(coords[5]) > 4
    assert coords[6] > 0
    nogoList = []
    coords = spoof_geolocation('', 'unknown', curr_time,
                               decoySeed, citiesList, nogoList)
    assert coords[0] >= 51.8744 - cityRadius
    assert coords[0] <= 51.8744 + cityRadius
    assert coords[1] >= 0.368333 - cityRadius
    assert coords[1] <= 0.368333 + cityRadius
    assert coords[2] == 'N'
    assert coords[3] == 'W'
    assert len(coords[4]) == 0
    assert len(coords[5]) == 0
    assert coords[6] == 0
    kmlStr = '<?xml version="1.0" encoding="UTF-8"?>\n'
    kmlStr += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kmlStr += '<Document>\n'
    nogoLine2 = \
        'NEW YORK, USA: 74.115W,40.663,  74.065W,40.602,  ' + \
        '74.118W,40.555,  74.047W,40.516,  73.882W,40.547,  ' + \
        '73.909W,40.618,  73.978W,40.579,  74.009W,40.602,  ' + \
        '74.033W,40.61,  74.039W,40.623,  74.032W,40.641,  ' + \
        '73.996W,40.665'
    polygon2 = parse_nogo_string(nogoLine2)
    nogoList = [polygon, polygon2]
    for i in range(1000):
        dayNumber = randint(10, 30)
        hour = randint(1, 23)
        hourStr = str(hour)
        if hour < 10:
            hourStr = '0' + hourStr
        dateTimeStr = "2021-05-" + str(dayNumber) + " " + hourStr + ":14"
        curr_time = datetime.datetime.strptime(dateTimeStr, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'new york, usa', curr_time,
                                   decoySeed, citiesList, nogoList)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kmlStr += '<Placemark id="' + str(i) + '">\n'
        kmlStr += '  <name>' + str(i) + '</name>\n'
        kmlStr += '  <Point>\n'
        kmlStr += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kmlStr += '  </Point>\n'
        kmlStr += '</Placemark>\n'

    nogoLine = \
        'LONDON, ENGLAND: 0.23888E,51.459,  0.1216E,51.5,  ' + \
        '0.016E,51.479,  0.097W,51.502,  0.126W,51.482,  ' + \
        '0.196W,51.457,  0.292W,51.465,  0.309W,51.49,  ' + \
        '0.226W,51.495,  0.198W,51.47,  0.174W,51.488,  ' + \
        '0.136W,51.489,  0.1189W,51.515,  0.038E,51.513,  ' + \
        '0.0692E,51.51,  0.12833E,51.526,  0.3289E,51.475'
    polygon = parse_nogo_string(nogoLine)
    nogoLine2 = \
        'LONDON, ENGLAND: 0.054W,51.535,  0.044W,51.53,  ' + \
        '0.008W,51.55,  0.0429W,51.57,  0.038W,51.6,  ' + \
        '0.0209W,51.603,  0.032W,51.613,  0.00191E,51.66,  ' + \
        '0.024W,51.666,  0.0313W,51.659,  0.0639W,51.579,  ' + \
        '0.059W,51.568,  0.0329W,51.552'
    polygon2 = parse_nogo_string(nogoLine2)
    nogoList = [polygon, polygon2]
    for i in range(1000):
        dayNumber = randint(10, 30)
        hour = randint(1, 23)
        hourStr = str(hour)
        if hour < 10:
            hourStr = '0' + hourStr
        dateTimeStr = "2021-05-" + str(dayNumber) + " " + hourStr + ":14"
        curr_time = datetime.datetime.strptime(dateTimeStr, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'london, england', curr_time,
                                   decoySeed, citiesList, nogoList)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kmlStr += '<Placemark id="' + str(i) + '">\n'
        kmlStr += '  <name>' + str(i) + '</name>\n'
        kmlStr += '  <Point>\n'
        kmlStr += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kmlStr += '  </Point>\n'
        kmlStr += '</Placemark>\n'

    nogoLine = \
        'SAN FRANCISCO, USA: 121.988W,37.408,  121.924W,37.452,  ' + \
        '121.951W,37.498,  121.992W,37.505,  122.056W,37.54,  ' + \
        '122.077W,37.578,  122.098W,37.618,  122.131W,37.637,  ' + \
        '122.189W,37.706,  122.227W,37.775,  122.279W,37.798,  ' + \
        '122.315W,37.802,  122.291W,37.832,  122.309W,37.902,  ' + \
        '122.382W,37.915,  122.368W,37.927,  122.514W,37.882,  ' + \
        '122.473W,37.83,  122.481W,37.788,  122.394W,37.796,  ' + \
        '122.384W,37.729,  122.4W,37.688,  122.382W,37.654,  ' + \
        '122.406W,37.637,  122.392W,37.612,  122.356W,37.586,  ' + \
        '122.332W,37.586,  122.275W,37.529,  122.228W,37.488,  ' + \
        '122.181W,37.482,  122.134W,37.48,  122.128W,37.471,  ' + \
        '122.122W,37.448,  122.095W,37.428,  122.07W,37.413,  ' + \
        '122.036W,37.402,  122.035W,37.421'
    polygon = parse_nogo_string(nogoLine)
    nogoLine2 = \
        'SAN FRANCISCO, USA: 122.446W,37.794,  122.511W,37.778,  ' + \
        '122.51W,37.771,  122.454W,37.775,  122.452W,37.766,  ' + \
        '122.510W,37.763,  122.506W,37.735,  122.498W,37.733,  ' + \
        '122.496W,37.729,  122.491W,37.729,  122.475W,37.73,  ' + \
        '122.474W,37.72,  122.484W,37.72,  122.485W,37.703,  ' + \
        '122.495W,37.702,  122.493W,37.679,  122.486W,37.667,  ' + \
        '122.492W,37.664,  122.493W,37.629,  122.456W,37.625,  ' + \
        '122.450W,37.617,  122.455W,37.621,  122.41W,37.586,  ' + \
        '122.383W,37.561,  122.335W,37.509,  122.655W,37.48,  ' + \
        '122.67W,37.9,  122.272W,37.93,  122.294W,37.801,  ' + \
        '122.448W,37.804'
    polygon2 = parse_nogo_string(nogoLine2)
    nogoList = [polygon, polygon2]
    for i in range(1000):
        dayNumber = randint(10, 30)
        hour = randint(1, 23)
        hourStr = str(hour)
        if hour < 10:
            hourStr = '0' + hourStr
        dateTimeStr = "2021-05-" + str(dayNumber) + " " + hourStr + ":14"
        curr_time = datetime.datetime.strptime(dateTimeStr, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'SAN FRANCISCO, USA', curr_time,
                                   decoySeed, citiesList, nogoList)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kmlStr += '<Placemark id="' + str(i) + '">\n'
        kmlStr += '  <name>' + str(i) + '</name>\n'
        kmlStr += '  <Point>\n'
        kmlStr += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kmlStr += '  </Point>\n'
        kmlStr += '</Placemark>\n'

    nogoLine = \
        'SEATTLE, USA: 122.247W,47.918,  122.39W,47.802,  ' + \
        '122.389W,47.769,  122.377W,47.758,  122.371W,47.726,  ' + \
        '122.379W,47.706,  122.4W,47.696,  122.405W,47.673,  ' + \
        '122.416W,47.65,  122.414W,47.642,  122.391W,47.632,  ' + \
        '122.373W,47.633,  122.336W,47.602,  122.288W,47.501,  ' + \
        '122.299W,47.503,  122.386W,47.592,  122.412W,47.574,  ' + \
        '122.394W,47.549,  122.388W,47.507,  122.35W,47.481,  ' + \
        '122.365W,47.459,  122.33W,47.406,  122.323W,47.392,  ' + \
        '122.321W,47.346,  122.441W,47.302,  122.696W,47.085,  ' + \
        '122.926W,47.066,  122.929W,48.383'
    polygon = parse_nogo_string(nogoLine)
    nogoLine2 = \
        'SEATTLE, USA: 122.267W,47.758,  122.29W,47.471,  ' + \
        '122.272W,47.693,  122.256W,47.672,  122.278W,47.652,  ' + \
        '122.29W,47.583,  122.262W,47.548,  122.265W,47.52,  ' + \
        '122.218W,47.498,  122.194W,47.501,  122.193W,47.55,  ' + \
        '122.173W,47.58,  122.22W,47.617,  122.238W,47.617,  ' + \
        '122.239W,47.637,  122.2W,47.644,  122.207W,47.703,  ' + \
        '122.22W,47.705,  122.231W,47.699,  122.255W,47.751'
    polygon2 = parse_nogo_string(nogoLine2)
    nogoLine3 = \
        'SEATTLE, USA: 122.347W,47.675,  122.344W,47.681,  ' + \
        '122.337W,47.685,  122.324W,47.679,  122.331W,47.677,  ' + \
        '122.34W,47.669,  122.34W,47.664,  122.348W,47.665'
    polygon3 = parse_nogo_string(nogoLine3)
    nogoLine4 = \
        'SEATTLE, USA: 122.423W,47.669,  122.345W,47.641,  ' + \
        '122.34W,47.625,  122.327W,47.626,  122.274W,47.64,  ' + \
        '122.268W,47.654,  122.327W,47.654,  122.336W,47.647,  ' + \
        '122.429W,47.684'
    polygon4 = parse_nogo_string(nogoLine4)
    nogoList = [polygon, polygon2, polygon3, polygon4]
    for i in range(1000):
        dayNumber = randint(10, 30)
        hour = randint(1, 23)
        hourStr = str(hour)
        if hour < 10:
            hourStr = '0' + hourStr
        dateTimeStr = "2021-05-" + str(dayNumber) + " " + hourStr + ":14"
        curr_time = datetime.datetime.strptime(dateTimeStr, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'SEATTLE, USA', curr_time,
                                   decoySeed, citiesList, nogoList)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kmlStr += '<Placemark id="' + str(i) + '">\n'
        kmlStr += '  <name>' + str(i) + '</name>\n'
        kmlStr += '  <Point>\n'
        kmlStr += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kmlStr += '  </Point>\n'
        kmlStr += '</Placemark>\n'

    kmlStr += '</Document>\n'
    kmlStr += '</kml>'
    with open('unittest_decoy.kml', 'w+') as kmlFile:
        kmlFile.write(kmlStr)


def _test_skills() -> None:
    print('testSkills')
    actor_json = {
        'hasOccupation': [
            {
                '@type': 'Occupation',
                'name': "Sysop",
                "occupationLocation": {
                    "@type": "City",
                    "name": "Fediverse"
                },
                'skills': []
            }
        ]
    }
    skillsDict = {
        'bakery': 40,
        'gardening': 70
    }
    set_skills_from_dict(actor_json, skillsDict)
    assert actor_has_skill(actor_json, 'bakery')
    assert actor_has_skill(actor_json, 'gardening')
    assert actor_skill_value(actor_json, 'bakery') == 40
    assert actor_skill_value(actor_json, 'gardening') == 70


def _test_roles() -> None:
    print('testRoles')
    actor_json = {
        'hasOccupation': [
            {
                '@type': 'Occupation',
                'name': "Sysop",
                'occupationLocation': {
                    '@type': 'City',
                    'name': 'Fediverse'
                },
                'skills': []
            }
        ]
    }
    testRolesList = ["admin", "moderator"]
    set_rolesFromList(actor_json, testRolesList)
    assert actor_has_role(actor_json, "admin")
    assert actor_has_role(actor_json, "moderator")
    assert not actor_has_role(actor_json, "editor")
    assert not actor_has_role(actor_json, "counselor")
    assert not actor_has_role(actor_json, "artist")


def _test_useragent_domain() -> None:
    print('testUserAgentDomain')
    userAgent = \
        'http.rb/4.4.1 (Mastodon/9.10.11; +https://mastodon.something/)'
    assert user_agent_domain(userAgent, False) == 'mastodon.something'
    userAgent = \
        'Mozilla/70.0 (X11; Linux x86_64; rv:1.0) Gecko/20450101 Firefox/1.0'
    assert user_agent_domain(userAgent, False) is None


def _test_switch_word(base_dir: str) -> None:
    print('testSwitchWords')
    rules = [
        "rock -> hamster",
        "orange -> lemon"
    ]
    nickname = 'testuser'
    domain = 'testdomain.com'

    content = 'This is a test'
    result = switch_words(base_dir, nickname, domain, content, rules)
    assert result == content

    content = 'This is orange test'
    result = switch_words(base_dir, nickname, domain, content, rules)
    assert result == 'This is lemon test'

    content = 'This is a test rock'
    result = switch_words(base_dir, nickname, domain, content, rules)
    assert result == 'This is a test hamster'


def _test_word_lengths_limit() -> None:
    print('testLimitWordLengths')
    maxWordLength = 13
    text = "This is a test"
    result = limit_word_lengths(text, maxWordLength)
    assert result == text

    text = "This is an exceptionallylongword test"
    result = limit_word_lengths(text, maxWordLength)
    assert result == "This is an exceptionally test"


def _test_limit_repeted_words() -> None:
    print('limit_repeated_words')
    text = \
        "This is a preamble.\n\n" + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same\n\n" + \
        "Some other text."
    expected = \
        "This is a preamble.\n\n" + \
        "Same Same Same Same Same Same\n\n" + \
        "Some other text."
    result = limit_repeated_words(text, 6)
    assert result == expected

    text = \
        "This is other preamble.\n\n" + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same " + \
        "Same Same Same Same Same Same Same Same Same Same"
    expected = \
        "This is other preamble.\n\n" + \
        "Same Same Same Same Same Same"
    result = limit_repeated_words(text, 6)
    assert result == expected


def _test_set_actor_language():
    print('testSetActorLanguages')
    actor_json = {
        "attachment": []
    }
    set_actor_languages(None, actor_json, 'es, fr, en')
    assert len(actor_json['attachment']) == 1
    assert actor_json['attachment'][0]['name'] == 'Languages'
    assert actor_json['attachment'][0]['type'] == 'PropertyValue'
    assert isinstance(actor_json['attachment'][0]['value'], str)
    assert ',' in actor_json['attachment'][0]['value']
    lang_list = get_actor_languages_list(actor_json)
    assert 'en' in lang_list
    assert 'fr' in lang_list
    assert 'es' in lang_list
    languagesStr = get_actor_languages(actor_json)
    assert languagesStr == 'en / es / fr'


def _test_get_links_from_content():
    print('testGetLinksFromContent')
    content = 'This text has no links'
    links = get_links_from_content(content)
    assert not links

    link1 = 'https://somewebsite.net'
    link2 = 'http://somewhere.or.other'
    content = \
        'This is <a href="' + link1 + '">@linked</a>. ' + \
        'And <a href="' + link2 + '">another</a>.'
    links = get_links_from_content(content)
    assert len(links.items()) == 2
    assert links.get('@linked')
    assert links['@linked'] == link1
    assert links.get('another')
    assert links['another'] == link2

    contentPlain = '<p>' + remove_html(content) + '</p>'
    assert '>@linked</a>' not in contentPlain
    content = add_links_to_content(contentPlain, links)
    assert '>@linked</a>' in content


def _test_authorized_shared_items():
    print('testAuthorizeSharedItems')
    shared_items_fed_domains = \
        ['dog.domain', 'cat.domain', 'birb.domain']
    tokensJson = \
        generate_shared_item_federation_tokens(shared_items_fed_domains, None)
    tokensJson = \
        create_shared_item_federation_token(None, 'cat.domain',
                                            False, tokensJson)
    assert tokensJson
    assert not tokensJson.get('dog.domain')
    assert tokensJson.get('cat.domain')
    assert not tokensJson.get('birb.domain')
    assert len(tokensJson['dog.domain']) == 0
    assert len(tokensJson['cat.domain']) >= 64
    assert len(tokensJson['birb.domain']) == 0
    assert not authorize_shared_items(shared_items_fed_domains, None,
                                      'birb.domain',
                                      'cat.domain', 'M' * 86,
                                      False, tokensJson)
    assert authorize_shared_items(shared_items_fed_domains, None,
                                  'birb.domain',
                                  'cat.domain', tokensJson['cat.domain'],
                                  False, tokensJson)
    tokensJson = \
        update_shared_item_federation_token(None,
                                            'dog.domain', 'testToken',
                                            True, tokensJson)
    assert tokensJson['dog.domain'] == 'testToken'

    # the shared item federation list changes
    shared_items_federated_domains = \
        ['possum.domain', 'cat.domain', 'birb.domain']
    tokensJson = merge_shared_item_tokens(None, '',
                                          shared_items_federated_domains,
                                          tokensJson)
    assert 'dog.domain' not in tokensJson
    assert 'cat.domain' in tokensJson
    assert len(tokensJson['cat.domain']) >= 64
    assert 'birb.domain' in tokensJson
    assert 'possum.domain' in tokensJson
    assert len(tokensJson['birb.domain']) == 0
    assert len(tokensJson['possum.domain']) == 0


def _test_date_conversions() -> None:
    print('testDateConversions')
    dateStr = "2021-05-16T14:37:41Z"
    dateSec = date_string_to_seconds(dateStr)
    dateStr2 = date_seconds_to_string(dateSec)
    assert dateStr == dateStr2


def _test_valid_password():
    print('testValidPassword')
    assert not valid_password('123')
    assert not valid_password('')
    assert valid_password('パスワード12345')
    assert valid_password('测试密码12345')
    assert valid_password('A!bc:defg1/234?56')


def _test_get_price_from_string() -> None:
    print('testGetPriceFromString')
    price, curr = get_price_from_string("5.23")
    assert price == "5.23"
    assert curr == "EUR"
    price, curr = get_price_from_string("£7.36")
    assert price == "7.36"
    assert curr == "GBP"
    price, curr = get_price_from_string("$10.63")
    assert price == "10.63"
    assert curr == "USD"


def _translate_ontology(base_dir: str) -> None:
    return
    ontologyTypes = get_category_types(base_dir)
    url = 'https://translate.astian.org'
    apiKey = None
    ltLangList = libretranslate_languages(url, apiKey)

    languagesStr = get_supported_languages(base_dir)
    assert languagesStr

    for oType in ontologyTypes:
        changed = False
        filename = base_dir + '/ontology/' + oType + 'Types.json'
        if not os.path.isfile(filename):
            continue
        ontologyJson = load_json(filename)
        if not ontologyJson:
            continue
        index = -1
        for item in ontologyJson['@graph']:
            index += 1
            if "rdfs:label" not in item:
                continue
            englishStr = None
            languagesFound = []
            for label in item["rdfs:label"]:
                if '@language' not in label:
                    continue
                languagesFound.append(label['@language'])
                if '@value' not in label:
                    continue
                if label['@language'] == 'en':
                    englishStr = label['@value']
            if not englishStr:
                continue
            for lang in languagesStr:
                if lang not in languagesFound:
                    translatedStr = None
                    if url and lang in ltLangList:
                        translatedStr = \
                            libretranslate(url, englishStr, 'en', lang, apiKey)
                    if not translatedStr:
                        translatedStr = englishStr
                    else:
                        translatedStr = translatedStr.replace('<p>', '')
                        translatedStr = translatedStr.replace('</p>', '')
                    ontologyJson['@graph'][index]["rdfs:label"].append({
                        "@value": translatedStr,
                        "@language": lang
                    })
                    changed = True
        if not changed:
            continue
        save_json(ontologyJson, filename + '.new')


def _test_can_replyto(base_dir: str) -> None:
    print('testCanReplyTo')
    system_language = 'en'
    nickname = 'test27637'
    domain = 'rando.site'
    port = 443
    http_prefix = 'https'
    content = 'This is a test post with links.\n\n' + \
        'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v4/\n\nhttps://libreserver.org'
    followersOnly = False
    saveToFile = False
    client_to_server = False
    commentsEnabled = True
    attachImageFilename = None
    mediaType = None
    imageDescription = None
    city = 'London, England'
    testInReplyTo = None
    testInReplyToAtomUri = None
    testSubject = None
    testSchedulePost = False
    testEventDate = None
    testEventTime = None
    testLocation = None
    testIsArticle = False
    conversationId = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    post_json_object = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content, followersOnly, saveToFile,
                           client_to_server, commentsEnabled,
                           attachImageFilename, mediaType,
                           imageDescription, city,
                           testInReplyTo, testInReplyToAtomUri,
                           testSubject, testSchedulePost,
                           testEventDate, testEventTime, testLocation,
                           testIsArticle, system_language, conversationId,
                           low_bandwidth, content_license_url)
    # set the date on the post
    currDateStr = "2021-09-08T20:45:00Z"
    post_json_object['published'] = currDateStr
    post_json_object['object']['published'] = currDateStr

    # test a post within the reply interval
    postUrl = post_json_object['object']['id']
    replyIntervalHours = 2
    currDateStr = "2021-09-08T21:32:10Z"
    assert can_reply_to(base_dir, nickname, domain,
                        postUrl, replyIntervalHours,
                        currDateStr,
                        post_json_object)

    # test a post outside of the reply interval
    currDateStr = "2021-09-09T09:24:47Z"
    assert not can_reply_to(base_dir, nickname, domain,
                            postUrl, replyIntervalHours,
                            currDateStr,
                            post_json_object)


def _test_seconds_between_publish() -> None:
    print('testSecondsBetweenPublished')
    published1 = "2021-10-14T09:39:27Z"
    published2 = "2021-10-14T09:41:28Z"

    secondsElapsed = seconds_between_published(published1, published2)
    assert secondsElapsed == 121
    # invalid date
    published2 = "2021-10-14N09:41:28Z"
    secondsElapsed = seconds_between_published(published1, published2)
    assert secondsElapsed == -1


def _test_word_similarity() -> None:
    print('testWordsSimilarity')
    minWords = 10
    content1 = "This is the same"
    content2 = "This is the same"
    assert words_similarity(content1, content2, minWords) == 100
    content1 = "This is our world now... " + \
        "the world of the electron and the switch, the beauty of the baud"
    content2 = "This is our world now. " + \
        "The world of the electron and the webkit, the beauty of the baud"
    similarity = words_similarity(content1, content2, minWords)
    assert similarity > 70
    content1 = "<p>We&apos;re growing! </p><p>A new denizen " + \
        "is frequenting HackBucket. You probably know him already " + \
        "from her epic typos - but let&apos;s not spoil too much " + \
        "\ud83d\udd2e</p>"
    content2 = "<p>We&apos;re growing! </p><p>A new denizen " + \
        "is frequenting HackBucket. You probably know them already " + \
        "from their epic typos - but let&apos;s not spoil too much " + \
        "\ud83d\udd2e</p>"
    similarity = words_similarity(content1, content2, minWords)
    assert similarity > 80


def _test_add_cw_lists(base_dir: str) -> None:
    print('testAddCWfromLists')
    translate = {}
    cw_lists = load_cw_lists(base_dir, True)
    assert cw_lists

    post_json_object = {
        "object": {
            "sensitive": False,
            "summary": None,
            "content": ""
        }
    }
    add_cw_from_lists(post_json_object, cw_lists, translate, 'Murdoch press')
    assert post_json_object['object']['sensitive'] is False
    assert post_json_object['object']['summary'] is None

    post_json_object = {
        "object": {
            "sensitive": False,
            "summary": None,
            "content": "Blah blah news.co.uk blah blah"
        }
    }
    add_cw_from_lists(post_json_object, cw_lists, translate, 'Murdoch press')
    assert post_json_object['object']['sensitive'] is True
    assert post_json_object['object']['summary'] == "Murdoch Press"

    post_json_object = {
        "object": {
            "sensitive": True,
            "summary": "Existing CW",
            "content": "Blah blah news.co.uk blah blah"
        }
    }
    add_cw_from_lists(post_json_object, cw_lists, translate, 'Murdoch press')
    assert post_json_object['object']['sensitive'] is True
    assert post_json_object['object']['summary'] == \
        "Murdoch Press / Existing CW"


def _test_valid_emoji_content() -> None:
    print('testValidEmojiContent')
    assert not valid_emoji_content(None)
    assert not valid_emoji_content(' ')
    assert not valid_emoji_content('j')
    assert not valid_emoji_content('😀😀😀')
    assert valid_emoji_content('😀')
    assert valid_emoji_content('😄')


def _test_httpsig_base_new(withDigest: bool, base_dir: str,
                           algorithm: str, digestAlgorithm: str) -> None:
    print('testHttpsigNew(' + str(withDigest) + ')')

    debug = True
    path = base_dir + '/.testHttpsigBaseNew'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)

    content_type = 'application/activity+json'
    nickname = 'socrates'
    hostDomain = 'someother.instance'
    domain = 'argumentative.social'
    http_prefix = 'https'
    port = 5576
    password = 'SuperSecretPassword'
    privateKeyPem, publicKeyPem, person, wfEndpoint = \
        create_person(path, nickname, domain, port, http_prefix,
                      False, False, password)
    assert privateKeyPem
    if withDigest:
        messageBodyJson = {
            "a key": "a value",
            "another key": "A string",
            "yet another key": "Another string"
        }
        messageBodyJsonStr = json.dumps(messageBodyJson)
    else:
        messageBodyJsonStr = ''

    headersDomain = get_full_domain(hostDomain, port)

    dateStr = strftime("%a, %d %b %Y %H:%M:%S %Z", gmtime())
    boxpath = '/inbox'
    if not withDigest:
        headers = {
            'host': headersDomain,
            'date': dateStr,
            'accept': content_type
        }
        signatureIndexHeader, signatureHeader = \
            sign_post_headers_new(dateStr, privateKeyPem, nickname,
                                  domain, port,
                                  hostDomain, port,
                                  boxpath, http_prefix, messageBodyJsonStr,
                                  algorithm, digestAlgorithm, debug)
    else:
        digestPrefix = get_digest_prefix(digestAlgorithm)
        bodyDigest = \
            message_content_digest(messageBodyJsonStr, digestAlgorithm)
        contentLength = len(messageBodyJsonStr)
        headers = {
            'host': headersDomain,
            'date': dateStr,
            'digest': f'{digestPrefix}={bodyDigest}',
            'content-type': content_type,
            'content-length': str(contentLength)
        }
        assert get_digest_algorithm_from_headers(headers) == digestAlgorithm
        signatureIndexHeader, signatureHeader = \
            sign_post_headers_new(dateStr, privateKeyPem, nickname,
                                  domain, port,
                                  hostDomain, port,
                                  boxpath, http_prefix, messageBodyJsonStr,
                                  algorithm, digestAlgorithm, debug)

    headers['signature'] = signatureHeader
    headers['signature-input'] = signatureIndexHeader
    print('headers: ' + str(headers))

    GETmethod = not withDigest
    debug = True
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, GETmethod, None,
                               messageBodyJsonStr, debug)
    debug = False
    if withDigest:
        # everything correct except for content-length
        headers['content-length'] = str(contentLength + 2)
        assert verify_post_headers(http_prefix, publicKeyPem, headers,
                                   boxpath, GETmethod, None,
                                   messageBodyJsonStr, debug) is False
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               '/parambulator' + boxpath, GETmethod, None,
                               messageBodyJsonStr, debug) is False
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, not GETmethod, None,
                               messageBodyJsonStr, debug) is False
    if not withDigest:
        # fake domain
        headers = {
            'host': 'bogon.domain',
            'date': dateStr,
            'content-type': content_type
        }
    else:
        # correct domain but fake message
        messageBodyJsonStr = \
            '{"a key": "a value", "another key": "Fake GNUs", ' + \
            '"yet another key": "More Fake GNUs"}'
        contentLength = len(messageBodyJsonStr)
        digestPrefix = get_digest_prefix(digestAlgorithm)
        bodyDigest = \
            message_content_digest(messageBodyJsonStr, digestAlgorithm)
        headers = {
            'host': domain,
            'date': dateStr,
            'digest': f'{digestPrefix}={bodyDigest}',
            'content-type': content_type,
            'content-length': str(contentLength)
        }
        assert get_digest_algorithm_from_headers(headers) == digestAlgorithm
    headers['signature'] = signatureHeader
    headers['signature-input'] = signatureIndexHeader
    pprint(headers)
    assert verify_post_headers(http_prefix, publicKeyPem, headers,
                               boxpath, not GETmethod, None,
                               messageBodyJsonStr, False) is False

    os.chdir(base_dir)
    shutil.rmtree(path, ignore_errors=False, onerror=None)


def _test_get_actor_from_in_reply_to() -> None:
    print('testGetActorFromInReplyTo')
    inReplyTo = \
        'https://fosstodon.org/users/bashrc/statuses/107400700612621140'
    replyActor = get_actor_from_in_reply_to(inReplyTo)
    assert replyActor == 'https://fosstodon.org/users/bashrc'

    inReplyTo = 'https://fosstodon.org/activity/107400700612621140'
    replyActor = get_actor_from_in_reply_to(inReplyTo)
    assert replyActor is None


def run_all_tests():
    base_dir = os.getcwd()
    print('Running tests...')
    update_default_themes_list(os.getcwd())
    _test_source_contains_no_tabs()
    _translate_ontology(base_dir)
    _test_get_price_from_string()
    _test_post_variable_names()
    _test_config_param_names()
    _test_post_field_names()
    _test_checkbox_names()
    _test_functions()
    _test_get_actor_from_in_reply_to()
    _test_valid_emoji_content()
    _test_add_cw_lists(base_dir)
    _test_word_similarity()
    _test_seconds_between_publish()
    _test_sign_and_verify()
    _test_danger_svg(base_dir)
    _test_can_replyto(base_dir)
    _test_date_conversions()
    _test_authorized_shared_items()
    _test_valid_password()
    _test_get_links_from_content()
    _test_set_actor_language()
    _test_limit_repeted_words()
    _test_word_lengths_limit()
    _test_switch_word(base_dir)
    _test_useragent_domain()
    _test_roles()
    _test_skills()
    _test_spoofed_geolocation()
    _test_remove_interactions()
    _test_extract_pgp_public_key()
    _test_emoji_images()
    _test_camel_case_split()
    _test_speaker_replace_link()
    _test_extract_text_fields_from_post()
    _test_markdown_to_html()
    _test_valid_hash_tag()
    _test_prepare_html_post_nick()
    _test_domain_handling()
    _test_mastoapi()
    _test_links_within_post(base_dir)
    _test_reply_to_public_post(base_dir)
    _test_mentioned_people(base_dir)
    _test_guess_tag_category()
    _test_valid_nick()
    _test_parse_feed_date()
    _test_first_paragraph_from_string()
    _test_newswire_tags()
    _test_hashtag_rules()
    _test_strip_html_tag()
    _test_replace_email_quote()
    _test_constant_time_string()
    _test_translations(base_dir)
    _test_valid_content_warning()
    _test_remove_id_ending()
    _test_json_post_allows_comment()
    _run_html_replace_quote_marks()
    _test_danger_css(base_dir)
    _test_danger_markup()
    _test_strip_html()
    _test_site_active()
    _test_jsonld()
    _test_remove_txt_formatting()
    _test_web_links()
    _test_recent_posts_cache()
    _test_theme()
    _test_save_load_json()
    _test_json_string()
    _test_get_status_number()
    _test_addemoji(base_dir)
    _test_actor_parsing()
    _test_httpsig(base_dir)
    _test_http_signed_get(base_dir)
    _test_http_sig_new('rsa-sha256', 'rsa-sha256')
    _test_httpsig_base_new(True, base_dir, 'rsa-sha256', 'rsa-sha256')
    _test_httpsig_base_new(False, base_dir, 'rsa-sha256', 'rsa-sha256')
    _test_cache()
    _test_threads()
    _test_create_person_account(base_dir)
    _test_authentication(base_dir)
    _test_followers_of_person(base_dir)
    _test_followers_on_domain(base_dir)
    _test_follows(base_dir)
    _test_group_followers(base_dir)
    print('Tests succeeded\n')
