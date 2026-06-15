from flask import Flask, jsonify, request, Response
import socket
from datetime import datetime
import json

app = Flask(__name__)

todo = []
counter = 1

# Model Todo:
# {
#   "id": 1,
#   "titulo": "Aprender Flask",
#   "descripcion": "Completar el mini-proyecto",
#   "completada": False,
#   "creada_en": "2025-06-15T10:00:00"
# }

@app.route('/')
def home():
    data = {
        "message": "API funcionando correctamente 🚀",
        "pod": socket.gethostname(),
        "endpoints": {
            "GET /tareas": "lista de todas las tareas",
            "GET /tareas/<id>": "obtener tarea por ID",
            "POST /tareas": "crear una nueva tarea",
            "PUT /tareas/<id>": "actualizar una tarea completa",
            "PATCH /tareas/<id>": "actualizar una tarea parcialmente",
            "DELETE /tareas/<id>": "eliminar una tarea",
        }
    }
    return Response(json.dumps(data, indent=2, ensure_ascii=False), mimetype='application/json')

@app.route('/health')
def health():
    return jsonify({"status": "healthy"}), 200

@app.route('/ready')
def ready():
    return jsonify({"status": "ready"}), 200

# ========== CRUD DE TAREAS ==========

@app.route('/tareas', methods=['GET'])
def obtener_tareas():
    return jsonify({"tareas": todo, "total": len(todo)}), 200

@app.route('/tareas/<int:id>', methods=['GET'])
def obtener_tarea(id):
    tarea = next((t for t in todo if t["id"] == id), None)
    if tarea is None:
        return jsonify({"error": f"Tarea con id {id} no encontrada"}), 404
    return jsonify(tarea), 200

@app.route('/tareas', methods=['POST'])
def crear_tarea():
    global counter
    datos = request.get_json()
    
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
    if 'titulo' not in datos:
        return jsonify({"error": "El campo 'titulo' es obligatorio"}), 400
    
    nueva_tarea = {
        "id": counter,
        "titulo": datos['titulo'],
        "descripcion": datos.get('descripcion', ''),
        "completada": datos.get('completada', False),
        "creada_en": datetime.now().isoformat()
    }
    todo.append(nueva_tarea)
    counter += 1
    return jsonify(nueva_tarea), 201

@app.route('/tareas/<int:id>', methods=['PUT'])
def actualizar_tarea_completa(id):
    tarea = next((t for t in todo if t["id"] == id), None)
    if tarea is None:
        return jsonify({"error": f"Tarea con id {id} no encontrada"}), 404
    
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
    
    tarea['titulo'] = datos.get('titulo', tarea['titulo'])
    tarea['descripcion'] = datos.get('descripcion', tarea['descripcion'])
    tarea['completada'] = datos.get('completada', tarea['completada'])
    
    return jsonify(tarea), 200

@app.route('/tareas/<int:id>', methods=['PATCH'])
def actualizar_tarea_parcial(id):
    tarea = next((t for t in todo if t["id"] == id), None)
    if tarea is None:
        return jsonify({"error": f"Tarea con id {id} no encontrada"}), 404
    
    datos = request.get_json()
    if not datos:
        return jsonify({"error": "No se recibieron datos"}), 400
    
    if 'titulo' in datos:
        tarea['titulo'] = datos['titulo']
    if 'descripcion' in datos:
        tarea['descripcion'] = datos['descripcion']
    if 'completada' in datos:
        tarea['completada'] = datos['completada']
    
    return jsonify(tarea), 200

@app.route('/tareas/<int:id>', methods=['DELETE'])
def eliminar_tarea(id):
    global todo
    tarea = next((t for t in todo if t["id"] == id), None)
    if tarea is None:
        return jsonify({"error": f"Tarea con id {id} no encontrada"}), 404
    
    todo = [t for t in todo if t["id"] != id]
    return jsonify({"mensaje": f"Tarea con id {id} eliminada correctamente"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)