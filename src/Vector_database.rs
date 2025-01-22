use sqlx::{Pool, Postgres, Row};
use sqlx::postgres::PgPoolOptions;
use anyhow::Result;

pub struct VectorDatabase {
    pool: Pool<Postgres>,
    table_name: String,
}

impl VectorDatabase {
    pub async fn new(connection_string: &str, table_name: &str) -> Result<Self> {
        let pool = PgPoolOptions::new()
            .max_connections(5)
            .connect(connection_string)
            .await?;

        Ok(Self {
            pool,
            table_name: table_name.to_string(),
        })
    }

    pub async fn create_table(&self) -> Result<()> {
        let query = format!(
            "CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                vector FLOAT NOT NULL
            )",
            self.table_name
        );

        sqlx::query(&query).execute(&self.pool).await?;
        Ok(())
    }

    pub async fn insert_vector(&self, vector: f32) -> Result<()> {
        let query = format!(
            "INSERT INTO {} (vector) VALUES ($1)",
            self.table_name
        );

        sqlx::query(&query)
            .bind(vector)
            .execute(&self.pool)
            .await?;
        Ok(())
    }

    pub async fn query_vectors(&self) -> Result<Vec<f32>> {
        let query = format!(
            "SELECT vector FROM {}",
            self.table_name
        );

        let rows = sqlx::query(&query)
            .fetch_all(&self.pool)
            .await?;

        Ok(rows.iter().map(|row| row.get("vector")).collect())
    }
}
