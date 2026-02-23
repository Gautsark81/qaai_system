from .checksum import compute_checksum


class AuditPackReader:
    @staticmethod
    def verify(pack) -> bool:
        return pack.checksum == compute_checksum(pack.serialize())
