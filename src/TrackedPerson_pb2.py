# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: TrackedPerson.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from google.protobuf import timestamp_pb2 as google_dot_protobuf_dot_timestamp__pb2


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x13TrackedPerson.proto\x12\x0fSpreadYourWings\x1a\x1fgoogle/protobuf/timestamp.proto\"B\n\x0b\x42oundingBox\x12\t\n\x01x\x18\x01 \x01(\x02\x12\t\n\x01y\x18\x02 \x01(\x02\x12\r\n\x05width\x18\x03 \x01(\x02\x12\x0e\n\x06height\x18\x04 \x01(\x02\"}\n\rTrackedPerson\x12\x31\n\x0b\x62oundingbox\x18\x01 \x01(\x0b\x32\x1c.SpreadYourWings.BoundingBox\x12\n\n\x02id\x18\x02 \x01(\x05\x12-\n\ttimestamp\x18\x03 \x01(\x0b\x32\x1a.google.protobuf.Timestamp\"\x07\n\x05\x45mpty2]\n\x14TrackedPersonService\x12\x45\n\tGetTracks\x12\x16.SpreadYourWings.Empty\x1a\x1e.SpreadYourWings.TrackedPerson0\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'TrackedPerson_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _globals['_BOUNDINGBOX']._serialized_start=73
  _globals['_BOUNDINGBOX']._serialized_end=139
  _globals['_TRACKEDPERSON']._serialized_start=141
  _globals['_TRACKEDPERSON']._serialized_end=266
  _globals['_EMPTY']._serialized_start=268
  _globals['_EMPTY']._serialized_end=275
  _globals['_TRACKEDPERSONSERVICE']._serialized_start=277
  _globals['_TRACKEDPERSONSERVICE']._serialized_end=370
# @@protoc_insertion_point(module_scope)
