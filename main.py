from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
import os 
from wtforms.validators import InputRequired
import io
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import base64

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/files'
app.config["data"] = "./info"

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit  = SubmitField("Upload File")

@app.route('/', methods=["GET","POST"])
@app.route('/home', methods=["GET","POST"])

def home():
    path_logo = "/static/logoweb.png"
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)),app.config['UPLOAD_FOLDER'],secure_filename(file.filename)))
        return "File has been uploaded."
    return render_template('index.html',logo=path_logo, form=form)

@app.route('/columnas', methods=['POST'])
def columnas():
    path_logo = "/static/logoweb.png"
    if request.method == 'POST':
        da = request.files['file']
        filename = secure_filename(da.filename)
        da.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
        df = pd.read_csv('./static/files/{}'.format(filename))
        columnas = { 
            'columnas': df.columns.tolist(),
            'filename': filename
        }

        
        return render_template('showCSV.html', columnas=columnas,logo=path_logo)   


@app.route('/graphic', methods=['POST'])
def graphic():
    path_logo = "/static/logoweb.png"
    if request.method == 'POST':
        columna = request.form['columna']
        columna1 = request.form['columna1']
        grafica = request.form['tipo']
        filename = request.form['filename']
        data= pd.read_csv('./static/files/{}'.format(filename), usecols = [columna,columna1])
        print(columna +" COLUMNA "+ columna1)
        # data.columns = ['c1','c2']
        df = pd.read_csv('./static/files/{}'.format(filename))[columna]
        df1= pd.read_csv('./static/files/{}'.format(filename))[columna1]
        
        plt.clf() 
        if grafica == 'Scatter':
            img = io.BytesIO()
            plt.title("Grafica por: "+columna +" y "+ columna1)
            plt.scatter(df,df1,color= 'b')
            plt.xlabel(columna)
            plt.ylabel(columna1)
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('graphic.html', imagen={ 'imagen': plot_url },logo=path_logo)
        elif grafica == 'lineal':
            print('lineas')
            img = io.BytesIO()
            plt.title("Grafica por: "+columna +" y "+ columna1)
            # for x in len(df1.unique().tolist()):
            #     data.c1[data.c2 == x].plot()
            # plt.legend(df1.unique().tolist())
            # plt.legend(columna,columna1)
            data.plot()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('graphic.html', imagen={ 'imagen': plot_url },logo=path_logo)
        elif grafica == 'barras':
            img = io.BytesIO()
            plt.title("Grafica por: "+columna)
            df.value_counts().plot(kind='bar')
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('graphic.html', imagen={ 'imagen': plot_url },logo=path_logo)
        elif grafica == 'barrasY':
            img = io.BytesIO()
            plt.title("Grafica por: "+columna)
            df.value_counts().plot(kind='barh')
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('graphic.html', imagen={ 'imagen': plot_url },logo=path_logo)
        elif grafica == 'pie':
            img = io.BytesIO()
            plt.title("Grafica por: "+columna)
            plt.pie(df.value_counts(),labels=df.unique().tolist(),autopct='%1.1f%%')
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('graphic.html', imagen={ 'imagen': plot_url },logo=path_logo)
        else:
            img = io.BytesIO()
            
            datos = df.head(10).tolist()
            for i in range(len(datos)):
                plt.bar(i, datos[i], align = 'center')
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            return render_template('graphic.html', imagen={ 'imagen': plot_url },logo=path_logo)

if __name__=='__main__':
    app.run(debug=True)