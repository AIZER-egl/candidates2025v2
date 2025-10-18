import struct
from collections import namedtuple

# '<' little endian (standard size and alignment - #pragma pack(1))
# 'h' short (2 bytes)
# 'B' unsigned char (1 byte)
# 'H' unsigned short (2 bytes)
# 'f' float (4 bytes)
# '?' bool (1 byte)
STRUCT_FORMAT = "<hBHHHH?fHhB????"
PACKET_SIZE = struct.calcsize(STRUCT_FORMAT)

_FIELD_NAMES = [
	'yaw',
	'floor_color',
	'motor_distance',
	'front_wall',
	'left_wall',
	'right_wall',
	'start',
	'test_pid_error_sum',
	'motor_speed_target',
	'motor_facing_target',
	'motor_move_form',
	'reset_distance',
	'reset_pid',
	'servo_active',
	'kicker_active'
]

_BinaryDataTuple = namedtuple('BinaryDataPacket', _FIELD_NAMES)

def unpack_data(raw_bytes: bytes):
	if len(raw_bytes) != PACKET_SIZE:
		raise ValueError(f"Expected {PACKET_SIZE} bytes, got {len(raw_bytes)} bytes")

	unpacked = struct.unpack(STRUCT_FORMAT, raw_bytes)
	return _BinaryDataTuple(*unpacked)

def pack_data(data: _BinaryDataTuple) -> bytes:
	if not isinstance(data, _BinaryDataTuple):
		raise TypeError(f"Expected _BinaryDataTuple, got {type(data)}")

	return struct.pack(STRUCT_FORMAT, *data)

default_packet = _BinaryDataTuple(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
