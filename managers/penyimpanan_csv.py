from managers.csv_alat import CsvAlat
from managers.csv_mahasiswa import CsvMahasiswa
from managers.csv_transaksi import CsvTransaksi

class PenyimpananCSV:
    def __init__(self, mahasiswa_mgr, alat_mgr, transaksi_mgr, folder: str = "data"):
        self.__transaksi_mgr = transaksi_mgr
        self.__mahasiswa = CsvMahasiswa(mahasiswa_mgr, folder)
        self.__alat = CsvAlat(alat_mgr, folder)
        self.__transaksi = CsvTransaksi(transaksi_mgr, mahasiswa_mgr, alat_mgr, folder)

    def simpan_semua(self) -> None:
        try:
            self.__mahasiswa.simpan()
            self.__alat.simpan()
            self.__transaksi.simpan()
        except OSError as e:
            print(f"[PERINGATAN] CSV gagal disimpan ({e}). "
                  "Tutup file CSV jika sedang dibuka di Excel.")

    def muat(self) -> list[str]:
        peringatan: list[str] = []
        peringatan += self.__mahasiswa.muat()
        peringatan += self.__alat.muat()
        peringatan += self.__transaksi.muat()
        peringatan += self.__alat.hitung_stok(self.__transaksi_mgr.semua())
        return peringatan