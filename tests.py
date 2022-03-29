__filename__ = "tests.py"
__author__ = "Bob Mottram"
__license__ = "AGPL3+"
__version__ = "1.3.0"
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
from follow import send_follow_request_via_server
from follow import send_unfollow_request_via_server
from siteactive import site_is_active
from utils import convert_published_to_local_timezone
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
from utils import valid_hash_tag
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
from content import bold_reading_string
from content import safe_web_text
from content import words_similarity
from content import get_price_from_string
from content import limit_repeated_words
from content import switch_words
from content import extract_text_fields_in_post
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
from theme import set_css_param
from theme import scan_themes_for_scripts
from linked_data_sig import generate_json_signature
from linked_data_sig import verify_json_signature
from newsdaemon import hashtag_rule_tree
from newsdaemon import hashtag_rule_resolve
from newswire import get_link_from_rss_item
from newswire import xml_podcast_to_dict
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
from happening import dav_month_via_server
from happening import dav_day_via_server


TEST_SERVER_GROUP_RUNNING = False
TEST_SERVER_ALICE_RUNNING = False
TEST_SERVER_BOB_RUNNING = False
TEST_SERVER_EVE_RUNNING = False

THR_GROUP = None
THR_ALICE = None
THR_BOB = None
THR_EVE = None


def _test_http_signed_get(base_dir: str):
    print('test_http_signed_get')
    http_prefix = 'https'
    debug = True

    boxpath = "/users/Actor"
    host = "epicyon.libreserver.org"
    content_length = "0"
    user_agent = "http.rb/4.4.1 (Mastodon/3.4.1; +https://octodon.social/)"
    date_str = 'Wed, 01 Sep 2021 16:11:10 GMT'
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
    public_key_pem = \
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
        "date": date_str,
        "accept": accept,
        "accept-encoding": accept_encoding,
        "signature": signature
    }
    getreq_method = True
    message_body_digest = None
    message_body_json_str = ''
    no_recency_check = True
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, getreq_method, message_body_digest,
                               message_body_json_str, debug, no_recency_check)
    # Change a single character and the signature should fail
    headers['date'] = headers['date'].replace(':10', ':11')
    assert not verify_post_headers(http_prefix, public_key_pem, headers,
                                   boxpath, getreq_method, message_body_digest,
                                   message_body_json_str, debug,
                                   no_recency_check)

    path = base_dir + '/.testHttpsigGET'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)

    nickname = 'testactor'
    host_domain = 'someother.instance'
    domain = 'argumentative.social'
    http_prefix = 'https'
    port = 443
    with_digest = False
    password = 'SuperSecretPassword'
    no_recency_check = True
    private_key_pem, public_key_pem, _, _ = \
        create_person(path, nickname, domain, port, http_prefix,
                      False, False, password)
    assert private_key_pem
    assert public_key_pem
    message_body_json_str = ''

    headers_domain = get_full_domain(host_domain, port)

    date_str = 'Tue, 14 Sep 2021 16:19:00 GMT'
    boxpath = '/inbox'
    accept = 'application/json'
#    accept = 'application/activity+json'
    headers = {
        'user-agent': 'Epicyon/1.3.0; +https://' + domain + '/',
        'host': headers_domain,
        'date': date_str,
        'accept': accept,
        'content-length': 0
    }
    signature_header = \
        create_signed_header(date_str,
                             private_key_pem, nickname,
                             domain, port,
                             host_domain, port,
                             boxpath, http_prefix, False,
                             None, accept)

    headers['signature'] = signature_header['signature']
    getreq_method = not with_digest
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, getreq_method, None,
                               message_body_json_str, debug, no_recency_check)
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)


def _test_sign_and_verify() -> None:
    print('test_sign_and_verify')
    public_key_pem = \
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

    private_key_pem = \
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
    signed_header_text = \
        '(request-target): get /actor\n' + \
        'host: octodon.social\n' + \
        'date: Tue, 14 Sep 2021 16:19:00 GMT\n' + \
        'accept: application/json'
    header_digest = get_sha_256(signed_header_text.encode('ascii'))
    key = load_pem_private_key(private_key_pem.encode('utf-8'),
                               None, backend=default_backend())
    raw_signature = key.sign(header_digest,
                             padding.PKCS1v15(),
                             hazutils.Prehashed(hashes.SHA256()))
    signature1 = base64.b64encode(raw_signature).decode('ascii')

    # verify
    padding_str = padding.PKCS1v15()
    alg = hazutils.Prehashed(hashes.SHA256())
    pubkey = load_pem_public_key(public_key_pem.encode('utf-8'),
                                 backend=default_backend())
    signature2 = base64.b64decode(signature1)
    pubkey.verify(signature2, header_digest, padding_str, alg)


def _test_http_sig_new(algorithm: str, digest_algorithm: str):
    print('test_http_sig_new')
    http_prefix = 'https'
    port = 443
    debug = True
    message_body_json = {"hello": "world"}
    message_body_json_str = json.dumps(message_body_json)
    nickname = 'foo'
    path_str = "/" + nickname + "?param=value&pet=dog HTTP/1.1"
    domain = 'example.com'
    date_str = 'Tue, 20 Apr 2021 02:07:55 GMT'
    digest_prefix = get_digest_prefix(digest_algorithm)
    digest_str = \
        digest_prefix + '=X48E9qOokqqrvdts8nOJRJN3OWDUoyWxBf7kbu9DBPE='
    body_digest = \
        message_content_digest(message_body_json_str, digest_algorithm)
    assert body_digest in digest_str
    content_length = 18
    content_type = 'application/activity+json'
    public_key_pem = \
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

    private_key_pem = \
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
        "date": date_str,
        "digest": f'{digest_prefix}={body_digest}',
        "content-type": content_type,
        "content-length": str(content_length)
    }
    signature_index_header, signature_header = \
        sign_post_headers_new(date_str, private_key_pem, nickname,
                              domain, port,
                              domain, port,
                              path_str, http_prefix, message_body_json_str,
                              algorithm, digest_algorithm, debug)
    print('signature_index_header1: ' + str(signature_index_header))
    print('signature_header1: ' + str(signature_header))
    sig_input = "keyId=\"https://example.com/users/foo#main-key\"; " + \
        "alg=hs2019; created=1618884475; " + \
        "sig1=(@request-target, @created, host, date, digest, " + \
        "content-type, content-length)"
    assert signature_index_header == sig_input
    sig = "sig1=:NXAQ7AtDMR2iwhmH1qCwiZw5PVTjOw5+5kSu0Tsx/3gqz0D" + \
        "py7OQbWqFHrNB7MmS4TukX/vDyQOFdElY5yxnEhbgRwKACq0AP4QH9H" + \
        "CiRyCE8UXDdAkY4VUd6jrWjRHKRoqQN7I+Q5tb2Fu5cDfifw/PQc86Z" + \
        "NmMhPrg3OjUJ9Q2Gj29NhgJ+4el1ECg0cAy4yG1M9AQ3KvQooQFvlg1" + \
        "vp0H2xfbJQjv8FsR/lKiRdaVHqGR2CKrvxvPRPaOsFANp2wzEtiMk3O" + \
        "TrBTYU+Zb53mIspfEeLxsNtcGmBDmQKZ9Pud8f99XGJrP+uDd3zKtnr" + \
        "f3fUnRRqy37yhB7WVwkg==:"
    assert signature_header == sig

    debug = True
    headers['path'] = path_str
    headers['signature'] = sig
    headers['signature-input'] = sig_input
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               path_str, False, None,
                               message_body_json_str, debug, True)

    # make a deliberate mistake
    debug = False
    headers['signature'] = headers['signature'].replace('V', 'B')
    assert not verify_post_headers(http_prefix, public_key_pem, headers,
                                   path_str, False, None,
                                   message_body_json_str, debug, True)


def _test_httpsig_base(with_digest: bool, base_dir: str):
    print('test_httpsig(' + str(with_digest) + ')')

    path = base_dir + '/.testHttpsigBase'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)

    algorithm = 'rsa-sha256'
    digest_algorithm = 'rsa-sha256'
    content_type = 'application/activity+json'
    nickname = 'socrates'
    host_domain = 'someother.instance'
    domain = 'argumentative.social'
    http_prefix = 'https'
    port = 5576
    password = 'SuperSecretPassword'
    private_key_pem, public_key_pem, person, wf_endpoint = \
        create_person(path, nickname, domain, port, http_prefix,
                      False, False, password)
    assert private_key_pem
    assert public_key_pem
    assert person
    assert wf_endpoint
    if with_digest:
        message_body_json = {
            "a key": "a value",
            "another key": "A string",
            "yet another key": "Another string"
        }
        message_body_json_str = json.dumps(message_body_json)
    else:
        message_body_json_str = ''

    headers_domain = get_full_domain(host_domain, port)

    date_str = strftime("%a, %d %b %Y %H:%M:%S %Z", gmtime())
    boxpath = '/inbox'
    if not with_digest:
        headers = {
            'host': headers_domain,
            'date': date_str,
            'accept': content_type
        }
        signature_header = \
            sign_post_headers(date_str, private_key_pem, nickname,
                              domain, port,
                              host_domain, port,
                              boxpath, http_prefix, None, content_type,
                              algorithm, None)
    else:
        digest_prefix = get_digest_prefix(digest_algorithm)
        body_digest = \
            message_content_digest(message_body_json_str, digest_algorithm)
        content_length = len(message_body_json_str)
        headers = {
            'host': headers_domain,
            'date': date_str,
            'digest': f'{digest_prefix}={body_digest}',
            'content-type': content_type,
            'content-length': str(content_length)
        }
        assert get_digest_algorithm_from_headers(headers) == digest_algorithm
        signature_header = \
            sign_post_headers(date_str, private_key_pem, nickname,
                              domain, port,
                              host_domain, port,
                              boxpath, http_prefix, message_body_json_str,
                              content_type, algorithm, digest_algorithm)

    headers['signature'] = signature_header
    getreq_method = not with_digest
    debug = True
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, getreq_method, None,
                               message_body_json_str, debug)
    if with_digest:
        # everything correct except for content-length
        headers['content-length'] = str(content_length + 2)
        assert verify_post_headers(http_prefix, public_key_pem, headers,
                                   boxpath, getreq_method, None,
                                   message_body_json_str, False) is False
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               '/parambulator' + boxpath, getreq_method, None,
                               message_body_json_str, False) is False
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, not getreq_method, None,
                               message_body_json_str, False) is False
    if not with_digest:
        # fake domain
        headers = {
            'host': 'bogon.domain',
            'date': date_str,
            'content-type': content_type
        }
    else:
        # correct domain but fake message
        message_body_json_str = \
            '{"a key": "a value", "another key": "Fake GNUs", ' + \
            '"yet another key": "More Fake GNUs"}'
        content_length = len(message_body_json_str)
        digest_prefix = get_digest_prefix(digest_algorithm)
        body_digest = \
            message_content_digest(message_body_json_str, digest_algorithm)
        headers = {
            'host': domain,
            'date': date_str,
            'digest': f'{digest_prefix}={body_digest}',
            'content-type': content_type,
            'content-length': str(content_length)
        }
        assert get_digest_algorithm_from_headers(headers) == digest_algorithm
    headers['signature'] = signature_header
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, not getreq_method, None,
                               message_body_json_str, False) is False

    os.chdir(base_dir)
    shutil.rmtree(path, ignore_errors=False, onerror=None)


def _test_httpsig(base_dir: str):
    _test_httpsig_base(True, base_dir)
    _test_httpsig_base(False, base_dir)


def _test_cache():
    print('test_cache')
    person_url = "cat@cardboard.box"
    person_json = {
        "id": 123456,
        "test": "This is a test"
    }
    person_cache = {}
    store_person_in_cache(None, person_url, person_json, person_cache, True)
    result = get_person_from_cache(None, person_url, person_cache, True)
    assert result['id'] == 123456
    assert result['test'] == 'This is a test'


def _test_threads_function(param: str):
    for _ in range(10000):
        time.sleep(2)


def _test_threads():
    print('test_threads')
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
                        bob_address: str, federation_list: [],
                        hasFollows: bool, hasPosts: bool,
                        send_threads: []):
    print('Creating test server: Alice on port ' + str(port))
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)
    shared_items_federated_domains = []
    system_language = 'en'
    languages_understood = [system_language]
    nickname = 'alice'
    http_prefix = 'http'
    proxy_type = None
    password = 'alicepass'
    max_replies = 64
    domain_max_posts_per_day = 1000
    account_max_posts_per_day = 1000
    allow_deletion = True
    low_bandwidth = True
    private_key_pem, public_key_pem, person, wf_endpoint = \
        create_person(path, nickname, domain, port, http_prefix, True,
                      False, password)
    assert private_key_pem
    assert public_key_pem
    assert person
    assert wf_endpoint
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    assert set_skill_level(path, nickname, domain, 'hacking', 90)
    assert set_role(path, nickname, domain, 'guru')
    if hasFollows:
        follow_person(path, nickname, domain, 'bob', bob_address,
                      federation_list, False, False)
        add_follower_of_person(path, nickname, domain, 'bob', bob_address,
                               federation_list, False, False)
    if hasPosts:
        test_followers_only = False
        test_save_to_file = True
        client_to_server = False
        test_comments_enabled = True
        test_attach_image_filename = None
        test_media_type = None
        test_image_description = None
        test_city = 'London, England'
        test_in_reply_to = None
        test_in_reply_to_atom_uri = None
        test_subject = None
        test_schedule_post = False
        test_event_date = None
        test_event_time = None
        test_location = None
        test_is_article = False
        conversation_id = None
        content_license_url = 'https://creativecommons.org/licenses/by/4.0'
        create_public_post(path, nickname, domain, port, http_prefix,
                           "No wise fish would go anywhere without a porpoise",
                           test_followers_only,
                           test_save_to_file,
                           client_to_server,
                           test_comments_enabled,
                           test_attach_image_filename,
                           test_media_type,
                           test_image_description, test_city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "Curiouser and curiouser!",
                           test_followers_only,
                           test_save_to_file,
                           client_to_server,
                           test_comments_enabled,
                           test_attach_image_filename,
                           test_media_type,
                           test_image_description, test_city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "In the gardens of memory, in the palace " +
                           "of dreams, that is where you and I shall meet",
                           test_followers_only,
                           test_save_to_file,
                           client_to_server,
                           test_comments_enabled,
                           test_attach_image_filename,
                           test_media_type,
                           test_image_description, test_city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
        regenerate_index_for_box(path, nickname, domain, 'outbox')
    global TEST_SERVER_ALICE_RUNNING
    TEST_SERVER_ALICE_RUNNING = True
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
    dyslexic_font = False
    crawlers_allowed = []
    print('Server running: Alice')
    run_daemon(crawlers_allowed,
               dyslexic_font,
               content_license_url,
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
                      alice_address: str, federation_list: [],
                      hasFollows: bool, hasPosts: bool,
                      send_threads: []):
    print('Creating test server: Bob on port ' + str(port))
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)
    shared_items_federated_domains = []
    system_language = 'en'
    languages_understood = [system_language]
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
    private_key_pem, public_key_pem, person, wf_endpoint = \
        create_person(path, nickname, domain, port, http_prefix, True,
                      False, password)
    assert private_key_pem
    assert public_key_pem
    assert person
    assert wf_endpoint
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    if hasFollows and alice_address:
        follow_person(path, nickname, domain,
                      'alice', alice_address, federation_list, False, False)
        add_follower_of_person(path, nickname, domain,
                               'alice', alice_address, federation_list,
                               False, False)
    if hasPosts:
        test_followers_only = False
        test_save_to_file = True
        test_comments_enabled = True
        test_attach_image_filename = None
        test_image_description = None
        test_media_type = None
        test_city = 'London, England'
        test_in_reply_to = None
        test_in_reply_to_atom_uri = None
        test_subject = None
        test_schedule_post = False
        test_event_date = None
        test_event_time = None
        test_location = None
        test_is_article = False
        conversation_id = None
        content_license_url = 'https://creativecommons.org/licenses/by/4.0'
        create_public_post(path, nickname, domain, port, http_prefix,
                           "It's your life, live it your way.",
                           test_followers_only,
                           test_save_to_file,
                           client_to_server,
                           test_comments_enabled,
                           test_attach_image_filename,
                           test_media_type,
                           test_image_description, test_city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "One of the things I've realised is that " +
                           "I am very simple",
                           test_followers_only,
                           test_save_to_file,
                           client_to_server,
                           test_comments_enabled,
                           test_attach_image_filename,
                           test_media_type,
                           test_image_description, test_city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
        create_public_post(path, nickname, domain, port, http_prefix,
                           "Quantum physics is a bit of a passion of mine",
                           test_followers_only,
                           test_save_to_file,
                           client_to_server,
                           test_comments_enabled,
                           test_attach_image_filename,
                           test_media_type,
                           test_image_description, test_city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
        regenerate_index_for_box(path, nickname, domain, 'outbox')
    global TEST_SERVER_BOB_RUNNING
    TEST_SERVER_BOB_RUNNING = True
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
    dyslexic_font = False
    crawlers_allowed = []
    print('Server running: Bob')
    run_daemon(crawlers_allowed,
               dyslexic_font,
               content_license_url,
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
    private_key_pem, public_key_pem, person, wf_endpoint = \
        create_person(path, nickname, domain, port, http_prefix, True,
                      False, password)
    assert private_key_pem
    assert public_key_pem
    assert person
    assert wf_endpoint
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    global TEST_SERVER_EVE_RUNNING
    TEST_SERVER_EVE_RUNNING = True
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
    dyslexic_font = False
    crawlers_allowed = []
    print('Server running: Eve')
    run_daemon(crawlers_allowed,
               dyslexic_font,
               content_license_url,
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
    private_key_pem, public_key_pem, person, wf_endpoint = \
        create_group(path, nickname, domain, port, http_prefix, True,
                     password)
    assert private_key_pem
    assert public_key_pem
    assert person
    assert wf_endpoint
    delete_all_posts(path, nickname, domain, 'inbox')
    delete_all_posts(path, nickname, domain, 'outbox')
    global TEST_SERVER_GROUP_RUNNING
    TEST_SERVER_GROUP_RUNNING = True
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
    dyslexic_font = False
    crawlers_allowed = []
    print('Server running: Group')
    run_daemon(crawlers_allowed,
               dyslexic_font,
               content_license_url,
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

    global TEST_SERVER_ALICE_RUNNING
    global TEST_SERVER_BOB_RUNNING
    TEST_SERVER_ALICE_RUNNING = False
    TEST_SERVER_BOB_RUNNING = False

    system_language = 'en'
    languages_understood = [system_language]
    http_prefix = 'http'
    proxy_type = None
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    alice_dir = base_dir + '/.tests/alice'
    alice_domain = '127.0.0.50'
    alice_port = 61935
    alice_address = alice_domain + ':' + str(alice_port)

    bob_dir = base_dir + '/.tests/bob'
    bob_domain = '127.0.0.100'
    bob_port = 61936
    federation_list = [bob_domain, alice_domain]
    alice_send_threads = []
    bob_send_threads = []
    bob_address = bob_domain + ':' + str(bob_port)

    global THR_ALICE
    if THR_ALICE:
        while THR_ALICE.is_alive():
            THR_ALICE.stop()
            time.sleep(1)
        THR_ALICE.kill()

    THR_ALICE = \
        thread_with_trace(target=create_server_alice,
                          args=(alice_dir, alice_domain, alice_port,
                                bob_address, federation_list, False, False,
                                alice_send_threads),
                          daemon=True)

    global THR_BOB
    if THR_BOB:
        while THR_BOB.is_alive():
            THR_BOB.stop()
            time.sleep(1)
        THR_BOB.kill()

    THR_BOB = \
        thread_with_trace(target=create_server_bob,
                          args=(bob_dir, bob_domain, bob_port, alice_address,
                                federation_list, False, False,
                                bob_send_threads),
                          daemon=True)

    THR_ALICE.start()
    THR_BOB.start()
    assert THR_ALICE.is_alive() is True
    assert THR_BOB.is_alive() is True

    # wait for both servers to be running
    while not (TEST_SERVER_ALICE_RUNNING and TEST_SERVER_BOB_RUNNING):
        time.sleep(1)

    time.sleep(1)

    print('\n\n*******************************************************')
    print('Alice sends to Bob')
    os.chdir(alice_dir)
    session_alice = create_session(proxy_type)
    in_reply_to = None
    in_reply_to_atom_uri = None
    subject = None
    alice_post_log = []
    followers_only = False
    save_to_file = True
    client_to_server = False
    cc_url = None
    alice_person_cache = {}
    alice_cached_webfingers = {}
    alice_shared_items_federated_domains = []
    alice_shared_item_federation_tokens = {}
    attached_image_filename = base_dir + '/img/logo.png'
    test_image_width, test_image_height = \
        get_image_dimensions(attached_image_filename)
    assert test_image_width
    assert test_image_height
    media_type = get_attachment_media_type(attached_image_filename)
    attached_image_description = 'Logo'
    is_article = False
    city = 'London, England'
    # nothing in Alice's outbox
    outbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/outbox'
    assert len([name for name in os.listdir(outbox_path)
                if os.path.isfile(os.path.join(outbox_path, name))]) == 0
    low_bandwidth = False
    signing_priv_key_pem = None
    send_result = \
        send_post(signing_priv_key_pem, __version__,
                  session_alice, alice_dir, 'alice', alice_domain, alice_port,
                  'bob', bob_domain, bob_port, cc_url, http_prefix,
                  'Why is a mouse when it spins? ' +
                  'यह एक परीक्षण है #sillyquestion',
                  followers_only,
                  save_to_file, client_to_server, True,
                  attached_image_filename, media_type,
                  attached_image_description, city, federation_list,
                  alice_send_threads, alice_post_log, alice_cached_webfingers,
                  alice_person_cache, is_article, system_language,
                  languages_understood,
                  alice_shared_items_federated_domains,
                  alice_shared_item_federation_tokens, low_bandwidth,
                  content_license_url,
                  in_reply_to, in_reply_to_atom_uri, subject)
    print('send_result: ' + str(send_result))

    queue_path = bob_dir + '/accounts/bob@' + bob_domain + '/queue'
    inbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/inbox'
    m_path = get_media_path()
    media_path = alice_dir + '/' + m_path
    for _ in range(30):
        if os.path.isdir(inbox_path):
            if len([name for name in os.listdir(inbox_path)
                    if os.path.isfile(os.path.join(inbox_path, name))]) > 0:
                if len([name for name in os.listdir(outbox_path)
                        if os.path.isfile(os.path.join(outbox_path,
                                                       name))]) == 1:
                    if len([name for name in os.listdir(media_path)
                            if os.path.isfile(os.path.join(media_path,
                                                           name))]) > 0:
                        if len([name for name in os.listdir(queue_path)
                                if os.path.isfile(os.path.join(queue_path,
                                                               name))]) == 0:
                            break
        time.sleep(1)

    # check that a news account exists
    news_actor_dir = alice_dir + '/accounts/news@' + alice_domain
    print("news_actor_dir: " + news_actor_dir)
    assert os.path.isdir(news_actor_dir)
    news_actor_file = news_actor_dir + '.json'
    assert os.path.isfile(news_actor_file)
    news_actor_json = load_json(news_actor_file)
    assert news_actor_json
    assert news_actor_json.get("id")
    # check the id of the news actor
    print('News actor Id: ' + news_actor_json["id"])
    assert (news_actor_json["id"] ==
            http_prefix + '://' + alice_address + '/users/news')

    # Image attachment created
    assert len([name for name in os.listdir(media_path)
                if os.path.isfile(os.path.join(media_path, name))]) > 0
    # inbox item created
    assert len([name for name in os.listdir(inbox_path)
                if os.path.isfile(os.path.join(inbox_path, name))]) == 1
    # queue item removed
    testval = len([name for name in os.listdir(queue_path)
                   if os.path.isfile(os.path.join(queue_path, name))])
    print('queue_path: ' + queue_path + ' '+str(testval))
    assert testval == 0
    assert valid_inbox(bob_dir, 'bob', bob_domain)
    assert valid_inbox_filenames(bob_dir, 'bob', bob_domain,
                                 alice_domain, alice_port)
    print('Check that message received from Alice contains the expected text')
    for name in os.listdir(inbox_path):
        filename = os.path.join(inbox_path, name)
        assert os.path.isfile(filename)
        received_json = load_json(filename, 0)
        if received_json:
            pprint(received_json['object']['content'])
        assert received_json
        assert 'Why is a mouse when it spins?' in \
            received_json['object']['content']
        assert 'Why is a mouse when it spins?' in \
            received_json['object']['contentMap'][system_language]
        assert 'यह एक परीक्षण है' in received_json['object']['content']
        print('Check that message received from Alice contains an attachment')
        assert received_json['object']['attachment']
        assert len(received_json['object']['attachment']) == 1
        attached = received_json['object']['attachment'][0]
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

    alice_domain_str = alice_domain + ':' + str(alice_port)
    add_follower_of_person(bob_dir, 'bob', bob_domain, 'alice',
                           alice_domain_str, federation_list, False, False)
    bob_domain_str = bob_domain + ':' + str(bob_port)
    follow_person(alice_dir, 'alice', alice_domain, 'bob',
                  bob_domain_str, federation_list, False, False)

    session_bob = create_session(proxy_type)
    bob_post_log = []
    bob_person_cache = {}
    bob_cached_webfingers = {}
    status_number = None
    outbox_post_filename = None
    outbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/outbox'
    for name in os.listdir(outbox_path):
        if '#statuses#' in name:
            status_number = \
                int(name.split('#statuses#')[1].replace('.json', ''))
            outbox_post_filename = outbox_path + '/' + name
    assert status_number > 0
    assert outbox_post_filename
    assert like_post({}, session_bob, bob_dir, federation_list,
                     'bob', bob_domain, bob_port, http_prefix,
                     'alice', alice_domain, alice_port, [],
                     status_number, False, bob_send_threads, bob_post_log,
                     bob_person_cache, bob_cached_webfingers,
                     True, __version__, signing_priv_key_pem,
                     bob_domain, None, None)

    for _ in range(20):
        if 'likes' in open(outbox_post_filename).read():
            break
        time.sleep(1)

    alice_post_json = load_json(outbox_post_filename, 0)
    if alice_post_json:
        pprint(alice_post_json)

    assert 'likes' in open(outbox_post_filename).read()

    print('\n\n*******************************************************')
    print("Bob reacts to Alice's post")

    assert reaction_post({}, session_bob, bob_dir, federation_list,
                         'bob', bob_domain, bob_port, http_prefix,
                         'alice', alice_domain, alice_port, [],
                         status_number, '😀',
                         False, bob_send_threads, bob_post_log,
                         bob_person_cache, bob_cached_webfingers,
                         True, __version__, signing_priv_key_pem,
                         bob_domain, None, None)

    for i in range(20):
        if 'reactions' in open(outbox_post_filename).read():
            break
        time.sleep(1)

    alice_post_json = load_json(outbox_post_filename, 0)
    if alice_post_json:
        pprint(alice_post_json)

    # TODO: fix reactions unit test
#    assert 'reactions' in open(outbox_post_filename).read()

    print('\n\n*******************************************************')
    print("Bob repeats Alice's post")
    object_url = \
        http_prefix + '://' + alice_domain + ':' + str(alice_port) + \
        '/users/alice/statuses/' + str(status_number)
    inbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/inbox'
    outbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/outbox'
    outbox_before_announce_count = \
        len([name for name in os.listdir(outbox_path)
             if os.path.isfile(os.path.join(outbox_path, name))])
    before_announce_count = \
        len([name for name in os.listdir(inbox_path)
             if os.path.isfile(os.path.join(inbox_path, name))])
    print('inbox items before announce: ' + str(before_announce_count))
    print('outbox items before announce: ' + str(outbox_before_announce_count))
    assert outbox_before_announce_count == 0
    assert before_announce_count == 0
    announce_public(session_bob, bob_dir, federation_list,
                    'bob', bob_domain, bob_port, http_prefix,
                    object_url,
                    False, bob_send_threads, bob_post_log,
                    bob_person_cache, bob_cached_webfingers,
                    True, __version__, signing_priv_key_pem,
                    bob_domain, None, None)
    announce_message_arrived = False
    outbox_message_arrived = False
    for i in range(20):
        time.sleep(1)
        if not os.path.isdir(inbox_path):
            continue
        if len([name for name in os.listdir(outbox_path)
                if os.path.isfile(os.path.join(outbox_path, name))]) > 0:
            outbox_message_arrived = True
            print('Announce created by Bob')
        if len([name for name in os.listdir(inbox_path)
                if os.path.isfile(os.path.join(inbox_path, name))]) > 0:
            announce_message_arrived = True
            print('Announce message sent to Alice!')
        if announce_message_arrived and outbox_message_arrived:
            break
    after_announce_count = \
        len([name for name in os.listdir(inbox_path)
             if os.path.isfile(os.path.join(inbox_path, name))])
    outbox_after_announce_count = \
        len([name for name in os.listdir(outbox_path)
             if os.path.isfile(os.path.join(outbox_path, name))])
    print('inbox items after announce: ' + str(after_announce_count))
    print('outbox items after announce: ' + str(outbox_after_announce_count))
    assert after_announce_count == before_announce_count + 1
    assert outbox_after_announce_count == outbox_before_announce_count + 1
    # stop the servers
    THR_ALICE.kill()
    THR_ALICE.join()
    assert THR_ALICE.is_alive() is False

    THR_BOB.kill()
    THR_BOB.join()
    assert THR_BOB.is_alive() is False

    os.chdir(base_dir)
    shutil.rmtree(alice_dir, ignore_errors=False, onerror=None)
    shutil.rmtree(bob_dir, ignore_errors=False, onerror=None)


def test_follow_between_servers(base_dir: str) -> None:
    print('Testing sending a follow request from one server to another')

    global TEST_SERVER_ALICE_RUNNING
    global TEST_SERVER_BOB_RUNNING
    TEST_SERVER_ALICE_RUNNING = False
    TEST_SERVER_BOB_RUNNING = False

    system_language = 'en'
    languages_understood = [system_language]
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    alice_dir = base_dir + '/.tests/alice'
    alice_domain = '127.0.0.47'
    alice_port = 61935
    alice_send_threads = []
    alice_address = alice_domain + ':' + str(alice_port)

    bob_dir = base_dir + '/.tests/bob'
    bob_domain = '127.0.0.79'
    bob_port = 61936
    bob_send_threads = []
    bob_address = bob_domain + ':' + str(bob_port)

    global THR_ALICE
    if THR_ALICE:
        while THR_ALICE.is_alive():
            THR_ALICE.stop()
            time.sleep(1)
        THR_ALICE.kill()

    THR_ALICE = \
        thread_with_trace(target=create_server_alice,
                          args=(alice_dir, alice_domain, alice_port,
                                bob_address, federation_list, False, False,
                                alice_send_threads),
                          daemon=True)

    global THR_BOB
    if THR_BOB:
        while THR_BOB.is_alive():
            THR_BOB.stop()
            time.sleep(1)
        THR_BOB.kill()

    THR_BOB = \
        thread_with_trace(target=create_server_bob,
                          args=(bob_dir, bob_domain, bob_port, alice_address,
                                federation_list, False, False,
                                bob_send_threads),
                          daemon=True)

    THR_ALICE.start()
    THR_BOB.start()
    assert THR_ALICE.is_alive() is True
    assert THR_BOB.is_alive() is True

    # wait for all servers to be running
    ctr = 0
    while not (TEST_SERVER_ALICE_RUNNING and TEST_SERVER_BOB_RUNNING):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(TEST_SERVER_ALICE_RUNNING))
    print('Bob online: ' + str(TEST_SERVER_BOB_RUNNING))
    assert ctr <= 60
    time.sleep(1)

    # In the beginning all was calm and there were no follows

    print('*********************************************************')
    print('Alice sends a follow request to Bob')
    os.chdir(alice_dir)
    session_alice = create_session(proxy_type)
    in_reply_to = None
    in_reply_to_atom_uri = None
    subject = None
    alice_post_log = []
    followers_only = False
    save_to_file = True
    client_to_server = False
    cc_url = None
    alice_person_cache = {}
    alice_cached_webfingers = {}
    alice_post_log = []
    bob_actor = http_prefix + '://' + bob_address + '/users/bob'
    signing_priv_key_pem = None
    send_result = \
        send_follow_request(session_alice, alice_dir,
                            'alice', alice_domain,
                            alice_domain, alice_port, http_prefix,
                            'bob', bob_domain, bob_actor,
                            bob_port, http_prefix,
                            client_to_server, federation_list,
                            alice_send_threads, alice_post_log,
                            alice_cached_webfingers, alice_person_cache,
                            True, __version__, signing_priv_key_pem,
                            alice_domain, None, None)
    print('send_result: ' + str(send_result))

    for _ in range(16):
        if os.path.isfile(bob_dir + '/accounts/bob@' +
                          bob_domain + '/followers.txt'):
            if os.path.isfile(alice_dir + '/accounts/alice@' +
                              alice_domain + '/following.txt'):
                if os.path.isfile(alice_dir + '/accounts/alice@' +
                                  alice_domain + '/followingCalendar.txt'):
                    break
        time.sleep(1)

    assert valid_inbox(bob_dir, 'bob', bob_domain)
    assert valid_inbox_filenames(bob_dir, 'bob', bob_domain,
                                 alice_domain, alice_port)
    assert 'alice@' + alice_domain in open(bob_dir + '/accounts/bob@' +
                                           bob_domain +
                                           '/followers.txt').read()
    assert 'bob@' + bob_domain in open(alice_dir + '/accounts/alice@' +
                                       alice_domain + '/following.txt').read()
    assert 'bob@' + bob_domain in open(alice_dir + '/accounts/alice@' +
                                       alice_domain +
                                       '/followingCalendar.txt').read()
    assert not is_group_actor(alice_dir, bob_actor, alice_person_cache)
    assert not is_group_account(alice_dir, 'alice', alice_domain)

    print('\n\n*********************************************************')
    print('Alice sends a message to Bob')
    alice_post_log = []
    alice_person_cache = {}
    alice_cached_webfingers = {}
    alice_shared_items_federated_domains = []
    alice_shared_item_federation_tokens = {}
    alice_post_log = []
    is_article = False
    city = 'London, England'
    low_bandwidth = False
    signing_priv_key_pem = None
    send_result = \
        send_post(signing_priv_key_pem, __version__,
                  session_alice, alice_dir, 'alice', alice_domain, alice_port,
                  'bob', bob_domain, bob_port, cc_url,
                  http_prefix, 'Alice message', followers_only, save_to_file,
                  client_to_server, True,
                  None, None, None, city, federation_list,
                  alice_send_threads, alice_post_log, alice_cached_webfingers,
                  alice_person_cache, is_article, system_language,
                  languages_understood,
                  alice_shared_items_federated_domains,
                  alice_shared_item_federation_tokens, low_bandwidth,
                  content_license_url,
                  in_reply_to, in_reply_to_atom_uri, subject)
    print('send_result: ' + str(send_result))

    queue_path = bob_dir + '/accounts/bob@' + bob_domain + '/queue'
    inbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/inbox'
    alice_message_arrived = False
    for i in range(20):
        time.sleep(1)
        if os.path.isdir(inbox_path):
            if len([name for name in os.listdir(inbox_path)
                    if os.path.isfile(os.path.join(inbox_path, name))]) > 0:
                alice_message_arrived = True
                print('Alice message sent to Bob!')
                break

    assert alice_message_arrived is True
    print('Message from Alice to Bob succeeded')

    # stop the servers
    THR_ALICE.kill()
    THR_ALICE.join()
    assert THR_ALICE.is_alive() is False

    THR_BOB.kill()
    THR_BOB.join()
    assert THR_BOB.is_alive() is False

    # queue item removed
    time.sleep(4)
    assert len([name for name in os.listdir(queue_path)
                if os.path.isfile(os.path.join(queue_path, name))]) == 0

    os.chdir(base_dir)
    shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)


def test_shared_items_federation(base_dir: str) -> None:
    print('Testing federation of shared items between Alice and Bob')

    global TEST_SERVER_ALICE_RUNNING
    global TEST_SERVER_BOB_RUNNING
    TEST_SERVER_ALICE_RUNNING = False
    TEST_SERVER_BOB_RUNNING = False

    system_language = 'en'
    languages_understood = [system_language]
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    alice_dir = base_dir + '/.tests/alice'
    alice_domain = '127.0.0.74'
    alice_port = 61917
    alice_send_threads = []
    alice_address = alice_domain + ':' + str(alice_port)

    bob_dir = base_dir + '/.tests/bob'
    bob_domain = '127.0.0.81'
    bob_port = 61983
    bob_send_threads = []
    bob_address = bob_domain + ':' + str(bob_port)
    bob_password = 'bobpass'
    bob_cached_webfingers = {}
    bob_person_cache = {}

    global THR_ALICE
    if THR_ALICE:
        while THR_ALICE.is_alive():
            THR_ALICE.stop()
            time.sleep(1)
        THR_ALICE.kill()

    THR_ALICE = \
        thread_with_trace(target=create_server_alice,
                          args=(alice_dir, alice_domain, alice_port,
                                bob_address, federation_list, False, False,
                                alice_send_threads),
                          daemon=True)

    global THR_BOB
    if THR_BOB:
        while THR_BOB.is_alive():
            THR_BOB.stop()
            time.sleep(1)
        THR_BOB.kill()

    THR_BOB = \
        thread_with_trace(target=create_server_bob,
                          args=(bob_dir, bob_domain, bob_port, alice_address,
                                federation_list, False, False,
                                bob_send_threads),
                          daemon=True)

    THR_ALICE.start()
    THR_BOB.start()
    assert THR_ALICE.is_alive() is True
    assert THR_BOB.is_alive() is True

    # wait for all servers to be running
    ctr = 0
    while not (TEST_SERVER_ALICE_RUNNING and TEST_SERVER_BOB_RUNNING):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(TEST_SERVER_ALICE_RUNNING))
    print('Bob online: ' + str(TEST_SERVER_BOB_RUNNING))
    assert ctr <= 60
    time.sleep(1)

    signing_priv_key_pem = None
    session_client = create_session(proxy_type)

    # Get Bob's instance actor
    print('\n\n*********************************************************')
    print("Test Bob's instance actor")
    profile_str = 'https://www.w3.org/ns/activitystreams'
    test_headers = {
        'host': bob_address,
        'Accept': 'application/ld+json; profile="' + profile_str + '"'
    }
    bob_instance_actor_json = \
        get_json(signing_priv_key_pem, session_client,
                 'http://' + bob_address + '/@actor', test_headers, {}, True,
                 __version__, 'http', 'somedomain.or.other', 10, True)
    assert bob_instance_actor_json
    pprint(bob_instance_actor_json)
    assert bob_instance_actor_json['name'] == 'ACTOR'

    # In the beginning all was calm and there were no follows

    print('\n\n*********************************************************')
    print("Alice and Bob agree to share items catalogs")
    assert os.path.isdir(alice_dir)
    assert os.path.isdir(bob_dir)
    set_config_param(alice_dir, 'sharedItemsFederatedDomains', bob_address)
    set_config_param(bob_dir, 'sharedItemsFederatedDomains', alice_address)

    print('*********************************************************')
    print('Alice sends a follow request to Bob')
    os.chdir(alice_dir)
    session_alice = create_session(proxy_type)
    in_reply_to = None
    in_reply_to_atom_uri = None
    subject = None
    alice_post_log = []
    followers_only = False
    save_to_file = True
    client_to_server = False
    cc_url = None
    alice_person_cache = {}
    alice_cached_webfingers = {}
    alice_post_log = []
    bob_actor = http_prefix + '://' + bob_address + '/users/bob'
    send_result = \
        send_follow_request(session_alice, alice_dir,
                            'alice', alice_domain,
                            alice_domain, alice_port, http_prefix,
                            'bob', bob_domain, bob_actor,
                            bob_port, http_prefix,
                            client_to_server, federation_list,
                            alice_send_threads, alice_post_log,
                            alice_cached_webfingers, alice_person_cache,
                            True, __version__, signing_priv_key_pem,
                            alice_domain, None, None)
    print('send_result: ' + str(send_result))

    for _ in range(16):
        if os.path.isfile(bob_dir + '/accounts/bob@' +
                          bob_domain + '/followers.txt'):
            if os.path.isfile(alice_dir + '/accounts/alice@' +
                              alice_domain + '/following.txt'):
                if os.path.isfile(alice_dir + '/accounts/alice@' +
                                  alice_domain + '/followingCalendar.txt'):
                    break
        time.sleep(1)

    assert valid_inbox(bob_dir, 'bob', bob_domain)
    assert valid_inbox_filenames(bob_dir, 'bob', bob_domain,
                                 alice_domain, alice_port)
    assert 'alice@' + alice_domain in open(bob_dir + '/accounts/bob@' +
                                           bob_domain +
                                           '/followers.txt').read()
    assert 'bob@' + bob_domain in open(alice_dir + '/accounts/alice@' +
                                       alice_domain + '/following.txt').read()
    assert 'bob@' + bob_domain in open(alice_dir + '/accounts/alice@' +
                                       alice_domain +
                                       '/followingCalendar.txt').read()
    assert not is_group_actor(alice_dir, bob_actor, alice_person_cache)
    assert not is_group_account(bob_dir, 'bob', bob_domain)

    print('\n\n*********************************************************')
    print('Bob publishes some shared items')
    if os.path.isdir(bob_dir + '/ontology'):
        shutil.rmtree(bob_dir + '/ontology', ignore_errors=False, onerror=None)
    os.mkdir(bob_dir + '/ontology')
    copyfile(base_dir + '/img/logo.png', bob_dir + '/logo.png')
    copyfile(base_dir + '/ontology/foodTypes.json',
             bob_dir + '/ontology/foodTypes.json')
    copyfile(base_dir + '/ontology/toolTypes.json',
             bob_dir + '/ontology/toolTypes.json')
    copyfile(base_dir + '/ontology/clothesTypes.json',
             bob_dir + '/ontology/clothesTypes.json')
    copyfile(base_dir + '/ontology/medicalTypes.json',
             bob_dir + '/ontology/medicalTypes.json')
    copyfile(base_dir + '/ontology/accommodationTypes.json',
             bob_dir + '/ontology/accommodationTypes.json')
    assert os.path.isfile(bob_dir + '/logo.png')
    assert os.path.isfile(bob_dir + '/ontology/foodTypes.json')
    assert os.path.isfile(bob_dir + '/ontology/toolTypes.json')
    assert os.path.isfile(bob_dir + '/ontology/clothesTypes.json')
    assert os.path.isfile(bob_dir + '/ontology/medicalTypes.json')
    assert os.path.isfile(bob_dir + '/ontology/accommodationTypes.json')
    shared_item_name = 'cheddar'
    shared_item_description = 'Some cheese'
    shared_item_image_filename = 'logo.png'
    shared_item_qty = 1
    shared_item_type = 'Cheese'
    shared_item_category = 'Food'
    shared_item_location = "Bob's location"
    shared_item_duration = "10 days"
    shared_item_price = "1.30"
    shared_item_currency = "EUR"
    signing_priv_key_pem = None
    session_bob = create_session(proxy_type)
    share_json = \
        send_share_via_server(bob_dir, session_bob,
                              'bob', bob_password,
                              bob_domain, bob_port,
                              http_prefix, shared_item_name,
                              shared_item_description,
                              shared_item_image_filename,
                              shared_item_qty, shared_item_type,
                              shared_item_category,
                              shared_item_location, shared_item_duration,
                              bob_cached_webfingers, bob_person_cache,
                              True, __version__,
                              shared_item_price, shared_item_currency,
                              signing_priv_key_pem)
    assert share_json
    assert isinstance(share_json, dict)
    shared_item_name = 'Epicyon T-shirt'
    shared_item_description = 'A fashionable item'
    shared_item_image_filename = 'logo.png'
    shared_item_qty = 1
    shared_item_type = 'T-Shirt'
    shared_item_category = 'Clothes'
    shared_item_location = "Bob's location"
    shared_item_duration = "5 days"
    shared_item_price = "0"
    shared_item_currency = "EUR"
    share_json = \
        send_share_via_server(bob_dir, session_bob,
                              'bob', bob_password,
                              bob_domain, bob_port,
                              http_prefix, shared_item_name,
                              shared_item_description,
                              shared_item_image_filename,
                              shared_item_qty, shared_item_type,
                              shared_item_category,
                              shared_item_location, shared_item_duration,
                              bob_cached_webfingers, bob_person_cache,
                              True, __version__,
                              shared_item_price, shared_item_currency,
                              signing_priv_key_pem)
    assert share_json
    assert isinstance(share_json, dict)
    shared_item_name = 'Soldering iron'
    shared_item_description = 'A soldering iron'
    shared_item_image_filename = 'logo.png'
    shared_item_qty = 1
    shared_item_type = 'Soldering iron'
    shared_item_category = 'Tools'
    shared_item_location = "Bob's location"
    shared_item_duration = "9 days"
    shared_item_price = "10.00"
    shared_item_currency = "EUR"
    share_json = \
        send_share_via_server(bob_dir, session_bob,
                              'bob', bob_password,
                              bob_domain, bob_port,
                              http_prefix, shared_item_name,
                              shared_item_description,
                              shared_item_image_filename,
                              shared_item_qty, shared_item_type,
                              shared_item_category,
                              shared_item_location, shared_item_duration,
                              bob_cached_webfingers, bob_person_cache,
                              True, __version__,
                              shared_item_price, shared_item_currency,
                              signing_priv_key_pem)
    assert share_json
    assert isinstance(share_json, dict)

    time.sleep(2)
    print('\n\n*********************************************************')
    print('Bob has a shares.json file containing the uploaded items')

    shares_filename = bob_dir + '/accounts/bob@' + bob_domain + '/shares.json'
    assert os.path.isfile(shares_filename)
    shares_json = load_json(shares_filename)
    assert shares_json
    pprint(shares_json)
    assert len(shares_json.items()) == 3
    for item_id, item in shares_json.items():
        if not item.get('dfcId'):
            pprint(item)
            print(item_id + ' does not have dfcId field')
        assert item.get('dfcId')

    print('\n\n*********************************************************')
    print('Bob can read the shared items catalog on his own instance')
    signing_priv_key_pem = None
    catalog_json = \
        get_shared_items_catalog_via_server(bob_dir, session_bob,
                                            'bob', bob_password,
                                            bob_domain, bob_port,
                                            http_prefix, True,
                                            signing_priv_key_pem)
    assert catalog_json
    pprint(catalog_json)
    assert 'DFC:supplies' in catalog_json
    assert len(catalog_json.get('DFC:supplies')) == 3

    print('\n\n*********************************************************')
    print('Alice sends a message to Bob')
    alice_tokens_filename = \
        alice_dir + '/accounts/sharedItemsFederationTokens.json'
    assert os.path.isfile(alice_tokens_filename)
    alice_shared_item_federation_tokens = load_json(alice_tokens_filename)
    assert alice_shared_item_federation_tokens
    print('Alice shared item federation tokens:')
    pprint(alice_shared_item_federation_tokens)
    assert len(alice_shared_item_federation_tokens.items()) > 0
    for host_str, token in alice_shared_item_federation_tokens.items():
        assert ':' in host_str
    alice_post_log = []
    alice_person_cache = {}
    alice_cached_webfingers = {}
    alice_shared_items_federated_domains = [bob_address]
    alice_post_log = []
    is_article = False
    city = 'London, England'
    low_bandwidth = False
    signing_priv_key_pem = None
    send_result = \
        send_post(signing_priv_key_pem, __version__,
                  session_alice, alice_dir, 'alice', alice_domain, alice_port,
                  'bob', bob_domain, bob_port, cc_url,
                  http_prefix, 'Alice message', followers_only, save_to_file,
                  client_to_server, True,
                  None, None, None, city, federation_list,
                  alice_send_threads, alice_post_log, alice_cached_webfingers,
                  alice_person_cache, is_article, system_language,
                  languages_understood,
                  alice_shared_items_federated_domains,
                  alice_shared_item_federation_tokens, low_bandwidth,
                  content_license_url, True,
                  in_reply_to, in_reply_to_atom_uri, subject)
    print('send_result: ' + str(send_result))

    queue_path = bob_dir + '/accounts/bob@' + bob_domain + '/queue'
    inbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/inbox'
    alice_message_arrived = False
    for _ in range(20):
        time.sleep(1)
        if os.path.isdir(inbox_path):
            if len([name for name in os.listdir(inbox_path)
                    if os.path.isfile(os.path.join(inbox_path, name))]) > 0:
                alice_message_arrived = True
                print('Alice message sent to Bob!')
                break

    assert alice_message_arrived is True
    print('Message from Alice to Bob succeeded')

    print('\n\n*********************************************************')
    print('Check that Alice received the shared items authorization')
    print('token from Bob')
    alice_tokens_filename = \
        alice_dir + '/accounts/sharedItemsFederationTokens.json'
    bob_tokens_filename = \
        bob_dir + '/accounts/sharedItemsFederationTokens.json'
    assert os.path.isfile(alice_tokens_filename)
    assert os.path.isfile(bob_tokens_filename)
    alice_tokens = load_json(alice_tokens_filename)
    assert alice_tokens
    for host_str, token in alice_tokens.items():
        assert ':' in host_str
    assert alice_tokens.get(alice_address)
    print('Alice tokens')
    pprint(alice_tokens)
    bob_tokens = load_json(bob_tokens_filename)
    assert bob_tokens
    for host_str, token in bob_tokens.items():
        assert ':' in host_str
    assert bob_tokens.get(bob_address)
    print("Check that Bob now has Alice's token")
    assert bob_tokens.get(alice_address)
    print('Bob tokens')
    pprint(bob_tokens)

    print('\n\n*********************************************************')
    print('Alice can read the federated shared items catalog of Bob')
    headers = {
        'Origin': alice_address,
        'Authorization': bob_tokens[bob_address],
        'host': bob_address,
        'Accept': 'application/json'
    }
    url = http_prefix + '://' + bob_address + '/catalog'
    signing_priv_key_pem = None
    catalog_json = get_json(signing_priv_key_pem, session_alice, url, headers,
                            None, True)
    assert catalog_json
    pprint(catalog_json)
    assert 'DFC:supplies' in catalog_json
    assert len(catalog_json.get('DFC:supplies')) == 3

    # queue item removed
    ctr = 0
    while len([name for name in os.listdir(queue_path)
               if os.path.isfile(os.path.join(queue_path, name))]) > 0:
        ctr += 1
        if ctr > 10:
            break
        time.sleep(1)

#    assert len([name for name in os.listdir(queue_path)
#                if os.path.isfile(os.path.join(queue_path, name))]) == 0

    # stop the servers
    THR_ALICE.kill()
    THR_ALICE.join()
    assert THR_ALICE.is_alive() is False

    THR_BOB.kill()
    THR_BOB.join()
    assert THR_BOB.is_alive() is False

    os.chdir(base_dir)
    shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    print('Testing federation of shared items between ' +
          'Alice and Bob is complete')


def test_group_follow(base_dir: str) -> None:
    print('Testing following of a group')

    global TEST_SERVER_ALICE_RUNNING
    global TEST_SERVER_BOB_RUNNING
    global TEST_SERVER_GROUP_RUNNING
    system_language = 'en'
    languages_understood = [system_language]
    TEST_SERVER_ALICE_RUNNING = False
    TEST_SERVER_BOB_RUNNING = False
    TEST_SERVER_GROUP_RUNNING = False

    # system_language = 'en'
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    alice_dir = base_dir + '/.tests/alice'
    alice_domain = '127.0.0.57'
    alice_port = 61927
    alice_send_threads = []
    alice_address = alice_domain + ':' + str(alice_port)

    bob_dir = base_dir + '/.tests/bob'
    bob_domain = '127.0.0.59'
    bob_port = 61814
    bob_send_threads = []
    # bob_address = bob_domain + ':' + str(bob_port)

    testgroup_dir = base_dir + '/.tests/testgroup'
    testgroup_domain = '127.0.0.63'
    testgroupPort = 61925
    testgroupSendThreads = []
    testgroupAddress = testgroup_domain + ':' + str(testgroupPort)

    global THR_ALICE
    if THR_ALICE:
        while THR_ALICE.is_alive():
            THR_ALICE.stop()
            time.sleep(1)
        THR_ALICE.kill()

    THR_ALICE = \
        thread_with_trace(target=create_server_alice,
                          args=(alice_dir, alice_domain, alice_port,
                                testgroupAddress,
                                federation_list, False, True,
                                alice_send_threads),
                          daemon=True)

    global THR_BOB
    if THR_BOB:
        while THR_BOB.is_alive():
            THR_BOB.stop()
            time.sleep(1)
        THR_BOB.kill()

    THR_BOB = \
        thread_with_trace(target=create_server_bob,
                          args=(bob_dir, bob_domain, bob_port, None,
                                federation_list, False, False,
                                bob_send_threads),
                          daemon=True)

    global THR_GROUP
    if THR_GROUP:
        while THR_GROUP.is_alive():
            THR_GROUP.stop()
            time.sleep(1)
        THR_GROUP.kill()

    THR_GROUP = \
        thread_with_trace(target=create_server_group,
                          args=(testgroup_dir, testgroup_domain, testgroupPort,
                                federation_list, False, False,
                                testgroupSendThreads),
                          daemon=True)

    THR_ALICE.start()
    THR_BOB.start()
    THR_GROUP.start()
    assert THR_ALICE.is_alive() is True
    assert THR_BOB.is_alive() is True
    assert THR_GROUP.is_alive() is True

    # wait for all servers to be running
    ctr = 0
    while not (TEST_SERVER_ALICE_RUNNING and
               TEST_SERVER_BOB_RUNNING and
               TEST_SERVER_GROUP_RUNNING):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(TEST_SERVER_ALICE_RUNNING))
    print('Bob online: ' + str(TEST_SERVER_BOB_RUNNING))
    print('Test Group online: ' + str(TEST_SERVER_GROUP_RUNNING))
    assert ctr <= 60
    time.sleep(1)

    print('*********************************************************')
    print('Alice has some outbox posts')
    alice_outbox = 'http://' + alice_address + '/users/alice/outbox'
    session = create_session(None)
    profile_str = 'https://www.w3.org/ns/activitystreams'
    as_header = {
        'Accept': 'application/ld+json; profile="' + profile_str + '"'
    }
    signing_priv_key_pem = None
    outbox_json = get_json(signing_priv_key_pem, session, alice_outbox,
                           as_header, None, True, __version__, 'http', None)
    assert outbox_json
    pprint(outbox_json)
    assert outbox_json['type'] == 'OrderedCollection'
    assert 'first' in outbox_json
    first_page = outbox_json['first']
    assert 'totalItems' in outbox_json
    print('Alice outbox totalItems: ' + str(outbox_json['totalItems']))
    assert outbox_json['totalItems'] == 3

    outbox_json = get_json(signing_priv_key_pem, session,
                           first_page, as_header,
                           None, True, __version__, 'http', None)
    assert outbox_json
    pprint(outbox_json)
    assert 'orderedItems' in outbox_json
    assert outbox_json['type'] == 'OrderedCollectionPage'
    print('Alice outbox orderedItems: ' +
          str(len(outbox_json['orderedItems'])))
    assert len(outbox_json['orderedItems']) == 3

    queue_path = \
        testgroup_dir + '/accounts/testgroup@' + testgroup_domain + '/queue'

    # In the beginning the test group had no followers

    print('*********************************************************')
    print('Alice sends a follow request to the test group')
    os.chdir(alice_dir)
    session_alice = create_session(proxy_type)
    in_reply_to = None
    in_reply_to_atom_uri = None
    subject = None
    alice_post_log = []
    followers_only = False
    save_to_file = True
    client_to_server = False
    cc_url = None
    alice_person_cache = {}
    alice_cached_webfingers = {}
    alice_post_log = []
    # aliceActor = http_prefix + '://' + alice_address + '/users/alice'
    testgroup_actor = \
        http_prefix + '://' + testgroupAddress + '/users/testgroup'
    signing_priv_key_pem = None
    send_result = \
        send_follow_request(session_alice, alice_dir,
                            'alice', alice_domain,
                            alice_domain, alice_port, http_prefix,
                            'testgroup', testgroup_domain, testgroup_actor,
                            testgroupPort, http_prefix,
                            client_to_server, federation_list,
                            alice_send_threads, alice_post_log,
                            alice_cached_webfingers, alice_person_cache,
                            True, __version__, signing_priv_key_pem,
                            alice_domain, None, None)
    print('send_result: ' + str(send_result))

    alice_following_filename = \
        alice_dir + '/accounts/alice@' + alice_domain + '/following.txt'
    alice_following_calendar_filename = \
        alice_dir + '/accounts/alice@' + alice_domain + \
        '/followingCalendar.txt'
    testgroup_followers_filename = \
        testgroup_dir + '/accounts/testgroup@' + testgroup_domain + \
        '/followers.txt'

    for _ in range(16):
        if os.path.isfile(testgroup_followers_filename):
            if os.path.isfile(alice_following_filename):
                if os.path.isfile(alice_following_calendar_filename):
                    break
        time.sleep(1)

    assert valid_inbox(testgroup_dir, 'testgroup', testgroup_domain)
    assert valid_inbox_filenames(testgroup_dir, 'testgroup', testgroup_domain,
                                 alice_domain, alice_port)
    assert 'alice@' + alice_domain in open(testgroup_followers_filename).read()
    assert '!alice@' + alice_domain not in \
        open(testgroup_followers_filename).read()

    testgroup_webfinger_filename = \
        testgroup_dir + '/wfendpoints/testgroup@' + \
        testgroup_domain + ':' + str(testgroupPort) + '.json'
    assert os.path.isfile(testgroup_webfinger_filename)
    assert 'acct:testgroup@' in open(testgroup_webfinger_filename).read()
    print('acct: exists within the webfinger endpoint for testgroup')

    testgroup_handle = 'testgroup@' + testgroup_domain
    following_str = ''
    with open(alice_following_filename, 'r') as fp_foll:
        following_str = fp_foll.read()
        print('Alice following.txt:\n\n' + following_str)
    if '!testgroup' not in following_str:
        print('Alice following.txt does not contain !testgroup@' +
              testgroup_domain + ':' + str(testgroupPort))
    assert is_group_actor(alice_dir, testgroup_actor, alice_person_cache)
    assert not is_group_account(alice_dir, 'alice', alice_domain)
    assert is_group_account(testgroup_dir, 'testgroup', testgroup_domain)
    assert '!testgroup' in following_str
    assert testgroup_handle in open(alice_following_filename).read()
    assert testgroup_handle in open(alice_following_calendar_filename).read()
    print('\n\n*********************************************************')
    print('Alice follows the test group')

    print('*********************************************************')
    print('Bob sends a follow request to the test group')
    os.chdir(bob_dir)
    session_bob = create_session(proxy_type)
    in_reply_to = None
    in_reply_to_atom_uri = None
    subject = None
    bob_post_log = []
    followers_only = False
    save_to_file = True
    client_to_server = False
    cc_url = None
    bob_person_cache = {}
    bob_cached_webfingers = {}
    bob_post_log = []
    # bob_actor = http_prefix + '://' + bob_address + '/users/bob'
    testgroup_actor = \
        http_prefix + '://' + testgroupAddress + '/users/testgroup'
    signing_priv_key_pem = None
    send_result = \
        send_follow_request(session_bob, bob_dir,
                            'bob', bob_domain,
                            bob_domain, bob_port, http_prefix,
                            'testgroup', testgroup_domain, testgroup_actor,
                            testgroupPort, http_prefix,
                            client_to_server, federation_list,
                            bob_send_threads, bob_post_log,
                            bob_cached_webfingers, bob_person_cache,
                            True, __version__, signing_priv_key_pem,
                            bob_domain, None, None)
    print('send_result: ' + str(send_result))

    bob_following_filename = \
        bob_dir + '/accounts/bob@' + bob_domain + '/following.txt'
    bob_following_calendar_filename = \
        bob_dir + '/accounts/bob@' + bob_domain + \
        '/followingCalendar.txt'
    testgroup_followers_filename = \
        testgroup_dir + '/accounts/testgroup@' + testgroup_domain + \
        '/followers.txt'

    for _ in range(16):
        if os.path.isfile(testgroup_followers_filename):
            if os.path.isfile(bob_following_filename):
                if os.path.isfile(bob_following_calendar_filename):
                    break
        time.sleep(1)

    assert valid_inbox(testgroup_dir, 'testgroup', testgroup_domain)
    assert valid_inbox_filenames(testgroup_dir, 'testgroup', testgroup_domain,
                                 bob_domain, bob_port)
    assert 'bob@' + bob_domain in open(testgroup_followers_filename).read()
    assert '!bob@' + bob_domain not in \
        open(testgroup_followers_filename).read()

    testgroup_webfinger_filename = \
        testgroup_dir + '/wfendpoints/testgroup@' + \
        testgroup_domain + ':' + str(testgroupPort) + '.json'
    assert os.path.isfile(testgroup_webfinger_filename)
    assert 'acct:testgroup@' in open(testgroup_webfinger_filename).read()
    print('acct: exists within the webfinger endpoint for testgroup')

    testgroup_handle = 'testgroup@' + testgroup_domain
    following_str = ''
    with open(bob_following_filename, 'r') as fp_foll:
        following_str = fp_foll.read()
        print('Bob following.txt:\n\n' + following_str)
    if '!testgroup' not in following_str:
        print('Bob following.txt does not contain !testgroup@' +
              testgroup_domain + ':' + str(testgroupPort))
    assert is_group_actor(bob_dir, testgroup_actor, bob_person_cache)
    assert '!testgroup' in following_str
    assert testgroup_handle in open(bob_following_filename).read()
    assert testgroup_handle in open(bob_following_calendar_filename).read()
    print('Bob follows the test group')

    print('\n\n*********************************************************')
    print('Alice posts to the test group')
    inbox_path_bob = \
        bob_dir + '/accounts/bob@' + bob_domain + '/inbox'
    start_posts_bob = \
        len([name for name in os.listdir(inbox_path_bob)
             if os.path.isfile(os.path.join(inbox_path_bob, name))])
    assert start_posts_bob == 0
    alice_post_log = []
    alice_person_cache = {}
    alice_cached_webfingers = {}
    alice_shared_items_federated_domains = []
    alice_shared_item_federation_tokens = {}
    alice_post_log = []
    is_article = False
    city = 'London, England'
    low_bandwidth = False
    signing_priv_key_pem = None

    queue_path = \
        testgroup_dir + '/accounts/testgroup@' + testgroup_domain + '/queue'
    inbox_path = \
        testgroup_dir + '/accounts/testgroup@' + testgroup_domain + '/inbox'
    outbox_path = \
        testgroup_dir + '/accounts/testgroup@' + testgroup_domain + '/outbox'
    alice_message_arrived = False
    start_posts_inbox = \
        len([name for name in os.listdir(inbox_path)
             if os.path.isfile(os.path.join(inbox_path, name))])
    start_posts_outbox = \
        len([name for name in os.listdir(outbox_path)
             if os.path.isfile(os.path.join(outbox_path, name))])

    send_result = \
        send_post(signing_priv_key_pem, __version__,
                  session_alice, alice_dir, 'alice', alice_domain, alice_port,
                  'testgroup', testgroup_domain, testgroupPort, cc_url,
                  http_prefix, "Alice group message", followers_only,
                  save_to_file, client_to_server, True,
                  None, None, None, city, federation_list,
                  alice_send_threads, alice_post_log, alice_cached_webfingers,
                  alice_person_cache, is_article, system_language,
                  languages_understood,
                  alice_shared_items_federated_domains,
                  alice_shared_item_federation_tokens, low_bandwidth,
                  content_license_url,
                  in_reply_to, in_reply_to_atom_uri, subject)
    print('send_result: ' + str(send_result))

    for _ in range(20):
        time.sleep(1)
        if os.path.isdir(inbox_path):
            curr_posts_inbox = \
                len([name for name in os.listdir(inbox_path)
                     if os.path.isfile(os.path.join(inbox_path, name))])
            curr_posts_outbox = \
                len([name for name in os.listdir(outbox_path)
                     if os.path.isfile(os.path.join(outbox_path, name))])
            if curr_posts_inbox > start_posts_inbox and \
               curr_posts_outbox > start_posts_outbox:
                alice_message_arrived = True
                print('Alice post sent to test group!')
                break

    assert alice_message_arrived is True
    print('\n\n*********************************************************')
    print('Post from Alice to test group succeeded')

    print('\n\n*********************************************************')
    print('Check that post was relayed from test group to bob')

    bob_message_arrived = False
    for _ in range(20):
        time.sleep(1)
        if os.path.isdir(inbox_path_bob):
            curr_posts_bob = \
                len([name for name in os.listdir(inbox_path_bob)
                     if os.path.isfile(os.path.join(inbox_path_bob, name))])
            if curr_posts_bob > start_posts_bob:
                bob_message_arrived = True
                print('Bob received relayed group post!')
                break

    assert bob_message_arrived is True

    # check that the received post has an id from the group,
    # not from the original sender (alice)
    group_id_checked = False
    for name in os.listdir(inbox_path_bob):
        filename = os.path.join(inbox_path_bob, name)
        if os.path.isfile(filename):
            received_json = load_json(filename)
            assert received_json
            print('Received group post ' + received_json['id'])
            assert '/testgroup/statuses/' in received_json['id']
            group_id_checked = True
            break
    assert group_id_checked

    # stop the servers
    THR_ALICE.kill()
    THR_ALICE.join()
    assert THR_ALICE.is_alive() is False

    THR_BOB.kill()
    THR_BOB.join()
    assert THR_BOB.is_alive() is False

    THR_GROUP.kill()
    THR_GROUP.join()
    assert THR_GROUP.is_alive() is False

    # queue item removed
    time.sleep(4)
    assert len([name for name in os.listdir(queue_path)
                if os.path.isfile(os.path.join(queue_path, name))]) == 0

    os.chdir(base_dir)
    shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    print('Testing following of a group is complete')


def _test_followers_of_person(base_dir: str) -> None:
    print('test_followers_of_person')
    curr_dir = base_dir
    nickname = 'mxpop'
    domain = 'diva.domain'
    password = 'birb'
    port = 80
    http_prefix = 'https'
    federation_list = []
    base_dir = curr_dir + '/.tests_followersofperson'
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

    follow_list = get_followers_of_person(base_dir, 'ultrapancake', domain)
    assert len(follow_list) == 3
    assert 'mxpop@' + domain in follow_list
    assert 'drokk@' + domain in follow_list
    assert 'sausagedog@' + domain in follow_list
    os.chdir(curr_dir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_followers_on_domain(base_dir: str) -> None:
    print('test_followers_on_domain')
    curr_dir = base_dir
    nickname = 'mxpop'
    domain = 'diva.domain'
    otherdomain = 'soup.dragon'
    password = 'birb'
    port = 80
    http_prefix = 'https'
    federation_list = []
    base_dir = curr_dir + '/.tests_nooffollowersOndomain'
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

    followers_on_other_domain = \
        no_of_followers_on_domain(base_dir,
                                  nickname + '@' + domain, otherdomain)
    assert followers_on_other_domain == 3

    unfollower_of_account(base_dir, nickname, domain, 'sausagedog',
                          otherdomain, False, False)
    followers_on_other_domain = \
        no_of_followers_on_domain(base_dir,
                                  nickname + '@' + domain, otherdomain)
    assert followers_on_other_domain == 2

    os.chdir(curr_dir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_group_followers(base_dir: str) -> None:
    print('test_group_followers')

    curr_dir = base_dir
    nickname = 'test735'
    domain = 'mydomain.com'
    password = 'somepass'
    port = 80
    http_prefix = 'https'
    federation_list = []
    base_dir = curr_dir + '/.tests_testgroupfollowers'
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

    os.chdir(curr_dir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_follows(base_dir: str) -> None:
    print('test_follows')
    curr_dir = base_dir
    nickname = 'test529'
    domain = 'testdomain.com'
    password = 'mypass'
    port = 80
    http_prefix = 'https'
    federation_list = ['wild.com', 'mesh.com']
    base_dir = curr_dir + '/.tests_testfollows'
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

    account_dir = acct_dir(base_dir, nickname, domain)
    with open(account_dir + '/following.txt', 'r') as fp_foll:
        domain_found = False
        for following_domain in fp_foll:
            test_domain = following_domain.split('@')[1]
            test_domain = test_domain.replace('\n', '').replace('\r', '')
            if test_domain == 'mesh.com':
                domain_found = True
            if test_domain not in federation_list:
                print(test_domain)
                assert False

        assert domain_found
        unfollow_account(base_dir, nickname, domain, 'batman', 'mesh.com',
                         True, False)

        domain_found = False
        for following_domain in fp_foll:
            test_domain = following_domain.split('@')[1]
            test_domain = test_domain.replace('\n', '').replace('\r', '')
            if test_domain == 'mesh.com':
                domain_found = True
        assert domain_found is False

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

    account_dir = acct_dir(base_dir, nickname, domain)
    with open(account_dir + '/followers.txt', 'r') as fp_foll:
        for follower_domain in fp_foll:
            test_domain = follower_domain.split('@')[1]
            test_domain = test_domain.replace('\n', '').replace('\r', '')
            if test_domain not in federation_list:
                print(test_domain)
                assert False

    os.chdir(curr_dir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def _test_create_person_account(base_dir: str):
    print('test_create_person_account')
    system_language = 'en'
    languages_understood = [system_language]
    curr_dir = base_dir
    nickname = 'test382'
    domain = 'badgerdomain.com'
    password = 'mypass'
    port = 80
    http_prefix = 'https'
    client_to_server = False
    base_dir = curr_dir + '/.tests_createperson'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)

    private_key_pem, public_key_pem, person, wf_endpoint = \
        create_person(base_dir, nickname, domain, port,
                      http_prefix, True, False, password)
    assert private_key_pem
    assert public_key_pem
    assert person
    assert wf_endpoint
    assert os.path.isfile(base_dir + '/accounts/passwords')
    delete_all_posts(base_dir, nickname, domain, 'inbox')
    delete_all_posts(base_dir, nickname, domain, 'outbox')
    set_display_nickname(base_dir, nickname, domain, 'badger')
    set_bio(base_dir, nickname, domain, 'Randomly roaming in your backyard')
    archive_posts_for_person(nickname, domain, base_dir, 'inbox', None, {}, 4)
    archive_posts_for_person(nickname, domain, base_dir, 'outbox', None, {}, 4)
    test_in_reply_to = None
    test_in_reply_to_atom_uri = None
    test_subject = None
    test_schedule_post = False
    test_event_date = None
    test_event_time = None
    test_location = None
    test_is_article = False
    followers_only = False
    save_to_file = True
    comments_enabled = True
    attach_image_filename = None
    media_type = None
    conversation_id = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    content = \
        "If your \"independent organization\" is government funded...\n\n" + \
        "(yawn)\n\n...then it's not really independent.\n\n" + \
        "Politicians will threaten to withdraw funding if you do " + \
        "anything which challenges middle class sensibilities or incomes."
    test_post_json = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content, followers_only, save_to_file,
                           client_to_server,
                           comments_enabled, attach_image_filename, media_type,
                           'Not suitable for Vogons', 'London, England',
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
    assert test_post_json
    assert test_post_json.get('object')
    assert test_post_json['object']['content']
    assert '(yawn)' in test_post_json['object']['content']

    os.chdir(curr_dir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def show_test_boxes(name: str, inbox_path: str, outbox_path: str) -> None:
    inbox_posts = \
        len([name for name in os.listdir(inbox_path)
             if os.path.isfile(os.path.join(inbox_path, name))])
    outbox_posts = \
        len([name for name in os.listdir(outbox_path)
             if os.path.isfile(os.path.join(outbox_path, name))])
    print('EVENT: ' + name +
          ' inbox has ' + str(inbox_posts) + ' posts and ' +
          str(outbox_posts) + ' outbox posts')


def _test_authentication(base_dir: str) -> None:
    print('test_authentication')
    curr_dir = base_dir
    nickname = 'test8743'
    password = 'SuperSecretPassword12345'

    base_dir = curr_dir + '/.tests_authentication'
    if os.path.isdir(base_dir):
        shutil.rmtree(base_dir, ignore_errors=False, onerror=None)
    os.mkdir(base_dir)
    os.chdir(base_dir)

    assert store_basic_credentials(base_dir, 'othernick', 'otherpass')
    assert store_basic_credentials(base_dir, 'bad:nick', 'otherpass') is False
    assert store_basic_credentials(base_dir, 'badnick', 'otherpa:ss') is False
    assert store_basic_credentials(base_dir, nickname, password)

    auth_header = create_basic_auth_header(nickname, password)
    assert authorize_basic(base_dir, '/users/' + nickname + '/inbox',
                           auth_header, False)
    assert authorize_basic(base_dir, '/users/' + nickname,
                           auth_header, False) is False
    assert authorize_basic(base_dir, '/users/othernick/inbox',
                           auth_header, False) is False

    auth_header = create_basic_auth_header(nickname, password + '1')
    assert authorize_basic(base_dir, '/users/' + nickname + '/inbox',
                           auth_header, False) is False

    password = 'someOtherPassword'
    assert store_basic_credentials(base_dir, nickname, password)

    auth_header = create_basic_auth_header(nickname, password)
    assert authorize_basic(base_dir, '/users/' + nickname + '/inbox',
                           auth_header, False)

    os.chdir(curr_dir)
    shutil.rmtree(base_dir, ignore_errors=False, onerror=None)


def test_client_to_server(base_dir: str):
    print('EVENT: Testing sending a post via c2s')

    global TEST_SERVER_ALICE_RUNNING
    global TEST_SERVER_BOB_RUNNING
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    TEST_SERVER_ALICE_RUNNING = False
    TEST_SERVER_BOB_RUNNING = False

    system_language = 'en'
    languages_understood = [system_language]
    http_prefix = 'http'
    proxy_type = None
    federation_list = []
    low_bandwidth = False

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the servers
    alice_dir = base_dir + '/.tests/alice'
    alice_domain = '127.0.0.42'
    alice_port = 61935
    alice_send_threads = []
    alice_address = alice_domain + ':' + str(alice_port)

    bob_dir = base_dir + '/.tests/bob'
    bob_domain = '127.0.0.64'
    bob_port = 61936
    bob_send_threads = []
    bob_address = bob_domain + ':' + str(bob_port)

    global THR_ALICE
    if THR_ALICE:
        while THR_ALICE.is_alive():
            THR_ALICE.stop()
            time.sleep(1)
        THR_ALICE.kill()

    THR_ALICE = \
        thread_with_trace(target=create_server_alice,
                          args=(alice_dir, alice_domain, alice_port,
                                bob_address, federation_list, False, False,
                                alice_send_threads),
                          daemon=True)

    global THR_BOB
    if THR_BOB:
        while THR_BOB.is_alive():
            THR_BOB.stop()
            time.sleep(1)
        THR_BOB.kill()

    THR_BOB = \
        thread_with_trace(target=create_server_bob,
                          args=(bob_dir, bob_domain, bob_port, alice_address,
                                federation_list, False, False,
                                bob_send_threads),
                          daemon=True)

    THR_ALICE.start()
    THR_BOB.start()
    assert THR_ALICE.is_alive() is True
    assert THR_BOB.is_alive() is True

    # wait for both servers to be running
    ctr = 0
    while not (TEST_SERVER_ALICE_RUNNING and TEST_SERVER_BOB_RUNNING):
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(TEST_SERVER_ALICE_RUNNING))
    print('Bob online: ' + str(TEST_SERVER_BOB_RUNNING))

    time.sleep(1)

    # set bob to be following the calendar of alice
    print('Bob follows the calendar of Alice')
    following_cal_path = \
        bob_dir + '/accounts/bob@' + bob_domain + '/followingCalendar.txt'
    with open(following_cal_path, 'w+') as fp:
        fp.write('alice@' + alice_domain + '\n')

    print('\n\n*******************************************************')
    print('EVENT: Alice sends to Bob via c2s')

    session_alice = create_session(proxy_type)
    followers_only = False
    attached_image_filename = base_dir + '/img/logo.png'
    media_type = get_attachment_media_type(attached_image_filename)
    attached_image_description = 'Logo'
    city = 'London, England'
    is_article = False
    cached_webfingers = {}
    person_cache = {}
    password = 'alicepass'
    conversation_id = None

    alice_inbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/inbox'
    alice_outbox_path = \
        alice_dir + '/accounts/alice@' + alice_domain + '/outbox'
    bob_inbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/inbox'
    bob_outbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/outbox'

    outbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/outbox'
    inbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/inbox'
    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    assert len([name for name in os.listdir(alice_inbox_path)
                if os.path.isfile(os.path.join(alice_inbox_path, name))]) == 0
    assert len([name for name in os.listdir(alice_outbox_path)
                if os.path.isfile(os.path.join(alice_outbox_path, name))]) == 0
    assert len([name for name in os.listdir(bob_inbox_path)
                if os.path.isfile(os.path.join(bob_inbox_path, name))]) == 0
    assert len([name for name in os.listdir(bob_outbox_path)
                if os.path.isfile(os.path.join(bob_outbox_path, name))]) == 0
    print('EVENT: all inboxes and outboxes are empty')
    signing_priv_key_pem = None
    test_date = datetime.datetime.now()
    event_date = \
        str(test_date.year) + '-' + str(test_date.month) + '-' + \
        str(test_date.day)
    event_time = '11:45'
    location = "Kinshasa"
    send_result = \
        send_post_via_server(signing_priv_key_pem, __version__,
                             alice_dir, session_alice, 'alice', password,
                             alice_domain, alice_port,
                             'bob', bob_domain, bob_port, None,
                             http_prefix, 'Sent from my ActivityPub client',
                             followers_only, True,
                             attached_image_filename, media_type,
                             attached_image_description, city,
                             cached_webfingers, person_cache, is_article,
                             system_language, languages_understood,
                             low_bandwidth, content_license_url,
                             event_date, event_time, location,
                             True, None, None,
                             conversation_id, None)
    print('send_result: ' + str(send_result))

    for _ in range(30):
        if os.path.isdir(outbox_path):
            if len([name for name in os.listdir(outbox_path)
                    if os.path.isfile(os.path.join(outbox_path, name))]) == 1:
                break
        time.sleep(1)

    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    assert len([name for name in os.listdir(alice_inbox_path)
                if os.path.isfile(os.path.join(alice_inbox_path, name))]) == 0
    assert len([name for name in os.listdir(alice_outbox_path)
                if os.path.isfile(os.path.join(alice_outbox_path, name))]) == 1
    print(">>> c2s post arrived in Alice's outbox\n\n\n")

    for _ in range(30):
        if os.path.isdir(inbox_path):
            if len([name for name in os.listdir(bob_inbox_path)
                    if os.path.isfile(os.path.join(bob_inbox_path,
                                                   name))]) == 1:
                break
        time.sleep(1)

    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    assert len([name for name in os.listdir(bob_inbox_path)
                if os.path.isfile(os.path.join(bob_inbox_path, name))]) == 1
    assert len([name for name in os.listdir(bob_outbox_path)
                if os.path.isfile(os.path.join(bob_outbox_path, name))]) == 0

    print(">>> s2s post arrived in Bob's inbox")

    time.sleep(2)

    calendar_path = bob_dir + '/accounts/bob@' + bob_domain + '/calendar'
    if not os.path.isdir(calendar_path):
        print('Missing calendar path: ' + calendar_path)
    assert os.path.isdir(calendar_path)
    assert os.path.isdir(calendar_path + '/' + str(test_date.year))
    assert os.path.isfile(calendar_path + '/' + str(test_date.year) + '/' +
                          str(test_date.month) + '.txt')
    print(">>> calendar entry created for s2s post which arrived at " +
          "Bob's inbox")

    print("c2s send success\n\n\n")

    print('\n\nEVENT: Getting message id for the post')
    status_number = 0
    outbox_post_filename = None
    outbox_post_id = None
    for name in os.listdir(outbox_path):
        if '#statuses#' in name:
            status_number = name.split('#statuses#')[1].replace('.json', '')
            status_number = int(status_number.replace('#activity', ''))
            outbox_post_filename = outbox_path + '/' + name
            post_json_object = load_json(outbox_post_filename, 0)
            if post_json_object:
                outbox_post_id = remove_id_ending(post_json_object['id'])
    assert outbox_post_id
    print('message id obtained: ' + outbox_post_id)
    assert valid_inbox(bob_dir, 'bob', bob_domain)
    assert valid_inbox_filenames(bob_dir, 'bob', bob_domain,
                                 alice_domain, alice_port)

    print('\n\nAlice follows Bob')
    signing_priv_key_pem = None
    send_follow_request_via_server(alice_dir, session_alice,
                                   'alice', password,
                                   alice_domain, alice_port,
                                   'bob', bob_domain, bob_port,
                                   http_prefix,
                                   cached_webfingers, person_cache,
                                   True, __version__, signing_priv_key_pem)
    alice_petnames_filename = alice_dir + '/accounts/' + \
        'alice@' + alice_domain + '/petnames.txt'
    alice_following_filename = \
        alice_dir + '/accounts/alice@' + alice_domain + '/following.txt'
    bob_followers_filename = \
        bob_dir + '/accounts/bob@' + bob_domain + '/followers.txt'
    for _ in range(10):
        if os.path.isfile(bob_followers_filename):
            if 'alice@' + alice_domain + ':' + str(alice_port) in \
               open(bob_followers_filename).read():
                if os.path.isfile(alice_following_filename) and \
                   os.path.isfile(alice_petnames_filename):
                    if 'bob@' + bob_domain + ':' + str(bob_port) in \
                       open(alice_following_filename).read():
                        break
        time.sleep(1)

    assert os.path.isfile(bob_followers_filename)
    assert os.path.isfile(alice_following_filename)
    assert os.path.isfile(alice_petnames_filename)
    assert 'bob bob@' + bob_domain in \
        open(alice_petnames_filename).read()
    print('alice@' + alice_domain + ':' + str(alice_port) + ' in ' +
          bob_followers_filename)
    assert 'alice@' + alice_domain + ':' + str(alice_port) in \
        open(bob_followers_filename).read()
    print('bob@' + bob_domain + ':' + str(bob_port) + ' in ' +
          alice_following_filename)
    assert 'bob@' + bob_domain + ':' + str(bob_port) in \
        open(alice_following_filename).read()
    assert valid_inbox(bob_dir, 'bob', bob_domain)
    assert valid_inbox_filenames(bob_dir, 'bob', bob_domain,
                                 alice_domain, alice_port)

    print('\n\nEVENT: Bob follows Alice')
    send_follow_request_via_server(alice_dir, session_alice,
                                   'bob', 'bobpass',
                                   bob_domain, bob_port,
                                   'alice', alice_domain, alice_port,
                                   http_prefix,
                                   cached_webfingers, person_cache,
                                   True, __version__, signing_priv_key_pem)
    for _ in range(10):
        if os.path.isfile(alice_dir + '/accounts/alice@' + alice_domain +
                          '/followers.txt'):
            if 'bob@' + bob_domain + ':' + str(bob_port) in \
               open(alice_dir + '/accounts/alice@' + alice_domain +
                    '/followers.txt').read():
                if os.path.isfile(bob_dir + '/accounts/bob@' + bob_domain +
                                  '/following.txt'):
                    alice_handle_str = \
                        'alice@' + alice_domain + ':' + str(alice_port)
                    if alice_handle_str in \
                       open(bob_dir + '/accounts/bob@' + bob_domain +
                            '/following.txt').read():
                        if os.path.isfile(bob_dir + '/accounts/bob@' +
                                          bob_domain +
                                          '/followingCalendar.txt'):
                            if alice_handle_str in \
                               open(bob_dir + '/accounts/bob@' + bob_domain +
                                    '/followingCalendar.txt').read():
                                break
        time.sleep(1)

    assert os.path.isfile(alice_dir + '/accounts/alice@' + alice_domain +
                          '/followers.txt')
    assert os.path.isfile(bob_dir + '/accounts/bob@' + bob_domain +
                          '/following.txt')
    assert 'bob@' + bob_domain + ':' + str(bob_port) in \
        open(alice_dir + '/accounts/alice@' + alice_domain +
             '/followers.txt').read()
    assert 'alice@' + alice_domain + ':' + str(alice_port) in \
        open(bob_dir + '/accounts/bob@' + bob_domain + '/following.txt').read()

    session_bob = create_session(proxy_type)
    password = 'bobpass'
    outbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/outbox'
    inbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/inbox'
    print(str(len([name for name in os.listdir(bob_outbox_path)
                   if os.path.isfile(os.path.join(bob_outbox_path, name))])))
    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    assert len([name for name in os.listdir(bob_outbox_path)
                if os.path.isfile(os.path.join(bob_outbox_path, name))]) == 1
    print(str(len([name for name in os.listdir(alice_inbox_path)
                   if os.path.isfile(os.path.join(alice_inbox_path, name))])))
    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    assert len([name for name in os.listdir(alice_inbox_path)
                if os.path.isfile(os.path.join(alice_inbox_path, name))]) == 0

    print('\n\nEVENT: Bob checks his calendar via caldav')
    # test caldav result for a month
    result = \
        dav_month_via_server(session_bob, http_prefix,
                             'bob', bob_domain, bob_port, True,
                             test_date.year, test_date.month,
                             'bobpass')
    print('response: ' + str(result))
    assert 'VCALENDAR' in str(result)
    assert 'VEVENT' in str(result)
    # test caldav result for a day
    result = \
        dav_day_via_server(session_bob, http_prefix,
                           'bob', bob_domain, bob_port, True,
                           test_date.year, test_date.month,
                           test_date.day, 'bobpass')
    print('response: ' + str(result))
    assert 'VCALENDAR' in str(result)
    assert 'VEVENT' in str(result)
    # test for incorrect caldav login
    result = \
        dav_day_via_server(session_bob, http_prefix,
                           'bob', bob_domain, bob_port, True,
                           test_date.year, test_date.month,
                           test_date.day, 'wrongpass')
    assert 'VCALENDAR' not in str(result)
    assert 'VEVENT' not in str(result)

    print('\n\nEVENT: Bob likes the post')
    send_like_via_server(bob_dir, session_bob,
                         'bob', 'bobpass',
                         bob_domain, bob_port,
                         http_prefix, outbox_post_id,
                         cached_webfingers, person_cache,
                         True, __version__, signing_priv_key_pem)
    for _ in range(20):
        if os.path.isdir(outbox_path) and os.path.isdir(inbox_path):
            if len([name for name in os.listdir(outbox_path)
                    if os.path.isfile(os.path.join(outbox_path, name))]) == 2:
                test = len([name for name in os.listdir(inbox_path)
                            if os.path.isfile(os.path.join(inbox_path, name))])
                if test == 1:
                    break
        time.sleep(1)
    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    bob_outbox_path_ctr = \
        len([name for name in os.listdir(bob_outbox_path)
             if os.path.isfile(os.path.join(bob_outbox_path, name))])
    print('bob_outbox_path_ctr: ' + str(bob_outbox_path_ctr))
    assert bob_outbox_path_ctr == 2
    alice_inbox_path_ctr = \
        len([name for name in os.listdir(alice_inbox_path)
             if os.path.isfile(os.path.join(alice_inbox_path, name))])
    print('alice_inbox_path_ctr: ' + str(alice_inbox_path_ctr))
    assert alice_inbox_path_ctr == 0
    print('EVENT: Post liked')

    print('\n\nEVENT: Bob reacts to the post')
    send_reaction_via_server(bob_dir, session_bob,
                             'bob', 'bobpass',
                             bob_domain, bob_port,
                             http_prefix, outbox_post_id, '😃',
                             cached_webfingers, person_cache,
                             True, __version__, signing_priv_key_pem)
    for _ in range(20):
        if os.path.isdir(outbox_path) and os.path.isdir(inbox_path):
            if len([name for name in os.listdir(outbox_path)
                    if os.path.isfile(os.path.join(outbox_path, name))]) == 3:
                test = len([name for name in os.listdir(inbox_path)
                            if os.path.isfile(os.path.join(inbox_path, name))])
                if test == 1:
                    break
        time.sleep(1)
    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    bob_outbox_path_ctr = \
        len([name for name in os.listdir(bob_outbox_path)
             if os.path.isfile(os.path.join(bob_outbox_path, name))])
    print('bob_outbox_path_ctr: ' + str(bob_outbox_path_ctr))
    assert bob_outbox_path_ctr == 3
    alice_inbox_path_ctr = \
        len([name for name in os.listdir(alice_inbox_path)
             if os.path.isfile(os.path.join(alice_inbox_path, name))])
    print('alice_inbox_path_ctr: ' + str(alice_inbox_path_ctr))
    assert alice_inbox_path_ctr == 0
    print('EVENT: Post reacted to')

    print(str(len([name for name in os.listdir(outbox_path)
                   if os.path.isfile(os.path.join(outbox_path, name))])))
    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    outbox_path_ctr = \
        len([name for name in os.listdir(outbox_path)
             if os.path.isfile(os.path.join(outbox_path, name))])
    print('outbox_path_ctr: ' + str(outbox_path_ctr))
    assert outbox_path_ctr == 3
    inbox_path_ctr = \
        len([name for name in os.listdir(inbox_path)
             if os.path.isfile(os.path.join(inbox_path, name))])
    print('inbox_path_ctr: ' + str(inbox_path_ctr))
    assert inbox_path_ctr == 0
    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    print('\n\nEVENT: Bob repeats the post')
    signing_priv_key_pem = None
    send_announce_via_server(bob_dir, session_bob, 'bob', password,
                             bob_domain, bob_port,
                             http_prefix, outbox_post_id,
                             cached_webfingers,
                             person_cache, True, __version__,
                             signing_priv_key_pem)
    for _ in range(20):
        if os.path.isdir(outbox_path) and os.path.isdir(inbox_path):
            if len([name for name in os.listdir(outbox_path)
                    if os.path.isfile(os.path.join(outbox_path, name))]) == 4:
                if len([name for name in os.listdir(inbox_path)
                        if os.path.isfile(os.path.join(inbox_path,
                                                       name))]) == 2:
                    break
        time.sleep(1)

    show_test_boxes('alice', alice_inbox_path, alice_outbox_path)
    show_test_boxes('bob', bob_inbox_path, bob_outbox_path)
    bob_outbox_path_ctr = \
        len([name for name in os.listdir(bob_outbox_path)
             if os.path.isfile(os.path.join(bob_outbox_path, name))])
    print('bob_outbox_path_ctr: ' + str(bob_outbox_path_ctr))
    assert bob_outbox_path_ctr == 5
    alice_inbox_path_ctr = \
        len([name for name in os.listdir(alice_inbox_path)
             if os.path.isfile(os.path.join(alice_inbox_path, name))])
    print('alice_inbox_path_ctr: ' + str(alice_inbox_path_ctr))
    assert alice_inbox_path_ctr == 1
    print('EVENT: Post repeated')

    inbox_path = bob_dir + '/accounts/bob@' + bob_domain + '/inbox'
    outbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/outbox'
    posts_before = \
        len([name for name in os.listdir(inbox_path)
             if os.path.isfile(os.path.join(inbox_path, name))])
    print('\n\nEVENT: Alice deletes her post: ' + outbox_post_id + ' ' +
          str(posts_before))
    password = 'alicepass'
    send_delete_via_server(alice_dir, session_alice, 'alice', password,
                           alice_domain, alice_port,
                           http_prefix, outbox_post_id,
                           cached_webfingers, person_cache,
                           True, __version__, signing_priv_key_pem)
    for _ in range(30):
        if os.path.isdir(inbox_path):
            test = len([name for name in os.listdir(inbox_path)
                        if os.path.isfile(os.path.join(inbox_path, name))])
            if test == posts_before-1:
                break
        time.sleep(1)

    test = len([name for name in os.listdir(inbox_path)
                if os.path.isfile(os.path.join(inbox_path, name))])
    assert test == posts_before - 1
    print(">>> post deleted from Alice's outbox and Bob's inbox")
    assert valid_inbox(bob_dir, 'bob', bob_domain)
    assert valid_inbox_filenames(bob_dir, 'bob', bob_domain,
                                 alice_domain, alice_port)

    print('\n\nEVENT: Alice unfollows Bob')
    password = 'alicepass'
    send_unfollow_request_via_server(base_dir, session_alice,
                                     'alice', password,
                                     alice_domain, alice_port,
                                     'bob', bob_domain, bob_port,
                                     http_prefix,
                                     cached_webfingers, person_cache,
                                     True, __version__, signing_priv_key_pem)
    for _ in range(10):
        if 'alice@' + alice_domain + ':' + str(alice_port) not in \
           open(bob_followers_filename).read():
            if 'bob@' + bob_domain + ':' + str(bob_port) not in \
               open(alice_following_filename).read():
                break
        time.sleep(1)

    assert os.path.isfile(bob_followers_filename)
    assert os.path.isfile(alice_following_filename)
    assert 'alice@' + alice_domain + ':' + str(alice_port) \
        not in open(bob_followers_filename).read()
    assert 'bob@' + bob_domain + ':' + str(bob_port) \
        not in open(alice_following_filename).read()
    assert valid_inbox(bob_dir, 'bob', bob_domain)
    assert valid_inbox_filenames(bob_dir, 'bob', bob_domain,
                                 alice_domain, alice_port)
    assert valid_inbox(alice_dir, 'alice', alice_domain)
    assert valid_inbox_filenames(alice_dir, 'alice', alice_domain,
                                 bob_domain, bob_port)

    # stop the servers
    THR_ALICE.kill()
    THR_ALICE.join()
    assert THR_ALICE.is_alive() is False

    THR_BOB.kill()
    THR_BOB.join()
    assert THR_BOB.is_alive() is False

    os.chdir(base_dir)
    # shutil.rmtree(alice_dir, ignore_errors=False, onerror=None)
    # shutil.rmtree(bob_dir, ignore_errors=False, onerror=None)


def _test_actor_parsing():
    print('test_actor_parsing')
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
    print('test_web_links')

    example_text = \
        "<p>Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        " <a href=\"https://domain.ugh/tags/turbot\" class=\"mention " + \
        "hashtag\" rel=\"tag\">#<span>turbot</span></a> <a href=\"" + \
        "https://domain.ugh/tags/haddock\" class=\"mention hashtag\"" + \
        " rel=\"tag\">#<span>haddock</span></a></p>"
    result_text = remove_long_words(example_text, 40, [])
    assert result_text == "<p>Aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" + \
        " <a href=\"https://domain.ugh/tags/turbot\" class=\"mention " + \
        "hashtag\" rel=\"tag\">#<span>turbot</span></a> " + \
        "<a href=\"https://domain.ugh/tags/haddock\" " + \
        "class=\"mention hashtag\" rel=\"tag\">#<span>haddock</span></a></p>"

    example_text = \
        '<p><span class=\"h-card\"><a href=\"https://something/@orother' + \
        '\" class=\"u-url mention\">@<span>foo</span></a></span> Some ' + \
        'random text.</p><p>AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA' + \
        'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA</p>'
    result_text = remove_long_words(example_text, 40, [])
    assert result_text == \
        '<p><span class="h-card"><a href="https://something/@orother"' + \
        ' class="u-url mention">@<span>foo</span></a></span> ' + \
        'Some random text.</p>'

    example_text = \
        'This post has a web links https://somesite.net\n\nAnd some other text'
    linked_text = add_web_links(example_text)
    assert \
        '<a href="https://somesite.net" rel="nofollow noopener noreferrer"' + \
        ' target="_blank"><span class="invisible">https://' + \
        '</span><span class="ellipsis">somesite.net</span></a' in linked_text

    example_text = \
        'This post has a very long web link\n\nhttp://' + \
        'cbwebewuvfuftdiudbqd33dddbbyuef23fyug3bfhcyu2fct2' + \
        'cuyqbcbucuwvckiwyfgewfvqejbchevbhwevuevwbqebqekve' + \
        'qvuvjfkf.onion\n\nAnd some other text'
    linked_text = add_web_links(example_text)
    assert 'ellipsis' in linked_text

    example_text = \
        '<p>1. HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAH' + \
        'AHAHAHHAHAHAHAHAHAHAHAHAHAHAHAHHAHAHAHAHAHAHAHAH</p>'
    result_text = remove_long_words(example_text, 40, [])
    assert result_text == '<p>1. HAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHAHA</p>'

    example_text = \
        '<p>Tox address is 88AB9DED6F9FBEF43E105FB72060A2D89F9B93C74' + \
        '4E8C45AB3C5E42C361C837155AFCFD9D448 </p>'
    result_text = remove_long_words(example_text, 40, [])
    assert result_text == example_text

    example_text = \
        'some.incredibly.long.and.annoying.word.which.should.be.removed: ' + \
        'The remaining text'
    result_text = remove_long_words(example_text, 40, [])
    assert result_text == \
        'some.incredibly.long.and.annoying.word.w\n' + \
        'hich.should.be.removed: The remaining text'

    example_text = \
        '<p>Tox address is 88AB9DED6F9FBEF43E105FB72060A2D89F9B93C74' + \
        '4E8C45AB3C5E42C361C837155AFCFD9D448</p>'
    result_text = remove_long_words(example_text, 40, [])
    assert result_text == \
        '<p>Tox address is 88AB9DED6F9FBEF43E105FB72060A2D89F9B93C7\n' + \
        '44E8C45AB3C5E42C361C837155AFCFD9D448</p>'

    example_text = \
        '<p>ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCA' + \
        'BCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB' + \
        'CABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC' + \
        'ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCA' + \
        'BCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB' + \
        'CABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABC' + \
        'ABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCA' + \
        'BCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCABCAB' + \
        'CABCABCABCABCABCABCABCABC</p>'
    result_text = remove_long_words(example_text, 40, [])
    assert result_text == r'<p>ABCABCABCABCABCABCABCABCABCABCABCABCABCA<\p>'

    example_text = \
        '"the nucleus of mutual-support institutions, habits, and customs ' + \
        'remains alive with the millions; it keeps them together; and ' + \
        'they prefer to cling to their customs, beliefs, and traditions ' + \
        'rather than to accept the teachings of a war of each ' + \
        'against all"\n\n--Peter Kropotkin'
    test_fn_str = add_web_links(example_text)
    result_text = remove_long_words(test_fn_str, 40, [])
    assert result_text == example_text
    assert 'ellipsis' not in result_text

    example_text = \
        '<p>ｆｉｌｅｐｏｐｏｕｔ＝' + \
        'ＴｅｍｐｌａｔｅＡｔｔａｃｈｍｅｎｔＲｉｃｈＰｏｐｏｕｔ<<\\p>'
    result_text = replace_content_duplicates(example_text)
    assert result_text == \
        '<p>ｆｉｌｅｐｏｐｏｕｔ＝' + \
        'ＴｅｍｐｌａｔｅＡｔｔａｃｈｍｅｎｔＲｉｃｈＰｏｐｏｕｔ'

    example_text = \
        '<p>Test1 test2 #YetAnotherExcessivelyLongwindedAndBoringHashtag</p>'
    test_fn_str = add_web_links(example_text)
    result_text = remove_long_words(test_fn_str, 40, [])
    assert(result_text ==
           '<p>Test1 test2 '
           '#YetAnotherExcessivelyLongwindedAndBorin\ngHashtag</p>')

    example_text = \
        "<p>Don't remove a p2p link " + \
        "rad:git:hwd1yrerc3mcgn8ga9rho3dqi4w33nep7kxmqezss4topyfgmexihp" + \
        "33xcw</p>"
    test_fn_str = add_web_links(example_text)
    result_text = remove_long_words(test_fn_str, 40, [])
    assert result_text == example_text


def _test_addemoji(base_dir: str):
    print('test_addemoji')
    content = "Emoji :lemon: :strawberry: :banana:"
    http_prefix = 'http'
    nickname = 'testuser'
    domain = 'testdomain.net'
    port = 3682
    recipients = []
    hashtags = {}
    base_dir_original = base_dir
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
    copytree(base_dir_original + '/emoji', base_dir + '/emoji')
    os.chdir(base_dir)
    private_key_pem, public_key_pem, person, wf_endpoint = \
        create_person(base_dir, nickname, domain, port,
                      http_prefix, True, False, 'password')
    assert private_key_pem
    assert public_key_pem
    assert person
    assert wf_endpoint
    content_modified = \
        add_html_tags(base_dir, http_prefix,
                      nickname, domain, content,
                      recipients, hashtags, True)
    assert ':lemon:' in content_modified
    assert content_modified.startswith('<p>')
    assert content_modified.endswith('</p>')
    tags = []
    for _, tag in hashtags.items():
        tags.append(tag)
    content = content_modified
    content_modified = \
        replace_emoji_from_tags(None, base_dir, content, tags, 'content', True)
    # print('content_modified: ' + content_modified)
    assert content_modified == '<p>Emoji 🍋 🍓 🍌</p>'

    os.chdir(base_dir_original)
    shutil.rmtree(base_dir_original + '/.tests',
                  ignore_errors=False, onerror=None)


def _test_get_status_number():
    print('test_get_status_number')
    prev_status_number = None
    for _ in range(1, 20):
        status_number, _ = get_status_number()
        if prev_status_number:
            assert len(status_number) == 18
            assert int(status_number) > prev_status_number
        prev_status_number = int(status_number)


def _test_json_string() -> None:
    print('test_json_string')
    filename = '.epicyon_tests_test_json_string.json'
    message_str = "Crème brûlée यह एक परीक्षण ह"
    test_json = {
        "content": message_str
    }
    assert save_json(test_json, filename)
    received_json = load_json(filename, 0)
    assert received_json
    assert received_json['content'] == message_str
    encoded_str = json.dumps(test_json, ensure_ascii=False)
    assert message_str in encoded_str
    try:
        os.remove(filename)
    except OSError:
        pass


def _test_save_load_json():
    print('test_save_load_json')
    test_json = {
        "param1": 3,
        "param2": '"Crème brûlée यह एक परीक्षण ह"'
    }
    test_filename = '.epicyon_tests_test_save_load_json.json'
    if os.path.isfile(test_filename):
        try:
            os.remove(test_filename)
        except OSError:
            pass
    assert save_json(test_json, test_filename)
    assert os.path.isfile(test_filename)
    test_load_json = load_json(test_filename)
    assert test_load_json
    assert test_load_json.get('param1')
    assert test_load_json.get('param2')
    assert test_load_json['param1'] == 3
    assert test_load_json['param2'] == '"Crème brûlée यह एक परीक्षण ह"'
    try:
        os.remove(test_filename)
    except OSError:
        pass


def _test_theme():
    print('test_theme')
    css = 'somestring --background-value: 24px; --foreground-value: 24px;'
    result = set_css_param(css, 'background-value', '32px')
    assert result == \
        'somestring --background-value: 32px; --foreground-value: 24px;'
    css = \
        'somestring --background-value: 24px; --foreground-value: 24px; ' + \
        '--background-value: 24px;'
    result = set_css_param(css, 'background-value', '32px')
    assert result == \
        'somestring --background-value: 32px; --foreground-value: 24px; ' + \
        '--background-value: 32px;'
    css = '--background-value: 24px; --foreground-value: 24px;'
    result = set_css_param(css, 'background-value', '32px')
    assert result == '--background-value: 32px; --foreground-value: 24px;'


def _test_recent_posts_cache():
    print('test_recent_posts_cache')
    recent_posts_cache = {}
    max_recent_posts = 3
    html_str = '<html></html>'
    for i in range(5):
        post_json_object = {
            "id": "https://somesite.whatever/users/someuser/statuses/" + str(i)
        }
        update_recent_posts_cache(recent_posts_cache, max_recent_posts,
                                  post_json_object, html_str)
    assert len(recent_posts_cache['index']) == max_recent_posts
    assert len(recent_posts_cache['json'].items()) == max_recent_posts
    assert len(recent_posts_cache['html'].items()) == max_recent_posts


def _test_remove_txt_formatting():
    print('test_remove_txt_formatting')
    test_str = '<p>Text without formatting</p>'
    result_str = remove_text_formatting(test_str, False)
    assert result_str == test_str
    test_str = '<p>Text <i>with</i> <h3>formatting</h3></p>'
    result_str = remove_text_formatting(test_str, False)
    assert result_str == '<p>Text with formatting</p>'


def _test_jsonld():
    print("test_jsonld")

    jld_document = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "actor": "https://somesite.net/users/gerbil",
        "description": "My json document",
        "numberField": 83582,
        "object": {
            "content": "valid content"
        }
    }
    # private_key_pem, public_key_pem = generate_rsa_key()
    private_key_pem = '-----BEGIN RSA PRIVATE KEY-----\n' \
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
    public_key_pem = '-----BEGIN PUBLIC KEY-----\n' \
        'MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAod9iHfIn4ugY/2byFrFj\n' \
        'UprrFLkkH5bCrjiBq2/MdHFg99IQ7li2x2mg5fkBMhU5SJIxlN8kiZMFq7JUXSA9\n' \
        '7Yo4puhVubqTSHihIh6Xn2mTjTgszNo9SBbmN3YiyBPTcr0rF4jGWZAduJ8u6i7E\n' \
        'ky2QH+UBKyUNRZrcfoVq+7grHUIA45pE7vAfEEWtgRiw32Nwlx55N3hayHax0y8g\n' \
        'MdKEF/vfYKRLcM7rZgEASMtlCpgyfsyHwFCDzl/BP8AhP9u3dM+SEundeAvF58Ai\n' \
        'Xx1pKvBpxqttDNAsKWCRQ06/WI/W2Rwihl9yCjobqRoFsZ/cTEi6FG9AbDAds5Yj\n' \
        'TwIDAQAB\n' \
        '-----END PUBLIC KEY-----'

    signed_document = jld_document.copy()
    generate_json_signature(signed_document, private_key_pem)
    assert signed_document
    assert signed_document.get('signature')
    assert signed_document['signature'].get('signatureValue')
    assert signed_document['signature'].get('type')
    assert len(signed_document['signature']['signatureValue']) > 50
    # print str(signed_document['signature'])
    assert signed_document['signature']['type'] == 'RsaSignature2017'
    assert verify_json_signature(signed_document, public_key_pem)

    # alter the signed document
    signed_document['object']['content'] = 'forged content'
    assert not verify_json_signature(signed_document, public_key_pem)

    jld_document2 = {
        "@context": "https://www.w3.org/ns/activitystreams",
        "actor": "https://somesite.net/users/gerbil",
        "description": "Another json document",
        "numberField": 13353,
        "object": {
            "content": "More content"
        }
    }
    signed_document2 = jld_document2.copy()
    generate_json_signature(signed_document2, private_key_pem)
    assert signed_document2
    assert signed_document2.get('signature')
    assert signed_document2['signature'].get('signatureValue')
    # changed signature on different document
    if signed_document['signature']['signatureValue'] == \
       signed_document2['signature']['signatureValue']:
        print('json signature has not changed for different documents')
    assert '.' not in str(signed_document['signature']['signatureValue'])
    assert len(str(signed_document['signature']['signatureValue'])) > 340
    assert (signed_document['signature']['signatureValue'] !=
            signed_document2['signature']['signatureValue'])


def _test_site_active():
    print('test_site_is_active')
    timeout = 10
    # at least one site should resolve
    if not site_is_active('https://archive.org', timeout):
        if not site_is_active('https://wikipedia.org', timeout):
            assert site_is_active('https://mastodon.social', timeout)
    assert not site_is_active('https://notarealwebsite.a.b.c', timeout)


def _test_strip_html():
    print('test_remove_html')
    test_str = 'This string has no html.'
    assert remove_html(test_str) == test_str
    test_str = 'This string <a href="1234.567">has html</a>.'
    assert remove_html(test_str) == 'This string has html.'
    test_str = '<label>This string has.</label><label>Two labels.</label>'
    assert remove_html(test_str) == 'This string has. Two labels.'
    test_str = '<p>This string has.</p><p>Two paragraphs.</p>'
    assert remove_html(test_str) == 'This string has.\n\nTwo paragraphs.'
    test_str = 'This string has.<br>A new line.'
    assert remove_html(test_str) == 'This string has.\nA new line.'
    test_str = '<p>This string contains a url http://somesite.or.other</p>'
    assert remove_html(test_str) == \
        'This string contains a url http://somesite.or.other'


def _test_danger_css(base_dir: str) -> None:
    print('test_dangerous_css')
    for _, _, files in os.walk(base_dir):
        for fname in files:
            if not fname.endswith('.css'):
                continue
            assert not dangerous_css(base_dir + '/' + fname, False)
        break


def _test_danger_svg(base_dir: str) -> None:
    print('test_dangerous_svg')
    svg_content = \
        '  <svg viewBox="0 0 10 10" xmlns="http://www.w3.org/2000/svg">' + \
        '  <circle cx="5" cy="5" r="4" />' + \
        '</svg>'
    assert not dangerous_svg(svg_content, False)
    svg_content = \
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
    assert dangerous_svg(svg_content, False)

    assert not scan_themes_for_scripts(base_dir)


def _test_danger_markup():
    print('test_dangerous_markup')
    allow_local_network_access = False
    content = '<p>This is a valid message</p>'
    assert not dangerous_markup(content, allow_local_network_access)

    content = 'This is a valid message without markup'
    assert not dangerous_markup(content, allow_local_network_access)

    content = '<p>This is a valid-looking message. But wait... ' + \
        '<script>document.getElementById("concentrated")' + \
        '.innerHTML = "evil";</script></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This is a valid-looking message. But wait... ' + \
        '&lt;script&gt;document.getElementById("concentrated")' + \
        '.innerHTML = "evil";&lt;/script&gt;</p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This html contains more than you expected... ' + \
        '<script language="javascript">document.getElementById("abc")' + \
        '.innerHTML = "def";</script></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This is a valid-looking message. But wait... ' + \
        '<script src="https://evilsite/payload.js" /></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This is a valid-looking message. But it contains ' + \
        'spyware. <amp-analytics type="gtag" ' + \
        'data-credentials="include"></amp-analytics></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This is a valid-looking message. But it contains ' + \
        '<a href="something.googleapis.com/anotherthing">spyware.</a></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This message embeds an evil frame.' + \
        '<iframe src="somesite"></iframe></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This message tries to obfuscate an evil frame.' + \
        '<  iframe     src = "somesite"></    iframe  ></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This message is not necessarily evil, but annoying.' + \
        '<hr><br><br><br><br><br><br><br><hr><hr></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This message contans a ' + \
        '<a href="https://validsite/index.html">valid link.</a></p>'
    assert not dangerous_markup(content, allow_local_network_access)

    content = '<p>This message contans a ' + \
        '<a href="https://validsite/iframe.html">' + \
        'valid link having invalid but harmless name.</a></p>'
    assert not dangerous_markup(content, allow_local_network_access)

    content = '<p>This message which <a href="127.0.0.1:8736">' + \
        'tries to access the local network</a></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>This message which <a href="http://192.168.5.10:7235">' + \
        'tries to access the local network</a></p>'
    assert dangerous_markup(content, allow_local_network_access)

    content = '<p>127.0.0.1 This message which does not access ' + \
        'the local network</a></p>'
    assert not dangerous_markup(content, allow_local_network_access)


def _run_html_replace_quote_marks():
    print('html_replace_quote_marks')
    test_str = 'The "cat" "sat" on the mat'
    result = html_replace_quote_marks(test_str)
    assert result == 'The “cat” “sat” on the mat'

    test_str = 'The cat sat on the mat'
    result = html_replace_quote_marks(test_str)
    assert result == 'The cat sat on the mat'

    test_str = '"hello"'
    result = html_replace_quote_marks(test_str)
    assert result == '“hello”'

    test_str = '"hello" <a href="somesite.html">&quot;test&quot; html</a>'
    result = html_replace_quote_marks(test_str)
    assert result == '“hello” <a href="somesite.html">“test” html</a>'


def _test_json_post_allows_comment():
    print('test_json_post_allows_comments')
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
    print('test_remove_id_ending')
    test_str = 'https://activitypub.somedomain.net'
    result_str = remove_id_ending(test_str)
    assert result_str == 'https://activitypub.somedomain.net'

    test_str = \
        'https://activitypub.somedomain.net/users/foo/' + \
        'statuses/34544814814/activity'
    result_str = remove_id_ending(test_str)
    assert result_str == \
        'https://activitypub.somedomain.net/users/foo/statuses/34544814814'

    test_str = \
        'https://undo.somedomain.net/users/foo/statuses/34544814814/undo'
    result_str = remove_id_ending(test_str)
    assert result_str == \
        'https://undo.somedomain.net/users/foo/statuses/34544814814'

    test_str = \
        'https://event.somedomain.net/users/foo/statuses/34544814814/event'
    result_str = remove_id_ending(test_str)
    assert result_str == \
        'https://event.somedomain.net/users/foo/statuses/34544814814'


def _test_valid_content_warning():
    print('test_valid_content_warning')
    result_str = valid_content_warning('Valid content warning')
    assert result_str == 'Valid content warning'

    result_str = valid_content_warning('Invalid #content warning')
    assert result_str == 'Invalid content warning'

    result_str = \
        valid_content_warning('Invalid <a href="somesite">content warning</a>')
    assert result_str == 'Invalid content warning'


def _test_translations(base_dir: str) -> None:
    print('test_translations')
    languages_str = get_supported_languages(base_dir)
    assert languages_str

    # load all translations into a dict
    lang_dict = {}
    for lang in languages_str:
        lang_json = load_json('translations/' + lang + '.json')
        if not lang_json:
            print('Missing language file ' +
                  'translations/' + lang + '.json')
        assert lang_json
        lang_dict[lang] = lang_json

    # load english translations
    translations_json = load_json('translations/en.json')
    # test each english string exists in the other language files
    for english_str, _ in translations_json.items():
        for lang in languages_str:
            lang_json = lang_dict[lang]
            if not lang_json.get(english_str):
                print(english_str + ' is missing from ' + lang + '.json')
            assert lang_json.get(english_str)


def _test_constant_time_string():
    print('test_constant_time_string_check')
    assert constant_time_string_check('testing', 'testing')
    assert not constant_time_string_check('testing', '1234')
    assert not constant_time_string_check('testing', '1234567')

    itterations = 256

    start = time.time()
    test_str = 'nnjfbefefbsnjsdnvbcueftqfeuqfbqefnjeniwufgy'
    for _ in range(itterations):
        constant_time_string_check(test_str, test_str)
    end = time.time()
    av_time1 = ((end - start) * 1000000 / itterations)

    # change a single character and observe timing difference
    start = time.time()
    for _ in range(itterations):
        constant_time_string_check(test_str, test_str)
    end = time.time()
    av_time2 = ((end - start) * 1000000 / itterations)
    time_diff_microseconds = abs(av_time2 - av_time1)
    # time difference should be less than 10uS
    assert int(time_diff_microseconds) < 10

    # change multiple characters and observe timing difference
    start = time.time()
    test_str2 = 'ano1befffbsn7sd3vbluef6qseuqfpqeznjgni9bfgi'
    for _ in range(itterations):
        constant_time_string_check(test_str, test_str2)
    end = time.time()
    av_time2 = ((end - start) * 1000000 / itterations)
    time_diff_microseconds = abs(av_time2 - av_time1)
    # time difference should be less than 10uS
    assert int(time_diff_microseconds) < 10


def _test_replace_email_quote():
    print('test_replace_email_quote')
    test_str = '<p>This content has no quote.</p>'
    assert html_replace_email_quote(test_str) == test_str

    test_str = '<p>This content has no quote.</p>' + \
        '<p>With multiple</p><p>lines</p>'
    assert html_replace_email_quote(test_str) == test_str

    test_str = '<p>&quot;This is a quoted paragraph.&quot;</p>'
    assert html_replace_email_quote(test_str) == \
        '<p><blockquote>This is a quoted paragraph.</blockquote></p>'

    test_str = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somewebsite/@nickname\" " + \
        "class=\"u-url mention\">@<span>nickname</span></a></span> " + \
        "<br />&gt; This is a quote</p><p>Some other text.</p>"
    expected_str = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somewebsite/@nickname\" " + \
        "class=\"u-url mention\">@<span>nickname</span></a></span> " + \
        "<br /><blockquote>This is a quote</blockquote></p>" + \
        "<p>Some other text.</p>"
    result_str = html_replace_email_quote(test_str)
    if result_str != expected_str:
        print('Result: ' + str(result_str))
        print('Expect: ' + expected_str)
    assert result_str == expected_str

    test_str = "<p>Some text:</p><p>&gt; first line-&gt;second line</p>" + \
        "<p>Some question?</p>"
    expected_str = "<p>Some text:</p><p><blockquote>first line-<br>" + \
        "second line</blockquote></p><p>Some question?</p>"
    result_str = html_replace_email_quote(test_str)
    if result_str != expected_str:
        print('Result: ' + str(result_str))
        print('Expect: ' + expected_str)
    assert result_str == expected_str

    test_str = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somedomain/@somenick\" " + \
        "class=\"u-url mention\">@<span>somenick</span>" + \
        "</a></span> </p><p>&gt; Text1.<br />&gt; <br />" + \
        "&gt; Text2<br />&gt; <br />&gt; Text3<br />" + \
        "&gt;<br />&gt; Text4<br />&gt; <br />&gt; " + \
        "Text5<br />&gt; <br />&gt; Text6</p><p>Text7</p>"
    expected_str = "<p><span class=\"h-card\">" + \
        "<a href=\"https://somedomain/@somenick\" " + \
        "class=\"u-url mention\">@<span>somenick</span></a>" + \
        "</span> </p><p><blockquote> Text1.<br /><br />" + \
        "Text2<br /><br />Text3<br />&gt;<br />Text4<br />" + \
        "<br />Text5<br /><br />Text6</blockquote></p><p>Text7</p>"
    result_str = html_replace_email_quote(test_str)
    if result_str != expected_str:
        print('Result: ' + str(result_str))
        print('Expect: ' + expected_str)
    assert result_str == expected_str


def _test_strip_html_tag():
    print('test_remove_html_tag')
    test_str = "<p><img width=\"864\" height=\"486\" " + \
        "src=\"https://somesiteorother.com/image.jpg\"></p>"
    result_str = remove_html_tag(test_str, 'width')
    assert result_str == "<p><img height=\"486\" " + \
        "src=\"https://somesiteorother.com/image.jpg\"></p>"


def _test_hashtag_rules():
    print('test_hashtag_rule_tree')
    operators = ('not', 'and', 'or', 'xor', 'from', 'contains')

    url = 'testsite.com'
    moderated = True
    conditions_str = \
        'contains "Cat" or contains "Corvid" or ' + \
        'contains "Dormouse" or contains "Buzzard"'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == str(['or', ['contains', ['"Cat"']],
                             ['contains', ['"Corvid"']],
                             ['contains', ['"Dormouse"']],
                             ['contains', ['"Buzzard"']]])

    content = 'This is a test'
    moderated = True
    conditions_str = '#foo or #bar'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == str(['or', ['#foo'], ['#bar']])
    assert str(tags_in_conditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    content = 'This is a test'
    url = 'https://testsite.com/something'
    moderated = True
    conditions_str = '#foo and from "testsite.com"'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == str(['and', ['#foo'], ['from', ['"testsite.com"']]])
    assert str(tags_in_conditions) == str(['#foo'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content,
                                    'othersite.net')

    content = 'This is a test'
    moderated = True
    conditions_str = 'contains "is a" and #foo or #bar'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == \
        str(['and', ['contains', ['"is a"']],
             ['or', ['#foo'], ['#bar']]])
    assert str(tags_in_conditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    moderated = False
    conditions_str = 'not moderated and #foo or #bar'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == \
        str(['not', ['and', ['moderated'], ['or', ['#foo'], ['#bar']]]])
    assert str(tags_in_conditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    moderated = True
    conditions_str = 'moderated and #foo or #bar'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == \
        str(['and', ['moderated'], ['or', ['#foo'], ['#bar']]])
    assert str(tags_in_conditions) == str(['#foo', '#bar'])
    hashtags = ['#foo']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#carrot', '#stick']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditions_str = 'x'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert tree is None
    assert tags_in_conditions == []
    hashtags = ['#foo']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditions_str = '#x'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == str(['#x'])
    assert str(tags_in_conditions) == str(['#x'])
    hashtags = ['#x']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#y', '#z']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditions_str = 'not #b'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == str(['not', ['#b']])
    assert str(tags_in_conditions) == str(['#b'])
    hashtags = ['#y', '#z']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#a', '#b', '#c']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)

    conditions_str = '#foo or #bar and #a'
    tags_in_conditions = []
    tree = hashtag_rule_tree(operators, conditions_str,
                             tags_in_conditions, moderated)
    assert str(tree) == str(['and', ['or', ['#foo'], ['#bar']], ['#a']])
    assert str(tags_in_conditions) == str(['#foo', '#bar', '#a'])
    hashtags = ['#foo', '#bar', '#a']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#bar', '#a']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#foo', '#a']
    assert hashtag_rule_resolve(tree, hashtags, moderated, content, url)
    hashtags = ['#x', '#a']
    assert not hashtag_rule_resolve(tree, hashtags, moderated, content, url)


def _test_newswire_tags():
    print('test_newswire_tags')
    rss_description = '<img src="https://somesite/someimage.jpg" ' + \
        'class="misc-stuff" alt="#ExcitingHashtag" ' + \
        'srcset="https://somesite/someimage.jpg" ' + \
        'sizes="(max-width: 864px) 100vw, 864px" />' + \
        'Compelling description with #ExcitingHashtag, which is ' + \
        'being posted in #BoringForum'
    tags = get_newswire_tags(rss_description, 10)
    assert len(tags) == 2
    assert '#BoringForum' in tags
    assert '#ExcitingHashtag' in tags


def _test_first_paragraph_from_string():
    print('test_first_paragraph_from_string')
    test_str = \
        '<p><a href="https://somesite.com/somepath">This is a test</a></p>' + \
        '<p>This is another paragraph</p>'
    result_str = first_paragraph_from_string(test_str)
    if result_str != 'This is a test':
        print(result_str)
    assert result_str == 'This is a test'

    test_str = 'Testing without html'
    result_str = first_paragraph_from_string(test_str)
    assert result_str == test_str


def _test_parse_newswire_feed_date():
    print('test_parse_feed_date')

    unique_string_identifier = 'some string abcd'

    pub_date = "2020-12-14T00:08:06+00:00"
    published_date = parse_feed_date(pub_date, unique_string_identifier)
    assert published_date == "2020-12-14 00:08:06+00:00"

    pub_date = "Tue, 08 Dec 2020 06:24:38 -0600"
    published_date = parse_feed_date(pub_date, unique_string_identifier)
    assert published_date == "2020-12-08 12:24:38+00:00"

    pub_date = "2020-08-27T16:12:34+00:00"
    published_date = parse_feed_date(pub_date, unique_string_identifier)
    assert published_date == "2020-08-27 16:12:34+00:00"

    pub_date = "Sun, 22 Nov 2020 19:51:33 +0100"
    published_date = parse_feed_date(pub_date, unique_string_identifier)
    assert published_date == "2020-11-22 18:51:33+00:00"

    pub_date = "Sun, 22 Nov 2020 00:00:00 +0000"
    published_date = parse_feed_date(pub_date, unique_string_identifier)
    assert published_date != "2020-11-22 00:00:00+00:00"
    assert "2020-11-22 00:" in published_date


def _test_valid_nick():
    print('test_valid_nickname')
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
    print('test_guess_hashtag_category')
    hashtag_categories = {
        "foo": ["swan", "goose"],
        "bar": ["cats", "mouse"]
    }
    guess = guess_hashtag_category("unspecifiedgoose", hashtag_categories)
    assert guess == "foo"

    guess = guess_hashtag_category("mastocats", hashtag_categories)
    assert guess == "bar"


def _test_mentioned_people(base_dir: str) -> None:
    print('test_get_mentioned_people')
    content = "@dragon@cave.site @bat@cave.site This is a test."
    actors = \
        get_mentioned_people(base_dir, 'https', content, 'mydomain', False)
    assert actors
    assert len(actors) == 2
    assert actors[0] == "https://cave.site/users/dragon"
    assert actors[1] == "https://cave.site/users/bat"


def _test_reply_to_public_post(base_dir: str) -> None:
    system_language = 'en'
    languages_understood = [system_language]
    nickname = 'test7492362'
    domain = 'other.site'
    port = 443
    http_prefix = 'https'
    post_id = \
        http_prefix + '://rat.site/users/ninjarodent/statuses/63746173435'
    content = "@ninjarodent@rat.site This is a test."
    followers_only = False
    save_to_file = False
    client_to_server = False
    comments_enabled = True
    attach_image_filename = None
    media_type = None
    image_description = 'Some description'
    city = 'London, England'
    test_in_reply_to = post_id
    test_in_reply_to_atom_uri = None
    test_subject = None
    test_schedule_post = False
    test_event_date = None
    test_event_time = None
    test_location = None
    test_is_article = False
    conversation_id = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'
    reply = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content, followers_only, save_to_file,
                           client_to_server, comments_enabled,
                           attach_image_filename, media_type,
                           image_description, city, test_in_reply_to,
                           test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
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


def _get_function_call_args(name: str, lines: [], start_line_ctr: int) -> []:
    """Returns the arguments of a function call given lines
    of source code and a starting line number
    """
    args_str = lines[start_line_ctr].split(name + '(')[1]
    if ')' in args_str:
        args_str = args_str.split(')')[0].replace(' ', '').split(',')
        return args_str
    for line_ctr in range(start_line_ctr + 1, len(lines)):
        if ')' not in lines[line_ctr]:
            args_str += lines[line_ctr]
            continue
        args_str += lines[line_ctr].split(')')[0]
        break
    return args_str.replace('\n', '').replace(' ', '').split(',')


def get_function_calls(name: str, lines: [], start_line_ctr: int,
                       function_properties: {}) -> []:
    """Returns the functions called by the given one,
    Starting with the given source code at the given line
    """
    calls_functions = []
    function_content_str = ''
    for line_ctr in range(start_line_ctr + 1, len(lines)):
        line_str = lines[line_ctr].strip()
        if line_str.startswith('def '):
            break
        if line_str.startswith('class '):
            break
        function_content_str += lines[line_ctr]
    for func_name, _ in function_properties.items():
        if func_name + '(' in function_content_str:
            calls_functions.append(func_name)
    return calls_functions


def _function_args_match(call_args: [], func_args: []):
    """Do the function artuments match the function call arguments
    """
    if len(call_args) == len(func_args):
        return True

    # count non-optional arguments
    call_args_ctr = 0
    for arg1 in call_args:
        if arg1 == 'self':
            continue
        if '=' not in arg1 or arg1.startswith("'"):
            call_args_ctr += 1

    func_args_ctr = 0
    for arg2 in func_args:
        if arg2 == 'self':
            continue
        if '=' not in arg2 or arg2.startswith("'"):
            func_args_ctr += 1

    return call_args_ctr >= func_args_ctr


def _module_in_groups(mod_name: str, include_groups: [],
                      mod_groups: {}) -> bool:
    """Is the given module within the included groups list?
    """
    for group_name in include_groups:
        if mod_name in mod_groups[group_name]:
            return True
    return False


def _diagram_groups(include_groups: [],
                    exclude_extra_modules: [],
                    modules: {}, mod_groups: {},
                    max_module_calls: int) -> None:
    """Draws a dot diagram containing only the given module groups
    """
    call_graph_str = 'digraph EpicyonGroups {\n\n'
    call_graph_str += \
        '  graph [fontsize=10 fontname="Verdana" compound=true];\n'
    call_graph_str += '  node [fontsize=10 fontname="Verdana"];\n\n'
    exclude_modules_from_diagram = [
        'setup', 'tests', '__init__', 'pyjsonld'
    ]
    exclude_modules_from_diagram += exclude_extra_modules
    # colors of modules nodes
    for mod_name, mod_properties in modules.items():
        if mod_name in exclude_modules_from_diagram:
            continue
        if not _module_in_groups(mod_name, include_groups, mod_groups):
            continue
        if not mod_properties.get('calls'):
            call_graph_str += '  "' + mod_name + \
                '" [fillcolor=yellow style=filled];\n'
            continue
        if len(mod_properties['calls']) <= int(max_module_calls / 8):
            call_graph_str += '  "' + mod_name + \
                '" [fillcolor=green style=filled];\n'
        elif len(mod_properties['calls']) < int(max_module_calls / 4):
            call_graph_str += '  "' + mod_name + \
                '" [fillcolor=orange style=filled];\n'
        else:
            call_graph_str += '  "' + mod_name + \
                '" [fillcolor=red style=filled];\n'
    call_graph_str += '\n'
    # connections between modules
    for mod_name, mod_properties in modules.items():
        if mod_name in exclude_modules_from_diagram:
            continue
        if not _module_in_groups(mod_name, include_groups, mod_groups):
            continue
        if not mod_properties.get('calls'):
            continue
        for mod_call in mod_properties['calls']:
            if mod_call in exclude_modules_from_diagram:
                continue
            if not _module_in_groups(mod_call, include_groups, mod_groups):
                continue
            call_graph_str += '  "' + mod_name + '" -> "' + mod_call + '";\n'
    # module groups/clusters
    cluster_ctr = 1
    for group_name, group_modules in mod_groups.items():
        if group_name not in include_groups:
            continue
        call_graph_str += '\n'
        call_graph_str += \
            '  subgraph cluster_' + str(cluster_ctr) + ' {\n'
        call_graph_str += '    node [style=filled];\n'
        for mod_name in group_modules:
            if mod_name not in exclude_modules_from_diagram:
                call_graph_str += '    ' + mod_name + ';\n'
        call_graph_str += '    label = "' + group_name + '";\n'
        call_graph_str += '    color = blue;\n'
        call_graph_str += '  }\n'
        cluster_ctr += 1
    call_graph_str += '\n}\n'
    filename = 'epicyon_groups'
    for group_name in include_groups:
        filename += '_' + group_name.replace(' ', '-')
    filename += '.dot'
    with open(filename, 'w+') as fp_graph:
        fp_graph.write(call_graph_str)
        print('Graph saved to ' + filename)
        print('Plot using: ' +
              'sfdp -x -Goverlap=false -Goverlap_scaling=2 ' +
              '-Gsep=+100 -Tx11 epicyon_modules.dot')


def _test_post_variable_names():
    print('test_post_variable_names')

    for _, _, files in os.walk('.'):
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
    print('test_config_param_names')

    fnames = ('get_config_param', 'set_config_param')
    for _, _, files in os.walk('.'):
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
    print('test_source_contains_no_tabs')

    for _, _, files in os.walk('.'):
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
    print('test_checkbox_names')

    fnames = ['edit_text_field', 'edit_check_box', 'edit_text_area']
    for _, _, files in os.walk('.'):
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


def _test_post_field_names(source_file: str, fieldnames: []):
    print('test_post_field_Names')

    fnames = []
    for field in fieldnames:
        fnames.append(field + '.get')

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
            if '"' not in param_var_name and \
               "'" not in param_var_name:
                continue

            quote_str = '"'
            if "'" in param_var_name:
                quote_str = "'"

            orig_param_var_name = fname + '(' + param_var_name + ')'
            param_var_name = param_var_name.split(quote_str)[1]
            if ' ' in param_var_name:
                continue
            if '/' in param_var_name:
                continue
            if '_' in param_var_name:
                print(orig_param_var_name + ' in ' + source_file +
                      ' should be camel case')
                assert False

    fnames = []
    for field in fieldnames:
        fnames.append(field + '[')
    for fname in fnames:
        if fname in source_str:
            names_list = source_str.split(fname)
            for index in range(1, len(names_list)):
                if ']' not in names_list[index]:
                    continue
                param_var_name = names_list[index].split(']')[0].strip()
                if '"' not in param_var_name and \
                   "'" not in param_var_name:
                    continue

                quote_str = '"'
                if "'" in param_var_name:
                    quote_str = "'"

                orig_param_var_name = fname.strip() + param_var_name + ']'
                param_var_name = param_var_name.split(quote_str)[1]
                if ' ' in param_var_name:
                    continue
                if '/' in param_var_name:
                    continue
                if '_' in param_var_name:
                    print(orig_param_var_name + ' in ' + source_file +
                          ' should be camel case')
                    assert False


def _test_functions():
    print('test_functions')
    function = {}
    function_properties = {}
    modules = {}
    mod_groups = {}
    method_loc = []

    for _, _, files in os.walk('.'):
        for source_file in files:
            if not source_file.endswith('.py'):
                continue
            if source_file.startswith('.#'):
                continue
            if source_file.startswith('flycheck_'):
                continue
            mod_name = source_file.replace('.py', '')
            modules[mod_name] = {
                'functions': []
            }
            source_str = ''
            with open(source_file, 'r') as fp_src:
                source_str = fp_src.read()
                modules[mod_name]['source'] = source_str
            with open(source_file, 'r') as fp_src:
                lines = fp_src.readlines()
                modules[mod_name]['lines'] = lines
                line_count = 0
                prev_line = 'start'
                method_name = ''
                for line in lines:
                    if '__module_group__' in line:
                        if '=' in line:
                            group_name = line.split('=')[1].strip()
                            group_name = group_name.replace('"', '')
                            group_name = group_name.replace("'", '')
                            modules[mod_name]['group'] = group_name
                            if not mod_groups.get(group_name):
                                mod_groups[group_name] = [mod_name]
                            else:
                                if mod_name not in mod_groups[group_name]:
                                    mod_groups[group_name].append(mod_name)
                    if not line.strip().startswith('def '):
                        if line_count > 0:
                            line_count += 1
                        # add LOC count for this function
                        if len(prev_line.strip()) == 0 and \
                           len(line.strip()) == 0 and \
                           line_count > 2:
                            line_count -= 2
                            if line_count > 80:
                                loc_str = str(line_count) + ';' + method_name
                                if line_count < 1000:
                                    loc_str = '0' + loc_str
                                if line_count < 100:
                                    loc_str = '0' + loc_str
                                if line_count < 10:
                                    loc_str = '0' + loc_str
                                if loc_str not in method_loc:
                                    method_loc.append(loc_str)
                                    line_count = 0
                        prev_line = line
                        continue
                    prev_line = line
                    line_count = 1
                    method_name = line.split('def ', 1)[1].split('(')[0]
                    method_args = \
                        source_str.split('def ' + method_name + '(')[1]
                    method_args = method_args.split(')')[0]
                    method_args = method_args.replace(' ', '').split(',')
                    if function.get(mod_name):
                        function[mod_name].append(method_name)
                    else:
                        function[mod_name] = [method_name]
                    if method_name not in modules[mod_name]['functions']:
                        modules[mod_name]['functions'].append(method_name)
                    function_properties[method_name] = {
                        "args": method_args,
                        "module": mod_name,
                        "calledInModule": []
                    }
                # LOC count for the last function
                if line_count > 2:
                    line_count -= 2
                    if line_count > 80:
                        loc_str = str(line_count) + ';' + method_name
                        if line_count < 1000:
                            loc_str = '0' + loc_str
                        if line_count < 100:
                            loc_str = '0' + loc_str
                        if line_count < 10:
                            loc_str = '0' + loc_str
                        if loc_str not in method_loc:
                            method_loc.append(loc_str)
        break

    print('LOC counts:')
    method_loc.sort()
    for loc_str in method_loc:
        print(loc_str.split(';')[0] + ' ' + loc_str.split(';')[1])

    exclude_func_args = [
        'pyjsonld'
    ]
    exclude_funcs = [
        'link',
        'set',
        'get'
    ]

    bad_function_names = []
    for name, properties in function_properties.items():
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
    for mod_name, _ in modules.items():
        print('Module: ' + mod_name + ' ✓')
        for name, properties in function_properties.items():
            line_ctr = 0
            for line in modules[mod_name]['lines']:
                line_str = line.strip()
                if line_str.startswith('def '):
                    line_ctr += 1
                    continue
                if line_str.startswith('class '):
                    line_ctr += 1
                    continue
                if name + '(' in line:
                    mod_list = \
                        function_properties[name]['calledInModule']
                    if mod_name not in mod_list:
                        mod_list.append(mod_name)
                    if mod_name in exclude_func_args:
                        line_ctr += 1
                        continue
                    if name in exclude_funcs:
                        line_ctr += 1
                        continue
                    call_args = \
                        _get_function_call_args(name,
                                                modules[mod_name]['lines'],
                                                line_ctr)
                    func_args = function_properties[name]['args']
                    if not _function_args_match(call_args, func_args):
                        print('Call to function ' + name +
                              ' does not match its arguments')
                        print('def args: ' +
                              str(len(function_properties[name]['args'])) +
                              '\n' + str(function_properties[name]['args']))
                        print('Call args: ' + str(len(call_args)) + '\n' +
                              str(call_args))
                        print('module ' + mod_name + ' line ' + str(line_ctr))
                        assert False
                line_ctr += 1

    # don't check these functions, because they are procedurally called
    exclusions = [
        'do_GET',
        'do_POST',
        'do_HEAD',
        'do_PROPFIND',
        'do_PUT',
        'do_REPORT',
        'do_DELETE',
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
    exclude_imports = [
        'link',
        'start'
    ]
    exclude_local = [
        'pyjsonld',
        'daemon',
        'tests'
    ]
    exclude_mods = [
        'pyjsonld'
    ]
    # check that functions are called somewhere
    for name, properties in function_properties.items():
        if name.startswith('__'):
            if name.endswith('__'):
                continue
        if name in exclusions:
            continue
        if properties['module'] in exclude_mods:
            continue
        is_local_function = False
        if not properties['calledInModule']:
            print('function ' + name +
                  ' in module ' + properties['module'] +
                  ' is not called anywhere')
        assert properties['calledInModule']

        if len(properties['calledInModule']) == 1:
            mod_name = properties['calledInModule'][0]
            if mod_name not in exclude_local and \
               mod_name == properties['module']:
                is_local_function = True
                if not name.startswith('_'):
                    print('Local function ' + name +
                          ' in ' + mod_name + '.py does not begin with _')
                    assert False

        if name not in exclude_imports:
            for mod_name in properties['calledInModule']:
                if mod_name == properties['module']:
                    continue
                import_str = 'from ' + properties['module'] + ' import ' + name
                if import_str not in modules[mod_name]['source']:
                    print(import_str + ' not found in ' + mod_name + '.py')
                    assert False

        if not is_local_function:
            if name.startswith('_'):
                exclude_public = [
                    'pyjsonld',
                    'daemon',
                    'tests'
                ]
                mod_name = properties['module']
                if mod_name not in exclude_public:
                    print('Public function ' + name + ' in ' +
                          mod_name + '.py begins with _')
                    assert False
        print('Function: ' + name + ' ✓')

    print('Constructing function call graph')
    module_colors = (
        'red', 'green', 'yellow', 'orange', 'purple', 'cyan',
        'darkgoldenrod3', 'darkolivegreen1', 'darkorange1',
        'darkorchid1', 'darkseagreen', 'darkslategray4',
        'deeppink1', 'deepskyblue1', 'dimgrey', 'gold1',
        'goldenrod', 'burlywood2', 'bisque1', 'brown1',
        'chartreuse2', 'cornsilk', 'darksalmon'
    )
    max_module_calls = 1
    max_function_calls = 1
    color_ctr = 0
    for mod_name, _ in modules.items():
        line_ctr = 0
        modules[mod_name]['color'] = module_colors[color_ctr]
        color_ctr += 1
        if color_ctr >= len(module_colors):
            color_ctr = 0
        for line in modules[mod_name]['lines']:
            if line.strip().startswith('def '):
                name = line.split('def ')[1].split('(')[0]
                calls_list = \
                    get_function_calls(name, modules[mod_name]['lines'],
                                       line_ctr, function_properties)
                function_properties[name]['calls'] = calls_list.copy()
                if len(calls_list) > max_function_calls:
                    max_function_calls = len(calls_list)
                # keep track of which module calls which other module
                for fnc in calls_list:
                    mod_call = function_properties[fnc]['module']
                    if mod_call != mod_name:
                        if modules[mod_name].get('calls'):
                            if mod_call not in modules[mod_name]['calls']:
                                modules[mod_name]['calls'].append(mod_call)
                                if len(modules[mod_name]['calls']) > \
                                   max_module_calls:
                                    max_module_calls = \
                                        len(modules[mod_name]['calls'])
                        else:
                            modules[mod_name]['calls'] = [mod_call]
            line_ctr += 1

    _diagram_groups(['Commandline Interface', 'ActivityPub'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Commandline Interface', 'Core'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Timeline', 'Core'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Web Interface', 'Core'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Web Interface Columns', 'Core'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Core'], [],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['ActivityPub'], [],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['ActivityPub', 'Core'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['ActivityPub', 'Security'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Core', 'Security'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Timeline', 'Security'], ['utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Web Interface', 'Accessibility'],
                    ['utils', 'webapp_utils'],
                    modules, mod_groups, max_module_calls)
    _diagram_groups(['Core', 'Accessibility'], ['utils'],
                    modules, mod_groups, max_module_calls)


def _test_links_within_post(base_dir: str) -> None:
    print('test_links_within_post')
    system_language = 'en'
    languages_understood = [system_language]
    nickname = 'test27636'
    domain = 'rando.site'
    port = 443
    http_prefix = 'https'
    content = 'This is a test post with links.\n\n' + \
        'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v4/\n\nhttps://libreserver.org'
    followers_only = False
    save_to_file = False
    client_to_server = False
    comments_enabled = True
    attach_image_filename = None
    media_type = None
    image_description = None
    city = 'London, England'
    test_in_reply_to = None
    test_in_reply_to_atom_uri = None
    test_subject = None
    test_schedule_post = False
    test_event_date = None
    test_event_time = None
    test_location = None
    test_is_article = False
    conversation_id = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    post_json_object = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content, followers_only, save_to_file,
                           client_to_server, comments_enabled,
                           attach_image_filename, media_type,
                           image_description, city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)

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
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
    assert post_json_object['object']['content'] == content
    assert post_json_object['object']['contentMap'][system_language] == content


def _test_mastoapi():
    print('test_masto_api')
    nickname = 'ThisIsATestNickname'
    masto_id = get_masto_api_v1id_from_nickname(nickname)
    assert masto_id
    nickname2 = get_nickname_from_masto_api_v1id(masto_id)
    if nickname2 != nickname:
        print(nickname + ' != ' + nickname2)
    assert nickname2 == nickname


def _test_domain_handling():
    print('test_domain_handling')
    test_domain = 'localhost'
    assert decoded_host(test_domain) == test_domain
    test_domain = '127.0.0.1:60'
    assert decoded_host(test_domain) == test_domain
    test_domain = '192.168.5.153'
    assert decoded_host(test_domain) == test_domain
    test_domain = 'xn--espaa-rta.icom.museum'
    assert decoded_host(test_domain) == "españa.icom.museum"


def _test_prepare_html_post_nick():
    print('test_prepare_html_post_nickname')
    post_html = '<a class="imageAnchor" href="/users/bob?replyfollowers='
    post_html += '<a class="imageAnchor" href="/users/bob?repeatprivate='
    result = prepare_html_post_nickname('alice', post_html)
    assert result == post_html.replace('/bob?', '/alice?')

    post_html = '<a class="imageAnchor" href="/users/bob?replyfollowers='
    post_html += '<a class="imageAnchor" href="/users/bob;repeatprivate='
    expected_html = '<a class="imageAnchor" href="/users/alice?replyfollowers='
    expected_html += '<a class="imageAnchor" href="/users/bob;repeatprivate='
    result = prepare_html_post_nickname('alice', post_html)
    assert result == expected_html


def _test_valid_hash_tag():
    print('test_valid_hash_tag')
    assert valid_hash_tag('blobcat_thisisfine')
    assert valid_hash_tag('ThisIsValid')
    assert valid_hash_tag('this_is_valid')
    assert valid_hash_tag('ThisIsValid12345')
    assert valid_hash_tag('ThisIsVälid')
    assert valid_hash_tag('यहमान्यहै')
    assert valid_hash_tag('한국어')
    assert valid_hash_tag('테스트')
    assert valid_hash_tag('테_스트')
    assert not valid_hash_tag('this-is-invalid')
    assert not valid_hash_tag('ThisIsNotValid!')
    assert not valid_hash_tag('#ThisIsAlsoNotValid')
    assert not valid_hash_tag('#यहमान्यहै')
    assert not valid_hash_tag('ThisIsAlso&NotValid')
    assert not valid_hash_tag('ThisIsAlsoNotValid"')
    assert not valid_hash_tag('This Is Also Not Valid"')
    assert not valid_hash_tag('This=IsAlsoNotValid"')


def _test_markdown_to_html():
    print('test_markdown_to_html')
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
    print('test_extract_text_fields_in_post')
    boundary = '-----------------------------116202748023898664511855843036'
    form_data = '-----------------------------116202748023898664511855' + \
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
    fields = extract_text_fields_in_post(None, boundary, debug, form_data)
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
    detected_links = []
    result = \
        speaker_replace_links(text, {'Linked': 'Web link'}, detected_links)
    assert len(detected_links) == 1
    assert detected_links[0] == \
        'https://support.torproject.org/censorship/' + \
        'how-to-help-running-snowflake/'
    assert 'Web link support.torproject.org' in result


def _test_camel_case_split():
    print('test_camel_case_split')
    test_str = 'ThisIsCamelCase'
    assert camel_case_split(test_str) == 'This Is Camel Case'

    test_str = 'Notcamelcase test'
    assert camel_case_split(test_str) == 'Notcamelcase test'


def _test_emoji_images():
    print('test_emoji_images')
    emoji_filename = 'emoji/default_emoji.json'
    assert os.path.isfile(emoji_filename)
    emoji_json = load_json(emoji_filename)
    assert emoji_json
    for emoji_name, emoji_image in emoji_json.items():
        emoji_image_filename = 'emoji/' + emoji_image + '.png'
        if not os.path.isfile(emoji_image_filename):
            print('Missing emoji image ' + emoji_name + ' ' +
                  emoji_image + '.png')
        assert os.path.isfile(emoji_image_filename)


def _test_extract_pgp_public_key():
    print('testExtractPGPPublicKey')
    pub_key = \
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
    test_str = "Some introduction\n\n" + pub_key + "\n\nSome message."
    assert contains_pgp_public_key(test_str)
    assert not contains_pgp_public_key('String without a pgp key')
    result = extract_pgp_public_key(test_str)
    assert result
    assert result == pub_key


def test_update_actor(base_dir: str):
    print('Testing update of actor properties')

    global TEST_SERVER_ALICE_RUNNING
    TEST_SERVER_ALICE_RUNNING = False

    http_prefix = 'http'
    proxy_type = None
    federation_list = []

    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests',
                      ignore_errors=False, onerror=None)
    os.mkdir(base_dir + '/.tests')

    # create the server
    alice_dir = base_dir + '/.tests/alice'
    alice_domain = '127.0.0.11'
    alice_port = 61792
    alice_send_threads = []
    bob_address = '127.0.0.84:6384'

    global THR_ALICE
    if THR_ALICE:
        while THR_ALICE.is_alive():
            THR_ALICE.stop()
            time.sleep(1)
        THR_ALICE.kill()

    THR_ALICE = \
        thread_with_trace(target=create_server_alice,
                          args=(alice_dir, alice_domain,
                                alice_port, bob_address,
                                federation_list, False, False,
                                alice_send_threads),
                          daemon=True)

    THR_ALICE.start()
    assert THR_ALICE.is_alive() is True

    # wait for server to be running
    ctr = 0
    while not TEST_SERVER_ALICE_RUNNING:
        time.sleep(1)
        ctr += 1
        if ctr > 60:
            break
    print('Alice online: ' + str(TEST_SERVER_ALICE_RUNNING))

    print('\n\n*******************************************************')
    print('Alice updates her PGP key')

    session_alice = create_session(proxy_type)
    cached_webfingers = {}
    person_cache = {}
    password = 'alicepass'
    outbox_path = alice_dir + '/accounts/alice@' + alice_domain + '/outbox'
    actor_filename = \
        alice_dir + '/accounts/' + 'alice@' + alice_domain + '.json'
    assert os.path.isfile(actor_filename)
    assert len([name for name in os.listdir(outbox_path)
                if os.path.isfile(os.path.join(outbox_path, name))]) == 0
    pub_key = \
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
    actor_update = \
        pgp_public_key_upload(alice_dir, session_alice,
                              'alice', password,
                              alice_domain, alice_port,
                              http_prefix,
                              cached_webfingers, person_cache,
                              True, pub_key, signing_priv_key_pem)
    print('actor update result: ' + str(actor_update))
    assert actor_update

    # load alice actor
    print('Loading actor: ' + actor_filename)
    actor_json = load_json(actor_filename)
    assert actor_json
    if len(actor_json['attachment']) == 0:
        print("actor_json['attachment'] has no contents")
    assert len(actor_json['attachment']) > 0
    property_found = False
    for property_value in actor_json['attachment']:
        if property_value['name'] == 'PGP':
            print('PGP property set within attachment')
            assert pub_key in property_value['value']
            property_found = True
    assert property_found

    # stop the server
    THR_ALICE.kill()
    THR_ALICE.join()
    assert THR_ALICE.is_alive() is False

    os.chdir(base_dir)
    if os.path.isdir(base_dir + '/.tests'):
        shutil.rmtree(base_dir + '/.tests', ignore_errors=False, onerror=None)


def _test_remove_interactions() -> None:
    print('test_remove_post_interactions')
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
    print('test_spoof_geolocation')
    nogo_line = \
        'NEW YORK, USA: 73.951W,40.879,  73.974W,40.83,  ' + \
        '74.029W,40.756,  74.038W,40.713,  74.056W,40.713,  ' + \
        '74.127W,40.647,  74.038W,40.629,  73.995W,40.667,  ' + \
        '74.014W,40.676,  73.994W,40.702,  73.967W,40.699,  ' + \
        '73.958W,40.729,  73.956W,40.745,  73.918W,40.781,  ' + \
        '73.937W,40.793,  73.946W,40.782,  73.977W,40.738,  ' + \
        '73.98W,40.713,  74.012W,40.705,  74.006W,40.752,  ' + \
        '73.955W,40.824'
    polygon = parse_nogo_string(nogo_line)
    assert len(polygon) > 0
    assert polygon[0][1] == -73.951
    assert polygon[0][0] == 40.879
    cities_list = [
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
    test_square = [
        [[0.03, 0.01], [0.02, 10], [10.01, 10.02], [10.03, 0.02]]
    ]
    assert point_in_nogo(test_square, 5, 5)
    assert point_in_nogo(test_square, 2, 3)
    assert not point_in_nogo(test_square, 20, 5)
    assert not point_in_nogo(test_square, 11, 6)
    assert not point_in_nogo(test_square, 5, -5)
    assert not point_in_nogo(test_square, 5, 11)
    assert not point_in_nogo(test_square, -5, -5)
    assert not point_in_nogo(test_square, -5, 5)
    nogo_list = []
    curr_time = datetime.datetime.utcnow()
    decoy_seed = 7634681
    city_radius = 0.1
    coords = spoof_geolocation('', 'los angeles', curr_time,
                               decoy_seed, cities_list, nogo_list)
    assert coords[0] >= 34.0536909 - city_radius
    assert coords[0] <= 34.0536909 + city_radius
    assert coords[1] >= 118.242766 - city_radius
    assert coords[1] <= 118.242766 + city_radius
    assert coords[2] == 'N'
    assert coords[3] == 'W'
    assert len(coords[4]) > 4
    assert len(coords[5]) > 4
    assert coords[6] > 0
    nogo_list = []
    coords = spoof_geolocation('', 'unknown', curr_time,
                               decoy_seed, cities_list, nogo_list)
    assert coords[0] >= 51.8744 - city_radius
    assert coords[0] <= 51.8744 + city_radius
    assert coords[1] >= 0.368333 - city_radius
    assert coords[1] <= 0.368333 + city_radius
    assert coords[2] == 'N'
    assert coords[3] == 'W'
    assert len(coords[4]) == 0
    assert len(coords[5]) == 0
    assert coords[6] == 0
    kml_str = '<?xml version="1.0" encoding="UTF-8"?>\n'
    kml_str += '<kml xmlns="http://www.opengis.net/kml/2.2">\n'
    kml_str += '<Document>\n'
    nogo_line2 = \
        'NEW YORK, USA: 74.115W,40.663,  74.065W,40.602,  ' + \
        '74.118W,40.555,  74.047W,40.516,  73.882W,40.547,  ' + \
        '73.909W,40.618,  73.978W,40.579,  74.009W,40.602,  ' + \
        '74.033W,40.61,  74.039W,40.623,  74.032W,40.641,  ' + \
        '73.996W,40.665'
    polygon2 = parse_nogo_string(nogo_line2)
    nogo_list = [polygon, polygon2]
    for i in range(1000):
        day_number = randint(10, 30)
        hour = randint(1, 23)
        hour_str = str(hour)
        if hour < 10:
            hour_str = '0' + hour_str
        date_time_str = "2021-05-" + str(day_number) + " " + hour_str + ":14"
        curr_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'new york, usa', curr_time,
                                   decoy_seed, cities_list, nogo_list)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kml_str += '<Placemark id="' + str(i) + '">\n'
        kml_str += '  <name>' + str(i) + '</name>\n'
        kml_str += '  <Point>\n'
        kml_str += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kml_str += '  </Point>\n'
        kml_str += '</Placemark>\n'

    nogo_line = \
        'LONDON, ENGLAND: 0.23888E,51.459,  0.1216E,51.5,  ' + \
        '0.016E,51.479,  0.097W,51.502,  0.126W,51.482,  ' + \
        '0.196W,51.457,  0.292W,51.465,  0.309W,51.49,  ' + \
        '0.226W,51.495,  0.198W,51.47,  0.174W,51.488,  ' + \
        '0.136W,51.489,  0.1189W,51.515,  0.038E,51.513,  ' + \
        '0.0692E,51.51,  0.12833E,51.526,  0.3289E,51.475'
    polygon = parse_nogo_string(nogo_line)
    nogo_line2 = \
        'LONDON, ENGLAND: 0.054W,51.535,  0.044W,51.53,  ' + \
        '0.008W,51.55,  0.0429W,51.57,  0.038W,51.6,  ' + \
        '0.0209W,51.603,  0.032W,51.613,  0.00191E,51.66,  ' + \
        '0.024W,51.666,  0.0313W,51.659,  0.0639W,51.579,  ' + \
        '0.059W,51.568,  0.0329W,51.552'
    polygon2 = parse_nogo_string(nogo_line2)
    nogo_list = [polygon, polygon2]
    for i in range(1000):
        day_number = randint(10, 30)
        hour = randint(1, 23)
        hour_str = str(hour)
        if hour < 10:
            hour_str = '0' + hour_str
        date_time_str = "2021-05-" + str(day_number) + " " + hour_str + ":14"
        curr_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'london, england', curr_time,
                                   decoy_seed, cities_list, nogo_list)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kml_str += '<Placemark id="' + str(i) + '">\n'
        kml_str += '  <name>' + str(i) + '</name>\n'
        kml_str += '  <Point>\n'
        kml_str += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kml_str += '  </Point>\n'
        kml_str += '</Placemark>\n'

    nogo_line = \
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
    polygon = parse_nogo_string(nogo_line)
    nogo_line2 = \
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
    polygon2 = parse_nogo_string(nogo_line2)
    nogo_list = [polygon, polygon2]
    for i in range(1000):
        day_number = randint(10, 30)
        hour = randint(1, 23)
        hour_str = str(hour)
        if hour < 10:
            hour_str = '0' + hour_str
        date_time_str = "2021-05-" + str(day_number) + " " + hour_str + ":14"
        curr_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'SAN FRANCISCO, USA', curr_time,
                                   decoy_seed, cities_list, nogo_list)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kml_str += '<Placemark id="' + str(i) + '">\n'
        kml_str += '  <name>' + str(i) + '</name>\n'
        kml_str += '  <Point>\n'
        kml_str += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kml_str += '  </Point>\n'
        kml_str += '</Placemark>\n'

    nogo_line = \
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
    polygon = parse_nogo_string(nogo_line)
    nogo_line2 = \
        'SEATTLE, USA: 122.267W,47.758,  122.29W,47.471,  ' + \
        '122.272W,47.693,  122.256W,47.672,  122.278W,47.652,  ' + \
        '122.29W,47.583,  122.262W,47.548,  122.265W,47.52,  ' + \
        '122.218W,47.498,  122.194W,47.501,  122.193W,47.55,  ' + \
        '122.173W,47.58,  122.22W,47.617,  122.238W,47.617,  ' + \
        '122.239W,47.637,  122.2W,47.644,  122.207W,47.703,  ' + \
        '122.22W,47.705,  122.231W,47.699,  122.255W,47.751'
    polygon2 = parse_nogo_string(nogo_line2)
    nogo_line3 = \
        'SEATTLE, USA: 122.347W,47.675,  122.344W,47.681,  ' + \
        '122.337W,47.685,  122.324W,47.679,  122.331W,47.677,  ' + \
        '122.34W,47.669,  122.34W,47.664,  122.348W,47.665'
    polygon3 = parse_nogo_string(nogo_line3)
    nogo_line4 = \
        'SEATTLE, USA: 122.423W,47.669,  122.345W,47.641,  ' + \
        '122.34W,47.625,  122.327W,47.626,  122.274W,47.64,  ' + \
        '122.268W,47.654,  122.327W,47.654,  122.336W,47.647,  ' + \
        '122.429W,47.684'
    polygon4 = parse_nogo_string(nogo_line4)
    nogo_list = [polygon, polygon2, polygon3, polygon4]
    for i in range(1000):
        day_number = randint(10, 30)
        hour = randint(1, 23)
        hour_str = str(hour)
        if hour < 10:
            hour_str = '0' + hour_str
        date_time_str = "2021-05-" + str(day_number) + " " + hour_str + ":14"
        curr_time = datetime.datetime.strptime(date_time_str, "%Y-%m-%d %H:%M")
        coords = spoof_geolocation('', 'SEATTLE, USA', curr_time,
                                   decoy_seed, cities_list, nogo_list)
        longitude = coords[1]
        if coords[3] == 'W':
            longitude = -coords[1]
        kml_str += '<Placemark id="' + str(i) + '">\n'
        kml_str += '  <name>' + str(i) + '</name>\n'
        kml_str += '  <Point>\n'
        kml_str += '    <coordinates>' + str(longitude) + ',' + \
            str(coords[0]) + ',0</coordinates>\n'
        kml_str += '  </Point>\n'
        kml_str += '</Placemark>\n'

    kml_str += '</Document>\n'
    kml_str += '</kml>'
    with open('unittest_decoy.kml', 'w+') as kmlfile:
        kmlfile.write(kml_str)


def _test_skills() -> None:
    print('test_skills')
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
    skills_dict = {
        'bakery': 40,
        'gardening': 70
    }
    set_skills_from_dict(actor_json, skills_dict)
    assert actor_has_skill(actor_json, 'bakery')
    assert actor_has_skill(actor_json, 'gardening')
    assert actor_skill_value(actor_json, 'bakery') == 40
    assert actor_skill_value(actor_json, 'gardening') == 70


def _test_roles() -> None:
    print('test_roles')
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
    test_roles_list = ["admin", "moderator"]
    set_rolesFromList(actor_json, test_roles_list)
    assert actor_has_role(actor_json, "admin")
    assert actor_has_role(actor_json, "moderator")
    assert not actor_has_role(actor_json, "editor")
    assert not actor_has_role(actor_json, "counselor")
    assert not actor_has_role(actor_json, "artist")


def _test_useragent_domain() -> None:
    print('test_user_agent_domain')
    user_agent = \
        'http.rb/4.4.1 (Mastodon/9.10.11; +https://mastodon.something/)'
    agent_domain = user_agent_domain(user_agent, False)
    if agent_domain != 'mastodon.something':
        print(agent_domain)
    assert agent_domain == 'mastodon.something'
    user_agent = \
        'Mozilla/70.0 (X11; Linux x86_64; rv:1.0) Gecko/20450101 Firefox/1.0'
    assert user_agent_domain(user_agent, False) is None


def _test_switch_word(base_dir: str) -> None:
    print('test_switch_words')
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
    print('test_limit_word_lengths')
    max_word_length = 13
    text = "This is a test"
    result = limit_word_lengths(text, max_word_length)
    assert result == text

    text = "This is an exceptionallylongword test"
    result = limit_word_lengths(text, max_word_length)
    assert result == "This is an exceptionally test"


def _test_limit_repeted_words() -> None:
    print('test_limit_repeated_words')
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
    print('test_set_actor_languages')
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
    languages_str = get_actor_languages(actor_json)
    assert languages_str == 'en / es / fr'


def _test_get_links_from_content():
    print('test_get_links_from_content')
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

    content_plain = '<p>' + remove_html(content) + '</p>'
    assert '>@linked</a>' not in content_plain
    content = add_links_to_content(content_plain, links)
    assert '>@linked</a>' in content


def _test_authorized_shared_items():
    print('test_authorize_shared_items')
    shared_items_fed_domains = \
        ['dog.domain', 'cat.domain', 'birb.domain']
    tokens_json = \
        generate_shared_item_federation_tokens(shared_items_fed_domains, None)
    tokens_json = \
        create_shared_item_federation_token(None, 'cat.domain',
                                            False, tokens_json)
    assert tokens_json
    assert not tokens_json.get('dog.domain')
    assert tokens_json.get('cat.domain')
    assert not tokens_json.get('birb.domain')
    assert len(tokens_json['dog.domain']) == 0
    assert len(tokens_json['cat.domain']) >= 64
    assert len(tokens_json['birb.domain']) == 0
    assert not authorize_shared_items(shared_items_fed_domains, None,
                                      'birb.domain',
                                      'cat.domain', 'M' * 86,
                                      False, tokens_json)
    assert authorize_shared_items(shared_items_fed_domains, None,
                                  'birb.domain',
                                  'cat.domain', tokens_json['cat.domain'],
                                  False, tokens_json)
    tokens_json = \
        update_shared_item_federation_token(None,
                                            'dog.domain', 'testToken',
                                            True, tokens_json)
    assert tokens_json['dog.domain'] == 'testToken'

    # the shared item federation list changes
    shared_items_federated_domains = \
        ['possum.domain', 'cat.domain', 'birb.domain']
    tokens_json = \
        merge_shared_item_tokens(None, '',
                                 shared_items_federated_domains,
                                 tokens_json)
    assert 'dog.domain' not in tokens_json
    assert 'cat.domain' in tokens_json
    assert len(tokens_json['cat.domain']) >= 64
    assert 'birb.domain' in tokens_json
    assert 'possum.domain' in tokens_json
    assert len(tokens_json['birb.domain']) == 0
    assert len(tokens_json['possum.domain']) == 0


def _test_date_conversions() -> None:
    print('test_date_conversions')
    date_str = "2021-05-16T14:37:41Z"
    date_sec = date_string_to_seconds(date_str)
    date_str2 = date_seconds_to_string(date_sec)
    assert date_str == date_str2


def _test_valid_password():
    print('test_valid_password')
    assert not valid_password('123')
    assert not valid_password('')
    assert valid_password('パスワード12345')
    assert valid_password('测试密码12345')
    assert valid_password('A!bc:defg1/234?56')


def _test_get_price_from_string() -> None:
    print('test_get_price_from_string')
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
    print('test_translate_ontology')
    return
    ontology_types = get_category_types(base_dir)
    url = 'https://translate.astian.org'
    api_key = None
    lt_lang_list = libretranslate_languages(url, api_key)

    languages_str = get_supported_languages(base_dir)
    assert languages_str

    for otype in ontology_types:
        changed = False
        filename = base_dir + '/ontology/' + otype + 'Types.json'
        if not os.path.isfile(filename):
            continue
        ontology_json = load_json(filename)
        if not ontology_json:
            continue
        index = -1
        for item in ontology_json['@graph']:
            index += 1
            if "rdfs:label" not in item:
                continue
            english_str = None
            languages_found = []
            for label in item["rdfs:label"]:
                if '@language' not in label:
                    continue
                languages_found.append(label['@language'])
                if '@value' not in label:
                    continue
                if label['@language'] == 'en':
                    english_str = label['@value']
            if not english_str:
                continue
            for lang in languages_str:
                if lang not in languages_found:
                    translated_str = None
                    if url and lang in lt_lang_list:
                        translated_str = \
                            libretranslate(url, english_str,
                                           'en', lang, api_key)
                    if not translated_str:
                        translated_str = english_str
                    else:
                        translated_str = translated_str.replace('<p>', '')
                        translated_str = translated_str.replace('</p>', '')
                    ontology_json['@graph'][index]["rdfs:label"].append({
                        "@value": translated_str,
                        "@language": lang
                    })
                    changed = True
        if not changed:
            continue
        save_json(ontology_json, filename + '.new')


def _test_can_replyto(base_dir: str) -> None:
    print('test_can_reply_to')
    system_language = 'en'
    languages_understood = [system_language]
    nickname = 'test27637'
    domain = 'rando.site'
    port = 443
    http_prefix = 'https'
    content = 'This is a test post with links.\n\n' + \
        'ftp://ftp.ncdc.noaa.gov/pub/data/ghcn/v4/\n\nhttps://libreserver.org'
    followers_only = False
    save_to_file = False
    client_to_server = False
    comments_enabled = True
    attach_image_filename = None
    media_type = None
    image_description = None
    city = 'London, England'
    test_in_reply_to = None
    test_in_reply_to_atom_uri = None
    test_subject = None
    test_schedule_post = False
    test_event_date = None
    test_event_time = None
    test_location = None
    test_is_article = False
    conversation_id = None
    low_bandwidth = True
    content_license_url = 'https://creativecommons.org/licenses/by/4.0'

    post_json_object = \
        create_public_post(base_dir, nickname, domain, port, http_prefix,
                           content, followers_only, save_to_file,
                           client_to_server, comments_enabled,
                           attach_image_filename, media_type,
                           image_description, city,
                           test_in_reply_to, test_in_reply_to_atom_uri,
                           test_subject, test_schedule_post,
                           test_event_date, test_event_time, test_location,
                           test_is_article, system_language, conversation_id,
                           low_bandwidth, content_license_url,
                           languages_understood)
    # set the date on the post
    curr_date_str = "2021-09-08T20:45:00Z"
    post_json_object['published'] = curr_date_str
    post_json_object['object']['published'] = curr_date_str

    # test a post within the reply interval
    post_url = post_json_object['object']['id']
    reply_interval_hours = 2
    curr_date_str = "2021-09-08T21:32:10Z"
    assert can_reply_to(base_dir, nickname, domain,
                        post_url, reply_interval_hours,
                        curr_date_str,
                        post_json_object)

    # test a post outside of the reply interval
    curr_date_str = "2021-09-09T09:24:47Z"
    assert not can_reply_to(base_dir, nickname, domain,
                            post_url, reply_interval_hours,
                            curr_date_str,
                            post_json_object)


def _test_seconds_between_publish() -> None:
    print('test_seconds_between_published')
    published1 = "2021-10-14T09:39:27Z"
    published2 = "2021-10-14T09:41:28Z"

    seconds_elapsed = seconds_between_published(published1, published2)
    assert seconds_elapsed == 121
    # invalid date
    published2 = "2021-10-14N09:41:28Z"
    seconds_elapsed = seconds_between_published(published1, published2)
    assert seconds_elapsed == -1


def _test_word_similarity() -> None:
    print('test_words_similarity')
    min_words = 10
    content1 = "This is the same"
    content2 = "This is the same"
    assert words_similarity(content1, content2, min_words) == 100
    content1 = "This is our world now... " + \
        "the world of the electron and the switch, the beauty of the baud"
    content2 = "This is our world now. " + \
        "The world of the electron and the webkit, the beauty of the baud"
    similarity = words_similarity(content1, content2, min_words)
    assert similarity > 70
    content1 = "<p>We&apos;re growing! </p><p>A new denizen " + \
        "is frequenting HackBucket. You probably know him already " + \
        "from her epic typos - but let&apos;s not spoil too much " + \
        "\ud83d\udd2e</p>"
    content2 = "<p>We&apos;re growing! </p><p>A new denizen " + \
        "is frequenting HackBucket. You probably know them already " + \
        "from their epic typos - but let&apos;s not spoil too much " + \
        "\ud83d\udd2e</p>"
    similarity = words_similarity(content1, content2, min_words)
    assert similarity > 80


def _test_add_cw_lists(base_dir: str) -> None:
    print('test_add_CW_from_lists')
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
    print('test_valid_emoji_content')
    assert not valid_emoji_content(None)
    assert not valid_emoji_content(' ')
    assert not valid_emoji_content('j')
    assert not valid_emoji_content('😀😀😀')
    assert valid_emoji_content('😀')
    assert valid_emoji_content('😄')


def _test_httpsig_base_new(with_digest: bool, base_dir: str,
                           algorithm: str, digest_algorithm: str) -> None:
    print('test_httpsig_new(' + str(with_digest) + ')')

    debug = True
    path = base_dir + '/.testHttpsigBaseNew'
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=False, onerror=None)
    os.mkdir(path)
    os.chdir(path)

    content_type = 'application/activity+json'
    nickname = 'socrates'
    host_domain = 'someother.instance'
    domain = 'argumentative.social'
    http_prefix = 'https'
    port = 5576
    password = 'SuperSecretPassword'
    private_key_pem, public_key_pem, _, _ = \
        create_person(path, nickname, domain, port, http_prefix,
                      False, False, password)
    assert private_key_pem
    if with_digest:
        message_body_json = {
            "a key": "a value",
            "another key": "A string",
            "yet another key": "Another string"
        }
        message_body_json_str = json.dumps(message_body_json)
    else:
        message_body_json_str = ''

    headers_domain = get_full_domain(host_domain, port)

    date_str = strftime("%a, %d %b %Y %H:%M:%S %Z", gmtime())
    boxpath = '/inbox'
    if not with_digest:
        headers = {
            'host': headers_domain,
            'date': date_str,
            'accept': content_type
        }
        signature_index_header, signature_header = \
            sign_post_headers_new(date_str, private_key_pem, nickname,
                                  domain, port,
                                  host_domain, port,
                                  boxpath, http_prefix, message_body_json_str,
                                  algorithm, digest_algorithm, debug)
    else:
        digest_prefix = get_digest_prefix(digest_algorithm)
        body_digest = \
            message_content_digest(message_body_json_str, digest_algorithm)
        content_length = len(message_body_json_str)
        headers = {
            'host': headers_domain,
            'date': date_str,
            'digest': f'{digest_prefix}={body_digest}',
            'content-type': content_type,
            'content-length': str(content_length)
        }
        assert get_digest_algorithm_from_headers(headers) == digest_algorithm
        signature_index_header, signature_header = \
            sign_post_headers_new(date_str, private_key_pem, nickname,
                                  domain, port, host_domain, port,
                                  boxpath, http_prefix, message_body_json_str,
                                  algorithm, digest_algorithm, debug)

    headers['signature'] = signature_header
    headers['signature-input'] = signature_index_header
    print('headers: ' + str(headers))

    getreq_method = not with_digest
    debug = True
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, getreq_method, None,
                               message_body_json_str, debug)
    debug = False
    if with_digest:
        # everything correct except for content-length
        headers['content-length'] = str(content_length + 2)
        assert verify_post_headers(http_prefix, public_key_pem, headers,
                                   boxpath, getreq_method, None,
                                   message_body_json_str, debug) is False
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               '/parambulator' + boxpath, getreq_method, None,
                               message_body_json_str, debug) is False
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, not getreq_method, None,
                               message_body_json_str, debug) is False
    if not with_digest:
        # fake domain
        headers = {
            'host': 'bogon.domain',
            'date': date_str,
            'content-type': content_type
        }
    else:
        # correct domain but fake message
        message_body_json_str = \
            '{"a key": "a value", "another key": "Fake GNUs", ' + \
            '"yet another key": "More Fake GNUs"}'
        content_length = len(message_body_json_str)
        digest_prefix = get_digest_prefix(digest_algorithm)
        body_digest = \
            message_content_digest(message_body_json_str, digest_algorithm)
        headers = {
            'host': domain,
            'date': date_str,
            'digest': f'{digest_prefix}={body_digest}',
            'content-type': content_type,
            'content-length': str(content_length)
        }
        assert get_digest_algorithm_from_headers(headers) == digest_algorithm
    headers['signature'] = signature_header
    headers['signature-input'] = signature_index_header
    pprint(headers)
    assert verify_post_headers(http_prefix, public_key_pem, headers,
                               boxpath, not getreq_method, None,
                               message_body_json_str, False) is False

    os.chdir(base_dir)
    shutil.rmtree(path, ignore_errors=False, onerror=None)


def _test_get_actor_from_in_reply_to() -> None:
    print('test_get_actor_from_in_reply_to')
    in_reply_to = \
        'https://fosstodon.org/users/bashrc/statuses/107400700612621140'
    reply_actor = get_actor_from_in_reply_to(in_reply_to)
    assert reply_actor == 'https://fosstodon.org/users/bashrc'

    in_reply_to = 'https://fosstodon.org/activity/107400700612621140'
    reply_actor = get_actor_from_in_reply_to(in_reply_to)
    assert reply_actor is None


def _test_xml_podcast_dict(base_dir: str) -> None:
    print('test_xml_podcast_dict')
    xml_str = \
        '<?xml version="1.0" encoding="UTF-8" ?>\n' + \
        '<rss version="2.0" xmlns:podcast="' + \
        'https://podcastindex.org/namespace/1.0">\n' + \
        '<podcast:episode>5</podcast:episode>\n' + \
        '<podcast:chapters ' + \
        'url="https://whoframed.rodger/ep1_chapters.json" ' + \
        'type="application/json"/>\n' + \
        '<podcast:funding ' + \
        'url="https://whoframed.rodger/donate">' + \
        'Support the show</podcast:funding>\n' + \
        '<podcast:images ' + \
        'srcset="https://whoframed.rodger/images/ep1/' + \
        'pci_avatar-massive.jpg 1500w, ' + \
        'https://whoframed.rodger/images/ep1/pci_avatar-middle.jpg 600w, ' + \
        'https://whoframed.rodger/images/ep1/pci_avatar-small.jpg 300w, ' + \
        'https://whoframed.rodger/images/ep1/' + \
        'pci_avatar-microfiche.jpg 50w" />\n' + \
        '<podcast:location geo="geo:57.4272,34.63763" osm="R472152">' + \
        'Nowheresville</podcast:location>\n' + \
        '<podcast:locked owner="podcastowner@whoframed.rodger">yes' + \
        '</podcast:locked>\n' + \
        '<podcast:person group="visuals" role="cover art designer" ' + \
        'href="https://whoframed.rodger/artist/rodgetrabbit">' + \
        'Rodger Rabbit</podcast:person>\n' + \
        '<podcast:person href="https://whoframed.rodger" ' + \
        'img="http://whoframed.rodger/images/rr.jpg">Rodger Rabbit' + \
        '</podcast:person>\n' + \
        '<podcast:person href="https://whoframed.rodger" ' + \
        'img="http://whoframed.rodger/images/jr.jpg">' + \
        'Jessica Rabbit</podcast:person>\n' + \
        '<podcast:person role="guest" ' + \
        'href="https://whoframed.rodger/blog/bettyboop/" ' + \
        'img="http://whoframed.rodger/images/bb.jpg">' + \
        'Betty Boop</podcast:person>\n' + \
        '<podcast:person role="guest" ' + \
        'href="https://goodto.talk/bobhoskins/" ' + \
        'img="https://goodto.talk/images/bhosk.jpg">' + \
        'Bob Hoskins</podcast:person>\n' + \
        '<podcast:season name="Podcasting 2.0">1</podcast:season>\n' + \
        '<podcast:soundbite startTime="15.27" duration="8.0" />\n' + \
        '<podcast:soundbite startTime="21.34" duration="32.0" />\n' + \
        '<podcast:transcript ' + \
        'url="https://whoframed.rodger/ep1/transcript.txt" ' + \
        'type="text/plain" />\n' + \
        '<podcast:transcript ' + \
        'url="https://whoframed.rodger/ep2/transcript.txt" ' + \
        'type="text/plain" />\n' + \
        '<podcast:transcript ' + \
        'url="https://whoframed.rodger/ep3/transcript.txt" ' + \
        'type="text/plain" />\n' + \
        '<podcast:value type="donate" method="keysend" ' + \
        'suggested="2.95">\n' + \
        '  <podcast:valueRecipient name="hosting company" ' + \
        'type="node" address="someaddress1" split="1" />\n' + \
        '  <podcast:valueRecipient name="podcaster" type="node" ' + \
        'address="someaddress2" split="99" />\n' + \
        '</podcast:value>\n' + \
        '</rss>'
    podcast_properties = xml_podcast_to_dict(base_dir, xml_str, xml_str)
    assert podcast_properties
    # pprint(podcast_properties)
    assert podcast_properties.get('valueRecipients')
    assert podcast_properties.get('persons')
    assert podcast_properties.get('soundbites')
    assert podcast_properties.get('locations')
    assert podcast_properties.get('transcripts')
    assert podcast_properties.get('episode')
    assert podcast_properties.get('funding')
    assert int(podcast_properties['episode']) == 5
    assert podcast_properties['funding']['text'] == "Support the show"
    assert podcast_properties['funding']['url'] == \
        "https://whoframed.rodger/donate"
    assert len(podcast_properties['transcripts']) == 3
    assert len(podcast_properties['valueRecipients']) == 2
    assert len(podcast_properties['persons']) == 5
    assert len(podcast_properties['locations']) == 1


def _test_get_link_from_rss_item() -> None:
    print('test_get_link_from_rssitem')
    rss_item = \
        '<link>' + \
        'https://anchor.fm/creativecommons/episodes/' + \
        'Hessel-van-Oorschot-of-Tribe-of-Noise--Free-Music-Archive-e1crvce' + \
        '</link>' + \
        '<pubDate>Wed, 12 Jan 2022 14:28:46 GMT</pubDate>' + \
        '<enclosure url="https://anchor.fm/s/4d70d828/podcast/' + \
        'play/46054222/https%3A%2F%2Fd3ctxlq1ktw2nl.cloudfront.net' + \
        '%2Fstaging%2F2022-0-12%2F7352f28c-a928-ea7a-65ae-' + \
        'ccb5edffbac1.mp3" length="67247880" type="audio/mpeg"/>'
    link, mime_type = get_link_from_rss_item(rss_item)
    assert link
    assert link.endswith('.mp3')
    assert mime_type
    assert mime_type == 'audio/mpeg'

    rss_item = \
        '<link>' + \
        'https://anchor.fm/creativecommons/episodes/' + \
        'Hessel-van-Oorschot-of-Tribe-of-Noise--Free-Music-Archive-e1crvce' + \
        '</link>' + \
        '<pubDate>Wed, 12 Jan 2022 14:28:46 GMT</pubDate>'
    link, mime_type = get_link_from_rss_item(rss_item)
    assert link
    assert link.startswith('https://anchor.fm')
    assert not mime_type

    rss_item = \
        '<link href="' + \
        'https://test.link/creativecommons/episodes/' + \
        'Hessel-van-Oorschot-of-Tribe-of-Noise--Free-Music-Archive-e1crvce' + \
        '"/>' + \
        '<pubDate>Wed, 12 Jan 2022 14:28:46 GMT</pubDate>'
    link, mime_type = get_link_from_rss_item(rss_item)
    assert link
    assert link.startswith('https://test.link/creativecommons')


def _test_safe_webtext() -> None:
    print('test_safe_webtext')
    web_text = '<p>Some text including a link https://some.site/some-path</p>'
    expected_text = 'Some text including a link ' + \
        '<a href="https://some.site/some-path"'
    safe_text = safe_web_text(web_text)
    if expected_text not in safe_text:
        print('Original html: ' + web_text)
        print('Expected html: ' + expected_text)
        print('Actual html: ' + safe_text)
    assert expected_text in safe_text
    assert '<p>' not in safe_text
    assert '</p>' not in safe_text

    web_text = 'Some text with <script>some script</script>'
    expected_text = 'Some text with some script'
    safe_text = safe_web_text(web_text)
    if expected_text != safe_text:
        print('Original html: ' + web_text)
        print('Expected html: ' + expected_text)
        print('Actual html: ' + safe_text)
    assert expected_text == safe_text


def _test_published_to_local_timezone() -> None:
    print('published_to_local_timezone')
    published_str = '2022-02-25T20:15:00Z'
    timezone = 'Europe/Berlin'
    published = \
        datetime.datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
    datetime_object = \
        convert_published_to_local_timezone(published, timezone)
    local_time_str = datetime_object.strftime("%a %b %d, %H:%M")
    assert local_time_str == 'Fri Feb 25, 21:15'

    timezone = 'Asia/Seoul'
    published = \
        datetime.datetime.strptime(published_str, "%Y-%m-%dT%H:%M:%SZ")
    datetime_object = \
        convert_published_to_local_timezone(published, timezone)
    local_time_str = datetime_object.strftime("%a %b %d, %H:%M")
    assert local_time_str == 'Sat Feb 26, 05:15'


def _test_bold_reading() -> None:
    print('bold_reading')
    text = "This is a test of emboldening."
    text_bold = bold_reading_string(text)
    expected = \
        "<b>Th</b>is <b>i</b>s a <b>te</b>st <b>o</b>f " + \
        "<b>embold</b>ening."
    if text_bold != expected:
        print(text_bold)
    assert text_bold == expected

    text = "<p>This is a test of emboldening with paragraph.<p>"
    text_bold = bold_reading_string(text)
    expected = \
        "<p><b>Th</b>is <b>i</b>s a <b>te</b>st <b>o</b>f " + \
        "<b>embold</b>ening <b>wi</b>th <b>parag</b>raph.</p>"
    if text_bold != expected:
        print(text_bold)
    assert text_bold == expected

    text = \
        "<p>This is a test of emboldening</p>" + \
        "<p>With more than one paragraph.<p>"
    text_bold = bold_reading_string(text)
    expected = \
        "<p><b>Th</b>is <b>i</b>s a <b>te</b>st <b>o</b>f " + \
        "<b>embold</b>ening</p><p><b>Wi</b>th <b>mo</b>re " + \
        "<b>th</b>an <b>on</b>e <b>parag</b>raph.</p>"
    if text_bold != expected:
        print(text_bold)
    assert text_bold == expected

    text = '<p>This is a test <a class="some class" ' + \
        'href="some_url"><label>with markup containing spaces</label></a><p>'
    text_bold = bold_reading_string(text)
    expected = \
        '<p><b>Th</b>is <b>i</b>s a <b>te</b>st ' + \
        '<a class="some class" href="some_url"><label>with ' + \
        '<b>mar</b>kup <b>conta</b>ining spaces</label></a></p>'
    if text_bold != expected:
        print(text_bold)
    assert text_bold == expected

    text = "There&apos;s the quoted text here"
    text_bold = bold_reading_string(text)
    expected = \
        "<b>Ther</b>e's <b>th</b>e <b>quo</b>ted <b>te</b>xt <b>he</b>re"
    if text_bold != expected:
        print(text_bold)
    assert text_bold == expected

    text = '<p><span class=\"h-card\"><a ' + \
        'href=\"https://something.social/@someone\" ' + \
        'class=\"u-url mention\">@<span>Someone or other' + \
        '</span></a></span> some text</p>'
    text_bold = bold_reading_string(text)
    expected = \
        '<p><span class="h-card">' + \
        '<a href="https://something.social/@someone" ' + \
        'class="u-url mention">@<span>Someone <b>o</b>r other' + \
        '</span></a></span> <b>so</b>me <b>te</b>xt</p>'
    if text_bold != expected:
        print(text_bold)
    assert text_bold == expected


def run_all_tests():
    base_dir = os.getcwd()
    print('Running tests...')
    update_default_themes_list(os.getcwd())
    _test_source_contains_no_tabs()
    _translate_ontology(base_dir)
    _test_get_price_from_string()
    _test_post_variable_names()
    _test_config_param_names()
    _test_post_field_names('daemon.py', ['fields', 'actor_json'])
    _test_post_field_names('theme.py', ['config_json'])
    _test_post_field_names('inbox.py',
                           ['queue_json', 'post_json_object',
                            'message_json', 'liked_post_json'])
    _test_checkbox_names()
    _test_functions()
    _test_bold_reading()
    _test_published_to_local_timezone()
    _test_safe_webtext()
    _test_get_link_from_rss_item()
    _test_xml_podcast_dict(base_dir)
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
    _test_parse_newswire_feed_date()
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
    time.sleep(2)
    print('Tests succeeded\n')
