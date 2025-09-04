import streamlit as st
import pandas as pd
import numpy as np
from utils import (
    conductor_weight_housewire,
    conductor_weight_aluminium,
    conductor_weight_multicore,
    conductor_weight_armoured,
    calculate_costs_from_inputs,
    sample_catalog_df
)

st.set_page_config(page_title="Wire Costing", layout="centered")

st.title("⚡ Wire Costing • Calculator & Comparison")

# --- Sidebar ---
with st.sidebar:
    st.header("Data (optional)")
    uploaded_file = st.file_uploader("Upload costing sheet (Excel)", type=["xlsx", "xls"])
    st.markdown("---")

# Load catalog
if uploaded_file is not None:
    try:
        df_catalog = pd.read_excel(uploaded_file)
        st.sidebar.success("Excel loaded ✓")
    except Exception as e:
        st.sidebar.error("Could not read Excel. Using sample data.")
        df_catalog = sample_catalog_df()
else:
    df_catalog = sample_catalog_df()

CABLE_CATEGORIES = sorted(df_catalog['Category'].unique().tolist())

# --- Mode Selection ---
mode = st.radio("Choose Mode:", ["Calculator", "Comparison Maker"])

# --- CALCULATOR MODE ---
if mode == "Calculator":
    st.header("Calculator")

    category = st.selectbox("Wire Category", options=["House Wire", "Aluminium Cable", "Multi-core Cable", "Armoured Cable"])

    with st.form("calc_form"):
        st.subheader("Inputs")
        col1, col2 = st.columns(2)
        with col1:
            gauge = st.number_input("Gauge (mm)", value=9.5, format="%.3f")
            strands = st.number_input("No. of Strands", min_value=1, value=14)
            length = st.number_input("Length (gaj)", value=100.0)
            coil_weight = st.number_input("Coil Weight (kg)", value=1.2, format="%.3f")
        with col2:
            pvc_rate = st.number_input("PVC Rate (₹/kg)", value=130.0)
            conductor_rate = st.number_input("Conductor Rate (₹/kg)", value=950.0)
            labour_type = st.selectbox("Labour Type", options=["percentage", "per_kg"])
            labour_value = st.number_input("Labour Value", value=4.0)

        # Extra inputs depending on category
        cores, armour_wt, armour_rate = None, 0.0, 0.0
        if category == "Multi-core Cable":
            cores = st.number_input("No. of Cores", min_value=2, value=2)
        if category == "Armoured Cable":
            armour_wt = st.number_input("Armour Weight (kg)", min_value=0.0, value=0.2)
            armour_rate = st.number_input("Armour Rate (₹/kg)", min_value=0.0, value=70.0)

        submit = st.form_submit_button("Calculate")

    if submit:
        # Formula per category
        if category == "House Wire":
            conductor_wt = conductor_weight_housewire(gauge, strands, length)
        elif category == "Aluminium Cable":
            conductor_wt = conductor_weight_aluminium(gauge, strands, length)
        elif category == "Multi-core Cable":
            conductor_wt = conductor_weight_multicore(gauge, strands, length, cores)
        elif category == "Armoured Cable":
            conductor_wt = conductor_weight_armoured(gauge, strands, length, armour_wt)
        else:
            conductor_wt = 0.0

        pvc_wt = max(0.0, coil_weight - conductor_wt)

        result = calculate_costs_from_inputs(
            conductor_weight=conductor_wt,
            pvc_weight=pvc_wt,
            pvc_rate=pvc_rate,
            conductor_rate=conductor_rate,
            labour_type=labour_type,
            labour_value=labour_value,
            armour_weight=armour_wt,
            armour_rate=armour_rate
        )

        st.subheader("Result")
        st.metric("Final Cost (₹)", f"{result['final_cost']:.2f}")
        st.write({
            "Conductor Weight (kg)": round(conductor_wt, 4),
            "PVC Weight (kg)": round(pvc_wt, 4),
            "Conductor Cost (₹)": round(result['conductor_cost'], 2),
            "Insulation Cost (₹)": round(result['insulation_cost'], 2),
            "Armour Cost (₹)": round(result['armour_cost'], 2),
            "Labour Cost (₹)": round(result['labour_cost'], 2),
            "Final Cost (₹)": round(result['final_cost'], 2)
        })
        st.pyplot(result['chart_fig'])
