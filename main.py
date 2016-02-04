from flask import Flask, request
from flask.views import MethodView
import hashlib
import hmac
import os
import requests
import sys

COMMENTS_TO_DELETE = ["+1", ":+1:"]


class GithubHook(MethodView):
    def post(self):
        try:
            signature = request.headers["X-Hub-Signature"]
        except Exception, e:
            print "No hub signature %s : %s" % (request.headers,
                                                request.get_json())
            return "This is sketchy, I'm leaving"

        try:
            secret = os.environ["hook_secret"]
            hash_string = hmac.new(secret.encode('utf-8'),
                                   msg=request.data,
                                   digestmod=hashlib.sha1).hexdigest()
            expected_hash = "sha1=" + hash_string
        except Exception, e:
            print "Building expected hash failed: %s" % e
            return "Building expected hash failed", 500

        if signature != expected_hash:
            return "Wrong hash, gtfo"

        request_json = request.get_json()
        if request_json.get("action") != "created":
            return "Meh, only care about new comments"

        issue = request_json.get("issue")
        if "pull_request" in issue:
            return "Ignoring pull request comment"

        comment = request_json.get("comment")
        body = comment.get("body")

        if body.strip() not in COMMENTS_TO_DELETE:
            return "Not a +1, so it's fine"

        comment_url = comment.get("url")
        auth = (os.environ["github_user"], os.environ["github_pass"])

        try:
            requests.delete(comment_url, auth=auth)
        except Exception, e:
            print "Exception: ", e

        return "42"


app = Flask(__name__)
app.add_url_rule('/', view_func=GithubHook.as_view('counter'))

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print "Usage: %s <PORT>" % sys.argv[0]
        sys.exit(1)

    app.run(port=int(sys.argv[1]), host="0.0.0.0")
