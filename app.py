from flask import Flask,render_template,redirect,request 
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime;

#my app
app =Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///project.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False
db =SQLAlchemy(app);

#Table /Modal
class Task(db.Model):
    id=db.Column(db.Integer, primary_key=True)
    content=db.Column(db.String(100),nullable=False)
    complete=db.Column(db.Integer,default=0)
    created=db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__ (self)->str:
        return f"Task {self.id}"
with app.app_context():
    db.create_all()
#home page
@app.route("/", methods=["POST", "GET"]) 
def index():
    if request.method == "POST": 
        current_task = request.form['contant']
        new_task = Task(content=current_task)
        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as error:
            print (f"Erron:{error}")
            return f"Error: {error}"
    else:
        tasks = Task.query.order_by(Task.created).all()   
        return render_template('index.html',tasks=tasks)


#Delete tasks
@app.route('/delete/<int:id>')
def delete(id:int):
    delete_task = Task.query.get_or_404(id)
    try:
        db.session.delete(delete_task)
        db.session.commit()
        return redirect('/')
    except Exception as error:
        return f"Error deleting task {error}"


#Edit tasks or update tasks

@app.route('/edit/<int:id>',methods=['POST','GET'])
def edit(id:int):
    task = Task.query.get_or_404(id)
    if request.method == 'POST':
        task.content = request.form['content']
        try:
            db.session.commit()
            return redirect('/')
        except Exception as error:
            return f"Error updating task {error}"
    else:     
        return  render_template('edit.html',task=task)


    




if __name__=="__main__":
   
    app.run(debug=True)