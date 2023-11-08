from flask import Flask, make_response, request
from gauth_python.requests import token_issuance,token_reissuance
import modules
import os
from bson import json_util

app = Flask(__name__)

#return 대상을 함수로 변경하여금 응답 값을 유연하게 변경할 수 있도록 해야함, 리팩토링 필요

#account
@app.route('/api/users/login', methods=['POST'])
def getCodeAndGenToken():
    params = request.get_json()
    user_token = token_issuance(
        code = params['client_code'],
        clientId = os.environ.get('gauth_clientId'),
        clientSecret = os.environ.get('gauth_clientSecret'),
        redirectUri = os.environ.get('gauth_redirectUri')
    )
    if ((modules.getUserIdFromDb(modules.getUserEmail(user_token))) == None):
        client_id = modules.writeUserDb(user_token)
        return json_util.dumps((client_id, user_token,  False), default=json_util.default)
    client_id = modules.getUserIdFromDb
    return json_util.dumps((client_id, user_token, True), default=json_util.default)

@app.route('/api/users/token', methods=['POST'])
def getUserToken():
    params = request.get_json()
    return_token = token_reissuance(
        refreshToken = params['client_refresh_token']
    )
    return json_util.dumps(return_token, default=json_util.default)

@app.route('/api/users/nickname', methods=['POST'])
def writeUserNickname():
    params = request.get_json()
    findUserByEmail = modules.getUserEmail(params['user_token'])
    modules.changeUserNickname(findUserByEmail,params['nickname'])
    return make_response("status 200", 200)

@app.route('/api/user/<clientId>', methods=['GET'])
def getUserInfo(clientId):
    result = list(modules.getUserInfo(clientId))
    return json_util.dumps(result, default=json_util.default)

@app.route('/api/user/<clientId>/pins', methods=['GET'])
def getOwnPins(clientId):
    result = list(modules.getUserBoardDb(clientId))
    return json_util.dumps(result, default=json_util.default)

@app.route('/api/user/<clientId>/likes', methods=['GET'])
def getLikedPosting(clientId):
    result = list(modules.getLikedPostDb(clientId))
    return json_util.dumps(result, default=json_util.default)

#pins (board)
@app.route('/api/pins', methods=['POST'])
def writeUserPins():
    params = request.get_json()
    return json_util.dumps(modules.writeBoardDb(params['doc'], params['clientId'], "board", "0", "0") == True)

@app.route('/api/pins', methods=['GET'])
def getBoardPins():
    result = list(modules.getBoardDb())
    return json_util.dumps(result, default=json_util.default)

@app.route('/api/pins/<pinId>', methods=['GET'])
def getUserPins(pinId):
    result = list(modules.getPostDb(post_id=pinId))
    return json_util.dumps(result, default=json_util.default)

@app.route('/api/pins/<pinId>', methods=['PUT'])
def putPostEdit(pinId):
    data = request.get_json()
    if (modules.writeBoardDb(data.doc, data.clientId, data.type, data.post_id, pinId) == False):
        return make_response("status 400", 400)
    return make_response("status 200", 200)

@app.route('/api/pins/search', methods=['GET'])
def getUserSearchPins():
    keywords = request.args.get('keywords')
    result = list(modules.getPostDb(keyword=keywords))
    return json_util.dumps(list(result), default=json_util.default)

# @app.route('/api/pins/<pinId>/likes', methods=['POST'])
# def postPostLikes(pinId):
#     clientId = request.args.get('clientId')
#     if (modules.putPostLikeDb(pinId,clientId) == False):
#         return make_response("status 400", 400)
#     return make_response("status 200", 200)

# @app.route('/api/pins/<pinId>/dislikes', methods=['POST'])
# def postPostdisLikes(pinId):
#     clientId = request.args.get('clientId')
#     if (modules.deletePostLikeDb(pinId,clientId) == False):
#         return make_response("status 400", 400)
#     return make_response("status 200", 200)


@app.route('/api/pins/<pinId>', methods=['DELETE'])
def deletePostLikes(pinId):
    modules.deletePostDb(pinId)
    return make_response("status 200", 200)

@app.route('/api/images', methods=['POST'])
def upload_profile_picture():
    params = request.get_json()
    modules.uploadFile(request,params['clientId'])

if __name__ == '__main__':
    app.run(debug=True)
