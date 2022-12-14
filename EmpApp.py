from flask import Flask, render_template, request, url_for, redirect
from pymysql import connections
import os
import boto3
import calendar
import datetime
from config import *

# Flask constructor#
# WSGI Application
# Provide template folder name
# The default folder name should be "templates" else need to mention custom folder name
app = Flask(__name__,template_folder="templates", static_folder="static")

Upload_folder = "uploads"
bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


# Creating a route that has both GET and POST request methods
@app.route("/", methods=['GET', 'POST'])
def profile():
    return render_template('Profile.html')

@app.route("/Employees")
def employee():
    search_sql = "SELECT * FROM employee where status = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, ("ACTIVE"))
    allemp = cursor.fetchall()
    cursor.close()
    return render_template('Employee.html', allemp = allemp)

@app.route("/Add_employee", methods=['GET', 'POST'])
def addEmployee():
    if request.method == 'POST':
       #add userdata when press submit button#
       fname = request.form['fname']
       lname = request.form['lname']
       eid = request.form['eid']
       dept = request.form['dept']
       deg = request.form['deg']
       role = request.form['role']
       gender = request.form['gender']
       blood = request.form['blood']
       nid = request.form['nid']
       contact = request.form['contact']
       dob = request.form['dob']
       joindate = request.form['joindate']
       leavedate = request.form['leavedate']
       username = request.form['username']
       email = request.form['email']
       image_url = request.files['image_url']
       status = "ACTIVE"

       insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
       cursor = db_conn.cursor()

       try:

        cursor.execute(insert_sql, (fname, lname, eid, dept, deg, role, gender, blood, nid, contact, dob, joindate, leavedate, username, email, status))
        db_conn.commit()

        sid = ""
        emid = eid
        typeid = "Monthly"
        total = ""

        insert_sql = "INSERT INTO salary VALUES (%s, %s, %s, %s)"
        cursor = db_conn.cursor()
        cursor.execute(insert_sql, (sid, emid, typeid, total))
        db_conn.commit()

  
        #Set name for listout#
        emp_name = "" + fname + " " + lname
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "upload/emp-id-" + str(eid) + "_image_file.png" 
        
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=image_url.read())
            #copy obj and change meta#
            s3_object = s3.Object(bucket, emp_image_file_name_in_s3)
            #change metadata#
            s3_object.copy_from(CopySource={'Bucket':bucket, 'Key':emp_image_file_name_in_s3}, MetadataDirective='REPLACE', ContentType= "image/png")
          
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

       finally:
        cursor.close()

       

       print("all modification done...")
       #after store data return back#

    #Generate auto number#
    search_sql = "SELECT eid FROM employee ORDER BY eid DESC"
    cursor = db_conn.cursor()

    cursor.execute(search_sql)
    existing_userID = cursor.fetchone()
    eid = 1000
    #detect to search existing user#
    if existing_userID:
       eid = existing_userID[0] + 1
    return render_template('Add_employee.html', eid = eid)

@app.route("/Single_Employee/<eid>")
def singleEmployee(eid):
    #Using %s to Prevent SQL Injection#
    search_sql = "SELECT * FROM employee where eid = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (eid))
    single_emp = cursor.fetchone()

    search_sql = "SELECT * FROM salary where emid = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (eid))
    salary_emp = cursor.fetchone()

    user_img = "https://chowwenghoong-bucket.s3.amazonaws.com/upload/emp-id-{0}_image_file.png".format(eid)
    cursor.close()
    return render_template('Single_Employee.html', single_emp = single_emp, salary_emp = salary_emp, user_img = user_img)

@app.route("/Update_Employee", methods=['GET', 'POST'])
def updateEmployee():
    if request.method == 'POST':
       #add userdata when press submit button#
       fname = request.form['fname']
       lname = request.form['lname']
       eid = request.form['eid']
       dept = request.form['dept']
       deg = request.form['deg']
       role = request.form['role']
       gender = request.form['gender']
       blood = request.form['blood']
       nid = request.form['nid']
       contact = request.form['contact']
       dob = request.form['dob']
       joindate = request.form['joindate']
       leavedate = request.form['leavedate']
       email = request.form['email']
       status = request.form['status']
       image_url = request.files['image_url']
    
       update_sql = "UPDATE employee SET fname = %s, lname = %s, dept = %s, deg = %s, role = %s, gender = %s, blood = %s, nid = %s, contact = %s, dob = %s, joindate = %s, leavedate = %s, email = %s, status = %s where eid = %s"
       cursor = db_conn.cursor()
       cursor.execute(update_sql, (fname, lname, dept, deg, role, gender, blood, nid, contact, dob, joindate, leavedate, email, status, eid))
       db_conn.commit()

       if image_url.filename != "":
       # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "upload/emp-id-" + str(eid) + "_image_file.png" 
        
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=image_url.read())
            #copy obj and change meta#
            s3_object = s3.Object(bucket, emp_image_file_name_in_s3)
            #change metadata#
            s3_object.copy_from(CopySource={'Bucket':bucket, 'Key':emp_image_file_name_in_s3}, MetadataDirective='REPLACE', ContentType= "image/png")
          
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
               s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

        finally:
         cursor.close()

    return employee()

    

@app.route("/Attendance")
def attendance():
    search_sql = "SELECT * FROM attendance"
    cursor = db_conn.cursor()

    cursor.execute(search_sql)
    allattend = cursor.fetchall()  
    cursor.close()
    return render_template('Attendance.html', allattend = allattend)


@app.route("/Save_Attendance", methods=['GET', 'POST'])
def addAttendance():
    if request.method == 'POST':
       #add userdata when press submit button#
       emid = request.form['emid']
       attdate = request.form['attdate']
       signin = request.form['signin']
       signout = request.form['signout']
       place = request.form['place']
       id = request.form['id']
       
    
       insert_sql = "INSERT INTO attendance VALUES (%s, %s, %s, %s, %s, %s)"
       cursor = db_conn.cursor()
       cursor.execute(insert_sql, (id, emid, attdate, signin, signout, place))
       db_conn.commit()

    search_sql = "SELECT * FROM employee"
    cursor = db_conn.cursor()

    cursor.execute(search_sql)
    allemp = cursor.fetchall()
    cursor.close()
    return render_template('Save_Attendance.html', allemp = allemp)

@app.route("/Single_Attendance/<id>")
def singleAttendance(id):
    #Using %s to Prevent SQL Injection#
    search_sql = "SELECT * FROM attendance where id = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (id))
    attendance_emp = cursor.fetchone()

    search_sql = "SELECT * FROM employee where eid = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (attendance_emp[1]))
    single_emp = cursor.fetchone()
    cursor.close()
    return render_template('Single_Attendance.html', single_emp = single_emp, attendance_emp = attendance_emp)

@app.route("/Update_Attendance", methods=['GET', 'POST'])
def updateAttendance():
    if request.method == 'POST':
       #add userdata when press submit button#
       attdate = request.form['attdate']
       signin = request.form['signin']
       signout = request.form['signout']
       place = request.form['place']
       id = request.form['id']
    
       update_sql = "UPDATE attendance SET attdate = %s, signin = %s, signout = %s, place = %s where id = %s"
       cursor = db_conn.cursor()
       cursor.execute(update_sql, (attdate, signin, signout, place, id))
       db_conn.commit()
       cursor.close()
    return attendance()

@app.route("/Leave")
def leave(): 
    
    search_sql = "SELECT * FROM empLeave"
    cursor = db_conn.cursor()

    cursor.execute(search_sql)
    allleave = cursor.fetchall()
    cursor.close()
    if allleave:
        return render_template('Leave.html', allleave = allleave)

    return render_template('Leave.html')

@app.route("/Add_Leave", methods=['GET', 'POST'])
def addLeave():
    if request.method == 'POST':
       #add userdata when press submit button#
       em_id = request.form['em_id']
       leave_type = request.form['leave_type']
       start_date = request.form['start_date']
       end_date = request.form['end_date']
       leaveStatus = "Pending"
       reason = request.form['reason']
       id = request.form['id']
       
    
       insert_sql = "INSERT INTO empLeave VALUES (%s, %s, %s, %s, %s, %s, %s)"
       cursor = db_conn.cursor()
       cursor.execute(insert_sql, (id, em_id, leave_type, start_date, end_date, leaveStatus, reason))
       db_conn.commit()
       cursor.close()

    search_sql = "SELECT * FROM employee"
    cursor = db_conn.cursor()

    cursor.execute(search_sql)
    allemp = cursor.fetchall()
    cursor.close()
    return render_template('Add_Leave.html', allemp = allemp)

@app.route("/ApproveLeave/<id>")
def approveLeave(id): 
    #add userdata when press submit button#
    status = "Approve"
       
    update_sql = "UPDATE empLeave SET leaveStatus = %s where id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (status, id))
    db_conn.commit()
    cursor.close()
    return redirect(url_for('leave'))

@app.route("/RejectLeave/<id>")
def rejectLeave(id): 
    #add userdata when press submit button#
    status = "Reject"
       
    update_sql = "UPDATE empLeave SET leaveStatus = %s where id = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (status, id))
    db_conn.commit()
    cursor.close()
    return redirect(url_for('leave'))

@app.route("/Single_Leave/<id>")
def singleLeave(id):
    #Using %s to Prevent SQL Injection#

    search_sql = "SELECT * FROM empLeave where id = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (id))
    leave_emp = cursor.fetchone()

    search_sql = "SELECT * FROM employee where eid = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (leave_emp[1]))
    single_emp = cursor.fetchone()
    cursor.close()
    return render_template('Single_Leave.html', single_emp = single_emp, leave_emp = leave_emp)

@app.route("/Update_Leave", methods=['GET', 'POST'])
def updateLeave():
    if request.method == 'POST':
       #add userdata when press submit button#
       id = request.form['id']
       em_id = request.form['em_id']
       leave_type = request.form['leave_type']
       start_date = request.form['start_date']
       end_date = request.form['end_date']
       reason = request.form['reason']
    
       update_sql = "UPDATE empLeave SET leave_type = %s, start_date = %s, end_date = %s, reason = %s where id = %s"
       cursor = db_conn.cursor()
       cursor.execute(update_sql, (leave_type, start_date, end_date, reason, id))
       db_conn.commit()
       cursor.close()
    return leave()

@app.route("/Salary_List")
def salaryList(): 
    
    search_sql = "SELECT * FROM paySalary"
    cursor = db_conn.cursor()

    cursor.execute(search_sql)
    allsalary = cursor.fetchall()
    cursor.close()
    if allsalary:
        return render_template('Salary_List.html', allsalary = allsalary)

    return render_template('Salary_List.html')

@app.route("/Single_Salary/<eid>")
def singleSalary(eid):
    #Using %s to Prevent SQL Injection#
    search_sql = "SELECT * FROM employee where eid = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (eid))
    single_emp = cursor.fetchone()

    search_sql = "SELECT * FROM salary where emid = %s"
    cursor = db_conn.cursor()

    cursor.execute(search_sql, (eid))
    salary_emp = cursor.fetchone()
    cursor.close()

    return render_template('Single_Salary.html', single_emp = single_emp, salary_emp = salary_emp)

@app.route("/Add_Salary", methods=['GET', 'POST'])
def addSalary():
    if request.method == 'POST':
       #add userdata when press submit button#
       typeid = request.form['typeid']
       total = request.form['total']
       emid = request.form['emid']
       
       update_sql = "UPDATE salary SET typeid = %s, total = %s where emid = %s"
       cursor = db_conn.cursor()
       cursor.execute(update_sql, (typeid, total, emid))
       db_conn.commit()
       cursor.close()

    return salaryList()

@app.route("/Generate_Salary", methods=['GET', 'POST'])
def generateSalary(): 
    if request.method == 'POST':
       #add userdata when press submit button#
       emid = request.form['emid']
       month = request.form['month']
       total_paid = request.form['total_paid']
       status = "Process"
       paidType = request.form['paidType']
       pay_id = request.form['pay_id']
       
       insert_sql = "INSERT INTO paySalary VALUES (%s, %s, %s, %s, %s, %s)"
       cursor = db_conn.cursor()
       cursor.execute(insert_sql, (pay_id, emid, month, total_paid, status, paidType))
       db_conn.commit()
       cursor.close()

    search_sql = "SELECT * FROM employee"
    cursor = db_conn.cursor()

    cursor.execute(search_sql)
    allemp = cursor.fetchall()
    cursor.close()
    return render_template('Generate_Salary.html', allemp=allemp)

@app.route("/UpdatePaidStatus/<eid>")
def updatePaidStatus(eid): 
    #add userdata when press submit button#
    status = "Paid"
       
    update_sql = "UPDATE paySalary SET status = %s where emid = %s"
    cursor = db_conn.cursor()
    cursor.execute(update_sql, (status, eid))
    db_conn.commit()
    cursor.close()
    return redirect(url_for('salaryList'))


@app.context_processor
def utility_processor():
    def getEmpName(empid):
        search_sql = "SELECT * FROM employee where eid = %s"
        cursor = db_conn.cursor()

        cursor.execute(search_sql, (empid))
        single_emp = cursor.fetchone()
        cursor.close()
        name = single_emp[0] +" "+ single_emp[1]
        return name

    def getEmpSalary(empid):
        search_sql = "SELECT total FROM salary where emid = %s"
        cursor = db_conn.cursor()

        cursor.execute(search_sql, (empid))
        salary = cursor.fetchone()
        cursor.close()
        return salary[0]

    return dict(getEmpName=getEmpName, getEmpSalary=getEmpSalary)

# Initiating the application
if __name__ == '__main__':
 # Running the application and leaving the debug mode ON
    app.run(host='0.0.0.0', port=80, debug=True)
