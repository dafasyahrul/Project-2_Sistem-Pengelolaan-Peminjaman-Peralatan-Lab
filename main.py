import sys

from managers.alat_manager import AlatManager
from managers.mahasiswa_manager import MahasiswaManager
from managers.penyimpanan_csv import PenyimpananCSV
from managers.transaksi_manager import TransaksiManager
from menu_app import MenuApp

def muat_data_contoh(mahasiswa_mgr, alat_mgr) -> None:
    mahasiswa_mgr.tambah("2400001", "Budi Santoso", "081234567890")
    mahasiswa_mgr.tambah("2400002", "Siti Aminah", "085612345678")
    alat_mgr.tambah("A01", "Multimeter", "Elektronik", 5)
    alat_mgr.tambah("A02", "Osiloskop", "Elektronik", 2)
    alat_mgr.tambah("A03", "Mikroskop", "Optik", 3)

def main() -> None:
    mahasiswa_mgr = MahasiswaManager()
    alat_mgr = AlatManager()
    transaksi_mgr = TransaksiManager(mahasiswa_mgr, alat_mgr)
    penyimpanan = PenyimpananCSV(mahasiswa_mgr, alat_mgr, transaksi_mgr)

    for pesan in penyimpanan.muat():
        print(f"[PERINGATAN] {pesan}")
    jumlah = (len(mahasiswa_mgr.semua()), len(alat_mgr.semua()), len(transaksi_mgr.semua()))
    if any(jumlah):
        print(f"Data dimuat dari CSV: {jumlah[[0]]} mahasiswa, "
              f"{jumlah[1]} alat, {jumlah[2]} transaksi.")
        
    if "--demo" in sys.argv:
        muat_data_contoh(mahasiswa_mgr, alat_mgr)
        penyimpanan.simpan_semua()
        print("[Mode demo] Data contoh dimuat.")

    MenuApp(mahasiswa_mgr, alat_mgr, transaksi_mgr, penyimpanan).jalankan()

if __name__ == "__main__":
    main()