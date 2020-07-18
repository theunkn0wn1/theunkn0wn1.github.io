import response_streaming_pb2_grpc
from request_streaming_pb2 import Data, OK, TIRED, UNKNOWN, STARVED, THIRSTY

import grpc  # `grpcio` PyPi package
import concurrent.futures


class ResponseStreamingServer(response_streaming_pb2_grpc.ResponseStreamingServicer):
    def fetch_status(self, request, context):
        messages = [
            Data(status=UNKNOWN, info="no record...."),
            Data(status=STARVED, info="Too long without food."),
            Data(status=THIRSTY, info="Requires watering."),
            Data(status=TIRED, info="Shutting down for the night."),
            Data(status=OK, info="OK.")
        ]
        for payload in messages:
            yield payload


if __name__ == '__main__':
    # Grpcio is implemented using threads by default...
    # Create a server object that will house the services
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    # Instantiate the unary service and use the generated method to register it with the general server
    response_streaming_pb2_grpc.add_ResponseStreamingServicer_to_server(ResponseStreamingServer(),
                                                                        server)
    # Add a port for gRPC to serve on, as gRPC is network-based.
    # in this instance, bind to all interfaces on port 50051.
    server.add_insecure_port("[::]:50051")
    # then start the server and wait for it to complete...
    server.start()
    server.wait_for_termination()
