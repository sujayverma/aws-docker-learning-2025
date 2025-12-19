SELECT 
    activities.uuid, 
    users.display_name,
    users.handle, 
    activities.message, 
    activities.expires_at, 
    activities.created_at
FROM activities LEFT JOIN users ON users.uuid = activities.user_uuid 
WHERE activities.uuid = %(uuid)s