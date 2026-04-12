import json
from flask import Flask, abort, jsonify, request
from flask_restx import Api, Resource, fields

PAGE_SIZE = 25

app = Flask(__name__)
api = Api(app, version='1.0', title='Nobel API', description='API for awards and laureates')

with open('awards.json', encoding='utf-8') as f:
    awards = json.load(f)

with open('laureats.json', encoding='utf-8') as f:
    laureats = json.load(f)

laureate_model = api.model('Laureate', {
    'id': fields.String(description='ID лауреата'),
    'knownName': fields.String(description='Известное имя'),
    'givenName': fields.String(description='Имя'),
    'familyName': fields.String(description='Фамилия'),
    'fullName': fields.String(description='Полное имя'),
    'gender': fields.String(description='Пол'),
    'birth': fields.String(description='Дата рождения'),
    'death': fields.String(description='Дата смерти'),
    'nobelPrizes': fields.List(fields.String, description='Список премий')
})

@app.route("/api/v1/awards/")
def awards_list():
    try:
        p = int(request.args.get('p', 0))
        if p < 0:
            raise ValueError
    except ValueError:
        return abort(400)
    page = awards[p * 50:(p + 1)*50]
    return jsonify({
        'page': p,
        'count_on_page': PAGE_SIZE,
        'total': len(awards),
        'items': page,
    })

@app.route("/api/v1/award/<int:pk>/")
def award_object(pk):
    if 0 <= pk < len(awards):
        return jsonify(awards[pk])
    else:
        abort(404)

@api.route('/v2/laureats/')
class LaureatesList(Resource):
    @api.doc('get_laureates_list')
    @api.marshal_list_with(laureate_model)
    def get(self):
        return laureates, 200

@api.route('/v2/laureat/<string:id>/')
class LaureateItem(Resource):
    @api.doc('get_laureate')
    @api.marshal_with(laureate_model)
    def get(self, id):
        for laureate in laureates:
            if str(laureate['id']) == str(id):
                return laureate, 200
        abort(404, message=f"Лауреат с id {id} не найден")

if __name__ == '__main__':
    app.run(debug=True)