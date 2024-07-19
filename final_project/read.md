
python -m venv photoshare
python.exe -m pip install --upgrade pip


.\activate
source bin/activate

pip install -r requirements.txt


Remember to add .env to your .gitignore file to prevent it from being committed to version control. You might want to include a .env.example file in your repository with dummy values as a template for other developers or for deployment.


uvicorn app.main:app --reload

http://127.0.0.1:8000/docs