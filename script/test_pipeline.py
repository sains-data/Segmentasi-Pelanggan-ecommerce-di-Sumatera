import unittest
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import os

class TestPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.spark = SparkSession.builder \
            .appName("TestPipeline") \
            .master("local[*]") \
            .getOrCreate()

        cls.project_dir = os.path.dirname(os.path.abspath(__file__))
        cls.data_dir = os.path.join(cls.project_dir, '../data')

    @classmethod
    def tearDownClass(cls):
        cls.spark.stop()

    def test_ingest_data(self):
        # Misal data hasil ingest di bronze layer tersimpan di data/bronze
        bronze_path = os.path.join(self.data_dir, 'bronze')
        df = self.spark.read.parquet(bronze_path)
        self.assertGreater(df.count(), 0, "Data ingest ke bronze layer tidak boleh kosong")
        self.assertIn('id_pelanggan', df.columns, "Kolom 'id_pelanggan' harus ada di bronze data")

    def test_clean_transform(self):
        silver_path = os.path.join(self.data_dir, 'silver')
        df = self.spark.read.parquet(silver_path)
        self.assertGreater(df.count(), 0, "Data silver layer tidak boleh kosong")
        # Contoh cek data bersih, misal kolom harga tidak boleh negatif
        invalid_harga = df.filter(col('harga') < 0).count()
        self.assertEqual(invalid_harga, 0, "Harga tidak boleh negatif")

    def test_clustering_output(self):
        gold_path = os.path.join(self.data_dir, 'gold')
        df = self.spark.read.parquet(gold_path)
        self.assertGreater(df.count(), 0, "Hasil clustering (gold) tidak boleh kosong")
        self.assertIn('segment', df.columns, "Output clustering harus memiliki kolom 'segment'")

if __name__ == '__main__':
    unittest.main()
