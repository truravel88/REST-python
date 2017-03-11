from flask import Flask, request
from flask_restful import abort, Api, Resource
import sys,os,time
import sqlobject
import md5 # inseguro pero es un ejemplo demostrativo. 
#from myapp.Contact import Contact

app = Flask(__name__)
api = Api(app)


def IsValid(token):
	query = TokenObj.q.token==token
	if TokenObj.select(query).count() == 1:
		return True
	else:
		return False


def get_elements(data):
	ret = dict()
	try:
		elements = data.split('&')
		for tupla in elements:
			datos = tupla.split('=')
			if datos[1]: 
				ret[datos[0]]=datos[1]
		return ret
	except Exception as e:
		return ret


class UserObj(sqlobject.SQLObject):
	name = sqlobject.StringCol(length=40, unique=True)

class TokenObj(sqlobject.SQLObject):
	token = sqlobject.StringCol(length=256, unique=True)

class ContactObj(sqlobject.SQLObject):
	data = sqlobject.StringCol(length=256, unique=True)
	datatype = sqlobject.StringCol(length=60, unique=True)
	user = sqlobject.IntCol()


class User(Resource):

	def get(self,data):
		try:
			args = get_elements(data)
			if IsValid(args['token']):
				if args['name'] is not None:
					query = UserObj.q.name==args['name']
					user = UserObj.select(query)[0]
					if UserObj.select(query).count() == 0:
						return  {'Error':'Not Found'}, 404
					return {'id': user.id,'name' : user.name},
				else:
					lista = {}
					for user in UserObj.select():
						lista[user.id] = user.name
					return lista
			else:
				return {'Error':'Invalid Token'}, 401
		except Exception as e:
			return {'Error':'Bad Request'}, 400


	def post(self,data):
		try:
			args = get_elements(data)
			if IsValid(args['token']):
				#
				return {'id': 'Hello world'}, 201
			else:
				return {'Error':'Invalid Token'}, 401
		except Exception as e:
			return {'Error':'Bad Request'}, 400



	def delete(self,data):
		try:
			args = get_elements(data)
			if IsValid(args['token']):
				if args['name'] is not None:
					query = UserObj.q.name==args['name']
					UserObj.select(query)
					UserObj.delete(1)
				return {'message': 'Done'},
			else:
				return {'Error':'Invalid Token'}, 401
		except Exception as e:
			return {'Error':'Bad Request'}, 400


	def put(self,data):
		try:
			args = get_elements(data)
			if IsValid(args['token']):
				if args['name'] is not None:
					UserObj(name=args['name'])
				return {'id': args['name']}, 201
			else:
				return {'Error':'Invalid Token'}, 401
		except Exception as e:
			return {'Error':'Bad Request'}, 400



# Set token, only demostration
class Token(Resource):

	def get(self):
		token = md5.new( str(time.time())).hexdigest()
		TokenObj(token=token)
		return {'Token': token }
	
	def put(self):
		return  {'Error':'Forbidden'}, 403

	def post(self):
		return  {'Error':'Forbidden'}, 403

	def delete(self):
		return  {'Error':'Forbidden'}, 403



class Contact(Resource):

	def get(self,data):
		return data

	def put(self,data):
		args = get_elements(data)
		if IsValid(args['token']):
			if args['user'] is not None:
				query = UserObj.q.id==args['user']
				if UserObj.select(query).count() != 0:
					user = UserObj.select(query)[0]
				else:
					return  {'Error':args['user']}, 404
			if args['data'] is not None and args['datatype'] is not None and user.id > 0:
				ContactObj(data=args['data'],user=user.id,datatype=args['datatype']), 201
			return {'id': 'Hello world'},
		else:
			return {'Error':'Invalid Token'}, 401
		return json



api.add_resource(Contact, '/contact', '/contact/<string:data>')
api.add_resource(User, '/user', '/user/<string:data>')
api.add_resource(Token, '/gettoken','/gettoken/')


def db_open(filename):
    create = False
    filename = os.path.abspath(filename)
    string_conn = 'sqlite:' + filename
    conn = sqlobject.connectionForURI(string_conn)
    sqlobject.sqlhub.processConnection = conn
    UserObj.createTable(ifNotExists=True)
    TokenObj.createTable(ifNotExists=True)
    ContactObj.createTable(ifNotExists=True)



def main():
	db_open("myapp.db")
	app.run(debug=True, host='localhost', port=8080)

if __name__ == '__main__':
	main()


