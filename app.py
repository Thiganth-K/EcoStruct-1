from flask import Flask, render_template, redirect, url_for, request, session
import time

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Needed for session

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    return render_template('signup.html')

@app.route('/materials', methods=['GET', 'POST'])
def materials():
    return render_template('materials.html')

@app.route('/material_selected', methods=['POST'])
def material_selected():
    material = request.form.get('material')
    if material == "Concrete":
        return redirect(url_for('concrete'))
    return render_template('material_selected.html', material=material)

@app.route('/column_count', methods=['GET', 'POST'])
def column_count():
    if request.method == 'POST':
        count = int(request.form.get('column_count'))
        session['column_count'] = count
        return redirect(url_for('multi_full_concrete_input'))
    return render_template('column_count.html')

@app.route('/multi_full_concrete_input', methods=['GET', 'POST'])
def multi_full_concrete_input():
    count = session.get('column_count', 1)
    if request.method == 'POST':
        columns = []
        for i in range(count):
            prefix = f'col_{i}_'
            columns.append({
                'length': float(request.form.get(prefix + 'length')),
                'breadth': float(request.form.get(prefix + 'breadth')),
                'height': float(request.form.get(prefix + 'height')),
                'diameter': float(request.form.get(prefix + 'diameter')),
                'steel_length': float(request.form.get(prefix + 'steel_length')),
                'count': int(request.form.get(prefix + 'count')),
                'grade': request.form.get(prefix + 'grade'),
                'ratio': request.form.get(prefix + 'ratio'),
                'cement': float(request.form.get(prefix + 'cement')),
                'fine': float(request.form.get(prefix + 'fine')),
                'coarse': float(request.form.get(prefix + 'coarse')),
                'ecf': float(request.form.get(prefix + 'ecf')),
            })
        session['columns'] = columns
        return redirect(url_for('loading'))
    return render_template('multi_full_concrete_input.html', count=count)

@app.route('/multi_full_concrete_result')
def multi_full_concrete_result():
    import time
    time.sleep(2)
    columns = session.get('columns', [])
    results = []
    total_weight = 0
    for col in columns:
        length = col['length']
        breadth = col['breadth']
        height = col['height']
        diameter = col['diameter']
        steel_length = col['steel_length']
        count = col['count']
        grade = col['grade']
        ratio = col['ratio']
        cement_per_m3 = col['cement']
        fine_per_m3 = col['fine']
        coarse_per_m3 = col['coarse']
        ecf = col['ecf']

        volume = length * breadth * height
        cement = cement_per_m3 * volume
        fine = fine_per_m3 * volume
        coarse = coarse_per_m3 * volume
        concrete_weight = cement + fine + coarse

        diameter_m = diameter / 1000
        steel_volume = ((3.14 * (diameter_m ** 2)) / 4) * steel_length
        steel_kg = steel_volume * 7860
        applied_count_steel_kg = steel_kg * count
        weight_of_steel_concrete = concrete_weight + applied_count_steel_kg
        emitted_carbon = weight_of_steel_concrete * ecf

        total_weight += weight_of_steel_concrete

        results.append({
            'length': length, 'breadth': breadth, 'height': height,
            'diameter': diameter, 'steel_length': steel_length, 'count': count,
            'grade': grade, 'ratio': ratio, 'cement': round(cement,2), 'fine': round(fine,2), 'coarse': round(coarse,2),
            'ecf': ecf, 'volume': round(volume,2), 'total_weight': round(concrete_weight,2),
            'steel_kg': round(steel_kg,2), 'applied_count_steel_kg': round(applied_count_steel_kg,2),
            'weight_of_steel_concrete': round(weight_of_steel_concrete,2), 'emitted_carbon': round(emitted_carbon,2)
        })
    return render_template('multi_full_concrete_result.html', results=results, total_weight=round(total_weight,2))

# Update the /concrete route to redirect to column_count
@app.route('/concrete', methods=['GET', 'POST'])
def concrete():
    if request.method == 'POST':
        option = request.form.get('concrete_section')
        if option == "Column":
            return redirect(url_for('column_count'))
        # You can add more redirects for Beam, Shear Wall, Slab as needed
    return render_template('concrete.html')

@app.route('/full_concrete_input', methods=['GET', 'POST'])
def full_concrete_input():
    if request.method == 'POST':
        # Store form data in session
        session['length'] = float(request.form.get('length'))
        session['breadth'] = float(request.form.get('breadth'))
        session['height'] = float(request.form.get('height'))
        session['diameter'] = float(request.form.get('diameter'))
        session['steel_length'] = float(request.form.get('steel_length'))
        session['count'] = int(request.form.get('count'))
        session['grade'] = request.form.get('grade')
        session['ratio'] = request.form.get('ratio')
        session['cement'] = float(request.form.get('cement'))
        session['fine'] = float(request.form.get('fine'))
        session['coarse'] = float(request.form.get('coarse'))
        session['ecf'] = float(request.form.get('ecf'))
        return redirect(url_for('loading'))
    return render_template('full_concrete_input.html')

@app.route('/loading')
def loading():
    return render_template('loading.html')

@app.route('/full_concrete_result')
def full_concrete_result():
    # Simulate calculation delay
    time.sleep(2)
    length = session.get('length')
    breadth = session.get('breadth')
    height = session.get('height')
    diameter = session.get('diameter')
    steel_length = session.get('steel_length')
    count = session.get('count')
    grade = session.get('grade')
    ratio = session.get('ratio')
    cement_per_m3 = session.get('cement')
    fine_per_m3 = session.get('fine')
    coarse_per_m3 = session.get('coarse')
    ecf = session.get('ecf')

    # Calculations
    volume = length * breadth * height
    cement = cement_per_m3 * volume
    fine = fine_per_m3 * volume
    coarse = coarse_per_m3 * volume
    total_weight = cement + fine + coarse

    # Steel calculations
    diameter_m = diameter / 1000  # Convert mm to meters
    # volume of steel for one bar: ((π * d^2) / 4) * length
    steel_volume = ((3.14 * (diameter_m ** 2)) / 4) * steel_length
    steel_kg = steel_volume * 7860  # Density of steel in kg/m³
    applied_count_steel_kg = steel_kg * count
    weight_of_steel_concrete = total_weight + applied_count_steel_kg
    emitted_carbon = weight_of_steel_concrete * ecf

    return render_template(
        'full_concrete_result.html',
        length=length, breadth=breadth, height=height,
        diameter=diameter, steel_length=steel_length, count=count,
        grade=grade, ratio=ratio, cement=round(cement,2), fine=round(fine,2), coarse=round(coarse,2),
        ecf=ecf, volume=round(volume,2), total_weight=round(total_weight,2),
        steel_kg=round(steel_kg,2), applied_count_steel_kg=round(applied_count_steel_kg,2),
        weight_of_steel_concrete=round(weight_of_steel_concrete,2), emitted_carbon=round(emitted_carbon,2)
    )

@app.route('/concrete_option')
def concrete_option():
    option = request.args.get('option')
    return render_template('concrete_option.html', option=option)

if __name__ == '__main__':
    app.run(debug=True)