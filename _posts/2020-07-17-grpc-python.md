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
package, covering the basics of the `protobuf` IDL and each of the RPC types. 
The main reason I wrote this guide is because i found the classical [RouteGuide](https://grpc.io/docs/languages/python/basics/) examples to contain far 
too much hand-waving which made it difficult to follow for a beginner. 

# Part 1: `protobuf` objects
To be able to use gRPC, one first must write `protobuf` definitions for the objects and services. 
These `protobuf` definitions are language neutral and used to generate the client/service implementations.
A language reference for `protobuf` can be found [here.](https://developers.google.com/protocol-buffers/docs/overview)

The two fields that will be at the top of any protobuf file will be the `syntax` and the `package`.
the `package` field doesn't do much in the python implementation, however is VERY important for other languages such as `java`, `rust`, and `golang`.
 - the `package` name should be kept short and simple, without any nesting unless you know what you are doing, otherwise it will be a headache to fix later.
 - For this document, all protobuf files will use the `proto3` syntax and feature set. 
```proto
// must define the syntax or protoc will reject the file
syntax = "proto3"; 
// must define a package or protoc will reject the file.
// the package determines the name the generated implementations can be 
// imported under in many languages (Excluding python)
package my_package;
```

## Object definitions
Defining objects requires knowing three things:
 - the data type of each attribute, protobuf is a binary encoding and the types are known at compile time.
 - the name of the attributes. 
 - their position within an encoded stream. (Typically just an incrementing counter, see below example.)
 
Here is a sample object defining a message:
```proto
syntax = "proto3";
package my_package;

message MyMessage {
    string payload = 1;
    string sender = 2;
}
``` 
This object defines two attributes, `payload` and `sender`, both of type `string`.
Note the `= 1` after `payload`? When defining an object we must define the order in which the attributes appear in the 
encoded string. Thus this object is defined that `payload` appears first, followed by `sender`.

- Generally speaking, simply setting the first field to `1` and incrementing subsequent fields works just fine. 

## Objects inside objects
Objects can also be defined with other defined objects as fields.
```proto
syntax = "proto3";
package my_package;

message Point {
    int32 x = 1;
    int32 y = 2;
}

message Displacement {
    Point origin = 1; // field positions are relative to the Message object they are defined in.
    Point destination = 2; // thus these are still fields 1,2 irregardless to Point's fields. (handled by protobuf)
}
```

## Enumerations
Protobuf also provides for C-style enumerations, which may be used as fields in message objects.
 - internally protobuf uses integers to represent enumerated types, which is why the first `StatusCode` is set to zero.
 
```proto
syntax = "proto3";
package my_package;
enum StatusCodes {
    UNKNOWN = 0;
    OK = 1;
    FAILED = 2;
}

message Status {
    StatusCodes code = 1;
    string description = 2;
}
```

## Other things
Protobuf objects also support [repeated](https://developers.google.com/protocol-buffers/docs/proto3#specifying_field_rules), [OneOf](https://developers.google.com/protocol-buffers/docs/proto3#specifying_field_rules), and other kinds of advanced fields, see linked documentation for their usage.

## Generating client/server code
Now that the general syntax of protobuf defined, it would help to be able to actually /write/ code against these definitions.
Compiling `.proto` into usable language source files is the responsibility of the `protoc` tool. 
- For Python, the `grpcio_tools` package provides a python version of this tool, which must otherwise be installed system-wide.
- On Ubuntu, a system-provided protoc (that works with languages other than python, as well) can be obtained via `apt install protobuf-compiler`

```bash
$ python3 -m grpc_tools.protoc -I=/path/to/protos /path/to/protos/*.proto --python_out=/path/to/output
# OR, if using a system-provided protoc
$ protoc -I=/path/to/protos /path/to/protos/*.proto --python_out=/path/to/output
```