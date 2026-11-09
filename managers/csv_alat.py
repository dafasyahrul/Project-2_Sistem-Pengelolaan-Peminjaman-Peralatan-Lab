from managers.csv_dasar import baca_csv, teks, tulis_csv
from models.enums import KondisiAlat

FILE_KATEGORI = "kategori.csv"
KOLOM_KATEGORI = ["nama"]
FILE_ALAT = "alat.csv"
KOLOM_ALAT = ["kode", "nama", "kategori", "stok_total", "stok_tersedia",
              "stok_dipinjam", "stok_rusak_ringan", "stok_rusak_berat"]


class CsvAlat:
    def __init__(self, alat_mgr, folder: str = "data"):
        self.__mgr = alat_mgr
        self.__folder = folder

    def simpan(self) -> None:
        tulis_csv(self.__folder, FILE_KATEGORI, KOLOM_KATEGORI,
                  [{"nama": k} for k in self.__mgr.semua_kategori()])
        tulis_csv(self.__folder, FILE_ALAT, KOLOM_ALAT, [
            {"kode": a.kode, "nama": a.nama, "kategori": a.kategori,
             "stok_total": a.stok_total, "stok_tersedia": a.stok_tersedia,
             "stok_dipinjam": a.stok_dipinjam,
             "stok_rusak_ringan": a.stok_rusak_ringan,
             "stok_rusak_berat": a.stok_rusak_berat}
            for a in self.__mgr.semua()])

    def muat(self) -> list[str]:
        """Mengisi kategori dan alat dari file. Mengembalikan daftar peringatan."""
        peringatan = []
        for b in baca_csv(self.__folder, FILE_KATEGORI):
            try:
                self.__mgr.tambah_kategori(teks(b, "nama"))
            except ValueError:
                pass  # sudah ada atau kosong
        for b in baca_csv(self.__folder, FILE_ALAT):
            try:
                kategori = teks(b, "kategori")
                try:
                    self.__mgr.tambah_kategori(kategori)
                except ValueError:
                    pass
                self.__mgr.tambah(teks(b, "kode"), teks(b, "nama"), kategori,
                                  int(teks(b, "stok_total")))
            except ValueError as e:
                peringatan.append(f"{FILE_ALAT}, kode '{teks(b, 'kode')}' dilewati: {e}")
        return peringatan

    def hitung_stok(self, daftar_transaksi: list) -> list[str]:
        """Menghitung stok tiap alat dari transaksi. Dipanggil SETELAH transaksi dimuat."""
        peringatan = []
        for alat in self.__mgr.semua():
            dipinjam = ringan = berat = 0
            for t in daftar_transaksi:
                dipinjam += sum(i.sisa() for i in t.daftar_item
                                if i.alat.kode == alat.kode)
                for p in t.daftar_pengembalian:
                    if p.alat.kode == alat.kode:
                        if p.kondisi == KondisiAlat.RUSAK_RINGAN:
                            ringan += p.jumlah
                        elif p.kondisi == KondisiAlat.RUSAK_BERAT:
                            berat += p.jumlah
            tersedia = alat.stok_total - dipinjam - ringan - berat
            try:
                alat.pulihkan_stok(tersedia, dipinjam, ringan, berat)
            except ValueError as e:
                peringatan.append(f"{FILE_ALAT}, {alat.kode}: {e} Stok dibiarkan penuh.")
        return peringatan
