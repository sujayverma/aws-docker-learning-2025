from datetime import datetime, timedelta, timezone
from libs.db import db as Db
class CreateActivity:
  def run(message, user_handle, ttl):
    model = {
      'errors': None,
      'data': None
    }

    now = datetime.now(timezone.utc).astimezone()
    

    if (ttl == '30-days'):
      ttl_offset = timedelta(days=30) 
    elif (ttl == '7-days'):
      ttl_offset = timedelta(days=7) 
    elif (ttl == '3-days'):
      ttl_offset = timedelta(days=3) 
    elif (ttl == '1-day'):
      ttl_offset = timedelta(days=1) 
    elif (ttl == '12-hours'):
      ttl_offset = timedelta(hours=12) 
    elif (ttl == '3-hours'):
      ttl_offset = timedelta(hours=3) 
    elif (ttl == '1-hour'):
      ttl_offset = timedelta(hours=1) 
    else:
      model['errors'] = ['ttl_blank']

    if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['user_handle_blank']

    if message == None or len(message) < 1:
      model['errors'] = ['message_blank'] 
    elif len(message) > 280:
      model['errors'] = ['message_exceed_max_chars'] 

    if model['errors']:
      model['data'] = {
        'handle':  user_handle,
        'message': message
      }   
    else:
      expire_at = (now + ttl_offset)
      print('User handle: ', user_handle)
      print('Message: ', message)
      print('Expire at: ', expire_at)
      uuid = CreateActivity.create_activity(user_handle, message, expire_at)
      object_json = CreateActivity.query_object_activity(uuid)
      model['data'] = object_json
    return model
  
  def create_activity(handle, message, expires_at):
    sql = Db.template('activities','create_activities')
    try:
      uuid = Db.query_commit(sql, {
        'handle': handle,
        'message': message,
        'expires_at': expires_at
      })
      return uuid
    except (Exception) as error:
      Db.print_sql_err(error)
    # finally:
    #   if conn is not None:
    #     cur.close()
    #     conn.close()
  
  def query_object_activity(uuid):
    sql = Db.template('activities','query_object_activity')
    
    return Db.query_object_json(sql, {
      'uuid': uuid
    })

    
  

   