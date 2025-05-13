from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
CORS(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/<path:filename>')
def static_files(filename):
    return render_template(f'/{filename}')

data_storage = {}

@app.route('/validate', methods=['POST'])
def validate_form():
    try:
        global data_storage
        data_storage = {
            'trucks': [],
            'warehouses': [],
            'destinations': []
        }

        data = request.get_json()
        
        # Проверка заполненности всех полей
        if not all_fields_filled(data):
            return jsonify({'success': False, 'message': 'Все поля должны быть заполнены'}), 400
        
        # Проверка наличия грузов на складах
        if not validate_warehouse_quantities(data['warehouses'], data['destinations']):
            return jsonify({'success': False, 'message': 'Недостаточное количество груза на складах'}), 400
        
        # Проверка уникальности названий
        if not validate_unique_names(data):
            return jsonify({'success': False, 'message': 'Названия должны быть уникальными в пределах каждой формы'}), 400
        
        data_storage['trucks'] = data.get('trucks', [])
        data_storage['warehouses'] = data.get('warehouses', [])
        data_storage['destinations'] = data.get('destinations', [])
        
        return jsonify({'success': True, 'redirect': '/itinerary.html'}), 200   
    
    except Exception as e:
        return jsonify({'success': False, 'message': f'Ошибка сервера: {str(e)}'}), 500


@app.route('/data')
def get_data():
    global data_storage

    return jsonify({
        'trucks': data_storage['trucks'],
        'warehouses': data_storage['warehouses'],
        'destinations': data_storage['destinations']
    })


def all_fields_filled(data):
    """Проверка заполненности всех полей"""
    # типы грузов
    for cargo in data['cargo_types']:
        if not cargo['name'] or not cargo['weight']:
            return False
        
    # типы машин
    for truck in data['trucks']:
        if not truck['name'] or not truck['capacity']:
            return False
    
    # склады
    for warehouse in data['warehouses']:
        if not warehouse['name'] or not warehouse['address']:
            return False
        for cargo in warehouse['cargos']:
            if not cargo['type'] or not cargo['quantity']:
                return False
    
    # пункты приема
    for destination in data['destinations']:
        if not destination['name'] or not destination['address']:
            return False
        for cargo in destination['cargos']:
            if not cargo['type'] or not cargo['quantity']:
                return False
    
    return True


def validate_warehouse_quantities(warehouses, destinations):
    """Проверка наличия достаточного количества грузов на складах"""
    warehouse_cargos = {}
    destination_cargos = {}
    
    for warehouse in warehouses:
        for cargo in warehouse['cargos']:
            if cargo['type'] in warehouse_cargos:
                warehouse_cargos[cargo['type']] += float(cargo['quantity'])
            else:
                warehouse_cargos[cargo['type']] = float(cargo['quantity'])
    
    for destination in destinations:
        for cargo in destination['cargos']:
            if cargo['type'] not in warehouse_cargos:
                return False
            elif cargo['type'] in destination_cargos:
                destination_cargos[cargo['type']] += float(cargo['quantity'])
            else:
                destination_cargos[cargo['type']] = float(cargo['quantity'])

    for destination_cargo, dest_cargo_quantity in destination_cargos.items():
        if float(dest_cargo_quantity) > warehouse_cargos[destination_cargo]:
            return False
    
    return True


def validate_unique_names(data):
    """Проверка уникальности названий в пределах каждой формы"""
    # типы грузов
    cargo_names = [cargo['name'] for cargo in data['cargo_types']]
    if len(cargo_names) != len(set(cargo_names)):
        return False
    
    # склады
    warehouse_names = [warehouse['name'] for warehouse in data['warehouses']]
    if len(warehouse_names) != len(set(warehouse_names)):
        return False

    for warehouse in data['warehouses']:
        cargo_names_wh = [cargo['type'] for cargo in warehouse['cargos']]
        if len(cargo_names_wh) != len(set(cargo_names_wh)):
            return False
    
    # пункты приема
    destination_names = [destination['name'] for destination in data['destinations']]
    if len(destination_names) != len(set(destination_names)):
        return False

    for destination in data['destinations']:
        cargo_names_ds = [cargo['type'] for cargo in destination['cargos']]
        if len(cargo_names_ds) != len(set(cargo_names_ds)):
            return False
    
    return True


if __name__ == '__main__':
    app.run(debug=True, port=5000)