import io
import base64

def encode_image(image):
    # Convert image to base64 string
    img_buffer = io.BytesIO()
    image.save(img_buffer, format="JPEG")
    base64_img_str = base64.b64encode(img_buffer.getvalue()).decode("utf-8")
    return base64_img_str
