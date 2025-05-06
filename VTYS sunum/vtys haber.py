from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId


app = Flask(__name__)

# MongoDB Bağlantısı
client = MongoClient("mongodb://localhost:27017")
db = client["haberdb"]
articles = db["haberler"]

# Bağlantıyı test etmek için:
@app.route('/test-db', methods=['GET'])
def test_db():
    return jsonify({"message": "MongoDB bağlantısı başarılı!"})


#Haber Ekleme (INSERT)
@app.route('/articles', methods=['POST'])
def add_article():
    data = request.json  # Kullanıcının gönderdiği veriyi al
    article_id = articles.insert_one(data).inserted_id  # Gelen tüm veriyi MongoDB'ye kaydet
    return jsonify({"message": "Haber başarıyla eklendi!", "id": str(article_id)})



#Haber Güncelleme (UPDATE)
@app.route('/articles/<article_id>', methods=['PUT'])
def update_article(article_id):
    data = request.json
    result = articles.update_one(
        {"_id": ObjectId(article_id)},
        {"$set": data}  # Tüm gelen verileri güncelle veya ekle
    )
    if result.modified_count > 0:
        return jsonify({"message": "Haber başarıyla güncellendi veya yeni alanlar eklendi!"})
    else:
        return jsonify({"message": "Haber bulunamadı veya değişmedi."})


#haber silme
@app.route('/articles/<article_id>', methods=['DELETE'])
def delete_article(article_id):
    result = articles.delete_one({"_id": ObjectId(article_id)})
    if result.deleted_count > 0:
        return jsonify({"message": "Haber başarıyla silindi!"})
    else:
        return jsonify({"message": "Haber bulunamadı."})


#haberleri listeleme
@app.route('/articles', methods=['GET'])
def get_articles():
    all_articles = list(articles.find({}))  # Tüm haberleri getir
    for article in all_articles:
        article["_id"] = str(article["_id"])  # ObjectId'yi string formatına çevir
    return jsonify(all_articles)


if __name__ == "__main__":
    app.run(debug=True)


