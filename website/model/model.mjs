import db from 'better-sqlite3'
import bcrypt from 'bcrypt'

const sql= new db('model/AutoSenseAnalytics.sqlite', { fileMustExist: true });

export let registerUser = async (username, email,password) => {
    const saltRounds = 10;
    const hashedPassword = await bcrypt.hash(password, saltRounds);
    let stmt = sql.prepare('INSERT INTO User(username,email,password) VALUES(?,?,?)');
    try{
        stmt.run(username,email,hashedPassword);
        return true;
    }
    catch(err){
        throw err;
    }
}

export let checkLogin = async (username, password) => {
    let stmt = sql.prepare('SELECT username,password FROM User WHERE username = ?');
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

export let getCompanyProjects = async (username) => {
    let stmt = await sql.prepare('SELECT projName,id FROM Project,HasAccess WHERE username = ? AND projID=id');
    try{
        let projects = stmt.all(username);
        return projects;
    }
    catch(err){
        throw err;
    }
}

export let getProjectData = async (projID) => {
    let stmt = await sql.prepare('SELECT * FROM Project WHERE id = ?');
    try{
        let project = stmt.get(projID);
        return project;
    }
    catch(err){
        throw err;
    }
}