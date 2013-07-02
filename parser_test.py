#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This is unit test code for robotexclusionrulesparser.py. For more info, see:
http://NikitaTheSpider.com/python/rerp/

"""

import sys
PY_MAJOR_VERSION = sys.version_info[0]
import time
import calendar
import socket

if PY_MAJOR_VERSION < 3:
    import robotparser
    import urllib2 as urllib_error
else:
    import urllib.robotparser as robotparser
    import urllib.error as urllib_error

import robotexclusionrulesparser


# These are enabled by default.
RUN_FETCH_TESTS = True



# -----------------------------------------------------------
# Test the classic parser (no wildcards)
# -----------------------------------------------------------
print("Running robotparser comparison test")

parser = robotexclusionrulesparser.RobotFileParserLookalike()

std_lib_parser = robotparser.RobotFileParser()

s = """
# robots.txt for http://www.example.com/

User-agent: *
Disallow:    /

User-agent: foobot
Disallow:

"""
parser.parse(s)

std_lib_parser.parse(s.split('\n'))

assert(parser.can_fetch("foobot", "/") == std_lib_parser.can_fetch("foobot", "/"))
assert(parser.can_fetch("Foobot", "/bar.html") == std_lib_parser.can_fetch("Foobot", "/bar.html"))
assert(parser.can_fetch("SomeOtherBot", "/") == std_lib_parser.can_fetch("SomeOtherBot", "/"))
assert(parser.can_fetch("SomeOtherBot", "/blahblahblah") == std_lib_parser.can_fetch("SomeOtherBot", "/blahblahblah"))

print("Passed.")

# I'm done with this.
del std_lib_parser

# The remainder of the tests use the standard RobotExclusionRulesParser()
# rather than the RobotParserLookalike(). They could just as well
# use RobotParserLookalike(), though, because its methods and attributes are 
# a superset of RobotExclusionRulesParser()

parser = robotexclusionrulesparser.RobotExclusionRulesParser()

# -----------------------------------------------------------
# Test the classic parser (no wildcards)
# -----------------------------------------------------------
print("Running Classic (MK1994/96) syntax test...")

s = """
# robots.txt for http://www.example.com/

# In the classic syntax, * is treated literally, not as a wildcard. 
# A Webmaster might expect the line below to disallow everything, but
# that's not how it works.
User-agent: foobot
Disallow: *

User-agent: barbot
Disallow: /private/*
"""
parser.parse(s)

# Note how results are completely opposite for the different syntaxes.
assert(parser.is_allowed("foobot", "/something.html", robotexclusionrulesparser.MK1996) == True)
assert(parser.is_allowed("foobot", "/something.html", robotexclusionrulesparser.GYM2008) == False)
assert(parser.is_allowed("barbot", "/private/xyz.html", robotexclusionrulesparser.MK1996) == True)
assert(parser.is_allowed("barbot", "/private/xyz.html", robotexclusionrulesparser.GYM2008) == False)

print("Passed.")


# The remainder of the tests use the default parser which accepts the 
# GYM2008 (Google-Yahoo-Microsoft 2008) syntax described here:
# http://www.google.com/support/webmasters/bin/answer.py?answer=40367
# Announced here:
# http://googlewebmastercentral.blogspot.com/2008/06/improving-on-robots-exclusion-protocol.html
# http://ysearchblog.com/2008/06/03/one-standard-fits-all-robots-exclusion-protocol-for-yahoo-google-and-microsoft/
# http://blogs.msdn.com/webmaster/archive/2008/06/03/robots-exclusion-protocol-joining-together-to-provide-better-documentation.aspx
# mk1994 = the 1994 robots.txt draft spec (http://www.robotstxt.org/orig.html)
# mk1996 = the 1996 robots.txt draft spec (http://www.robotstxt.org/norobots-rfc.txt)


# -----------------------------------------------------------
# This is the example from mk1994
# -----------------------------------------------------------
print("Running MK1994 example test...")
s = """
# robots.txt for http://www.example.com/

User-agent: *
Disallow: /cyberworld/map/ # This is an infinite virtual URL space
Disallow: /tmp/ # these will soon disappear
Disallow: /foo.html
"""
parser.parse(s)

assert(parser.is_allowed("CrunchyFrogBot", "/") == True)
assert(parser.is_allowed("CrunchyFrogBot", "/foo.html") == False)
assert(parser.is_allowed("CrunchyFrogBot", "/foo.htm") == True)
assert(parser.is_allowed("CrunchyFrogBot", "/foo.shtml") == True)
assert(parser.is_allowed("CrunchyFrogBot", "/foo.htmlx") == False)
assert(parser.is_allowed("CrunchyFrogBot", "/cyberworld/index.html") == True)
assert(parser.is_allowed("CrunchyFrogBot", "/tmp/foo.html") == False)
# Since it is the caller's responsibility to make sure the host name 
# matches, the parser disallows foo.html regardless of what I pass for 
# host name and protocol.
assert(parser.is_allowed("CrunchyFrogBot", "http://example.com/foo.html") == False)
assert(parser.is_allowed("CrunchyFrogBot", "http://www.example.com/foo.html") == False)
assert(parser.is_allowed("CrunchyFrogBot", "http://www.example.org/foo.html") == False)
assert(parser.is_allowed("CrunchyFrogBot", "https://www.example.org/foo.html") == False)
assert(parser.is_allowed("CrunchyFrogBot", "ftp://example.net/foo.html") == False)

print("Passed.")

# -----------------------------------------------------------
# This is the example A from MK1996
# -----------------------------------------------------------
print("Running Allows based on MK1996 example A test...")
s = """
# robots.txt for http://www.example.com/

User-agent: 1bot
Allow: /tmp
Disallow: /

User-agent: 2bot
Allow: /tmp/
Disallow: /

User-agent: 3bot
Allow: /a%3cd.html
Disallow: /

User-agent: 4bot
Allow: /a%3Cd.html
Disallow: /

User-agent: 5bot
Allow: /a%2fb.html
Disallow: /

User-agent: 6bot
Allow: /a/b.html
Disallow: /

User-agent: 7bot
Allow: /%7ejoe/index.html
Disallow: /

User-agent: 8bot
Allow: /~joe/index.html
Disallow: /


"""
parser.parse(s)

assert(parser.is_allowed("1bot", "/tmp") == True)
assert(parser.is_allowed("1bot", "/tmp.html") == True)
assert(parser.is_allowed("1bot", "/tmp/a.html") == True)
assert(parser.is_allowed("2bot", "/tmp") == False)
assert(parser.is_allowed("2bot", "/tmp/") == True)
assert(parser.is_allowed("2bot", "/tmp/a.html") == True)
assert(parser.is_allowed("3bot", "/a%3cd.html") == True)
assert(parser.is_allowed("3bot", "/a%3Cd.html") == True)
assert(parser.is_allowed("4bot", "/a%3cd.html") == True)
assert(parser.is_allowed("4bot", "/a%3Cd.html") == True)
assert(parser.is_allowed("5bot", "/a%2fb.html") == True)
assert(parser.is_allowed("5bot", "/a/b.html") == False)
assert(parser.is_allowed("6bot", "/a%2fb.html") == False)
assert(parser.is_allowed("6bot", "/a/b.html") == True)
assert(parser.is_allowed("7bot", "/~joe/index.html") == True)
assert(parser.is_allowed("8bot", "/%7Ejoe/index.html") == True)

print("Passed.")



# -----------------------------------------------------------
# This is the example B from MK1996 with the domain 
# changed to example.org 
# -----------------------------------------------------------
print("Running MK1996 example B test...")
s = """
# /robots.txt for http://www.example.org/
# comments to webmaster@example.org

User-agent: unhipbot
Disallow: /

User-agent: webcrawler
User-agent: excite
Disallow:

User-agent: *
Disallow: /org/plans.html
Allow: /org/
Allow: /serv
Allow: /~mak
Disallow: /

"""
parser.parse(s)

assert(parser.is_allowed("unhipbot", "http://www.example.org/") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/") == True)
assert(parser.is_allowed("excite", "http://www.example.org/") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/") == False)
assert(parser.is_allowed("unhipbot", "http://www.example.org/index.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/index.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/index.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/index.html") == False)
# Test for robots.txt dropped -- I presume that no one will fetch robots.txt
# to see if they're allowed to fetch robots.txt. Sheesh...
#         assert(parser.is_allowed("unhipbot", "http://www.example.org/robots.txt") == True)
#         assert(parser.is_allowed("webcrawler", "http://www.example.org/robots.txt") == True)
#         assert(parser.is_allowed("excite", "http://www.example.org/robots.txt") == True)
#         assert(parser.is_allowed("OtherBot", "http://www.example.org/robots.txt") == True)
assert(parser.is_allowed("unhipbot", "http://www.example.org/server.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/server.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/server.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/server.html") == True)
assert(parser.is_allowed("unhipbot", "http://www.example.org/services/fast.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/services/fast.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/services/fast.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/services/fast.html") == True)
assert(parser.is_allowed("unhipbot", "http://www.example.org/services/slow.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/services/slow.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/services/slow.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/services/slow.html") == True)
assert(parser.is_allowed("unhipbot", "http://www.example.org/orgo.gif") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/orgo.gif") == True)
assert(parser.is_allowed("excite", "http://www.example.org/orgo.gif") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/orgo.gif") == False)
assert(parser.is_allowed("unhipbot", "http://www.example.org/org/about.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/org/about.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/org/about.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/org/about.html") == True)
assert(parser.is_allowed("unhipbot", "http://www.example.org/org/plans.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/org/plans.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/org/plans.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/org/plans.html") == False)
assert(parser.is_allowed("unhipbot", "http://www.example.org/%7Ejim/jim.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/%7Ejim/jim.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/%7Ejim/jim.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/%7Ejim/jim.html") == False)
assert(parser.is_allowed("unhipbot", "http://www.example.org/%7Emak/mak.html") == False)
assert(parser.is_allowed("webcrawler", "http://www.example.org/%7Emak/mak.html") == True)
assert(parser.is_allowed("excite", "http://www.example.org/%7Emak/mak.html") == True)
assert(parser.is_allowed("OtherBot", "http://www.example.org/%7Emak/mak.html") == True)

print("Passed.")



# -----------------------------------------------------------
# Test a blank (or non-existent) robots.txt
# -----------------------------------------------------------
print("Running Blank test...")
s = ""

parser.parse(s)

assert(parser.is_allowed("foobot", "/") == True)
assert(parser.is_allowed("anybot", "/foo.html") == True)
assert(parser.is_allowed("anybot", "/TheGoldenAgeOfBallooning/") == True)
assert(parser.is_allowed("anybot", "/TheGoldenAgeOfBallooning/claret.html") == True)

print("Passed.")

# -----------------------------------------------------------
# Test the parser's generosity
# -----------------------------------------------------------
print("Running generosity test...")

utf8_byte_order_mark = chr(0xef) + chr(0xbb) + chr(0xbf)
s = """%sUSERAGENT: FOOBOT
%suser-agent:%s%s%sbarbot%s
disallow: /foo/
""" % (utf8_byte_order_mark, '\t', '\t', '\t', '\t', chr(0xb))
parser.parse(s)

assert(parser.is_allowed("foobot", "/") == True)
assert(parser.is_allowed("foobot", "/foo/bar.html") == False)
assert(parser.is_allowed("AnotherBot", "/foo/bar.html") == True)
assert(parser.is_allowed("Foobot Version 1.0", "/foo/bar.html") == False)
assert(parser.is_allowed("Mozilla/5.0 (compatible; Foobot/2.1)", "/foo/bar.html") == False)
assert(parser.is_allowed("barbot", "/foo/bar.html") == False)
assert(parser.is_allowed("barbot", "/tmp/") == True)

print("Passed.")


# -----------------------------------------------------------
# Test the parser's ability to handle non-ASCII
# -----------------------------------------------------------
print("Running Non-ASCII test...")
s = """# robots.txt for http://www.example.com/

UserAgent: Jävla-Foobot
Disallow: /

UserAgent: \u041b\u044c\u0432\u0456\u0432-bot
Disallow: /totalitarianism/

"""
if PY_MAJOR_VERSION < 3:
    s = s.decode("utf-8")
parser.parse(s)

user_agent = "jävla-fanbot"
if PY_MAJOR_VERSION < 3:
    user_agent = user_agent.decode("utf-8")
assert(parser.is_allowed(user_agent, "/foo/bar.html") == True)
assert(parser.is_allowed(user_agent.replace("fan", "foo"), "/foo/bar.html") == False)
assert(parser.is_allowed("foobot", "/") == True)
assert(parser.is_allowed("Mozilla/5.0 (compatible; \u041b\u044c\u0432\u0456\u0432-bot/1.1)", "/") == True)
assert(parser.is_allowed("Mozilla/5.0 (compatible; \u041b\u044c\u0432\u0456\u0432-bot/1.1)", "/totalitarianism/foo.htm") == False)

print("Passed.")



# -----------------------------------------------------------
# Test the implicit allow rule
# -----------------------------------------------------------
print("Running Implicit allow test...")
s = """
# robots.txt for http://www.example.com/

User-agent: *
Disallow:    /

User-agent: foobot
Disallow:

"""
parser.parse(s)

assert(parser.is_allowed("foobot", "/") == True)
assert(parser.is_allowed("foobot", "/bar.html") == True)
assert(parser.is_allowed("SomeOtherBot", "/") == False)
assert(parser.is_allowed("SomeOtherBot", "/blahblahblah") == False)

print("Passed.")



# -----------------------------------------------------------
# Test the GYM2008-specific syntax (wildcards)
# -----------------------------------------------------------
print("Running GYM2008 wildcards test...")
s = """
# robots.txt for http://www.example.com/

User-agent: Rule1TestBot
Disallow:  /foo*

User-agent: Rule2TestBot
Disallow:  /foo*/bar.html

# Disallows anything containing the letter m!
User-agent: Rule3TestBot
Disallow:  *m

User-agent: Rule4TestBot
Allow:  /foo/bar.html
Disallow: *

User-agent: Rule5TestBot
Disallow:  /foo*/*bar.html

User-agent: Rule6TestBot
Allow:  /foo$
Disallow:  /foo

"""
parser.parse(s)

assert(parser.is_allowed("Rule1TestBot", "/fo.html") == True)
assert(parser.is_allowed("Rule1TestBot", "/foo.html") == False) 
assert(parser.is_allowed("Rule1TestBot", "/food") == False)
assert(parser.is_allowed("Rule1TestBot", "/foo/bar.html") == False)

assert(parser.is_allowed("Rule2TestBot", "/fo.html") == True)
assert(parser.is_allowed("Rule2TestBot", "/foo/bar.html") == False) 
assert(parser.is_allowed("Rule2TestBot", "/food/bar.html") == False) 
assert(parser.is_allowed("Rule2TestBot", "/foo/a/b/c/x/y/z/bar.html") == False) 
assert(parser.is_allowed("Rule2TestBot", "/food/xyz.html") == True) 

assert(parser.is_allowed("Rule3TestBot", "/foo.htm") == False) 
assert(parser.is_allowed("Rule3TestBot", "/foo.html") == False) 
assert(parser.is_allowed("Rule3TestBot", "/foo") == True)
assert(parser.is_allowed("Rule3TestBot", "/foom") == False)
assert(parser.is_allowed("Rule3TestBot", "/moo") == False)
assert(parser.is_allowed("Rule3TestBot", "/foo/bar.html") == False)
assert(parser.is_allowed("Rule3TestBot", "/foo/bar.txt") == True)

assert(parser.is_allowed("Rule4TestBot", "/fo.html") == False)
assert(parser.is_allowed("Rule4TestBot", "/foo.html") == False) 
assert(parser.is_allowed("Rule4TestBot", "/foo") == False)
assert(parser.is_allowed("Rule4TestBot", "/foo/bar.html") == True)
assert(parser.is_allowed("Rule4TestBot", "/foo/bar.txt") == False)

assert(parser.is_allowed("Rule5TestBot", "/foo/bar.html") == False)
assert(parser.is_allowed("Rule5TestBot", "/food/rebar.html") == False)
assert(parser.is_allowed("Rule5TestBot", "/food/rebarf.html") == True)
assert(parser.is_allowed("Rule5TestBot", "/foo/a/b/c/rebar.html") == False)
assert(parser.is_allowed("Rule5TestBot", "/foo/a/b/c/bar.html") == False)

assert(parser.is_allowed("Rule6TestBot", "/foo") == True)
assert(parser.is_allowed("Rule6TestBot", "/foo/") == False)
assert(parser.is_allowed("Rule6TestBot", "/foo/bar.html") == False)
assert(parser.is_allowed("Rule6TestBot", "/fooey") == False)

print("Passed.")



# -----------------------------------------------------------
# Test the GYM2008-specific syntax (crawl-delays and sitemap)
# -----------------------------------------------------------

print("Running GYM2008 Crawl-delay and sitemap test...")
s = """
# robots.txt for http://www.example.com/

User-agent: Foobot
Disallow:  *
Crawl-Delay: 5

Sitemap: http://www.example.org/banana.xml

User-agent: Somebot
Allow: /foo.html
Crawl-Delay: .3
Allow: /bar.html
Disallow: *

User-agent: AnotherBot
Disallow:  *
Sitemap: http://www.example.net/sitemap.xml
Sitemap: http://www.example.com/another_sitemap.xml

User-agent: CamelBot
Disallow: /foo.html
Crawl-Delay: go away!

"""
parser.parse(s)

assert(parser.is_allowed("Foobot", "/foo.html") == False)
assert(parser.get_crawl_delay("Foobot") == 5)
assert(parser.get_crawl_delay("Blahbot") == None)
assert(parser.is_allowed("Somebot", "/foo.html") == True)
assert(parser.is_allowed("Somebot", "/bar.html") == True)
assert(parser.is_allowed("Somebot", "/x.html") == False)
assert(parser.get_crawl_delay("Somebot") == .3)
assert(parser.is_allowed("AnotherBot", "/foo.html") == False)
assert(parser.sitemaps[1] == "http://www.example.net/sitemap.xml")
assert(parser.get_crawl_delay("CamelBot") == None)

print("Passed.")


# -----------------------------------------------------------
# Test handling of bad syntax
# -----------------------------------------------------------
print("Running Bad Syntax test...")

s = """
# robots.txt for http://www.example.com/

# This is nonsense; UA most come first.
Disallow: /
User-agent: *

# With apologies to Dr. Seuss, this syntax won't act as the author expects. 
# It will only match UA strings that contain "onebot twobot greenbot bluebot".
# To match multiple UAs to a single rule, use multiple "User-agent:" lines.
User-agent: onebot twobot greenbot bluebot
Disallow: /

# Blank lines indicate an end-of-record so the first UA listed here is ignored.
User-agent: OneTwoFiveThreeSirBot

# Note from Webmaster: add new user-agents below:
User-agent: WotBehindTheRabbitBot
User-agent: ItIsTheRabbitBot
Disallow: /HolyHandGrenade/

"""
parser.parse(s)

assert(parser.is_allowed("onebot", "/") == True)
assert(parser.is_allowed("onebot", "/foo/bar.html") == True)
assert(parser.is_allowed("bluebot", "/") == True)
assert(parser.is_allowed("bluebot", "/foo/bar.html") == True)
assert(parser.is_allowed("OneTwoFiveThreeSirBot", "/HolyHandGrenade/Antioch.html") == True)
assert(parser.is_allowed("WotBehindTheRabbitBot", "/HolyHandGrenade/Antioch.html") == False)

print("Passed.")


# -----------------------------------------------------------
# Test case insensitivity
# -----------------------------------------------------------
print("Running Case Insensitivity test...")

s = """
# robots.txt for http://www.example.com/

User-agent: Foobot
Disallow: /

"""
parser.parse(s)

assert(parser.is_allowed("Foobot", "/") == False)
assert(parser.is_allowed("FOOBOT", "/") == False)
assert(parser.is_allowed("FoOBoT", "/") == False)
assert(parser.is_allowed("foobot", "/") == False)

print("Passed.")



if RUN_FETCH_TESTS:
    # -----------------------------------------------------------
    # Test the parser's ability to fetch and decode files from the Net
    # -----------------------------------------------------------
    print("Testing network fetching. This may take a moment...")


    print("Running non-existent URL handling test...")
    try:
        parser.fetch("http://SomeLongUrlThatDoesntExistBlahBlahBlah.qwertiop")
    except urllib_error.URLError:
        # Expected
        pass

    print("Running Fetch and decode (ISO-8859-1) test...")

    parser.fetch("http://NikitaTheSpider.com/python/rerp/robots.iso-8859-1.txt")
    
    user_agent = "BättreBot"
    if PY_MAJOR_VERSION < 3:
        user_agent = user_agent.decode("utf-8")

    assert(parser.is_allowed(user_agent, "/stuff") == False)
    assert(parser.is_allowed(user_agent, "/index.html") == True)

    user_agent = "BästaBot"
    if PY_MAJOR_VERSION < 3:
        user_agent = user_agent.decode("utf-8")
    
    assert(parser.is_allowed(user_agent, "/stuff") == True)
    assert(parser.is_allowed(user_agent, "/index.html") == False)
    assert(parser.is_allowed("foobot", "/stuff") == True)
    assert(parser.is_allowed("foobot", "/index.html") == True)

    print("Passed.")


    print("Running Fetch and decode (UTF-8) test...")
    
    parser.fetch("http://NikitaTheSpider.com/python/rerp/robots.utf-8.txt")
    user_agent = "BättreBot"
    if PY_MAJOR_VERSION < 3:
        user_agent = user_agent.decode("utf-8")
        
    parser.is_allowed(user_agent, "/stuff")
        
    assert(parser.is_allowed(user_agent, "/stuff") == False)
    assert(parser.is_allowed(user_agent, "/index.html") == True)
    user_agent = "BästaBot"
    if PY_MAJOR_VERSION < 3:
        user_agent = user_agent.decode("utf-8")
    assert(parser.is_allowed(user_agent, "/stuff") == True)
    assert(parser.is_allowed(user_agent, "/index.html") == False)
    assert(parser.is_allowed("foobot", "/stuff") == True)
    assert(parser.is_allowed("foobot", "/index.html") == True)
    
    print("Passed.")



    print("Running 404 handling test...")

    parser.fetch("http://NikitaTheSpider.com/ThisDirectoryDoesNotExist/robots.txt")
    assert(parser.is_allowed("foobot", "/") == True)
    assert(parser.is_allowed("javla-foobot", "/stuff") == True)
    assert(parser.is_allowed("anybot", "/TotallySecretStuff") == True)

    print("Passed.")

    # -----------------------------------------------------------
    # Test the parser's ability to handle non-200 response codes
    # -----------------------------------------------------------
    print("Running 401 test...")

    # Fetching this file returns a 401
    parser.fetch("http://NikitaTheSpider.com/python/rerp/robots.401.txt")
    assert(parser.is_allowed("NigelBot", "/") == False)
    assert(parser.is_allowed("StigBot", "/foo/bar.html") == False)
    assert(parser.is_allowed("BruceBruceBruceBot", "/index.html") == False)

    print("Passed.")


    print("Running 403 test...")

    # Fetching this file returns a 403
    parser.fetch("http://NikitaTheSpider.com/python/rerp/robots.403.txt")
    assert(parser.is_allowed("NigelBot", "/") == False)
    assert(parser.is_allowed("StigBot", "/foo/bar.html") == False)
    assert(parser.is_allowed("BruceBruceBruceBot", "/index.html") == False)

    print("Passed.")


    print("Running 404 test...")

    # Fetching this file returns a 404
    parser.fetch("http://NikitaTheSpider.com/python/rerp/robots.404.txt")
    assert(parser.is_allowed("NigelBot", "/") == True)
    assert(parser.is_allowed("StigBot", "/foo/bar.html") == True)
    assert(parser.is_allowed("BruceBruceBruceBot", "/index.html") == True)
    
    print("Passed.")
    

    print("Running 500 test...")

    # Fetching this file returns a 500
    try:
        parser.fetch("http://NikitaTheSpider.com/python/rerp/robots.500.txt")
    except urllib_error.URLError:
        # This is exactly what's supposed to happen.
        pass
    
    print("Passed.")

    # -----------------------------------------------------------
    # Test the parser's expiration features
    # -----------------------------------------------------------
    print("Running local time test...")

    # Create a fresh parser to (re)set the expiration date. I test to see if 
    # the dates are accurate to +/-1 minute. If your local clock is off by 
    # more than that, these tests will fail.

    parser = robotexclusionrulesparser.RobotExclusionRulesParser()
    localtime = time.mktime(time.localtime())
    assert((parser.expiration_date > localtime + robotexclusionrulesparser.SEVEN_DAYS - 60) and
           (parser.expiration_date < localtime + robotexclusionrulesparser.SEVEN_DAYS + 60))

    print("Passed.")


    print("Running UTC test...")

    parser = robotexclusionrulesparser.RobotExclusionRulesParser()
    parser.use_local_time = False
    utc = calendar.timegm(time.gmtime())
    assert((parser.expiration_date > utc + robotexclusionrulesparser.SEVEN_DAYS - 60) and
           (parser.expiration_date < utc + robotexclusionrulesparser.SEVEN_DAYS + 60))

    print("Passed.")


    # -----------------------------------------------------------
    # Test the fetch timeout, if possible. It's only supported 
    # in Python >= 2.6.
    # -----------------------------------------------------------
    major, minor = sys.version_info[:2]

    if (major > 2) or (minor > 5):
        print("Running timeout test 1...")
        try:
            parser.fetch("http://NikitaTheSpider.com/python/rerp/sleep3.php", 0.5)
        except socket.timeout:
            # This is exactly what's supposed to happen under Python 3.
            pass

        except urllib_error.URLError:
            # This is exactly what's supposed to happen under Python 2.
            pass

        print("Passed.")


        print("Running timeout test 2...")
        parser.fetch("http://NikitaTheSpider.com/python/rerp/sleep3.php", 5)

        print("Passed.")
    else:
        print("Skipping fetch timeout tests due to Python version <= 2.6.")

