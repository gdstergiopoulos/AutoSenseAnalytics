import db from 'better-sqlite3'
import bcrypt from 'bcrypt'

const sql= new db('model/hmtygrade.sqlite', { fileMustExist: true });

export let registerUser = async (username, email,password) => {
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);
    let stmt = sql.prepare('INSERT INTO Account(username,email,password) VALUES(?,?,?)');
    try{
        stmt.run(username,email,hashedPassword);
        return true;
    }
    catch(err){
        throw err;
    }
}

export let checkLogin = async (username, password) => {
    let stmt = sql.prepare('SELECT username,password FROM Account WHERE username = ?');
    try{
        let user = stmt.get(username);
        // console.log(user);
        if(user)
        {
            const match = await bcrypt.compare(password, user.password);
            if(match){
                console.log('Correct password');
                return user;
            }
            else{
                throw new Error('Wrong password');
            }
        }
        else{
            throw new Error('User does not exist');
        }
        // console.log(user[0].username);
    }
    catch(err){
        throw err;
    }
}   

export let getCourses= (semesterID) => {
    let stmt = sql.prepare('SELECT * FROM Course WHERE semester = ?');
    try{
        let courses = stmt.all(semesterID);
        return courses;
    }
    catch(err){
        throw err;
    }
}

export let getSelectedCourses = (studentID,semesterID) => {
    let stmt = sql.prepare('SELECT C.courseName,C.courseCode,S.Semester,C.syntelestis\
        FROM Course as C,Selection as S\
        WHERE C.courseCode=S.courseCode AND S.username=? AND S.Semester=?');
    try{
        let courses = stmt.all(studentID,semesterID);
        return courses;
    }
    catch(err){
        throw err;
    }
}

export let getSelectionCourses = () => {
    let stmt = sql.prepare('SELECT courseName, syntelestis, courseCode FROM Course WHERE semester not in (1,2,3,4,5,6,10)');
    try{
        let courses = stmt.all();
        // console.log(courses)
        return courses;
    }
    catch(err){
        throw err;
    }
}

export let getAllCoreCourses = () => {
    let stmt = sql.prepare('SELECT courseName, syntelestis FROM Course WHERE semester in (1,2,3,4,5,6,10)');
    try{
        let courses = stmt.all();
        return courses;
    }
    catch(err){
        throw err;
    }
}

export let saveGrade = (username, courseCode, grade) => {
    let stmt = sql.prepare('INSERT INTO Grades(student,course,grade) VALUES(?,?,?)');
    try{
        console.log("im here")
        stmt.run(username,courseCode,grade);
        return true;
    }
    catch(err){
        throw err;
    }
}

export let updateGrade = (username, courseCode, grade) => {
    let stmt = sql.prepare('UPDATE Grades SET grade = ? WHERE student = ? AND course = ?');
    try{
        stmt.run(grade,username,courseCode);
    }
    catch(err){
        throw err;
    }
}

export let getCodes= () => {
    let stmt = sql.prepare('SELECT courseCode FROM Course');
    try{
        let codes = stmt.all();
        return codes;
    }
    catch(err){
        throw err;
    }
}

export let getGrades = (username) => {
    let stmt = sql.prepare('SELECT course,grade FROM Grades WHERE student = ?');
    try{
        let grades = stmt.all(username);
        return grades;
    }
    catch(err){
        throw err;
    }
}

export let getSpecificGrade=  (username, courseCode) => {
    let stmt = sql.prepare('SELECT grade FROM Grades WHERE student = ? AND course = ?');
    try{
        let grade = stmt.all(username,courseCode);
        return grade;
    }
    catch(err){
        throw err;
    }
}

export let getAllStudentCodes = (username) => {
    let stmt = sql.prepare('SELECT DISTINCT courseCode FROM Course  WHERE semester in (1,2,3,4,5,6,10) UNION SELECT DISTINCT courseCode FROM Selection WHERE username=?');
    try{
        let courses = stmt.all(username);
        return courses;
    }
    catch(err){
        throw err;
    }
}

export let getAllGradedCourses = (username) => {
    let stmt = sql.prepare('SELECT course FROM Grades WHERE student = ?');
    try{
        let courses = stmt.all(username);
        return courses;
    }
    catch(err){
        throw err;
    }
}

export let checkUser= async (username) => {
    let stmt = sql.prepare('SELECT username FROM Account WHERE username = ?');
    try{
        let user = stmt.all(username);
        return user;
    }
    catch(err){
        throw err;
    }
}

export let checkEmail= async (email) => {
    let stmt = sql.prepare('SELECT email FROM Account WHERE email = ?');
    try{
        let user = stmt.all(email);
        return user;
    }
    catch(err){
        throw err;
    }
}

