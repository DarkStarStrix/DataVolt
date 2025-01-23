name := "SparkS3WordCount"

version := "0.1"

scalaVersion := "2.12.15"

libraryDependencies ++= Seq(
  "org.apache.spark" %% "spark-core" % "3.1.2",
  "org.apache.spark" %% "spark-sql" % "3.1.2",
  "org.apache.hadoop" % "hadoop-aws" % "3.2.0"
)

resolvers += "Apache Releases" at "https://repository.apache.org/content/repositories/releases/"
