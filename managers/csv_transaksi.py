"""Penyimpanan CSV untuk semua transaksi (data/transaksi.csv).

Satu transaksi bisa punya banyak baris:
  PINJAM  = alat yang dipinjam (satu baris per alat)
  KEMBALI = tiap kejadian pengembalian, lengkap dengan kondisi dan tanggal
"""
from datetime import date

from managers.csv_dasar import baca_csv, teks, tulis_csv
from models.alat import Alat
from models.enums import KondisiAlat
from models.mahasiswa import Mahasiswa
from models.transaksi import Transaksi

NAMA_FILE = "transaksi.csv"
KOLOM = ["id_transaksi", "jenis", "nim", "nama_mahasiswa", "kode_alat",
         "nama_alat", "jumlah", "tanggal_pinjam", "batas_kembali",
         "kondisi", "tanggal_kembali", "status"]


class CsvTransaksi:
    def __init__(self, transaksi_mgr, mahasiswa_mgr, alat_mgr, folder: str = "data"):
        self.__transaksi_mgr = transaksi_mgr
        self.__mahasiswa_mgr = mahasiswa_mgr
        self.__alat_mgr = alat_mgr
        self.__folder = folder
        self.__baris_sisa: list[dict] = []

    def simpan(self) -> None:
        baris = []
        for t in self.__transaksi_mgr.semua():
            umum = {
                "id_transaksi": t.id_transaksi,
                "nim": t.mahasiswa.nim,
                "nama_mahasiswa": t.mahasiswa.nama,
                "tanggal_pinjam": t.tanggal_pinjam.isoformat(),
                "batas_kembali": t.batas_kembali.isoformat(),
                "status": t.status.value,
            }
            for i in t.daftar_item:
                baris.append({**umum, "jenis": "PINJAM", "kode_alat": i.alat.kode,
                              "nama_alat": i.alat.nama, "jumlah": i.jumlah})
            for p in t.daftar_pengembalian:
                baris.append({**umum, "jenis": "KEMBALI", "kode_alat": p.alat.kode,
                              "nama_alat": p.alat.nama, "jumlah": p.jumlah,
                              "kondisi": p.kondisi.value,
                              "tanggal_kembali": p.tanggal_kembali.isoformat()})
        tulis_csv(self.__folder, NAMA_FILE, KOLOM, baris + self.__baris_sisa)

    def muat(self) -> list[str]:
        """Memulihkan transaksi dari file. Mengembalikan daftar peringatan."""
        peringatan: list[str] = []
        self.__baris_sisa = []
        kelompok: dict[str, list[dict]] = {}
        for b in baca_csv(self.__folder, NAMA_FILE):
            kelompok.setdefault(teks(b, "id_transaksi").upper(), []).append(b)
        for id_trx, baris in kelompok.items():
            try:
                self.__pulihkan(id_trx, baris, peringatan)
            except ValueError as e:
                peringatan.append(f"{NAMA_FILE}, '{id_trx}' tidak dipulihkan ({e}). "
                                  "Barisnya disimpan apa adanya.")
                self.__baris_sisa.extend(baris)
        return peringatan

    def __pulihkan(self, id_trx: str, baris: list[dict], peringatan: list[str]) -> None:
        if not id_trx:
            raise ValueError("ID transaksi kosong")
        pinjam = [r for r in baris if teks(r, "jenis").upper() == "PINJAM"]
        kembali = [r for r in baris if teks(r, "jenis").upper() == "KEMBALI"]
        if not pinjam:
            raise ValueError("tidak ada baris PINJAM")

        awal = pinjam[0]
        nim = teks(awal, "nim")
        if not nim:
            raise ValueError("NIM kosong")
        try:
            mhs, terdaftar = self.__mahasiswa_mgr.ambil(nim), True
        except ValueError:
            mhs, terdaftar = Mahasiswa(nim, teks(awal, "nama_mahasiswa") or nim, "-"), False

        trx = Transaksi(id_trx, mhs,
                        date.fromisoformat(teks(awal, "tanggal_pinjam")),
                        date.fromisoformat(teks(awal, "batas_kembali")))
        alat_hilang = []
        for r in pinjam:
            kode = teks(r, "kode_alat").upper()
            if not kode:
                raise ValueError("kode alat kosong")
            try:
                alat = self.__alat_mgr.ambil(kode)
            except ValueError:
                alat = Alat(kode, teks(r, "nama_alat") or kode, "-", 1)
                alat_hilang.append(kode)
            trx.tambah_item(alat, int(teks(r, "jumlah")))

        for r in kembali:
            try:
                trx.pulihkan_pengembalian(
                    teks(r, "kode_alat"), int(teks(r, "jumlah")),
                    KondisiAlat(teks(r, "kondisi").upper()),
                    date.fromisoformat(teks(r, "tanggal_kembali")))
            except ValueError as e:
                peringatan.append(f"{NAMA_FILE}, {id_trx}: baris KEMBALI "
                                  f"'{teks(r, 'kode_alat')}' diabaikan ({e})")

        if trx.masih_aktif():
            if not terdaftar:
                peringatan.append(f"{NAMA_FILE}, {id_trx}: NIM {nim} tidak ada di "
                                  "mahasiswa.csv padahal transaksi masih aktif.")
            else:
                try:
                    mhs.tambah_transaksi_aktif(id_trx)
                except ValueError as e:
                    peringatan.append(f"{NAMA_FILE}, {id_trx}: {e} Tetap dimuat.")
            if alat_hilang:
                peringatan.append(f"{NAMA_FILE}, {id_trx}: alat {', '.join(alat_hilang)} "
                                  "tidak ada di alat.csv padahal transaksi masih aktif.")
        self.__transaksi_mgr.pulihkan(trx)