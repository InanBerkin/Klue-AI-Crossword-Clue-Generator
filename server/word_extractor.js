const fs = require('fs');
const files = []

fs.readdirSync('./').forEach(file => {
    if (file.indexOf('.json') !== -1) {
        files.push(file)
    }
});
files.pop()

words = []
files.forEach((file) => {
    let puzzle = fs.readFileSync(file);
    puzzle = JSON.parse(puzzle);
    words = [...words, ...puzzle.across.map(x => x.answer)];
    words = [...words, ...puzzle.down.map(x => x.answer)];
})

words.sort()
console.dir(words, { 'maxArrayLength': null })




