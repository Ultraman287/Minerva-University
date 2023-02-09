from web import create_app
import os
from dotenv import load_dotenv

load_dotenv()

app = create_app()

if __name__== '__main__':
    app.run(debug=True, host=os.environ['HOST'], port=os.environ['PORT'])
