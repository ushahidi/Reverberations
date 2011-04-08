#!/usr/bin/env python
#
# Copyright 2009 Facebook
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import reverb
import json

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class TweetHandler(tornado.web.RequestHandler):
    def get(self):
        id =  self.get_argument("id")
        tree = reverb.rank(int(id))
        results = []
        for tweet in tree:
           results.append({ "twid":tweet.twid,"lvl":tweet.lvl,"rtusr":tweet.rtusr,"user_id": tweet.user.id,"ts":str(tweet.ts) ,"rank":tweet.rank   })
        self.write(json.dumps(results))


def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        (r"/tweet", TweetHandler),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
