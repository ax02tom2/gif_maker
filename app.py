import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

st.title("GIF Maker")

st.sidebar.header("Settings")
duration_ms = st.sidebar.slider("Speed (ms)", 200, 3000, 1000, 100)

add_watermark = st.sidebar.checkbox("Add Date Watermark", value=True)

if add_watermark:
    text_color = st.sidebar.color_picker("Color", "#FF0000")
    font_size = st.sidebar.slider("Size", 10, 150, 40, 5)
    text_pos = st.sidebar.selectbox("Position", ["BR", "BL", "TR", "TL"])
else:
    text_color = "#FF0000"
    font_size = 40
    text_pos = "BR"

uploaded_files = st.file_uploader("Upload JPG/PNG", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    st.success("Files uploaded!")
    
    if st.button("Create GIF"):
        with st.spinner("Processing..."):
            images = []
            for f in uploaded_files:
                img = Image.open(f).convert("RGBA")
                if add_watermark:
                    draw = ImageDraw.Draw(img)
                    file_name = os.path.splitext(f.name)[0]
                    display_text = file_name
                    
                    font = ImageFont.load_default()
                    try:
                        font = ImageFont.truetype("DejaVuSans.ttf", font_size)
                    except:
                        pass
                        
                    try:
                        left, top, right, bottom = font.getbbox(display_text)
                        tw, th = right - left, bottom - top
                    except:
                        tw, th = 200, 50
                        
                    w, h = img.size
                    margin = 30
                    
                    if text_pos == "BR":
                        xy = (w - tw - margin, h - th - margin)
                    elif text_pos == "BL":
                        xy = (margin, h - th - margin)
                    elif text_pos == "TR":
                        xy = (w - tw - margin, margin)
                    else:
                        xy = (margin, margin)
                        
                    draw.text((xy[0]+2, xy[1]+2), display_text, fill="black", font=font)
                    draw.text(xy, display_text, fill=text_color, font=font)
                
                images.append(img.convert("RGB"))
            
            base_size = images[0].size
            resized_images = [img.resize(base_size, Image.Resampling.LANCZOS) for img in images]
            
            output_path = "slideshow.gif"
            resized_images[0].save(
                output_path,
                save_all=True,
                append_images=resized_images[1:],
                duration=duration_ms,
                loop=0
            )
            
            with open(output_path, "rb") as file:
                gif_bytes = file.read()
                
        st.success("Done!")
        st.image(gif_bytes, use_container_width=True)
        st.download_button(label="Download GIF", data=gif_bytes, file_name="slideshow.gif", mime="image/gif")
