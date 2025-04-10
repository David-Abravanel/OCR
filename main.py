# import time
# from paddleocr import PaddleOCR
# import json

# from check import is_financial_document

# # List of languages supported by PaddleOCR
# languages = [
#     'en',
#     #   'ch', 'chinese_cht', 'japan', 'korean',
#     # 'latin', 'arabic', 'cyrillic', 'devanagari',
#     # 'ta', 'te', 'ka'
# ]

# # Path to the image
# image_path = 'example.png'

# # Prepare data for JSON
# output_data = []
# ocr_text = []

# # Initialize OCR models for each language
# ocr_models = {lang: PaddleOCR(use_angle_cls=True, lang=lang)
#               for lang in languages}

# start_time = time.time()

# for lang, ocr in ocr_models.items():
#     print(f"Running OCR for language: {lang}")
#     results = ocr.ocr(image_path, cls=True)

#     # Check if results are valid
#     if results is None or len(results) == 0 or results[0] is None:
#         print(f"No results for language: {lang}")
#         continue

#     for line in results[0]:
#         box = line[0]  # Coordinates of the bounding box
#         text = line[1][0]  # Extracted text
#         score = line[1][1]  # Confidence score
#         ocr_text.append(text)
#         output_data.append({
#             'language': lang,
#             'bounding_box': box,
#             'text': text,
#             'confidence': score
#         })

# print("OCR process time:", time.time() - start_time)

# is_financial, lang, keywords_found = is_financial_document("\n".join(ocr_text))

# # Check additional examples
# if is_financial:
#     print(
#         f"The document in {lang} contains financial content. Found keywords:")
#     print(keywords_found)
# else:
#     print(f"The document in {lang} does not contain financial content.")

# print("\n".join(ocr_text))
# # Save to JSON file
# output_json_path = 'ocr_results.json'
# with open(output_json_path, 'w', encoding='utf-8') as json_file:
#     json.dump(output_data, json_file, ensure_ascii=False, indent=4)

# print(f"OCR results saved to {output_json_path}")


import time
import cv2
import uvicorn
import numpy as np
from fastapi import FastAPI
from contextlib import asynccontextmanager

from services import OcrService, FinancialDocumentProcessor
from modules import OcrData
import warnings
warnings.filterwarnings("ignore")


ocr_service = OcrService()
document_type_service = FinancialDocumentProcessor.get_instance()


# Initialize OCR service globally


@asynccontextmanager
async def lifespan(app: FastAPI):
    await ocr_service.initialize()
    try:
        yield
    finally:
        await ocr_service.shutdown()
        pass

app = FastAPI(title="OCR Detection Service", lifespan=lifespan)


@app.post("/ocr")
async def run_ocr():
    start_time = time.time()
    image_path = "example.png"
    image = cv2.imread(image_path)
    if image is None:
        raise ValueError("Image could not be loaded")
    ocr_data = OcrData(image=image)

    result = await ocr_service.add_image_to_queue(ocr_data)

    print("OCR process time:", time.time() - start_time)
    is_financial, lang, keywords_found = document_type_service.is_financial_document(
        "\n".join(result.texts))

    # Check additional examples
    if is_financial:
        print(
            f"The document in {lang} contains financial content. Found keywords:")
        print(keywords_found)
    else:
        print(f"The document in {lang} does not contain financial content.")

    return {
        "lang": lang,
        "is_financial": is_financial,
        "keywords": keywords_found,
        "texts": result.texts,
        # "output_data": result.output_data
    }


@app.get("/health")
async def health_check():
    return {"status": "ok"}


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        # workers=1,
        reload=True
    )
