import unary_pb2_grpc  # grpc specific code gets generated into this module.
import unary_pb2  # messages get generated into this module.
import grpc

if __name__ == '__main__':
    # a channel defines how the client will connect with the gRPC server,
    # in effect, this should point at the target server.
    channel = grpc.insecure_channel("localhost:50051")
    # create a client stub using the channel
    print("calling server...")
    service_stub = unary_pb2_grpc.DisplacementServiceStub(channel)
    payload = unary_pb2.Displacement(start=unary_pb2.Point(x=0, y=12), end=unary_pb2.Point(x=12, y=14))
    # call remote RPC
    response = service_stub.computeDisplacement(payload)

    print("response = {!r}".format(response))

