import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import os
import urllib.request

st.title("📁 影像時序 GIF 動態圖製作工具")
st.write("請直接上傳依照日期命名的圖片，先即時預覽浮水印效果，再一鍵產出 GIF。")

# --- 側邊欄設定 ---
st.sidebar.header("⚙️ 播放設定")
duration_ms = st.sidebar.slider("每張圖片停留時間 (毫秒)", 200, 3000, 1000, 100)

st.sidebar.markdown("---")
st.sidebar.header("📝 日期浮水印設定")
add_watermark = st.sidebar.checkbox("自動加入日期浮水印", value=True)

if add_watermark:
    text_color = st.sidebar.color_picker("文字顏色", "#FF0000")
    font_size = st.sidebar.slider("文字大小", 20, 500, 150, step=10)
    text_pos = st.sidebar.selectbox("文字位置", ["右下", "左下", "右上", "左上"])
    margin_pct = st.sidebar.slider("邊距往內縮 (百分比 %)", 1, 40, 12, step=1)
else:
    text_color, font_size, text_pos, margin_pct = "#FF0000", 150, "右下", 12

# --- 自動下載清晰字型 ---
font_path = "Roboto-Bold.ttf"
if not os.path.exists(font_path):
    try:
        url = "https://github.com/googlefonts/roboto/raw/main/src/hinted/Roboto-Bold.ttf"
        urllib.request.urlretrieve(url, font_path)
    except:
        pass

# --- 浮水印繪製工具 (獨立出來以供預覽與生成共用) ---
def apply_watermark(img, file_name_str, f_size, t_color, t_pos, m_pct):
    draw = ImageDraw.Draw(img)
    file_name = os.path.splitext(file_name_str)[0]
    
    if len(file_name) == 7 and file_name.isdigit():
        display_text = f"{file_name[:3]} / {file_name[3:5]} / {file_name[5:]}"
    else:
        display_text = file_name
    
    try:
        font = ImageFont.truetype(font_path, f_size)
    except:
        font = ImageFont.load_default()

    w, h = img.size
    try:
        left, top, right, bottom = font.getbbox(display_text)
        tw, th = right - left, bottom - top
    except:
        tw, th = f_size * len(display_text) * 0.6, f_size

    margin_x = int(w * (m_pct / 100.0))
    margin_y = int(h * (m_pct / 100.0))
    
    if t_pos == "右下": xy = (w - tw - margin_x, h - th - margin_y)
    elif t_pos == "左下": xy = (margin_x, h - th - margin_y)
    elif t_pos == "右上": xy = (w - tw - margin_x, margin_y)
    else: xy = (margin_x, margin_y)

    shadow_offset = max(2, int(f_size * 0.08))
    draw.text((xy[0]+shadow_offset, xy[1]+shadow_offset), display_text, fill="black", font=font)
    draw.text(xy, display_text, fill=t_color, font=font)
    
    return img

# --- 主程式區塊 ---
uploaded_files = st.file_uploader("請選擇或拖曳圖片檔案", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    # 確保依檔名排序
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    
    # 1. 即時預覽區塊
    st.markdown("### 👁️ 浮水印即時預覽 (第一張圖片)")
    preview_file = uploaded_files[0]
    preview_file.seek(0) # 確保讀取指標在最前面
    preview_img = Image.open(preview_file).convert("RGBA")
    
    if add_watermark:
        preview_img = apply_watermark(preview_img, preview_file.name, font_size, text_color, text_pos, margin_pct)
    
    st.image(preview_img.convert("RGB"), caption="💡 調整左側拉桿，此預覽圖會即時更新！確認無誤後再按下方按鈕。", use_container_width=True)
    
    st.markdown("---")
    
    # 2. 產出 GIF 區塊
    if st.button("🚀 確認預覽無誤，開始製作 GIF"):
        with st.spinner("正在合成全部圖片中，請稍候..."):
            images = []
            for f in uploaded_files:
                f.seek(0) # 確保每張圖都能正確讀取
                img = Image.open(f).convert("RGBA")
                if add_watermark:
                    img = apply_watermark(img, f.name, font_size, text_color, text_pos, margin_pct)
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
                
        st.success("🎉 GIF 製作完成！")
        st.download_button(label="📥 下載您的 GIF 檔案", data=gif_bytes, file_name="slideshow.gif", mime="image/gif")
else:
    st.info("💡 請先由上方按鈕上傳圖片。")
