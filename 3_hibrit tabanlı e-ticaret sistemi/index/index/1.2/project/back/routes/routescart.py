# back/routes/routescart.py

from flask import Blueprint, request, jsonify
from back.database import cart_collection, product_collection
from back.auth import validate_jwt
from back.util.email_utils import send_email_to_users
from bson import ObjectId

cart_bp = Blueprint("cart", __name__)

@cart_bp.route('/add-to-cart', methods=['POST'])
def add_to_cart():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded_token = validate_jwt(token)
    if "error" in decoded_token:
        return jsonify(decoded_token), 401

    user_id = decoded_token['email']
    data = request.get_json()
    product_id_raw = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id_raw:
        return jsonify({"error": "Ürün ID eksik!"}), 400

    try:
        product_id = ObjectId(product_id_raw)
    except:
        return jsonify({"error": "Geçersiz ürün ID!"}), 400

    product = product_collection.find_one({"_id": product_id})
    if not product:
        return jsonify({"error": "Ürün bulunamadı!"}), 404

    cart_collection.insert_one({
        "user_id": user_id,
        "product_id": product_id,
        "product_name": product.get("product_name", "Bilinmeyen Ürün"),
        "price": product.get("price", 0),
        "quantity": quantity
    })

    send_email_to_users(user_id, "Sepetiniz Güncellendi!")

    return jsonify({"message": "Ürün sepete eklendi ve e-posta bildirimi gönderildi!"}), 201


@cart_bp.route('/complete-cart', methods=['POST'])
def complete_cart():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded_token = validate_jwt(token)
    if "error" in decoded_token:
        return jsonify(decoded_token), 401

    user_id = decoded_token['email']

    result = cart_collection.update_many(
        {"user_id": user_id},
        {"$set": {"status": "Tamamlandı"}}
    )

    # Eğer eşleşen belge yoksa sepette ürün yok demektir
    if result.matched_count == 0:
        return jsonify({"error": "Sepetinizde tamamlanacak ürün yok!"}), 400

    send_email_to_users(user_id, "Siparişiniz Alındı!")

    return jsonify({"message": "Sepet başarıyla tamamlandı ve e-posta bildirimi gönderildi!"}), 200


@cart_bp.route('/get-cart', methods=['GET'])
def get_cart():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded_token = validate_jwt(token)
    if "error" in decoded_token:
        return jsonify(decoded_token), 401

    user_id = decoded_token['email']
    cart_items_raw = list(cart_collection.find({"user_id": user_id}))
    cart_items = []

    for item in cart_items_raw:
        product_id = item.get("product_id")
        if isinstance(product_id, str) and ObjectId.is_valid(product_id):
            product_id = ObjectId(product_id)

        product = product_collection.find_one({"_id": product_id}) if product_id else None
        if product:
            cart_items.append({
                "_id": str(item["_id"]),
                "product_id": str(product_id),
                "product_name": product.get("product_name", "Bilinmeyen Ürün"),
                "price": product.get("price", 0),
                "quantity": item.get("quantity", 1)
            })

    return jsonify({"cart": cart_items}), 200


@cart_bp.route('/delete-from-cart', methods=['POST'])
def delete_from_cart():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"error": "Token bulunamadı!"}), 401

    token = auth_header.split(" ")[1]
    decoded_token = validate_jwt(token)
    if "error" in decoded_token:
        return jsonify(decoded_token), 401

    user_id = decoded_token['email']
    data = request.get_json()
    product_id_raw = data.get('product_id')

    if not product_id_raw:
        return jsonify({"error": "Ürün ID'si eksik!"}), 400

    try:
        product_id = ObjectId(product_id_raw)
    except:
        return jsonify({"error": "Geçersiz ürün ID!"}), 400

    result = cart_collection.delete_one({
        "user_id": user_id,
        "product_id": product_id
    })

    if result.deleted_count == 1:
        return jsonify({"message": "Ürün sepetten çıkarıldı!"}), 200
    else:
        return jsonify({"error": "Ürün sepette bulunamadı."}), 404