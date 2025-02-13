import uvicorn
from fastapi import FastAPI, UploadFile, File

from Loaders.csv_loader import CSVLoader
from preprocess import DataCleaner, Encoder

app = FastAPI()

@app.post("/preprocess/")
async def preprocess_data(file: UploadFile = File(...)):
    file_location = f"temp/{file.filename}"
    with open(file_location, "wb+") as file_object:
        file_object.write(file.file.read())

    loader = CSVLoader(file_path=file_location)
    data = loader.load_data()

    cleaner = DataCleaner(missing_value_strategy='mean')
    cleaned_data = cleaner.transform(data)

    encoder = Encoder()
    encoded_data = encoder.transform(cleaned_data)

    output_file_path = f"temp/processed_{file.filename}"
    encoded_data.to_csv(output_file_path, index=False)

    return {"message": "Data processed successfully", "file_path": output_file_path}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
