from datetime import date, timedelta
from models.enums import KondisiAlat
from models.transaksi import Transaksi

MAKS_LAMA_HARI = 7

class TransaksiManager:
    def __init__(self, mahasiswa_mgr, alat_mgr):
        self.__data: dict[str, Transaksi] = {}  
        self.__mahasiswa_mgr = mahasiswa_mgr
        self.__alat_mgr = alat_mgr
        self.__counter = 0

    def __buat_id(self) -> str:
        self.__counter += 1
        return f"TRX-{self.__counter:03d}"

    def buat_transaksi(self, nim: str, items: list[tuple[str, int]],
                       lama_hari: int = MAKS_LAMA_HARI,
                       tanggal_pinjam: date | None = None) -> Transaksi:
        mhs = self.__mahasiswa_mgr.ambil(nim)
        if not mhs.bisa_meminjam():
            raise ValueError("Mahasiswa sudah mencapai batas 2 transaksi aktif.")
        if not 1 <= lama_hari <= MAKS_LAMA_HARI:
            raise ValueError(f"Lama peminjaman harus 1-{MAKS_LAMA_HARI} hari.")
        if not items:
            raise ValueError("Transaksi harus berisi minimal 1 alat.")

        gabungan: dict[str, int] = {}
        for kode, jumlah in items:
            kode = kode.strip().upper()
            gabungan[kode] = gabungan.get(kode, 0) + jumlah
        for kode, jumlah in gabungan.items():
            alat = self.__alat_mgr.ambil(kode)
            if not alat.cukup_stok(jumlah):
                raise ValueError(
                    f"Stok '{alat.nama}' tidak cukup "
                    f"(diminta {jumlah}, tersedia {alat.stok_tersedia}).")

        tanggal_pinjam = tanggal_pinjam or date.today()
        trx = Transaksi(self.__buat_id(), mhs, tanggal_pinjam,
                        tanggal_pinjam + timedelta(days=lama_hari))
        for kode, jumlah in gabungan.items():
            alat = self.__alat_mgr.ambil(kode)
            trx.tambah_item(alat, jumlah)
            alat.keluarkan_untuk_dipinjam(jumlah)
        mhs.tambah_transaksi_aktif(trx.id_transaksi)
        self.__data[trx.id_transaksi] = trx
        return trx

    def proses_pengembalian(self, id_trx: str, kode: str, jumlah: int,
                            kondisi: KondisiAlat,
                            tanggal: date | None = None) -> Transaksi:
        id_trx = id_trx.strip().upper()
        if id_trx not in self.__data:
            raise ValueError(f"Transaksi {id_trx} tidak ditemukan.")
        trx = self.__data[id_trx]
        if not trx.masih_aktif():
            raise ValueError(f"Transaksi {id_trx} sudah selesai.")
        trx.catat_pengembalian(kode, jumlah, kondisi, tanggal)
        if not trx.masih_aktif():
            trx.mahasiswa.hapus_transaksi_aktif(trx.id_transaksi)
        return trx

    def cari_by_mahasiswa(self, nim: str) -> list[Transaksi]:
        self.__mahasiswa_mgr.ambil(nim)
        return [t for t in self.__data.values() if t.mahasiswa.nim == nim]

    def riwayat_mahasiswa(self, nim: str) -> list[Transaksi]:
        selesai = [t for t in self.cari_by_mahasiswa(nim) if not t.masih_aktif()]
        return sorted(selesai, key=lambda t: t.tanggal_pinjam, reverse=True)

    def transaksi_aktif(self) -> list[Transaksi]:
        return [t for t in self.__data.values() if t.masih_aktif()]

    def alat_sedang_dipinjam(self) -> list[str]:
        hasil = []
        for t in self.transaksi_aktif():
            for i in t.daftar_item:
                if i.sisa() > 0:
                    hasil.append(
                        f"{i.alat.nama} ({i.alat.kode}) x{i.sisa()} - "
                        f"{t.mahasiswa.nama} - {t.id_transaksi} - "
                        f"batas {t.batas_kembali}"
                        + (" [TERLAMBAT]" if t.terlambat() else ""))
        return hasil

    def semua(self) -> list[Transaksi]:
        return list(self.__data.values())

    def jumlah_transaksi_selesai(self) -> int:
        return sum(1 for t in self.__data.values() if not t.masih_aktif())

    def jumlah_transaksi_aktif(self) -> int:
        return len(self.transaksi_aktif())

    def alat_paling_sering_dipinjam(self) -> list[tuple]:
        hitung: dict[str, list] = {}
        for t in self.__data.values():
            for i in t.daftar_item:
                kode = i.alat.kode
                if kode not in hitung:
                    hitung[kode] = [i.alat, 0, 0]
                hitung[kode][1] += 1
                hitung[kode][2] += i.jumlah
        return sorted((tuple(v) for v in hitung.values()),
                      key=lambda x: (-x[1], -x[2], x[0].kode))

    def mahasiswa_paling_sering_meminjam(self) -> list[tuple]:
        hitung: dict[str, list] = {}
        for t in self.__data.values():
            nim = t.mahasiswa.nim
            if nim not in hitung:
                hitung[nim] = [t.mahasiswa, 0]
            hitung[nim][1] += 1
        return sorted((tuple(v) for v in hitung.values()),
                      key=lambda x: (-x[1], x[0].nim))

    def pulihkan(self, trx: Transaksi) -> None:
        self.__data[trx.id_transaksi] = trx
        angka = trx.id_transaksi.rsplit("-", 1)[-1]
        if angka.isdigit():
            self.__counter = max(self.__counter, int(angka))