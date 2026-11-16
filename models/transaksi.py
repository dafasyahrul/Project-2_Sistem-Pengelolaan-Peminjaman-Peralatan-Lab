"""Kelas Transaksi, ItemPeminjaman, dan Pengembalian."""
from datetime import date

from models.alat import Alat
from models.enums import KondisiAlat, StatusTransaksi
from models.mahasiswa import Mahasiswa


class ItemPeminjaman:
    """Satu baris alat dalam sebuah transaksi."""

    def __init__(self, alat: Alat, jumlah: int):
        if jumlah < 1:
            raise ValueError("Jumlah pinjam minimal 1.")
        self.__alat = alat
        self.__jumlah = jumlah
        self.__jumlah_kembali = 0

    @property
    def alat(self) -> Alat:
        return self.__alat

    @property
    def jumlah(self) -> int:
        return self.__jumlah

    @property
    def jumlah_kembali(self) -> int:
        return self.__jumlah_kembali

    def sisa(self) -> int:
        return self.__jumlah - self.__jumlah_kembali

    def kembalikan(self, jumlah: int) -> None:
        if jumlah < 1 or jumlah > self.sisa():
            raise ValueError(
                f"Jumlah kembali tidak valid untuk '{self.__alat.nama}' "
                f"(sisa belum kembali: {self.sisa()})."
            )
        self.__jumlah_kembali += jumlah

    def sudah_kembali_semua(self) -> bool:
        return self.sisa() == 0


class Pengembalian:
    """Catatan satu kali pengembalian."""

    def __init__(self, alat: Alat, jumlah: int, kondisi: KondisiAlat,
                 tanggal_kembali: date):
        self.__alat = alat
        self.__jumlah = jumlah
        self.__kondisi = kondisi
        self.__tanggal_kembali = tanggal_kembali

    @property
    def alat(self) -> Alat:
        return self.__alat

    @property
    def jumlah(self) -> int:
        return self.__jumlah

    @property
    def kondisi(self) -> KondisiAlat:
        return self.__kondisi

    @property
    def tanggal_kembali(self) -> date:
        return self.__tanggal_kembali

    def __str__(self) -> str:
        return (f"{self.__tanggal_kembali} - {self.__alat.nama} x{self.__jumlah} "
                f"({self.__kondisi.value})")


class Transaksi:
    def __init__(self, id_transaksi: str, mahasiswa: Mahasiswa,
                 tanggal_pinjam: date, batas_kembali: date):
        self.__id_transaksi = id_transaksi
        self.__mahasiswa = mahasiswa
        self.__daftar_item: list[ItemPeminjaman] = []
        self.__daftar_pengembalian: list[Pengembalian] = []
        self.__tanggal_pinjam = tanggal_pinjam
        self.__batas_kembali = batas_kembali
        self.__status = StatusTransaksi.DIPINJAM

    @property
    def id_transaksi(self) -> str:
        return self.__id_transaksi

    @property
    def mahasiswa(self) -> Mahasiswa:
        return self.__mahasiswa

    @property
    def daftar_item(self) -> list[ItemPeminjaman]:
        return list(self.__daftar_item)

    @property
    def daftar_pengembalian(self) -> list[Pengembalian]:
        return list(self.__daftar_pengembalian)

    @property
    def tanggal_pinjam(self) -> date:
        return self.__tanggal_pinjam

    @property
    def batas_kembali(self) -> date:
        return self.__batas_kembali

    @property
    def status(self) -> StatusTransaksi:
        return self.__status

    def __cari_item(self, kode: str) -> ItemPeminjaman | None:
        kode = kode.strip().upper()
        for item in self.__daftar_item:
            if item.alat.kode == kode:
                return item
        return None

    def tambah_item(self, alat: Alat, jumlah: int) -> None:
        if self.mengandung_alat(alat.kode):
            raise ValueError(f"Alat {alat.kode} sudah ada di transaksi ini.")
        self.__daftar_item.append(ItemPeminjaman(alat, jumlah))

    def catat_pengembalian(self, kode: str, jumlah: int, kondisi: KondisiAlat,
                           tanggal: date | None = None) -> None:
        item = self.__cari_item(kode)
        if item is None:
            raise ValueError(f"Alat {kode} tidak ada di transaksi {self.__id_transaksi}.")
        if item.sudah_kembali_semua():
            raise ValueError(f"Alat {item.alat.kode} sudah dikembalikan semua.")
        item.kembalikan(jumlah)
        item.alat.terima_kembali(jumlah, kondisi)
        self.__daftar_pengembalian.append(
            Pengembalian(item.alat, jumlah, kondisi, tanggal or date.today()))
        self.perbarui_status()

def pulihkan_pengembalian(
    self,
    kode: str,
    jumlah: int,
    kondisi: KondisiAlat,
    tanggal: date
) -> None:
    """Memulihkan catatan pengembalian dari CSV tanpa mengubah stok alat."""
    item = self.__cari_item(kode)

    if item is None:
        raise ValueError(
            f"Alat {kode} tidak ada di transaksi {self.__id_transaksi}."
        )

    item.kembalikan(jumlah)

    self.__daftar_pengembalian.append(
        Pengembalian(item.alat, jumlah, kondisi, tanggal)
    )

    self.perbarui_status()

    def perbarui_status(self) -> None:
        if all(i.sudah_kembali_semua() for i in self.__daftar_item):
            self.__status = StatusTransaksi.SELESAI
        elif any(i.jumlah_kembali > 0 for i in self.__daftar_item):
            self.__status = StatusTransaksi.SEBAGIAN_DIKEMBALIKAN
        else:
            self.__status = StatusTransaksi.DIPINJAM

    def masih_aktif(self) -> bool:
        return self.__status != StatusTransaksi.SELESAI

    def mengandung_alat(self, kode: str) -> bool:
        return self.__cari_item(kode) is not None

    def terlambat(self, tanggal: date | None = None) -> bool:
        tanggal = tanggal or date.today()
        return self.masih_aktif() and tanggal > self.__batas_kembali

    def __str__(self) -> str:
        baris = [
            f"Transaksi {self.__id_transaksi} | {self.__mahasiswa.nama} "
            f"({self.__mahasiswa.nim}) | Status: {self.__status.value}",
            f"  Pinjam: {self.__tanggal_pinjam} | Batas kembali: {self.__batas_kembali}"
            + (" | TERLAMBAT" if self.terlambat() else ""),
        ]
        for i in self.__daftar_item:
            baris.append(f"  - {i.alat.nama} ({i.alat.kode}): dipinjam {i.jumlah}, "
                         f"kembali {i.jumlah_kembali}, sisa {i.sisa()}")
        for p in self.__daftar_pengembalian:
            baris.append(f"  * Kembali: {p}")
        return "\n".join(baris)