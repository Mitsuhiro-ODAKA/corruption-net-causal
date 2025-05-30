# process_contracts.py

import argparse
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, explode, regexp_extract, initcap

def main():
    parser = argparse.ArgumentParser(description="Process procurement JSON into CSV with country column")
    parser.add_argument("--input",  required=True, help="Path to input contracts.json")
    parser.add_argument("--output", required=True, help="Path to output folder for CSV")
    args = parser.parse_args()

    # Spark セッションの作成
    spark = SparkSession.builder \
        .appName("ProcurementProcessing") \
        .getOrCreate()

    # JSON を読み込む（配列形式 JSON 対応）
    df = spark.read \
        .option("multiline", "true") \
        .json(args.input)

    # awards 配列を展開し、bureau と supplier を抽出
    exploded = df.select(
        col("buyer.id").alias("bureau"),
        explode("awards").alias("award")
    )

    # supplier.id 抽出 ＆ bureau から country 列を作成
    edges = exploded.select(
        col("bureau"),
        col("award.supplier.id").alias("supplier")
    ).withColumn(
        "country",
        initcap(
            regexp_extract(col("bureau"), r"^gov_(.+)$", 1)
        )
    )

    # CSV として出力（ヘッダー付き）
    edges.write \
        .mode("overwrite") \
        .option("header", "true") \
        .csv(args.output)

    spark.stop()

if __name__ == "__main__":
    main()
