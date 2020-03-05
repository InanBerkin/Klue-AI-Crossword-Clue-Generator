const puppeteer = require('puppeteer');

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
    await (await page.$('button[aria-label="OK"]')).click();
    await (await page.$('button[aria-label="reveal"]')).click();
    const [button] = await page.$x("//*[@id='root']/div/div/div[4]/div/main/div[2]/div/div/ul/div[2]/li[2]/ul/li[3]");
    if (button) {
        button.click();
    }
    await (await page.waitForSelector('button[aria-label="Reveal"]')).click();
    await (await page.waitForSelector('#root > div > div.ModalWrapper-wrapper--1GgyB.ModalWrapper-stretch--19Bif > div.ModalBody-body--3PkKz > span')).click();
}

async function getAnswers(page) {
    await page.waitForSelector("[aria-live='polite']");
    await page.waitForSelector(".Shame-revealed--3jDzk");
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
//     let x = await getCrosswordData();
//     console.log(x.answers);
// })();

module.exports = getCrosswordData;