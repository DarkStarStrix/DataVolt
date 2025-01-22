/// Rust bindings for loading CSV data with optimal memory usage and parallel processing
use std::path::{Path, PathBuf};
use std::sync::Arc;
use std::error::Error;
use log::{info, error};
use polars::prelude::*;
use rayon::prelude::*;
use sysinfo::{System, SystemExt};
use thiserror::Error;

#[derive(Error, Debug)]
pub enum LoaderError {
    #[error("Failed to read CSV file: {0}")]
    IoError(#[from] std::io::Error),
    #[error("Failed to process data: {0}")]
    ProcessingError(String),
    #[error("Invalid file path: {0}")]
    InvalidPath(String),
}

/// Configuration for the CSV loader
#[derive(Clone)]
pub struct LoaderConfig {
    reserved_ram_gb: f64,
    num_workers: usize,
}

impl Default for LoaderConfig {
    fn default() -> Self {
        Self {
            reserved_ram_gb: 2.0, // Reserve 2GB for system
            num_workers: 7,       // Use 7 threads by default
        }
    }
}

/// Main CSV loader struct
pub struct CSVLoader {
    file_path: PathBuf,
    config: LoaderConfig,
}

impl CSVLoader {
    /// Create a new CSVLoader instance
    pub fn new<P: AsRef<Path>>(file_path: P, config: Option<LoaderConfig>) -> Result<Self, LoaderError> {
        let file_path = file_path.as_ref().to_path_buf();
        if !file_path.exists() {
            return Err(LoaderError::InvalidPath(
                file_path.to_string_lossy().to_string()
            ));
        }

        Ok(Self {
            file_path,
            config: config.unwrap_or_default(),
        })
    }

    /// Calculate optimal chunk size based on available RAM
    fn calculate_chunk_size(&self, file_size: u64) -> usize {
        let sys = System::new_all();
        let total_ram_gb = sys.total_memory() as f64 / (1024.0 * 1024.0 * 1024.0);
        let available_ram_gb = total_ram_gb - self.config.reserved_ram_gb;

        // Estimate 1.5x file size for DataFrame memory usage
        let estimated_df_size_gb = (file_size as f64 * 1.5) / (1024.0 * 1024.0 * 1024.0);

        if estimated_df_size_gb < available_ram_gb {
            0 // Load entire file
        } else {
            // Calculate chunks to fit in 1/4 of available RAM
            let chunk_size = ((available_ram_gb * 0.25 * 1024.0 * 1024.0) / estimated_df_size_gb) as usize;
            chunk_size.max(1000) // Minimum 1000 rows per chunk
        }
    }

    /// Optimize data types for a DataFrame chunk
    fn optimize_chunk(df: &mut DataFrame) -> Result<(), LoaderError> {
        for column_name in df.get_column_names() {
            let column = df.column(column_name).map_err(|e| LoaderError::ProcessingError(e.to_string()))?;

            match column.dtype() {
                DataType::String => {
                    // Convert to categorical if less than 50% unique values
                    let unique_ratio = column.n_unique().map_err(|e| LoaderError::ProcessingError(e.to_string()))? as f64
                        / column.len() as f64;
                    if unique_ratio < 0.5 {
                        df.try_apply(column_name, |s| s.cast(&DataType::Categorical(None)))
                            .map_err(|e| LoaderError::ProcessingError(e.to_string()))?;
                    }
                },
                DataType::Float64 => {
                    // Downcast to Float32 if possible
                    df.try_apply(column_name, |s| s.cast(&DataType::Float32))
                        .map_err(|e| LoaderError::ProcessingError(e.to_string()))?;
                },
                DataType::Int64 => {
                    // Try to downcast to smaller integer types
                    let min = column.min::<i64>().unwrap_or(i64::MAX);
                    let max = column.max::<i64>().unwrap_or(i64::MIN);

                    let new_type = if min >= 0 {
                        if max <= u8::MAX as i64 { DataType::UInt8 }
                        else if max <= u16::MAX as i64 { DataType::UInt16 }
                        else if max <= u32::MAX as i64 { DataType::UInt32 }
                        else { DataType::UInt64 }
                    } else {
                        if min >= i8::MIN as i64 && max <= i8::MAX as i64 { DataType::Int8 }
                        else if min >= i16::MIN as i64 && max <= i16::MAX as i64 { DataType::Int16 }
                        else if min >= i32::MIN as i64 && max <= i32::MAX as i64 { DataType::Int32 }
                        else { DataType::Int64 }
                    };

                    df.try_apply(column_name, |s| s.cast(&new_type))
                        .map_err(|e| LoaderError::ProcessingError(e.to_string()))?;
                },
                _ => {}
            }
        }
        Ok(())
    }

    /// Load CSV data with optimal memory usage and parallel processing
    pub fn load_data(&self) -> Result<DataFrame, LoaderError> {
        let file_size = std::fs::metadata(&self.file_path)?.len();
        let chunk_size = self.calculate_chunk_size(file_size);

        info!("Loading CSV with chunk size: {}", if chunk_size > 0 { chunk_size.to_string() } else { "Full file".to_string() });

        if chunk_size == 0 {
            // Load entire file at once
            let mut df = CsvReader::from_path(&self.file_path)
                .map_err(|e| LoaderError::ProcessingError(e.to_string()))?
                .finish()
                .map_err(|e| LoaderError::ProcessingError(e.to_string()))?;

            Self::optimize_chunk(&mut df)?;
            info!("Successfully loaded data with shape: {:?}", df.shape());
            Ok(df)
        } else {
            // Load and process in chunks
            let file_path = Arc::new(self.file_path.clone());
            let chunks: Result<Vec<DataFrame>, LoaderError> = (0..)
                .into_par_iter()
                .map(|chunk_idx| {
                    let offset = chunk_idx * chunk_size;
                    let mut reader = CsvReader::from_path(file_path.as_ref())
                        .map_err(|e| LoaderError::ProcessingError(e.to_string()))?
                        .with_chunk_size(chunk_size)
                        .finish()
                        .map_err(|e| LoaderError::ProcessingError(e.to_string()))?;

                    match reader.nth(chunk_idx) {
                        Some(chunk_result) => {
                            let mut chunk = chunk_result.map_err(|e| LoaderError::ProcessingError(e.to_string()))?;
                            Self::optimize_chunk(&mut chunk)?;
                            Ok(chunk)
                        },
                        None => Err(LoaderError::ProcessingError("No more chunks".to_string())),
                    }
                })
                .take_while(|result| !matches!(result, Err(LoaderError::ProcessingError(e)) if e == "No more chunks"))
                .collect();

            // Combine all chunks
            let df = concat(chunks?.as_slice(), true)
                .map_err(|e| LoaderError::ProcessingError(e.to_string()))?;

            info!("Successfully loaded data with shape: {:?}", df.shape());
            Ok(df)
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use tempfile::NamedTempFile;
    use std::io::Write;

    #[test]
    fn test_csv_loader() -> Result<(), Box<dyn Error>> {
        // Create a temporary CSV file
        let mut file = NamedTempFile::new()?;
        writeln!(file, "id,value,category")?;
        writeln!(file, "1,10.5,A")?;
        writeln!(file, "2,20.7,B")?;
        writeln!(file, "3,30.2,A")?;

        // Initialize loader
        let loader = CSVLoader::new(file.path(), None)?;

        // Load data
        let df = loader.load_data()?;

        // Verify results
        assert_eq!(df.shape(), (3, 3));
        assert_eq!(df.column("id")?.len(), 3);

        Ok(())
    }
}
