import random
from datetime import datetime

# ========== DATA ==========
data_pengguna = {}
akun_admin = {"admin": "123"}
norek_terakhir_ditambah = None
jumlah_pin_gagal = {}  # norek -> int (jumlah salah PIN)

# Harga dinamis (akan dihasilkan saat pelanggan login)
harga_emas_sekarang = 1_000_000
harga_tanah_sekarang = 500_000

#--------- MENU ADMIN---------
def tambah_nasabah():
    global norek_terakhir_ditambah
    print("\n=== Tambah Nasabah ===")

    nama = input("Masukkan Nama: ")
    norek = input_norek()
    if norek in data_pengguna:
        print("Nomor rekening sudah terdaftar!")
        return
    pin = input_pin()

    while True:
        try:
            saldo_awal = int(input("Masukkan saldo awal (minimal 100000): "))
        except:
            print("Input tidak valid!")
            continue

        if saldo_awal >= 100000:
            break
        print("Saldo awal minimal Rp 100.000!")

    data_pengguna[norek] = {
        "nama": nama,
        "pin": pin,
        "saldo": saldo_awal,
        "saldo_riwayat": [f"+{saldo_awal} (Saldo Awal)"],
        "investasi": {"emas":0, "tanah":0, "deposito":0},
        "investasi_riwayat": [],
        "blocked": False
    }
    jumlah_pin_gagal[norek] = 0

    norek_terakhir_ditambah = norek
    print("Nasabah berhasil ditambahkan!")

def update_nasabah():
    print("\n=== Update Nasabah ===")
    norek = input("Masukkan norek yang ingin diupdate: ")

    if norek not in data_pengguna:
        print("Data tidak ditemukan!")
        return

    print("\nApa yang ingin diubah?")
    print("1. Ubah Nama")
    print("2. Ubah PIN")
    print("3. Ubah Nomor Rekening")
    pilihan = input("Pilih menu: ")

    # ---- 1. Ubah Nama ----
    if pilihan == "1":
        nama_baru = input("Masukkan nama baru: ")
        data_pengguna[norek]["nama"] = nama_baru
        print("Nama berhasil diupdate!")

    # ---- 2. Ubah PIN ----
    elif pilihan == "2":
        pin_baru = input_pin()
        data_pengguna[norek]["pin"] = pin_baru
        print("PIN berhasil diupdate!")

    # ---- 3. Ubah Nomor Rekening ----
    elif pilihan == "3":
        norek_baru = input_norek()

        if norek_baru in data_pengguna:
            print("Norek baru sudah digunakan!")
            return

        # Pindahkan data lama ke data baru
        data_pengguna[norek_baru] = data_pengguna[norek]
        del data_pengguna[norek]

        # Pindahkan juga jumlah_pin_gagal
        jumlah_pin_gagal[norek_baru] = jumlah_pin_gagal.get(norek, 0)
        if norek in jumlah_pin_gagal:
            del jumlah_pin_gagal[norek]

        print(f"Norek berhasil diubah dari {norek} ke {norek_baru}")

    else:
        print("Pilihan tidak valid!")


def lihat_data():
    print("\n=== Data Semua Nasabah ===")
    if not data_pengguna:
        print("Belum ada data nasabah.")
        return
    for norek, info in data_pengguna.items():
        status = "BLOKIR" if info.get("blocked", False) else "AKTIF"
        print(f"Norek: {norek} | Nama: {info['nama']} | Saldo: {format_rp(info['saldo'])} | Status: {status}")

#------ HAPUS NASABAH ---------
def hapus_nasabah():
    print("\n=== Hapus Nasabah ===")
    norek = input("Masukkan nomor rekening yang ingin dihapus: ")

    if norek not in data_pengguna:
        print("Data tidak ditemukan!")
        return

    # Jika nasabah masih punya saldo, minta konfirmasi
    saldo = data_pengguna[norek]["saldo"]
    if saldo > 0:
        print(f"Nasabah masih memiliki saldo {format_rp(saldo)}")
        yakin = input("Apakah tetap ingin menghapus? (y/n): ").lower()
        if yakin != "y":
            print("Penghapusan dibatalkan.")
            return

    # Hapus data
    del data_pengguna[norek]

    # Hapus riwayat jumlah PIN gagal jika ada
    if norek in jumlah_pin_gagal:
        del jumlah_pin_gagal[norek]

    # Jika yang dihapus adalah rekening terakhir ditambah, reset variabel
    global norek_terakhir_ditambah
    if norek_terakhir_ditambah == norek:
        norek_terakhir_ditambah = None

    print(f"Nasabah dengan rekening {norek} berhasil dihapus!")

#------- BUKA BLOKIR NASABAH ---------
def buka_blokir_nasabah():
    print("\n=== Buka Blokir Nasabah ===")
    norek = input("Masukkan nomor rekening: ")

    if norek not in data_pengguna:
        print("Nomor rekening tidak ditemukan!")
        return

    if not data_pengguna[norek].get("blocked", False):
        print("Rekening ini tidak dalam keadaan terblokir.")
        return

    # Memastikan admin yakin membuka blokir
    yakin = input("Rekening terblokir. Buka blokir? (y/n): ").lower()
    if yakin != "y":
        print("Pembukaan blokir dibatalkan.")
        return

    data_pengguna[norek]["blocked"] = False
    data_pengguna[norek]["saldo_riwayat"].append("!BLOKIR DIBUKA oleh admin")
    print(f"Rekening {norek} berhasil dibuka kembali!")


#--------- MENU NASABAH------------
def setor_uang(norek):
    if data_pengguna[norek].get("blocked", False):
        print("Rekening diblokir.")
        return
    try:
        jumlah = int(input("Masukkan jumlah setor: "))
    except:
        print("Jumlah tidak valid!")
        return
    data_pengguna[norek]["saldo"] += jumlah
    data_pengguna[norek]["saldo_riwayat"].append(f"+{jumlah} ({waktu_sekarang()})")
    print(f"Berhasil setor {format_rp(jumlah)}")
    cetak_struk(norek, data_pengguna[norek]["nama"], "Setor Tunai", jumlah, data_pengguna[norek]["saldo"])

def tarik_uang(norek):
    if data_pengguna[norek].get("blocked", False):
        print("Rekening diblokir.")
        return

    saldo = data_pengguna[norek]["saldo"]

    if saldo <= 50000:
        print("Tidak bisa tarik! saldo harus minimal Rp50.000 tersisa")
        return

    try:
        jumlah = int(input("Masukkan jumlah tarik: "))
    except:
        print("Jumlah tidak valid!")
        return

    if jumlah <= 0:
        print("Jumlah harus > 0")
        return

    if jumlah <= saldo - 50000:
        # verifikasi PIN sebelum tarik (pilihan B sebelumnya meminta verifikasi untuk transfer;
        # untuk keamanan, kita minta PIN juga untuk tarik)
        if not verifikasi_aksi_pin(norek):
            return
        data_pengguna[norek]["saldo"] -= jumlah
        data_pengguna[norek]["saldo_riwayat"].append(f"-{jumlah} ({waktu_sekarang()})")
        print(f"Berhasil tarik {format_rp(jumlah)}")
        cetak_struk(norek, data_pengguna[norek]["nama"], "Tarik Tunai", jumlah, data_pengguna[norek]["saldo"])
    else:
        print("Jumlah tarik melebihi batas minimal saldo Rp50.000")

def transfer(norek):
    """Transfer dari norek (pengirim) ke norek tujuan."""
    if data_pengguna[norek].get("blocked", False):
        print("Rekening Anda diblokir. Tidak dapat transfer.")
        return

    tujuan = input("Masukkan nomor rekening tujuan: ")
    if tujuan not in data_pengguna:
        print("Rekening tujuan tidak ditemukan.")
        return
    if data_pengguna[tujuan].get("blocked", False):
        print("Rekening tujuan sedang diblokir. Transfer dibatalkan.")
        return

    try:
        jumlah = int(input("Masukkan jumlah transfer: "))
    except:
        print("Jumlah tidak valid!")
        return

    if jumlah <= 0:
        print("Jumlah harus > 0")
        return

    # pastikan menyisakan minimal 50k
    if jumlah > data_pengguna[norek]["saldo"] - 50000:
        print("Saldo tidak cukup! Wajib menyisakan Rp50.000 di rekening.")
        return

    # Verifikasi PIN sebelum transfer (sesuai pilihan B)
    if not verifikasi_aksi_pin(norek):
        return

    # Proses transfer
    data_pengguna[norek]["saldo"] -= jumlah
    data_pengguna[tujuan]["saldo"] += jumlah

    data_pengguna[norek]["saldo_riwayat"].append(f"-{jumlah} TRANSFER ke {tujuan} ({waktu_sekarang()})")
    data_pengguna[tujuan]["saldo_riwayat"].append(f"+{jumlah} TRANSFER dari {norek} ({waktu_sekarang()})")

    print(f"Transfer {format_rp(jumlah)} ke {tujuan} berhasil.")
    # cetak struk untuk pengirim dan penerima (pengirim lihat struk)
    cetak_struk(norek, data_pengguna[norek]["nama"], f"Transfer ke {tujuan}", jumlah, data_pengguna[norek]["saldo"])
    # untuk penerima, juga cetak ringkasan kecil
    cetak_struk(tujuan, data_pengguna[tujuan]["nama"], f"Transfer dari {norek}", jumlah, data_pengguna[tujuan]["saldo"])


#------------- MENU INVESTASI -------------
def investasi(norek):
    if data_pengguna[norek].get("blocked", False):
        print("Rekening diblokir.")
        return

    while True:
        print("\n=== MENU INVESTASI ===")
        print("1. Emas (per gram)")
        print("2. Tanah (per meter persegi)")
        print("3. Deposito (uang)")
        print("4. Cek Total Investasi")
        print("5. Hitung Bunga 2%")
        print("6. Riwayat Investasi")
        print("7. Kembali")

        pilih = input("Pilih menu: ")

        if pilih == "1":
            try:
                gram = int(input(f"Masukkan jumlah gram emas (Harga saat ini {format_rp(harga_emas_sekarang)}/gr): "))
            except:
                print("Jumlah invalid!")
                continue

            harga_per_gram = harga_emas_sekarang
            total = gram * harga_per_gram

            # pastikan saldo setelah pembelian tetap >= 50k
            if total > data_pengguna[norek]["saldo"] - 50000:
                print("Saldo tidak cukup! Wajib menyisakan Rp50.000 setelah beli investasi.")
                continue

            if gram <= 0:
                print("Jumlah gram harus > 0")
                continue

            data_pengguna[norek]["saldo"] -= total
            data_pengguna[norek]["investasi"]["emas"] += gram
            data_pengguna[norek]["investasi_riwayat"].append(f"Beli emas {gram}gr (Rp{total}) at {waktu_sekarang()}")
            data_pengguna[norek]["saldo_riwayat"].append(f"-{total} (INVESTASI EMAS) ({waktu_sekarang()})")
            print(f"Emas berhasil dibeli: {gram} gr seharga {format_rp(total)}")
            cetak_struk(norek, data_pengguna[norek]["nama"], f"Investasi Emas ({gram} gr)", total, data_pengguna[norek]["saldo"])

        elif pilih == "2":
            try:
                meter = int(input(f"Masukkan jumlah meter tanah (Harga saat ini {format_rp(harga_tanah_sekarang)}/m²): "))
            except:
                print("Jumlah invalid!")
                continue

            harga_per_meter = harga_tanah_sekarang
            total = meter * harga_per_meter

            if total > data_pengguna[norek]["saldo"] - 50000:
                print("Saldo tidak cukup! Wajib menyisakan Rp50.000 setelah beli investasi.")
                continue

            if meter <= 0:
                print("Jumlah meter harus > 0")
                continue

            data_pengguna[norek]["saldo"] -= total
            data_pengguna[norek]["investasi"]["tanah"] += meter
            data_pengguna[norek]["investasi_riwayat"].append(f"Beli tanah {meter}m² (Rp{total}) at {waktu_sekarang()}")
            data_pengguna[norek]["saldo_riwayat"].append(f"-{total} (INVESTASI TANAH) ({waktu_sekarang()})")
            print(f"Tanah berhasil dibeli: {meter} m² seharga {format_rp(total)}")
            cetak_struk(norek, data_pengguna[norek]["nama"], f"Investasi Tanah ({meter} m²)", total, data_pengguna[norek]["saldo"])

        elif pilih == "3":
            try:
                uang = int(input("Masukkan nominal deposito: "))
            except:
                print("Jumlah invalid!")
                continue

            if uang > data_pengguna[norek]["saldo"] - 50000:
                print("Saldo tidak cukup! Wajib menyisakan Rp50.000 setelah deposito.")
                continue

            if uang <= 0:
                print("Jumlah harus > 0")
                continue

            data_pengguna[norek]["saldo"] -= uang
            data_pengguna[norek]["investasi"]["deposito"] += uang
            data_pengguna[norek]["investasi_riwayat"].append(f"Deposito Rp{uang} at {waktu_sekarang()}")
            data_pengguna[norek]["saldo_riwayat"].append(f"-{uang} (DEPOSITO) ({waktu_sekarang()})")
            print(f"Deposito berhasil: {format_rp(uang)}")
            cetak_struk(norek, data_pengguna[norek]["nama"], f"Deposito Rp{uang}", uang, data_pengguna[norek]["saldo"])

        elif pilih == "4":
            total_nilai = (
                data_pengguna[norek]["investasi"]["emas"] * harga_emas_sekarang +
                data_pengguna[norek]["investasi"]["tanah"] * harga_tanah_sekarang +
                data_pengguna[norek]["investasi"]["deposito"]
            )
            print("\n=== NILAI INVESTASI ===")
            print(f"Emas: {data_pengguna[norek]['investasi']['emas']} gr  (nilai {format_rp(data_pengguna[norek]['investasi']['emas'] * harga_emas_sekarang)})")
            print(f"Tanah: {data_pengguna[norek]['investasi']['tanah']} m²  (nilai {format_rp(data_pengguna[norek]['investasi']['tanah'] * harga_tanah_sekarang)})")
            print(f"Deposito: {format_rp(data_pengguna[norek]['investasi']['deposito'])}")
            print(f"TOTAL = {format_rp(total_nilai)}")

        elif pilih == "5":
            total_nilai = (
                data_pengguna[norek]["investasi"]["emas"] * harga_emas_sekarang +
                data_pengguna[norek]["investasi"]["tanah"] * harga_tanah_sekarang +
                data_pengguna[norek]["investasi"]["deposito"]
            )
            bunga = total_nilai * 0.02
            data_pengguna[norek]["saldo"] += bunga
            data_pengguna[norek]["saldo_riwayat"].append(f"+{bunga:.2f} (BUNGA INVESTASI) ({waktu_sekarang()})")
            print(f"Bunga sebesar {format_rp(bunga):} ditambahkan ke saldo")
            cetak_struk(norek, data_pengguna[norek]["nama"], "Bunga Investasi 2%", bunga, data_pengguna[norek]["saldo"])

        elif pilih == "6":
            lihat_transaksi_investasi(norek)

        elif pilih == "7":
            break

        else:
            print("Pilihan tidak valid!")

# ========== UTIL ==========
def format_rp(n):
    """Format angka ke format Rp1.234.567 (Indonesia)."""
    try:
        n = float(n)
    except:
        return str(n)
    s = f"{n:,.0f}"  # 1,234,567
    return "Rp" + s.replace(",", ".")

def waktu_sekarang():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def cetak_struk(norek, nama, jenis, jumlah, saldo_setelah):
    """Cetak struk transaksi sederhana."""
    print("\n====== STRUK TRANSAKSI ======")
    print(f"Tanggal  : {waktu_sekarang()}")
    print(f"Nama     : {nama}")
    print(f"Rekening : {norek}")
    print(f"Jenis    : {jenis}")
    print(f"Jumlah   : {format_rp(jumlah)}")
    print(f"Saldo    : {format_rp(saldo_setelah)}")
    print("=============================\n")

def hasilkan_harga():
    """Hasilkan harga emas dan tanah acak di rentang wajar setiap login."""
    global harga_emas_sekarang, harga_tanah_sekarang
    harga_emas_sekarang = random.randint(900_000, 1_200_000)   # per gram
    harga_tanah_sekarang = random.randint(400_000, 700_000)    # per m2

def masker_rek(norek):
    """Mask nomor rekening untuk dashboard: tampilkan 4 awal + **** + 4 akhir."""
    return norek[:4] + "****" + norek[-4:]

# ========== INPUT VALIDASI ==========
def input_norek():
    while True:
        norek = input("Masukkan No Rekening (12 digit): ")
        if norek.isdigit() and len(norek) == 12:
            return norek
        print("Norek harus angka & terdiri dari 12 digit!")

def input_pin():
    while True:
        pin = input("Masukkan PIN (6 karakter, boleh huruf/angka): ")
        if len(pin) == 6:
            return pin
        print("PIN harus 6 karakter!")


# ========== LIHAT / RIWAYAT ==========
def cek_saldo(norek):
    print(f"\nSaldo anda: {format_rp(data_pengguna[norek]['saldo'])}")

def lihat_transaksi_saldo(norek):
    print("\n=== Riwayat Transaksi Saldo ===")
    if not data_pengguna[norek]["saldo_riwayat"]:
        print("Belum ada transaksi.")
        return
    for trx in data_pengguna[norek]["saldo_riwayat"]:
        print(trx)

def lihat_transaksi_investasi(norek):
    print("\n=== Riwayat Investasi ===")
    if not data_pengguna[norek]["investasi_riwayat"]:
        print("Belum ada transaksi investasi.")
        return
    for trx in data_pengguna[norek]["investasi_riwayat"]:
        print(trx)

# ========== DASHBOARD ==========
def dashboard_nasabah(norek):
    """Tampilkan dashboard lengkap (pilihan B)."""
    nama = data_pengguna[norek]["nama"]
    saldo = data_pengguna[norek]["saldo"]
    emas = data_pengguna[norek]["investasi"]["emas"]
    tanah = data_pengguna[norek]["investasi"]["tanah"]
    deposito = data_pengguna[norek]["investasi"]["deposito"]
    total_investasi = emas * harga_emas_sekarang + tanah * harga_tanah_sekarang + deposito

    print("\n===== DASHBOARD =====")
    print(f"Nama            : {nama}")
    print(f"Rekening        : {masker_rek(norek)}")
    print(f"Saldo           : {format_rp(saldo)}")
    print(f"Emas            : {emas} gr")
    print(f"Tanah           : {tanah} m²")
    print(f"Deposito        : {format_rp(deposito)}")
    print(f"Total Investasi : {format_rp(total_investasi)}")
    print(f"Harga Emas Hari Ini : {format_rp(harga_emas_sekarang)}/gr")
    print(f"Harga Tanah Hari Ini: {format_rp(harga_tanah_sekarang)}/m²")
    print("======================\n")

# ========== LOGIN NASABAH (dengan generate harga & blokir 3x salah PIN) ==========
def login_nasabah():
    print("\n=== Login nasabah ===")
    norek = input("Masukkan No Rekening: ")
    pin = input("Masukkan PIN: ")

    if norek not in data_pengguna:
        print("Norek tidak ditemukan!")
        return

    if data_pengguna[norek].get("blocked", False):
        print("Rekening anda diblokir. Hubungi admin.")
        return

    if pin == data_pengguna[norek]["pin"]:
        # reset failed count
        jumlah_pin_gagal[norek] = 0

        # generate harga dinamis setiap kali nasabah berhasil login
        hasilkan_harga()

        # tampilkan dashboard lengkap
        dashboard_nasabah(norek)

        # lanjut ke menu nasabah
        menu_nasabah(norek)
    else:
        jumlah_pin_gagal[norek] = jumlah_pin_gagal.get(norek, 0) + 1
        sisa = 3 - jumlah_pin_gagal[norek]
        print(f"PIN salah! Sisa kesempatan: {max(sisa,0)}")
        if jumlah_pin_gagal[norek] >= 3:
            data_pengguna[norek]["blocked"] = True
            data_pengguna[norek]["saldo_riwayat"].append(f"!DIBLOKIR otomatis karena 3x salah PIN ({waktu_sekarang()})")
            print("Akun diblokir permanen. Hubungi admin untuk membuka blokir.")

# ========== VERIVUKASI PIN ==========
def verifikasi_aksi_pin(norek):
    """Minta PIN untuk konfirmasi tindakan sensitif. Jika salah 3x -> blokir permanen."""
    if data_pengguna[norek].get("blocked", False):
        print("Rekening diblokir.")
        return False

    pin = input("Masukkan PIN untuk konfirmasi: ")
    if pin == data_pengguna[norek]["pin"]:
        # reset counter jika sukses
        jumlah_pin_gagal[norek] = 0
        return True
    else:
        # salah PIN -> increment
        jumlah_pin_gagal[norek] = jumlah_pin_gagal.get(norek, 0) + 1
        sisa = 3 - jumlah_pin_gagal[norek]
        print(f"PIN salah! Sisa kesempatan: {max(sisa,0)}")
        if jumlah_pin_gagal[norek] >= 3:
            data_pengguna[norek]["blocked"] = True
            data_pengguna[norek]["saldo_riwayat"].append(f"!DIBLOKIR otomatis karena 3x salah PIN ({waktu_sekarang()})")
            print("Akun diblokir permanen. Hubungi admin untuk membuka blokir.")
        return False

# ========== MENU NASABAH ==========
def menu_nasabah(norek):
    while True:
        print("\n=== MENU PELANGGAN ===")
        print("1. Setor Uang")
        print("2. Transfer Antar Rekening")
        print("3. Tarik Uang")
        print("4. Cek Saldo")
        print("5. Riwayat Saldo")
        print("6. Investasi")
        print("7. Kembali")

        p = input("Pilih menu: ")

        if p == "1": setor_uang(norek)
        elif p == "2": transfer(norek)
        elif p == "3": tarik_uang(norek)
        elif p == "4": cek_saldo(norek)
        elif p == "5": lihat_transaksi_saldo(norek)
        elif p == "6": investasi(norek)
        elif p == "7": break
        else:
            print("Pilihan tidak valid!")

# ========== MENU ADMIN ==========
def menu_admin():
    while True:
        print("\n==== MENU ADMIN ====")
        print("1. Tambah Nasabah")
        print("2. Update Nasabah")
        print("3. Lihat Semua Nasabah")
        print("4. Buka Blokir  Nasabah")
        print("5. Hapus Nasabah")
        print("6. Kembali")

        pilihan = input("Pilih menu: ")

        if pilihan == "1": tambah_nasabah()
        elif pilihan == "2": update_nasabah()
        elif pilihan == "3": lihat_data()
        elif pilihan == "4": buka_blokir_nasabah()
        elif pilihan == "5": hapus_nasabah()
        elif pilihan == "6": break
        else:
            print("Pilihan tidak valid!")

def login_admin():
    print("\n=== Login Admin ===")
    user = input("Username admin: ")
    pw = input("Password admin: ")

    if user in akun_admin and akun_admin[user] == pw:
        print("Login admin berhasil!")
        menu_admin()
    else:
        print("Username / Password admin salah!")

# ========== PROGRAM UTAMA ==========
def menu_utama():
    print("=== SISTEM ADMINISTRASI BANK MINI ===")

if __name__ == "__main__":
    while True:
        print("\n=== LOGIN SEBAGAI ===")
        print("1. Login Admin")
        print("2. Login Nasabah")
        print("3. Keluar")

        role = input("Pilih: ")

        if role == "1":
            login_admin()
        elif role == "2":
            login_nasabah()
        elif role == "3":
            print("Program selesai.")
            break
        else:
            print("Input salah!")
