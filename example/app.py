import os
import datetime

from flask import Flask, render_template
from flask_mongoengine import MongoEngine

from flask_tus import FlaskTus
from flask_tus.models import MongoengineModel


app = Flask(__name__)

app.config.update({
    'TUS_UPLOAD_DIR': os.getcwd() + '/example/uploads',
    'TUS_EXPIRATION': datetime.timedelta(days=1),
    'MONGODB_SETTINGS': {
        'db': os.environ.get('DB_NAME', 'tus_dev'),
        'host': os.environ.get('DB_HOST', 'mongodb'),
        'port': int(os.environ.get('DB_PORT', 27017)),
    }
})

class FlaskTusExtended(FlaskTus):
    def on_complete(self,upload_uuid=None):
        if(upload_uuid==None):
            return
        else:
            upload = self.repo.find_by(upload_uuid=upload_uuid)[0]
            uuid = upload.upload_uuid
            path = upload.path
            filename = upload.filename
            # need to clean the file, make sure it's ok for filesystem storage
            correct_filename = secure_filename(filename)
            p = Path(path)
            # reconstruct the path now
            full_path = p.root
            for a in p.parts[:-1]: full_path = os.path.join(full_path,a)
            #create directory structure if not already exists
            Path(full_path).mkdir(parents=True, exist_ok=True)
            # change the name of the file to the original filename
            new_path = os.path.join(full_path, correct_filename)
            # do the renaming and move in 1
            Path(path).rename(new_path)

db = MongoEngine(app)
flask_tus = FlaskTusExtended(app, model=MongoengineModel, db=db)


@app.route('/')
def index():
    return render_template("index.html")


if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)
