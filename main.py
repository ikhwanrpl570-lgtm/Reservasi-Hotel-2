"""Sistem Manajemen Reservasi Hotel - Paket 15
Teknologi: Python 3, Tkinter + ttkbootstrap, MySQL (XAMPP), mysql-connector-python, ttk.Treeview
Install  : pip install ttkbootstrap mysql-connector-python openpyxl reportlab
Siapkan  : nyalakan MySQL di XAMPP, import schema_baru.sql, lalu  python main.py
Login    : admin / 12345  (admin)   |   resepsionis / 12345
"""
import os
import sys
import shutil
import hashlib
import subprocess
import datetime as dt
import tkinter as tk
from tkinter import messagebox, filedialog

import mysql.connector
import ttkbootstrap as tb

DB = dict(host="localhost", user="root", password="", database="hotel_db")
FONT = ("Segoe UI", 11)


# ---------- Utilitas ----------
def run(sql, p=(), fetch=False):
    con = mysql.connector.connect(**DB)
    try:
        cur = con.cursor()
        cur.execute(sql, p)
        if fetch:
            return cur.fetchall()
        con.commit()
        return cur.lastrowid
    finally:
        con.close()


def sha(t):
    return hashlib.sha256(t.encode()).hexdigest()


def rupiah(x):
    return "Rp " + "{:,.0f}".format(float(x)).replace(",", ".")


def parse_tanggal(teks):
    """Terima 2026-2-6, 2026-02-06, atau 2026/2/6."""
    y, m, d = teks.strip().replace("/", "-").split("-")
    return dt.date(int(y), int(m), int(d))


def rapikan_id(*tabel):
    """Setelah hapus data, nomor ID berikutnya kembali ke (ID terbesar + 1), atau 1 jika tabel kosong."""
    for t in tabel:
        run(f"ALTER TABLE {t} AUTO_INCREMENT = 1")


def path_laporan(ext):
    """Folder 'laporan' di samping main.py; nama file tetap, jadi setiap ekspor menimpa file lama."""
    basis = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    folder = os.path.join(basis, "laporan")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "laporan_pendapatan." + ext)


def selesai(f):
    """Beri tahu lokasi file, lalu langsung buka."""
    try:
        os.startfile(f)  # Windows
    except (AttributeError, OSError):
        pass
    messagebox.showinfo("Sukses", f"Laporan tersimpan di:\n{f}")


def peringatan(pesan):
    messagebox.showwarning("Peringatan", pesan)


def buat_tree(parent, heads):
    """ttk.Treeview dengan scrollbar; baris asli disimpan di tv.data[iid]."""
    wrap = tb.Frame(parent)
    wrap.pack(fill="both", expand=True)
    ids = [str(i) for i in range(len(heads))]
    tv = tb.Treeview(wrap, columns=ids, show="headings", bootstyle="info", selectmode="browse")
    sb = tb.Scrollbar(wrap, orient="vertical", command=tv.yview)
    tv.configure(yscrollcommand=sb.set)
    for i, h in zip(ids, heads):
        tv.heading(i, text=h, anchor="center")
        tv.column(i, anchor="center", width=100, stretch=True)
    tv.pack(side="left", fill="both", expand=True)
    sb.pack(side="right", fill="y")
    tv.data = {}
    return tv


def isi(tv, rows, fmt=None):
    tv.delete(*tv.get_children())
    tv.data = {}
    for r in rows:
        iid = tv.insert("", "end", values=fmt(r) if fmt else r)
        tv.data[iid] = r


def terpilih(tv):
    s = tv.selection()
    return tv.data.get(s[0]) if s else None


def cari_exe(nama):
    p = shutil.which(nama)
    if p:
        return p
    for d in (r"C:\xampp\mysql\bin", r"D:\xampp\mysql\bin"):
        f = os.path.join(d, nama + ".exe")
        if os.path.exists(f):
            return f
    return None


# ---------- Kerangka tab master (Tamu & Kamar) ----------
class MasterTab(tb.Frame):
    FORM = LIST = CARI = ""
    FIELDS, HEAD = [], []

    def __init__(self, master):
        super().__init__(master, padding=10)
        f = tb.Labelframe(self, text=self.FORM, padding=15, bootstyle="info")
        f.pack(fill="x")
        self.v = {}
        for i, (label, key) in enumerate(self.FIELDS):
            self.v[key] = tk.StringVar()
            tb.Label(f, text=label).grid(row=i, column=0, sticky="w", pady=5, padx=(0, 40))
            tb.Entry(f, textvariable=self.v[key], width=34).grid(row=i, column=1, pady=5, sticky="w")
        bar = tb.Frame(f)
        bar.grid(row=len(self.FIELDS), column=0, columnspan=2, sticky="w", pady=(12, 0))
        self.b_simpan = tb.Button(bar, text="Simpan Baru", bootstyle="success", command=self.simpan)
        self.b_ubah = tb.Button(bar, text="Update / Ubah", bootstyle="warning", command=self.ubah)
        self.b_hapus = tb.Button(bar, text="Hapus Data", bootstyle="danger", command=self.hapus)
        for b in (self.b_simpan, self.b_ubah, self.b_hapus,
                  tb.Button(bar, text="Reset Form", bootstyle="secondary", command=self.reset)):
            b.pack(side="left", padx=(0, 4))

        g = tb.Labelframe(self, text=self.LIST, padding=15, bootstyle="info")
        g.pack(fill="both", expand=True, pady=(12, 0))
        top = tb.Frame(g)
        top.pack(fill="x", pady=(0, 8))
        tb.Label(top, text=self.CARI).pack(side="left")
        self.q = tk.StringVar()
        e = tb.Entry(top, textvariable=self.q, width=32)
        e.pack(side="left", padx=8)
        e.bind("<Return>", lambda ev: self.muat())
        tb.Button(top, text="Cari", bootstyle="info-outline", command=self.muat).pack(side="left", padx=2)
        tb.Button(top, text="Reset", bootstyle="secondary-outline", command=self.reset_cari).pack(side="left", padx=2)
        self.tv = buat_tree(g, self.HEAD)
        self.tv.bind("<<TreeviewSelect>>", lambda ev: self.pilih())
        self.muat()

    def form_dari(self, r):
        return r[1:]

    def pilih(self):
        r = terpilih(self.tv)
        if r:
            for var, x in zip(self.v.values(), self.form_dari(r)):
                var.set("" if x is None else x)

    def reset(self):
        for var in self.v.values():
            var.set("")
        self.tv.selection_remove(*self.tv.selection())

    def reset_cari(self):
        self.q.set("")
        self.muat()

    def isian(self):
        return [var.get().strip() for var in self.v.values()]


# ---------- Tab 1: Data Tamu ----------
class TamuTab(MasterTab):
    FORM = "Formulir Kelola Data Tamu"
    LIST = "Daftar Tamu Terdaftar & Pencarian"
    CARI = "Cari (Nama/Telp):"
    FIELDS = [("Nama Tamu:", "nama"), ("Alamat:", "alamat"), ("No. Telepon:", "telp"), ("Email:", "email")]
    HEAD = ["ID", "Nama Tamu", "Alamat", "Telepon", "Email"]

    def muat(self):
        k = f"%{self.q.get().strip()}%"
        isi(self.tv, run("""SELECT id_tamu,nama,alamat,telepon,email FROM tamu
                            WHERE nama LIKE %s OR telepon LIKE %s ORDER BY id_tamu""", (k, k), True))

    def _valid(self):
        nama, alamat, telp, email = self.isian()
        if not nama or not telp:
            peringatan("Nama dan No. Telepon wajib diisi.")
            return None
        if email and "@" not in email:
            peringatan("Format email tidak valid.")
            return None
        return nama, alamat, telp, email

    def simpan(self):
        d = self._valid()
        if d:
            run("INSERT INTO tamu (nama,alamat,telepon,email) VALUES (%s,%s,%s,%s)", d)
            self.reset()
            self.muat()

    def ubah(self):
        r = terpilih(self.tv)
        if not r:
            return peringatan("Pilih data tamu di tabel terlebih dahulu.")
        d = self._valid()
        if d:
            run("UPDATE tamu SET nama=%s,alamat=%s,telepon=%s,email=%s WHERE id_tamu=%s", d + (r[0],))
            self.muat()

    def hapus(self):
        r = terpilih(self.tv)
        if not r:
            return peringatan("Pilih data tamu di tabel terlebih dahulu.")
        if not messagebox.askyesno("Konfirmasi", f"Hapus tamu '{r[1]}'?"):
            return
        try:
            run("DELETE FROM tamu WHERE id_tamu=%s", (r[0],))
        except mysql.connector.Error:
            return peringatan("Tamu tidak bisa dihapus karena masih punya riwayat reservasi.")
        rapikan_id("tamu")
        self.reset()
        self.muat()


# ---------- Tab 2: Data Kamar (CRUD + pencarian) ----------
class KamarTab(MasterTab):
    FORM = "Formulir Kelola Data Kamar"
    LIST = "Daftar Inventaris Kamar & Pencarian"
    CARI = "Cari (No/Tipe):"
    FIELDS = [("Nomor Kamar:", "no"), ("Tipe Kamar:", "tipe"), ("Tarif per Malam (Rp):", "tarif")]
    HEAD = ["ID", "Nomor Kamar", "Tipe Kamar", "Tarif / Malam", "Status"]

    def form_dari(self, r):
        return [r[1], r[2], int(r[3])]

    def muat(self):
        k = f"%{self.q.get().strip()}%"
        isi(self.tv, run("""SELECT id_kamar,nomor_kamar,tipe_kamar,tarif_per_malam,status FROM kamar
                            WHERE nomor_kamar LIKE %s OR tipe_kamar LIKE %s ORDER BY id_kamar""", (k, k), True),
            fmt=lambda r: (r[0], r[1], r[2], rupiah(r[3]), r[4]))

    def _valid(self):
        no, tipe, tarif = self.isian()
        try:
            tarif = float(tarif.replace(".", ""))
            assert tarif > 0
        except (ValueError, AssertionError):
            peringatan("Tarif harus berupa angka lebih dari 0.")
            return None
        if not no or not tipe:
            peringatan("Nomor dan tipe kamar wajib diisi.")
            return None
        return no, tipe, tarif

    def simpan(self):
        d = self._valid()
        if d:
            try:
                run("INSERT INTO kamar (nomor_kamar,tipe_kamar,tarif_per_malam) VALUES (%s,%s,%s)", d)
            except mysql.connector.Error:
                return peringatan("Nomor kamar sudah terdaftar.")
            self.reset()
            self.muat()

    def ubah(self):
        r = terpilih(self.tv)
        if not r:
            return peringatan("Pilih kamar di tabel terlebih dahulu.")
        d = self._valid()
        if d:
            try:
                run("UPDATE kamar SET nomor_kamar=%s,tipe_kamar=%s,tarif_per_malam=%s WHERE id_kamar=%s", d + (r[0],))
            except mysql.connector.Error:
                return peringatan("Nomor kamar sudah dipakai kamar lain.")
            self.muat()

    def hapus(self):
        r = terpilih(self.tv)
        if not r:
            return peringatan("Pilih kamar di tabel terlebih dahulu.")
        if r[4] == "Terisi":
            return peringatan("Kamar sedang terisi, tidak bisa dihapus.")
        if not messagebox.askyesno("Konfirmasi", f"Hapus kamar {r[1]}?"):
            return
        try:
            run("DELETE FROM kamar WHERE id_kamar=%s", (r[0],))
        except mysql.connector.Error:
            return peringatan("Kamar tidak bisa dihapus karena sudah punya riwayat reservasi.")
        rapikan_id("kamar")
        self.reset()
        self.muat()


# ---------- Tab 3: Reservasi & Check-In/Out ----------
class ReservasiTab(tb.Frame):
    HEAD = ["ID Res", "Nama Tamu", "No Kamar", "Check-In", "Check-Out", "Status"]

    def __init__(self, master):
        super().__init__(master, padding=10)
        f = tb.Labelframe(self, text="Formulir Transaksi & Check-In / Check-Out", padding=15, bootstyle="info")
        f.pack(fill="x")
        self.v = {k: tk.StringVar() for k in ("tamu", "kamar", "masuk", "keluar")}
        self.metode = tk.StringVar(value="Tunai")

        def baris(r, c, teks, w):
            tb.Label(f, text=teks).grid(row=r, column=c, sticky="w", pady=5, padx=(0, 15))
            w.grid(row=r, column=c + 1, pady=5, padx=(0, 40), sticky="w")

        baris(0, 0, "ID Tamu:", tb.Entry(f, textvariable=self.v["tamu"], width=22))
        baris(0, 2, "ID Kamar:", tb.Entry(f, textvariable=self.v["kamar"], width=22))
        baris(1, 0, "Check-In (YYYY-MM-DD):", tb.Entry(f, textvariable=self.v["masuk"], width=22))
        baris(1, 2, "Check-Out (YYYY-MM-DD):", tb.Entry(f, textvariable=self.v["keluar"], width=22))
        baris(2, 0, "Metode Pembayaran:", tb.Combobox(f, textvariable=self.metode, state="readonly", width=20,
                                                      values=["Tunai", "Transfer", "Kartu"]))
        bar = tb.Frame(f)
        bar.grid(row=3, column=0, columnspan=4, sticky="w", pady=(12, 0))
        self.b_hapus = tb.Button(bar, text="Hapus Reservasi", bootstyle="danger", command=self.hapus)
        for b in (tb.Button(bar, text="Proses Check-In", bootstyle="success", command=self.checkin),
                  tb.Button(bar, text="Proses Check-Out & Tagihan", bootstyle="warning", command=self.checkout),
                  self.b_hapus,
                  tb.Button(bar, text="Reset Form", bootstyle="secondary", command=self.reset)):
            b.pack(side="left", padx=(0, 4))

        g = tb.Labelframe(self, text="Riwayat Transaksi Reservasi & Status", padding=15, bootstyle="info")
        g.pack(fill="both", expand=True, pady=(12, 0))
        self.tv = buat_tree(g, self.HEAD)
        self.tv.bind("<<TreeviewSelect>>", lambda e: self.pilih())
        self.muat()

    def muat(self):
        isi(self.tv, run("""SELECT r.id_reservasi,t.nama,k.nomor_kamar,r.tgl_checkin,r.tgl_checkout,
                            r.status,r.id_tamu,r.id_kamar
                            FROM reservasi r JOIN tamu t ON t.id_tamu=r.id_tamu
                            JOIN kamar k ON k.id_kamar=r.id_kamar ORDER BY r.id_reservasi""", fetch=True))

    def pilih(self):
        r = terpilih(self.tv)
        if r:
            self.v["tamu"].set(r[6])
            self.v["kamar"].set(r[7])
            self.v["masuk"].set(str(r[3]))
            self.v["keluar"].set(str(r[4]))

    def reset(self):
        for var in self.v.values():
            var.set("")
        self.metode.set("Tunai")
        self.tv.selection_remove(*self.tv.selection())

    def checkin(self):
        try:
            idt, idk = int(self.v["tamu"].get()), int(self.v["kamar"].get())
            a = parse_tanggal(self.v["masuk"].get())
            b = parse_tanggal(self.v["keluar"].get())
        except ValueError:
            return peringatan("ID harus angka dan tanggal berformat YYYY-MM-DD.")
        if b <= a:
            return peringatan("Tanggal check-out harus setelah check-in.")
        if not run("SELECT 1 FROM tamu WHERE id_tamu=%s", (idt,), True):
            return peringatan("ID Tamu tidak ditemukan.")
        kamar = run("SELECT nomor_kamar,status FROM kamar WHERE id_kamar=%s", (idk,), True)
        if not kamar:
            return peringatan("ID Kamar tidak ditemukan.")
        if kamar[0][1] != "Tersedia":
            return peringatan(f"Kamar {kamar[0][0]} sedang terisi.")
        run("""INSERT INTO reservasi (id_tamu,id_kamar,tgl_checkin,tgl_checkout,status)
               VALUES (%s,%s,%s,%s,'Check-In')""", (idt, idk, a, b))
        run("UPDATE kamar SET status='Terisi' WHERE id_kamar=%s", (idk,))
        messagebox.showinfo("Check-In", f"Check-in kamar {kamar[0][0]} berhasil.")
        self.reset()
        self.muat()

    def checkout(self):
        r = terpilih(self.tv)
        if not r:
            return peringatan("Pilih reservasi di tabel terlebih dahulu.")
        if r[5] != "Check-In":
            return peringatan("Reservasi ini sudah Check-Out.")
        try:
            keluar = parse_tanggal(self.v["keluar"].get())
        except ValueError:
            return peringatan("Tanggal check-out harus berformat YYYY-MM-DD.")
        malam = max(1, (keluar - r[3]).days)
        tarif = run("SELECT tarif_per_malam FROM kamar WHERE id_kamar=%s", (r[7],), True)[0][0]
        total, metode = tarif * malam, self.metode.get()
        run("UPDATE reservasi SET tgl_checkout=%s,status='Check-Out' WHERE id_reservasi=%s", (keluar, r[0]))
        run("UPDATE kamar SET status='Tersedia' WHERE id_kamar=%s", (r[7],))
        run("INSERT INTO pembayaran (id_reservasi,tgl_bayar,total_biaya,metode) VALUES (%s,%s,%s,%s)",
            (r[0], keluar, total, metode))
        messagebox.showinfo("Tagihan",
                            f"Tamu        : {r[1]}\nKamar       : {r[2]}\nLama inap   : {malam} malam\n"
                            f"Tarif/malam : {rupiah(tarif)}\nTOTAL       : {rupiah(total)}\nMetode      : {metode}")
        self.reset()
        self.muat()

    def hapus(self):
        r = terpilih(self.tv)
        if not r:
            return peringatan("Pilih reservasi di tabel terlebih dahulu.")
        if not messagebox.askyesno("Konfirmasi", f"Hapus reservasi #{r[0]}?"):
            return
        run("DELETE FROM pembayaran WHERE id_reservasi=%s", (r[0],))
        run("DELETE FROM reservasi WHERE id_reservasi=%s", (r[0],))
        rapikan_id("pembayaran", "reservasi")
        if r[5] == "Check-In":
            run("UPDATE kamar SET status='Tersedia' WHERE id_kamar=%s", (r[7],))
        self.reset()
        self.muat()


# ---------- Tab 4: Statistik & Laporan ----------
class StatistikTab(tb.Frame):
    HEAD = ["ID Bayar", "ID Res", "Nama Tamu", "No Kamar", "Tgl Bayar", "Total Biaya", "Metode"]

    def __init__(self, master, admin):
        super().__init__(master, padding=10)
        kartu = tb.Frame(self)
        kartu.pack(fill="x")
        self.k = {}
        for i, (key, style) in enumerate((("tamu", "info"), ("kamar", "success"), ("uang", "warning"))):
            self.k[key] = tb.Label(kartu, bootstyle=f"inverse-{style}", font=("Segoe UI", 16, "bold"), padding=10)
            self.k[key].grid(row=0, column=i, sticky="ew", padx=2)
            kartu.columnconfigure(i, weight=1)

        g = tb.Labelframe(self, text="Rekapitulasi Pembayaran & Pendapatan", padding=15, bootstyle="info")
        g.pack(fill="both", expand=True, pady=(12, 0))
        self.tv = buat_tree(g, self.HEAD)

        bar = tb.Frame(self)
        bar.pack(fill="x", pady=(10, 0))
        if admin:
            tb.Button(bar, text="Backup DB", bootstyle="secondary", command=self.backup).pack(side="left", padx=2)
            tb.Button(bar, text="Restore DB", bootstyle="warning-outline", command=self.restore).pack(side="left", padx=2)
        for teks, style, cmd in (("Refresh", "secondary", self.muat), ("Ekspor PDF", "danger", self.pdf),
                                 ("Ekspor Excel", "success", self.excel), ("Tampilkan Grafik", "info", self.grafik)):
            tb.Button(bar, text=teks, bootstyle=style, command=cmd).pack(side="right", padx=2)
        self.muat()

    def muat(self):
        q = lambda s: run(s, fetch=True)[0][0]
        tersedia = q("SELECT COUNT(*) FROM kamar WHERE status='Tersedia'")
        self.total = q("SELECT IFNULL(SUM(total_biaya),0) FROM pembayaran")
        self.k["tamu"]["text"] = f"Total Tamu: {q('SELECT COUNT(*) FROM tamu')}"
        self.k["kamar"]["text"] = f"Kamar Tersedia: {tersedia}"
        self.k["uang"]["text"] = f"Total Pendapatan: {rupiah(self.total)}"
        self.rows = run("""SELECT p.id_pembayaran,p.id_reservasi,t.nama,k.nomor_kamar,p.tgl_bayar,p.total_biaya,p.metode
                           FROM pembayaran p JOIN reservasi r ON r.id_reservasi=p.id_reservasi
                           JOIN tamu t ON t.id_tamu=r.id_tamu JOIN kamar k ON k.id_kamar=r.id_kamar
                           ORDER BY p.id_pembayaran""", fetch=True)
        isi(self.tv, self.rows, fmt=lambda r: (r[0], r[1], r[2], r[3], r[4], rupiah(r[5]), r[6]))

    def grafik(self):
        data = run("SELECT DATE_FORMAT(tgl_bayar,'%Y-%m'),SUM(total_biaya) FROM pembayaran GROUP BY 1 ORDER BY 1",
                   fetch=True)
        win = tk.Toplevel(self)
        win.title("Grafik Pendapatan per Bulan")
        W, H, kiri, atas, bawah = 780, 440, 40, 70, 50
        c = tk.Canvas(win, width=W, height=H, bg="white", highlightthickness=0)
        c.pack()
        c.create_text(W / 2, 25, text="Pendapatan per Bulan", font=("Segoe UI", 14, "bold"))
        if not data:
            return c.create_text(W / 2, H / 2, text="Belum ada data pembayaran", font=FONT)
        mx = max(float(v) for _, v in data) or 1
        slot = (W - kiri * 2) / len(data)
        c.create_line(kiri, H - bawah, W - kiri, H - bawah)
        for i, (bln, v) in enumerate(data):
            tinggi = (H - atas - bawah) * float(v) / mx
            x = kiri + i * slot + slot * 0.2
            c.create_rectangle(x, H - bawah - tinggi, x + slot * 0.6, H - bawah, fill="#3498db", outline="")
            c.create_text(x + slot * 0.3, H - bawah - tinggi - 12, text=rupiah(v), font=("Segoe UI", 9))
            c.create_text(x + slot * 0.3, H - bawah + 16, text=bln, font=("Segoe UI", 10))

    def excel(self):
        try:
            from openpyxl import Workbook
        except ImportError:
            return peringatan("Install dulu: pip install openpyxl")
        f = path_laporan("xlsx")
        wb = Workbook()
        ws = wb.active
        ws.append(self.HEAD)
        for r in self.rows:
            ws.append([r[0], r[1], r[2], r[3], str(r[4]), float(r[5]), r[6]])
        ws.append(["", "", "", "", "TOTAL", float(self.total), ""])
        from openpyxl.styles import Font, PatternFill, Alignment
        for c in ws[1]:
            c.font = Font(bold=True, color="FFFFFF")
            c.fill = PatternFill("solid", fgColor="3498DB")
            c.alignment = Alignment(horizontal="center")
        for kol in ws.columns:
            ws.column_dimensions[kol[0].column_letter].width = max(len(str(c.value or "")) for c in kol) + 4
        for baris in ws.iter_rows(min_row=2, min_col=6, max_col=6):
            baris[0].number_format = '"Rp" #,##0'
        try:
            wb.save(f)
        except PermissionError:
            return peringatan("File laporan_pendapatan.xlsx sedang dibuka. Tutup dulu, lalu coba lagi.")
        selesai(f)

    def pdf(self):
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        except ImportError:
            return peringatan("Install dulu: pip install reportlab")
        f = path_laporan("pdf")
        st = getSampleStyleSheet()
        data = [self.HEAD] + [[r[0], r[1], r[2], r[3], str(r[4]), rupiah(r[5]), r[6]] for r in self.rows]
        tabel = Table(data, repeatRows=1)
        tabel.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#3498db")),
                                   ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                                   ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                                   ("ALIGN", (0, 0), (-1, -1), "CENTER")]))
        isi_pdf = [Paragraph("Laporan Pembayaran & Pendapatan Hotel", st["Title"]), tabel, Spacer(1, 12),
                   Paragraph(f"<b>Total Pendapatan: {rupiah(self.total)}</b>", st["Heading3"])]
        try:
            SimpleDocTemplate(f, pagesize=landscape(A4)).build(isi_pdf)
        except PermissionError:
            return peringatan("File laporan_pendapatan.pdf sedang dibuka. Tutup dulu, lalu coba lagi.")
        selesai(f)

    def _args(self):
        a = ["-u", DB["user"]]
        if DB["password"]:
            a.append("-p" + DB["password"])
        return a

    def backup(self):
        exe = cari_exe("mysqldump")
        if not exe:
            return peringatan("mysqldump tidak ditemukan. Pastikan XAMPP terpasang di C:\\xampp.")
        f = filedialog.asksaveasfilename(defaultextension=".sql", initialfile="backup_hotel.sql",
                                         filetypes=[("SQL", "*.sql")])
        if f:
            ok = subprocess.run([exe, *self._args(), "--result-file=" + f, DB["database"]]).returncode == 0
            messagebox.showinfo("Backup", "Backup berhasil." if ok else "Backup gagal.")

    def restore(self):
        exe = cari_exe("mysql")
        if not exe:
            return peringatan("mysql tidak ditemukan. Pastikan XAMPP terpasang di C:\\xampp.")
        f = filedialog.askopenfilename(filetypes=[("SQL", "*.sql")])
        if f and messagebox.askyesno("Restore", "Data saat ini akan ditimpa. Lanjutkan?"):
            with open(f, "rb") as fh:
                ok = subprocess.run([exe, *self._args(), DB["database"]], stdin=fh).returncode == 0
            messagebox.showinfo("Restore", "Restore berhasil." if ok else "Restore gagal.")
            self.muat()


# ---------- Aplikasi (login + jendela utama) ----------
class App:
    def __init__(self):
        self.root = tb.Window(themename="flatly")
        self.root.title("Sistem Manajemen Reservasi Hotel - Paket 15")
        st = self.root.style
        st.configure("Treeview", rowheight=28, font=FONT)
        st.configure("Treeview.Heading", font=("Segoe UI", 12))
        st.configure("TNotebook.Tab", background="#2c3e50", foreground="white", padding=(20, 10), font=FONT)
        st.map("TNotebook.Tab", background=[("selected", "white"), ("active", "#34495e")],
               foreground=[("selected", "#222222"), ("active", "white")])
        self.frame = None
        self.login()

    def ganti(self, frame):
        if self.frame:
            self.frame.destroy()
        self.frame = frame
        frame.pack(fill="both", expand=True)

    def login(self):
        try:
            self.root.state("normal")
        except tk.TclError:
            pass
        self.root.geometry("520x400")
        f = tb.Frame(self.root, padding=25)
        tb.Label(f, text="LOGIN HOTEL", font=("Segoe UI", 24, "bold")).pack(pady=(5, 20))
        tb.Label(f, text="Username:").pack(anchor="w")
        self.u = tb.Entry(f)
        self.u.pack(fill="x", pady=(2, 12), ipady=4)
        tb.Label(f, text="Password:").pack(anchor="w")
        self.p = tb.Entry(f, show="*")
        self.p.pack(fill="x", pady=(2, 18), ipady=4)
        tb.Button(f, text="LOGIN", bootstyle="success", command=self.cek).pack(fill="x", ipady=8)
        tb.Label(f, text="Default: username 'admin' | password '12345'", bootstyle="secondary",
                 font=("Segoe UI", 10, "italic")).pack(pady=15)
        self.root.bind("<Return>", lambda e: self.cek())
        self.ganti(f)
        self.u.focus()

    def cek(self):
        r = run("SELECT role FROM pengguna WHERE username=%s AND password_hash=%s",
                (self.u.get().strip(), sha(self.p.get())), True)
        if not r:
            return peringatan("Username atau password salah.")
        self.root.unbind("<Return>")
        self.utama(r[0][0] == "admin")

    def utama(self, admin):
        try:
            self.root.state("zoomed")
        except tk.TclError:
            self.root.geometry("1250x800")
        f = tb.Frame(self.root, padding=(12, 6))
        head = tb.Frame(f)
        head.pack(fill="x", pady=(0, 10))
        tb.Label(head, text="SISTEM MANAJEMEN RESERVASI HOTEL", font=("Segoe UI", 22, "bold")).pack(side="left")
        tb.Button(head, text="Logout", bootstyle="danger-outline", command=self.login).pack(side="right")
        nb = tb.Notebook(f)
        nb.pack(fill="both", expand=True)
        tabs = [(TamuTab(nb), "1. Data Tamu"), (KamarTab(nb), "2. Data Kamar"),
                (ReservasiTab(nb), "3. Reservasi & Check-In"), (StatistikTab(nb, admin), "4. Statistik & Laporan")]
        for w, n in tabs:
            nb.add(w, text=n)
        if not admin:  # resepsionis tidak boleh menghapus data
            for w in (tabs[0][0], tabs[1][0], tabs[2][0]):
                w.b_hapus.pack_forget()
            for b in (tabs[1][0].b_simpan, tabs[1][0].b_ubah):  # tarif & data kamar hanya diubah admin
                b.pack_forget()
        nb.bind("<<NotebookTabChanged>>", lambda e: nb.nametowidget(nb.select()).muat())
        self.ganti(f)


def siapkan_user():
    # Samakan tanggal bayar dengan tanggal check-out (memperbaiki data lama)
    run("""UPDATE pembayaran p JOIN reservasi r ON r.id_reservasi=p.id_reservasi
           SET p.tgl_bayar=r.tgl_checkout WHERE p.tgl_bayar<>r.tgl_checkout""")
    if not run("SELECT COUNT(*) FROM pengguna", fetch=True)[0][0]:
        for u, r in (("admin", "admin"), ("resepsionis", "resepsionis")):
            run("INSERT INTO pengguna (username,password_hash,role) VALUES (%s,%s,%s)", (u, sha("12345"), r))


if __name__ == "__main__":
    try:
        siapkan_user()
    except mysql.connector.Error as e:
        messagebox.showerror("Koneksi Gagal", "Tidak bisa terhubung ke MySQL.\nPastikan MySQL di XAMPP menyala dan "
                                              f"schema_baru.sql sudah diimport.\n\n{e}")
    else:
        App().root.mainloop()