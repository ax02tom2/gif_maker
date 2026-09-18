import streamlit as st
from PIL import Image

st.title("📁 影像時序 GIF 動態圖製作工具")
st.write("請直接將多張依照日期命名的圖片拖曳或上傳至下方，即可自動排序並製作幻燈片 GIF！")

st.sidebar.header("⚙️ 設定選項")
duration_ms = st.sidebar.slider("每張圖片停留時間 (毫秒)", min_value=200, max_value=3000, value=1000, step=100)

uploaded_files = st.file_uploader("請選擇或拖曳 JPG/PNG 圖片檔案", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    uploaded_files = sorted(uploaded_files, key=lambda x: x.name)
    
    st.success(f"✅ 成功上傳 {len(uploaded_files)} 張圖片！已自動按日期排序：")
    
    for idx, f in enumerate(uploaded_files, 1):
        st.text(f"{idx}. {f.name}")

    if st.button("🚀 開始製作 GIF"):
        with st.spinner("正在合成 GIF 中，請稍候..."):
            images = [Image.open(f) for f in uploaded_files]
            
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
            
        st.success("🎉 GIF 製作完成！")
        
        st.image(output_path, caption="幻燈片預覽", use_column_width=True)
        
        with open(output_path, "rb") as file:
            st.download_button(
                label="📥 下載您的 GIF 檔案",
                data=file,
                file_name="terrain_slideshow.gif",
                mime="image/gif"
            )
else:
    st.info("💡 請先上方按鈕或拖曳上傳圖片以開始。")
