import Handlebars from 'handlebars';

Handlebars.registerHelper('eq', function(a, b) {
    // console.log(a, b);
    return a === b;
});

export default Handlebars;