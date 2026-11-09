from managers.csv_dasar import baca_csv, teks, tulis_csv

NAMA_FILE = "mahasiswa.csv"
KOLOM = ["nim", "nama", "no_hp"]

class CsvMahasiswa:
    def __init__(self, mahasiswa_mgr, folder: str = "data"):
        self.__mgr = mahasiswa_mgr
        self.__folder = folder

    def simpan(self) -> None:
        tulis_csv(self.__folder, NAMA_FILE, KOLOM, [
            {"nim": m.nim, "nama": m.nama, "no_hp": m.no_hp}
            for m in self.__mgr.semua()])

    def muat(self) -> list[str]:
        peringatan = []
        for b in baca_csv(self.__folder, NAMA_FILE):
            try:
                self.__mgr.tambah(teks(b, "nim"), teks(b, "nama"), teks(b, "no_hp"))
            except ValueError as e:
                peringatan.append(f"{NAMA_FILE}, NIM '{teks(b, 'nim')}' dilewati: {e}")
        return peringatan