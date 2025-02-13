import org.apache.spark.sql.{SparkSession, Dataset}
import org.apache.hadoop.conf.Configuration

object SparkS3WordCount {

  def main(args: Array[String]): Unit = {
    val spark = createSparkSession()

    val inputPath = "s3a://your-bucket-name/input/textfile.txt"
    val outputPath = "s3a://your-bucket-name/output/wordcount"

    val wordCounts = processWordCount(spark, inputPath)

    saveToS3(wordCounts, outputPath)

    spark.stop()
  }

  def createSparkSession(): SparkSession = {
    val spark = SparkSession.builder()
      .appName("Spark S3 Word Count")
      .master("local[*]") // Use "yarn" for cluster execution
      .getOrCreate()

    val hadoopConf: Configuration = spark.sparkContext.hadoopConfiguration
    hadoopConf.set("fs.s3a.access.key", "<AWS_ACCESS_KEY>")
    hadoopConf.set("fs.s3a.secret.key", "<AWS_SECRET_KEY>")
    hadoopConf.set("fs.s3a.endpoint", "s3.amazonaws.com")

    spark
  }

  def processWordCount(spark: SparkSession, inputPath: String): Dataset[(String, Int)] = {
    import spark.implicits._

    spark.sparkContext
      .textFile(inputPath)
      .flatMap(_.split("\\W+"))
      .map(_.toLowerCase)
      .filter(_.nonEmpty)
      .map(word => (word, 1))
      .reduceByKey(_ + _)
      .toDS()
  }

  def saveToS3(wordCounts: Dataset[(String, Int)], outputPath: String): Unit = {
    wordCounts
      .map { case (word, count) => s"$word: $count" }
      .write
      .text(outputPath)
  }
}
