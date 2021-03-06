# INASYLLG2P

*n*-gram tagger untuk silabifikasi dan konversi grapheme-to-phoneme (G2P) kata bahasa Indonesia.

## Pilih mode

Untuk memilih mode antara SYL (silabifikasi) dan G2P (konversi grafem ke fonem), pilih mode yang bersesuaian di bagian atas kiri aplikasi.

# Silabifikasi (SYL)

## Training

Tab training akan membuat model n-gram berdasarkan data train dan parameter yang diberikan.

### Data train

Data train berupa file teks yang berisi dua kolom yang dipisahkan oleh karakter TAB (\t) di mana kolom pertama berupa kata utuh (contoh: "angkasa") dan kolom kedua berupa silabifikasinya (contoh: ang&#46;ka&#46;sa). Tiap silabel dipisahkan oleh karakter titik ("."). Baris pertama tidak perlu diisi oleh judul/header kolom. Karakter yang diperbolehkan adalah huruf a-z (huruf kecil) dan dash ("-"). Selain dari karakter-karakter tersebut akan menyebabkan error jadi pastikan karakter-karakter lain sudah di-strip dari data train.

Berikut adalah contoh dari data train yang valid:
```
april   a.pril
apriori	a.pri.o.ri
aprit	a.prit
aprit-apritan	a.prit-a.pri.tan
apsara	ap.sa.ra
apsidal	ap.si.dal
```

Jika akan menggunakan k-fold cross validation, nama file harus berakhiran "\_fold\_[*k*]"  di mana [*k*] adalah nomor fold. 

Berikut contoh nama-nama file untuk 5-fold cross validation:
```
train_fold_1.txt
train_fold_2.txt
train_fold_3.txt
train_fold_4.txt
train_fold_5.txt
```

### Pengaturan parameter

Pengaturan parameter ada di sidebar "Params" pada bagian kiri aplikasi. Berikut penjelasan dari masing-masing parameter:

- `Maximum n`: Order *n* maksimal yang akan digunakan. Jika dimasukkan nilai 5, model yang dibuat akan terdiri dari 5-gram, 4-gram, sampai unigram yang disatukan dalam satu file. Order lebih rendah nanti digunakan dalam proses back-off/interpolation pada smoothing di fase testing. Jika pada fase testing rencananya akan mencoba untuk memakai bigram sampai 6-gram, maka hanya perlu membuat satu model dengan parameter Maximum *n* = 6.
- `Ensure lower case`: Mengubah teks pada data train menjadi huruf kecil semua sebelum diproses.
- `Continuation count`: Digunakan untuk metode smoothing `GKN` dan `KN` pada fase testing.
- `Follow count`: Digunakan untuk metode smoothing `GKN` pada fase testing.

Jika ragu, biarkan parameter `Continuation count` dan `Follow count` bernilai default (aktif).

### File data train

Untuk menambah file data train, klik tombol `Add File(s)`  pada bagian "Train file" lalu pilih satu atau beberapa file yang diinginkan. Saat menggunakan k-fold cross validation, bisa langsung dipilih semua fold yang akan digunakan. Jika berhasil, nama file akan ditambahkan di daftar "Train file". Untuk menghapus satu file, klik tombol `X` di samping nama file. Untuk menghapus semua file, klik tombol `Remove All`

### File output

Model n-gram yang dihasilkan akan disimpan pada file JSON (\*.json). Masukan nama file yang diinginkan pada bagian "File name". Klik tombol `Auto` untuk meng-generate file name secara otomatis berdasarkan parameter. Pilih lokasi folder tempat menyimpan model dengan meng-klik tombol `Browse` pada bagian "Directory". Jika menggunakan k-fold cross validation dan penamaan file data train sesuai dengan yang dijelaskan di bagian A, nama file output akan otomatis diberi akhiran "\_fold\_[*k*]" untuk setiap fold.

### Memulai training

Jika semua parameter dan file data train sudah siap, klik tombol `Start` untuk memulai proses training. Status dari training dapat dilihat pada status bar di bagian bawah aplikasi.

## Testing

Tab testing akan melakukan silabifikasi pada kata berdasarkan model n-gram yang telah dibuat pada fase training dan menghitung error rate yang dihasilkan.

### Data test

Ketentuan data test sama dengan yang dijelaskan pada bagian data train sebelumnya. Begitu juga penamaan file untuk k-fold cross validation. Pastikan penamaan nomor fold pada nama file sesuai dengan data train yang bersangkutan. Data test dapat hanya terdiri dari satu kolom saja yang berisi kata utuh tanpa silabifikasinya. Jika demikian, matikan opsi `validation` pada pengaturan parameter.

### Pengaturan parameter

Pengaturan parameter ada di sidebar "Params" pada bagian kiri aplikasi. Berikut penjelasan dari masing-masing parameter:

- `n`:  Order *n* yang digunakan. Pastikan nilai *n* tidak melebihi nilai *n* maksimal dari model yang digunakan.
- `Ensure lower case`: Mengubah teks pada data test menjadi huruf kecil semua sebelum diproses.
- `State-elimination`: Opsi untuk menggunakan metode state-elimination pada proses tagging.
- `Augmented n-gram`: Opsi untuk menggunakan n-gram tambahan hasil augmentasi. Jika aktif, maka perlu memilih dua set file model n-gram untuk setiap data test.
- `Aug. weight`: Bobot dari n-gram augmentasi pada perhitungan probabilitas jika menggunakan `Augmented n-gram`.
- `Augmented probability`: Opsi untuk menggunakan augmented probability.
- `Flipped onsets`: Menggunakan probabilitas dari kata yang di-flip onsetnya dalam perhitungan probabilitas jika menggunakan `Augmented probability`.
- `Transposed nucleus`: Menggunakan probabilitas dari kata yang di-transpose nucleusnya dalam perhitungan probabilitas jika menggunakan `Augmented probability`.
- `Smoothing`: Metode smoothing yang digunakan dalam perhitungan probabilitas. Terdapat tiga opsi: `GKN` (Generalized Kneser-Ney), `KN` (Kneser-Ney) dan `Stupid Backoff`. `GKN` mempunyai performa paling bagus tetapi lebih lambat dari dua opsi lainnya.
- `B` (Parameter `GKN`): Jumlah parameter diskon yang digunakan.
- `D` (Parameter `KN`): Nilai diskon yang digunakan.
- `Alpha` (Parameter `Stupid Backoff`): Nilai pengali pada nilai probabilitas backoff.
- `Validation`: Jika aktif, berarti hasil prediksi silabifikasi akan dibandingkan dengan silabifikasi sebenarnya yang ada di data test dan dihitung error rate-nya. Jika tidak aktif, tidak akan dilakukan perhitungan error rate dan data test harus hanya terdiri dari satu kolom saja (kata tanpa silabifikasinya).
- `Save log`: File log akan memuat informasi mengenai hasil testing.
- `Save result`: File result akan berisi hasil prediksi silabifikasi.
- `Timestamp`: Opsi untuk menambah prefix timestamp pada file result.

### File data test dan n-gram

Cara untuk menambah file data test sama seperti menambahkan data train di fase training. Hanya saja di sini perlu juga untuk menambahkan file model n-gram yang dihasilkan dari training. Jika menggunakan `Augmented n-gram`, tambahkan juga file model augmented n-gram. Pastikan file data test dan n-gram jumlahnya sama.

### File output

Masukan nama file untuk file log dan result pada bagian "File name". Klik tombol `Auto` untuk meng-generate file name secara otomatis berdasarkan parameter. Pilih lokasi folder tempat menyimpan file result dengan meng-klik tombol `Browse` pada bagian "Directory". Jika menggunakan k-fold cross validation dan penamaan file data test sesuai dengan yang dijelaskan di bagian data train, nama file result akan otomatis diberi akhiran "\_fold\_[*k*]" untuk setiap fold. File log akan disimpan di subfolder "logs" pada folder file result.

### Memulai testing

Jika semua parameter, file data test, dan file n-gram sudah siap, klik tombol `Start` untuk memulai proses testing. Status dari testing dapat dilihat pada status bar di bagian bawah aplikasi.

## Augmentation

Tab augmentation akan membuat data train baru berdasarkan data train asli dengan menerapkan berbagai metode augmentasi.

### Data train

Spesifikasi data train yang digunakan sama dengan bagian Training

### Opsi augmentasi

- `Ensure lower case`: Mengubah teks pada data train menjadi huruf kecil semua sebelum diaugmentasi.

### Metode augmentasi

- `Flip onsets`: Menukar onset silabel pertama dan kedua dari kata.
- `Swap consonants`: Menukar konsonan pada kata dengan konsonan lain yang berbunyi mirip.
- `Transpose nucleus`: Menukar nucleus silabel pertama dan kedua dari kata.

### Pengaturan lainnya

- `Distinct`: Memastikan semua kata hasil augmentasi unik (tidak ada duplikat).
- `Validation`: Memvalidasi setiap kata hasil augmentasi terhadap daftar sekuen grafem ilegal. Jika opsi dipilih, file teks (\*.txt) yang berisi daftar sekuen grafem ilegal harus dipilih.
- `Inc. original words`: Mengikutsertakan kata asli ke hasil augmentasi.

### File data train

Peraturan nama file sama dengan bagian Training

### Memulai augmentasi

Untuk memulai augmentasi data train, minimal harus ada satu metode yang dipilih. Beberapa metode dapat digunakan sekaligus. Jika file data train sudah siap, klik tombol `Start` untuk memulai proses augmentasi.

## Settings

Pada tab settings, dapat ditentukan `List of vowels`, `List of semi-vowels`, dan `List of diphtongs` yang digunakan dalam proses augmentasi data train. Setiap item pada masing-masing list dipisahkan oleh spasi. Klik tombol `Apply` untuk menyimpan pengaturan. Klik tombol `Revert` untuk mengembalikan ke pengaturan sebelumnya.

## Log file

Syllable error rate (SER) keseluruhan dapat dilihat pada bagian `"overall": average_ser`. Untuk SER dari masing-masing file data test/fold dapat dilihat pada bagian `"results: [i/fold]: syllable_error_rate"` 

## Result file

Untuk testing dengan validation, file result yang dihasilkan terdiri dari 4 kolom:

1. Kata asli
2. Silabifikasi sebenarnya
3. Silabifikasi hasil prediksi
4. Jumlah kesalahan silabel prediksi

Sedangkan tanpa validation, file result terdiri dari 2 kolom:

1. Kata asli
2. Silabifikasi hasil prediksi

# Grapheme-to-phoneme (G2P)

## Training

Tab training akan membuat model n-gram berdasarkan data train dan parameter yang diberikan.

### Data train

Data train berupa file teks yang berisi dua kolom yang dipisahkan oleh karakter TAB (\t) di mana kolom pertama berupa kata dalam bentuk grafem (contoh: "berang") dan kolom kedua berupa kata dalam bentuk fonem (contoh: "bera)*"). Baris pertama tidak perlu diisi oleh judul/header kolom.

Berikut adalah contoh dari data train yang valid:
```
gerai	g#r$*
geramang	g#rama)*
gerangan	g#ra)*an
gerantang	g#ranta)*
geratak	g#ratak
```

Jika akan menggunakan k-fold cross validation, nama file harus berakhiran "\_fold\_[*k*]"  di mana [*k*] adalah nomor fold. 

Berikut contoh nama-nama file untuk 5-fold cross validation:
```
train_fold_1.txt
train_fold_2.txt
train_fold_3.txt
train_fold_4.txt
train_fold_5.txt
```

### Pengaturan parameter

Pengaturan parameter ada di sidebar "Params" pada bagian kiri aplikasi. Berikut penjelasan dari masing-masing parameter:

- `Maximum n`: Order *n* maksimal yang akan digunakan. Jika dimasukkan nilai 5, model yang dibuat akan terdiri dari 5-gram, 4-gram, sampai unigram yang disatukan dalam satu file. Order lebih rendah nanti digunakan dalam proses back-off/interpolation pada smoothing di fase testing. Jika pada fase testing rencananya akan mencoba untuk memakai bigram sampai 6-gram, maka hanya perlu membuat satu model dengan parameter Maximum *n* = 6.
- `Ensure lower case`: Mengubah teks pada data train menjadi huruf kecil semua sebelum diproses.
- `Continuation count`: Digunakan untuk metode smoothing `GKN` dan `KN` pada fase testing.
- `Follow count`: Digunakan untuk metode smoothing `GKN` pada fase testing.

Jika ragu, biarkan parameter `Continuation count` dan `Follow count` bernilai default (aktif).

### File data train

Untuk menambah file data train, klik tombol `Add File(s)`  pada bagian "Train file" lalu pilih satu atau beberapa file yang diinginkan. Saat menggunakan k-fold cross validation, bisa langsung dipilih semua fold yang akan digunakan. Jika berhasil, nama file akan ditambahkan di daftar "Train file". Untuk menghapus satu file, klik tombol `X` di samping nama file. Untuk menghapus semua file, klik tombol `Remove All`

### File output

Model n-gram yang dihasilkan akan disimpan pada file JSON (\*.json). Masukan nama file yang diinginkan pada bagian "File name". Klik tombol `Auto` untuk meng-generate file name secara otomatis berdasarkan parameter. Pilih lokasi folder tempat menyimpan model dengan meng-klik tombol `Browse` pada bagian "Directory". Jika menggunakan k-fold cross validation dan penamaan file data train sesuai dengan yang dijelaskan di bagian A, nama file output akan otomatis diberi akhiran "\_fold\_[*k*]" untuk setiap fold.

### Memulai training

Jika semua parameter dan file data train sudah siap, klik tombol `Start` untuk memulai proses training. Status dari training dapat dilihat pada status bar di bagian bawah aplikasi.

## Testing

Tab testing akan melakukan fonemisasi pada kata berdasarkan model n-gram yang telah dibuat pada fase training dan menghitung error rate yang dihasilkan.

### Data test

Ketentuan data test sama dengan yang dijelaskan pada bagian data train sebelumnya. Begitu juga penamaan file untuk k-fold cross validation. Pastikan penamaan nomor fold pada nama file sesuai dengan data train yang bersangkutan. Data test dapat hanya terdiri dari satu kolom saja yang berisi kata dalam bentuk grafem. Jika demikian, matikan opsi `validation` pada pengaturan parameter.

### Pengaturan parameter

Pengaturan parameter ada di sidebar "Params" pada bagian kiri aplikasi. Berikut penjelasan dari masing-masing parameter:

- `n`:  Order *n* yang digunakan. Pastikan nilai *n* tidak melebihi nilai *n* maksimal dari model yang digunakan.
- `Ensure lower case`: Mengubah teks pada data test menjadi huruf kecil semua sebelum diproses.
- `Phonetic rules`: Opsi untuk menggunakan phonetic rules pada proses tagging.
- `Stemming`: Opsi untuk menggunakan stemming pada proses tagging.
- `Smoothing`: Metode smoothing yang digunakan dalam perhitungan probabilitas. Terdapat tiga opsi: `GKN` (Generalized Kneser-Ney), `KN` (Kneser-Ney) dan `Stupid Backoff`. `GKN` mempunyai performa paling bagus tetapi lebih lambat dari dua opsi lainnya.
- `B` (Parameter `GKN`): Jumlah parameter diskon yang digunakan.
- `D` (Parameter `KN`): Nilai diskon yang digunakan.
- `Alpha` (Parameter `Stupid Backoff`): Nilai pengali pada nilai probabilitas backoff.
- `Validation`: Jika aktif, berarti hasil prediksi fonemisasi akan dibandingkan dengan fonemisasi sebenarnya yang ada di data test dan dihitung error rate-nya. Jika tidak aktif, tidak akan dilakukan perhitungan error rate dan data test harus hanya terdiri dari satu kolom saja (kata tanpa fonemisasinya).
- `Save log`: File log akan memuat informasi mengenai hasil testing.
- `Save result`: File result akan berisi hasil prediksi fonemisasi.
- `Timestamp`: Opsi untuk menambah prefix timestamp pada file result.
- `Inc. no-phoneme symbol`: Opsi untuk menyertakan simbol *no-phoneme* `*` pada file result.

### File data test dan n-gram

Cara untuk menambah file data test sama seperti menambahkan data train di fase training. Hanya saja di sini perlu juga untuk menambahkan file model n-gram yang dihasilkan dari training.

### File output

Masukan nama file untuk file log dan result pada bagian "File name". Klik tombol `Auto` untuk meng-generate file name secara otomatis berdasarkan parameter. Pilih lokasi folder tempat menyimpan file result dengan meng-klik tombol `Browse` pada bagian "Directory". Jika menggunakan k-fold cross validation dan penamaan file data test sesuai dengan yang dijelaskan di bagian data train, nama file result akan otomatis diberi akhiran "\_fold\_[*k*]" untuk setiap fold. File log akan disimpan di subfolder "logs" pada folder file result.

### Memulai testing

Jika semua parameter, file data test, dan file n-gram sudah siap, klik tombol `Start` untuk memulai proses testing. Status dari testing dapat dilihat pada status bar di bagian bawah aplikasi.

## Log file

Phoneme error rate (PER) keseluruhan dapat dilihat pada bagian `"overall": average_per`. Untuk PER dari masing-masing file data test/fold dapat dilihat pada bagian `"results: [i/fold]: phoneme_error_rate"` 

## Result file

Untuk testing dengan validation, file result yang dihasilkan terdiri dari 4 kolom:

1. Kata asli
2. Fonemisasi sebenarnya
3. Fonemisasi hasil prediksi
4. Jumlah kesalahan fonem prediksi

Sedangkan tanpa validation, file result terdiri dari 2 kolom:

1. Kata asli
2. Fonemisasi hasil prediksi