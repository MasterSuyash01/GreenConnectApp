from flask import Flask, request, jsonify
from flask_restful import Api
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import check_password_hash
from werkzeug.security import generate_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask import abort
from sqlalchemy.orm import joinedload,relationship
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/suyashsrivastav/Downloads/GreenConnect-main 2/database.db'  # SQLite database file path
db = SQLAlchemy(app)
api = Api(app)

app.config['JWT_SECRET_KEY'] = 'your-secret-key'  # Change this to a secure secret key
jwt = JWTManager(app)

# Mock user data (replace this with your database logic)
users = [
    {'UserID': 1, 'Username': 'user1', 'Password': generate_password_hash('password1')},
    {'UserID': 2, 'Username': 'user2', 'Password': generate_password_hash('password2')},
    # Add more users as needed
]

# Define Models
class Users(db.Model):
    UserID = db.Column(db.Integer, primary_key=True)
    Username = db.Column(db.String(50), unique=True, nullable=False)
    Password = db.Column(db.String(50), nullable=False)
    Email = db.Column(db.String(120), nullable=False)
    Address = db.Column(db.String(200), nullable=False)

class Trees(db.Model):
    TreeID = db.Column(db.Integer, primary_key=True)
    TreeType = db.Column(db.String(50), nullable=False)
    TreeLocation = db.Column(db.String(100), nullable=False)
    DatePlanted = db.Column(db.String(20), nullable=False)
    Status = db.Column(db.String(20), nullable=False)
    adoptions = relationship('TreeAdoptions', backref='tree', lazy=True)

class TreeAdoptions(db.Model):
    AdoptionID = db.Column(db.Integer, primary_key=True)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    TreeID = db.Column(db.Integer, db.ForeignKey('trees.TreeID'), nullable=False)
    AdoptionDate = db.Column(db.String(20), nullable=False)
    


class ProduceDistribution(db.Model):
    DistributionID = db.Column(db.Integer, primary_key=True)
    TreeID = db.Column(db.Integer, db.ForeignKey('trees.TreeID'), nullable=False)
    UserID = db.Column(db.Integer, db.ForeignKey('users.UserID'), nullable=False)
    DistributionDate = db.Column(db.String(20), nullable=False)
    SharePercentage = db.Column(db.Numeric, nullable=False)


# Authentication endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # Mock database check (replace this with your database logic)
    user = next((user for user in users if user['Username'] == username), None)

    if user and check_password_hash(user['Password'], password):
        access_token = create_access_token(identity=user['UserID'])
        return jsonify(access_token=access_token), 200
    else:
        return jsonify(message='Invalid credentials'), 401

# Protected route example
@app.route('/protected', methods=['GET'])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    # You can use the current_user_id to fetch user-specific data from your database
    return jsonify(logged_in_as=current_user_id), 200


from flask_restful import Resource, reqparse

class TreeAdoptionResource(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_id', type=int, required=True, help='User ID is required')
        parser.add_argument('tree_id', type=int, required=True, help='Tree ID is required')
        args = parser.parse_args()

        user_id = args['user_id']
        tree_id = args['tree_id']
        print(f"User ID: {user_id}, Tree ID: {tree_id}")
        # Check if the user and tree exist in the database
        user = Users.query.get(user_id)
        tree = Trees.query.get(tree_id)
        print(f"User: {user}, Tree: {tree}")
        if not user:
            abort(404, description='User not found')

        if not tree:
            abort(404, description='Tree not found')

        # Check if the tree is available for adoption (status can be 'available')
        if tree.Status != 'available':
            abort(400, description='Tree is not available for adoption')

        # Update the status of the tree to 'adopted'
        tree.Status = 'adopted'
        
        # Record the tree adoption in the TreeAdoptions table
        adoption = TreeAdoptions(UserID=user_id, TreeID=tree_id, AdoptionDate='current_date')
        db.session.add(adoption)
        db.session.commit()

        return {'message': 'Tree adopted successfully'}, 201

api.add_resource(TreeAdoptionResource, '/tree/adoption')


class TreeResource(Resource):
    def get(self):
        trees = Trees.query.options(joinedload(Trees.adoptions)).all()
        tree_list = []
        for tree in trees:
            tree_dict = {'TreeID': tree.TreeID, 'TreeType': tree.TreeType, 'TreeLocation': tree.TreeLocation, 'DatePlanted': tree.DatePlanted, 'Status': tree.Status}
            if tree.adoptions:
                tree_dict['adoptions'] = [{'AdoptionID': adoption.AdoptionID, 'UserID': adoption.UserID, 'AdoptionDate': adoption.AdoptionDate} for adoption in tree.adoptions]
            tree_list.append(tree_dict)
        return {'trees': tree_list}, 200

    
api.add_resource(TreeResource, '/tree')


if __name__ == '__main__':
    app.run(debug=True)
