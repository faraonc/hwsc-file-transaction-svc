import grpc
import hwsc_file_transaction_svc_pb2
import hwsc_file_transaction_svc_pb2_grpc
from service import server
from utility import utility
from logger import logger


class FileTransactionService(hwsc_file_transaction_svc_pb2_grpc.FileTransactionServiceServicer):
    """A FileTransactionService class contains services for handling file transactions."""

    def __init__(self, server):
        self.__server = server

    def GetStatus(self, request, context):
        """Return the status of the service"""
        logger.request_service("GetStatus")

        # Lock service state for reading
        with self.__server.get_state_locker().lock.gen_rlock():
            logger.info("Service State:", str(self.__server.get_state_locker().current_service_state))

            context.set_code = grpc.StatusCode.OK.value[0]
            context.set_details = grpc.StatusCode.OK.name

            if self.__server.get_state_locker().current_service_state == server.State.UNAVAILABLE:
                context.set_code = grpc.StatusCode.UNAVAILABLE.value[0]
                context.set_details = grpc.StatusCode.UNAVAILABLE.name

            # Check connection to Azure Blob Storage
            try:
                utility.block_blob_service.get_blob_service_properties()
            except:
                logger.error("failed to connect to Azure Blob Storage")
                context.set_code = grpc.StatusCode.UNAVAILABLE.value[0]
                context.set_details = grpc.StatusCode.UNAVAILABLE.name

            return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                code=context.set_code,
                message=context.set_details
            )

    def UploadFile(self, request_iterator, context):
        """Upload a file to the azure blob storage."""
        logger.request_service("UploadFile")

        d = utility.get_property(request_iterator)

        file_type = utility.get_file_type(d["f_name"])
        logger.info("file type:", file_type)

        is_uuid_valid = utility.verify_uuid(d["uuid"])
        logger.info("valid uuid:", is_uuid_valid)

        if is_uuid_valid:
            has_folder = utility.find_folder(d["uuid"], file_type)

            logger.info("has folder:", has_folder)

            get_url = utility.upload_file_to_azure(d["stream"], has_folder, d["uuid"], d["f_name"])

            if get_url != "":
                return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                    code=grpc.StatusCode.OK.value[0],
                    message="success uploadfile",
                    url=get_url
                )

            else:
                return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                    code=grpc.StatusCode.UNKNOWN.value[0],
                    message='fail uploadfile',
                )

        else:
            return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                code=grpc.StatusCode.UNKNOWN.value[0],
                message="invalid uuid"
            )

    def CreateUserFolder(self, request, context):
        """Create user folder in the azure blob storage."""
        logger.request_service("CreateUserFolder")

        is_uuid_valid = utility.verify_uuid(request.uuid)

        if is_uuid_valid:
            count = utility.count_folders(request.uuid)
            logger.info("count:", count)
            created = utility.create_uuid_container_in_azure(count, request.uuid)

            if created:
                return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                    code=grpc.StatusCode.OK.value[0],
                    message="success"
                )
            else:
                return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                    code=grpc.StatusCode.UNKNOWN.value[0],
                    message="user folder already exist"
                )
        else:
            return hwsc_file_transaction_svc_pb2.FileTransactionResponse(
                code=grpc.StatusCode.UNKNOWN.value[0],
                message="invalid uuid"
            )

    # TODO
    def DownloadZippedFiles(self, request_iterator, context):
        """Download zipped files from azrue blob storage."""
        if request_iterator.name:
            return utility.download_chunk(self.tmp_file_name)
