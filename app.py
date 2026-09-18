import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os

st.title("📁 影像時序 GIF 動態圖製作工具")
st.write("請直接上傳依照日期命名的圖片，即可自動排序並加入日期製作 GIF。")

st.sidebar.header("⚙️ 播放設定")
duration_ms = st.sidebar.slider("每張圖片停留時間 (毫秒)", 200, 3000, 1000, 100)

st.sidebar.markdown("---")
st.sidebar.header("📝 日期浮水印設定")
add_watermark = st.sidebar.checkbox("自動加入日期浮水印", value=True)

if add_watermark:
    text_color = st.sidebar.color_picker("文字顏色", "#FF0000")
    font_size = st.sidebar.slider("文字大小", 10, 150, 60, step=5)
    text_pos = st.sidebar.selectbox("文字位置", ["右下", "左下", "右上", "左上"])
else:
    text_color, font_size, text_pos = "#FF0000", 60, "右下"

uploaded_files = st.file_uploader("請選擇或拖曳圖片檔案", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    st.success(f"✅ 成功上傳 {len(uploaded_files)} 張圖片！")
    
    for f in uploaded_files:
        st.text(f"已排入: {f.name}")

    if st.button("🚀 開始製作 GIF"):
        with st.spinner("正在合成中，請稍候..."):
            images = []
            for f in uploaded_files:
                img = Image.open(f).convert("RGBA")
                if add_watermark:
                    draw = ImageDraw.Draw(img)
                    file_name = os.path.splitext(f.name)[0]
                    # 日期格式化: 1150522 -> 115 / 05 / 22
                    if len(file_name) == 7 and file_name.isdigit():
                        display_text = f"{file_name[:3]} / {file_name[3:5]} / {file_name[5:]}"
                    else:
                        display_text = file_name
                    
                    # 尋找雲端系統可用的字型
                    font = None
                    font_paths = [
                        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
                    ]
                    for path in font_paths:
                        if os.path.exists(path):
                            font = ImageFont.truetype(path, font_size)
                            break
                    if font is None:
                        font = ImageFont.load_default()

                    # 計算位置
                    w, h = img.size
                    try:
                        left, top, right, bottom = font.getbbox(display_text)
                        tw, th = right - left, bottom - top
                    except:
                        tw, th = font_size * len(display_text) * 0.6, font_size

                    margin = 40
                    if text_pos == "右下": xy = (w - tw - margin, h - th - margin)
                    elif text_pos == "左下": xy = (margin, h - th - margin)
                    elif text_pos == "右上": xy = (w - tw - margin, margin)
                    else: xy = (margin, margin)

                    # 繪製黑色陰影，確保字體清晰
                    draw.text((xy[0]+3, xy[1]+3), display_text, fill="black", font=font)
                    draw.text(xy, display_text, fill=text_color, font=font)
                
                images.append(img.convert("RGB"))
            
            # 統一尺寸
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
                
        st.success("🎉 GIF 製作完成！")
        st.image(gif_bytes, caption="幻燈片預覽", use_container_width=True)
        st.download_button(label="📥 下載您的 GIF 檔案", data=gif_bytes, file_name="slideshow.gif", mime="image/gif")
else:
    st.info("💡 請先由上方按鈕上傳圖片。")
