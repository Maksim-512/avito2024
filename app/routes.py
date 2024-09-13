from flask import Flask, request, jsonify, Blueprint
from .models import Employee, Organization, OrganizationResponsible, Tender, Bid, BidReview
from .extensions import db

api = Blueprint('api', __name__)


# 1. Проверка доступности сервера
@api.route('/api/ping', methods=['GET'])
def ping():
    try:
        return jsonify('ok'), 200
    except Exception as e:
        return jsonify({"reason": str(e)}), 500


# 2. Получение списка тендеров
@api.route('/api/tenders', methods=['GET'])
def list_tenders():
    try:
        tenders = Tender.query.all()
        tenders_list = [
            {
                "id": tender.id,
                "name": tender.name,
                "description": tender.description,
                "status": tender.status,
                "service_type": tender.service_type,
                "version": tender.version,
                "created_at": tender.created_at
            }
            for tender in tenders
        ]
        return jsonify(tenders_list), 200
    except Exception as e:
        return jsonify({"reason": str(e)}), 400


# 3. Создание нового тендера
@api.route('/api/tenders/new', methods=['POST'])
def create_new_tender():
    try:
        print('Начало создания тендера')

        data = request.json
        print("Полученные данные:", data)

        name = data.get('name')
        description = data.get('description')
        service_type = data.get('serviceType')
        organization_id = data.get('organizationId')
        creator_username = data.get('creatorUsername')

        if not all([name, description, service_type, organization_id, creator_username]):
            return jsonify({"reason": "Не все данные предоставлены"}), 401

        print(
            f"Имя: {name}, Описание: {description}, Тип услуги: {service_type}, ID организации: {organization_id}, Имя пользователя: {creator_username}")

        creator = Employee.query.filter_by(username=creator_username).first()
        if not creator:
            return jsonify({"reason": "Пользователь не найден"}), 401

        print("Создатель найден:", creator_username)

        responsible = OrganizationResponsible.query.filter_by(organization_id=organization_id,
                                                              user_id=creator.id).first()
        if not responsible:
            return jsonify({"reason": "Пользователь не отвечает за данную организацию"}), 403

        print("Пользователь отвечает за организацию")

        tender = Tender(
            name=name,
            description=description,
            service_type=service_type,
            status="Created",
            organization_id=organization_id
        )
        db.session.add(tender)
        db.session.commit()

        print("Тендер успешно создан:", tender)

        return jsonify({
            "id": str(tender.id),
            "name": tender.name,
            "description": tender.description,
            "status": tender.status,
            "serviceType": tender.service_type,
            "version": tender.version,
            "createdAt": tender.created_at.isoformat()
        }), 200
    except Exception as e:
        print("Произошла ошибка:", str(e))
        return jsonify({"reason": "Ошибка сервера", "details": str(e)}), 500


# 4. Получить тендеры пользователя
@api.route('/api/tenders/my', methods=['GET'])
def list_user_tenders():
    try:
        username = request.args.get('username')
        print(f"Получен username: {username}")
        user = Employee.query.filter_by(username=username).first()

        if not user:
            return jsonify({"reason": "Пользователь не найден"}), 401

        print(f"Найден user ID: {user.id}")

        responsible = OrganizationResponsible.query.filter_by(user_id=user.id).first()

        if not responsible:
            return jsonify({"reason": "Пользователь не отвечает за организацию"}), 401

        print(f"Найден organization ID: {responsible.organization_id}")

        tenders = Tender.query.filter_by(organization_id=responsible.organization_id).all()
        tenders_list = [
            {
                "id": str(tender.id),
                "name": tender.name,
                "description": tender.description,
                "status": tender.status,
                "serviceType": tender.service_type,
                "version": tender.version,
                "createdAt": tender.created_at.isoformat()
            }
            for tender in tenders
        ]

        return jsonify(tenders_list), 200

    except Exception as e:
        print(f"Произошла ошибка: {e}")
        return jsonify({"reason": "Internal Server Error", "details": str(e)}), 500


# 5. Получение текущего статуса тендера
@api.route('/api/tenders/<string:tenderId>/status', methods=['GET'])
def get_tender_status(tenderId):
    username = request.args.get('username')
    user = Employee.query.filter_by(username=username).first()

    if not user:
        return jsonify({"reason": "Пользователь не найден"}), 401

    print(f"Найден user ID: {user.id}")

    responsible = OrganizationResponsible.query.filter_by(user_id=user.id).first()

    if not responsible:
        return jsonify({"reason": "Пользователь не отвечает за организацию"}), 403

    print(f"Найден organization ID: {responsible.organization_id}")

    tender = Tender.query.filter_by(id=tenderId, organization_id=responsible.organization_id).first()

    if not tender:
        return jsonify({"reason": "Тендер не найден"}), 404
    return jsonify({"status": tender.status}), 200


# 6. Изменение статуса тендера
@api.route('/api/tenders/<string:tenderId>/status', methods=['PUT'])
def update_tender_status(tenderId):
    try:
        data = request.json
        username = request.args.get('username')

        if not data or not username:
            return jsonify({"reason": "Неверный формат запроса или его параметры"}), 400

        status = data.get('status')

        if status not in ['Created', 'Published', 'Closed']:
            return jsonify({"reason": "Неверный статус"}), 400

        user = Employee.query.filter_by(username=username).first()
        if not user:
            return jsonify({"reason": "Пользователь не найден"}), 401

        responsible = OrganizationResponsible.query.filter_by(user_id=user.id).first()
        if not responsible:
            return jsonify({"reason": "Недостаточно прав для выполнения действия"}), 403

        tender = Tender.query.filter_by(id=tenderId, organization_id=responsible.organization_id).first()
        if not tender:
            return jsonify({"reason": "Тендер не найден"}), 404

        tender.status = status
        tender.version += 1
        db.session.commit()

        return jsonify({
            "id": str(tender.id),
            "name": tender.name,
            "description": tender.description,
            "status": tender.status,
            "serviceType": tender.service_type,
            "version": tender.version,
            "createdAt": tender.created_at.isoformat()
        }), 200

    except Exception as e:
        print(f"Ошибка: {str(e)}")
        return jsonify({"reason": "Внутренняя ошибка сервера"}), 500


# 7. Редактирование тендера
@api.route('/api/tenders/<string:tenderId>/edit', methods=['PATCH'])
def edit_tender(tenderId):
    tender_data = request.json
    username = request.args.get('username')

    if not username:
        return jsonify({"reason": "Пользователь не указан"}), 400

    user = Employee.query.filter_by(username=username).first()
    if not user:
        return jsonify({"reason": "Пользователь не найден"}), 401

    responsible = OrganizationResponsible.query.filter_by(user_id=user.id).first()
    if not responsible:
        return jsonify({"reason": "Недостаточно прав для выполнения действия"}), 403

    tender = Tender.query.get(tenderId)
    if not tender:
        return jsonify({"reason": "Тендер не найден"}), 404

    if 'name' in tender_data:
        tender.name = tender_data['name']
    if 'description' in tender_data:
        tender.description = tender_data['description']
    if 'status' in tender_data:
        tender.status = tender_data['status']
    if 'serviceType' in tender_data:
        tender.service_type = tender_data['serviceType']

    tender.version += 1
    db.session.commit()

    return jsonify({
        "id": str(tender.id),
        "name": tender.name,
        "description": tender.description,
        "status": tender.status,
        "serviceType": tender.service_type,
        "version": tender.version,
        "createdAt": tender.created_at.isoformat()
    }), 200


# 8. Откат версии тендера
@api.route('/api/tenders/<string:tenderId>/rollback/<int:version>', methods=['PUT'])
def rollback_tender(tenderId, version):
    tender = Tender.query.get(tenderId)
    if not tender:
        return jsonify({"reason": "Тендер не найден"}), 404

    target_version = Tender.query.filter_by(tender_id=tenderId, version=version - 1).first()
    if not target_version:
        return jsonify({"reason": "Версия не найдена"}), 404

    target_version = Tender.query.filter_by(tender_id=tenderId, version=version).first().delete()

    db.session.commit()

    return jsonify({"id": target_version.id, "name": target_version.name, "version": target_version.version}), 200


# 9. Создание нового предложения
@api.route('/api/bids/new', methods=['POST'])
def creating_new_bid():
    bid_data = request.json

    tender = Tender.query.get(bid_data['tender_id'])
    if not tender:
        return jsonify({"reason": "Тендер не найден"}), 404

    new_bid = Bid(
        name=bid_data['name'],
        description=bid_data['description'],
        tender_id=bid_data['tender_id'],
        status='CREATED',
        author_type=bid_data['author_type'],
        author_id=bid_data['author_id']
    )

    db.session.add(new_bid)
    db.session.commit()

    return jsonify({
        "id": new_bid.id,
        "name": new_bid.name,
        "status": new_bid.status,
        "version": new_bid.version
    }), 200


# 10. Получение списка ваших предложений
@api.route('/api/bids/my', methods=['GET'])
def list_user_bids():
    user_id = request.args.get('user_id')

    if not user_id:
        return jsonify({"reason": "Пользователь не найден"}), 400

    bids = Bid.query.filter_by(author_id=user_id).all()
    bids_list = [{"id": bid.id, "name": bid.name, "status": bid.status} for bid in bids]

    return jsonify(bids_list), 200


# 11. Получение списка предложений для тендера
@api.route('/api/bids/<string:tenderId>/list', methods=['GET'])
def list_bids_for_tender(tenderId):
    bids = Bid.query.filter_by(tender_id=tenderId).all()
    bids_list = [{"id": bid.id, "name": bid.name, "status": bid.status} for bid in bids]

    return jsonify(bids_list), 200


# 12. Получение текущего статуса предложения
@api.route('/api/bids/<string:bidId>/status', methods=['PUT'])
def update_bid_status(bidId):
    bid = Bid.query.get(bidId)

    if not bid:
        return jsonify({"reason": "Предложение не найдено"}), 404

    bid.status = request.args.get('status', bid.status)

    db.session.commit()

    return jsonify({"id": bid.id, "status": bid.status}), 200


# 13. Изменение статуса предложения
@api.route('/api/bids/<string:bidId>/edit', methods=['PATCH'])
def edit_bid(bidId):
    bid = Bid.query.get(bidId)

    if not bid:
        return jsonify({"reason": "Предложение не найдено"}), 404

    bid_data = request.json
    bid.name = bid_data.get('name', bid.name)
    bid.description = bid_data.get('description', bid.description)

    db.session.commit()

    return jsonify({"id": bid.id, "name": bid.name, "description": bid.description}), 200


# 14. Редактирование предложения
@api.route('/api/bids/<string:bidId>/submit_decision', methods=['PUT'])
def submit_bid_decision(bidId):
    bid = Bid.query.get(bidId)

    if not bid:
        return jsonify({"reason": "Предложение не найдено"}), 404

    description = request.args.get('description')

    if description not in ['Approved', 'Rejected']:
        return jsonify({"reason": "Некорректное решение"}), 400

    bid.description = description
    db.session.commit()

    return jsonify({"id": bid.id, "description": bid.decision}), 200


# 15. Отправка решения по предложению
@api.route('/bids/<uuid:bidId>/submit_decision', methods=['PUT'])
def subm_bid_decision(bidId):
    description = request.args.get('description')
    username = request.args.get('username')

    if not description or description not in ['Approved', 'Rejected']:
        return jsonify({"reason": "Некорректное решение"}), 400

    if not username:
        return jsonify({"reason": "Пользователь не существует или некорректен"}), 401

    bid = Bid.query.get(bidId)
    if not bid:
        return jsonify({"reason": "Предложение не найдено"}), 404

    bid.description = description
    db.session.commit()

    return jsonify({
        "id": str(bid.id),
        "name": bid.name,
        "status": bid.status,
        "authorType": bid.author_type,
        "authorId": str(bid.author_id),
        "version": bid.version,
        "createdAt": bid.created_at.isoformat()
    }), 200


# 16. Отправка отзыва по предложению
@api.route('/bids/<int:bidId>/feedback', methods=['PUT'])
def submit_bid_feedback(bidId):
    feedback_data = request.json
    bid = Bid.query.get(bidId)
    bid.feedback = feedback_data['feedback']
    db.session.commit()
    return jsonify({"id": bid.id, "feedback": bid.feedback}), 200


# 17. Откат версии предложения
@api.route('/bids/<int:bidId>/rollback/<int:version>', methods=['PUT'])
def rollback_bid(bidId, version):
    bid = Bid.query.get(bidId)
    bid.version = version
    db.session.commit()
    return jsonify({"id": bid.id, "version": version}), 200


# 18. Просмотр отзывов на прошлые предложения
@api.route('/bids/<int:tenderId>/reviews', methods=['GET'])
def get_tender_reviews(tenderId):
    reviews = Bid.query.filter_by(tender_id=tenderId).all()
    reviews_list = [{"id": review.id, "feedback": review.feedback} for review in reviews]
    return jsonify(reviews_list), 200
