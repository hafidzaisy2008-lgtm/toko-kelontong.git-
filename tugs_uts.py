import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

DB_NAME = "Toko_Kelontong.db"


# =========================================================
# DATABASE
# =========================================================

def koneksi_db():
    return sqlite3.connect(DB_NAME)


def buat_database():
    with koneksi_db() as conn:
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS produk (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_produk TEXT NOT NULL,
                harga_modal INTEGER NOT NULL,
                harga_jual INTEGER NOT NULL,
                stok INTEGER NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tanggal TEXT NOT NULL,
                total_bayar INTEGER NOT NULL
            )
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS detail_transaksi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                id_transaksi INTEGER NOT NULL,
                id_produk INTEGER NOT NULL,
                jumlah INTEGER NOT NULL,
                subtotal INTEGER NOT NULL,
                FOREIGN KEY (id_transaksi) REFERENCES transaksi(id),
                FOREIGN KEY (id_produk) REFERENCES produk(id)
            )
        """)

        cur.execute("""
            INSERT OR IGNORE INTO users
            (username, password, role)
            VALUES (?, ?, ?)
        """, ("admin", "cristiano rozikin", "admin"))

        cur.execute("""
            INSERT OR IGNORE INTO users
            (username, password, role)
            VALUES (?, ?, ?)
        """, ("kasir", "cr messi", "kasir"))

        cur.execute("SELECT COUNT(*) FROM produk")

        if cur.fetchone()[0] == 0:
            produk = [
                ("Beras 5 Kg", 65000, 75000, 20),
                ("Gula 1 Kg", 15000, 18000, 30),
                ("Minyak Goreng", 19000, 22000, 25),
                ("Mie Instan", 2500, 3500, 100)
            ]

            cur.executemany("""
                INSERT INTO produk
                (nama_produk, harga_modal, harga_jual, stok)
                VALUES (?, ?, ?, ?)
            """, produk)


# =========================================================
# FORMAT RUPIAH
# =========================================================

def rupiah(angka):
    return "Rp" + f"{angka:,}".replace(",", ".")


# =========================================================
# APLIKASI
# =========================================================

class AplikasiToko:

    def __init__(self, root):

        self.root = root
        self.root.title("SMART-RETAIL - Toko Kelontong")
        self.root.geometry("900x600")
        self.root.resizable(False, False)

        self.user = None
        self.keranjang = {}

        buat_database()

        self.halaman_login()


    # =====================================================
    # HAPUS SEMUA WIDGET
    # =====================================================

    def bersihkan(self):

        for widget in self.root.winfo_children():
            widget.destroy()


    # =====================================================
    # LOGIN
    # =====================================================

    def halaman_login(self):

        self.bersihkan()

        frame = tk.Frame(self.root)
        frame.pack(expand=True)

        tk.Label(
            frame,
            text="SMART-RETAIL",
            font=("Arial", 28, "bold")
        ).pack(pady=10)

        tk.Label(
            frame,
            text="TOKO KELONTONG",
            font=("Arial", 14)
        ).pack(pady=5)

        tk.Label(
            frame,
            text="Username"
        ).pack(pady=(30, 5))

        self.entry_username = tk.Entry(
            frame,
            width=30
        )
        self.entry_username.pack()

        tk.Label(
            frame,
            text="Password"
        ).pack(pady=(15, 5))

        self.entry_password = tk.Entry(
            frame,
            width=30,
            show="*"
        )
        self.entry_password.pack()

        tk.Button(
            frame,
            text="LOGIN",
            width=25,
            command=self.login
        ).pack(pady=25)


    def login(self):

        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        with koneksi_db() as conn:

            cur = conn.cursor()

            cur.execute("""
                SELECT id, username, role
                FROM users
                WHERE username = ? AND password = ?
            """, (username, password))

            user = cur.fetchone()

        if user:

            self.user = {
                "id": user[0],
                "username": user[1],
                "role": user[2]
            }

            self.halaman_utama()

        else:

            messagebox.showerror(
                "Login Gagal",
                "Username atau password salah."
            )


    # =====================================================
    # MENU UTAMA
    # =====================================================

    def halaman_utama(self):

        self.bersihkan()

        tk.Label(
            self.root,
            text=f"SMART-RETAIL | {self.user['role'].upper()}",
            font=("Arial", 24, "bold")
        ).pack(pady=20)

        tk.Label(
            self.root,
            text=f"Selamat datang, {self.user['username']}"
        ).pack()

        frame = tk.Frame(self.root)
        frame.pack(pady=40)

        if self.user["role"] == "admin":

            tk.Button(
                frame,
                text="KELOLA PRODUK",
                width=25,
                height=2,
                command=self.halaman_produk
            ).grid(row=0, column=0, padx=10, pady=10)

        tk.Button(
            frame,
            text="TRANSAKSI PENJUALAN",
            width=25,
            height=2,
            command=self.halaman_transaksi
        ).grid(row=0, column=1, padx=10, pady=10)

        tk.Button(
            frame,
            text="RIWAYAT TRANSAKSI",
            width=25,
            height=2,
            command=self.halaman_riwayat
        ).grid(row=1, column=0, padx=10, pady=10)

        if self.user["role"] == "admin":

            tk.Button(
                frame,
                text="LAPORAN PENJUALAN",
                width=25,
                height=2,
                command=self.halaman_laporan
            ).grid(row=1, column=1, padx=10, pady=10)

        tk.Button(
            frame,
            text="LOGOUT",
            width=25,
            height=2,
            command=self.logout
        ).grid(row=2, column=0, columnspan=2, pady=20)


    # =====================================================
    # KELOLA PRODUK
    # =====================================================

    def halaman_produk(self):

        self.bersihkan()

        tk.Label(
            self.root,
            text="KELOLA PRODUK",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        frame_input = tk.Frame(self.root)
        frame_input.pack()

        tk.Label(frame_input, text="Nama").grid(row=0, column=0)
        self.entry_nama = tk.Entry(frame_input, width=25)
        self.entry_nama.grid(row=0, column=1, padx=5)

        tk.Label(frame_input, text="Harga Modal").grid(row=1, column=0)
        self.entry_modal = tk.Entry(frame_input, width=25)
        self.entry_modal.grid(row=1, column=1, padx=5)

        tk.Label(frame_input, text="Harga Jual").grid(row=2, column=0)
        self.entry_jual = tk.Entry(frame_input, width=25)
        self.entry_jual.grid(row=2, column=1, padx=5)

        tk.Label(frame_input, text="Stok").grid(row=3, column=0)
        self.entry_stok = tk.Entry(frame_input, width=25)
        self.entry_stok.grid(row=3, column=1, padx=5)

        tk.Button(
            frame_input,
            text="TAMBAH PRODUK",
            command=self.tambah_produk
        ).grid(row=4, column=0, columnspan=2, pady=10)

        self.tabel_produk = ttk.Treeview(
            self.root,
            columns=("id", "nama", "modal", "jual", "stok"),
            show="headings",
            height=12
        )

        self.tabel_produk.heading("id", text="ID")
        self.tabel_produk.heading("nama", text="Nama")
        self.tabel_produk.heading("modal", text="Harga Modal")
        self.tabel_produk.heading("jual", text="Harga Jual")
        self.tabel_produk.heading("stok", text="Stok")

        self.tabel_produk.pack(pady=15)

        tk.Button(
            self.root,
            text="HAPUS PRODUK",
            command=self.hapus_produk
        ).pack(side="left", padx=250)

        tk.Button(
            self.root,
            text="KEMBALI",
            command=self.halaman_utama
        ).pack(side="right", padx=250)

        self.tampilkan_produk_gui()


    def tampilkan_produk_gui(self):

        for item in self.tabel_produk.get_children():
            self.tabel_produk.delete(item)

        with koneksi_db() as conn:

            cur = conn.cursor()

            cur.execute("""
                SELECT id, nama_produk,
                       harga_modal,
                       harga_jual,
                       stok
                FROM produk
                ORDER BY id
            """)

            data = cur.fetchall()

        for row in data:

            self.tabel_produk.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    rupiah(row[2]),
                    rupiah(row[3]),
                    row[4]
                )
            )


    def tambah_produk(self):

        nama = self.entry_nama.get().strip()

        try:
            modal = int(self.entry_modal.get())
            jual = int(self.entry_jual.get())
            stok = int(self.entry_stok.get())

        except ValueError:

            messagebox.showerror(
                "Error",
                "Harga dan stok harus berupa angka."
            )
            return

        if not nama:

            messagebox.showerror(
                "Error",
                "Nama produk tidak boleh kosong."
            )
            return

        with koneksi_db() as conn:

            conn.execute("""
                INSERT INTO produk
                (nama_produk, harga_modal, harga_jual, stok)
                VALUES (?, ?, ?, ?)
            """, (nama, modal, jual, stok))

        messagebox.showinfo(
            "Berhasil",
            "Produk berhasil ditambahkan."
        )

        self.entry_nama.delete(0, tk.END)
        self.entry_modal.delete(0, tk.END)
        self.entry_jual.delete(0, tk.END)
        self.entry_stok.delete(0, tk.END)

        self.tampilkan_produk_gui()


    def hapus_produk(self):

        pilihan = self.tabel_produk.selection()

        if not pilihan:

            messagebox.showwarning(
                "Peringatan",
                "Pilih produk terlebih dahulu."
            )
            return

        data = self.tabel_produk.item(pilihan[0])
        id_produk = data["values"][0]

        konfirmasi = messagebox.askyesno(
            "Konfirmasi",
            "Yakin ingin menghapus produk ini?"
        )

        if konfirmasi:

            with koneksi_db() as conn:

                conn.execute(
                    "DELETE FROM produk WHERE id = ?",
                    (id_produk,)
                )

            self.tampilkan_produk_gui()


    # =====================================================
    # TRANSAKSI
    # =====================================================

    def halaman_transaksi(self):

        self.bersihkan()

        self.keranjang = {}

        tk.Label(
            self.root,
            text="TRANSAKSI PENJUALAN",
            font=("Arial", 22, "bold")
        ).pack(pady=15)

        frame = tk.Frame(self.root)
        frame.pack()

        tk.Label(
            frame,
            text="ID Produk"
        ).grid(row=0, column=0)

        self.entry_id_produk = tk.Entry(
            frame,
            width=15
        )
        self.entry_id_produk.grid(row=0, column=1)

        tk.Label(
            frame,
            text="Jumlah"
        ).grid(row=0, column=2)

        self.entry_jumlah = tk.Entry(
            frame,
            width=15
        )
        self.entry_jumlah.grid(row=0, column=3)

        tk.Button(
            frame,
            text="TAMBAH",
            command=self.tambah_keranjang
        ).grid(row=0, column=4, padx=10)

        self.tabel_keranjang = ttk.Treeview(
            self.root,
            columns=("id", "nama", "harga", "jumlah", "subtotal"),
            show="headings",
            height=12
        )

        self.tabel_keranjang.heading("id", text="ID")
        self.tabel_keranjang.heading("nama", text="Nama")
        self.tabel_keranjang.heading("harga", text="Harga")
        self.tabel_keranjang.heading("jumlah", text="Jumlah")
        self.tabel_keranjang.heading("subtotal", text="Subtotal")

        self.tabel_keranjang.pack(pady=20)

        self.label_total = tk.Label(
            self.root,
            text="TOTAL: Rp0",
            font=("Arial", 18, "bold")
        )

        self.label_total.pack()

        frame_bayar = tk.Frame(self.root)
        frame_bayar.pack(pady=10)

        tk.Label(
            frame_bayar,
            text="Uang Bayar"
        ).grid(row=0, column=0)

        self.entry_bayar = tk.Entry(
            frame_bayar,
            width=20
        )
        self.entry_bayar.grid(row=0, column=1)

        tk.Button(
            frame_bayar,
            text="BAYAR",
            command=self.proses_bayar
        ).grid(row=0, column=2, padx=10)

        tk.Button(
            self.root,
            text="KEMBALI",
            command=self.halaman_utama
        ).pack(pady=10)


    def tambah_keranjang(self):

        try:

            id_produk = int(
                self.entry_id_produk.get()
            )

            jumlah = int(
                self.entry_jumlah.get()
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "ID dan jumlah harus berupa angka."
            )
            return

        with koneksi_db() as conn:

            cur = conn.cursor()

            cur.execute("""
                SELECT nama_produk,
                       harga_jual,
                       stok
                FROM produk
                WHERE id = ?
            """, (id_produk,))

            produk = cur.fetchone()

        if not produk:

            messagebox.showerror(
                "Error",
                "Produk tidak ditemukan."
            )
            return

        nama, harga, stok = produk

        jumlah_lama = self.keranjang.get(
            id_produk,
            {}
        ).get("jumlah", 0)

        if jumlah_lama + jumlah > stok:

            messagebox.showerror(
                "Error",
                "Stok tidak mencukupi."
            )
            return

        self.keranjang[id_produk] = {
            "nama": nama,
            "harga": harga,
            "jumlah": jumlah_lama + jumlah
        }

        self.entry_id_produk.delete(0, tk.END)
        self.entry_jumlah.delete(0, tk.END)

        self.tampilkan_keranjang()


    def tampilkan_keranjang(self):

        for item in self.tabel_keranjang.get_children():
            self.tabel_keranjang.delete(item)

        total = 0

        for id_produk, item in self.keranjang.items():

            subtotal = (
                item["harga"] *
                item["jumlah"]
            )

            total += subtotal

            self.tabel_keranjang.insert(
                "",
                "end",
                values=(
                    id_produk,
                    item["nama"],
                    rupiah(item["harga"]),
                    item["jumlah"],
                    rupiah(subtotal)
                )
            )

        self.total_transaksi = total

        self.label_total.config(
            text=f"TOTAL: {rupiah(total)}"
        )


    def proses_bayar(self):

        if not self.keranjang:

            messagebox.showwarning(
                "Peringatan",
                "Keranjang masih kosong."
            )
            return

        try:

            bayar = int(
                self.entry_bayar.get()
            )

        except ValueError:

            messagebox.showerror(
                "Error",
                "Uang pembayaran harus berupa angka."
            )
            return

        total = self.total_transaksi

        if bayar < total:

            messagebox.showerror(
                "Pembayaran",
                f"Uang kurang {rupiah(total - bayar)}"
            )
            return

        kembalian = bayar - total

        try:

            with koneksi_db() as conn:

                cur = conn.cursor()

                tanggal = datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )

                cur.execute("""
                    INSERT INTO transaksi
                    (tanggal, total_bayar)
                    VALUES (?, ?)
                """, (tanggal, total))

                id_transaksi = cur.lastrowid

                for id_produk, item in self.keranjang.items():

                    subtotal = (
                        item["harga"] *
                        item["jumlah"]
                    )

                    cur.execute("""
                        INSERT INTO detail_transaksi
                        (id_transaksi,
                         id_produk,
                         jumlah,
                         subtotal)
                        VALUES (?, ?, ?, ?)
                    """, (
                        id_transaksi,
                        id_produk,
                        item["jumlah"],
                        subtotal
                    ))

                    cur.execute("""
                        UPDATE produk
                        SET stok = stok - ?
                        WHERE id = ?
                    """, (
                        item["jumlah"],
                        id_produk
                    ))

            self.cetak_struk(
                id_transaksi,
                bayar,
                kembalian
            )

        except sqlite3.Error as error:

            messagebox.showerror(
                "Database Error",
                str(error)
            )


    # =====================================================
    # CETAK STRUK
    # =====================================================

    def cetak_struk(
        self,
        id_transaksi,
        bayar,
        kembalian
    ):

        struk = tk.Toplevel(self.root)

        struk.title("Struk Pembelian")

        struk.geometry("450x500")

        teks = tk.Text(
            struk,
            font=("Courier New", 10)
        )

        teks.pack(
            fill="both",
            expand=True,
            padx=10,
            pady=10
        )

        teks.insert(
            tk.END,
            "=" * 40 + "\n"
        )

        teks.insert(
            tk.END,
            "        TOKO KELONTONG\n"
        )

        teks.insert(
            tk.END,
            "       SMART-RETAIL\n"
        )

        teks.insert(
            tk.END,
            "=" * 40 + "\n"
        )

        teks.insert(
            tk.END,
            f"Transaksi : {id_transaksi}\n"
        )

        teks.insert(
            tk.END,
            f"Tanggal   : "
            f"{datetime.now().strftime('%d-%m-%Y %H:%M')}\n"
        )

        teks.insert(
            tk.END,
            "-" * 40 + "\n"
        )

        for item in self.keranjang.values():

            subtotal = (
                item["harga"] *
                item["jumlah"]
            )

            teks.insert(
                tk.END,
                f"{item['nama']}\n"
            )

            teks.insert(
                tk.END,
                f"{item['jumlah']} x "
                f"{rupiah(item['harga'])}"
                f" = {rupiah(subtotal)}\n"
            )

        teks.insert(
            tk.END,
            "-" * 40 + "\n"
        )

        teks.insert(
            tk.END,
            f"TOTAL      : "
            f"{rupiah(self.total_transaksi)}\n"
        )

        teks.insert(
            tk.END,
            f"BAYAR      : "
            f"{rupiah(bayar)}\n"
        )

        teks.insert(
            tk.END,
            f"KEMBALIAN  : "
            f"{rupiah(kembalian)}\n"
        )

        teks.insert(
            tk.END,
            "=" * 40 + "\n"
        )

        teks.insert(
            tk.END,
            "    Terima kasih sudah berbelanja!\n"
        )

        teks.insert(
            tk.END,
            "=" * 40
        )

        teks.config(state="disabled")

        # Kosongkan keranjang
        self.keranjang = {}

        messagebox.showinfo(
            "Berhasil",
            "Transaksi berhasil disimpan."
        )


    # =====================================================
    # RIWAYAT TRANSAKSI
    # =====================================================

    def halaman_riwayat(self):

        self.bersihkan()

        tk.Label(
            self.root,
            text="RIWAYAT TRANSAKSI",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        tabel = ttk.Treeview(
            self.root,
            columns=("id", "tanggal", "total"),
            show="headings",
            height=15
        )

        tabel.heading("id", text="ID")
        tabel.heading("tanggal", text="Tanggal")
        tabel.heading("total", text="Total")

        tabel.pack(pady=10)

        with koneksi_db() as conn:

            cur = conn.cursor()

            cur.execute("""
                SELECT id,
                       tanggal,
                       total_bayar
                FROM transaksi
                ORDER BY id DESC
            """)

            data = cur.fetchall()

        for row in data:

            tabel.insert(
                "",
                "end",
                values=(
                    row[0],
                    row[1],
                    rupiah(row[2])
                )
            )

        tk.Button(
            self.root,
            text="KEMBALI",
            command=self.halaman_utama
        ).pack(pady=15)


    # =====================================================
    # LAPORAN
    # =====================================================

    def halaman_laporan(self):

        self.bersihkan()

        tk.Label(
            self.root,
            text="LAPORAN PENJUALAN",
            font=("Arial", 22, "bold")
        ).pack(pady=20)

        with koneksi_db() as conn:

            cur = conn.cursor()

            cur.execute("""
                SELECT COUNT(*),
                       COALESCE(SUM(total_bayar), 0)
                FROM transaksi
            """)

            jumlah, pendapatan = cur.fetchone()

            cur.execute("""
                SELECT p.nama_produk,
                       SUM(dt.jumlah)
                FROM detail_transaksi dt
                JOIN produk p
                ON p.id = dt.id_produk
                GROUP BY dt.id_produk
                ORDER BY SUM(dt.jumlah) DESC
                LIMIT 1
            """)

            terlaris = cur.fetchone()

        tk.Label(
            self.root,
            text=f"Jumlah transaksi : {jumlah}",
            font=("Arial", 14)
        ).pack(pady=10)

        tk.Label(
            self.root,
            text=f"Total penjualan : {rupiah(pendapatan)}",
            font=("Arial", 14)
        ).pack(pady=10)

        if terlaris:

            tk.Label(
                self.root,
                text=(
                    f"Produk terlaris : "
                    f"{terlaris[0]} "
                    f"({terlaris[1]} pcs)"
                ),
                font=("Arial", 14)
            ).pack(pady=10)

        else:

            tk.Label(
                self.root,
                text="Belum ada penjualan."
            ).pack(pady=10)

        tk.Button(
            self.root,
            text="KEMBALI",
            command=self.halaman_utama
        ).pack(pady=30)


    # =====================================================
    # LOGOUT
    # =====================================================

    def logout(self):

        self.user = None
        self.keranjang = {}

        self.halaman_login()


# =========================================================
# PROGRAM UTAMA
# =========================================================

if __name__ == "__main__":

    root = tk.Tk()

    app = AplikasiToko(root)

    root.mainloop()