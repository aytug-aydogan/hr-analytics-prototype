"""
İK Analitiği — HR Analytics Prototype
Content-area prototype (embedded inside Dakika app).
Filters: period type, period, department.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="İK Analitiği",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #f0f2f5; }
#MainMenu, footer, header { visibility: hidden; }

/* Collapse sidebar toggle button */
[data-testid="collapsedControl"] { display: none; }

/* Main content */
[data-testid="stMain"] .block-container {
    padding: 28px 32px 32px 32px;
    max-width: 100%;
}

/* ── KPI card ── */
.kpi-card {
    background: white;
    border-radius: 10px;
    padding: 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    border: 1px solid #e2e6ea;
    min-height: 110px;
}
.kpi-label {
    font-size: 12.5px;
    color: #374151;
    font-weight: 500;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 6px;
}
.kpi-value {
    font-size: 32px;
    font-weight: 700;
    color: #111827;
    line-height: 1.1;
    margin-bottom: 4px;
}
.kpi-sub {
    font-size: 11.5px;
    color: #6b7280;
    margin-top: 4px;
}

/* ── Chart card — style Streamlit's own container wrapper ── */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 10px !important;
    padding: 16px 18px 8px 18px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
    border: 1px solid #e2e6ea !important;
    margin-bottom: 16px;
}
.chart-title {
    font-size: 14px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 12px;
}

/* ── Page header ── */
.page-title {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
    line-height: 1.2;
}
.page-sub {
    font-size: 12.5px;
    color: #6b7280;
    margin-top: 2px;
    margin-bottom: 0;
}

/* ── Filter label ── */
.filter-label {
    font-size: 11px;
    font-weight: 600;
    color: #374151;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    gap: 2px;
    background: white;
    border-radius: 8px;
    padding: 4px;
    border: 1px solid #e2e6ea;
    margin-bottom: 20px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 6px;
    padding: 7px 16px;
    font-weight: 500;
    font-size: 13px;
    color: #374151;
}
.stTabs [aria-selected="true"] {
    background-color: #2563eb !important;
    color: white !important;
}

/* selectbox label */
div[data-testid="stSelectbox"] label { display: none; }
</style>
""", unsafe_allow_html=True)


# ── Constants ─────────────────────────────────────────────────────────────────
DEPARTMENTS = [
    "Tüm Departmanlar",
    "Yazılım & Teknoloji",
    "Satış & Pazarlama",
    "Muhasebe & Finans",
    "İnsan Kaynakları",
    "Operasyon",
    "Hukuk",
    "Yönetim",
]

COMPANIES = [
    "Tüm Şirketler",
    "Şirket A",
    "Şirket B",
    "Şirket C",
]

MONTHS_TR = [
    "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran",
    "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık",
]

BLUE = "#1d6fce"
# High-contrast qualitative palette (ColorBrewer Set1 + adjustments)
COLORS = [
    "#1d6fce",  # blue
    "#e05c00",  # orange
    "#2ca02c",  # green
    "#d62728",  # red
    "#9467bd",  # purple
    "#8c564b",  # brown
    "#e377c2",  # pink
    "#17becf",  # teal
]

# ── Mock Data ─────────────────────────────────────────────────────────────────
MOCK = {
    # Demografi
    "headcount": 248,
    "avg_age": 34.2,
    "avg_tenure": 3.7,
    "retired_count": 12,
    "gender": {"Erkek": 142, "Kadın": 106},
    "collar": {"Beyaz Yaka": 163, "Mavi Yaka": 85},
    "headcount_by_dept": {
        "Yazılım & Teknoloji": 68, "Satış & Pazarlama": 52,
        "Operasyon": 44, "Muhasebe & Finans": 38,
        "İnsan Kaynakları": 22, "Hukuk": 14, "Yönetim": 10,
    },
    "headcount_by_position": {
        "Yazılım Geliştirici": 58, "Satış Temsilcisi": 42,
        "Muhasebe Uzmanı": 31, "İK Uzmanı": 24,
        "Operasyon Uzmanı": 38, "Yönetici": 19, "Diğer": 36,
    },
    "age_groups": {
        "18-25": 28, "26-35": 94, "36-45": 76, "46-55": 38, "55+": 12,
    },
    "tenure_groups": {
        "0-1 Yıl": 41, "1-3 Yıl": 72, "3-5 Yıl": 63, "5-10 Yıl": 48, "10+ Yıl": 24,
    },
    "headcount_trend": [231, 235, 238, 241, 244, 246, 248, 247, 245, 246, 247, 248],

    # Ücret
    "salary_avg": 42_800,
    "salary_min": 18_500,
    "salary_max": 145_000,
    "salary_hourly_avg": 267.5,
    "salary_hourly_min": 115.6,
    "salary_hourly_max": 906.3,
    "salary_by_dept": {
        "Yazılım & Teknoloji": 58_400, "Satış & Pazarlama": 41_200,
        "Operasyon": 31_800, "Muhasebe & Finans": 43_500,
        "İnsan Kaynakları": 38_200, "Hukuk": 52_100, "Yönetim": 98_500,
    },
    "salary_by_position": {
        "Yazılım Geliştirici": 62_400, "Satış Temsilcisi": 38_200,
        "Muhasebe Uzmanı": 41_500, "İK Uzmanı": 39_800,
        "Operasyon Uzmanı": 31_200, "Yönetici": 98_500,
    },
    "salary_by_tenure": {
        "0-1 Yıl": 26_400, "1-3 Yıl": 35_800, "3-5 Yıl": 44_200,
        "5-10 Yıl": 55_600, "10+ Yıl": 72_300,
    },

    # Maliyet
    "cost_labor_total": 10_614_400,
    "cost_sgk_total": 2_335_168,
    "cost_overtime_total": 318_450,

    # Fazla Mesai
    "overtime_total": 1_842,
    "overtime_avg": 7.4,
    "overtime_by_position": {
        "Yazılım Geliştirici": 9.2, "Satış Temsilcisi": 11.4,
        "Muhasebe Uzmanı": 6.1, "İnsan Kaynakları": 4.3,
        "Operasyon": 8.7, "Yönetici": 5.2,
    },
    "overtime_by_type": {"Hafta İçi": 1_124, "Hafta Sonu": 512, "Resmi Tatil": 206},

    # Devamsızlık
    "total_absent_days": 412,
    "avg_absent_days": 1.66,
    "total_annual_leave_balance": 3_840,
    "avg_annual_leave_balance": 15.5,
    "total_used_annual_leave": 1_124,
    "avg_used_annual_leave": 4.5,
    "absence_types": {
        "Yıllık İzin": 312, "Hastalık İzni": 64, "Mazeret İzni": 18,
        "Ücretsiz İzin": 8, "Babalık İzni": 5, "Diğer": 5,
    },
    "absence_by_tenure": {
        "0-1 Yıl": 2.4, "1-3 Yıl": 1.9, "3-5 Yıl": 1.5,
        "5-10 Yıl": 1.3, "10+ Yıl": 1.1,
    },
    "absence_by_age": {
        "18-25": 1.4, "26-35": 1.7, "36-45": 1.9, "46-55": 2.1, "55+": 1.8,
    },

    # İşe Alım & Çıkış
    "hires": 18,
    "terminations": 11,
    "turnover_rate_monthly": 4.4,
    "turnover_rate_yearly": 52.8,
    "termination_reasons": {
        "İstifa": 6, "Sözleşme Sonu": 2, "Emeklilik": 1, "İşten Çıkarma": 2,
    },
    "termination_by_collar": {"Beyaz Yaka": 7, "Mavi Yaka": 4},
    "termination_by_tenure": {
        "0-1 Yıl": 5, "1-3 Yıl": 3, "3-5 Yıl": 2, "5-10 Yıl": 1, "10+ Yıl": 0,
    },
    "hires_trend":        [8, 12, 15, 22, 18, 14, 20, 17, 11, 16, 19, 18],
    "terminations_trend": [5,  7,  9, 14, 11,  8, 13, 10,  6,  9, 12, 11],
}

TREND_PERIODS = [f"{m} 2025" for m in MONTHS_TR]


# ── Helpers ───────────────────────────────────────────────────────────────────
def fmt_num(v, d=0):
    return f"{v:,.{d}f}".replace(",", ".")

def fmt_currency(v):
    return f"₺{v:,.0f}"

def kpi(label, value, sub="", icon=""):
    icon_html = f'<span style="font-size:15px">{icon}</span> ' if icon else ""
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-label">{icon_html}{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
    </div>""", unsafe_allow_html=True)

HOVER_BG    = "rgba(255,255,255,0.97)"
HOVER_FONT  = dict(family="Inter", size=13, color="#111827")
HOVER_BORDER = "rgba(0,0,0,0)"

def _base_layout(height=260, extra_margin_b=0):
    return dict(
        plot_bgcolor="white", paper_bgcolor="white",
        margin=dict(l=0, r=0, t=4, b=extra_margin_b),
        font=dict(family="Inter", size=12, color="#111827"),
        hoverlabel=dict(
            bgcolor=HOVER_BG,
            font=HOVER_FONT,
            bordercolor="#e2e6ea",
            namelength=-1,
        ),
        height=height,
    )

def bar_chart(data, title, color=BLUE, horizontal=False, x_label="", y_label=""):
    cats = list(data.keys())
    vals = list(data.values())
    col_x = x_label or "Kategori"
    col_y = y_label or "Değer"
    df = pd.DataFrame({col_x: cats, col_y: vals})

    if horizontal:
        hover_tpl = f"<b>%{{y}}</b><br>{col_x}: %{{x:,.0f}}<extra></extra>"
        fig = px.bar(df, x=col_y, y=col_x, orientation="h",
                     color_discrete_sequence=[color],
                     hover_data={col_x: False, col_y: False})
        fig.update_traces(
            hovertemplate=f"<b>%{{y}}</b><br>%{{x:,.1f}}<extra></extra>",
            marker_line_width=0,
        )
        fig.update_layout(yaxis={"categoryorder": "total ascending"})
    else:
        fig = px.bar(df, x=col_x, y=col_y, color_discrete_sequence=[color],
                     hover_data={col_x: False, col_y: False})
        fig.update_traces(
            hovertemplate=f"<b>%{{x}}</b><br>%{{y:,.1f}}<extra></extra>",
            marker_line_width=0,
        )

    fig.update_layout(**_base_layout(), showlegend=False, xaxis_title="", yaxis_title="")
    fig.update_xaxes(showgrid=False, tickfont=dict(color="#111827"), title_font=dict(color="#111827"))
    fig.update_yaxes(gridcolor="#f3f4f6", tickfont=dict(color="#111827"), title_font=dict(color="#111827"))
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def pie_chart(data, title):
    cats = list(data.keys())
    vals = list(data.values())
    df = pd.DataFrame({"Grup": cats, "Adet": vals})
    fig = px.pie(df, names="Grup", values="Adet",
                 color_discrete_sequence=COLORS, hole=0.5)
    fig.update_layout(
        **_base_layout(),
        legend=dict(orientation="v", x=1, y=0.5, font=dict(color="#111827", size=12)),
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent",
        textfont=dict(color="white", size=12),
        hovertemplate="<b>%{label}</b><br>%{value:,.0f} (%{percent})<extra></extra>",
    )
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

def trend_line(periods, series, title):
    fig = go.Figure()
    line_colors = [BLUE, "#dc2626"]
    for i, (name, values) in enumerate(series.items()):
        fig.add_trace(go.Scatter(
            x=periods, y=values, mode="lines+markers", name=name,
            line=dict(color=line_colors[i % 2], width=2),
            marker=dict(size=5),
            hovertemplate=f"<b>%{{x}}</b><br>{name}: %{{y}}<extra></extra>",
        ))
    fig.update_layout(
        **_base_layout(height=270, extra_margin_b=60),
        legend=dict(orientation="h", y=-0.32, xanchor="center", x=0.5,
                    font=dict(color="#111827", size=13)),
    )
    fig.update_xaxes(showgrid=False, tickfont=dict(color="#111827"), title_font=dict(color="#111827"))
    fig.update_yaxes(gridcolor="#f3f4f6", tickfont=dict(color="#111827"), title_font=dict(color="#111827"))
    st.markdown(f'<div class="chart-title">{title}</div>', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})



# ── Header row: title + filters ───────────────────────────────────────────────
title_col, f0, f1, f2, f3 = st.columns([3, 1.4, 1.2, 1.2, 1.4])

with title_col:
    st.markdown('<div class="page-title">İK Analitik Panosu</div>', unsafe_allow_html=True)

with f0:
    st.markdown('<div class="filter-label">Şirket</div>', unsafe_allow_html=True)
    selected_company = st.selectbox("co", COMPANIES, label_visibility="collapsed")

with f1:
    st.markdown('<div class="filter-label">Dönem Türü</div>', unsafe_allow_html=True)
    period_type = st.selectbox("pt", ["Aylık", "Çeyreklik", "Yıllık"], label_visibility="collapsed")

with f2:
    st.markdown('<div class="filter-label">Dönem</div>', unsafe_allow_html=True)
    if period_type == "Aylık":
        period_opts = [f"{m} 2025" for m in MONTHS_TR] + ["Ocak 2026"]
        period_default = len(period_opts) - 1
    elif period_type == "Çeyreklik":
        period_opts = ["Q1 2025", "Q2 2025", "Q3 2025", "Q4 2025", "Q1 2026"]
        period_default = len(period_opts) - 1
    else:
        period_opts = ["2024", "2025", "2026"]
        period_default = 1
    selected_period = st.selectbox("dp", period_opts, index=period_default, label_visibility="collapsed")

with f3:
    st.markdown('<div class="filter-label">Departman</div>', unsafe_allow_html=True)
    selected_dept = st.selectbox("dept", DEPARTMENTS, label_visibility="collapsed")

# Sub-header
company_label = selected_company if selected_company != "Tüm Şirketler" else "Tüm Şirketler"
dept_label = selected_dept if selected_dept != "Tüm Departmanlar" else "Tüm Departmanlar"
st.markdown(
    f'<div class="page-sub" style="margin-bottom:20px">'
    f'{company_label} · {period_type} · {selected_period} · {dept_label}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "👥 Demografi",
    "💰 Ücret",
    "🏭 Maliyet",
    "🕐 Fazla Mesai",
    "🏖️ Devamsızlık",
    "🔄 İşe Alım & Çıkış",
])


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Demografi
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi("Toplam Çalışan", fmt_num(MOCK["headcount"]), icon="👥")
    with c2: kpi("Ortalama Yaş", fmt_num(MOCK["avg_age"], 1), icon="🎂")
    with c3: kpi("Ortalama Kıdem", f"{fmt_num(MOCK['avg_tenure'], 1)} yıl", icon="📅")
    with c4: kpi("Emekli Çalışan", fmt_num(MOCK["retired_count"]), icon="🏅")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True): pie_chart(MOCK["collar"], "Beyaz / Mavi Yaka Dağılımı")
    with col_b:
        with st.container(border=True): pie_chart(MOCK["gender"], "Cinsiyete Göre Çalışan Sayısı")

    col_c, col_d = st.columns(2)
    with col_c:
        with st.container(border=True): bar_chart(MOCK["age_groups"], "Yaş Skalasına Göre Çalışan Sayısı", color=BLUE)
    with col_d:
        with st.container(border=True): bar_chart(MOCK["tenure_groups"], "Kıdem Yılı Skalasına Göre Çalışan Sayısı", color="#7c3aed")

    col_e, col_f = st.columns(2)
    with col_e:
        with st.container(border=True): bar_chart(MOCK["headcount_by_dept"], "Departmanlara Göre Çalışan Sayısı", color="#059669", horizontal=True)
    with col_f:
        with st.container(border=True): bar_chart(MOCK["headcount_by_position"], "Pozisyonlara Göre Çalışan Sayısı", color="#d97706", horizontal=True)

    if period_type == "Yıllık":
        with st.container(border=True):
            trend_line(
                TREND_PERIODS,
                {"Çalışan Sayısı": MOCK["headcount_trend"]},
                "Aylara Göre Çalışan Sayısı — Son 12 Ay",
            )


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Ücret
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    c1, c2, c3 = st.columns(3)
    with c1: kpi("Ortalama Maaş", fmt_currency(MOCK["salary_avg"]), icon="💵")
    with c2: kpi("Minimum Maaş", fmt_currency(MOCK["salary_min"]), icon="📉")
    with c3: kpi("Maksimum Maaş", fmt_currency(MOCK["salary_max"]), icon="📈")

    c4, c5, c6 = st.columns(3)
    with c4: kpi("Ort. Saatlik Ücret", fmt_currency(MOCK["salary_hourly_avg"]), icon="⏱️")
    with c5: kpi("Min. Saatlik Ücret", fmt_currency(MOCK["salary_hourly_min"]), icon="📉")
    with c6: kpi("Maks. Saatlik Ücret", fmt_currency(MOCK["salary_hourly_max"]), icon="📈")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True): bar_chart(MOCK["salary_by_dept"], "Departmanlara Göre Ortalama Maaş (₺)", color=BLUE, horizontal=True)
    with col_b:
        with st.container(border=True): bar_chart(MOCK["salary_by_position"], "Pozisyona Göre Ortalama Maaş (₺)", color="#059669", horizontal=True)

    with st.container(border=True): bar_chart(MOCK["salary_by_tenure"], "Kıdem Yılı Skalasına Göre Ortalama Maaş (₺)", color="#d97706")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Maliyet
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    c1, c2, c3 = st.columns(3)
    with c1: kpi("Toplam İşçilik Maliyeti", fmt_currency(MOCK["cost_labor_total"]), icon="🏭")
    with c2: kpi("Toplam SGK Maliyeti", fmt_currency(MOCK["cost_sgk_total"]), icon="🏛️")
    with c3: kpi("Toplam Fazla Mesai Maliyeti", fmt_currency(MOCK["cost_overtime_total"]), icon="⚡")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Fazla Mesai
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    c1, c2 = st.columns(2)
    with c1: kpi("Toplam Fazla Mesai Gün", f"{fmt_num(MOCK['overtime_total'])} saat", icon="🕐")
    with c2: kpi("Ortalama Fazla Mesai", f"{fmt_num(MOCK['overtime_avg'], 1)} saat", icon="📊")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True): bar_chart(MOCK["overtime_by_position"], "Pozisyonlara Göre Ortalama FM (saat)", color=BLUE, horizontal=True)
    with col_b:
        with st.container(border=True): pie_chart(MOCK["overtime_by_type"], "Fazla Mesai Türü Dağılımı")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Devamsızlık
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    c1, c2, c3 = st.columns(3)
    with c1: kpi("Toplam Devamsızlık", f"{fmt_num(MOCK['total_absent_days'])} gün", icon="📋")
    with c2: kpi("Ortalama Devamsızlık", f"{fmt_num(MOCK['avg_absent_days'], 2)} gün", icon="📉")
    with c3: kpi("Toplam Yıllık İzin Bakiyesi", f"{fmt_num(MOCK['total_annual_leave_balance'])} gün", icon="🏖️")

    c4, c5, c6 = st.columns(3)
    with c4: kpi("Ort. Yıllık İzin Bakiyesi", f"{fmt_num(MOCK['avg_annual_leave_balance'], 1)} gün", icon="📅")
    with c5: kpi("Toplam Kullanılan Yıllık İzin", f"{fmt_num(MOCK['total_used_annual_leave'])} gün", icon="✅")
    with c6: kpi("Ort. Kullanılan Yıllık İzin", f"{fmt_num(MOCK['avg_used_annual_leave'], 1)} gün", icon="📊")

    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True): pie_chart(MOCK["absence_types"], "Devamsızlık Türüne Göre Dağılım")
    with col_b:
        with st.container(border=True): bar_chart(MOCK["absence_by_tenure"], "Kıdem Skalasına Göre Devamsızlık (gün)", color="#d97706")

    with st.container(border=True): bar_chart(MOCK["absence_by_age"], "Yaş Skalasına Göre Devamsızlık (gün)", color="#7c3aed")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — İşe Alım & Çıkış
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    c1, c2, c3 = st.columns(3)
    with c1: kpi("İş Başı Yapan Çalışan", fmt_num(MOCK["hires"]), icon="🟢")
    with c2: kpi("İşten Çıkan Çalışan", fmt_num(MOCK["terminations"]), icon="🔴")
    if period_type == "Yıllık":
        with c3: kpi("Turnover Oranı (Yıllık)", f"%{fmt_num(MOCK['turnover_rate_yearly'], 1)}", icon="📆")
    else:
        with c3: kpi("Turnover Oranı", f"%{fmt_num(MOCK['turnover_rate_monthly'], 1)}", icon="🔄")


    st.markdown("<br>", unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        with st.container(border=True): pie_chart(MOCK["termination_reasons"], "İşten Çıkış Sebebi Dağılımı")
    with col_b:
        with st.container(border=True): pie_chart(MOCK["termination_by_collar"], "Yaka Rengine Göre İşten Çıkma Dağılımı")

    with st.container(border=True): bar_chart(MOCK["termination_by_tenure"], "Kıdeme Göre İşten Çıkma Dağılımı", color="#dc2626")

    if period_type == "Yıllık":
        with st.container(border=True):
            trend_line(
                TREND_PERIODS,
                {"İşe Alım": MOCK["hires_trend"], "İşten Çıkış": MOCK["terminations_trend"]},
                "Aylara Göre İşe Alım & Çıkma — Son 12 Ay",
            )
