const express = require('express')
const scraper = require('./scraper');
const app = express()
const port = 3000;
let result = null;
let day = new Date().getDay();

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

app.get('/', async (req, res) => {
    if (result == null || day !== new Date().getDay()) {
        result = await scraper();
    }
    res.send(result);
})

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
