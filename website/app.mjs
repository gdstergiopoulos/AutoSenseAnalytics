    // Express.js
import express, { response } from 'express'
// Handlebars (https://www.npmjs.com/package/express-handlebars)
import { engine } from 'express-handlebars'
import session from 'express-session';
import * as model from './model/model.mjs'
import * as model_influx from './model/model_influx.mjs'
import Handlebars from './helpers.js'
import mqtt from 'mqtt';
import multer from 'multer';
import fs from 'fs';
import path from 'path';
import cors from 'cors';




const app = express()
const router = express.Router();
const port = process.env.PORT || '3000';

app.use(express.static('public'));
app.engine('hbs', engine({ extname: 'hbs' }));
app.set('view engine', 'hbs');
app.use(cors());

app.use(router);
router.use(express.json());
router.use(express.urlencoded({ extended: true }));

router.use(session({
        
    secret: process.env.SESSION_SECRET || "PynOjAuHetAuWawtinAytVunar", // κλειδί για κρυπτογράφηση του cookie
    resave: false, // δεν χρειάζεται να αποθηκεύεται αν δεν αλλάξει
    saveUninitialized: false, // όχι αποθήκευση αν δεν έχει αρχικοποιηθεί
    cookie: {
      maxAge: 2 * 60 * 60 * 1000, //TWO_HOURS χρόνος ζωής του cookie σε ms
      sameSite: true
    }
  }));

const storage = multer.diskStorage({
    destination: function (req, file, cb) {
        const uploadDir = 'public/uploads';
        if (!fs.existsSync(uploadDir)) {
            fs.mkdirSync(uploadDir); // Create the directory if it doesn't exist
        }
        cb(null, uploadDir);
    },
    filename: function (req, file, cb) {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, uniqueSuffix + path.extname(file.originalname)); // Unique filename
    }
});

const upload = multer({ storage: storage });

router.route('/').get(async (req, res) => {
    
    if(req.session.username){
        
        res.render('main', {username: req.session.username, page:"home"});
    }
    else
    {   
        res.render('main',{page:"home"});
    }
});

router.route('/login').get((req, res) => {
    if(req.session.username){
        res.redirect('/mycompany');
    }
    else{
        res.render('login');
    }
});

router.route('/login').post(async (req, res) => {
    let login;
    try{
        login=await model.checkLogin(req.body.username, req.body.password);
        if(login){
            req.session.username = login.username;
            res.redirect('/mycompany');
        }
    }
    catch(err){
        res.render('login', {error: err.message});
    }
});

router.route('/register').post(async (req, res) => {
    try{
        if(req.body.username === '' || req.body.email === '' || req.body.password === '' || req.body.confirmpassword === '') {
            res.render('register', {error: 'All fields are required'});
        }
        if(req.body.password !== req.body.confirmpassword){
            res.render('register', {error: 'Passwords do not match'});
        }
        else{
            if(await model.registerUser(req.body.username,req.body.email, req.body.password)){
                req.session.username = req.body.username;
                res.redirect('/mycompany');
            }
        }
    }
    catch(err){
        res.render('register', {error: err.message});
    }
    
});

router.route('/register').get((req, res) => {
    res.render('register');
});

router.route('/home').get((req, res) => {
    res.redirect('/');
});

router.route('/logout').get((req, res) => {
    req.session.destroy();
    res.redirect('/');
});

router.route('/about').get((req, res) => {
    res.render('about', {username: req.session.username , page:"about"});
});

router.route('/projects').get((req, res) => {
    res.render('projects', {username: req.session.username, page:"projects"});
});

router.route('/contact').get((req, res) => {
    res.render('contact', {username: req.session.username, page:"contact"});
});

router.route('/mycompany').get(async (req, res) => {
    if(req.session.username){
        try{
            try {
                let projects = await model.getCompanyProjects(req.session.username);
                res.render('companyhome', {username: req.session.username, page:"mycompany",projects: projects});
            }
            catch(err){
                res.render('companyhome', {username: req.session.username, page:"mycompany", error: err.message});
            }
        }
        catch(err){
            res.render('companyhome', {username: req.session.username, error: err.message});
        }
    }
    else{
        res.redirect('/login');
    }
});

router.route('/mycompany/project/:id').get(async (req, res) => {
    if(!req.session.username){
        res.redirect('/login');
    }
    else{
    try{
        let project= await model.getProjectData(req.params.id);
        let projectPoints;
        if(project.projName==="Signal Coverage - LoRA"){
            projectPoints= await model_influx.getMeasurementsLoRa();
        }
        else if (project.projName==="Access Point Mapping - eduroam"){
            projectPoints= await model_influx.getMeasurementsWifi();
        }
        else if(project.projName==="3D Reconstruction"){
            projectPoints= await model.getPhotos();
        }
        // console.log(projectPoints);
        // res.render('projectpg', {layout: 'main_google' , username: req.session.username, project: project, projectPoints: projectPoints});
        res.render('projectpg', {layout: 'main',username: req.session.username, project: project});
    }
    catch(err){
        res.redirect('companyhome', {error: err.message});
    }
}
});

router.route('/contact').post(async (req, res) => {
    try{
        if(req.body.name === '' || req.body.email === '' || req.body.message === ''){
            res.render('contact', {error: 'All fields are required'});
        }
        else{
            await model.addMessage(req.body.name, req.body.email, req.body.message);
            res.render('contact', {success: 'Message sent successfully', username: req.session.username});
        }
    }
    catch(err){
        res.render('contact', {error: err.message});
    }
});

router.route('/wakeup').get((req, res) => {
    const client = mqtt.connect('mqtt://150.140.186.118:1883');

    client.on('connect', () => {
        client.publish('autosense/wifi', 'Server is awake');
        client.end();
    });

    res.redirect('/');
});

router.route('/measurements').get(async (req, res) => {
    try{
        const measurements = await model_influx.getMeasurementsWifi();
        res.send(measurements);
    }
    catch(err){
        res.send(err.message);
    }
});

router.route('/admin/assignproject').get(async (req, res) => {
    // if(req.session.username){
    //     try{
    //         if (req.session.username == 'AutoSense'){
    //             let users = await model.getAllUsers();
    //             let projects = await model.getAllProjects();
    //             console.log(users);
    //             res.render('assignproject', {username: req.session.username, users: users, projects: projects});
    //         }
    //         else{
    //             res.render('login', {error: 'You do not have permission to access this page'});
    //         }
    //     }
    //     catch(err){
    //         res.render('assignproject', {error: err.message});
    //     }
    // }
    // else{
    //     res.redirect('/login');
    // }
    let users = await model.getAllUsers();
    let projects = await model.getAllProjects();
    res.render('assignproject', {username: req.session.username, page:"assignproject" , users: users, projects: projects});
}
);

router.route('/api/company/:name/projects').get(async (req, res) => {
    try{
        let projects = await model.getCompanyProjects(req.params.name);
        res.send(projects);
    }
    catch(err){
        res.send(err.message);
    }
}
);

router.route('/api/users').get(async (req, res) => {
    try{
        let users = await model.getAllUsers();
        res.send(users);
    }
    catch(err){
        res.send(err.message);
    }
});

router.route('/api/project/:id/users').get(async (req, res) => {
    try{
        let users = await model.getProjectUsers(req.params.id);
        res.send(users);
    }
    catch(err){
        res.send(err.message);
    }
});

router.route('/api/measurements/:project/').get(async (req, res) => {
    try{
        let nocase = req.params.project.toLowerCase();
        if(nocase=="lora"){
            let measurements = await model_influx.getMeasurementsLoRa();
            res.send(measurements);
        }
        else if(nocase=="wifi"){
            let measurements = await model_influx.getMeasurementsWifi();
            res.send(measurements);
        }
        else if(nocase=="processed"){
            let measurements = await model_influx.getMeasurementsLoRaproc();
            res.send(measurements);
        }
        else if(nocase=="4g"){
            let measurements = await model_influx.getMeasurements4G();
            res.send(measurements);
        }
    }
    catch(err){
        res.send(err.message);
    }
});

router.route('/admin/createproject').get((req, res) => {
    res.render('create_project',{username: req.session.username, page:"createproject"});
});

router.route('/admin/createuser').get((req, res) => {
    res.render('create_newuser',{username: req.session.username, page:"createuser"});
}
);

router.route('/admin/createuser').post(async (req, res) => {
    // res.render('create_newuser',{username: req.session.username, page:"createuser"});
    try{
        if(req.body.username === '' || req.body.email === '' || req.body.password === '' || req.body.confirmpassword === '') {
            res.render('create_newuser', {username: req.session.username, page:"createuser",error: 'All fields are required'});
        }
        if(req.body.password !== req.body.confirmpassword){
            res.render('create_newuser', {username: req.session.username, page:"createuser",error: 'Passwords do not match'});
        }
        else{
            if(await model.registerUser(req.body.username,req.body.email, req.body.password)){
                // req.session.username = req.body.username;
                res.render('create_newuser', {username: req.session.username, page:"createuser",success: 'User created successfully'});
            }
        }
    }
    catch(err){
        res.render('create_newuser', {username: req.session.username,page:"createuser",error: err.message});
    }
}
);

router.route('/admin/createproject').post(async (req, res) => {
    try{
        await model.createProject(req.body.projectName, req.body.projectDescription);
        // res.render('assignproject', {success: 'Project created successfully'});
        res.render('create_project', {username: req.session.username ,success: 'Project created successfully'});
        // console.log(req.body);
        // if(req.body.projectName === '' || req.body.req.body.projectDescription === ''){
        //     res.render('create_project', {error: 'All fields are required'});
        // }
        // else{
        //     console.log("im here")
        //     // await model.createProject(req.body.projectName, req.body.projectDescription);
        //     res.redirect('/admin/assignproject');
        // }
    }
    catch(err){
        res.render('create_project', {username: req.session.username,error: err.message});
    }
}
);

router.route('/admin/editproject/:id').get(async (req, res) => {
    try{
        let project = await model.getProjectData(req.params.id);
        let users_assigned = await model.getProjectUsers(req.params.id);
        console.log(users_assigned);
        res.render('edit_project', {username: req.session.username, project: project,users_assigned: users_assigned});
    }
    catch(err){
        res.render('edit_project', {username: req.session.username, error: err.message});
    }
});

router.route('/admin/edituser/:username').get(async (req, res) => {
    try{
        let user = await model.getUserData(req.params.username);
        let projects_assigned = await model.getUserProjects(req.params.username);
        res.render('edit_user', {username: req.session.username, user: user, projects_assigned: projects_assigned});
    }
    catch(err){
        res.render('edit_user', {username: req.session.username, error: err.message});
    }
}
);

router.route('/test/leaflet/heatmap').get(async (req, res) => {
    try{
        let project= await model.getProjectData(3);
        let projectPoints;
        if(project.projName==="Signal Coverage - LoRA"){
            projectPoints= await model_influx.getMeasurementsLoRa();
        }
        else if (project.projName==="Access Point Mapping - eduroam"){
            projectPoints= await model_influx.getMeasurementsWifi();
        }
        // console.log(projectPoints);
        // res.render('projectpg', {layout: 'main_google' , username: req.session.username, project: project, projectPoints: projectPoints});
        res.render('projectpg', {layout: 'main',username: req.session.username, project: project});
    }
    catch(err){
        res.redirect('/mycompany', {error: err.message});
    }
});

//TODO remove this
router.route('/test/heatmap').get(async (req, res) => {
    try{
        // let projectPoints = await model_influx.getMeasurementsLoRa();
        res.render('heatmap2', {layout: 'heatmap_test'});
    }
    catch(err){
        res.redirect('/mycompany', {error: err.message});
    }
}
);

router.route('/upload_photo').post(upload.single('photo'), async (req, res) => {
    const metadata = req.body;
    const photoFile = req.file;

    if (!photoFile || !metadata.lat || !metadata.lon || !metadata.timestamp) {
        return res.status(400).send('Photo and metadata (lat, lon, timestamp) are required.');
    }

    // Save metadata to a JSON file (you can replace this with a database)
    const metadataFile = 'metadata.json';
    const metadataEntry = {
        lat: metadata.lat,
        lon: metadata.lon,
        timestamp: metadata.timestamp,
        photoPath: `/uploads/${photoFile.filename}`
    };

    //write the data to the sqlite
    try{
        await model.writePhotoData(metadata.timestamp, metadata.lat, metadata.lon, metadataEntry.photoPath);
    }
    catch(err){
        console.log(err);
    }

    // fs.readFile(metadataFile, (err, data) => {
    //     const metadataArray = err ? [] : JSON.parse(data); // If file doesn't exist, start with an empty array
    //     metadataArray.push(metadataEntry);

    //     fs.writeFile(metadataFile, JSON.stringify(metadataArray, null, 2), (err) => {
    //         if (err) {
    //             console.error(err);
    //             return res.status(500).send('Error saving metadata.');
    //         }
    //         res.send({
    //             message: 'Photo and metadata saved successfully!',
    //             data: metadataEntry,
    //         });
    //     });
    // });
});

router.route('/api/photos').get(async (req, res) => {
    try{
        let photos = await model.getPhotos();
        res.send(photos);
    }
    catch(err){
        res.send(err.message);
    }
});

router.route('/admin/live').get(async (req, res) => {
    res.render('live', {username: req.session.username, page:"live"});
});

router.route('/api/demo/measurements/car/:car_id').get(async (req, res) => {
    try{
        let measurements = await fetch('http://150.140.186.118:1026/v2/entities/car'+req.params.car_id+'/attrs')
        .then(response => response.json())
        .then(data => {
            res.send(data);
        });
    }
    catch(err){
        res.send(err.message);
    }
}
);

router.use((req, res) => {
    res.render('catcherror');
});





const PORT=process.env.PORT || 3000;
const server = app.listen(PORT,"0.0.0.0", () => { console.log(`http://localhost:${PORT}`) });

