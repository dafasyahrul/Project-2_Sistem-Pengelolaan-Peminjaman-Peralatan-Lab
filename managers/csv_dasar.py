import csv
import io
import os

def teks(baris: dict, kunci: str) -> str:
    return (baris.get(kunci) or "").strip()

def baca_csv(folder: str, nama_file: str) -> list[dict]:
    path = os.path.join(folder, nama_file)
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8-sig") as f:
        isi = f.read()
    if not isi.strip():
        return []
    header = isi.splitlines()[0]
    pemisah = ";" if header.count(";") > header.count(",") else ","
    return list(csv.DictReader(io.StringIO(isi), delimiter=pemisah))

def tulis_csv(folder: str, nama_file: str, kolom: list[str], baris: list[dict]) -> None:
    os.makedirs(folder, exist_ok=True)
    path = os.path.join(folder, nama_file)
    sementara = path + ".tmp"
    with open(sementara, "w", newline="", encoding="utf-8-sig") as f:
        penulis = csv.DictWriter(f, fieldnames=kolom, extrasaction="ignore")
        penulis.writeheader()
        penulis.writerows(baris)
    os.replace(sementara, path)