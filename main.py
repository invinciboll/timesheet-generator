from flask import Flask, render_template, request, send_file, send_from_directory
from tinydb import TinyDB
from run import generate_file

app = Flask(__name__)

# Initialize TinyDB with the JSON file
db = TinyDB('members.json')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        month = request.form.get('month')
        year = request.form.get('year')
        pdf_output = generate_file(int(month), int(year))
        return send_file(pdf_output, as_attachment=True, download_name='generated_timesheets.pdf', mimetype='application/pdf')

    members = db.all()
    return render_template('index.html', members=members)

@app.route('/add-member', methods=['POST'])
def add_member():
    db.insert({'firstname': request.form.get('firstname'), 'lastname': request.form.get('lastname'), 'persnr': request.form.get('persnr')})
    new_member = db.all()[-1]
    return render_template('member_row.html', member=new_member)

@app.route('/delete-member/<int:doc_id>', methods=['DELETE'])
def delete_member(doc_id):
    member = db.get(doc_id=doc_id)
    if member:
        db.remove(doc_ids=[doc_id])
        return '', 200  # No content needed, 204 indicates successful deletion
    else:
        return 'ID not found', 404


if __name__ == '__main__':
    app.run(debug=True)
