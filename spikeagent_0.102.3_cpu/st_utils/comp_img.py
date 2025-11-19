import base64
from PIL import Image
from io import BytesIO

def compress_and_encode(image, max_size=(800, 800), quality=70):
    """이미지를 리사이징하고 base64로 인코딩하여 반환"""
    img = Image.open(image)

    # 이미지 리사이징 (최대 max_size 유지)
    img.thumbnail(max_size)

    # 압축된 이미지를 메모리 버퍼에 저장
    buffer = BytesIO()
    if img.format == "PNG":
        img.save(buffer, format="PNG", optimize=True)  # PNG 압축
    else:
        img.save(buffer, format="JPEG", quality=quality)  # JPEG 품질 조정
    
    # base64 인코딩
    encoded = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return encoded