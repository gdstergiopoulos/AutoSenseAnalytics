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
        // console.log(projects);
        return projects;
    }
    catch(err){
        throw err;
    }
}

export let getProjectUsers = async (projID) => {
    let stmt = await sql.prepare("SELECT username FROM Project,HasAccess WHERE projID = ? AND projID=id AND username != 'AutoSense'");
    try{
        let users = stmt.all(projID);
        return users;
    }
    catch(err){
        throw err;
    }
}

export let createProject = async (projName, projDesc) => {
    
    try{
        let idStmt = await sql.prepare('SELECT MAX(id) as maxId FROM Project');
        let result = idStmt.get();
        let newId = (result.maxId || 0) + 1;

        let stmt = await sql.prepare('INSERT INTO Project(id,projName,projDescrip) VALUES(?,?,?)');
        try{
            stmt.run(newId,projName,projDesc);
            return true;
        }
        catch(err){
            throw err;
        }
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

export let getAllProjects = async () => {
    let stmt = await sql.prepare('SELECT DISTINCT * FROM Project');
    try{
        let projects = stmt.all();
        return projects;
    }
    catch(err){
        throw err;
    }
}

export let getAllUsers = async () => {
    console.log('In model');
    let stmt = sql.prepare("SELECT * FROM User WHERE username != 'AutoSense'");
    try{
        let users = stmt.all();
        console.log(users)
        return users;
    }
    catch(err){
        throw err;
    }
}

export let addMessage = async (name,email,msg) => {
    let stmt= await sql.prepare('INSERT INTO Messages VALUES (?,?,?)')
    try{
        let insertmsg= stmt.run(name,email,msg);
        return insertmsg;
    }
    catch(err){
        throw err;
    }
}

export let writePhotoData = async (timestamp, latitude, longitude, path) => {
    let stmt = await sql.prepare('INSERT INTO Photos VALUES(?,?,?,?)');
    try{
        stmt.run(latitude, longitude,timestamp, path);
        return true;
    }
    catch(err){
        throw err;
    }
}

export let getPhotos = async () => {
    let stmt = await sql.prepare('SELECT * FROM Photos');
    try{
        let photos = stmt.all();
        return photos;
    }
    catch(err){
        throw err;
    }
}