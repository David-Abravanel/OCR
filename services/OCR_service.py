import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from paddleocr import PaddleOCR
from modules import OcrData, OcrResult

logger = logging.getLogger(__name__)

SUPPORTED_LANGUAGES = ['en', 'es', 'fr', 'de', 'it']


class OcrService:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OcrService, cls).__new__(cls)
        return cls._instance

    def __init__(self, max_workers=8):
        if hasattr(self, "initialized"):
            return

        self.initialized = False
        self.ocr_models = {}
        self.queue = asyncio.Queue()
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        # Limit the number of concurrent tasks
        self.semaphore = asyncio.Semaphore(1)
        self.worker_task = None
        self._shutdown_event = asyncio.Event()

    async def initialize(self):
        async with self._lock:
            if self.initialized:
                return

            logger.info("Initializing OCR models...")
            try:
                self.ocr_models = {
                    lang: PaddleOCR(
                        lang=lang,
                        show_log=False,
                        det_db_box_thresh=0.3,
                        use_angle_cls=False,
                        rec_algorithm='CRNN',
                    )
                    for lang in SUPPORTED_LANGUAGES
                }
                self.worker_task = asyncio.create_task(self._process_queue())
                self.initialized = True
                logger.info("OCR models initialized successfully.")
            except Exception as e:
                logger.exception(f"Failed to initialize OCR models: {e}")
                raise

    async def shutdown(self):
        logger.info("Shutting down OcrService...")
        self._shutdown_event.set()

        # Wait for the queue to empty before shutting down
        await self.queue.join()
        if self.worker_task:
            await self.worker_task

        self.executor.shutdown(wait=True)
        logger.info("OcrService shutdown complete.")

    def _run_model(self, ocr_data: OcrData) -> OcrResult:
        if ocr_data.lang not in SUPPORTED_LANGUAGES:
            raise ValueError(f"Language '{ocr_data.lang}' is not supported")

        ocr_model = self.ocr_models[ocr_data.lang]
        results = ocr_model.ocr(ocr_data.image)

        texts = []
        output_data = []

        for line in results[0]:
            box, (text, score) = line
            texts.append(text)
            output_data.append({
                'language': ocr_data.lang,
                'bounding_box': box,
                'text': text,
                'confidence': score
            })

        return OcrResult(texts=texts, output_data=output_data)

    async def add_image_to_queue(self, ocr_data: OcrData) -> OcrResult:
        if not self.initialized:
            raise RuntimeError("OcrService not initialized")

        result = await self._process_task(ocr_data)
        return result

    async def _process_task(self, ocr_data: OcrData) -> OcrResult:
        """Process each OCR task asynchronously"""
        async with self.semaphore:  # Limit concurrency
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(self.executor, self._run_model, ocr_data)
        return result

    async def _process_queue(self):
        while not self._shutdown_event.is_set() or not self.queue.empty():
            try:
                try:
                    ocr_data, future = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                except asyncio.TimeoutError:
                    continue  # Check shutdown event periodically

                # Process task concurrently
                result = await self._process_task(ocr_data)
                future.set_result(result)

                self.queue.task_done()

            except Exception as e:
                logger.exception(f"Error in processing queue: {e}")
                if 'future' in locals() and not future.done():
                    future.set_exception(e)
