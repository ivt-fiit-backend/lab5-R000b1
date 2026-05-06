import json
from flask import Flask, abort, jsonify, request
from flask_restx import Api, Namespace, Resource, fields

PAGE_SIZE = 25

app = Flask(__name__)
api = Api(app)

with open('awards.json', encoding='utf-8') as f:
    awards = json.load(f)

with open('laureats.json', encoding='utf-8') as f:
    laureats = json.load(f)


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


v2_ns = Namespace('v2', description='Laureates API')

laureate_model = v2_ns.model('Laureate', {
    'id': fields.String,
    'knownName': fields.Raw,
    'givenName': fields.Raw,
    'familyName': fields.Raw,
    'gender': fields.String,
    'birth': fields.Raw
})


@v2_ns.route('/laureats/')
class LaureatesList(Resource):
    @v2_ns.doc('list_laureates')
    def get(self):
        try:
            p = int(request.args.get('p', 0))
            if p < 0:
                raise ValueError
        except ValueError:
            abort(400)

        page_size = 25
        start = p * page_size
        end = start + page_size
        page = laureats[start:end]

        return {
            'page': p,
            'count_on_page': page_size,
            'total': len(laureats),
            'items': page
        }


@v2_ns.route('/laureat/<int:id>')
class LaureateResource(Resource):
    @v2_ns.doc('get_laureate')
    def get(self, id):
        laureate = next(
            (item for item in laureats
             if str(item.get('id')) == str(id)),
            None
        )
        if laureate is None:
            abort(404)
        return laureate


api.add_namespace(v2_ns)

if __name__ == '__main__':
    app.run(debug=True)