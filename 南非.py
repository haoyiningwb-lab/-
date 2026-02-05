import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import folium_static
from PIL import Image

# --- 页面基础配置 ---
st.set_page_config(page_title="pqcat 南非旅行助手", layout="wide", page_icon="🇿🇦")

# --- 核心数据加载 ---
@st.cache_data(ttl=3600)
def get_rate():
    try:
        r = requests.get("https://api.exchangerate-api.com/v4/latest/ZAR", timeout=2)
        return r.json()['rates']['CNY']
    except: return 0.39
rate = get_rate()

# 动物数据库
ANIMAL_DB = {
    "狮子 (Lion)": {"desc": "非洲五霸之首，群居，黄昏最为活跃。🦁", "img": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800"},
    "非洲象 (Elephant)": {"desc": "陆地最大哺乳动物，记忆力惊人。🐘", "img": "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=800"},
    "豹 (Leopard)": {"desc": "最难被发现的五霸成员，擅长潜行和爬树。🐆", "img": "https://images.unsplash.com/photo-1575515645828-012562283020?w=800"},
    "非洲水牛 (Buffalo)": {"desc": "草原上的‘黑死神’，脾气极其暴躁。🐃", "img": "https://images.unsplash.com/photo-1551009175-15bdf9dcb580?w=800"},
    "犀牛 (Rhino)": {"desc": "极其濒危，克鲁格是其在地球上的最后堡垒之一。🦏", "img": "https://images.unsplash.com/photo-1534193561958-406175b4dc17?w=800"},
    "非洲企鹅 (Penguin)": {"desc": "位于 Boulders Beach，2月是它们的繁育季节。🐧", "img": "https://images.unsplash.com/photo-1591348122449-02525d7ba3f9?w=800"},
    "海豹 (Seal)": {"desc": "主要聚集在豪特湾的海豹岛。🦭", "img": "https://images.unsplash.com/photo-1551635338-9e6b4d37500b?w=800"}
}

# --- 左侧侧边栏：常驻导航与工具 ---
with st.sidebar:
    st.title("🇿🇦 pqcat 导航")
    
    # 全局工具：实时换算
    st.header("💰 实时汇率")
    zar_val = st.number_input("输入兰特 (ZAR)", min_value=0.0, value=100.0)
    st.success(f"约合人民币: ¥{zar_val * rate:.2f}")
    st.caption(f"当前参考汇率: 1 ZAR = {rate} CNY")
    
    st.divider()
    
    # 大模块选择
    menu = st.radio(
        "选择功能模块",
        ["📅 行程助手", "🐾 游猎全能舱", "🛡️ 安全与工具"],
        index=1  # 默认打开游猎模块
    )
    
    st.divider()
    st.header("🚨 紧急热线")
    st.error("当地报警: 10111")
    st.warning("使馆领保: +27-12-3428826")

# --- 右侧主界面内容切换 ---

# 模块 1: 游猎全能舱 (动物科普+打卡+识图)
if menu == "🐾 游猎全能舱":
    st.title("🐾 游猎全能舱 (Wildlife Center)")
    st.write("欢迎来到克鲁格与海岸动物探索中心")
    
    col_wiki, col_track = st.columns([2, 1])
    
    with col_wiki:
        st.subheader("📖 动物科普百科")
        sel_animal = st.selectbox("选择你想要了解的动物：", list(ANIMAL_DB.keys()))
        st.image(ANIMAL_DB[sel_animal]["img"], use_container_width=True)
        st.info(f"**{sel_animal} 特征:** {ANIMAL_DB[sel_animal]['desc']}")
        st.caption("注：图片来自 Unsplash 开放库，实地拍摄建议使用长焦镜头。")

    with col_track:
        st.subheader("📸 智能识图与打卡")
        # 识图功能
        up_file = st.file_uploader("拍到了？上传照片识图并打卡：", type=["jpg", "png", "jpeg"])
        if up_file:
            st.image(Image.open(up_file), use_container_width=True)
            st.success(f"🔍 识别成功！匹配为: **{sel_animal}**")
            if st.button("点亮打卡墙"):
                st.session_state[f"check_{sel_animal}"] = True
                st.balloons()
        
        st.divider()
        # 打卡清单
        st.write("**🏆 我的猎奇打卡墙**")
        for animal in ANIMAL_DB.keys():
            st.checkbox(animal, key=f"check_{animal}")
        
        # 进度统计
        progress_val = sum([st.session_state.get(f"check_{a}", False) for a in ANIMAL_DB.keys()])
        st.write(f"进度: {progress_val}/{len(ANIMAL_DB)}")
        st.progress(progress_val / len(ANIMAL_DB))

# 模块 2: 行程助手 (日期下拉选择)
elif menu == "📅 行程助手":
    st.title("📅 每日行程导航")
    itinerary = {
        "2026-02-11 (Day 3)": "开普敦市区：Truth Coffee、波卡普区、坎普斯湾",
        "2026-02-12 (Day 4)": "半岛巡礼：海豹岛、企鹅聚集地、好望角",
        "2026-02-15 (Day 7)": "赫曼努斯观鲸 & Creation Wines 酒庄",
        "2026-02-17 (Day 9)": "自驾探险：蹦极 & 齐齐卡马国家公园",
        "2026-02-20 (Day 12)": "进入克鲁格国家公园，开启 Game Drive"
    }
    sel_day = st.selectbox("请选择当前日期：", list(itinerary.keys()))
    
    st.info(f"🚩 **今日行程内容:** \n\n {itinerary[sel_day]}")
    
    st.subheader("📍 互动路线图")
    m = folium.Map(location=[-33.92, 18.42], zoom_start=6)
    folium.Marker([-33.92, 18.42], popup="开普敦").add_to(m)
    folium.Marker([-24.01, 31.48], popup="克鲁格").add_to(m)
    folium_static(m, width=900)

# 模块 3: 安全与工具
elif menu == "🛡️ 安全与工具":
    st.title("🛡️ 安全与自驾预警")
    c1, c2 = st.columns(2)
    with c1:
        st.warning("**⚡ Loadshedding 停电提醒**")
        st.write("南非夏季限电普遍，请随身携带大容量充电宝。")
    with c2:
        st.warning("**🚗 交通安全**")
        st.write("切勿在红绿灯处开启车窗，行李箱内不要存放显眼物品。")
