from gauth_python.requests import user_info
from pymongo import MongoClient
import datetime, secrets, os
from bson.objectid import ObjectId

client = MongoClient(os.environ.get('MONGO_URL'))
db = client['event']
nowtime = datetime.datetime.now()

#account
def getUserEmail(user_token):
    UserInfo = user_info(
        accessToken = user_token
    )
    return UserInfo.email

def writeUserDb(user_token):
    UserInfo = user_info(
        accessToken = user_token
    )
    doc = {
        'clientId' : secrets.token_hex(nbytes=40),
        'email' : UserInfo.email,
        'profile_image' : UserInfo.profileUrl,
        'liked_post' : [],
        'created_at': datetime.datetime.utcnow()
    }
    db.users.insert_one(doc)
    return doc.clientId

def changeUserNickname(user_email,nickname):
    db.users.update_one({'email':f'{user_email}'},{'$set':{'nickname':f'{nickname}'}})
    return True

def getUserIdFromDb(user_email):
    user_info = db.userinfo.find({'user_email':user_email})
    return user_info['clientId']

def getUserInfo(clientId):
    user_info = db.users.find_one({'clientId':f"{clientId}"})
    return user_info

def checkUserExists(userId):
    user_info = db.userinfo.find({'clientId':userId})
    if user_info != None:
        return True
    else:
        return False 
    
def getLikedPostDb(clientId):
    if (checkUserExists(clientId) == False):
        return False
    doc = db.userinfo.find({'clientId':clientId})
    return doc['liked_post']

# board

def checkownPost(clientId, post_id):
    if (checkUserExists(clientId) == False):
        return False
    doc = db.globalboard.find_one({'_id':ObjectId(f'{post_id}')})
    if doc['clientId'] == clientId:
        return True
    else:
        return False

def getUserBoardDb(clientId):
    if (checkUserExists(clientId) == False):
        return False
    user_info = db.globalboard.find({'clientId':clientId})
    return user_info

def putPostLikeDb(post_id, clientId):
    if (checkUserExists(clientId) == False and checkownPost(clientId,post_id)):
        return False
    doc = db.globalboard.find_one_and_update({'post_id':post_id},{'$inc':{ 'post_like': 1}})
    db.userinfo.update_one({'clientId':clientId},{'$push':{'liked_post':post_id}})
    return True

def deletePostLikeDb(post_id, clientId):
    if (checkUserExists(clientId) == False and checkownPost(clientId,post_id)):
        return False
    doc = db.globalboard.find_one_and_update({'post_id':post_id},{'$inc':{ 'post_like': -1}})
    client = db.userinfo.update_one({'clientId':clientId},{'$pull':{'liked_post':post_id}})
    if ((doc | client) == None |"null"):
        return False
    return True

def getBoardDb():
    board_doc = db.globalboard.find({})
    return board_doc

def getPostDb(keyword=None, post_id=None):
    board_doc = db.globalboard.find_one({'_id':ObjectId(f'{post_id}')}) if post_id is not None else db.globalboard.find({'detail': {'$regex': f'{keyword}'}})
    return board_doc

def deletePostDb(post_id,clientId):
    if (checkownPost(clientId,post_id) == True):
        board_doc = db.globalboard.find_one_and_delete({'_id':ObjectId(f'{post_id}')})
    elif (board_doc == None |"null"):
        return False
    else:
        return False
    return True

def writeBoardDb(doc, clientId, type, post_id, ref_id):
    if checkUserExists(client) == False:
        return False
    doc = {
            'date' : nowtime.year+nowtime.month+nowtime.day,
            'detail' : doc,
            'clientId': clientId,
            'like_count': 0
    }
    if type == "comment":
        doc['post_id'] = post_id
        db.globalboardcomment.insert_one(doc)
    elif type == "recomment":
        doc['post_id'] = post_id
        doc['ref_comment_id'] = ref_id
        db.globalboardrecomment.insert_one(doc)
    elif type == "board":
        db.globalboard.insert_one(doc)
    elif type == "update":
        post_id = ref_id
        db.globalboard.update_one({'_id':ObjectId(f'{post_id}')},{'$set':{'detail':f'{doc}'}})

    return True

# def getCommentDb(post_id):
#     comment_doc = db.globalboardcomment.find({'post_id':post_id}) + db.globalboardrecomment.find({'post_id':post_id})
#     return comment_doc

# def getCommentDb(post_id):
#     comment_doc = db.globalboardcomment.find({'post_id':post_id}) + db.globalboardrecomment.find({'post_id':post_id})
#     return comment_doc

# def getUserCommentDb(clientId):
#     user_info = db.globalboardrecomment.find({'clientId':clientId}) + db.globalboardcomment.find({'clientId':clientId})
#     return user_info

# --
