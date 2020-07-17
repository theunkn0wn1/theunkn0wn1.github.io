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

This post does **not** aim to cover the design methodology of gRPC nor serve as an introduction,
 for that i suggest [further reading here first.](https://grpc.io/docs/what-is-grpc/introduction/) 
 
This post aims to demonstrate how to use gRPC in a python project, utilizing the [`grpcio`](https://pypi.org/project/grpcio/)
package, and assumes familiarity with the `protobuf` IDL.
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
Here is the client-side code for the above:
```python

```

and the server-side code:
```python

```

# Client -> Server "request-streaming" RPC
A "request-streaming" RPC is one in which the client streams many objects to the server, where the server only sends back a single object once the client is done.
This can be useful for 