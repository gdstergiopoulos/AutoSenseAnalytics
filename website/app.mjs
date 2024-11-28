// Express.js
import express from 'express'
// Handlebars (https://www.npmjs.com/package/express-handlebars)
import { engine } from 'express-handlebars'
import session from 'express-session';
import * as model from './model/model.mjs'
import Handlebars from './helpers.js'
import mqtt from 'mqtt';
//TODO not logged in or declared Μάθημα 1 .. κλπ με toggle συντελεστή

const app = express()
const router = express.Router();
const port = process.env.PORT || '3000';

app.use(express.static('public'));
app.engine('hbs', engine({ extname: 'hbs' }));
app.set('view engine', 'hbs');


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
                res.render('companyhome', {username: req.session.username, projects: projects});
            }
            catch(err){
                res.render('companyhome', {username: req.session.username, error: err.message});
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
    try{
        let project= await model.getProjectData(req.params.id);
        res.render('projectpg', {username: req.session.username, project: project});
    }
    catch(err){
        res.redirect('/mycompany', {error: err.message});
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

router.use((req, res) => {
    res.render('catcherror');
});




const PORT=process.env.PORT || 3000;
const server = app.listen(PORT, () => { console.log(`http://127.0.0.1:${PORT}`) });

