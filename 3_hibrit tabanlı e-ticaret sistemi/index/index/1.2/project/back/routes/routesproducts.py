# back/routes/routesproducts.py

from flask import Blueprint, request, jsonify
from back.database import product_collection
from back.auth import validate_jwt
from bson.objectid import ObjectId, InvalidId

products_bp = Blueprint("products", __name__)


@products_bp.route('/add-product', methods=['POST'])
def add_product():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded = validate_jwt(token)
    if "error" in decoded:
        return jsonify(decoded), 401

    # Sadece tedarikçi rolü
    if decoded.get('role') != 'supplier':
        return jsonify({"error": "Bu işlem yalnızca Tedarikçiler için geçerlidir!"}), 403

    data = request.get_json() or {}
    product_name = data.get('product_name')
    price = data.get('price')

    # Eksik alanlar
    if not product_name or price is None:
        return jsonify({"error": "Ürün adı ve fiyat zorunludur!"}), 400

    product_collection.insert_one({
        "product_name": product_name,
        "price": price,
        "added_by": decoded['email']
    })

    return jsonify({"message": "Ürün başarıyla eklendi!"}), 201

@products_bp.route('/update-product/<product_id>', methods=['PUT'])
def update_product(product_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded = validate_jwt(token)
    if "error" in decoded:
        return jsonify(decoded), 401

    if decoded.get('role') != 'supplier':
        return jsonify({"error": "Bu işlem yalnızca Tedarikçiler için geçerlidir!"}), 403

    # Geçersiz ObjectId yakalama
    try:
        oid = ObjectId(product_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Geçersiz ürün ID!"}), 400

    data = request.get_json() or {}
    product_name = data.get('product_name')
    price = data.get('price')

    # Eksik alanlar
    if not product_name or price is None:
        return jsonify({"error": "Ürün adı ve fiyat zorunludur!"}), 400

    result = product_collection.update_one(
        {"_id": oid},
        {"$set": {"product_name": product_name, "price": price}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Ürün bulunamadı veya güncellenemedi!"}), 404

    return jsonify({"message": "Ürün başarıyla güncellendi!"}), 200

@products_bp.route('/delete-product/<product_id>', methods=['DELETE'])
def delete_product(product_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded = validate_jwt(token)
    if "error" in decoded:
        return jsonify(decoded), 401

    if decoded.get('role') != 'supplier':
        return jsonify({"error": "Bu işlem yalnızca Tedarikçiler için geçerlidir!"}), 403

    try:
        oid = ObjectId(product_id)
    except (InvalidId, TypeError):
        return jsonify({"error": "Geçersiz ürün ID!"}), 400

    result = product_collection.update_one(
        {"_id": oid},
        {"$set": {"is_deleted": True}}
    )

    if result.modified_count == 0:
        return jsonify({"error": "Ürün bulunamadı veya silinemedi!"}), 404

    return jsonify({"message": "Ürün başarıyla silindi (Soft-delete)!"}), 200

@products_bp.route('/list-products', methods=['GET'])
def list_products():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded = validate_jwt(token)
    if "error" in decoded:
        return jsonify(decoded), 401

    # Soft-delete edilmiş olmayanları listele
    cursor = product_collection.find({"is_deleted": {"$ne": True}})
    result = []
    for p in cursor:
        p['_id'] = str(p['_id'])
        result.append(p)
    return jsonify(result), 200