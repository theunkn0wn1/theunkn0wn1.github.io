# generated code into a submodule, so its easier to manage.
from generated import unary_pb2_grpc  # grpc specific code gets generated into this module.
from generated import unary_pb2  # messages get generated into this module.
import grpc
import concurrent.futures


class DisplacementService(unary_pb2_grpc.DisplacementServiceServicer):
    # implement unary RPC from the ABC protoc generated.
    def computeDisplacement(self, request, context):
        # compute delta
        dx = (request.end.x - request.start.x) ** 2
        dy = (request.end.y - request.start.y) ** 2
        # return net displacement sqrt(dx+dy)
        return unary_pb2.DisplacementResponse(distance=(dx + dy) ** 0.5)


if __name__ == '__main__':
    # Grpcio is implemented using threads...
    # Create a server object that will house the services
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))

    # Instantiate the unary service and use the generated method to register it with the general server
    unary_pb2_grpc.add_DisplacementServiceServicer_to_server(DisplacementService(), server)

    # Add a port for gRPC to serve on, as gRPC is network-based.
    # in this instance, bind to all interfaces on port 50051.
    server.add_insecure_port("[::]:50051")

    # then start the server and wait for it to complete...
    server.start()
    server.wait_for_termination()
