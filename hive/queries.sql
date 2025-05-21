-- Total pembelian per provinsi per segmen
SELECT provinsi_pelanggan, segment, SUM(total_pembayaran) AS total_pembelian
FROM gold_segmentasi_pelanggan
GROUP BY provinsi_pelanggan, segment;

-- Frekuensi transaksi per segmen
SELECT segment, COUNT(*) AS jumlah_pelanggan
FROM gold_segmentasi_pelanggan
GROUP BY segment;
