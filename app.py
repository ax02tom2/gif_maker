import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

st.title("影像時序 GIF 動態圖製作工具")
st.write("請上傳多張依照日期命名的圖片，即可自動排序並加入浮水印製作 GIF！")

st.sidebar.header("設定選項")
duration_ms = st.sidebar.slider("每張圖片停留時間 (毫秒)", 200, 3000, 1000, 100)

st.sidebar.markdown("---")
st.sidebar.header("日期浮水印設定")
add_watermark = st.sidebar.checkbox("自動加入日期浮水印", value=True)

if add_watermark:
    text_color = st.sidebar.color_picker("文字顏色", "#FF0000")
    font_size = st.sidebar.slider("文字大小", 10, 150, 40, step=5)
    text_pos = st.sidebar.selectbox("文字位置", ["右下", "左下", "右上", "左上"])
else:
    text_color = "#FF0000"
    font_size = 40
    text_pos = "右下"

uploaded_files = st.file_uploader("請選擇或拖曳 JPG/PNG 圖片", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    st.success(f"成功上傳 {len(uploaded_files)} 張圖片！")
    
    if st.button("開始製作 GIF"):
        with st.spinner("正在合成中..."):
            images = []
            for f in uploaded_files:
                img = Image.open(f).convert("RGBA")
                if add_watermark:
                    draw = ImageDraw.Draw(img)
                    file_name = os.path.splitext(f.name)[0]
                    if len(file_name) == 7 and file_name.isdigit():
                        display_text = f"{file_name[:3]} / {file_name[3:5]} / {file_name[5:]}"
                    else:
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
                    
                    if text_pos == "右下":
                        xy = (w - tw - margin, h - th - margin)
                    elif text_pos == "左下":
                        xy = (margin, h - th - margin)
                    elif text_pos == "右上":
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
                
        st.success("GIF 製作完成！")
        st.image(gif_bytes, caption="預覽", use_container_width=True)
        st.download_button(label="下載 GIF 檔案", data=gif_bytes, file_name="slideshow.gif", mime="image/gif")
