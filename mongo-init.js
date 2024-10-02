var cfg = {
  "_id": "rs0",
  "version": 1,
  "members": [
    {
      "_id": 0,
      "host": "localhost:27017",
      "priority": 1
    }
  ]
};
rs.initiate(cfg);

use('rainfall');
db.createCollection('users');
db.getCollection('users').insertOne({
  "_id": "guest",
  "email": "guest",
  "username": "guest",
  "password": "$2y$10$LxUpriVaGd4a4EecnbM0..14hVhjxp9wgkaBg/J0mSIysAKnnslKu",
  "organization": "Unicam"
});