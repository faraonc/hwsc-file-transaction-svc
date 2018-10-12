# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
import grpc

import hwsc_file_svc_pb2 as hwsc__file__svc__pb2


class FileServiceStub(object):
  # missing associated documentation comment in .proto file
  pass

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.GetStatus = channel.unary_unary(
        '/hwscFileSvc.FileService/GetStatus',
        request_serializer=hwsc__file__svc__pb2.FileRequest.SerializeToString,
        response_deserializer=hwsc__file__svc__pb2.FileResponse.FromString,
        )


class FileServiceServicer(object):
  # missing associated documentation comment in .proto file
  pass

  def GetStatus(self, request, context):
    # missing associated documentation comment in .proto file
    pass
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_FileServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'GetStatus': grpc.unary_unary_rpc_method_handler(
          servicer.GetStatus,
          request_deserializer=hwsc__file__svc__pb2.FileRequest.FromString,
          response_serializer=hwsc__file__svc__pb2.FileResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'hwscFileSvc.FileService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
