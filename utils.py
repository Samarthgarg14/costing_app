# utils.py
import pandas as pd
import matplotlib.pyplot as plt

def conductor_weight_housewire(gauge, strands, length_gaj):
    """
    Original formula used in conversation:
    conductor_weight_kg = (gauge^2 * 412 * strands * length) / 100000000
    where length is in 'gaj' as provided by user
    """
    try:
        val = (gauge ** 2) * 412 * strands * length_gaj / 100000000.0
        return float(val)
    except Exception:
        return 0.0

def conductor_weight_generic(gauge, strands, length_gaj, factor=412):
    return conductor_weight_housewire(gauge, strands, length_gaj)  # placeholder; can extend

def calculate_costs_from_inputs(conductor_weight, pvc_weight, pvc_rate, conductor_rate, labour_type, labour_value):
    """
    Returns a dictionary with conductor_cost, insulation_cost, labour_cost, final_cost and a chart figure.
    labour_type: 'percentage' or 'per_kg'
    labour_value: if percentage, provide 4.0 for 4%
                 if per_kg, provide rupees per kg
    """
    conductor_cost = conductor_weight * conductor_rate
    insulation_cost = pvc_weight * pvc_rate
    base_cost = conductor_cost + insulation_cost

    if labour_type == "percentage":
        labour_cost = base_cost * (labour_value / 100.0)
    else:
        # per kg on conductor weight
        labour_cost = conductor_weight * labour_value

    final_cost = base_cost + labour_cost

    # small chart: pie of contributions
    labels = []
    sizes = []
    if conductor_cost > 0:
        labels.append("Conductor")
        sizes.append(conductor_cost)
    if insulation_cost > 0:
        labels.append("Insulation")
        sizes.append(insulation_cost)
    if labour_cost > 0:
        labels.append("Labour")
        sizes.append(labour_cost)

    fig, ax = plt.subplots(figsize=(4,3))
    if sizes and sum(sizes) > 0:
        ax.pie(sizes, labels=labels, autopct='%1.1f%%')
        ax.set_title("Cost Breakdown")
    else:
        ax.text(0.5,0.5,"No cost data", ha='center')

    return {
        "conductor_cost": float(conductor_cost),
        "insulation_cost": float(insulation_cost),
        "labour_cost": float(labour_cost),
        "final_cost": float(final_cost),
        "chart_fig": fig
    }

def sample_catalog_df():
    # Create a sample catalog dataframe for comparison mode
    data = [
        {"Category":"House Wire", "Item":"HouseWire-1mm", "Gauge":9.5, "Strands":14, "Length":100, "CoilWeight":1.2, "PVC_Rate":130.0, "Conductor_Rate":950.0, "Labour_Type":"percentage", "Labour_Value":4.0},
        {"Category":"House Wire", "Item":"HouseWire-1.5mm", "Gauge":12.0, "Strands":20, "Length":100, "CoilWeight":1.8, "PVC_Rate":130.0, "Conductor_Rate":950.0, "Labour_Type":"percentage", "Labour_Value":4.0},
        {"Category":"Aluminium Cable", "Item":"Alu-2.5mm", "Gauge":9.5, "Strands":14, "Length":100, "CoilWeight":1.4, "PVC_Rate":120.0, "Conductor_Rate":180.0, "Labour_Type":"per_kg", "Labour_Value":20.0},
    ]
    return pd.DataFrame(data)
