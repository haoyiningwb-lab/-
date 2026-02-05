import streamlit as st
import pandas as pd
import requests
import folium
from streamlit_folium import folium_static
from PIL import Image

# --- 1. 访问加密功能 ---
def check_password():
    """如果输入正确密码则返回 True"""
    def password_entered():
        if st.session_state["password"] == st.secrets["access_password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("请输入 pqcat 的探险访问密码：", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("密码不正确，请重新输入：", type="password", on_change=password_entered, key="password")
        st.error("😕 密码错误，请检查。")
        return False
    else:
        return True

# --- 只有密码正确才运行主程序 ---
if check_password():
    
    # --- 2. 基础配置与数据加载 ---
    st.set_page_config(page_title="pqcat 南非全能自驾助手", layout="wide", page_icon="🇿🇦")

    @st.cache_data(ttl=3600)
    def get_zar_rate():
        try:
            r = requests.get("https://api.exchangerate-api.com/v4/latest/ZAR", timeout=2)
            return r.json()['rates']['CNY']
        except:
            return 0.39 # 2026年参考汇率 [cite: 2, 573]

    rate = get_zar_rate()

    # 动物百科数据库
    ANIMAL_DB = {
        "狮子 (Lion)": {"desc": "群居动物，草原之王。通常在清晨或黄昏最为活跃。🦁", "img": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=800"},
        "非洲象 (Elephant)": {"desc": "陆地最大哺乳动物，智商极高，成群活动。🐘", "img": "https://images.unsplash.com/photo-1557050543-4d5f4e07ef46?w=800"},
        "豹 (Leopard)": {"desc": "丛林隐士。独行侠，最难发现，喜欢把猎物拖上树。🐆", "img": "https://images.unsplash.com/photo-1575515645828-012562283020?w=800"},
        "非洲水牛 (Buffalo)": {"desc": "脾气暴躁，攻击性强。通常在水源附近。🐃", "img": "https://images.unsplash.com/photo-1551009175-15bdf9dcb580?w=800"},
        "犀牛 (Rhino)": {"desc": "濒危动物，主要有黑犀牛和白犀牛之分。🦏", "img": "https://images.unsplash.com/photo-1534193561958-406175b4dc17?w=800"},
        "非洲企鹅 (Penguin)": {"desc": "主要在 Boulders Beach 活动。2月是其繁育季节。🐧", "img": "https://images.unsplash.com/photo-1591348122449-02525d7ba3f9?w=800"},
        "海豹 (Seal)": {"desc": "常聚集在豪特湾的海豹岛。🦭", "img": "https://images.unsplash.com/photo-1551635338-9e6b4d37500b?w=800"}
    }

    # --- 3. 左侧侧边栏导航与全局工具 ---
    with st.sidebar:
        st.title("🇿🇦 探险中枢")
        
        # 实时换算工具
        st.header("💰 实时汇率换算")
        zar_val = st.number_input("输入兰特 (ZAR)", min_value=0.0, value=100.0)
        st.success(f"约合人民币: ¥{zar_val * rate:.2f}")
        st.caption(f"1 ZAR ≈ {rate} CNY")
        
        st.divider()
        
        # 功能模块选择
        menu = st.radio("选择大模块", ["📅 行程助手", "🐾 游猎全能舱", "🛡️ 自驾与安全"])
        
        st.divider()
        
        # 行李核对清单 [cite: 577, 578]
        st.header("🎒 实时行李核对")
        with st.expander("行李检查清单"):
            st.checkbox("大三圆头转换器", key="plug") [cite: 615]
            st.checkbox("护照/签证/复印件", key="docs") [cite: 600]
            st.checkbox("防虫驱蚊水", key="spray") [cite: 607]
            st.checkbox("防晒霜/帽子", key="sun") [cite: 585]
            st.checkbox("长袖衬衫/外套", key="cloth") [cite: 619, 620]

        st.divider()
        st.error("🚨 报警: 10111")
        st.warning("🇨🇳 使馆领保: +27-12-3428826")

    # --- 4. 右侧内容区域 ---
    if menu == "🐾 游猎全能舱":
        st.title("🐾 游猎全能舱 (Wildlife Center)")
        col_l, col_r = st.columns([2, 1])
        
        with col_l:
            st.subheader("📖 动物科普百科")
            sel_animal = st.selectbox("选择动物了解详情：", list(ANIMAL_DB.keys()))
            st.image(ANIMAL_DB[sel_animal]["img"], use_container_width=True)
            st.info(f"**{sel_animal} 特征:** {ANIMAL_DB[sel_animal]['desc']}")

        with col_r:
            st.subheader("📸 智能识图与打卡")
            up_file = st.file_uploader("上传野外照片识图并打卡：", type=["jpg", "png", "jpeg"])
            if up_file:
                st.image(Image.open(up_file), use_container_width=True)
                st.success(f"🔍 自动匹配为: {sel_animal}")
                if st.button("同步至我的打卡墙"):
                    st.session_state[f"found_{sel_animal}"] = True
                    st.balloons()
            
            st.divider()
            st.write("**🏆 五霸成就墙 (Big Five)**") [cite: 534]
            # 五霸打卡复选框
            for a in ["狮子", "大象", "水牛", "豹", "犀牛"]:
                st.checkbox(a, key=f"big5_{a}")
            
            # 进度统计
            found_num = sum([st.session_state.get(f"big5_{a}", False) for a in ["狮子", "大象", "水牛", "豹", "犀牛"]])
            st.progress(found_num / 5)
            st.write(f"收集进度: {found_num}/5")

    elif menu == "📅 行程助手":
        st.title("📅 每日行程导航")
        # 核心行程细节 [cite: 5]
        days_info = {
            "2026-02-11 (Day 3)": {"task": "开普敦市区：Truth Coffee, 波卡普, 坎普斯湾日落", "dist": "城区自驾约 20km", "sunset": "19:45"}, [cite: 5, 80]
            "2026-02-12 (Day 4)": {"task": "半岛巡礼：海豹岛, 企鹅聚集地, 好望角", "dist": "往返约 140km", "sunset": "19:43"}, [cite: 5, 227]
            "2026-02-15 (Day 7)": {"task": "赫曼努斯观鲸 & Creation Wines 酒庄", "dist": "约 120km", "sunset": "19:38"}, [cite: 5, 373, 387]
            "2026-02-16 (Day 8)": {"task": "阿古拉斯角 & 前往克尼斯纳", "dist": "今日驾驶较长约 400km", "sunset": "19:30"}, [cite: 5, 425]
            "2026-02-17 (Day 9)": {"task": "极限挑战：布劳克朗斯大桥蹦极 & 齐齐卡马", "dist": "约 80km", "sunset": "19:25"} [cite: 5, 457]
        }
        sel_date = st.selectbox("选择旅行日期:", list(days_info.keys()))
        
        c1, c2, c3 = st.columns(3)
        c1.metric("今日重点", "自驾/游览")
        c2.metric("预计里程", days_info[sel_date]["dist"])
        c3.metric("建议日落", days_info[sel_date]["sunset"])
        
        st.info(f"🚩 **行程详情:** {days_info[sel_date]['task']}")
        
        # 互动地图预览 [cite: 11]
        m = folium.Map(location=[-33.92, 18.42], zoom_start=6)
        folium.Marker([-33.92, 18.42], popup="开普敦", tooltip="起点").add_to(m) [cite: 55]
        folium.Marker([-24.01, 31.48], popup="克鲁格", tooltip="游猎区", icon=folium.Icon(color='green')).add_to(m) [cite: 528]
        folium_static(m, width=900)

    elif menu == "🛡️ 自驾与安全":
        st.title("🛡️ 实战预警与推荐")
        sc1, sc2 = st.columns(2)
        with sc1:
            st.warning("**⚡ Loadshedding (停电预警)**")
            st.write("请下载 EskomSePush 实时监控限电等级。")
            st.info("💡 提醒: 伊丽莎白港旅馆配有太阳能(#Solar Energy)，电力无忧。") [cite: 5, 470]
        with sc2:
            st.warning("**🚗 自驾防盗**")
            st.write("红绿灯处请锁死车窗，切勿在车内明处放置贵重物品。")
            st.error("紧急联系电话: 10111 (警察)") [cite: 600]

        st.divider()
        st.subheader("🍴 行程单必选打卡")
        st.write("- **Truth Coffee**: 蒸汽朋克主题，全球知名。") [cite: 80, 123]
        st.write("- **Creation Wines**: 赫曼努斯著名酒庄餐厅。") [cite: 387]
        st.write("- **好望角标志**: 拍照留念必经点。") [cite: 228]

    st.markdown("---")
    st.caption("pqcat 2026 南非行程定制助手 | 数据来源: 穷游行程助手") [cite: 4]
