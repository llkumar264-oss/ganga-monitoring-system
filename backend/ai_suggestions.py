def generate_suggestion(ph,turbidity,chemical):

    if chemical > 150:
        return "High chemical discharge detected. Inspect nearby industries."

    if turbidity > 70:
        return "Possible waste dumping detected."

    if ph < 6 or ph > 8:
        return "Water acidity abnormal. Immediate inspection required."

    return "Water quality normal."