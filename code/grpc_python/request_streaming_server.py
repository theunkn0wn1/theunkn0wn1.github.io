import request_streaming_pb2_grpc
import request_streaming_pb2
import grpc  # `grpcio` PyPi package
import concurrent.futures


class RequestStreamingServer(request_streaming_pb2_grpc.RequestStreamingServicer):
    def stream_state(self, request_iterator, context):
        for payload in request_iterator:
            print("payload Recv: status: {!r} | info: {!r}".format(payload.status, payload.info))
        return request_streaming_pb2.Empty()


if __name__ == '__main__':
    # Grpcio is implemented using threads by default...
    # Create a server object that will house the services
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    # Instantiate the unary service and use the generated method to register it with the general server
    request_streaming_pb2_grpc.add_RequestStreamingServicer_to_server(RequestStreamingServer(), server)
    # Add a port for gRPC to serve on, as gRPC is network-based.
    # in this instance, bind to all interfaces on port 50051.
    server.add_insecure_port("[::]:50051")
    # then start the server and wait for it to complete...
    server.start()
    server.wait_for_termination()
