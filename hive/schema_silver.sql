CREATE TABLE IF NOT EXISTS silver_pelanggan AS
SELECT
    id_pelanggan,
    provinsi_pelanggan,
    harga,
    total_pembayaran,
    kategori_produk,
    status_order,
    timestamp_pembelian,
    -- tambahan kolom yang sudah dibersihkan / diubah formatnya
FROM bronze_pelanggan
WHERE harga > 0 AND status_order = 'Selesai';
