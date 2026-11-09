from models.enums import KondisiAlat

class MenuApp:
    def __init__(self, mahasiswa_mgr, alat_mgr, transaksi_mgr, penyimpanan) -> None:
        self.__penyimpanan = penyimpanan
        self.__mahasiswa_mgr = mahasiswa_mgr
        self.__alat_mgr = alat_mgr
        self.__transaksi_mgr = transaksi_mgr

    def __baca_input(self, prompt: str) -> str:
        while True:
            teks = input(prompt).strip()
            if teks:
                return teks
            print("Input tidak boleh kosong.")

    def __baca_angka(self, prompt: str, minimum: int = 1) -> int:
        while True:
            teks = self.__baca_input(prompt)
            if teks.isdigit() and int(teks) >= minimum:
                return int(teks)
            print(f"Masukkan angka bulat >= {minimum}.")

    def __tampilkan_daftar(self, daftar, kosong: str = "Data kosong.") -> None:
        if not daftar:
            print(kosong)
            return
        for i, item in enumerate(daftar, 1):
            print(f"{i}. {item}")

    def __jalankan_aman(self, aksi) -> None:
        try:
            aksi()
            if self.__penyimpanan is not None:
                self.__penyimpanan.simpan_semua()
        except ValueError as e:
            print(f"[GAGAL] {e}")

    def jalankan(self) -> None:
        pilihan = {
            "1": self.menu_mahasiswa,
            "2": self.menu_alat,
            "3": self.menu_transaksi,
            "4": self.menu_laporan,
        }
        while True:
            print("\n=== SISTEM PEMINJAMAN PERALATAN LABORATORIUM ===")
            print("1. Kelola Mahasiswa")
            print("2. Kelola Alat")
            print("3. Transaksi (Pinjam / Kembali / Cari)")
            print("4. Laporan")
            print("0. Keluar")
            pil = input("Pilih menu: ").strip()
            if pil == "0":
                print("Terima kasih.")
                break
            if pil in pilihan:
                pilihan[pil]()
            else:
                print("Pilihan tidak valid.")

    def menu_mahasiswa(self) -> None:
        while True:
            print("\n--- Kelola Mahasiswa ---")
            print("1. Tambah\n2. Edit\n3. Hapus\n4. Cari\n5. Tampilkan semua\n0. Kembali")
            pil = input("Pilih: ").strip()
            if pil == "0":
                return
            elif pil == "1":
                self.__jalankan_aman(self.__tambah_mahasiswa)
            elif pil == "2":
                self.__jalankan_aman(self.__edit_mahasiswa)
            elif pil == "3":
                self.__jalankan_aman(self.__hapus_mahasiswa)
            elif pil == "4":
                kata = self.__baca_input("Kata kunci (NIM/nama): ")
                self.__tampilkan_daftar(self.__mahasiswa_mgr.cari(kata),
                                        "Mahasiswa tidak ditemukan.")
            elif pil == "5":
                self.__tampilkan_daftar(self.__mahasiswa_mgr.semua(),
                                        "Belum ada mahasiswa.")
            else:
                print("Pilihan tidak valid.")

    def __tambah_mahasiswa(self) -> None:
        nim = self.__baca_input("NIM: ")
        nama = self.__baca_input("Nama: ")
        no_hp = self.__baca_input("No HP: ")
        self.__mahasiswa_mgr.tambah(nim, nama, no_hp)
        print("Mahasiswa berhasil ditambahkan.")

    def __edit_mahasiswa(self) -> None:
        nim = self.__baca_input("NIM mahasiswa yang diubah: ")
        self.__mahasiswa_mgr.ambil(nim) 
        nama = self.__baca_input("Nama baru: ")
        no_hp = self.__baca_input("No HP baru: ")
        self.__mahasiswa_mgr.ubah(nim, nama, no_hp)
        print("Data mahasiswa berhasil diubah.")

    def __hapus_mahasiswa(self) -> None:
        nim = self.__baca_input("NIM mahasiswa yang dihapus: ")
        self.__mahasiswa_mgr.hapus(nim)
        print("Mahasiswa berhasil dihapus.")

    def menu_alat(self) -> None:
        while True:
            print("\n--- Kelola Alat ---")
            print("1. Tambah\n2. Edit\n3. Hapus\n4. Cari\n5. Tambah kategori\n"
                  "6. Tampilkan semua alat\n0. Kembali")
            pil = input("Pilih: ").strip()
            if pil == "0":
                return
            elif pil == "1":
                self.__jalankan_aman(self.__tambah_alat)
            elif pil == "2":
                self.__jalankan_aman(self.__edit_alat)
            elif pil == "3":
                self.__jalankan_aman(self.__hapus_alat)
            elif pil == "4":
                kata = self.__baca_input("Kata kunci (kode/nama/kategori): ")
                self.__tampilkan_daftar(self.__alat_mgr.cari(kata),
                                        "Alat tidak ditemukan.")
            elif pil == "5":
                nama = self.__baca_input("Nama kategori baru: ")
                self.__jalankan_aman(lambda: self.__alat_mgr.tambah_kategori(nama))
            elif pil == "6":
                self.__tampilkan_daftar(self.__alat_mgr.semua(), "Belum ada alat.")
            else:
                print("Pilihan tidak valid.")

    def __tambah_alat(self) -> None:
        kode = self.__baca_input("Kode alat: ")
        nama = self.__baca_input("Nama alat: ")
        print("Kategori tersedia:", ", ".join(self.__alat_mgr.semua_kategori()))
        kategori = self.__baca_input("Kategori: ")
        stok = self.__baca_angka("Stok: ")
        self.__alat_mgr.tambah(kode, nama, kategori, stok)
        print("Alat berhasil ditambahkan.")

    def __edit_alat(self) -> None:
        kode = self.__baca_input("Kode alat yang diubah: ")
        nama = self.__baca_input("Nama baru: ")
        print("Kategori tersedia:", ", ".join(self.__alat_mgr.semua_kategori()))
        kategori = self.__baca_input("Kategori baru: ")
        self.__alat_mgr.ubah(kode, nama, kategori)
        print("Data alat berhasil diubah.")

    def __hapus_alat(self) -> None:
        kode = self.__baca_input("Kode alat yang dihapus: ")
        self.__alat_mgr.hapus(kode)
        print("Alat berhasil dihapus.")

    def menu_transaksi(self) -> None:
        while True:
            print("\n--- Transaksi ---")
            print("1. Buat peminjaman\n2. Proses pengembalian\n"
                  "3. Cari transaksi mahasiswa\n4. Tampilkan semua transaksi\n0. Kembali")
            pil = input("Pilih: ").strip()
            if pil == "0":
                return
            elif pil == "1":
                self.__jalankan_aman(self.__buat_transaksi)
            elif pil == "2":
                self.__jalankan_aman(self.__proses_pengembalian)
            elif pil == "3":
                nim = self.__baca_input("NIM mahasiswa: ")
                self.__jalankan_aman(lambda: self.__tampilkan_daftar(
                    self.__transaksi_mgr.cari_by_mahasiswa(nim),
                    "Tidak ada transaksi untuk mahasiswa ini."))
            elif pil == "4":
                self.__tampilkan_daftar(self.__transaksi_mgr.semua(),
                                        "Belum ada transaksi.")
            else:
                print("Pilihan tidak valid.")

    def __buat_transaksi(self) -> None:
        nim = self.__baca_input("NIM peminjam: ")
        mhs = self.__mahasiswa_mgr.ambil(nim)
        if not mhs.bisa_meminjam():
            raise ValueError("Mahasiswa sudah mencapai batas 2 transaksi aktif.")

        items: list[tuple[str, int]] = []  # (kode_alat, jumlah)
        while True:
            kode = self.__baca_input("Kode alat: ")
            jumlah = self.__baca_angka("Jumlah: ")
            items.append((kode, jumlah))
            lagi = input("Tambah alat lain? (y/t): ").strip().lower()
            if lagi != "y":
                break
        lama = self.__baca_angka("Lama pinjam (hari, maks 7): ")

        if lama > 7:
            raise ValueError("Lama peminjaman maksimal 7 hari.")
        trx = self.__transaksi_mgr.buat_transaksi(nim, items, lama)
        print(f"Transaksi berhasil dibuat.\n{trx}")

    def __proses_pengembalian(self) -> None:
        id_trx = self.__baca_input("ID transaksi: ")
        kode = self.__baca_input("Kode alat yang dikembalikan: ")
        jumlah = self.__baca_angka("Jumlah dikembalikan: ")
        print("Kondisi: 1. BAIK  2. RUSAK_RINGAN  3. RUSAK_BERAT")
        peta = {"1": KondisiAlat.BAIK, "2": KondisiAlat.RUSAK_RINGAN,
                "3": KondisiAlat.RUSAK_BERAT}
        pil = self.__baca_input("Pilih kondisi: ")

        if pil not in peta:
            raise ValueError("Pilihan kondisi tidak valid.")
        self.__transaksi_mgr.proses_pengembalian(id_trx, kode, jumlah, peta[pil])
        print("Pengembalian berhasil dicatat.")

    def menu_laporan(self) -> None:
        while True:
            print("\n--- Laporan ---")
            print("1. Alat tersedia\n2. Alat sedang dipinjam\n3. Alat rusak\n"
                  "4. Riwayat mahasiswa (transaksi selesai)\n5. Transaksi aktif\n"
                  "6. Rincian alat yang belum kembali\n7. Statistik peminjaman\n"
                  "0. Kembali")
            pil = input("Pilih: ").strip()
            if pil == "0":
                return
            elif pil == "1":
                self.__tampilkan_daftar(self.__alat_mgr.daftar_tersedia(),
                                        "Tidak ada alat tersedia.")
            elif pil == "2":
                self.__tampilkan_daftar(self.__alat_mgr.daftar_dipinjam(),
                                        "Tidak ada alat yang sedang dipinjam.")
            elif pil == "3":
                self.__tampilkan_daftar(self.__alat_mgr.daftar_rusak(),
                                        "Tidak ada alat rusak.")
            elif pil == "4":
                nim = self.__baca_input("NIM mahasiswa: ")
                self.__jalankan_aman(lambda: self.__tampilkan_daftar(
                    self.__transaksi_mgr.riwayat_mahasiswa(nim),
                    "Belum ada riwayat."))
            elif pil == "5":
                self.__tampilkan_daftar(self.__transaksi_mgr.transaksi_aktif(),
                                        "Tidak ada transaksi aktif.")
            elif pil == "6":
                self.__tampilkan_daftar(self.__transaksi_mgr.alat_sedang_dipinjam(),
                                        "Tidak ada alat yang belum kembali.")
            elif pil == "7":
                self.__tampilkan_statistik()
            else:
                print("Pilihan tidak valid.")

    def __tampilkan_peringkat(self, judul: str, peringkat: list, deskripsi,
                              satuan: str, batas: int = 5) -> None:
        print(f"\n{judul}")
        if not peringkat:
            print("  Belum ada data peminjaman.")
            return
        tertinggi = peringkat[0][1]
        juara = [p for p in peringkat if p[1] == tertinggi]
        nama_juara = ", ".join(deskripsi(p) for p in juara)
        keterangan = "masing-masing " if len(juara) > 1 else ""
        print(f"  Terbanyak: {nama_juara} - {keterangan}{tertinggi} {satuan}")
        print(f"  Peringkat {batas} teratas:")
        for urutan, p in enumerate(peringkat[:batas], 1):
            print(f"   {urutan}. {deskripsi(p)} - {p[1]} {satuan}")

    def __tampilkan_statistik(self) -> None:
        print("\n=== STATISTIK PEMINJAMAN ===")
        print(f"Jumlah transaksi selesai : "
              f"{self.__transaksi_mgr.jumlah_transaksi_selesai()}")
        print(f"Jumlah transaksi aktif   : "
              f"{self.__transaksi_mgr.jumlah_transaksi_aktif()}")
        self.__tampilkan_peringkat(
            "Alat yang paling sering dipinjam:",
            self.__transaksi_mgr.alat_paling_sering_dipinjam(),
            lambda p: f"{p[0].nama} ({p[0].kode}, total {p[2]} unit)", "transaksi")
        self.__tampilkan_peringkat(
            "Mahasiswa yang paling sering meminjam:",
            self.__transaksi_mgr.mahasiswa_paling_sering_meminjam(),
            lambda p: f"{p[0].nama} ({p[0].nim})", "transaksi")