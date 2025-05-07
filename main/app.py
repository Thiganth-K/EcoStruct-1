from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Grade data for dropdown and calculations
GRADE_DATA = {
    "M20": {"ratio": "1:1.5:3", "cement": 403.2, "fine_agg": 672, "coarse_agg": 1260, "ecf": 0.11},
    "M25": {"ratio": "1:1:2", "cement": 360, "fine_agg": 679, "coarse_agg": 1207, "ecf": 0.12},
    "M30": {"ratio": "1:0.75:1.5", "cement": 350, "fine_agg": 711, "coarse_agg": 1283, "ecf": 0.13},
    "M35": {"ratio": "1:0.5:1", "cement": 420, "fine_agg": 750, "coarse_agg": 1200, "ecf": 0.14},
    "M40": {"ratio": "1:0.25:0.5", "cement": 400, "fine_agg": 660, "coarse_agg": 1168, "ecf": 0.15},
    "M45": {"ratio": "1:3.19:4.06", "cement": 450, "fine_agg": 685, "coarse_agg": 1150, "ecf": 0.16},
    "M50": {"ratio": "1:2.28:3.12", "cement": 450, "fine_agg": 750, "coarse_agg": 1200, "ecf": 0.17},
}

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/main_menu')
def main_menu():
    return render_template('main_menu.html')

@app.route('/material/<material>')
def material_page(material):
    if material.lower() == "concrete":
        return redirect(url_for('concrete_options'))
    return render_template('material_page.html', material=material)

@app.route('/concrete_options')
def concrete_options():
    return render_template('concrete_options.html')

@app.route('/concrete/column/step1', methods=['GET', 'POST'])
def column_step1():
    if request.method == 'POST':
        session['num_columns'] = request.form['num_columns']
        return redirect(url_for('column_step2'))
    return render_template('column_step1.html')

@app.route('/concrete/column/step2', methods=['GET', 'POST'])
def column_step2():
    num_columns = int(session.get('num_columns', 1))
    if request.method == 'POST':
        columns = []
        for i in range(num_columns):
            columns.append({
                "length": float(request.form[f'length_{i}']),
                "breadth": float(request.form[f'breadth_{i}']),
                "depth": float(request.form[f'depth_{i}']),
                "diameter": float(request.form[f'diameter_{i}']),
                "steel_length": float(request.form[f'steel_length_{i}']),
                "steel_count": int(request.form[f'steel_count_{i}']),
                "grade": request.form[f'grade_{i}'],
                "specification": request.form[f'specification_{i}'],
                "ecf": float(request.form[f'ecf_{i}'])
            })
        session['columns'] = columns
        return redirect(url_for('calculating'))
    return render_template('column_step2.html', grades=GRADE_DATA.keys(), num_columns=num_columns)

@app.route('/calculating')
def calculating():
    return render_template('calculating.html')

@app.route('/result')
def result():
    columns_input = session.get('columns', [])
    columns = []
    total_weight_of_steel_concrete = 0
    total_emitted_carbon = 0

    for col in columns_input:
        grade_data = GRADE_DATA.get(col['grade'], {})
        cement_per_m3 = grade_data.get('cement', 0)
        fine_per_m3 = grade_data.get('fine_agg', 0)
        coarse_per_m3 = grade_data.get('coarse_agg', 0)
        ecf = col['ecf']

        # Volume
        volume = col['length'] * col['breadth'] * col['depth']

        # Material Quantities
        cement = cement_per_m3 * volume
        fine = fine_per_m3 * volume
        coarse = coarse_per_m3 * volume
        concrete_weight = cement + fine + coarse

        # Steel Calculations
        diameter_m = col['diameter'] / 1000
        steel_volume = ((3.14 * (diameter_m ** 2)) / 4) * col['steel_length']
        steel_kg = steel_volume * 7860
        applied_count_steel_kg = steel_kg * col['steel_count']

        # Total Weight (Concrete + Steel)
        weight_of_steel_concrete = concrete_weight + applied_count_steel_kg

        # Emitted Carbon
        emitted_carbon = weight_of_steel_concrete * ecf

        total_weight_of_steel_concrete += weight_of_steel_concrete
        total_emitted_carbon += emitted_carbon

        columns.append({
            **col,
            "volume": volume,
            "cement": cement,
            "fine": fine,
            "coarse": coarse,
            "concrete_weight": concrete_weight,
            "steel_kg": steel_kg,
            "applied_count_steel_kg": applied_count_steel_kg,
            "weight_of_steel_concrete": weight_of_steel_concrete,
            "emitted_carbon": emitted_carbon
        })

    return render_template('result.html', columns=columns, num_columns=len(columns),
                           total_weight_of_steel_concrete=total_weight_of_steel_concrete,
                           total_emitted_carbon=total_emitted_carbon)

if __name__ == '__main__':
    app.run(debug=True)