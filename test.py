import streamlit as st
import pandas as pd
import plotly.express as px
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# --- 1. Page Configuration ---
st.set_page_config(page_title="C/DA-HK Demolition Carbon Management", layout="wide")


# --- 2. Robust Data Loading ---
@st.cache_data
def load_data():
    file_path = "/Users/chenyufei/Desktop/2010周三上午/小组作业/第二版数据.xlsx"
    try:
        # A. Macro Statistics
        df_macro = pd.read_excel(file_path, sheet_name="宏观统计", skiprows=1).iloc[:, [1, 2, 3, 4, 5, 6, 7, 8, 9]]
        df_macro.columns = ['Metric', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
        df_macro = df_macro.dropna(subset=['Metric'])

        # Safe translation for Macro Index
        macro_map = {
            "固体废物总量(公吨/日)": "Total Municipal Waste (t/day)",
            "拆卸废料总量(公吨/日)": "Demolition Waste (t/day)"
        }
        df_macro['Metric'] = df_macro['Metric'].str.strip().replace(macro_map)
        df_macro = df_macro.set_index('Metric')

        # B. Material Recycling
        df_recycle = pd.read_excel(file_path, sheet_name="物质循环").iloc[:, [4, 5, 6, 7, 8, 9, 10, 11, 12]]
        df_recycle.columns = ['Category', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']
        df_recycle = df_recycle.dropna(subset=['Category'])

        recycle_map = {"含铁金属": "Ferrous Metal", "纸张": "Paper", "塑料": "Plastic"}
        df_recycle['Category'] = df_recycle['Category'].str.strip().replace(recycle_map)
        df_recycle = df_recycle.set_index('Category')

        # C. Module 3 Benchmarks (Translation)
        df_cases = pd.read_excel(file_path, sheet_name="案例&对标", skiprows=4).dropna(subset=['案例'])

        # Translation Dictionary (Matches your exact Excel content)
        trans = {
            "启德社区隔离设施": "Kai Tak Isolation Facility",
            "香港MiC试点住宅项目": "HK MiC Pilot Project",
            "香港钢MiC住宅楼": "HK Steel MiC Building",
            "同上—材料隐含排放占比": "Ref: Material Embodied Carbon %",
            "同上—EOL碳节省": "Ref: EOL Carbon Savings",
            "同上—净排放": "Ref: Net Emissions",
            "20.7% 隐含碳减排": "20.7% Embodied Reduction",
            "21.60% GHG减排": "21.60% GHG Reduction",
            "缩短工期、减少废物、优化材料使用": "Optimized Time & Waste",
            "建材隐含排放、建筑废物运输、设备资源消耗": "Material/Transport/Resources",
            "材料再利用+废物回收": "Material Reuse & Recycling",
            "回收效益超过排放": "Recycling Benefit > Emissions",
            "材料生产阶段主导": "Material Production Stage",
            "废物处理为主": "Waste Disposal Dominated"
        }
        # Force translate all columns
        for col in df_cases.columns:
            df_cases[col] = df_cases[col].astype(str).str.strip().replace(trans)

        return df_macro, df_recycle, df_cases
    except Exception as e:
        st.error(f"❌ Error: {e}")
        return None, None, None


df_macro, df_recycle, df_cases = load_data()

# --- 3. Navigation ---
st.sidebar.title("🏗️ C/DA-HK")
module = st.sidebar.radio("Navigation", ["Module 1", "Module 2", "Module 3"])

# --- Module 1 ---
if module == "Module 1":
    st.header("Module 1: C/D Assessment Engine")
    area = st.number_input("Enter Building GFA (sqm)", value=1000)
    st.info("Baseline: 1,567 kg/m² (HK Public Housing)")
    boq = pd.DataFrame({
        "Material": ["Concrete", "Steel", "Aluminum", "Timber"],
        "Weight (t)": [area * 1.8, area * 0.12, area * 0.015, area * 0.01]
    })
    st.table(boq)

# --- Module 2 ---
elif module == "Module 2":
    st.header("Module 2: Tracking & Verification")

    st.subheader("HK Construction Waste Trends (2017-2024)")
    if df_macro is not None:
        # Select ONLY the translated rows to avoid errors
        targets = ["Total Municipal Waste (t/day)", "Demolition Waste (t/day)"]
        plot_df = df_macro.loc[df_macro.index.isin(targets)].T

        # Dual-Axis to make trends VISIBLE
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Scatter(x=plot_df.index, y=plot_df[targets[0]], name=targets[0], mode='lines+markers'),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(x=plot_df.index, y=plot_df[targets[1]], name=targets[1], mode='lines+markers'),
            secondary_y=True,
        )
        fig.update_layout(title="Waste Generation Trend (Dual Y-Axis for Visibility)")
        fig.update_yaxes(title_text="Municipal Waste", secondary_y=False)
        fig.update_yaxes(title_text="Demolition Waste", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Key Material Recycling Performance")
    if df_recycle is not None:
        rec_items = ["Ferrous Metal", "Paper", "Plastic"]
        st.bar_chart(df_recycle.loc[df_recycle.index.isin(rec_items)].T)

# --- Module 3 ---
elif module == "Module 3":
    st.header("Module 3: Industry Benchmarks")
    if df_cases is not None:
        display_df = df_cases[['案例', '减排数据', '原因', '数据来源']].rename(columns={
            '案例': 'Case Project', '减排数据': 'Performance', '原因': 'Key Drivers', '数据来源': 'Source'
        })
        st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.success(
        "🏆 **Strategic Highlight**: Steel MiC systems achieve **Negative Net Emissions** via high recyclability.")