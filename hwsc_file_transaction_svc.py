from concurrent import futures
from azure.storage.blob import BlockBlobService, PublicAccess
import os, uuid,sys
import io
import grpc
import time
import filetype
import os.path
import hwsc_file_transaction_svc_pb2
import hwsc_file_transaction_svc_pb2_grpc

CHUNK_SIZE = 1024 * 1024


def download_chunk(file):
     with open(file, 'rb')as f:
         while True:
             chunk = f.read(CHUNK_SIZE)
             if len(chunk) == 0:
                 return
             yield hwsc_file_transaction_svc_pb2.chunk(buffer=chunk)

def get_file_type(fileName):
    fileType = ''
    imageRegex = set('.jpg .jpeg . png .bmp . tif .gif .tiff'.split())
    audioRegex = set('.wav .wma . ogg . m4a .mp3'.split())
    videoRegex = set('.flv .wmv .mov .avi .mp4'.split())
    fileRegex = set('.doc .txt .mat'.split())

    _, extension = os.path.splitext(fileName)
    if extension in imageRegex:
        fileType = 'images'
    elif extension in audioRegex:
        fileType = 'audios'
    elif extension in videoRegex:
        fileType = 'videos'
    elif extension in fileRegex:
        fileType = 'files'
    return fileType

def upload_file_to_azure(chunks, fileName):

    try:
        # Create the BlockBlockService that is used to call the Blob service for the storage account
        block_blob_service = BlockBlobService(account_name='hwscdevstorage', account_key='qnxMLlxsVVpNkxxrr7+qzm3eEZMM0I8ab95eafqp8bnO9UbSucfsa2XlYhgkXLrFMb9/mihyd4loY69E+vQJiA==')

        # Create a container.
        container_name = get_file_type(fileName)
        block_blob_service.create_container(container_name);

        # Set the permission so the blobs are public.
        block_blob_service.set_container_acl(container_name, public_access=PublicAccess.Container)

        stream = io.BytesIO()

        for chunk in chunks:
            stream.write(chunk.buffer)

        stream.seek(0)
        block_blob_service.create_blob_from_stream(container_name, fileName, stream)

        print("\nUploading to Blob storage the file name:" + fileName)

        urlUpload = block_blob_service.make_blob_url(container_name, fileName)
        print(urlUpload)
        return urlUpload

    except Exception as NoSuchBlobException:
        print(NoSuchBlobException)

class FileTransactionService(hwsc_file_transaction_svc_pb2_grpc.FileTransactionServiceServicer):
     def __init__(self):

         class Servicer(hwsc_file_transaction_svc_pb2_grpc.FileTransactionServiceServicer):
             def __init__(self):
                 pass

             def get_status(self, request, context):
                 print("Get Status")

             def download_zip_files(self, request_iterator, context):
                 if request_iterator.name:
                     return download_chunk(self.tmp_file_name)

#             def UploadFile(self, request_iterator, context):
 #                print("[INFO] Requesting UploadFile service")
                # save_chunks_to_file(request_iterator, context.fileName)
                 # print(request_iterator.Chunk.fileName)
             #    print(context.Chunk.fileName)
              #   return hwsc_file_transaction_svc_pb2.FileTransactionResponse()
                 # if not request_iterator.buffer.is_valid or request_iterator.fileName.is_valid:
                 #     message = 'Upload Error!'
                 #     context.set_details(message)
                 #     context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
                 #     return hwsc_file_transaction_svc_pb2.FileTransactionResponse()
                 #
                 # status = hwsc_file_transaction_svc_pb2.FileTransactionResponse()
                 # status.code = grpc.StatusCode.OK
                 # assert status.HasField("code")
                 #
                 # return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                 #     message='OK',
                 #     status=status.code,
                 #     url='url: /res' + context.fileName,
                 #     length=64)



            # def upload_file(self, request_iterator, context):
             #    print("[INFO] Requesting UploadFile service")

              #   for getName in request_iterator:
               #      save_chunks_to_file(request_iterator, getName.fileName)

                 #status = hwsc_file_transaction_svc_pb2.FileTransactionResponse()
                 #status.code = grpc.StatusCode.OK
                 #assert status.HasField("code")

                # return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                 #    message='OK',
                  #   code = grpc.StatusCode.OK)


             def upload_file(self, request_iterator, context):
                 print("[INFO] Requesting UploadFile service")

                 for getName in request_iterator:
                     upload_file_to_azure(request_iterator, getName.fileName)

                 return hwsc_file_transaction_svc_pb2.FileTransactionResponse(message='OK')

             self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))

         hwsc_file_transaction_svc_pb2_grpc.add_FileTransactionServiceServicer_to_server(Servicer(), self.server)

     def start(self, port):
         self.server.add_insecure_port(f'[::]:{port}')
         self.server.start()
         print("Server is running...")

         try:
             while True:
                 time.sleep(60 * 60 * 24)
         except KeyboardInterrupt:
             self.server.stop(0)
