use sqlx::postgres::PgPoolOptions;
use serde::Serialize;
use std::error::Error;

#[derive(Serialize)]
struct Record {
    // Define your record fields here
    id: i32,
    value: String,
}

struct SQLLoader {
    connection_string: String,
    query: String,
}

impl SQLLoader {
    async fn new(connection_string: &str, query: &str) -> Self {
        SQLLoader {
            connection_string: connection_string.to_string(),
            query: query.to_string(),
        }
    }

    async fn load_data(&self) -> Result<Vec<Record>, Box<dyn Error>> {
        let pool = PgPoolOptions::new()
            .max_connections(5)
            .connect(&self.connection_string)
            .await?;

        let rows = sqlx::query_as!(Record, &self.query)
            .fetch_all(&pool)
            .await?;

        Ok(rows)
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn Error>> {
    let loader = SQLLoader::new("postgres://user:password@localhost/dbname", "SELECT id, value FROM table").await;
    let data = loader.load_data().await?;

    for record in data {
        println!("{:?}", record);
    }

    Ok(())
}
