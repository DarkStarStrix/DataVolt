import org.apache.spark.sql.{SparkSession, Dataset}
import org.apache.hadoop.conf.Configuration

object SparkS3WordCount {

  def main(args: Array[String]): Unit = {
    // Step 1: Initialize Spark session
    val spark = createSparkSession()

    // Input and output paths (can also be passed as arguments for flexibility)
    val inputPath = "s3a://your-bucket-name/input/textfile.txt"
    val outputPath = "s3a://your-bucket-name/output/wordcount"

    // Step 2: Process the data
    val wordCounts = processWordCount(spark, inputPath)

    // Step 3: Save the results to S3
    saveToS3(wordCounts, outputPath)

    // Stop Spark session
    spark.stop()
  }

  /** Creates and configures the Spark session. */
  def createSparkSession(): SparkSession = {
    val spark = SparkSession.builder()
      .appName("Spark S3 Word Count")
      .master("local[*]") // Use "yarn" for cluster execution
      .getOrCreate()

    // Configure S3 credentials
    val hadoopConf: Configuration = spark.sparkContext.hadoopConfiguration
    hadoopConf.set("fs.s3a.access.key", "<AWS_ACCESS_KEY>")
    hadoopConf.set("fs.s3a.secret.key", "<AWS_SECRET_KEY>")
    hadoopConf.set("fs.s3a.endpoint", "s3.amazonaws.com")

    spark
  }

  /** Processes the word count logic and returns the results as a Dataset. */
  def processWordCount(spark: SparkSession, inputPath: String): Dataset[(String, Int)] = {
    import spark.implicits._

    spark.sparkContext
      .textFile(inputPath) // Load the text file from S3
      .flatMap(_.split("\\W+")) // Split lines into words
      .map(_.toLowerCase) // Normalize to lowercase
      .filter(_.nonEmpty) // Filter out empty words
      .map(word => (word, 1)) // Create (word, 1) tuples
      .reduceByKey(_ + _) // Aggregate counts by key
      .toDS() // Convert to a Dataset for better type safety
  }

  /** Saves the processed data back to S3. */
  def saveToS3(wordCounts: Dataset[(String, Int)], outputPath: String): Unit = {
    wordCounts
      .map { case (word, count) => s"$word: $count" } // Format output as "word: count"
      .write
      .text(outputPath) // Save as text files in the specified S3 path
  }
}
