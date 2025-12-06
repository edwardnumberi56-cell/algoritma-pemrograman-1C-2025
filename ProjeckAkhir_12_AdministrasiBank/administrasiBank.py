import random #menginpor modul random dan datetime untuk dipakai  dlm program
from datetime import datetime

# ========== DATA ==========
data_pengguna = {}
akun_admin = {"admin": "123"}
norek_terakhir_ditambah = None #menyimpan nomor rekening yang terakhir dibuat. Awalnya None.
jumlah_pin_gagal = {}  # dictionary untuk mencatat berapa kali PIN nasabah salah.

# Harga dinamis (akan dihasilkan saat pelanggan login)
harga_emas_sekarang = 1_000_000 
harga_tanah_sekarang = 500_000

#--------- MENU ADMIN---------
def tambah_nasabah():
    global norek_terakhir_ditambah #agar fungsi dapat mengubah nilai variabel global tersebut.
    print("\n=== Tambah Nasabah ===")

    # Otomatis blokir rekening sebelumnya bila saldo 0
    if norek_terakhir_ditambah:
        prev = norek_terakhir_ditambah #Menyimpan nomor rekening terakhir yang ditambahkan ke variabel prev
        if prev in data_pengguna: #Mengecek apakah nomor rekening prev benar-benar ada di database data_pengguna.
            if data_pengguna[prev]["saldo"] == 0 and not data_pengguna[prev].get("blocked", False): #Mengecek apakah saldo rekening sebelumnya adalah nol. dab ambil nilai key blocked bila ada, jika tdk anggap false
                data_pengguna[prev]["blocked"] = True #Menandai bahwa rekening tersebut sekarang diblokir jdi tidak bbisa dipakai lagi
                data_pengguna[prev]["saldo_riwayat"].append(f"!DIBLOKIR otomatis saat admin menambah nasabah baru ({waktu_sekarang()})") #Menambahkan catatan ke daftar riwayat saldo. Fungsinya untuk dokumentasi agar ada jejak bahwa rekening diblokir otomatis.
                print(f"Rekening sebelumnya ({prev}) otomatis diblokir (saldo = 0).") #Menampilkan pesan di layar bahwa rekening yang sebelumnya dibuat telah diblokir. karena saldonya 0

    nama = input("Masukkan Nama: ")
    norek = input_norek()
    if norek in data_pengguna: #Jika nomor rekening sudah dipakai, maka tampilkan pesan dan keluar dari fungsi.
        print("Nomor rekening sudah terdaftar!")
        return
    pin = input_pin() #Memanggil fungsi input_pin() untuk meminta PIN.

    while True: #Loop untuk memastikan input benar
        try:
            saldo_awal = int(input("Masukkan saldo awal (minimal 100000): ")) #Coba mengambil input saldo dan mengubahnya menjadi integer.
        except:
            print("Input tidak valid!")
            continue #Jika input bukan angka, tampilkan pesan dan ulangi

        if saldo_awal >= 100000: #Jika saldo awal minimal Rp 100.000 → lanjut keluar loop.
            break
        print("Saldo awal minimal Rp 100.000!") #Menampilkan pesan kalau saldo kurang.

    data_pengguna[norek] = { #Membuat dictionary baru untuk nasabah baru.
        "nama": nama,
        "pin": pin,
        "saldo": saldo_awal,
        "saldo_riwayat": [f"+{saldo_awal} (Saldo Awal)"], #Membuat riwayat saldo pertama kali: saldo awal
        "investasi": {"emas":0, "tanah":0, "deposito":0}, #Menyediakan ruang untuk investasi nasabah:
        "investasi_riwayat": [], #Menyimpan riwayat transaksi investasi.
        "blocked": False #Menandakan bahwa rekening aktif (tidak diblokir).
    }
    jumlah_pin_gagal[norek] = 0 #Mengatur jumlah kesalahan PIN nasabah baru menjadi 0

    norek_terakhir_ditambah = norek #Mengupdate variabel global bahwa rekening terakhir yang dibuat adalah norek.
    print("Nasabah berhasil ditambahkan!")

def update_nasabah():
    print("\n=== Update Nasabah ===")
    norek = input("Masukkan norek yang ingin diupdate: ") #Meminta admin memasukkan nomor rekening nasabah yang ingin diubah datanya.

    if norek not in data_pengguna: #Mengecek apakah nomor rekening (norek) ada dalam database data_pengguna.
        print("Data tidak ditemukan!")
        return #Menghentikan fungsi karena rekening tidak ditemukan, sehingga tidak ada yang bisa diubah.

    print("\nApa yang ingin diubah?")
    print("1. Ubah Nama")
    print("2. Ubah PIN")
    print("3. Ubah Nomor Rekening")
    pilihan = input("Pilih menu: ")

    # ---- 1. Ubah Nama ----
    if pilihan == "1":
        nama_baru = input("Masukkan nama baru: ")
        data_pengguna[norek]["nama"] = nama_baru #Mengubah nilai nama pada dictionary data nasabah.
        print("Nama berhasil diupdate!")

    # ---- 2. Ubah PIN ----
    elif pilihan == "2":
        pin_baru = input_pin()
        data_pengguna[norek]["pin"] = pin_baru #Mengupdate PIN nasabah di database.
        print("PIN berhasil diupdate!")

    # ---- 3. Ubah Nomor Rekening ----
    elif pilihan == "3":
        norek_baru = input_norek() #Mengambil input nomor rekening baru melalui fungsi input_norek().

        if norek_baru in data_pengguna: #Mengecek apakah nomor rekening baru sudah dipakai nasabah lain.
            print("Norek baru sudah digunakan!")
            return #Hentikan proses update karena nomor rekening baru tidak valid.

        # Pindahkan data lama ke data baru
        data_pengguna[norek_baru] = data_pengguna[norek] #Memindahkan seluruh data nasabah lama ke entry baru dengan norek_baru
        del data_pengguna[norek] #Menghapus data lama berdasarkan nomor rekening lama. sekarang hanya norek bru yg tersisa

        # Pindahkan juga jumlah_pin_gagal
        jumlah_pin_gagal[norek_baru] = jumlah_pin_gagal.get(norek, 0) #Memindahkan jumlah kesalahan PIN dari rekening lama ke rekening baru. .get(norek, 0) → jika norek lama tidak ada dalam dictionary, anggap jumlah kesalahan 0.
        if norek in jumlah_pin_gagal: #Mengecek apakah nomor rekening lama ada di dictionary jumlah_pin_gagal
            del jumlah_pin_gagal[norek] #Jika ada → hapus entry jumlah PIN gagal lama (karena sudah dipindah ke norek baru).

        print(f"Norek berhasil diubah dari {norek} ke {norek_baru}")

    else:
        print("Pilihan tidak valid!") #Jika admin memasukkan angka selain 1, 2, atau 3 → tampil pesan salah


def lihat_data():
    print("\n=== Data Semua Nasabah ===")
    if not data_pengguna: #Mengecek apakah data_pengguna kosong.
        print("Belum ada data nasabah.")
        return #Mengakhiri fungsi karena tidak ada data untuk ditampilkan
    for norek, info in data_pengguna.items(): #Melakukan loop untuk setiap entry di dictionary data_pengguna.
        status = "BLOKIR" if info.get("blocked", False) else "AKTIF" # Mengambil status blokir nasabah.
        print(f"Norek: {norek} | Nama: {info['nama']} | Saldo: {format_rp(info['saldo'])} | Status: {status}") #Menampilkan semua informasi nasabah:

#------ HAPUS NASABAH ---------
def hapus_nasabah():
    print("\n=== Hapus Nasabah ===")
    norek = input("Masukkan nomor rekening yang ingin dihapus: ") #Meminta admin memasukkan nomor rekening yang ingin dihapus.

    if norek not in data_pengguna: #Mengecek apakah nomor rekening ada dalam database.
        print("Data tidak ditemukan!")
        return #Berhenti karena tidak ada data yang bisa dihapus.

    # Jika nasabah masih punya saldo, minta konfirmasi
    saldo = data_pengguna[norek]["saldo"] #Mengambil saldo nasabah dari database.
    if saldo > 0: #Mengecek apakah saldo nasabah masih ada (lebih dari 0).
        print(f"Nasabah masih memiliki saldo {format_rp(saldo)}")
        yakin = input("Apakah tetap ingin menghapus? (y/n): ").lower() #Meminta konfirmasi apakah ingin tetap menghapus
        if yakin != "y": #Jika admin menjawab selain "y" (yes) → batal menghapus.
            print("Penghapusan dibatalkan.")
            return #Menghentikan fungsi karena batal menghapus.

    # Hapus data
    del data_pengguna[norek] #Menghapus data nasabah dari dictionary data_pengguna.

    # Hapus riwayat jumlah PIN gagal jika ada
    if norek in jumlah_pin_gagal: #Mengecek apakah nasabah tersebut memiliki data jumlah kesalahan PIN.
        del jumlah_pin_gagal[norek] #Jika ada → hapus entry tersebut

    # Jika yang dihapus adalah rekening terakhir ditambah, reset variabel
    global norek_terakhir_ditambah #Memberi tahu Python bahwa kita akan mengubah variabel global norek_terakhir_ditambah.
    if norek_terakhir_ditambah == norek: #Mengecek apakah nomor rekening yang dihapus adalah rekening terakhir yang ditambahkan oleh admin.
        norek_terakhir_ditambah = None #Jika iya → set ulang ke None.

    print(f"Nasabah dengan rekening {norek} berhasil dihapus!") #Menampilkan pesan bahwa nasabah berhasil dihapus dari sistem.

#------- BUKA BLOKIR NASABAH ---------
def buka_blokir_nasabah():
    print("\n=== Buka Blokir Nasabah ===")
    norek = input("Masukkan nomor rekening: ")

    if norek not in data_pengguna: #Mengecek apakah nomor rekening ada dalam database
        print("Nomor rekening tidak ditemukan!")
        return #Menghentikan fungsi karena rekening tidak valid

    if not data_pengguna[norek].get("blocked", False): #Mengecek status blokir nasabah. ambil nilai blocked jika tidak anggap false
        print("Rekening ini tidak dalam keadaan terblokir.")
        return #Menghentikan fungsi karena rekening tidak diblokir.

    # Memastikan admin yakin membuka blokir
    yakin = input("Rekening terblokir. Buka blokir? (y/n): ").lower() #Meminta konfirmasi admin apakah ingin membuka blokir.
    if yakin != "y": #Jika admin menjawab selain "y" → batalkan membuka blokir.
        print("Pembukaan blokir dibatalkan.")
        return #Menghentikan eksekusi fungsi.

    data_pengguna[norek]["blocked"] = False #Mengubah status rekening menjadi tidak diblokir.
    data_pengguna[norek]["saldo_riwayat"].append("!BLOKIR DIBUKA oleh admin") #Mencatat riwayat bahwa blokir telah dibuka.
    print(f"Rekening {norek} berhasil dibuka kembali!") #Menampilkan pesan sukses.


#--------- MENU NASABAH------------
def setor_uang(norek):
    if data_pengguna[norek].get("blocked", False): #Mengecek apakah rekening diblokir. Jika "blocked" = True, fungsi tidak boleh lanjut.
        print("Rekening diblokir.")
        return #Menghentikan fungsi setor.
    try: #untuk menagani error agar program tidak berhenti saat terjadi kesalahan input.
        jumlah = int(input("Masukkan jumlah setor: "))
    except: #digunakan untuk menangkap error yang terjadi di dalam blok try
        print("Jumlah tidak valid!") #Jika input tidak bisa dikonversi ke angka → tampilkan pesan dan hentikan fungsi.
        return
    data_pengguna[norek]["saldo"] += jumlah #Menambahkan jumlah setor ke saldo nasabah.
    data_pengguna[norek]["saldo_riwayat"].append(f"+{jumlah} ({waktu_sekarang()})") #Menambahkan catatan riwayat transaksi setor dengan timestamp.
    print(f"Berhasil setor {format_rp(jumlah)}") #Menampilkan pesan bahwa setor berhasil.
    cetak_struk(norek, data_pengguna[norek]["nama"], "Setor Tunai", jumlah, data_pengguna[norek]["saldo"]) #Memanggil fungsi cetak_struk() untuk mencetak struk transaksi.

def tarik_uang(norek):
    if data_pengguna[norek].get("blocked", False): #Mengecek apakah rekening diblokir.
        print("Rekening diblokir.")
        return #Jika diblokir, tampilkan pesan dan hentikan fungsi.

    saldo = data_pengguna[norek]["saldo"] #Mengambil saldo nasabah.

    if saldo <= 50000:
        print("Tidak bisa tarik! saldo harus minimal Rp50.000 tersisa") #Tidak boleh tarik jika saldo terlalu kecil. Beri pesan dan hentikan.
        return

    try:
        jumlah = int(input("Masukkan jumlah tarik: ")) #Meminta jumlah uang yang ingin ditarik. Mencoba mengubah menjadi integer.
    except:
        print("Jumlah tidak valid!") #Jika gagal konversi (misal huruf) → hentikan fungsi
        return

    if jumlah <= 0:
        print("Jumlah harus > 0")
        return

    if jumlah <= saldo - 50000:
        # verifikasi PIN sebelum tarik (pilihan B sebelumnya meminta verifikasi untuk transfer;
        # untuk keamanan, kita minta PIN juga untuk tarik)
        if not verifikasi_aksi_pin(norek):
            return #Jika PIN salah → transaksi dibatalkan
        data_pengguna[norek]["saldo"] -= jumlah #Mengurangi saldo nasabah
        data_pengguna[norek]["saldo_riwayat"].append(f"-{jumlah} ({waktu_sekarang()})") #Mencatat transaksi tarik uang berikut waktu transaksi.
        print(f"Berhasil tarik {format_rp(jumlah)}") #Menampilkan pesan bahwa penarikan berhasil.
        cetak_struk(norek, data_pengguna[norek]["nama"], "Tarik Tunai", jumlah, data_pengguna[norek]["saldo"]) #Mencetak struk transaksi penarikan.
    else:
        print("Jumlah tarik melebihi batas minimal saldo Rp50.000") #Jika jumlah tarik terlalu besar sehingga sisa saldo < Rp50.000, tampilkan pesan error.

def transfer(norek):
    """Transfer dari norek (pengirim) ke norek tujuan."""
    if data_pengguna[norek].get("blocked", False): #Mengecek apakah rekening pengirim sedang diblokir.Ambil nilai "blocked", Jika tidak ada, default = False
        print("Rekening Anda diblokir. Tidak dapat transfer.") #Menampilkan pesan bahwa pengirim tidak boleh transfer.
        return

    tujuan = input("Masukkan nomor rekening tujuan: ") #Meminta input nomor rekening tujuan transfer.
    if tujuan not in data_pengguna: #Cek apakah rekening tujuan ada dalam database.
        print("Rekening tujuan tidak ditemukan.")
        return
    if data_pengguna[tujuan].get("blocked", False):
        print("Rekening tujuan sedang diblokir. Transfer dibatalkan.")
        return #Hentikan fungsi karena rekening tujuan tidak valid.

    try:
        jumlah = int(input("Masukkan jumlah transfer: "))
    except:
        print("Jumlah tidak valid!") #Jika user memasukkan huruf / karakter → except: menangkap error.
        return

    if jumlah <= 0:
        print("Jumlah harus > 0") #Tidak boleh transfer angka nol.
        return

    # pastikan menyisakan minimal 50k
    if jumlah > data_pengguna[norek]["saldo"] - 50000: #Mengecek apakah saldo setelah transfer masih tersisa minimal Rp 50.000.
        print("Saldo tidak cukup! Wajib menyisakan Rp50.000 di rekening.")
        return

    # Verifikasi PIN sebelum transfer (sesuai pilihan B)
    if not verifikasi_aksi_pin(norek):
        return #Jika PIN salah, batalkan transaksi.

    # Proses transfer 
    data_pengguna[norek]["saldo"] -= jumlah #Mengurangi saldo pengirim.
    data_pengguna[tujuan]["saldo"] += jumlah #Menambah saldo penerima.

    data_pengguna[norek]["saldo_riwayat"].append(f"-{jumlah} TRANSFER ke {tujuan} ({waktu_sekarang()})") #Mencatat riwayat transaksi pengirim. dan penerima
    data_pengguna[tujuan]["saldo_riwayat"].append(f"+{jumlah} TRANSFER dari {norek} ({waktu_sekarang()})")

    print(f"Transfer {format_rp(jumlah)} ke {tujuan} berhasil.")
    # cetak struk untuk pengirim dan penerima (pengirim lihat struk)
    cetak_struk(norek, data_pengguna[norek]["nama"], f"Transfer ke {tujuan}", jumlah, data_pengguna[norek]["saldo"])
    # untuk penerima, juga cetak ringkasan kecil
    cetak_struk(tujuan, data_pengguna[tujuan]["nama"], f"Transfer dari {norek}", jumlah, data_pengguna[tujuan]["saldo"])


#------------- MENU INVESTASI -------------
def investasi(norek):
    if data_pengguna[norek].get("blocked", False): #Mengecek apakah rekening diblokir..get("blocked", False) = ambil nilai blocked. Jika tidak ada, anggap False.
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
                gram = int(input(f"Masukkan jumlah gram emas (Harga saat ini {format_rp(harga_emas_sekarang)}/gr): ")) #Meminta user menginput jumlah gram emas. int() mengubah input menjadi angka.
            except:
                print("Jumlah invalid!")
                continue #Jika input tidak valid → kembali ke menu (continue)

            harga_per_gram = harga_emas_sekarang #Menyimpan harga emas saat ini.
            total = gram * harga_per_gram #Menghitung total biaya pembelian emas

            # pastikan saldo setelah pembelian tetap >= 50k
            if total > data_pengguna[norek]["saldo"] - 50000:
                print("Saldo tidak cukup! Wajib menyisakan Rp50.000 setelah beli investasi.")
                continue #Cek apakah saldo cukup setelah menyisakan minimal Rp50.000.

            if gram <= 0:
                print("Jumlah gram harus > 0") #Validasi input: gram harus lebih dari 0.
                continue

            data_pengguna[norek]["saldo"] -= total #Mengurangi saldo karena pembelian emas.
            data_pengguna[norek]["investasi"]["emas"] += gram # Menambah jumlah emas pada data investasi nasabah.
            data_pengguna[norek]["investasi_riwayat"].append(f"Beli emas {gram}gr (Rp{total}) at {waktu_sekarang()}") # Mencatat riwayat pembelian emas.
            data_pengguna[norek]["saldo_riwayat"].append(f"-{total} (INVESTASI EMAS) ({waktu_sekarang()})") #Mencatat transaksi pada riwayat saldo.
            print(f"Emas berhasil dibeli: {gram} gr seharga {format_rp(total)}") #Pesan sukses.
            cetak_struk(norek, data_pengguna[norek]["nama"], f"Investasi Emas ({gram} gr)", total, data_pengguna[norek]["saldo"]) #cetak struktur transaksi pembelian emas.

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
                uang = int(input("Masukkan nominal deposito: ")) #Input deposito (mirip emas/tanah)
            except:
                print("Jumlah invalid!")
                continue

            if uang > data_pengguna[norek]["saldo"] - 50000: #Validasi saldo + syarat minimal
                print("Saldo tidak cukup! Wajib menyisakan Rp50.000 setelah deposito.")
                continue

            if uang <= 0:
                print("Jumlah harus > 0")
                continue

            data_pengguna[norek]["saldo"] -= uang
            data_pengguna[norek]["investasi"]["deposito"] += uang #Menambah deposito
            data_pengguna[norek]["investasi_riwayat"].append(f"Deposito Rp{uang} at {waktu_sekarang()}") #Menambah riwayat
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
            print(f"Deposito: {format_rp(data_pengguna[norek]['investasi']['deposito'])}") #Hitung nilai dari 3 jenis investasi
            print(f"TOTAL = {format_rp(total_nilai)}") #Menghitung TOTAL nilai semua investasi.

        elif pilih == "5":
            total_nilai = (
                data_pengguna[norek]["investasi"]["emas"] * harga_emas_sekarang +
                data_pengguna[norek]["investasi"]["tanah"] * harga_tanah_sekarang +
                data_pengguna[norek]["investasi"]["deposito"]
            )
            bunga = total_nilai * 0.02
            data_pengguna[norek]["saldo"] += bunga # tambahkanbunga ke saldo
            data_pengguna[norek]["saldo_riwayat"].append(f"+{bunga:.2f} (BUNGA INVESTASI) ({waktu_sekarang()})") #Catat riwayat saldo
            print(f"Bunga sebesar {format_rp(bunga):} ditambahkan ke saldo")
            cetak_struk(norek, data_pengguna[norek]["nama"], "Bunga Investasi 2%", bunga, data_pengguna[norek]["saldo"]) #Cetak struk bunga

        elif pilih == "6":
            lihat_transaksi_investasi(norek) #Memanggil fungsi untuk menampilkan riwayat investasi.

        elif pilih == "7": 
            break #Keluar dari menu while True.

        else:
            print("Pilihan tidak valid!") #Ditampilkan jika user memasukkan selain angka 1–7.

# ========== UTIL ==========
def format_rp(n): #Mendefinisikan fungsi format_rp, menerima parameter n (angka)
    """Format angka ke format Rp1.234.567 (Indonesia)."""
    try: #Program mencoba (try) mengubah n menjadi float
        n = float(n)
    except: #Jika gagal (misalnya user menginput "abc") → masuk except
        return str(n) #Pada error → kembalikan string apa adanya (return str(n)).
    s = f"{n:,.0f}"  # 1,234,567 hasilnya disimpan kevariabel s
    return "Rp" + s.replace(",", ".") #Mengganti koma menjadi titik → 1.234.567

def waktu_sekarang():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # datetime.now() → mengambil waktu sekarang. .strftime(...) → mengubah format menjadi: 2025-01-28 14:33:50
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

def masker_rek(norek): #Mendefinisikan fungsi untuk memasking nomor rekening.
    """Mask nomor rekening untuk dashboard: tampilkan 4 awal + **** + 4 akhir."""
    return norek[:4] + "****" + norek[-4:] #Menghasilkan tampilan aman misal: "1234****5678"

# ========== INPUT VALIDASI ==========
def input_norek():
    while True:
        norek = input("Masukkan No Rekening (12 digit): ") #Minta user memasukkan nomor rekening.
        if norek.isdigit() and len(norek) == 12: #isdigit() → semua karakter angka panjang 12 digit
            return norek #Jika benar → kembalikan nomor rekenin
        print("Norek harus angka & terdiri dari 12 digit!") #Jika salah → tampilkan pesan error.

def input_pin():
    while True:
        pin = input("Masukkan PIN (6 karakter, boleh huruf/angka): ")
        if len(pin) == 6: #PIN harus tepat 6 karakter.
            return pin #Jika valid → kembalikan PIN.
        print("PIN harus 6 karakter!") #Jika salah → beritahu user.


# ========== LIHAT / RIWAYAT ==========
def cek_saldo(norek):
    print(f"\nSaldo anda: {format_rp(data_pengguna[norek]['saldo'])}") #Menampilkan saldo dengan format Rupiah.

def lihat_transaksi_saldo(norek):
    print("\n=== Riwayat Transaksi Saldo ===")
    if not data_pengguna[norek]["saldo_riwayat"]: #Cek apakah list saldo_riwayat kosong.
        print("Belum ada transaksi.") #Jika kosong → tampilkan pesan dan hentikan fungsi
        return
    for trx in data_pengguna[norek]["saldo_riwayat"]:
        print(trx) #Loop semua transaksi dan print satu per satu.

def lihat_transaksi_investasi(norek):
    print("\n=== Riwayat Investasi ===")
    if not data_pengguna[norek]["investasi_riwayat"]: #Jika tidak ada riwayat.
        print("Belum ada transaksi investasi.") #Tampilkan pesan dan keluar fungsi.
        return
    for trx in data_pengguna[norek]["investasi_riwayat"]: 
        print(trx) #Tampilkan pesan dan keluar fungsi.

# ========== DASHBOARD ==========
def dashboard_nasabah(norek):
    """Tampilkan dashboard lengkap (pilihan B)."""
    nama = data_pengguna[norek]["nama"] #Mengambil nama nasabah
    saldo = data_pengguna[norek]["saldo"] # Mengambil saldo
    emas = data_pengguna[norek]["investasi"]["emas"] # Jumlah emas yang dimiliki.
    tanah = data_pengguna[norek]["investasi"]["tanah"] #Jumlah meter tanah.
    deposito = data_pengguna[norek]["investasi"]["deposito"] #Dana deposito.
    total_investasi = emas * harga_emas_sekarang + tanah * harga_tanah_sekarang + deposito #Konversi emas dan tanah ke nilai Rupiah. tambahkan deosit. Hasil kekayaan investasi nasabha

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

    if norek not in data_pengguna: #Mengecek apakah nomor rekening tidak ada dalam database data_pengguna.
        print("Norek tidak ditemukan!")
        return

    if data_pengguna[norek].get("blocked", False): #Mengecek apakah akun memiliki status "blocked": True.
        print("Rekening anda diblokir. Hubungi admin.") #Jika terblokir → tidak bisa login.
        return

    if pin == data_pengguna[norek]["pin"]: #Mengecek apakah PIN yang diinput sama dengan PIN yang tersimpan.
        # reset failed count
        jumlah_pin_gagal[norek] = 0 #Reset hitungan kesalahan PIN menjadi 0.

        # generate harga dinamis setiap kali nasabah berhasil login
        hasilkan_harga()

        # tampilkan dashboard lengkap
        dashboard_nasabah(norek)

        # lanjut ke menu nasabah
        menu_nasabah(norek)
    else:
        jumlah_pin_gagal[norek] = jumlah_pin_gagal.get(norek, 0) + 1 #Menambah jumlah salah PIN sebanyak 1.
        sisa = 3 - jumlah_pin_gagal[norek] #Menghitung sisa kesempatan login (maksimal 3).
        print(f"PIN salah! Sisa kesempatan: {max(sisa,0)}")
        if jumlah_pin_gagal[norek] >= 3:
            data_pengguna[norek]["blocked"] = True #Mengubah status rekening menjadi terblokir.
            data_pengguna[norek]["saldo_riwayat"].append(f"!DIBLOKIR otomatis karena 3x salah PIN ({waktu_sekarang()})") #Menambahkan catatan ke riwayat saldo bahwa rekening diblokir otomatis.
            print("Akun diblokir permanen. Hubungi admin untuk membuka blokir.") #Menampilkan pesan bahwa akun terblokir dan harus dibuka admin.

# ========== VERIVUKASI PIN ==========
def verifikasi_aksi_pin(norek):
    """Minta PIN untuk konfirmasi tindakan sensitif. Jika salah 3x -> blokir permanen."""
    if data_pengguna[norek].get("blocked", False): #Mengecek apakah user sudah memiliki atribut "blocked": True.
        print("Rekening diblokir.")
        return False #Jika sudah terblokir → tidak bisa lanjut dan mengembalikan False.

    pin = input("Masukkan PIN untuk konfirmasi: ")
    if pin == data_pengguna[norek]["pin"]: #Mengecek kecocokan PIN.
        # reset counter jika sukses
        jumlah_pin_gagal[norek] = 0 #Reset jumlah pin gagal karena user sudah benar memasukkan PIN.
        return True #Berhasil → kembalikan True.
    else:
        # salah PIN -> increment
        jumlah_pin_gagal[norek] = jumlah_pin_gagal.get(norek, 0) + 1
        sisa = 3 - jumlah_pin_gagal[norek] #Hitung sisa kesempatan login.
        print(f"PIN salah! Sisa kesempatan: {max(sisa,0)}") #Tampilkan kesempatan yang tersisa.
        if jumlah_pin_gagal[norek] >= 3: #Jika kesalahan 3 kali atau lebih →
            data_pengguna[norek]["blocked"] = True #Rekening diblokir.
            data_pengguna[norek]["saldo_riwayat"].append(f"!DIBLOKIR otomatis karena 3x salah PIN ({waktu_sekarang()})")
            print("Akun diblokir permanen. Hubungi admin untuk membuka blokir.")
        return False #Karena PIN salah → kembalikan False.

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

    if user in akun_admin and akun_admin[user] == pw: #Apakah username ada dalam dictionary akun_admin. Apakah password yang diberikan cocok dengan yang tersimpan.
        print("Login admin berhasil!") #Jika benar → tampilkan pesan login sukses.
        menu_admin() #Kemudian masuk ke menu admin.
    else:
        print("Username / Password admin salah!") #Jika salah → tampilkan pesan error.

# ========== PROGRAM UTAMA ==========
def menu_utama():
    print("=== SISTEM ADMINISTRASI BANK MINI ===")

if __name__ == "__main__": #Mengecek apakah file ini dijalankan langsung (bukan di-import dari file lain).
    while True:             #Jika iya → menjalankan blok kode di bawahnya
        print("\n=== LOGIN SEBAGAI ===")
        print("1. Login Admin")
        print("2. Login Nasabah")
        print("3. Keluar")

        role = input("Pilih: ") #Meminta input pilihan user.

        if role == "1":
            login_admin()
        elif role == "2":
            login_nasabah()
        elif role == "3":
            print("Program selesai.")
            break
        else:
            print("Input salah!")
