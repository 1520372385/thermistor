import streamlit as st
import pandas as pd
import numpy as np
import io
from math import log, sqrt

# 设置页面
st.set_page_config(
    page_title="热敏电阻参数计算工具",
    page_icon="📊",
    layout="wide"
)

# 标题
st.title("📊 热敏电阻参数计算工具")
st.markdown("基于热敏电阻特性公式进行温度转换计算")

# 侧边栏选择计算模式
st.sidebar.header("计算模式选择")
calculation_mode = st.sidebar.radio(
    "选择计算类型:",
    ["公式1: 温度转换计算", "公式2: 电阻到温度转换"]
)

# 公式1：温度转换计算
if calculation_mode == "公式1: 温度转换计算":
    st.header("公式1: 温度转换计算")
    
    # 显示公式
    st.latex(r"T(t) = \frac{2C}{-B + \sqrt{B^2 - 4C\left(A - a - \frac{c + b(t + 273.15)}{(t + 273.15)^2}\right)}} - 273.15")
    
    # 参数输入
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("旧参数")
        a_old = st.number_input("参数 a (旧)", value=-0.22467, format="%.6f")
        b_old = st.number_input("参数 b (旧)", value=2658.1185, format="%.6f")
        c_old = st.number_input("参数 c (旧)", value=-78140.2863, format="%.6f")
    
    with col2:
        st.subheader("新参数")
        A_new = st.number_input("参数 A (新)", value=0.0, format="%.6f")
        B_new = st.number_input("参数 B (新)", value=0.0, format="%.6f")
        C_new = st.number_input("参数 C (新)", value=0.0, format="%.6f")
    
    # 文件上传
    st.subheader("数据输入")
    uploaded_file = st.file_uploader("上传温度数据文件", type=['csv', 'xlsx'])
    
    if uploaded_file is not None:
        try:
            # 根据文件类型读取数据
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("不支持的文件格式")
                st.stop()
            st.write("原始数据预览:")
            st.dataframe(df.head())
            
            # 检查数据格式
            if len(df.columns) < 2:
                st.error("数据文件需要至少包含两列：时间和温度")
            else:
                time_col = df.columns[0]
                temp_col = df.columns[1]
                
                # 执行计算
                def calculate_new_temperature(t):
                    """根据公式1计算新温度"""
                    try:
                        t_kelvin = t + 273.15
                        denominator = -B_new + sqrt(B_new**2 - 4*C_new*(A_new - a_old - (c_old + b_old*t_kelvin)/(t_kelvin**2)))
                        if denominator == 0:
                            return np.nan
                        T_new_kelvin = 2 * C_new / denominator
                        T_new_celsius = T_new_kelvin - 273.15
                        return T_new_celsius
                    except (ValueError, ZeroDivisionError):
                        return np.nan
                
                # 应用计算
                df['新温度(°C)'] = df[temp_col].apply(calculate_new_temperature)
                
                # 显示结果
                st.subheader("计算结果")
                st.dataframe(df)
                
                # 统计信息
                st.subheader("统计信息")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("数据点数", len(df))
                with col2:
                    st.metric("有效计算点数", df['新温度(°C)'].notna().sum())
                with col3:
                    st.metric("平均新温度", f"{df['新温度(°C)'].mean():.2f}°C")
                
                # 导出数据
                st.subheader("数据导出")
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="下载转换后的CSV文件",
                    data=csv,
                    file_name="转换后的温度数据.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"处理文件时出错: {str(e)}")

# 公式2：电阻到温度转换
else:
    st.header("公式2: 电阻到温度转换")
    
    # 显示公式
    st.latex(r"t = \frac{2c}{-b + \sqrt{b^2 - 4c(a - \ln R)}} - 273.15")
    
    # 参数输入
    col1, col2, col3 = st.columns(3)
    
    with col1:
        a_param = st.number_input("参数 a", value=0.0, format="%.6f", key="a2")
    with col2:
        b_param = st.number_input("参数 b", value=0.0, format="%.6f", key="b2")
    with col3:
        c_param = st.number_input("参数 c", value=0.0, format="%.6f", key="c2")
    
    # 文件上传
    st.subheader("数据输入")
    uploaded_file = st.file_uploader("上传电阻数据文件", type=['csv', 'xlsx'], key="file2")
    
    if uploaded_file is not None:
        try:
            # 根据文件类型读取数据
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif uploaded_file.name.endswith('.xlsx'):
                df = pd.read_excel(uploaded_file)
            else:
                st.error("不支持的文件格式")
                st.stop()
            st.write("原始数据预览:")
            st.dataframe(df.head())
            
            # 检查数据格式
            if len(df.columns) < 2:
                st.error("数据文件需要至少包含两列：时间和电阻")
            else:
                time_col = df.columns[0]
                resistance_col = df.columns[1]
                
                # 执行计算
                def calculate_temperature_from_resistance(R):
                    """根据公式2计算温度"""
                    try:
                        if R <= 0:
                            return np.nan
                        denominator = -b_param + sqrt(b_param**2 - 4*c_param*(a_param - log(R)))
                        if denominator == 0:
                            return np.nan
                        t_kelvin = 2 * c_param / denominator
                        t_celsius = t_kelvin - 273.15
                        return t_celsius
                    except (ValueError, ZeroDivisionError):
                        return np.nan
                
                # 应用计算
                df['计算温度(°C)'] = df[resistance_col].apply(calculate_temperature_from_resistance)
                
                # 显示结果
                st.subheader("计算结果")
                st.dataframe(df)
                
                # 统计信息
                st.subheader("统计信息")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("数据点数", len(df))
                with col2:
                    st.metric("有效计算点数", df['计算温度(°C)'].notna().sum())
                with col3:
                    st.metric("平均温度", f"{df['计算温度(°C)'].mean():.2f}°C")
                
                # 导出数据
                st.subheader("数据导出")
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="下载温度计算结果CSV文件",
                    data=csv,
                    file_name="电阻转换温度数据.csv",
                    mime="text/csv"
                )
                
        except Exception as e:
            st.error(f"处理文件时出错: {str(e)}")

# 使用说明
with st.expander("📖 使用说明"):
    st.markdown("""
    ### 公式1使用说明
    - **输入**: 包含时间和温度数据的CSV或Excel文件(.xlsx)
    - **参数**: 需要输入旧参数(a,b,c)和新参数(A,B,C)
    - **输出**: 转换后的温度数据
    
    ### 公式2使用说明  
    - **输入**: 包含时间和电阻数据的CSV或Excel文件(.xlsx)
    - **参数**: 需要输入参数(a,b,c)
    - **输出**: 计算得到的温度数据
    
    ### 文件格式要求
    - 第一列: 时间数据
    - 第二列: 温度数据(公式1)或电阻数据(公式2)
    - 支持表头，程序会自动识别列名
    - 支持CSV和Excel(.xlsx)格式
    """)

# 示例数据生成
with st.expander("🔄 生成示例数据"):
    st.markdown("如果需要测试数据，可以使用以下按钮生成示例CSV文件")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("生成公式1示例数据"):
            # 生成温度示例数据
            time_data = np.arange(0, 100, 1)
            temp_data = 20 + 10 * np.sin(time_data * 0.1) + np.random.normal(0, 0.5, len(time_data))
            example_df1 = pd.DataFrame({
                '时间(s)': time_data,
                '温度(°C)': temp_data
            })
            csv1 = example_df1.to_csv(index=False)
            st.download_button(
                label="下载公式1示例CSV",
                data=csv1,
                file_name="示例温度数据.csv",
                mime="text/csv"
            )
    
    with col2:
        if st.button("生成公式2示例数据"):
            # 生成电阻示例数据
            time_data = np.arange(0, 100, 1)
            resistance_data = 10000 * np.exp(-0.01 * time_data) + np.random.normal(0, 100, len(time_data))
            example_df2 = pd.DataFrame({
                '时间(s)': time_data,
                '电阻(Ω)': resistance_data
            })
            csv2 = example_df2.to_csv(index=False)
            st.download_button(
                label="下载公式2示例CSV",
                data=csv2,
                file_name="示例电阻数据.csv",
                mime="text/csv"
            )
