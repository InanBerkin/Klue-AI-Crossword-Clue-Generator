const puppeteer = require('puppeteer');
const fs = require('fs');

const url = "https://www.nytimes.com/crosswords/game/mini";

async function getCrosswordData() {
    try {
        const browser = await puppeteer.launch({
            headless: true
        })
        const page = await browser.newPage()
        await page.setViewport({ width: 1366, height: 768 });
        await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 0 });
        await revealPuzzle(page);
        const answers = await getAnswers(page);
        const clues = await getClues(page);
        return {
            answers, clues
        };
    } catch (error) {
        console.log(error);
    }
}

async function revealPuzzle(page) {
    // Click on the initial popup and then click on the reveal button
    await (await page.$('button[aria-label="OK"]')).click();
    await (await page.$('button[aria-label="reveal"]')).click();
    const button = await page.waitForSelector("#root > div > div > div.app-mainContainer--3CJGG > div > main > div.layout > div > div > ul > div.Toolbar-expandedMenu--2s4M4 > li.Tool-button--39W4J.Tool-tool--Fiz94.Tool-texty--2w4Br.Tool-open--1Moaq > ul > li:nth-child(3) > a");
    if (button) {
        button.click();
    }
    await (await page.waitForSelector('button[aria-label="Reveal"]')).click();
    await (await page.waitForSelector('div.ModalBody-body--3PkKz > span')).click();
}

async function getAnswers(page) {
    // Wait for puzzle to be solved
    await page.waitForSelector("[aria-live='polite']");
    await page.waitForSelector(".Shame-revealed--3jDzk");

    // Get the letters in each block and numbers if any
    let options = await (await page.$("g[data-group='cells']")).$$eval("g", options => options.map(option => {
        if (option.childNodes.length === 1) {
            return null;
        }
        let text = option.textContent.slice(0, -1);
        return {
            num: text.length > 1 ? text.substring(0, text.length - 1) : null,
            letter: text[text.length - 1]
        };
    }));

    // Push answers to a grid
    const gridSize = Math.sqrt(options.length);
    let grid = [];
    for (let i = 0; i < options.length; i = i + gridSize) {
        grid.push(options.slice(i, i + gridSize));
    }
    return grid;
}

async function getClues(page) {
    let allClues = await page.$$("ol.ClueList-list--2dD5-");
    let acrossClues = await allClues[0].$$eval("li.Clue-li--1JoPu", options => options.map(option => {
        let clue = [...option.childNodes];
        let clueNumber = clue[0].textContent;
        let clueText = clue[1].textContent;
        return { clueNumber, clueText };
    }));
    let downClues = await allClues[1].$$eval("li.Clue-li--1JoPu", options => options.map(option => {
        let clue = [...option.childNodes];
        let clueNumber = clue[0].textContent;
        let clueText = clue[1].textContent;
        return { clueNumber, clueText };
    }));
    return { acrossClues, downClues };
}

// (async () => {
//     let { answers, clues } = await getCrosswordData();
//     const GRID_SIZE = 5;
//     let across = [];
//     let down = [];

//     for (let i = 0; i < GRID_SIZE; i++) {
//         let answer = "";
//         let clue = null;
//         for (let j = 0; j < GRID_SIZE; j++) {
//             block = answers[i][j];
//             if (block != null) {
//                 answer += block.letter;
//                 if (clue == null && block.num != null) {
//                     clue = block.num + "A";
//                 }
//             }
//         }
//         across.push({ clue, answer })
//     }

//     for (let i = 0; i < GRID_SIZE; i++) {
//         let answer = "";
//         let clue = null;
//         for (let j = 0; j < GRID_SIZE; j++) {
//             block = answers[j][i];
//             if (block != null) {
//                 answer += block.letter;
//                 if (clue == null && block.num != null) {
//                     clue = block.num + "D";
//                 }
//             }
//         }
//         down.push({ clue, answer })
//     }

//     fs.writeFile(new Date().toISOString().slice(0, 10) + ".json", JSON.stringify({ across, down, clues }), function (err, data) {
//         if (err) {
//             return console.log(err);
//         }
//     })

// })();

module.exports = getCrosswordData;