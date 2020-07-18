import grpc
from response_streaming_pb2_grpc import ResponseStreamingStub
from request_streaming_pb2 import Empty
if __name__ == '__main__':
    # a channel defines how the client will connect with the gRPC server,
    # in effect, this should point at the target server.
    channel = grpc.insecure_channel("localhost:50051")
    # create a client stub using the channel
    print("calling server...")
    service_stub = ResponseStreamingStub(channel)
    # call remote RPC
    for response in service_stub.fetch_status(Empty()):
        print(response)
