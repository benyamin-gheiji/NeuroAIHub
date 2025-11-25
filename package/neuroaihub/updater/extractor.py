import json
import re

field_descriptions = {
    "dataset_name": "The official name of the dataset.",
    "doi": "The Digital Object Identifier (DOI) if available.",
    "url": "Link to access the dataset (if provided).",
    "year": "The year the dataset was published.",
    "access_type": "Whether the dataset is open-access, restricted, etc.",
    "institution": "The university, research lab, or company that gathered the dataset.",
    "country": "The country of the institution.",
    "modality": "The imaging type (e.g., MRI, CT, X-ray).",
    "resolution": "The imaging resolution (e.g., voxel size).",
    "subject_no": "The number of subjects.",
    "slice_scan_no": "The number of image slices or scans available.",
    "age_range": "The age range of the subjects.",
    "acquisition_protocol": "Details of how images were acquired.",
    "format": "The file format (e.g., DICOM, NIfTI, MHA, PNG, JPG, etc.).",
    "segmentation_mask": "Whether segmentation masks are included (Yes/No) and how they were created (manual/automatic).",
    "preprocessing": "Preprocessing steps applied to the dataset.",
    "disease": "The main disease(s) studied in the dataset.",
    "healthy_control": "Whether healthy controls are included (Yes/No).",
    "staging_information": "Disease staging details if available.",
    "clinical_data_score": "Whether clinical data or scores are included (if yes, specify what).",
    "histopathology": "Whether histopathology data is included (Yes/No).",
    "lab_data": "Whether lab data (e.g., blood tests) is included (Yes/No)."
}

field_names = list(field_descriptions.keys())

extraction_prompt = f"""
You are a highly accurate assistant specialized in medical imaging datasets.

Your task:
Extract the following 22 metadata fields from the given text about a neuroradiology dataset.

For each field:
- Provide a concise string value.
- If the information is missing or unclear, set the value to "Not specified".
- Do NOT include extra commentary or Markdown.

FIELDS TO EXTRACT:
{json.dumps(field_descriptions, indent=2)}

RESPONSE FORMAT:
Return ONLY a valid JSON object with these 22 keys and string values.
"""

def extract_dataset_info(text: str, llm):
    """Extract structured neuroradiology dataset information using the LLM."""
    if not text.strip():
        return {f: "Not specified" for f in field_names}

    try:
        full_prompt = f"{extraction_prompt}\n\nTEXT TO ANALYZE:\n{text}"
        response = llm.generate_json(
            system_prompt="You are a precise JSON-only dataset metadata extractor.",
            user_prompt=full_prompt,
            max_tokens=5000
        )

        if isinstance(response, dict):
            data = response 

        elif isinstance(response, str):
            cleaned = response.replace("```json", "").replace("```", "").strip()
            match = re.search(r"\{.*\}", cleaned, re.DOTALL)
            if not match:
                raise ValueError("No valid JSON object found in model output.")
            json_text = match.group(0)
            data = json.loads(json_text)

        else:
            raise TypeError(f"Unexpected LLM output type: {type(response)}")

        if not isinstance(data, dict):
            raise ValueError("Extracted data is not a dictionary.")

        normalized = {}
        for field in field_names:
            val = data.get(field, "Not specified")
            if not isinstance(val, str):
                val = str(val)
            val = re.sub(r"\s+", " ", val.strip()) or "Not specified"
            normalized[field] = val
        return normalized

    except Exception as e:
        print(f"⚠️ Extraction failed: {e}")
        return {f: "Not specified" for f in field_names}