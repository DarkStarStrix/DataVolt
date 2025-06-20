from pydantic import BaseModel, Field

class BiologyRequest(BaseModel):
    sequence: str = Field(..., description="Protein sequence")
    model_version: str = Field(default="2", pattern="^[12]$")
    confidence_threshold: float = Field(default=0.8, ge=0.0, le=1.0)

class MaterialsRequest(BaseModel):
    structure: str = Field(..., description="Material structure")
    model_version: str = Field(default="2", pattern="^[12]$")
    energy_threshold: float = Field(default=0.5, ge=0.0)

class DatasetRequest(BaseModel):
    model_type: str = Field(..., pattern="^(bio|materials)$")
    model_version: str = Field(default="2", pattern="^[12]$")
    size: int = Field(default=100, ge=10, le=1000)