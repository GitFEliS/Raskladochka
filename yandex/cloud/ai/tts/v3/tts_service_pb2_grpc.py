# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from yandex.cloud.ai.tts.v3 import tts_pb2 as yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2


class SynthesizerStub(object):
    """A set of methods for voice synthesis.
    """

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.UtteranceSynthesis = channel.unary_stream(
            '/speechkit.tts.v3.Synthesizer/UtteranceSynthesis',
            request_serializer=yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2.UtteranceSynthesisRequest.SerializeToString,
            response_deserializer=yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2.UtteranceSynthesisResponse.FromString,
        )


class SynthesizerServicer(object):
    """A set of methods for voice synthesis.
    """

    def UtteranceSynthesis(self, request, context):
        """Synthesizing text into speech.
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SynthesizerServicer_to_server(servicer, server):
    rpc_method_handlers = {
        'UtteranceSynthesis': grpc.unary_stream_rpc_method_handler(
            servicer.UtteranceSynthesis,
            request_deserializer=yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2.UtteranceSynthesisRequest.FromString,
            response_serializer=yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2.UtteranceSynthesisResponse.SerializeToString,
        ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
        'speechkit.tts.v3.Synthesizer', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


# This class is part of an EXPERIMENTAL API.
class Synthesizer(object):
    """A set of methods for voice synthesis.
    """

    @staticmethod
    def UtteranceSynthesis(request,
                           target,
                           options=(),
                           channel_credentials=None,
                           call_credentials=None,
                           insecure=False,
                           compression=None,
                           wait_for_ready=None,
                           timeout=None,
                           metadata=None):
        return grpc.experimental.unary_stream(request, target, '/speechkit.tts.v3.Synthesizer/UtteranceSynthesis',
                                              yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2.UtteranceSynthesisRequest.SerializeToString,
                                              yandex_dot_cloud_dot_ai_dot_tts_dot_v3_dot_tts__pb2.UtteranceSynthesisResponse.FromString,
                                              options, channel_credentials,
                                              insecure, call_credentials, compression, wait_for_ready, timeout,
                                              metadata)
