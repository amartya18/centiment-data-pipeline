from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

from lib.tweets_predictor import TweetsPredictor


tweets_predictor = TweetsPredictor()

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# main
def main(tweet):
    tweets_predictor.predict_bot_tweets(tweet)

with SimpleXMLRPCServer(("127.0.0.1", 5001),
        requestHandler=RequestHandler, allow_none=True) as server:
    server.register_introspection_functions()

    server.register_function(main, "process_tweet")

    server.serve_forever()
