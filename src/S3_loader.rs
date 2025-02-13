use rusoto_core::Region;
use rusoto_s3::{S3Client, S3, GetObjectRequest};
use tokio::io::AsyncReadExt;
use serde::Deserialize;
use std::error::Error;

#[derive(Debug, Deserialize)]
struct Record {
    id: i32,
    value: String,
}

struct S3Loader {
    bucket_name: String,
    file_key: String,
    s3_client: S3Client,
}

impl S3Loader {
    fn new(bucket_name: &str, file_key: &str, aws_access_key_id: &str, aws_secret_access_key: &str) -> Self {
        let region = Region::default();
        let s3_client = S3Client::new_with(
            rusoto_core::request::HttpClient::new().expect("Failed to create HTTP client"),
            rusoto_credential::StaticProvider::new_minimal(aws_access_key_id.to_string(), aws_secret_access_key.to_string()),
            region,
        );

        S3Loader {
            bucket_name: bucket_name.to_string(),
            file_key: file_key.to_string(),
            s3_client,
        }
    }

    async fn load_data(&self) -> Result<Vec<Record>, Box<dyn Error>> {
        let get_req = GetObjectRequest {
            bucket: self.bucket_name.clone(),
            key: self.file_key.clone(),
            ..Default::default()
        };

        let result = self.s3_client.get_object(get_req).await?;
        let stream = result.body.ok_or("No body in response")?;
        let mut body = stream.into_async_read();
        let mut data = Vec::new();
        body.read_to_end(&mut data).await?;

        let mut rdr = csv::Reader::from_reader(&data[..]);
        let mut records = Vec::new();
        for result in rdr.deserialize() {
            let record: Record = result?;
            records.push(record);
        }

        Ok(records)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let loader = S3Loader::new("your-bucket-name", "your-file-key", "your-access-key-id", "your-secret-access-key");
    let data = loader.load_data().await?;

    for record in data {
        println!("{:?}", record);
    }

    Ok(())
}
