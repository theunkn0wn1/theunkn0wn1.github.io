---
layout: post
title:  "gRPC with python"
date:   2020-07-17 11:00:00 -0700
categories: "Python"
author: "Joshua Salzedo"
---

[gRPC](https://grpc.io/) is a open-source [Remote-Procedural-Call](https://en.wikipedia.org/wiki/Remote_procedure_call)
 framework which aims to facilitate a microservice architecture in a language-agnostic fashion. 

One of its key features is the ability to call functions on remote systems as if they were local functions in-memory.
It is relatively easy to call a function running on a Java server from a Python client or vice versa.

It has client/server  implementations in many languages, and is useful in a wide range of applications.

This post does **not** aim to cover the design methodology of gRPC, for that i suggest [further reading here first.](https://grpc.io/docs/what-is-grpc/introduction/) 
 
This post aims to demonstrate how to use gRPC in a python project, utilizing the [`grpcio`](https://pypi.org/project/grpcio/)
package, and assumes familiarity with the `protobuf` IDL and, optionally, familiarity with using gRPC in other languages.

The main reason I wrote this guide is because i found the classical [RouteGuide](https://grpc.io/docs/languages/python/basics/) examples to contain far 
too much hand-waving which made it difficult to follow for a beginner. 

All code examples can be found on my github repository [here](https://github.com/theunkn0wn1/theunkn0wn1.github.io).

# Services
A `service` provides functions that may be called, thus a `service` block defines the interface of some RPC server.

See subsequent sections for the different RPC types that may be defined in a service.
```proto
syntax = "proto3";
package my_package;
service SomeService{
    // contents of service go here
}
```

# Unary RPC
A Unary RPC is the simplest form, its roughly equivalent to a single function call. One call -> one result.

The syntax for a unary rpc is `rpc name(ArgumentType) returns (return_type)`
 - `name` is the function's name, `ArgumentTYpe` is the type of the object it expects to be called with, and the `return_type` defines, well, what kind of object this RPC returns.
 - all RPC implementations MUST return an protobuf object, even if that something is a message object with no fields. 
    - (Returning `None` is an error.)

```proto
syntax = "proto3";
package my_package;
// coordinate pair
message Point{
    int32 x = 1;
    int32 y = 2;
}
// query message type
message Displacement{
    Point start = 1;
    Point end = 2;
}
// Response message type
message DisplacementResponse{
    float distance = 1;
}
// RPC definitions
service DisplacementService{
    rpc computeDisplacement (Displacement) returns (DisplacementResponse);
}
```

Once the python code has been generated (see [generating below.](#generating)), two files will be created in the output directory per input `.proto` file.

| Suffix        | Description                                                           |
| _pb2.py       | Contains message and enum classes                                     |
| _pb2_grpc.py  | Contains gRPC specific code, such as Service stubs and base classes   |

## server side implementation
The server side implementation is more involved than the client, as this side actually implements the logic the RPC defines.

I recommend using a development environment that allows for autocompletion and generation of method overrides.

```python
import unary_pb2_grpc  # grpc specific code gets generated into this module.
import unary_pb2  # messages & enums get generated into this module.

class DisplacementService(unary_pb2_grpc.DisplacementServiceServicer):
    """ Implementation of the Displacement Service """
    # Implement unary RPC from the ABC protoc generated.
    def computeDisplacement(self, request, context):
        # compute delta
        dx = (request.end.x - request.start.x) ** 2
        dy = (request.end.y - request.start.y) ** 2
        # return net displacement sqrt(dx**2+dy**2)
        return unary_pb2.DisplacementResponse(distance=(dx + dy) ** 0.5)
```
Implementing the RPC is achieved by subclassing the generated `Servicer` class and implementing its methods.
- the `request` object passed to the method is the same object the client passed as the arguments to the call.
- the `context` object allows the server to get some general context from the query, as well as to report failures.
     - the server can either raise an exception, or set the code & details using `context.set_code` and `context.set_details`

Once implemented, it just needs to be tied into the gRPC server object, see [Common Server Steps](#common-server-steps) below.
```python
import grpc
context: grpc.ServicerContext
# this code obviously won't run without an actual context object, this code block is included for 
# completeness.
context.set_details("something went horribly wrong")
context.set_code(grpc.StatusCode.FAILED_PRECONDITION)
```

## Client side implementation
Implementing this on the client side is straight-forward. 
Instantiate the client stub (see [Common Client Steps](#common-client-steps) below) and call the relevant method on the stub.
```python
import unary_pb2_grpc  # grpc specific code gets generated into this module.
import unary_pb2  # messages get generated into this module.

...

# create a client stub using the channel
print("calling server...")
service_stub = unary_pb2_grpc.DisplacementServiceStub(channel)
payload = unary_pb2.Displacement(start=unary_pb2.Point(x=0, y=12), end=unary_pb2.Point(x=12, y=14))
# call remote RPC
response = service_stub.computeDisplacement(payload)
```



# Client -> Server "request-streaming" RPC
A "request-streaming" RPC is one in which the client streams many objects to the server as a stream,
 where the server only sends back a single object once the client is done.
This can be useful for sending a large number of objects to a server.
 - Note:: client streams are limited only by how fast the client can stream objects, not by the rate in which the server processes them. 

Streams are specified by placing the `stream` keyword before the RPC argument.
```proto
syntax = "proto3";
package my_package;

enum Status {
    UNKNOWN = 0;
    OK = 1;
    THIRSTY = 2;
    STARVED = 3;
    TIRED = 4;
};
message Data {
    Status status = 1;
    string info = 2;
}
// empty message
message Empty{

}

service RequestStreaming {
    rpc stream_state(stream Data) returns (Empty);
}
```
## Server side
Implementing a request-streamed RPC is straight-forward, the request implements the interface of `Iterator` thus can be `for` looped over.
```python
import request_streaming_pb2
import request_streaming_pb2_grpc

class RequestStreamingServer(request_streaming_pb2_grpc.RequestStreamingServicer):
    def stream_state(self, request_iterator, context):
        for payload in request_iterator:
            print("payload Recv: status: {!r} | info: {!r}".format(payload.status, payload.info))
        # don't forget to return something, otherwise an exception WILL be raised
        return request_streaming_pb2.Empty()

```

## Client side
Implementing a request-streaming RPC from the client side requires producing an `Iterator`, this can be 
achieved by calling `iter(...)` on an [`abc.collections.Iterable`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Iterable) object such as a
 - [`abc.collections.Collection`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Collection)
 - [`abc.collections.Generator`](https://docs.python.org/3/library/collections.abc.html#collections.abc.Generator)
 
In the following example, `iter` is called on a `list` object, where `list` implements `abc.collections.Collection` and thus `abc.collections.Iterable`.
 - Most primitive python containers implement `abc.collections.Collection`.
 
```python
import grpc

from request_streaming_pb2 import Data, STARVED, THIRSTY, TIRED, UNKNOWN, OK
from request_streaming_pb2_grpc import RequestStreamingStub
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


```

# Generating
Generating python client/server code requires using the [`grpcio_tools`](https://pypi.org/project/grpcio-tools/) python package.
```bash
$ python3 -m grpc_tools.protoc /path/to/*.proto --python_out=. --grpc_python_out=. -I=/path/to/protos
```
- Note:: this plugin tends to generate python modules that expect to be in the project's root folder. See [Related github threads...](https://github.com/protocolbuffers/protobuf/pull/7470)

# Common Server Steps
When creating a gRPC server, there are a couple boilerplate tasks that need to be done.
1. instantiate a `grpc.server` object.
2. add ports to serve on.
2. instantiate the `Servicer` classes for each gRPC service this server implements.
3. register the `Servicer` instances against the server using their generated `add_{{name}}Servicer_to_server`.
4. start the server.
the below snippet uses the [Unary Service example](#unary-rpc)/
```python
import unary_pb2_grpc  # grpc specific code gets generated into this module.
import unary_pb2  # messages get generated into this module.
import grpc  # `grpcio` PyPi package
import concurrent.futures
if __name__ == '__main__':
    # Grpcio is implemented using threads by default...
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
```

# Common Client Steps
working with gRPC as a client tends to be a bit simpler.

To act as a client:
1. Import relevant generated stub class definitions.
2. Define a `channel` object pointing at the gRPC server.
3. Instantiate relevant stubs with the `channel` object.
