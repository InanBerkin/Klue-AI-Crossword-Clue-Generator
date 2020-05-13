const express = require('express')
const scraper = require('./scraper');
const app = express()
const port = 3000;
let result = require('./2020-05-12.json');
let day = new Date().getDay();

app.use(function (req, res, next) {
    res.header("Access-Control-Allow-Origin", "*");
    res.header("Access-Control-Allow-Headers", "Origin, X-Requested-With, Content-Type, Accept");
    next();
});

app.get('/', async (req, res) => {
    // let response = await scraper();
    // console.log(response);
    // res.send(response);
    res.send(result)
})

app.get('/answers', async (req, res) => {
    // const GRID_SIZE = 5;
    // let answers = result.answers;
    // let across = [];
    // let down = [];

    // for (let i = 0; i < GRID_SIZE; i++) {
    //     let answer = "";
    //     let clue = null;
    //     for (let j = 0; j < GRID_SIZE; j++) {
    //         block = answers[i][j];
    //         if (block != null) {
    //             answer += block.letter;
    //             if (clue == null && block.num != null) {
    //                 clue = block.num + "A";
    //             }
    //         }
    //     }
    //     across.push({ clue, answer })
    // }

    // for (let i = 0; i < GRID_SIZE; i++) {
    //     let answer = "";
    //     let clue = null;
    //     for (let j = 0; j < GRID_SIZE; j++) {
    //         block = answers[j][i];
    //         if (block != null) {
    //             answer += block.letter;
    //             if (clue == null && block.num != null) {
    //                 clue = block.num + "D";
    //             }
    //         }
    //     }
    //     down.push({ clue, answer })
    // }
    let response = {
        across: result.across,
        down: result.down
    }
    res.send(response);
})

app.listen(port, () => console.log(`Example app listening on port ${port}!`))
