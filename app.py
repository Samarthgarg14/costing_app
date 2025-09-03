# app.py
import streamlit as st
import pandas as pd
import numpy as np
from utils import (
    conductor_weight_housewire,
    conductor_weight_generic,
    calculate_costs_from_inputs,
    sample_catalog_df
)

st.set_page_config(page_title="Wire Costing", layout="centered")

st.title("⚡ Copper/ Cable Costing • Calculator & Comparison")
st.markdown("Mobile-friendly Streamlit app — Calculator + Comparison Maker")

# --- Sidebar: upload Excel / instructions ---
with st.sidebar:
    st.header("Data (optional)")
    uploaded_file = st.file_uploader("Upload costing sheet (Excel)", type=["xlsx", "xls"])
    st.markdown(
        """
**Format suggestion for Excel sheet (for Comparison Maker):**

Columns: `Category`, `Item`, `Gauge`, `Strands`, `Length`, `CoilWeight`, `PVC_Rate`, `Conductor_Rate`, `Labour_Type`, `Labour_Value`

Example Labour_Type values: `percentage` or `per_kg`.
"""
    )
    st.markdown("---")
    st.markdown("If you don't upload a file, sample items will be used.")

# Load dataframe either from uploaded excel or sample
if uploaded_file is not None:
    try:
        df_catalog = pd.read_excel(uploaded_file)
        st.sidebar.success("Excel loaded ✓")
    except Exception as e:
        st.sidebar.error("Could not read Excel. Using sample data.")
        df_catalog = sample_catalog_df()
else:
    df_catalog = sample_catalog_df()

# --- Home: two big buttons ---
st.markdown("### Choose Mode")
col1, col2 = st.columns(2)
with col1:
    if st.button("🧮 Calculator", key="calc"):
        st.session_state.mode = "calculator"
with col2:
    if st.button("🔁 Comparison Maker", key="cmp"):
        st.session_state.mode = "comparison"

# default mode
mode = st.session_state.get("mode", "calculator")

# --- Shared functions / constants ---
CABLE_CATEGORIES = sorted(df_catalog['Category'].unique().tolist())

# --- MODE: Calculator ---
if mode == "calculator":
    st.header("Calculator")
    # Category selection
    category = st.selectbox("Wire Category", options=["House Wire", "Aluminium Cable", "Multi-core Cable", "Armoured Cable", "Custom"], index=0)

    # Dynamic form area
    with st.form(key="calc_form"):
        st.subheader("Inputs")
        colA, colB = st.columns(2)
        with colA:
            gauge = st.number_input("Gauge (mm)", min_value=0.01, value=9.5, format="%.3f")
            strands = st.number_input("No. of Strands", min_value=1, value=14, step=1)
            length = st.number_input("Length (gaj)", min_value=1.0, value=100.0)
            coil_weight = st.number_input("Coil Weight (kg)", min_value=0.01, value=1.2, format="%.3f")
        with colB:
            pvc_rate = st.number_input("PVC Rate (₹/kg)", min_value=0.0, value=130.0)
            conductor_rate = st.number_input("Conductor Rate (₹/kg)", min_value=0.0, value=950.0)
            labour_type = st.selectbox("Labour Type", options=["percentage", "per_kg"])
            if labour_type == "percentage":
                labour_value = st.number_input("Labour (%)", min_value=0.0, value=4.0)
            else:
                labour_value = st.number_input("Labour (₹ / kg)", min_value=0.0, value=0.0)

        submit = st.form_submit_button("Calculate")

    if submit:
        # Choose conductor weight formula by category (extendable)
        if category == "House Wire":
            conductor_wt = conductor_weight_housewire(gauge, strands, length)
        else:
            # generic fallback (uses same 412 factor but allowing extension)
            conductor_wt = conductor_weight_generic(gauge, strands, length, factor=412)

        # Prevent negative pvc weight
        pvc_wt = max(0.0, coil_weight - conductor_wt)

        result = calculate_costs_from_inputs(
            conductor_weight=conductor_wt,
            pvc_weight=pvc_wt,
            pvc_rate=pvc_rate,
            conductor_rate=conductor_rate,
            labour_type=labour_type,
            labour_value=labour_value
        )

        st.subheader("Result")
        st.metric("Final Cost (₹)", f"{result['final_cost']:.2f}")
        st.write("---")
        st.write({
            "Conductor Weight (kg)": round(conductor_wt, 4),
            "Insulation Weight (kg)": round(pvc_wt, 4),
            "Conductor Cost (₹)": round(result['conductor_cost'], 2),
            "Insulation Cost (₹)": round(result['insulation_cost'], 2),
            "Labour Cost (₹)": round(result['labour_cost'], 2),
            "Final Cost (₹)": round(result['final_cost'], 2)
        })
        st.pyplot(result['chart_fig'])

# --- MODE: Comparison Maker ---
elif mode == "comparison":
    st.header("Comparison Maker")
    st.subheader("Select item from catalog (left) and enter custom inputs (right)")

    left_col, right_col = st.columns([1, 1])

    with left_col:
        st.markdown("**Catalog**")
        cat_choice = st.selectbox("Category", options=CABLE_CATEGORIES)
        items_in_cat = df_catalog.loc[df_catalog['Category'] == cat_choice, 'Item'].unique().tolist()
        item_choice = st.selectbox("Item", options=items_in_cat)

        # fetch row
        item_row = df_catalog[(df_catalog['Category'] == cat_choice) & (df_catalog['Item'] == item_choice)].iloc[0]

        st.markdown("**Standard (Catalog) Inputs**")
        st.write(item_row[['Gauge','Strands','Length','CoilWeight','PVC_Rate','Conductor_Rate','Labour_Type','Labour_Value']])

    with right_col:
        st.markdown("**Custom Inputs (override)**")
        g2 = st.number_input("Gauge (mm)", min_value=0.01, value=float(item_row.get('Gauge', 9.5)), format="%.3f")
        s2 = st.number_input("No. of Strands", min_value=1, value=int(item_row.get('Strands', 14)))
        l2 = st.number_input("Length (gaj)", min_value=1.0, value=float(item_row.get('Length', 100.0)))
        coil2 = st.number_input("Coil Weight (kg)", min_value=0.01, value=float(item_row.get('CoilWeight', 1.2)), format="%.3f")
        pvc_rate2 = st.number_input("PVC Rate (₹/kg)", min_value=0.0, value=float(item_row.get('PVC_Rate', 130.0)))
        cond_rate2 = st.number_input("Conductor Rate (₹/kg)", min_value=0.0, value=float(item_row.get('Conductor_Rate', 950.0)))
        labour_type2 = st.selectbox("Labour Type", options=["percentage", "per_kg"], index=0 if item_row.get('Labour_Type','percentage')=='percentage' else 1)
        if labour_type2 == "percentage":
            labour_value2 = st.number_input("Labour (%)", min_value=0.0, value=float(item_row.get('Labour_Value', 4.0)))
        else:
            labour_value2 = st.number_input("Labour (₹/kg)", min_value=0.0, value=float(item_row.get('Labour_Value', 0.0)))

        if st.button("Compare"):
            # Standard calc
            std_conductor = conductor_weight_housewire(item_row['Gauge'], item_row['Strands'], item_row['Length'])
            std_pvc = max(0.0, item_row['CoilWeight'] - std_conductor)
            std_result = calculate_costs_from_inputs(
                conductor_weight=std_conductor,
                pvc_weight=std_pvc,
                pvc_rate=item_row['PVC_Rate'],
                conductor_rate=item_row['Conductor_Rate'],
                labour_type=item_row['Labour_Type'],
                labour_value=item_row['Labour_Value']
            )

            # Custom calc
            cust_conductor = conductor_weight_housewire(g2, s2, l2)
            cust_pvc = max(0.0, coil2 - cust_conductor)
            cust_result = calculate_costs_from_inputs(
                conductor_weight=cust_conductor,
                pvc_weight=cust_pvc,
                pvc_rate=pvc_rate2,
                conductor_rate=cond_rate2,
                labour_type=labour_type2,
                labour_value=labour_value2
            )

            # Side by side
            st.subheader("Comparison")
            comp_df = pd.DataFrame({
                "Metric": ["Conductor Weight (kg)", "Insulation Weight (kg)", "Conductor Cost (₹)", "Insulation Cost (₹)", "Labour Cost (₹)", "Final Cost (₹)"],
                "Standard": [
                    round(std_conductor,4), round(std_pvc,4), round(std_result['conductor_cost'],2), round(std_result['insulation_cost'],2), round(std_result['labour_cost'],2), round(std_result['final_cost'],2)
                ],
                "Custom": [
                    round(cust_conductor,4), round(cust_pvc,4), round(cust_result['conductor_cost'],2), round(cust_result['insulation_cost'],2), round(cust_result['labour_cost'],2), round(cust_result['final_cost'],2)
                ]
            })
            st.dataframe(comp_df, use_container_width=True)

            diff_pct = (cust_result['final_cost'] - std_result['final_cost'])/std_result['final_cost']*100 if std_result['final_cost'] != 0 else np.nan
            st.metric("Difference (Custom vs Standard)", f"{diff_pct:.2f} %")
            st.pyplot(cust_result['chart_fig'])

st.markdown("---")
st.caption("Built with ❤️ • Streamlit. Ask to add features like saving history, PDF export, or live rate fetch.")
