import pandas as pd
import matplotlib.pyplot as plt

# ---------------------------
# CATEGORY-SPECIFIC FORMULAS
# ---------------------------

def conductor_weight_housewire(gauge, strands, length_gaj):
    """
    House Wire formula:
    (gauge^2 * 412 * strands * length) / 1e8
    """
    try:
        return (gauge ** 2) * 412 * strands * length_gaj / 100000000.0
    except Exception:
        return 0.0

def conductor_weight_aluminium(gauge, strands, length_gaj):
    """
    Aluminium cable formula (different factor, example = 300).
    Replace with real formula when available.
    """
    try:
        return (gauge ** 2) * 300 * strands * length_gaj / 100000000.0
    except Exception:
        return 0.0

def conductor_weight_multicore(gauge, strands, length_gaj, cores=2):
    """
    Multi-core cable: multiply base conductor by number of cores.
    """
    base = conductor_weight_housewire(gauge, strands, length_gaj)
    return base * cores

def conductor_weight_armoured(gauge, strands, length_gaj, armour_weight=0.0):
    """
    Armoured cable: base conductor + armour weight (given separately).
    """
    base = conductor_weight_housewire(gauge, strands, length_gaj)
    return base + armour_weight

# ---------------------------
# COST CALCULATION
# ---------------------------

def calculate_costs_from_inputs(conductor_weight, pvc_weight, pvc_rate, conductor_rate,
                                labour_type, labour_value,
                                armour_weight=0.0, armour_rate=0.0):
    conductor_cost = conductor_weight * conductor_rate
    insulation_cost = pvc_weight * pvc_rate
    armour_cost = armour_weight * armour_rate if armour_weight > 0 else 0.0

    base_cost = conductor_cost + insulation_cost + armour_cost

    if labour_type == "percentage":
        labour_cost = base_cost * (labour_value / 100.0)
    else:
        labour_cost = conductor_weight * labour_value

    final_cost = base_cost + labour_cost

    # Pie chart
    labels, sizes = [], []
    if conductor_cost: labels.append("Conductor"); sizes.append(conductor_cost)
    if insulation_cost: labels.append("Insulation"); sizes.append(insulation_cost)
    if armour_cost: labels.append("Armour"); sizes.append(armour_cost)
    if labour_cost: labels.append("Labour"); sizes.append(labour_cost)

    fig, ax = plt.subplots(figsize=(4,3))
    if sizes and sum(sizes) > 0:
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title("Cost Breakdown")
    else:
        ax.text(0.5,0.5,"No cost data", ha='center')

    return {
        "conductor_cost": float(conductor_cost),
        "insulation_cost": float(insulation_cost),
        "armour_cost": float(armour_cost),
        "labour_cost": float(labour_cost),
        "final_cost": float(final_cost),
        "chart_fig": fig
    }

# ---------------------------
# SAMPLE CATALOG
# ---------------------------

def sample_catalog_df():
    data = [
        {"Category":"House Wire", "Item":"HouseWire-1mm", "Gauge":9.5, "Strands":14, "Length":100, "CoilWeight":1.2, "PVC_Rate":130.0, "Conductor_Rate":950.0, "Labour_Type":"percentage", "Labour_Value":4.0},
        {"Category":"Aluminium Cable", "Item":"Alu-2.5mm", "Gauge":9.5, "Strands":14, "Length":100, "CoilWeight":1.4, "PVC_Rate":120.0, "Conductor_Rate":180.0, "Labour_Type":"per_kg", "Labour_Value":20.0},
        {"Category":"Multi-core Cable", "Item":"MultiCore-2x1.5mm", "Gauge":12.0, "Strands":20, "Length":100, "CoilWeight":2.5, "PVC_Rate":130.0, "Conductor_Rate":950.0, "Labour_Type":"percentage", "Labour_Value":5.0},
        {"Category":"Armoured Cable", "Item":"Armoured-4sqmm", "Gauge":14.0, "Strands":25, "Length":100, "CoilWeight":3.0, "PVC_Rate":120.0, "Conductor_Rate":950.0, "Labour_Type":"percentage", "Labour_Value":6.0},
    ]
    return pd.DataFrame(data)
