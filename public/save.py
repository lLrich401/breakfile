"""리치가 사용한 파일 저장 방식의 일부입니다.

한 번에 DATA_SHARDS 바이트씩 저장하고, 오류에 대비해 추가 값을 기록합니다.
이 코드는 저장(정상 파일 작성) 과정만 포함합니다.
"""
from struct import pack

MAGIC = b"RICHREC1"
P = 257
DATA_SHARDS = 4
PARITY_SHARDS = 3
ERASED = 0xFFFF


def value_at(known: list[tuple[int, int]], x: int) -> int:
    """GF(257)에서 주어진 점을 통과하는 다항식의 f(x)를 구합니다."""
    result = 0
    for i, (xi, yi) in enumerate(known):
        term = yi
        for j, (xj, _) in enumerate(known):
            if i != j:
                term = term * (x - xj) * pow(xi - xj, -1, P) % P
        result = (result + term) % P
    return result


def save(data: bytes) -> bytes:
    length = len(data)
    count = (length + DATA_SHARDS - 1) // DATA_SHARDS
    padded = data.ljust(count * DATA_SHARDS, b"\x00")
    output = bytearray(MAGIC + pack("<II", length, count))
    for offset in range(0, len(padded), DATA_SHARDS):
        row = padded[offset:offset + DATA_SHARDS]
        points = list(enumerate(row, start=1))
        values = list(row) + [value_at(points, x) for x in (5, 6, 7)]
        for v in values:
            output.extend(v.to_bytes(2, "little"))
    return bytes(output)
