from request_streaming_pb2 import Data, STARVED, THIRSTY, TIRED, UNKNOWN, OK
from request_streaming_pb2_grpc import RequestStreamingStub
import grpc
messages = [
    Data(status=UNKNOWN, info="no record...."),
    Data(status=STARVED, info="Too long without food."),
    Data(status=THIRSTY, info="Requires watering."),
    Data(status=TIRED, info="Shutting down for the night."),
    Data(status=OK, info="OK.")
]
if __name__ == '__main__':
    # a channel defines how the client will connect with the gRPC server,
    # in effect, this should point at the target server.
    channel = grpc.insecure_channel("localhost:50051")
    # create a client stub using the channel
    print("calling server...")
    service_stub = RequestStreamingStub(channel)
    # call remote RPC
    response = service_stub.stream_state(iter(messages))

