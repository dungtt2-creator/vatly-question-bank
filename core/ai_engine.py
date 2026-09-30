# -*- coding: utf-8 -*-
"""
AI Classification Engine – lớp trừu tượng theo §18 đặc tả.

MVP KHÔNG gọi AI trả phí. Lớp này định nghĩa hợp đồng (contract) để Phase 2
cắm vào bất kỳ provider nào (Gemini, OpenAI, local LLM...):

    Question → Context → Taxonomy → Classification

Mọi provider phải trả đúng schema dưới đây. `HeuristicProvider` là implement
mặc định (chạy cục bộ, không tốn phí). UI hiển thị kết quả kèm `confidence` và
`classification_basis`; người dùng luôn có thể sửa trước khi lưu.
"""
import json
from abc import ABC, abstractmethod

CLASSIFICATION_SCHEMA = {
    "content_strand": str,
    "content": str,
    "knowledge_unit": str,
    "learning_outcome": str,
    "question_type": str,
    "cognitive_level": str,
    "difficulty": str,
    "confidence": float,
    "classification_basis": str,
    "duplicate_candidates": list,
}


class BaseClassificationProvider(ABC):
    """Hợp đồng chung cho mọi provider AI/Vật lý heuristic."""

    name = "base"

    @abstractmethod
    def classify(self, question: dict, context: dict = None, taxonomy: dict = None) -> dict:
        """
        question: {question_text, options, answer, solution, ...}
        context : {source_name, year, exam_name, ...}
        taxonomy: cây taxonomy đã nạp (để gợi ý node cụ thể)
        Trả về dict theo CLASSIFICATION_SCHEMA.
        Độ tin cậy < 0.5 hoặc thiếu căn cứ -> UI hiển thị "CẦN THẨM ĐỊNH".
        """


class HeuristicProvider(BaseClassificationProvider):
    """Provider mặc định (MVP): heuristic cục bộ, không tốn phí."""

    name = "heuristic-local"

    def classify(self, question, context=None, taxonomy=None):
        from .classifier import heuristic_classify
        return heuristic_classify(question, taxonomy)


class OpenAIClientProvider(BaseClassificationProvider):
    """
    Provider mẫu cho Phase 2 – ví dụ tích hợp API LLM.
    KHÔNG dùng trong MVP (cần API key). Để lại kiến trúc để cắm thêm sau.
    """

    name = "openai-compatible"

    def __init__(self, api_key="", model="", base_url=""):
        self.api_key = api_key
        self.model = model
        self.base_url = base_url

    def classify(self, question, context=None, taxonomy=None):
        # Phase 2: gọi HTTP tới provider, parse JSON theo CLASSIFICATION_SCHEMA.
        # MVP trả heuristic để không crash khi người dùng chọn provider này chưa cấu hình.
        from .classifier import heuristic_classify
        return heuristic_classify(question, taxonomy)


class ClassificationEngine:
    """Điểm vào duy nhất cho UI – chọn provider theo cấu hình."""

    def __init__(self, provider: BaseClassificationProvider = None):
        self.provider = provider or HeuristicProvider()

    def classify_question(self, question, context=None, taxonomy=None) -> dict:
        raw = self.provider.classify(question, context, taxonomy)
        # Chuẩn hóa output + đảm bảo đầy đủ khóa
        out = {k: None for k in CLASSIFICATION_SCHEMA}
        out.update(raw or {})
        if not isinstance(out.get("duplicate_candidates"), list):
            out["duplicate_candidates"] = []
        # Thiếu căn cứ -> đánh dấu cần thẩm định.
        # Theo đặc tả: không được tự bịa YCCĐ — câu chưa gắn được học kết quả
        # (learning_outcome) thì không thể tự động duyệt, phải CẦN THẨM ĐỊNH.
        needs_review = (
            (out.get("confidence") or 0) < 0.5
            or not out.get("classification_basis")
            or not out.get("learning_outcome")
        )
        out["needs_review"] = needs_review
        return out

    def classify_many(self, questions, context=None, taxonomy=None):
        return [self.classify_question(q, context, taxonomy) for q in questions]