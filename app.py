from flask import Flask, render_template, request, send_file
from PIL import Image
import io
import os

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/process-image', methods=['POST'])
def process_image():
    if 'image' not in request.files:
        return "No image uploaded", 400
    
    file = request.files['image']
    if file.filename == '':
        return "No file selected", 400

    # অপারেশন টাইপ (Resize, Convert, Compress)
    operation = request.form.get('operation')
    
    try:
        img = Image.open(file.stream)
        img_io = io.BytesIO()

        # 1. কনভার্ট (Convert)
        if operation == 'convert':
            format_type = request.form.get('format').upper() # PNG, JPEG, WEBP
            if img.mode in ("RGBA", "P") and format_type == 'JPEG':
                img = img.convert("RGB") # JPEG ট্রান্সপারেন্সি সাপোর্ট করে না
            img.save(img_io, format_type, quality=90)
            mimetype = f'image/{format_type.lower()}'
            filename = f"converted.{format_type.lower()}"

        # 2. রিসাইজ (Resize)
        elif operation == 'resize':
            width = int(request.form.get('width'))
            height = int(request.form.get('height'))
            img = img.resize((width, height), Image.Resampling.LANCZOS)
            
            # সেভ করা
            fmt = img.format if img.format else 'PNG'
            img.save(img_io, fmt)
            mimetype = Image.MIME[fmt]
            filename = f"resized.{fmt.lower()}"

        # 3. কম্প্রেস (Compress)
        elif operation == 'compress':
            quality = int(request.form.get('quality')) # 10-90
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            img.save(img_io, 'JPEG', quality=quality, optimize=True)
            mimetype = 'image/jpeg'
            filename = "compressed.jpg"

        img_io.seek(0)
        return send_file(img_io, mimetype=mimetype, as_attachment=True, download_name=filename)

    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(debug=True)