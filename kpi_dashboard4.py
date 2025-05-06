import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from streamlit_extras.grid import grid

# Set page config
st.set_page_config(layout="wide")
st.title("📊 KPI Dashboard - Januari vs Februari")

# Upload file
uploaded_file = st.file_uploader("Upload file Excel", type=["xlsx"])
if uploaded_file:
    df = pd.read_excel(uploaded_file, sheet_name="Dulu")

    df = df[['Perspective', 'KPI', 'PIC', 'Target Jan', 'Actual Jan', 'Achv Jan', 'Target Feb', 'Actual Feb', 'Achv Feb']].copy()

    def get_status(achv, target):
        if pd.isna(achv) or pd.isna(target):
            return '⚫ Hitam'
        r = achv / target if target else 0
        if r > 1:
            return '🟢 Hijau'
        elif r >= 0.7:
            return '🟡 Kuning'
        return '🔴 Merah'

    df['Status'] = df.apply(lambda row: get_status(row['Achv Jan'], row['Target Jan']), axis=1)

    status_order = ['🔴 Merah', '🟡 Kuning', '🟢 Hijau', '⚫ Hitam']
    color_map = {
        '🔴 Merah': 'red',
        '🟡 Kuning': 'yellow',
        '🟢 Hijau': 'green',
        '⚫ Hitam': 'black'
    }

    overall = df['Status'].value_counts().reindex(status_order, fill_value=0)

    # Custom lampu lalu lintas
    st.subheader("📍 Total KPI per Traffic Light")
    fig_lampu = go.Figure()
    for status in status_order:
        fig_lampu.add_trace(go.Bar(
            y=[status],
            x=[overall[status]],
            name=status,
            orientation='h',
            marker_color=color_map[status],
            text=[overall[status]],
            textposition='outside'
        ))
    fig_lampu.update_layout(
        showlegend=False,
        xaxis=dict(showticklabels=False),
        height=300,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_lampu, use_container_width=True)

    # KPI per Perspective dan Status
    persp = (
        df.groupby(['Perspective','Status'])
        .size()
        .unstack(fill_value=0)
        .reindex(columns=status_order, fill_value=0)
    )
    st.subheader("📍 KPI per Perspective dan Status")
    st.dataframe(persp)

    # Filter perspective (slicer style)
    st.subheader("🔍 Filter KPI")
    perspective_options = df['Perspective'].unique()
    selected_persp = st.multiselect("Pilih Perspective:", perspective_options, default=perspective_options.tolist())

    filtered_df = df[df['Perspective'].isin(selected_persp)]

    selected_status = st.selectbox("Pilih warna status:", status_order)
    filtered_data = filtered_df[filtered_df['Status'] == selected_status]

    st.markdown(f"### 📋 Daftar KPI dengan Status {selected_status}")
    selected_kpi = st.radio("Klik KPI untuk melihat chart:", filtered_data['KPI'].tolist(), index=0, key="kpi_radio")

    kpi_data = filtered_data[filtered_data['KPI'] == selected_kpi]
    if not kpi_data.empty:
        target_jan = kpi_data['Target Jan'].values[0]
        target_feb = kpi_data['Target Feb'].values[0]
        actual_jan = kpi_data['Actual Jan'].values[0]
        actual_feb = kpi_data['Actual Feb'].values[0]
        achv_jan = kpi_data['Achv Jan'].values[0]
        achv_feb = kpi_data['Achv Feb'].values[0]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Januari', 'Februari'],
            y=[actual_jan, actual_feb],
            name='Actual',
            marker=dict(color='deepskyblue'),
        ))
        fig.add_trace(go.Bar(
            x=['Januari', 'Februari'],
            y=[target_jan, target_feb],
            name='Target',
            marker=dict(color='lightgrey'),
        ))
        fig.update_layout(
            title=f'📈 Actual vs Target: {selected_kpi}',
            xaxis_title='Bulan',
            yaxis_title='Nilai',
            barmode='group',
            template='plotly_white'
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown(f"**Achievement Januari:** {achv_jan * 100:.2f}%")
        st.markdown(f"**Achievement Februari:** {achv_feb * 100:.2f}%")
else:
    st.info("Silakan upload file Excel terlebih dahulu.")
