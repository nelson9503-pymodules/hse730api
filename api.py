from .cover_extractor import CoverExtractor
from .content_extractor import ContentExtactor


def extract_cover(ad_type: str, page: int) -> dict:
    extractor = CoverExtractor()
    result = extractor.extract(ad_type, page)
    return result


def extract_content(ad_type: str, id: int) -> dict:
    extractor = ContentExtactor()
    result = extractor.extract(ad_type, id)
    return result
