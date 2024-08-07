import hashlib
import time

from flask import Flask,render_template,redirect, request, session,send_file
from flask_mysqldb import MySQL
import MySQLdb.cursors
import os
import utils.rsa as rsaalg
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

app = Flask(__name__)

# configurasi database
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'bmt'
app.secret_key = 'supersecretkey'

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static\\images\\')

mysql = MySQL(app)

@app.route('/', methods=['GET'])
def index():
    if 'loggedin' in session:
        title = 'Dashboard'
        key_perempuan = request.args.get('anggotaperempuan', default='')
        key_lakilaki = request.args.get('anggotalakilaki', default='')
        if key_perempuan != '':
            cur = mysql.connection.cursor()
            print(key_perempuan)
            cur.execute("SELECT * FROM members where jk=0 and nama Like '%"+str(key_perempuan+"%' ORDER BY id DESC LIMIT 5"))
            mysql.connection.commit()
            datasatu = cur.fetchall()

            cur.execute("SELECT * FROM members WHERE jk=1 ORDER BY id DESC LIMIT 5")
            mysql.connection.commit()
            datadua = cur.fetchall()
        elif key_lakilaki != '':
            cur = mysql.connection.cursor()
            cur.execute('''SELECT * FROM members where jk=0 ORDER BY id DESC LIMIT 5''')
            mysql.connection.commit()
            datasatu = cur.fetchall()

            cur.execute("SELECT * FROM members WHERE jk=1 and nama Like '%"+str(key_lakilaki+"%' ORDER BY id DESC LIMIT 5"))
            mysql.connection.commit()
            datadua = cur.fetchall()
        else:
            cur = mysql.connection.cursor()
            cur.execute('''SELECT * FROM members where jk=0 ORDER BY id DESC LIMIT 5''')
            mysql.connection.commit()
            datasatu = cur.fetchall()

            cur.execute('''SELECT * FROM members WHERE jk=1 ORDER BY id DESC LIMIT 5''')
            mysql.connection.commit()
            datadua = cur.fetchall()
        return render_template('pages/index.html', title=title, dataperempuan=datasatu, datalaki = datadua)
        return render_template('pages/index.html', title=title, dataperempuan=datasatu, datalaki = datadua)
    else:
        return redirect('/login')

@app.route('/download-file/<int:id>', methods=['GET'])
def downloadFile(id):
    data =[]
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM members WHERE id = " + str(id))
    mysql.connection.commit()
    result = cur.fetchall()
    print(result)
    for res in result:
        saveFile('static/images/suami/'+res[5], res[5])
        print('hit1')
        saveFile('static/images/istri/'+res[6], res[6])
        print('hit2')
        saveFile('static/images/ktp/suami/'+res[7], res[7])
        print('hit3')
        saveFile('static/images/ktp/istri/'+res[8], res[8])
        print('hit4')
        saveFile('static/images/kk/'+res[9], res[9])
        print('hit5')
        saveFile('static/images/kendaraan/'+res[10], res[10])
        print('hit6')
        saveFile('static/images/sertifikat_tanah/'+res[11], res[11])
        print('hit7')
        saveFile('static/images/stnk/'+res[12], res[12])
        print('hit8')
        saveFile('static/images/bpkb/'+res[13], res[13])
        print('hit9')
        saveFile('static/images/rmh/'+res[15], res[15])
        print('hit10')
    return 'ok'

def saveFile(url, name):
    return send_file(url, as_attachment=True, download_name = name)

@app.route('/tambah-anggota', methods=['GET','POST'])
def addAnggota():
    if 'loggedin' in session:
        title = 'Halaman Tambah Anggota'
        if request.method == 'GET':
            return render_template('pages/addMember.html', title=title)
        elif request.method == 'POST':
            # validationInput
            error = {}
            data = {
                'nama': '',
                'ttl' : '',
                'tlp' : '',
                'alamat' : '',
                'ft_sm' : '',
                'ft_is' : '',
                'ft_ktp_sm' : '',
                'ft_ktp_is' : '',
                'ft_kk' : '',
                'ft_knd' : '',
                'ft_srf_tnh' : '',
                'ft_stnk' : '',
                'ft_bpkb' : '',
                'jk' : '',
                'ft_rmh': '',
            }
            sukses = 0
            if request.form.get('nama') == '':
                error['nama'] = 'Isian Nama Anggota Harus Diisi !'
            else:
                error['nama'] = ''
                data['nama'] = request.form.get('nama')
            if request.form.get('jk') != '0' and request.form.get('jk') != '1':
                error['jk'] = 'Jenis Kelamin Tidak Valid !'
            else:
                error['jk'] = ''
                data['jk'] = request.form.get('jk')
            if request.form.get('tlp') == '':
                error['tlp'] = 'Isian Nomor Telepon Anggota Harus Diisi !'
            else:
                error['tlp'] = ''
                data['tlp'] = request.form.get('tlp')
            if request.form.get('ttl') == '':
                error['ttl'] = 'Isian Tempat Tanggal Lahir Anggota Harus Diisi !'
            else:
                error['ttl'] = ''
                data['ttl'] = request.form.get('ttl')
            if request.form.get('alamat') == '':
                error['alamat'] = 'Isian Alamat Anggota Harus Diisi !'
            else:
                error['alamat'] = ''
                data['alamat'] = request.form.get('alamat')
            if request.form.get('ft_sm') == '':
                error['ft_sm'] = 'Isian Foto Suami Harus Diisi !'
            else:
                error['ft_sm'] = ''
                data['ft_sm'] = request.form.get('ft_sm')
            if request.form.get('ft_is') == '':
                error['ft_is'] = 'Isian Foto Istri Harus Diisi !'
            else:
                error['ft_is'] = ''
                data['ft_is'] = request.form.get('ft_is')
            if request.form.get('ft_ktp_sm') == '':
                error['ft_ktp_sm'] = 'Isian Foto KTP Suami Harus Diisi !'
            else:
                error['ft_ktp_sm'] = ''
                data['ft_ktp_sm'] = request.form.get('ft_ktp_sm')
            if request.form.get('ft_ktp_is') == '':
                error['ft_ktp_is'] = 'Isian Foto KTP Istri Harus Diisi !'
            else:
                error['ft_ktp_is'] = ''
                data['ft_ktp_is'] = request.form.get('ft_ktp_is')
            if request.form.get('ft_kk') == '':
                error['ft_kk'] = 'Isian Foto KK Harus Diisi !'
            else:
                error['ft_kk'] = ''
                data['ft_kk'] = request.form.get('ft_kk')
            if request.form.get('ft_knd') == '':
                error['ft_knd'] = 'Isian Foto Kendaraan Harus Diisi !'
            else:
                error['ft_knd'] = ''
                data['ft_knd'] = request.form.get('ft_knd')
            if request.form.get('ft_srf_tnh') == '':
                error['ft_srf_tnh'] = 'Isian Foto Sertifikat Tanah Harus Diisi !'
            else:
                error['ft_srf_tnh'] = ''
                data['ft_srf_tnh'] = request.form.get('ft_srf_tnh')
            if request.form.get('ft_stnk') == '':
                error['ft_stnk'] = 'Isian Foto STNK Harus Diisi !'
            else:
                error['ft_stnk'] = ''
                data['ft_stnk'] = request.form.get('ft_stnk')
            if request.form.get('ft_bpkb') == '':
                error['ft_bpkb'] = 'Isian Foto BPKB Harus Diisi !'
            else:
                error['ft_bpkb'] = ''
                data['ft_bpkb'] = request.form.get('ft_bpkb')
            if request.form.get('ft_rmh') == '':
                error['ft_rmh'] = 'Isian Foto Rumah Anggota Harus Diisi !'
            else:
                error['ft_rmh'] = ''
                data['ft_rmh'] = request.form.get('ft_rmh')


            x = list(error.values())
            res = False
            if(x.count(x[0]) == len(x)):
                res = True

            if res == True:

                # move file to selected folder
                ft_sm       = request.files['ft_sm']
                ft_is       = request.files['ft_is']
                ft_ktp_sm   = request.files['ft_ktp_sm']
                ft_ktp_is   = request.files['ft_ktp_is']
                ft_kk       = request.files['ft_kk']
                ft_knd      = request.files['ft_knd']
                ft_srf_tnh  = request.files['ft_srf_tnh']
                ft_stnk     = request.files['ft_stnk']
                ft_bpkb     = request.files['ft_bpkb']
                ft_rmh     = request.files['ft_rmh']

                if ft_sm.filename != '':
                    filename = ft_sm.filename.split('.')
                    newfilename = 'foto_suami_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_sm.save(UPLOAD_FOLDER+'\\suami\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\suami\\'+fixedfilename,UPLOAD_FOLDER+'\\enc\\suami\\'+fixedfilename,UPLOAD_FOLDER+'\\dec\\suami\\'+fixedfilename)
                    data['ft_sm'] = fixedfilename
                if ft_is.filename != '':
                    filename = ft_is.filename.split('.')
                    newfilename = 'foto_istri_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_is.save(UPLOAD_FOLDER+'\\istri\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\istri\\'+fixedfilename, UPLOAD_FOLDER+'\\enc\\istri\\'+fixedfilename,UPLOAD_FOLDER+'\\dec\\istri\\'+fixedfilename)
                    data['ft_is'] = fixedfilename
                if ft_ktp_sm.filename != '':
                    filename = ft_ktp_sm.filename.split('.')
                    newfilename = 'foto_ktp_suami_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_ktp_sm.save(UPLOAD_FOLDER+'\\ktp\\suami\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\ktp\\suami\\'+fixedfilename, UPLOAD_FOLDER+'\\enc\\ktp\\suami\\'+fixedfilename,UPLOAD_FOLDER+'\\dec\\ktp\\suami\\'+fixedfilename)
                    data['ft_ktp_sm'] = fixedfilename
                if ft_ktp_is.filename != '':
                    filename = ft_ktp_is.filename.split('.')
                    newfilename = 'foto_ktp_istri_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_ktp_is.save(UPLOAD_FOLDER+'\\ktp\\istri\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\ktp\\istri\\'+fixedfilename, UPLOAD_FOLDER+'\\enc\\ktp\\istri\\'+fixedfilename,UPLOAD_FOLDER+'\\dec\\ktp\\istri\\'+fixedfilename)
                    data['ft_ktp_is'] = fixedfilename
                if ft_kk.filename != '':
                    filename = ft_kk.filename.split('.')
                    newfilename = 'foto_kk_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_kk.save(UPLOAD_FOLDER+'\\kk\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\kk\\'+fixedfilename,UPLOAD_FOLDER+'\\enc\\kk\\'+fixedfilename,UPLOAD_FOLDER+'\\dec\\kk\\'+fixedfilename)
                    data['ft_kk'] = fixedfilename
                if ft_knd.filename != '':
                    filename = ft_knd.filename.split('.')
                    newfilename = 'foto_kendaraan_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_knd.save(UPLOAD_FOLDER+'\\kendaraan\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\kendaraan\\'+fixedfilename, UPLOAD_FOLDER+'\\enc\\kendaraan\\'+fixedfilename,UPLOAD_FOLDER+'\\dec\\kendaraan\\'+fixedfilename)
                    data['ft_knd'] = fixedfilename
                if ft_srf_tnh.filename != '':
                    filename = ft_srf_tnh.filename.split('.')
                    newfilename = 'foto_sertif_tanah_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_srf_tnh.save(UPLOAD_FOLDER+'\\sertifikat_tanah\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\sertifikat_tanah\\'+fixedfilename, UPLOAD_FOLDER+'\\enc\\sertifikat_tanah\\'+fixedfilename, UPLOAD_FOLDER+'\\dec\\sertifikat_tanah\\'+fixedfilename)
                    data['ft_srf_tnh'] = fixedfilename
                if ft_stnk.filename != '':
                    filename = ft_stnk.filename.split('.')
                    newfilename = 'foto_stnk_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_stnk.save(UPLOAD_FOLDER+'\\stnk\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\stnk\\'+fixedfilename, UPLOAD_FOLDER+'\\enc\\stnk\\'+fixedfilename, UPLOAD_FOLDER+'\\dec\\stnk\\'+fixedfilename)
                    data['ft_stnk'] = fixedfilename
                if ft_bpkb.filename != '':
                    filename = ft_bpkb.filename.split('.')
                    newfilename = 'foto_bpkb_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_bpkb.save(UPLOAD_FOLDER+'\\bpkb\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\bpkb\\'+fixedfilename, UPLOAD_FOLDER+'\\enc\\bpkb\\'+fixedfilename, UPLOAD_FOLDER+'\\dec\\bpkb\\'+fixedfilename)
                    data['ft_bpkb'] = fixedfilename
                if ft_rmh.filename != '':
                    filename = ft_rmh.filename.split('.')
                    newfilename = 'foto_rmh_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    ft_rmh.save(UPLOAD_FOLDER+'\\rmh\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\rmh\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\rmh\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\rmh\\'+fixedfilename)
                    data['ft_rmh'] = fixedfilename
                # Insert to Database
                cur = mysql.connection.cursor()
                cur.execute(
                    "INSERT INTO members(nama, ttl, tlp, alamat, ft_sm, ft_is, ft_ktp_sm, ft_ktp_is, ft_kk, ft_knd, ft_srf_tnh, ft_stnk, ft_bpkb, jk, ft_rmh) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (
                    data['nama'], data['ttl'], data['tlp'], data['alamat'], data['ft_sm'], data['ft_is'], data['ft_ktp_sm'],
                    data['ft_ktp_is'], data['ft_kk'], data['ft_knd'], data['ft_srf_tnh'], data['ft_stnk'], data['ft_bpkb'],
                    int(data['jk']), data['ft_rmh'],))
                mysql.connection.commit()
                cur.close()
                sukses = 1
            return render_template('pages/addMember.html', title=title, error=error,dt=data, sukses = sukses)
        else:
            return redirect('/login')
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def editAnggota(id):
    if 'loggedin' in session:
        error = {}
        data = {
            'nama': '',
            'ttl' : '',
            'tlp' : '',
            'alamat' : '',
            'ft_sm' : '',
            'ft_is' : '',
            'ft_ktp_sm' : '',
            'ft_ktp_is' : '',
            'ft_kk' : '',
            'ft_knd' : '',
            'ft_srf_tnh' : '',
            'ft_stnk' : '',
            'ft_bpkb' : '',
            'jk' : '',
            'ft_rmh' : '',
        }

        title = 'Edit Data Anggtota'
        if request.method == 'GET':
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM members WHERE id = "+str(id))
            mysql.connection.commit()
            result = cur.fetchall()
            print(result)
            for res in result:
                data['nama'] = res[1]
                data['ttl'] = res[2]
                data['tlp'] = res[3]
                data['alamat'] = res[4]
                data['ft_sm'] = res[5]
                data['ft_is'] = res[6]
                data['ft_ktp_sm'] = res[7]
                data['ft_ktp_is'] = res[8]
                data['ft_kk'] = res[9]
                data['ft_knd'] = res[10]
                data['ft_srf_tnh'] = res[11]
                data['ft_stnk'] = res[12]
                data['ft_bpkb'] = res[13]
                data['jk'] = res[14]
                data['ft_rmh'] = res[15]
            return render_template('pages/editMembers.html', title=title, dt = data, id=id)


        if request.method == 'POST':
            sukses = 0
            if request.form.get('nama') == '':
                error['nama'] = 'Isian Nama Anggota Harus Diisi !'
            else:
                error['nama'] = ''
                data['nama'] = request.form.get('nama')
            if request.form.get('jk') != '0' and request.form.get('jk') != '1':
                error['jk'] = 'Jenis Kelamin Tidak Valid !'
            else:
                error['jk'] = ''
                data['jk'] = request.form.get('jk')
            if request.form.get('tlp') == '':
                error['tlp'] = 'Isian Nomor Telepon Anggota Harus Diisi !'
            else:
                error['tlp'] = ''
                data['tlp'] = request.form.get('tlp')
            if request.form.get('ttl') == '':
                error['ttl'] = 'Isian Tempat Tanggal Lahir Anggota Harus Diisi !'
            else:
                error['ttl'] = ''
                data['ttl'] = request.form.get('ttl')
            if request.form.get('alamat') == '':
                error['alamat'] = 'Isian Alamat Anggota Harus Diisi !'
            else:
                error['alamat'] = ''
                data['alamat'] = request.form.get('alamat')
            if request.form.get('ft_rmh') == '':
                error['ft_rmh'] = 'Isian Foto Rumah Anggota Harus Diisi !'
            else:
                error['ft_rmh'] = ''
                data['ft_rmh'] = request.form.get('ft_rmh')


            x = list(error.values())
            res = False
            if(x.count(x[0]) == len(x)):
                res = True

            if res == True:
                ft_sm       = request.files['ft_sm']
                ft_is       = request.files['ft_is']
                ft_ktp_sm   = request.files['ft_ktp_sm']
                ft_ktp_is   = request.files['ft_ktp_is']
                ft_kk       = request.files['ft_kk']
                ft_knd      = request.files['ft_knd']
                ft_srf_tnh  = request.files['ft_srf_tnh']
                ft_stnk     = request.files['ft_stnk']
                ft_bpkb     = request.files['ft_bpkb']
                ft_rmh      = request.files['ft_rmh']

                cur = mysql.connection.cursor()
                cur.execute("SELECT * FROM members WHERE id = "+str(id))
                mysql.connection.commit()
                result = cur.fetchall()
                if ft_sm.filename != '':
                    filename = ft_sm.filename.split('.')
                    newfilename = 'foto_suami_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'suami\\'+result[0][5])
                    ft_sm.save(UPLOAD_FOLDER+'\\suami\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER + '\\suami\\' + fixedfilename,
                               UPLOAD_FOLDER + '\\enc\\suami\\' + fixedfilename,
                               UPLOAD_FOLDER + '\\dec\\suami\\' + fixedfilename)
                    data['ft_sm'] = fixedfilename
                if ft_is.filename != '':
                    filename = ft_is.filename.split('.')
                    newfilename = 'foto_istri_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'istri\\'+result[0][6])
                    ft_is.save(UPLOAD_FOLDER+'\\istri\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\istri\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\istri\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\istri\\'+fixedfilename)
                    data['ft_is'] = fixedfilename
                if ft_ktp_sm.filename != '':
                    filename = ft_ktp_sm.filename.split('.')
                    newfilename = 'foto_ktp_suami_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'ktp\\suami\\'+ result[0][7])
                    ft_ktp_sm.save(UPLOAD_FOLDER+'\\ktp\\suami\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\ktp\\suami\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\ktp\\suami\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\ktp\\suami\\'+fixedfilename)
                    data['ft_ktp_sm'] = fixedfilename
                if ft_ktp_is.filename != '':
                    filename = ft_ktp_is.filename.split('.')
                    newfilename = 'foto_ktp_istri_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'ktp\\istri\\'+ result[0][8])
                    ft_ktp_is.save(UPLOAD_FOLDER+'\\ktp\\istri\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\ktp\\istri\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\ktp\\istri\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\ktp\\istri\\'+fixedfilename)
                    data['ft_ktp_is'] = fixedfilename
                if ft_kk.filename != '':
                    filename = ft_kk.filename.split('.')
                    newfilename = 'foto_kk_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'kk\\'+ result[0][9])
                    ft_kk.save(UPLOAD_FOLDER+'\\kk\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\kk\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\kk\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\kk\\'+fixedfilename)
                    data['ft_kk'] = fixedfilename
                if ft_knd.filename != '':
                    filename = ft_knd.filename.split('.')
                    newfilename = 'foto_kendaraan_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'kendaraan\\'+ result[0][10])
                    ft_knd.save(UPLOAD_FOLDER+'\\kendaraan\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\kendaraan\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\kendaraan\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\kendaraan\\'+fixedfilename)
                    data['ft_knd'] = fixedfilename
                if ft_srf_tnh.filename != '':
                    filename = ft_srf_tnh.filename.split('.')
                    newfilename = 'foto_sertif_tanah_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'sertifikat_tanah\\'+ result[0][11])
                    ft_srf_tnh.save(UPLOAD_FOLDER+'\\sertifikat_tanah\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\sertifikat_tanah\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\sertifikat_tanah\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\sertifikat_tanah\\'+fixedfilename)
                    data['ft_srf_tnh'] = fixedfilename
                if ft_stnk.filename != '':
                    filename = ft_stnk.filename.split('.')
                    newfilename = 'foto_stnk_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'stnk\\'+ result[0][12])
                    ft_stnk.save(UPLOAD_FOLDER+'\\stnk\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\stnk\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\stnk\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\stnk\\'+fixedfilename)
                    data['ft_stnk'] = fixedfilename
                if ft_bpkb.filename != '':
                    filename = ft_bpkb.filename.split('.')
                    newfilename = 'foto_bpkb_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'bpkb\\'+ result[0][13])
                    ft_bpkb.save(UPLOAD_FOLDER+'\\bpkb\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\bpkb\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\bpkb\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\bpkb\\'+fixedfilename)
                    data['ft_bpkb'] = fixedfilename
                if ft_rmh.filename != '':
                    filename = ft_rmh.filename.split('.')
                    newfilename = 'foto_rmh_'+str(time.time())
                    fileType = filename[-1]
                    fixedfilename = newfilename+'.'+fileType
                    os.remove(UPLOAD_FOLDER+'rmh\\'+ result[0][15])
                    ft_rmh.save(UPLOAD_FOLDER+'\\rmh\\'+fixedfilename)
                    rsaalg.RSA(UPLOAD_FOLDER+'\\rmh\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\enc\\rmh\\'+fixedfilename,
                               UPLOAD_FOLDER+'\\dec\\rmh\\'+fixedfilename)
                    data['ft_rmh'] = fixedfilename

                updatedColumn = ''
                if data['nama'] != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'nama ="'+data['nama'].strip()+'"'
                if data['ttl'] != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ttl ="'+data['ttl'].strip()+'"'
                if data['tlp'] != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'tlp ="'+data['tlp'].strip()+'"'
                if data['alamat'] != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'alamat ="'+data['alamat'].strip()+'"'
                if ft_sm.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_sm ="'+data['ft_sm'].strip()+'"'
                if ft_is.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_is ="'+data['ft_is'].strip()+'"'
                if ft_ktp_sm.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_ktp_sm ="'+data['ft_ktp_sm'].strip()+'"'
                if ft_ktp_is.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_ktp_is ="'+data['ft_ktp_is'].strip()+'"'
                if ft_kk.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_kk ="'+data['ft_kk'].strip()+'"'
                if ft_knd.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_knd ="'+data['ft_knd'].strip()+'"'
                if ft_srf_tnh.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_srf_tnh ="'+data['ft_srf_tnh'].strip()+'"'
                if ft_stnk.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_stnk ="'+data['ft_stnk'].strip()+'"'
                if ft_bpkb.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_bpkb ="'+data['ft_bpkb'].strip()+'"'
                if ft_rmh.filename != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'ft_rmh ="'+data['ft_rmh'].strip()+'"'
                if data['jk'] != '':
                    if updatedColumn != '':
                        updatedColumn += ', '
                    updatedColumn += 'jk ="'+data['jk'].strip()+'"'

                cur = mysql.connection.cursor()
                cur.execute("UPDATE members SET "+updatedColumn+" WHERE id = "+str(id))
                mysql.connection.commit()
                cur.close()
                sukses = 1
            return render_template('pages/editMembers.html', title=title, error=error, dt=data, sukses=sukses, id=id)
    else:
        return  redirect('/login')

@app.route('/hapus/<int:id>', methods=['GET', 'POST'])
def hapusAnggota(id):
    if 'loggedin' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM members WHERE id = "+ str(id))
        mysql.connection.commit()
        result = cur.fetchall()
        os.remove(UPLOAD_FOLDER+'suami\\'+result[0][5])
        os.remove(UPLOAD_FOLDER+'istri\\'+result[0][6])
        os.remove(UPLOAD_FOLDER+'ktp\\suami\\'+ result[0][7])
        os.remove(UPLOAD_FOLDER+'ktp\\istri\\'+ result[0][8])
        os.remove(UPLOAD_FOLDER+'kk\\'+ result[0][9])
        os.remove(UPLOAD_FOLDER+'kendaraan\\'+ result[0][10])
        os.remove(UPLOAD_FOLDER+'sertifikat_tanah\\'+ result[0][11])
        os.remove(UPLOAD_FOLDER+'stnk\\'+ result[0][12])
        os.remove(UPLOAD_FOLDER+'bpkb\\'+ result[0][13])

        cur.execute("DELETE FROM members WHERE id="+str(id))
        mysql.connection.commit()
        return redirect('/')
    else:
        return redirect('/login')

@app.route('/anggota-all')
def allAnggota():
    if 'loggedin' in session:
        title = "Daftar Anggota"
        page = request.args.get('page', 1, type=int)
        per_page = 6
        search_query = request.args.get('search', '')  # Get search query

        cursor = mysql.connection.cursor()

        # Build SQL query with search (adjust column names as needed)
        if search_query:
            query = "SELECT * FROM members WHERE nama LIKE %s ORDER BY id DESC LIMIT %s OFFSET %s"
            search_term = f"%{search_query}%"
            cursor.execute(query, (search_term, per_page, (page - 1) * per_page))
        else:
            query = "SELECT * FROM members LIMIT %s OFFSET %s"
            cursor.execute(query, (per_page, (page - 1) * per_page))

        data = cursor.fetchall()

        # Count total results (adjust query for search if needed)
        if search_query:
            count_query = "SELECT COUNT(*) FROM members WHERE nama LIKE '%"+search_query+"%'"
            cursor.execute(count_query)
        else:
            count_query = "SELECT COUNT(*) FROM members"
            cursor.execute(count_query)

        total_results = cursor.fetchone()[0]
        total_pages = (total_results + per_page - 1) // per_page

        return render_template('pages/allAnggota.html',title=title, data=data, page=page, total_pages=total_pages, search_query=search_query)
        # return render_template('pages/allAnggota.html', title=title, data= result)
    else:
        return redirect('/login')
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'loggedin' in session:
        session.pop('loggedin', None)
        session.pop('id', None)
        session.pop('username', None)

    title = 'Halaman Login'
    pesan = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']

        hash_password = hashlib.md5(password.encode()).hexdigest()
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute("SELECT * FROM users where username = %s AND password = %s", (username, hash_password))
        user = cursor.fetchone()

        if user:
            session['loggedin'] = True
            session['id'] = user['id']
            session['username'] = user['username']
            return redirect('/')
        else:
            pesan ="Username dan atau password salah !"
    return render_template('pages/loginPage.html', title=title, pesan=pesan)

if __name__ == '__main__':
    app.run(debug=True)